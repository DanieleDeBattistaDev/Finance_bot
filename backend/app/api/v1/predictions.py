import pandas as pd
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from app.fundamental.analyzer import analyze_fundamental
from app.market_data.fetcher import fetch_market_data
from app.ml.predictor import predict
from app.schemas.prediction import PredictionResponse

router = APIRouter(prefix="/predictions", tags=["predictions"])


def _candles_to_df(candles: list) -> pd.DataFrame:
    records = [
        {
            "Date":   c.timestamp,
            "Open":   c.open,
            "High":   c.high,
            "Low":    c.low,
            "Close":  c.close,
            "Volume": c.volume,
        }
        for c in candles
    ]
    return pd.DataFrame(records).set_index("Date").sort_index()


@router.get("/{symbol}", response_model=PredictionResponse)
async def get_prediction(
    symbol: str,
    include_sentiment: bool = Query(True, description="Fetch live sentiment and include in features"),
):
    symbol = symbol.upper()
    try:
        market_data = await fetch_market_data(symbol, period="2y", interval="1d")
        df = _candles_to_df(market_data.candles)

        sentiment_score = 0.0
        if include_sentiment:
            try:
                fundamental = await analyze_fundamental(symbol)
                sentiment_score = fundamental.sentiment_score
            except Exception as exc:
                # Non-fatal: proceed without sentiment
                pass

        return await predict(symbol, df, sentiment_score)
    except FileNotFoundError as exc:
        raise HTTPException(404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(503, detail=str(exc))


@router.post("/{symbol}/train", status_code=202)
async def trigger_training(symbol: str, background_tasks: BackgroundTasks):
    """Start async model training for a symbol (uses 5y of daily data)."""
    from app.ml.trainer import train_for_symbol

    symbol = symbol.upper()

    async def _run_training() -> None:
        try:
            market_data = await fetch_market_data(symbol, period="5y", interval="1d")
            df = _candles_to_df(market_data.candles)
            result = await train_for_symbol(symbol, df)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).error("Training failed for %s: %s", symbol, exc)

    background_tasks.add_task(_run_training)
    return {"message": f"Training started for {symbol}. Check server logs for progress."}
