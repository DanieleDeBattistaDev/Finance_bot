import numpy as np
import pandas as pd

SEQ_LEN = 20

FEATURE_COLS = [
    "return_1d", "return_5d",
    "rsi",
    "macd", "macd_signal", "macd_hist",
    "bb_pct",
    "atr_pct",
    "vol_ratio",
    "sma_20_ratio", "sma_50_ratio",
    "volatility_10d",
    "sentiment",
]


def build_features(df: pd.DataFrame, sentiment_score: float = 0.0) -> pd.DataFrame:
    feat = pd.DataFrame(index=df.index)
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    feat["return_1d"] = close.pct_change(1)
    feat["return_5d"] = close.pct_change(5)

    delta = close.diff()
    avg_gain = delta.clip(lower=0).ewm(com=13, min_periods=14).mean()
    avg_loss = (-delta.clip(upper=0)).ewm(com=13, min_periods=14).mean()
    feat["rsi"] = (100 - 100 / (1 + avg_gain / avg_loss)) / 100  # normalised 0-1

    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    feat["macd"] = macd_line / close
    feat["macd_signal"] = signal_line / close
    feat["macd_hist"] = (macd_line - signal_line) / close

    sma_20 = close.rolling(20).mean()
    std_20 = close.rolling(20).std()
    bb_upper = sma_20 + 2 * std_20
    bb_lower = sma_20 - 2 * std_20
    feat["bb_pct"] = (close - bb_lower) / (bb_upper - bb_lower + 1e-9)

    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    atr = tr.ewm(com=13, min_periods=14).mean()
    feat["atr_pct"] = atr / close

    vol_ma = volume.rolling(20).mean()
    feat["vol_ratio"] = volume / (vol_ma + 1)

    sma_50 = close.rolling(50).mean()
    feat["sma_20_ratio"] = close / (sma_20 + 1e-9) - 1
    feat["sma_50_ratio"] = close / (sma_50 + 1e-9) - 1

    feat["volatility_10d"] = close.pct_change().rolling(10).std()
    feat["sentiment"] = sentiment_score

    return feat[FEATURE_COLS].dropna()


def build_targets(df: pd.DataFrame, horizon: int = 1) -> tuple[pd.Series, pd.Series]:
    future_return = df["Close"].pct_change(horizon).shift(-horizon)
    direction = (future_return > 0).astype(int)
    common = future_return.dropna().index
    return direction.loc[common], future_return.loc[common]


def build_sequences(
    features: pd.DataFrame, targets: pd.Series, seq_len: int = SEQ_LEN
) -> tuple[np.ndarray, np.ndarray]:
    common = features.index.intersection(targets.index)
    feat_arr = features.loc[common].values.astype(np.float32)
    tgt_arr = targets.loc[common].values.astype(np.float32)

    X, y = [], []
    for i in range(seq_len, len(feat_arr)):
        X.append(feat_arr[i - seq_len : i])
        y.append(tgt_arr[i])
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)
