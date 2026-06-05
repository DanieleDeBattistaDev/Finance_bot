import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.schemas.signal import SignalResponse

_ACTION_COLOR = {"buy": "#16a34a", "sell": "#dc2626", "hold": "#6b7280"}


def _html(signal: SignalResponse) -> str:
    color = _ACTION_COLOR.get(signal.action, "#6b7280")
    reasons_html = "".join(f"<li>{r}</li>" for r in signal.reasoning[1:6])
    return f"""
    <html><body style="font-family:sans-serif;max-width:600px;margin:auto">
      <h2 style="color:{color}">{signal.symbol} — {signal.action.upper()}</h2>
      <table>
        <tr><td><b>Confidence</b></td><td>{signal.confidence:.1f}%</td></tr>
        <tr><td><b>Strategy</b></td><td>{signal.strategy_type}</td></tr>
        <tr><td><b>Risk</b></td><td>{signal.risk_level}</td></tr>
        <tr><td><b>Timeframe</b></td><td>{signal.timeframe}</td></tr>
      </table>
      <h3>Top signals</h3>
      <ul>{reasons_html}</ul>
      <hr><small>Generated at {signal.generated_at.strftime('%Y-%m-%d %H:%M UTC')}</small>
    </body></html>
    """


async def send_signal(signal: SignalResponse) -> None:
    if not settings.SMTP_USER or not settings.ALERT_EMAIL_TO:
        raise ValueError("SMTP_USER / ALERT_EMAIL_TO not configured")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[FinanceBot] {signal.symbol} {signal.action.upper()} — {signal.confidence:.0f}% confidence"
    msg["From"] = settings.SMTP_USER
    msg["To"] = settings.ALERT_EMAIL_TO
    msg.attach(MIMEText(_html(signal), "html"))

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )
