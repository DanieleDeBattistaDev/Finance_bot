from datetime import datetime

from pydantic import BaseModel


class SignalSource(BaseModel):
    name: str
    vote: str    # bullish | bearish | neutral
    weight: float
    reason: str


class SignalResponse(BaseModel):
    symbol: str
    action: str          # buy | sell | hold
    confidence: float    # 0-100
    reasoning: list[str]
    sources: list[SignalSource]
    timeframe: str
    risk_level: str
    strategy_type: str
    generated_at: datetime
