import logging

from app.market_data.normalizer import normalize
from app.market_data.sources import alpha_vantage, binance, stooq, yahoo
from app.schemas.market import MarketDataResponse

logger = logging.getLogger(__name__)

_CRYPTO_BASES = {
    "BTC", "ETH", "BNB", "SOL", "ADA", "XRP",
    "DOGE", "AVAX", "MATIC", "DOT", "LINK", "LTC",
}

_STOCK_SOURCES = [
    ("yahoo", yahoo.fetch),
    ("alpha_vantage", alpha_vantage.fetch),
    ("stooq", stooq.fetch),
]

_CRYPTO_SOURCES = [
    ("binance", binance.fetch),
    ("yahoo", yahoo.fetch),
]


def _is_crypto(symbol: str) -> bool:
    base = symbol.upper().split("USDT")[0].split("-")[0].split("/")[0]
    return base in _CRYPTO_BASES


def _normalize_symbol(symbol: str) -> tuple[str, str]:
    """Return (display_symbol, binance_symbol). Adds USDT suffix for bare crypto tickers."""
    upper = symbol.upper()
    base = upper.split("USDT")[0].split("-")[0].split("/")[0]
    if base in _CRYPTO_BASES and not upper.endswith("USDT"):
        return upper, f"{base}USDT"
    return upper, upper


async def fetch_market_data(
    symbol: str,
    period: str = "1y",
    interval: str = "1d",
) -> MarketDataResponse:
    display_symbol, binance_symbol = _normalize_symbol(symbol)
    sources = _CRYPTO_SOURCES if _is_crypto(symbol) else _STOCK_SOURCES
    last_error: Exception | None = None

    for source_name, fetch_fn in sources:
        try:
            fetch_sym = binance_symbol if source_name == "binance" else display_symbol
            df = await fetch_fn(fetch_sym, period, interval)
            candles = normalize(display_symbol, df)
            logger.info("Fetched %d candles for %s from %s", len(candles), display_symbol, source_name)
            return MarketDataResponse(
                symbol=display_symbol,
                source=source_name,
                interval=interval,
                candles=candles,
            )
        except Exception as exc:
            logger.warning("%s failed for %s: %s", source_name, fetch_sym, exc)
            last_error = exc

    raise RuntimeError(f"All sources failed for {display_symbol}. Last error: {last_error}")
