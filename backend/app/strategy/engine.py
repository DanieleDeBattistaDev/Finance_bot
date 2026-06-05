import logging
from datetime import datetime

import pandas as pd

from app.fundamental.analyzer import analyze_fundamental
from app.market_data.fetcher import fetch_market_data
from app.ml.predictor import predict as ml_predict
from app.schemas.signal import SignalResponse, SignalSource
from app.strategy.rules import (
    Vote,
    eval_bollinger,
    eval_macd,
    eval_ml,
    eval_rsi,
    eval_sentiment,
    eval_sma_trend,
    eval_support_resistance,
    get_threshold,
    get_weights,
)
from app.technical.indicators import compute_all
from app.technical.support_resistance import find_levels

logger = logging.getLogger(__name__)

_TIMEFRAME_PARAMS: dict[str, tuple[str, str]] = {
    "short":  ("1mo",  "1h"),
    "medium": ("6mo",  "1d"),
    "long":   ("2y",   "1wk"),
}


def _candles_to_df(candles: list) -> pd.DataFrame:
    records = [
        {"Date": c.timestamp, "Open": c.open, "High": c.high,
         "Low": c.low, "Close": c.close, "Volume": c.volume}
        for c in candles
    ]
    return pd.DataFrame(records).set_index("Date").sort_index()


def _weighted_score(votes: list[Vote]) -> float:
    total_weight = sum(v.weight for v in votes)
    if total_weight == 0:
        return 0.0
    return sum(v.value * v.weight for v in votes) / total_weight


def _to_signal_source(vote: Vote) -> SignalSource:
    if vote.value > 0.1:
        direction = "bullish"
    elif vote.value < -0.1:
        direction = "bearish"
    else:
        direction = "neutral"
    return SignalSource(name=vote.label, vote=direction, weight=vote.weight, reason=vote.reason)


async def generate_signal(
    symbol: str,
    timeframe: str = "medium",
    risk_level: str = "medium",
    strategy_type: str = "swing",
) -> SignalResponse:
    period, interval = _TIMEFRAME_PARAMS.get(timeframe, ("6mo", "1d"))
    weights = get_weights(strategy_type)
    threshold = get_threshold(risk_level)

    # ── 1. Fetch market data ─────────────────────────────────────────────────
    market_data = await fetch_market_data(symbol, period=period, interval=interval)
    df = _candles_to_df(market_data.candles)

    # ── 2. Technical analysis ────────────────────────────────────────────────
    ta_series = compute_all(df)
    latest = ta_series[-1]
    support_levels, resistance_levels = find_levels(df)

    close = latest.close
    ta_votes: list[Vote] = [
        eval_rsi(latest.rsi),
        eval_macd(latest.macd.macd, latest.macd.signal, latest.macd.histogram),
        eval_bollinger(
            (latest.bollinger.middle and latest.bollinger.upper and latest.bollinger.lower)
            and (close - latest.bollinger.lower) / max(latest.bollinger.upper - latest.bollinger.lower, 1e-9)
        ),
        *eval_sma_trend(close, latest.sma_20, latest.sma_50, latest.sma_200, timeframe),
        *eval_support_resistance(close, support_levels, resistance_levels),
    ]

    # ── 3. Fundamental analysis ──────────────────────────────────────────────
    try:
        fundamental = await analyze_fundamental(symbol)
        fund_votes: list[Vote] = [eval_sentiment(fundamental.sentiment_score, fundamental.news_impact)]
    except Exception as exc:
        logger.warning("Fundamental analysis failed for %s: %s", symbol, exc)
        fund_votes = [Vote(0.0, 0.0, "Sentiment", "Fundamental analysis unavailable")]

    sentiment_score = fundamental.sentiment_score if 'fundamental' in dir() else 0.0

    # ── 4. ML prediction ─────────────────────────────────────────────────────
    try:
        ml_result = await ml_predict(symbol, df, sentiment_score)
        ml_votes: list[Vote] = [eval_ml(ml_result.prediction, ml_result.confidence)]
    except FileNotFoundError:
        ml_votes = [Vote(0.0, 0.0, "ML", "ML model not trained — run POST /predictions/{symbol}/train")]
    except Exception as exc:
        logger.warning("ML prediction failed for %s: %s", symbol, exc)
        ml_votes = [Vote(0.0, 0.0, "ML", f"ML unavailable: {exc}")]

    # ── 5. Weighted scoring ───────────────────────────────────────────────────
    ta_score = _weighted_score(ta_votes)
    fund_score = _weighted_score(fund_votes)
    ml_score = _weighted_score(ml_votes)

    composite = (
        ta_score   * weights["technical"]
        + fund_score * weights["fundamental"]
        + ml_score   * weights["ml"]
    )

    # ── 6. Decision ───────────────────────────────────────────────────────────
    if composite > threshold:
        action = "buy"
    elif composite < -threshold:
        action = "sell"
    else:
        action = "hold"

    confidence = round(min(abs(composite) / max(threshold, 1e-9) * 50 + 50, 100), 1)

    # ── 7. Build reasoning list ───────────────────────────────────────────────
    all_votes = ta_votes + fund_votes + ml_votes
    active_votes = [v for v in all_votes if v.weight > 0 and abs(v.value) > 0.1]
    active_votes.sort(key=lambda v: abs(v.value * v.weight), reverse=True)
    reasoning = [v.reason for v in active_votes[:8]]

    reasoning.insert(
        0,
        f"Composite score: {composite:+.3f} (TA={ta_score:+.3f} × {weights['technical']}, "
        f"Fund={fund_score:+.3f} × {weights['fundamental']}, "
        f"ML={ml_score:+.3f} × {weights['ml']}) — threshold ±{threshold}",
    )

    sources = [_to_signal_source(v) for v in all_votes if v.weight > 0]

    logger.info(
        "Signal %s: %s (conf=%.1f%%, composite=%+.3f, timeframe=%s, risk=%s, strategy=%s)",
        symbol, action.upper(), confidence, composite, timeframe, risk_level, strategy_type,
    )

    return SignalResponse(
        symbol=symbol,
        action=action,
        confidence=confidence,
        reasoning=reasoning,
        sources=sources,
        timeframe=timeframe,
        risk_level=risk_level,
        strategy_type=strategy_type,
        generated_at=datetime.now(),
    )
