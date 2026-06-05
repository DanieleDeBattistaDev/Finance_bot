import asyncio
from datetime import datetime, timedelta
from functools import partial

import pandas as pd

_PERIOD_DAYS: dict[str, int] = {
    "1d": 1, "5d": 5, "1mo": 30, "3mo": 90,
    "6mo": 180, "1y": 365, "2y": 730, "5y": 1825,
}


async def fetch(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    try:
        import pandas_datareader.data as web  # lazy — not compatible with Python 3.14+
    except Exception as exc:
        raise ValueError(f"Stooq unavailable (pandas_datareader import failed: {exc})") from exc

    days = _PERIOD_DAYS.get(period, 365)
    end = datetime.now()
    start = end - timedelta(days=days)

    loop = asyncio.get_event_loop()
    df: pd.DataFrame = await loop.run_in_executor(
        None, partial(web.DataReader, symbol, "stooq", start, end)
    )

    if df.empty:
        raise ValueError(f"Stooq returned no data for {symbol}")

    return df.sort_index()
