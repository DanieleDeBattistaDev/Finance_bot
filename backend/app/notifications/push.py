import httpx

from app.core.config import settings
from app.schemas.signal import SignalResponse

_ACTION_EMOJI = {"buy": "🟢", "sell": "🔴", "hold": "⚪"}
_PRIORITY = {"buy": "high", "sell": "high", "hold": "default"}


async def send_signal(signal: SignalResponse) -> None:
    """
    Sends a push notification via ntfy.sh.
    No account required for testing; set NTFY_TOPIC to a unique string.
    Production: self-host ntfy or replace with FCM.
    """
    if not settings.NTFY_TOPIC:
        raise ValueError("NTFY_TOPIC not configured")

    emoji = _ACTION_EMOJI.get(signal.action, "⚪")
    title = f"{emoji} {signal.symbol} — {signal.action.upper()} ({signal.confidence:.0f}%)"
    body = signal.reasoning[1] if len(signal.reasoning) > 1 else signal.reasoning[0]

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"https://ntfy.sh/{settings.NTFY_TOPIC}",
            content=body.encode(),
            headers={
                "Title": title,
                "Priority": _PRIORITY.get(signal.action, "default"),
                "Tags": signal.action,
            },
        )
        resp.raise_for_status()
