import asyncio
from datetime import datetime

import yfinance as yf


async def fetch_news(symbol: str, max_items: int = 20) -> list[dict]:
    loop = asyncio.get_event_loop()
    ticker = yf.Ticker(symbol)
    news: list[dict] = await loop.run_in_executor(None, lambda: ticker.news)

    results = []
    for item in (news or [])[:max_items]:
        results.append(
            {
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "source": item.get("publisher", "Yahoo Finance"),
                "published_at": (
                    datetime.fromtimestamp(item["providerPublishTime"])
                    if item.get("providerPublishTime")
                    else None
                ),
            }
        )
    return results
