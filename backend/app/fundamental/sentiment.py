from typing import NamedTuple

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.core.config import settings

_vader = SentimentIntensityAnalyzer()

# FinBERT is lazy-loaded only when SENTIMENT_PROVIDER=finbert
_finbert = None


def _load_finbert():
    global _finbert
    if _finbert is None:
        from transformers import pipeline  # noqa: PLC0415
        _finbert = pipeline(
            "text-classification",
            model="ProsusAI/finbert",
            truncation=True,
            max_length=512,
        )
    return _finbert


class SentimentResult(NamedTuple):
    score: float  # -1 to +1
    label: str    # positive | neutral | negative


def analyze(text: str) -> SentimentResult:
    if settings.SENTIMENT_PROVIDER == "finbert":
        model = _load_finbert()
        result = model(text[:512])[0]
        label: str = result["label"].lower()
        if label == "positive":
            score = result["score"]
        elif label == "negative":
            score = -result["score"]
        else:
            score = 0.0
        return SentimentResult(score=round(score, 4), label=label)

    # Default: VADER (fast, no GPU required)
    compound: float = _vader.polarity_scores(text)["compound"]
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return SentimentResult(score=round(compound, 4), label=label)
