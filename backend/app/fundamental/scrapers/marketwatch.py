import httpx
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


async def fetch_news(symbol: str, max_items: int = 10) -> list[dict]:
    url = f"https://www.marketwatch.com/investing/stock/{symbol.lower()}"

    async with httpx.AsyncClient(timeout=15, headers=_HEADERS, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    items = []
    for article in soup.select("div.article__content")[:max_items]:
        headline = article.select_one("h3.article__headline a")
        if not headline:
            continue
        items.append(
            {
                "title": headline.get_text(strip=True),
                "url": headline.get("href", ""),
                "source": "MarketWatch",
                "published_at": None,
            }
        )
    return items
