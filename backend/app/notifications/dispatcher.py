import asyncio
import logging

from app.core.config import settings
from app.notifications import email, push, telegram
from app.schemas.signal import SignalResponse

logger = logging.getLogger(__name__)


async def dispatch(signal: SignalResponse) -> None:
    """Send notifications for strong signals. Silent no-op if no channels configured."""
    if signal.action == "hold" or signal.confidence < settings.NOTIFY_MIN_CONFIDENCE:
        return

    tasks: list = []
    labels: list[str] = []

    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
        tasks.append(telegram.send_signal(signal))
        labels.append("telegram")

    if settings.SMTP_USER and settings.ALERT_EMAIL_TO:
        tasks.append(email.send_signal(signal))
        labels.append("email")

    if settings.NTFY_TOPIC:
        tasks.append(push.send_signal(signal))
        labels.append("push")

    if not tasks:
        logger.debug("No notification channels configured — skipping dispatch for %s", signal.symbol)
        return

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for label, result in zip(labels, results):
        if isinstance(result, Exception):
            logger.warning("Notification channel '%s' failed: %s", label, result)
        else:
            logger.info("Notification sent via %s for %s %s", label, signal.symbol, signal.action)
