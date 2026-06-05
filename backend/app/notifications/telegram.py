import httpx

from app.core.config import settings
from app.schemas.signal import SignalResponse

_ACTION_EMOJI = {"buy": "🟢", "sell": "🔴", "hold": "⚪"}


def _format(signal: SignalResponse) -> str:
    emoji = _ACTION_EMOJI.get(signal.action, "⚪")
    lines = [
        f"{emoji} *{signal.symbol}* — {signal.action.upper()}",
        f"Confidence: *{signal.confidence:.1f}%*",
        f"Strategy: {signal.strategy_type} | Risk: {signal.risk_level} | Timeframe: {signal.timeframe}",
        "",
        "*Top signals:*",
    ]
    for reason in signal.reasoning[1:6]:   # skip composite score line
        lines.append(f"• {reason}")
    return "\n".join(lines)


async def send_signal(signal: SignalResponse) -> None:
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        raise ValueError("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not configured")

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": _format(signal),
        "parse_mode": "Markdown",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
