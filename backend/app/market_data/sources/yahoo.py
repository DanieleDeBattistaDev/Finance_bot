import asyncio
from functools import partial

import pandas as pd
import yfinance as yf


async def fetch(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    loop = asyncio.get_event_loop()
    ticker = yf.Ticker(symbol)
    df: pd.DataFrame = await loop.run_in_executor(
        None, partial(ticker.history, period=period, interval=interval)
    )
    if df.empty:
        raise ValueError(f"Yahoo Finance returned no data for {symbol}")
    return df
