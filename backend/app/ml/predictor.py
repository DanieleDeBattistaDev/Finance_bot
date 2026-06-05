import logging
from pathlib import Path

import joblib
import numpy as np
import torch

from app.core.config import settings
from app.ml.features import SEQ_LEN, build_features
from app.ml.models.lstm import LSTMPredictor
from app.ml.models.xgboost_model import XGBoostPredictor
from app.schemas.prediction import ModelOutput, PredictionResponse

logger = logging.getLogger(__name__)

MODELS_DIR = Path(settings.ML_MODELS_DIR)

_lstm_cache: dict[str, LSTMPredictor] = {}
_xgb_cache: dict[str, XGBoostPredictor] = {}


def _load_xgb(symbol: str) -> XGBoostPredictor:
    if symbol not in _xgb_cache:
        path = MODELS_DIR / "xgboost" / f"{symbol}.joblib"
        if not path.exists():
            raise FileNotFoundError(f"XGBoost model not found for {symbol}. Train first via POST /predictions/{symbol}/train")
        _xgb_cache[symbol] = joblib.load(path)
    return _xgb_cache[symbol]


def _load_lstm(symbol: str) -> LSTMPredictor:
    if symbol not in _lstm_cache:
        path = MODELS_DIR / "lstm" / f"{symbol}.pt"
        if not path.exists():
            raise FileNotFoundError(f"LSTM model not found for {symbol}. Train first via POST /predictions/{symbol}/train")
        checkpoint = torch.load(path, map_location="cpu")
        model = LSTMPredictor(input_size=checkpoint["n_features"])
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        _lstm_cache[symbol] = model
    return _lstm_cache[symbol]


async def predict(
    symbol: str,
    df,
    sentiment_score: float = 0.0,
) -> PredictionResponse:
    features_df = build_features(df, sentiment_score)

    if len(features_df) < SEQ_LEN:
        raise ValueError(f"Not enough history ({len(features_df)} rows, need {SEQ_LEN})")

    # ── XGBoost ──────────────────────────────────────────────────────────────
    xgb_model = _load_xgb(symbol)
    X_flat = xgb_model.scaler.transform(features_df.values[-1:].astype(np.float32))
    xgb_prob = float(xgb_model.classifier.predict_proba(X_flat)[0][1])

    # ── LSTM ──────────────────────────────────────────────────────────────────
    lstm_model = _load_lstm(symbol)
    X_seq = torch.tensor(
        features_df.values[-SEQ_LEN:].astype(np.float32)
    ).unsqueeze(0)
    with torch.no_grad():
        lstm_dir_tensor, lstm_ret_tensor = lstm_model(X_seq)
    lstm_prob = float(lstm_dir_tensor[0][0])
    lstm_return = float(lstm_ret_tensor[0][0])

    # ── Ensemble ──────────────────────────────────────────────────────────────
    ensemble_prob = (xgb_prob + lstm_prob) / 2
    direction = "up" if ensemble_prob > 0.5 else "down"
    # Confidence = how far from the 50/50 boundary, scaled to [0.5, 1.0]
    confidence = max(ensemble_prob, 1 - ensemble_prob)

    logger.info(
        "Prediction %s: %s (conf=%.3f xgb=%.3f lstm=%.3f)",
        symbol, direction, confidence, xgb_prob, lstm_prob,
    )

    return PredictionResponse(
        symbol=symbol,
        prediction=direction,
        confidence=round(confidence, 4),
        expected_return=round(lstm_return * 100, 4),
        xgboost=ModelOutput(
            direction="up" if xgb_prob > 0.5 else "down",
            probability=round(xgb_prob, 4),
        ),
        lstm=ModelOutput(
            direction="up" if lstm_prob > 0.5 else "down",
            probability=round(lstm_prob, 4),
        ),
    )
