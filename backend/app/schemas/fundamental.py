from datetime import datetime

from pydantic import BaseModel


class NewsItem(BaseModel):
    title: str
    source: str
    url: str
    published_at: datetime | None
    sentiment_score: float  # -1 to +1
    sentiment_label: str    # positive | neutral | negative


class FundamentalAnalysisResponse(BaseModel):
    symbol: str
    sentiment_score: float  # aggregate -1 to +1
    news_impact: float      # 0-100
    key_events: list[str]
    news_items: list[NewsItem]
    analyzed_at: datetime
