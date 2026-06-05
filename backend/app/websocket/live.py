import asyncio
import logging
from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.market_data.fetcher import fetch_market_data
from app.strategy.engine import generate_signal

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])

PRICE_POLL_INTERVAL = 30   # seconds between price updates
SIGNAL_POLL_INTERVAL = 300  # seconds between signal recalculations


class _ConnectionManager:
    def __init__(self) -> None:
        self._subs: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, symbol: str, ws: WebSocket) -> None:
        await ws.accept()
        self._subs[symbol].add(ws)
        logger.info("WS connect %s  (subscribers: %d)", symbol, len(self._subs[symbol]))

    def disconnect(self, symbol: str, ws: WebSocket) -> None:
        self._subs[symbol].discard(ws)
        logger.info("WS disconnect %s (subscribers: %d)", symbol, len(self._subs[symbol]))

    async def send(self, symbol: str, payload: dict) -> None:
        dead: set[WebSocket] = set()
        for ws in list(self._subs[symbol]):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._subs[symbol].discard(ws)

    def has_subscribers(self, symbol: str) -> bool:
        return bool(self._subs[symbol])


manager = _ConnectionManager()


async def _price_loop(symbol: str) -> None:
    """Fetch latest candle and broadcast to all subscribers for `symbol`."""
    while manager.has_subscribers(symbol):
        try:
            data = await fetch_market_data(symbol, period="5d", interval="1d")
            if data.candles:
                c = data.candles[-1]
                prev = data.candles[-2] if len(data.candles) >= 2 else c
                change_pct = ((c.close - prev.close) / prev.close * 100) if prev.close else 0.0
                await manager.send(symbol, {
                    "type": "price_update",
                    "symbol": symbol,
                    "timestamp": c.timestamp.isoformat(),
                    "open": c.open,
                    "high": c.high,
                    "low": c.low,
                    "close": c.close,
                    "volume": c.volume,
                    "change_pct": round(change_pct, 4),
                })
        except Exception as exc:
            logger.warning("Price loop error for %s: %s", symbol, exc)
        await asyncio.sleep(PRICE_POLL_INTERVAL)


async def _signal_loop(symbol: str) -> None:
    """Recalculate strategy signal periodically and broadcast if actionable."""
    while manager.has_subscribers(symbol):
        await asyncio.sleep(SIGNAL_POLL_INTERVAL)
        if not manager.has_subscribers(symbol):
            break
        try:
            signal = await generate_signal(symbol)
            if signal.action != "hold":
                await manager.send(symbol, {
                    "type": "signal",
                    "symbol": symbol,
                    "action": signal.action,
                    "confidence": signal.confidence,
                    "reasoning": signal.reasoning[:3],
                    "generated_at": signal.generated_at.isoformat(),
                })
        except Exception as exc:
            logger.warning("Signal loop error for %s: %s", symbol, exc)


@router.websocket("/ws/live/{symbol}")
async def websocket_live(ws: WebSocket, symbol: str) -> None:
    symbol = symbol.upper()
    await manager.connect(symbol, ws)

    # Start background loops only for the first subscriber
    price_task = asyncio.create_task(_price_loop(symbol))
    signal_task = asyncio.create_task(_signal_loop(symbol))

    try:
        await ws.send_json({
            "type": "connected",
            "symbol": symbol,
            "message": f"Streaming {symbol} — price every {PRICE_POLL_INTERVAL}s, signals every {SIGNAL_POLL_INTERVAL}s",
            "timestamp": datetime.now().isoformat(),
        })

        while True:
            # Keep connection alive; handle client pings or disconnect
            msg = await ws.receive_text()
            if msg == "ping":
                await ws.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(symbol, ws)
        if not manager.has_subscribers(symbol):
            price_task.cancel()
            signal_task.cancel()
