import pandas as pd

from app.schemas.market import Candle


def normalize(symbol: str, df: pd.DataFrame) -> list[Candle]:
    candles: list[Candle] = []
    for ts, row in df.iterrows():
        timestamp = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
        # Strip timezone info — store everything as naive UTC
        if hasattr(timestamp, "tzinfo") and timestamp.tzinfo is not None:
            timestamp = timestamp.replace(tzinfo=None)

        candles.append(
            Candle(
                symbol=symbol,
                timestamp=timestamp,
                open=float(row.get("Open", row.get("open", 0))),
                high=float(row.get("High", row.get("high", 0))),
                low=float(row.get("Low", row.get("low", 0))),
                close=float(row.get("Close", row.get("close", 0))),
                volume=float(row.get("Volume", row.get("volume", 0))),
            )
        )
    return candles
