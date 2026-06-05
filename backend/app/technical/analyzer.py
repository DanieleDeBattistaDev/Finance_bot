import pandas as pd

from app.market_data.fetcher import fetch_market_data
from app.schemas.analysis import TechnicalAnalysisResponse
from app.technical.indicators import compute_all
from app.technical.support_resistance import find_levels


def _candles_to_df(candles: list) -> pd.DataFrame:
    records = [
        {
            "Date":   c.timestamp,
            "Open":   c.open,
            "High":   c.high,
            "Low":    c.low,
            "Close":  c.close,
            "Volume": c.volume,
        }
        for c in candles
    ]
    return pd.DataFrame(records).set_index("Date").sort_index()


async def analyze(
    symbol: str,
    period: str = "1y",
    interval: str = "1d",
) -> TechnicalAnalysisResponse:
    market_data = await fetch_market_data(symbol, period, interval)
    df = _candles_to_df(market_data.candles)

    series = compute_all(df)
    support, resistance = find_levels(df)

    return TechnicalAnalysisResponse(
        symbol=symbol,
        interval=interval,
        series=series,
        support_levels=support,
        resistance_levels=resistance,
    )
