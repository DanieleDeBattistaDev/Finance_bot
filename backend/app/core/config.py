from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ALPHA_VANTAGE_API_KEY: str = ""
    BINANCE_API_KEY: str = ""
    BINANCE_SECRET_KEY: str = ""
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/financebot"
    REDIS_URL: str = "redis://localhost:6379"
    # Reddit scraping
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "FinanceBot/1.0"
    # Sentiment: "vader" (default, fast) | "finbert" (accurate, requires torch)
    SENTIMENT_PROVIDER: str = "vader"
    # ML — override in Docker via env var
    ML_MODELS_DIR: str = str(
        __import__("pathlib").Path(__file__).parent.parent.parent.parent / "ml_models"
    )
    # Notifications
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    ALERT_EMAIL_TO: str = ""
    NTFY_TOPIC: str = ""           # ntfy.sh topic for push notifications
    NOTIFY_MIN_CONFIDENCE: float = 70.0  # only notify above this threshold

    model_config = {"env_file": ".env"}


settings = Settings()
