import math

import pandas as pd

from app.schemas.analysis import BollingerPoint, IndicatorPoint, MACDPoint


def _nan_to_none(value: float) -> float | None:
    return None if math.isnan(value) else round(value, 6)


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _macd(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line, macd_line - signal_line


def _bollinger(
    close: pd.Series, period: int = 20, num_std: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    sma = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    return sma + num_std * std, sma, sma - num_std * std


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return tr.ewm(com=period - 1, min_periods=period).mean()


def compute_all(df: pd.DataFrame) -> list[IndicatorPoint]:
    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    rsi = _rsi(close)
    macd_line, signal_line, histogram = _macd(close)
    bb_upper, bb_mid, bb_lower = _bollinger(close)
    atr = _atr(high, low, close)
    sma_20 = close.rolling(20).mean()
    sma_50 = close.rolling(50).mean()
    sma_200 = close.rolling(200).mean()
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()

    points: list[IndicatorPoint] = []
    for ts, row in df.iterrows():
        i = df.index.get_loc(ts)
        timestamp = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
        if hasattr(timestamp, "tzinfo") and timestamp.tzinfo is not None:
            timestamp = timestamp.replace(tzinfo=None)

        points.append(
            IndicatorPoint(
                timestamp=timestamp,
                close=round(float(row["Close"]), 6),
                rsi=_nan_to_none(rsi.iloc[i]),
                macd=MACDPoint(
                    macd=_nan_to_none(macd_line.iloc[i]),
                    signal=_nan_to_none(signal_line.iloc[i]),
                    histogram=_nan_to_none(histogram.iloc[i]),
                ),
                bollinger=BollingerPoint(
                    upper=_nan_to_none(bb_upper.iloc[i]),
                    middle=_nan_to_none(bb_mid.iloc[i]),
                    lower=_nan_to_none(bb_lower.iloc[i]),
                ),
                sma_20=_nan_to_none(sma_20.iloc[i]),
                sma_50=_nan_to_none(sma_50.iloc[i]),
                sma_200=_nan_to_none(sma_200.iloc[i]),
                ema_12=_nan_to_none(ema_12.iloc[i]),
                ema_26=_nan_to_none(ema_26.iloc[i]),
                atr=_nan_to_none(atr.iloc[i]),
            )
        )
    return points
