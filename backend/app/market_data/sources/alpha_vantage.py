from datetime import datetime, timedelta

import httpx
import pandas as pd

from app.core.config import settings

_INTERVAL_MAP: dict[str, tuple[str, str | None]] = {
    "1d":  ("TIME_SERIES_DAILY_ADJUSTED", None),
    "1wk": ("TIME_SERIES_WEEKLY_ADJUSTED", None),
    "1h":  ("TIME_SERIES_INTRADAY", "60min"),
    "30m": ("TIME_SERIES_INTRADAY", "30min"),
    "15m": ("TIME_SERIES_INTRADAY", "15min"),
    "5m":  ("TIME_SERIES_INTRADAY", "5min"),
    "1m":  ("TIME_SERIES_INTRADAY", "1min"),
}

_PERIOD_DAYS: dict[str, int] = {
    "1d": 1, "5d": 5, "1mo": 30, "3mo": 90,
    "6mo": 180, "1y": 365, "2y": 730, "5y": 1825,
}


async def fetch(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    if not settings.ALPHA_VANTAGE_API_KEY:
        raise ValueError("ALPHA_VANTAGE_API_KEY not configured")

    function, av_interval = _INTERVAL_MAP.get(interval, ("TIME_SERIES_DAILY_ADJUSTED", None))

    params: dict = {
        "function": function,
        "symbol": symbol,
        "outputsize": "full",
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
    }
    if av_interval:
        params["interval"] = av_interval

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get("https://www.alphavantage.co/query", params=params)
        resp.raise_for_status()
        data = resp.json()

    ts_key = next((k for k in data if "Time Series" in k), None)
    if not ts_key:
        error_msg = data.get("Note") or data.get("Information") or str(data)
        raise ValueError(f"Alpha Vantage error for {symbol}: {error_msg}")

    cutoff = datetime.now() - timedelta(days=_PERIOD_DAYS.get(period, 365))
    records = []
    for date_str, vals in data[ts_key].items():
        dt = datetime.fromisoformat(date_str)
        if dt < cutoff:
            continue
        records.append({
            "Date": dt,
            "Open":   float(vals.get("1. open", 0)),
            "High":   float(vals.get("2. high", 0)),
            "Low":    float(vals.get("3. low", 0)),
            "Close":  float(vals.get("4. close") or vals.get("5. adjusted close", 0)),
            "Volume": float(vals.get("6. volume", 0)),
        })

    if not records:
        raise ValueError(f"Alpha Vantage returned no data for {symbol} ({period})")

    return pd.DataFrame(records).set_index("Date").sort_index()
