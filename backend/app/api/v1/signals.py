from fastapi import APIRouter, HTTPException, Query

from app.notifications.dispatcher import dispatch
from app.schemas.signal import SignalResponse
from app.strategy.engine import generate_signal

router = APIRouter(prefix="/signals", tags=["signals"])

_VALID_TIMEFRAMES = {"short", "medium", "long"}
_VALID_RISK = {"low", "medium", "high"}
_VALID_STRATEGIES = {"scalping", "swing", "long_term"}


@router.get("/{symbol}", response_model=SignalResponse)
async def get_signal(
    symbol: str,
    timeframe: str = Query("medium", description="short | medium | long"),
    risk_level: str = Query("medium", description="low | medium | high"),
    strategy_type: str = Query("swing", description="scalping | swing | long_term"),
):
    if timeframe not in _VALID_TIMEFRAMES:
        raise HTTPException(400, f"Invalid timeframe. Valid: {sorted(_VALID_TIMEFRAMES)}")
    if risk_level not in _VALID_RISK:
        raise HTTPException(400, f"Invalid risk_level. Valid: {sorted(_VALID_RISK)}")
    if strategy_type not in _VALID_STRATEGIES:
        raise HTTPException(400, f"Invalid strategy_type. Valid: {sorted(_VALID_STRATEGIES)}")

    try:
        signal = await generate_signal(
            symbol=symbol.upper(),
            timeframe=timeframe,
            risk_level=risk_level,
            strategy_type=strategy_type,
        )
        await dispatch(signal)
        return signal
    except RuntimeError as exc:
        raise HTTPException(503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(500, detail=str(exc))
