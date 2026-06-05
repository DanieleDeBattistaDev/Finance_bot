from typing import NamedTuple


class Vote(NamedTuple):
    value: float   # -1.0 (bearish) to +1.0 (bullish)
    weight: float  # importance of this signal
    label: str     # short identifier
    reason: str    # human-readable explanation


# ── Weight profiles by strategy type ─────────────────────────────────────────

_STRATEGY_WEIGHTS = {
    "scalping":   {"technical": 0.70, "fundamental": 0.10, "ml": 0.20},
    "swing":      {"technical": 0.40, "fundamental": 0.30, "ml": 0.30},
    "long_term":  {"technical": 0.20, "fundamental": 0.50, "ml": 0.30},
}

# ── Buy/sell confidence thresholds by risk level ──────────────────────────────

_RISK_THRESHOLDS = {
    "low":    0.60,   # need strong consensus
    "medium": 0.40,
    "high":   0.25,
}


def get_weights(strategy_type: str) -> dict[str, float]:
    return _STRATEGY_WEIGHTS.get(strategy_type, _STRATEGY_WEIGHTS["swing"])


def get_threshold(risk_level: str) -> float:
    return _RISK_THRESHOLDS.get(risk_level, 0.40)


# ── Technical signal evaluators ───────────────────────────────────────────────

def eval_rsi(rsi: float | None) -> Vote:
    if rsi is None:
        return Vote(0.0, 0.0, "RSI", "RSI unavailable")
    if rsi < 30:
        return Vote(+0.8, 1.0, "RSI", f"RSI={rsi:.1f} — oversold, potential reversal up")
    if rsi > 70:
        return Vote(-0.8, 1.0, "RSI", f"RSI={rsi:.1f} — overbought, potential reversal down")
    if rsi < 45:
        return Vote(-0.2, 0.5, "RSI", f"RSI={rsi:.1f} — mild bearish momentum")
    if rsi > 55:
        return Vote(+0.2, 0.5, "RSI", f"RSI={rsi:.1f} — mild bullish momentum")
    return Vote(0.0, 0.3, "RSI", f"RSI={rsi:.1f} — neutral zone")


def eval_macd(macd: float | None, signal: float | None, histogram: float | None) -> Vote:
    if macd is None or signal is None:
        return Vote(0.0, 0.0, "MACD", "MACD unavailable")
    if macd > signal:
        strength = min(abs(histogram or 0) * 500, 1.0) if histogram else 0.4
        return Vote(+min(0.5 + strength * 0.3, 0.8), 0.9, "MACD",
                    f"MACD ({macd:.4f}) above signal ({signal:.4f}) — bullish crossover")
    else:
        strength = min(abs(histogram or 0) * 500, 1.0) if histogram else 0.4
        return Vote(-min(0.5 + strength * 0.3, 0.8), 0.9, "MACD",
                    f"MACD ({macd:.4f}) below signal ({signal:.4f}) — bearish crossover")


def eval_bollinger(bb_pct: float | None) -> Vote:
    """bb_pct = (close - lower) / (upper - lower): 0=at lower, 1=at upper"""
    if bb_pct is None:
        return Vote(0.0, 0.0, "Bollinger", "Bollinger unavailable")
    if bb_pct < 0.15:
        return Vote(+0.7, 0.8, "Bollinger", f"Price near lower Bollinger band ({bb_pct:.2f}) — mean-reversion signal up")
    if bb_pct > 0.85:
        return Vote(-0.7, 0.8, "Bollinger", f"Price near upper Bollinger band ({bb_pct:.2f}) — mean-reversion signal down")
    if bb_pct < 0.40:
        return Vote(-0.2, 0.4, "Bollinger", f"Price in lower half of band ({bb_pct:.2f})")
    if bb_pct > 0.60:
        return Vote(+0.2, 0.4, "Bollinger", f"Price in upper half of band ({bb_pct:.2f})")
    return Vote(0.0, 0.2, "Bollinger", f"Price mid-band ({bb_pct:.2f}) — no clear signal")


def eval_sma_trend(
    close: float,
    sma_20: float | None,
    sma_50: float | None,
    sma_200: float | None,
    timeframe: str,
) -> list[Vote]:
    votes: list[Vote] = []

    if sma_20 is not None:
        w = 0.6 if timeframe == "short" else 0.4
        if close > sma_20:
            votes.append(Vote(+0.4, w, "SMA20", f"Price ({close:.2f}) above SMA20 ({sma_20:.2f}) — short-term uptrend"))
        else:
            votes.append(Vote(-0.4, w, "SMA20", f"Price ({close:.2f}) below SMA20 ({sma_20:.2f}) — short-term downtrend"))

    if sma_50 is not None:
        w = 0.7 if timeframe == "medium" else 0.5
        if close > sma_50:
            votes.append(Vote(+0.5, w, "SMA50", f"Price above SMA50 ({sma_50:.2f}) — medium-term uptrend"))
        else:
            votes.append(Vote(-0.5, w, "SMA50", f"Price below SMA50 ({sma_50:.2f}) — medium-term downtrend"))

    if sma_200 is not None:
        w = 0.9 if timeframe == "long" else 0.5
        if close > sma_200:
            votes.append(Vote(+0.6, w, "SMA200", f"Price above SMA200 ({sma_200:.2f}) — long-term bullish structure"))
        else:
            votes.append(Vote(-0.6, w, "SMA200", f"Price below SMA200 ({sma_200:.2f}) — long-term bearish structure"))

    return votes


def eval_support_resistance(
    close: float,
    support_levels: list[float],
    resistance_levels: list[float],
    proximity_pct: float = 0.02,
) -> list[Vote]:
    votes: list[Vote] = []

    for lvl in support_levels:
        if abs(close - lvl) / lvl <= proximity_pct:
            votes.append(Vote(+0.6, 0.8, "Support",
                              f"Price ({close:.2f}) near support at {lvl:.2f} — bounce potential"))
            break

    for lvl in resistance_levels:
        if abs(close - lvl) / lvl <= proximity_pct:
            votes.append(Vote(-0.6, 0.8, "Resistance",
                              f"Price ({close:.2f}) near resistance at {lvl:.2f} — rejection potential"))
            break

    return votes


# ── Fundamental signal evaluator ──────────────────────────────────────────────

def eval_sentiment(sentiment_score: float, news_impact: float) -> Vote:
    impact_weight = 0.4 + (news_impact / 100) * 0.6  # 0.4 – 1.0
    if sentiment_score > 0.2:
        return Vote(+sentiment_score, impact_weight, "Sentiment",
                    f"Positive news sentiment ({sentiment_score:+.2f}, impact={news_impact:.0f})")
    if sentiment_score < -0.2:
        return Vote(sentiment_score, impact_weight, "Sentiment",
                    f"Negative news sentiment ({sentiment_score:+.2f}, impact={news_impact:.0f})")
    return Vote(0.0, impact_weight * 0.3, "Sentiment",
                f"Neutral news sentiment ({sentiment_score:+.2f})")


# ── ML signal evaluator ───────────────────────────────────────────────────────

def eval_ml(prediction: str | None, confidence: float | None) -> Vote:
    if prediction is None or confidence is None:
        return Vote(0.0, 0.0, "ML", "ML model not trained — signal skipped")
    value = +confidence if prediction == "up" else -confidence
    direction = "bullish" if prediction == "up" else "bearish"
    return Vote(value, confidence, "ML",
                f"ML ensemble predicts {prediction} with {confidence * 100:.1f}% confidence ({direction})")
