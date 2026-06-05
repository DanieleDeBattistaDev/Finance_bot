import asyncio
from datetime import datetime

import praw

from app.core.config import settings

_SUBREDDITS = ["stocks", "investing", "wallstreetbets"]


async def fetch_posts(symbol: str, max_items: int = 20) -> list[dict]:
    if not settings.REDDIT_CLIENT_ID:
        raise ValueError("Reddit credentials not configured")

    reddit = praw.Reddit(
        client_id=settings.REDDIT_CLIENT_ID,
        client_secret=settings.REDDIT_CLIENT_SECRET,
        user_agent=settings.REDDIT_USER_AGENT,
    )

    per_sub = max(1, max_items // len(_SUBREDDITS))

    def _fetch() -> list[dict]:
        items = []
        for sub_name in _SUBREDDITS:
            try:
                sub = reddit.subreddit(sub_name)
                for post in sub.search(symbol, limit=per_sub, sort="new"):
                    items.append(
                        {
                            "title": post.title,
                            "url": f"https://reddit.com{post.permalink}",
                            "source": f"r/{sub_name}",
                            "published_at": datetime.fromtimestamp(post.created_utc),
                        }
                    )
            except Exception:
                pass
        return items

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch)
