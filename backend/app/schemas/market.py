from datetime import datetime

from pydantic import BaseModel


class Candle(BaseModel):
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketDataResponse(BaseModel):
    symbol: str
    source: str
    interval: str
    candles: list[Candle]
