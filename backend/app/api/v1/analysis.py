from fastapi import APIRouter, HTTPException, Query

from app.fundamental.analyzer import analyze_fundamental
from app.schemas.analysis import TechnicalAnalysisResponse
from app.schemas.fundamental import FundamentalAnalysisResponse
from app.technical.analyzer import analyze

router = APIRouter(prefix="/analysis", tags=["analysis"])

_VALID_PERIODS = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"}
_VALID_INTERVALS = {"1m", "5m", "15m", "30m", "1h", "4h", "1d", "1wk"}


@router.get("/{symbol}/technical", response_model=TechnicalAnalysisResponse)
async def get_technical(
    symbol: str,
    period: str = Query("1y", description="1d | 5d | 1mo | 3mo | 6mo | 1y | 2y | 5y"),
    interval: str = Query("1d", description="1m | 5m | 15m | 30m | 1h | 4h | 1d | 1wk"),
):
    if period not in _VALID_PERIODS:
        raise HTTPException(400, f"Invalid period '{period}'. Valid: {sorted(_VALID_PERIODS)}")
    if interval not in _VALID_INTERVALS:
        raise HTTPException(400, f"Invalid interval '{interval}'. Valid: {sorted(_VALID_INTERVALS)}")
    try:
        return await analyze(symbol.upper(), period, interval)
    except RuntimeError as exc:
        raise HTTPException(503, detail=str(exc))


@router.get("/{symbol}/fundamental", response_model=FundamentalAnalysisResponse)
async def get_fundamental(symbol: str):
    try:
        return await analyze_fundamental(symbol.upper())
    except Exception as exc:
        raise HTTPException(503, detail=str(exc))
