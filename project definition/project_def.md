# FINANCE BOT - SYSTEM ARCHITECTURE

## OVERVIEW

This project is a multi-layer financial intelligence system composed of:

1. Market Data Layer
2. Technical Analysis Engine
3. Fundamental Analysis Engine (Scraping + NLP)
4. Machine Learning Prediction Engine
5. Strategy Decision Engine
6. Notification System

---

# 1. MARKET DATA LAYER

## Purpose
Collect historical and real-time market data.

## Data Sources
- Yahoo Finance API (primary)
- Alpha Vantage API (fallback)
- Binance API (crypto)
- Stooq (free fallback)

## Data Types
- OHLC (Open, High, Low, Close)
- Volume
- Adjusted close
- Time series candles

## Output Format
Standardized JSON:

{
  "symbol": "AAPL",
  "timestamp": "...",
  "open": 0,
  "high": 0,
  "low": 0,
  "close": 0,
  "volume": 0
}

---

# 2. TECHNICAL ANALYSIS ENGINE

## Purpose
Compute deterministic indicators from price history.

## Indicators
- RSI (14)
- MACD (12,26,9)
- Moving Averages (SMA, EMA)
- Bollinger Bands
- ATR (volatility)
- Support / Resistance levels

## Output
{
  "rsi": 0,
  "macd": 0,
  "signal": 0,
  "bollinger_upper": 0,
  "bollinger_lower": 0
}

---

# 3. FUNDAMENTAL ANALYSIS ENGINE

## Purpose
Scrape financial news and compute sentiment.

## Data Sources
- Yahoo Finance News
- Investing.com
- MarketWatch
- Reddit (r/stocks, r/investing)

## Pipeline
1. Scraping (Playwright / BeautifulSoup)
2. Cleaning text
3. NLP sentiment analysis
4. Event extraction

## Output
{
  "sentiment_score": -1 to +1,
  "news_impact": 0-100,
  "key_events": []
}

---

# 4. MACHINE LEARNING ENGINE

## Purpose
Predict future price movement.

## Models
- LSTM (time series)
- XGBoost (feature-based)
- Transformer (advanced stage)

## Features
- Technical indicators
- Sentiment score
- Volume anomalies
- Volatility

## Output
{
  "prediction": "up/down",
  "confidence": 0-1,
  "expected_return": %
}

---

# 5. STRATEGY ENGINE

## Purpose
Combine all signals into decision.

## Inputs
- Technical analysis
- Fundamental analysis
- ML prediction
- User preferences

## User Settings
- timeframe: short / medium / long
- risk level: low / medium / high
- strategy type: scalping / swing / long term

## Output
{
  "action": "buy/sell/hold",
  "confidence": 0-100,
  "reasoning": []
}

---

# 6. NOTIFICATION SYSTEM

## Channels
- Push notifications
- Telegram bot
- Email alerts

## Triggers
- strong buy/sell signal
- high confidence ML prediction
- sudden market change

---

# CLAUDE CODE AGENTS

## backend-engineer
Design APIs, services, and orchestration layer.

## data-engineer
Handles ingestion, pipelines, and cleaning.

## scraping-agent
Builds resilient scraping pipelines.

## ml-engineer
Designs and trains predictive models.

## strategy-engineer
Combines signals into trading decisions.

## devops-engineer
Handles deployment, docker, monitoring.

---

# DEVELOPMENT FLOW

1. Build Market Data Layer
2. Build Technical Analysis Engine
3. Build Scraping + Fundamental Engine
4. Train ML Models
5. Build Strategy Engine
6. Add Notifications
7. Deploy system

---

# RULES

- All data must be normalized to standard schema
- All models must be backtestable
- No single source of truth: ensemble approach
- Every prediction must include confidence score
- System must be modular and testable