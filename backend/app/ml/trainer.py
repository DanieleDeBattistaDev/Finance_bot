import logging
from pathlib import Path

import joblib
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score
from torch.utils.data import DataLoader, TensorDataset

from app.core.config import settings
from app.ml.features import SEQ_LEN, build_features, build_sequences, build_targets
from app.ml.models.lstm import LSTMPredictor
from app.ml.models.xgboost_model import XGBoostPredictor

logger = logging.getLogger(__name__)

MODELS_DIR = Path(settings.ML_MODELS_DIR)
EPOCHS = 50
BATCH_SIZE = 32


def _time_split_idx(n: int, test_ratio: float = 0.2) -> int:
    return int(n * (1 - test_ratio))


async def train_for_symbol(
    symbol: str,
    df,
    sentiment_score: float = 0.0,
) -> dict:
    import asyncio

    features_df = build_features(df, sentiment_score)
    direction, future_return = build_targets(df)

    common = features_df.index.intersection(direction.index)
    features_df = features_df.loc[common]
    direction = direction.loc[common]
    future_return = future_return.loc[common]

    n = len(features_df)
    if n < SEQ_LEN + 50:
        raise ValueError(f"Not enough data to train ({n} rows). Need at least {SEQ_LEN + 50}.")

    split = _time_split_idx(n)
    X_flat = features_df.values.astype(np.float32)
    y_dir = direction.values.astype(int)
    y_ret = future_return.values.astype(np.float32)

    # ── XGBoost ──────────────────────────────────────────────────────────────
    xgb_model = XGBoostPredictor()
    X_scaled = xgb_model.scaler.fit_transform(X_flat)

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: xgb_model.classifier.fit(X_scaled[:split], y_dir[:split]),
    )
    await loop.run_in_executor(
        None,
        lambda: xgb_model.regressor.fit(X_scaled[:split], y_ret[:split]),
    )

    xgb_acc = accuracy_score(y_dir[split:], xgb_model.classifier.predict(X_scaled[split:]))
    logger.info("XGBoost %s accuracy: %.3f", symbol, xgb_acc)

    xgb_dir = MODELS_DIR / "xgboost"
    xgb_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(xgb_model, xgb_dir / f"{symbol}.joblib")

    # ── LSTM ──────────────────────────────────────────────────────────────────
    X_seq, y_seq = build_sequences(features_df, direction, SEQ_LEN)
    split_seq = _time_split_idx(len(X_seq))

    X_train = torch.tensor(X_seq[:split_seq])
    y_train = torch.tensor(y_seq[:split_seq]).unsqueeze(1)
    loader = DataLoader(TensorDataset(X_train, y_train), batch_size=BATCH_SIZE, shuffle=False)

    n_features = X_seq.shape[2]
    lstm_model = LSTMPredictor(input_size=n_features)
    optimizer = torch.optim.Adam(lstm_model.parameters(), lr=1e-3)
    criterion = nn.BCELoss()

    def _train_lstm():
        lstm_model.train()
        for epoch in range(EPOCHS):
            total = 0.0
            for X_b, y_b in loader:
                optimizer.zero_grad()
                direction_pred, _ = lstm_model(X_b)
                loss = criterion(direction_pred, y_b)
                loss.backward()
                optimizer.step()
                total += loss.item()
            if (epoch + 1) % 10 == 0:
                logger.info("LSTM %s epoch %d/%d loss=%.4f", symbol, epoch + 1, EPOCHS, total / len(loader))

    await loop.run_in_executor(None, _train_lstm)

    lstm_dir = MODELS_DIR / "lstm"
    lstm_dir.mkdir(parents=True, exist_ok=True)
    torch.save(
        {"state_dict": lstm_model.state_dict(), "n_features": n_features},
        lstm_dir / f"{symbol}.pt",
    )

    return {
        "symbol": symbol,
        "xgboost_accuracy": round(xgb_acc, 4),
        "lstm_epochs": EPOCHS,
        "n_features": n_features,
        "train_samples": split,
        "test_samples": n - split,
    }
