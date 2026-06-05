import asyncio
import logging
from datetime import datetime

from app.fundamental.scrapers import marketwatch, reddit, yahoo_news
from app.fundamental.sentiment import analyze
from app.schemas.fundamental import FundamentalAnalysisResponse, NewsItem

logger = logging.getLogger(__name__)


async def _gather_news(symbol: str) -> list[dict]:
    results = await asyncio.gather(
        yahoo_news.fetch_news(symbol),
        marketwatch.fetch_news(symbol),
        reddit.fetch_posts(symbol),
        return_exceptions=True,
    )

    all_news: list[dict] = []
    for source_name, result in zip(["yahoo_news", "marketwatch", "reddit"], results):
        if isinstance(result, Exception):
            logger.warning("Scraper %s failed for %s: %s", source_name, symbol, result)
        else:
            all_news.extend(result)

    # Deduplicate by normalised title prefix
    seen: set[str] = set()
    deduped: list[dict] = []
    for item in all_news:
        key = item["title"].lower()[:60]
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    return deduped


async def analyze_fundamental(symbol: str) -> FundamentalAnalysisResponse:
    raw_news = await _gather_news(symbol)

    if not raw_news:
        return FundamentalAnalysisResponse(
            symbol=symbol,
            sentiment_score=0.0,
            news_impact=0.0,
            key_events=[],
            news_items=[],
            analyzed_at=datetime.now(),
        )

    news_items: list[NewsItem] = []
    for item in raw_news:
        result = analyze(item["title"])
        news_items.append(
            NewsItem(
                title=item["title"],
                source=item.get("source", "unknown"),
                url=item.get("url", ""),
                published_at=item.get("published_at"),
                sentiment_score=result.score,
                sentiment_label=result.label,
            )
        )

    scores = [n.sentiment_score for n in news_items]
    aggregate_score = round(sum(scores) / len(scores), 4)

    # news_impact 0-100: more articles + stronger sentiment = higher impact
    news_impact = round(min(len(news_items) * abs(aggregate_score) * 20, 100.0), 2)

    # key_events: top 5 headlines by absolute sentiment magnitude
    key_events = [
        n.title
        for n in sorted(news_items, key=lambda x: abs(x.sentiment_score), reverse=True)[:5]
    ]

    return FundamentalAnalysisResponse(
        symbol=symbol,
        sentiment_score=aggregate_score,
        news_impact=news_impact,
        key_events=key_events,
        news_items=news_items,
        analyzed_at=datetime.now(),
    )
