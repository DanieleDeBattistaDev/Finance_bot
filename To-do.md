# 📌 FINANCE BOT — TODO LIST (IMPLEMENTATION UPGRADE)

> Stato: app già esistente  
> Obiettivo: aggiungere feature avanzate senza riscrivere l’architettura

---

# 🧱 LAYER 1 — DATA & INFRA IMPROVEMENTS

## ☐ Standardizzare data ingestion
- [ ] Unificare formato candle (OHLCV standard)
- [ ] Centralizzare ingestion service
- [ ] Aggiungere caching Redis per prezzi e indicatori
- [ ] Implementare fallback tra provider (Yahoo / Binance)

---

## ☐ Ottimizzazione API
- [ ] Rate limit handler per provider esterni
- [ ] Retry strategy con exponential backoff
- [ ] Logging errori ingestion

---

# 📊 LAYER 2 — ANALYSIS ENGINE (ENHANCEMENT)

## ☐ Migliorare feature engineering
- [ ] Aggiungere ATR, VWAP, volatility index
- [ ] Aggiungere support/resistance dinamici
- [ ] Normalizzazione feature per ML

---

## ☐ Sentiment engine upgrade
- [ ] Aggregazione news multi-source
- [ ] Reddit sentiment scoring migliorato
- [ ] Peso dinamico sentiment nel signal engine

---

# 🧠 LAYER 3 — ML ENGINE IMPROVEMENTS

## ☐ Modelli ML
- [ ] Integrare LightGBM
- [ ] Integrare CatBoost
- [ ] Ottimizzare LSTM (sequence tuning)

---

## ☐ Training pipeline
- [ ] Implementare walk-forward validation
- [ ] Aggiungere dataset versioning
- [ ] Salvare metriche per ogni training run

---

## ☐ Ensemble system
- [ ] Implementare voting tra modelli
- [ ] Calibrazione probabilità output ML

---

# 🚨 LAYER 4 — SIGNAL ENGINE (CORE UPGRADE)

## ☐ Miglioramento logica segnali
- [ ] Rendere pesi dinamici (non statici 0.4/0.3/0.3)
- [ ] Aggiungere regime detection (trend vs sideways)
- [ ] Aggiungere volatility filter

---

## ☐ Signal explainability
- [ ] Espandere "reasons" con ranking importanza feature
- [ ] Aggiungere confidence breakdown (tech/fund/ML)

---

# 📈 LAYER 5 — SIGNALS ON CHART (CRITICO)

## ☐ Backend
- [ ] Creare endpoint:
- [ ] Restituire storico segnali con timestamp e prezzo
- [ ] Persistenza segnali nel database

---

## ☐ Frontend (GRAFICO)
- [ ] Aggiungere marker BUY / SELL sul candlestick chart
- [ ] Tooltip con:
- signal type
- confidence
- reasons
- [ ] Click su marker → dettaglio segnale

---

## ☐ UX miglioramenti grafico
- [ ] Colori coerenti (BUY verde, SELL rosso)
- [ ] Filtri: mostra solo BUY / SELL / entrambi
- [ ] Toggle segnali ON/OFF

---

# 🧪 LAYER 6 — BACKTESTING (NUOVO MODULO)

## ☐ Engine base
- [ ] Simulatore ordini storico
- [ ] Fee + slippage model
- [ ] Equity curve generator

---

## ☐ API
- [ ] POST /backtests/run
- [ ] GET /backtests/{id}

---

## ☐ Metrics
- [ ] Sharpe Ratio
- [ ] Sortino Ratio
- [ ] Max Drawdown
- [ ] Win Rate
- [ ] Profit Factor

---

# 🧾 LAYER 7 — PAPER TRADING

## ☐ Core system
- [ ] Portfolio virtuale
- [ ] Gestione posizioni
- [ ] Ordini simulated execution

---

## ☐ Tracking
- [ ] PnL realtime
- [ ] Equity curve
- [ ] Storico trade

---

# 📉 LAYER 8 — SIGNAL PERFORMANCE TRACKING

## ☐ Database
- [ ] Tabella signal history
- [ ] Tabella signal outcomes

---

## ☐ Evaluation engine
- [ ] Calcolo ritorno 1d / 7d / 30d
- [ ] Job schedulato (Celery beat)

---

## ☐ Dashboard
- [ ] Success rate segnali
- [ ] ROI medio per segnale
- [ ] Best / worst signals

---

# 👤 LAYER 9 — USER SYSTEM (SAAS READINESS)

## ☐ Auth
- [ ] JWT login/register
- [ ] Refresh tokens

---

## ☐ User features
- [ ] Watchlist per utente
- [ ] Preferenze strategia
- [ ] Storico segnali personalizzato

---

# ⚡ LAYER 10 — REALTIME SYSTEM

## ☐ WebSocket
- [ ] /ws/live/{symbol}
- [ ] Price updates (30s)
- [ ] Signal updates (5m)

---

## ☐ Stability
- [ ] auto-reconnect frontend
- [ ] heartbeat ping/pong

---

# 🔔 LAYER 11 — NOTIFICATIONS

## ☐ Canali
- [ ] Telegram integration
- [ ] Email alerts
- [ ] Push (ntfy)

---

## ☐ Regole notifiche
- [ ] solo BUY / SELL
- [ ] soglia confidence configurabile
- [ ] anti-spam rate limit

---

# 🚀 LAYER 12 — PRODUCTION DEPLOY

## ☐ Dockerization
- [ ] backend container
- [ ] frontend container
- [ ] postgres
- [ ] redis
- [ ] celery worker
- [ ] celery beat

---

## ☐ Nginx
- [ ] reverse proxy
- [ ] HTTPS redirect
- [ ] gzip + caching

---

## ☐ Hosting setup
- [ ] VPS provisioning
- [ ] environment separation (dev/prod)
- [ ] domain + SSL (Let's Encrypt)

---

# 📊 PRIORITÀ DI SVILUPPO

## 🔥 PRIORITÀ MASSIMA
- [ ] Signals on chart (feature differenziante)
- [ ] Backtesting engine base
- [ ] Signal performance tracking

---

## ⚡ PRIORITÀ MEDIA
- [ ] Paper trading
- [ ] ML improvements
- [ ] WebSocket stabilità

---

## 🧠 PRIORITÀ LUNGO TERMINE
- [ ] User system SaaS
- [ ] notifiche avanzate
- [ ] deploy scalabile

---

# 🧩 NOTE ARCHITETTURALI

- NON riscrivere backend esistente
- aggiungere moduli indipendenti
- mantenere FastAPI come core API gateway
- separare ML / signals / data ingestion
- ogni feature deve essere plug-in compatibile