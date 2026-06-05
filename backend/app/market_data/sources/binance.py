from datetime import datetime, timedelta

import httpx
import pandas as pd

_INTERVAL_MAP: dict[str, str] = {
    "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
    "1h": "1h", "4h": "4h", "1d": "1d", "1wk": "1w",
}

_PERIOD_DAYS: dict[str, int] = {
    "1d": 1, "5d": 5, "1mo": 30, "3mo": 90,
    "6mo": 180, "1y": 365, "2y": 730, "5y": 1825,
}

_BASE_URL = "https://api.binance.com/api/v3/klines"


async def fetch(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    binance_symbol = symbol.upper().replace("-", "").replace("/", "")
    binance_interval = _INTERVAL_MAP.get(interval, "1d")
    days = _PERIOD_DAYS.get(period, 365)
    start_ms = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

    all_klines: list = []
    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            resp = await client.get(
                _BASE_URL,
                params={
                    "symbol": binance_symbol,
                    "interval": binance_interval,
                    "startTime": start_ms,
                    "limit": 1000,
                },
            )
            resp.raise_for_status()
            klines: list = resp.json()
            if not klines:
                break
            all_klines.extend(klines)
            if len(klines) < 1000:
                break
            start_ms = klines[-1][0] + 1  # advance past last candle

    if not all_klines:
        raise ValueError(f"Binance returned no data for {symbol}")

    records = [
        {
            "Date":   datetime.fromtimestamp(k[0] / 1000),
            "Open":   float(k[1]),
            "High":   float(k[2]),
            "Low":    float(k[3]),
            "Close":  float(k[4]),
            "Volume": float(k[5]),
        }
        for k in all_klines
    ]
    return pd.DataFrame(records).set_index("Date")
