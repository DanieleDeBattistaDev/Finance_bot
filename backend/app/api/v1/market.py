from fastapi import APIRouter, HTTPException, Query

from app.market_data.fetcher import fetch_market_data
from app.schemas.market import MarketDataResponse

router = APIRouter(prefix="/market", tags=["market"])

_VALID_PERIODS = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"}
_VALID_INTERVALS = {"1m", "5m", "15m", "30m", "1h", "4h", "1d", "1wk"}


@router.get("/{symbol}/history", response_model=MarketDataResponse)
async def get_history(
    symbol: str,
    period: str = Query("1y", description="1d | 5d | 1mo | 3mo | 6mo | 1y | 2y | 5y"),
    interval: str = Query("1d", description="1m | 5m | 15m | 30m | 1h | 4h | 1d | 1wk"),
):
    if period not in _VALID_PERIODS:
        raise HTTPException(400, f"Invalid period '{period}'. Valid: {sorted(_VALID_PERIODS)}")
    if interval not in _VALID_INTERVALS:
        raise HTTPException(400, f"Invalid interval '{interval}'. Valid: {sorted(_VALID_INTERVALS)}")
    try:
        return await fetch_market_data(symbol.upper(), period, interval)
    except RuntimeError as exc:
        raise HTTPException(503, detail=str(exc))


@router.get("/{symbol}/latest", response_model=MarketDataResponse)
async def get_latest(symbol: str):
    try:
        data = await fetch_market_data(symbol.upper(), period="5d", interval="1d")
        data.candles = data.candles[-1:]
        return data
    except RuntimeError as exc:
        raise HTTPException(503, detail=str(exc))
