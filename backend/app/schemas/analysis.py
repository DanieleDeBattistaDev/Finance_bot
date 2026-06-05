from datetime import datetime

from pydantic import BaseModel


class MACDPoint(BaseModel):
    macd: float | None
    signal: float | None
    histogram: float | None


class BollingerPoint(BaseModel):
    upper: float | None
    middle: float | None
    lower: float | None


class IndicatorPoint(BaseModel):
    timestamp: datetime
    close: float
    rsi: float | None
    macd: MACDPoint
    bollinger: BollingerPoint
    sma_20: float | None
    sma_50: float | None
    sma_200: float | None
    ema_12: float | None
    ema_26: float | None
    atr: float | None


class TechnicalAnalysisResponse(BaseModel):
    symbol: str
    interval: str
    series: list[IndicatorPoint]
    support_levels: list[float]
    resistance_levels: list[float]
