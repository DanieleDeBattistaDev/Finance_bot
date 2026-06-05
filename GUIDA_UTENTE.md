# Finance Bot — Guida Utente

## Cos'è Finance Bot

Finance Bot è un sistema di intelligenza finanziaria che analizza azioni e criptovalute e genera segnali di trading (compra / vendi / attendi) combinando:

- **Analisi tecnica** — RSI, MACD, Bollinger Bands, medie mobili, supporti e resistenze
- **Analisi fondamentale** — sentiment su notizie da Yahoo Finance, Reddit e MarketWatch
- **Machine Learning** — modelli XGBoost + LSTM addestrati sui dati storici del titolo
- **Notifiche** — Telegram, Email, push (ntfy.sh) quando scatta un segnale ad alta confidenza

---

## Avvio rapido

### 1. Backend (FastAPI)

```powershell
cd backend
pip install -r requirements.txt
py -m uvicorn main:app --reload
```

Il backend gira su `http://localhost:8000`.  
Documentazione API interattiva: `http://localhost:8000/docs`

### 2. Frontend (React)

```powershell
cd frontend
npm install
npm run dev
```

L'interfaccia è disponibile su `http://localhost:3000`.

> Entrambi devono girare contemporaneamente in due terminali separati.

---

## Simboli supportati

Usa sempre il **ticker di borsa**, non il nome dell'azienda:

| Azienda | Simbolo corretto |
|---|---|
| Apple | `AAPL` |
| NVIDIA | `NVDA` |
| Microsoft | `MSFT` |
| Tesla | `TSLA` |
| Amazon | `AMZN` |
| Bitcoin | `BTC` o `BTCUSDT` |
| Ethereum | `ETH` o `ETHUSDT` |
| Solana | `SOL` |

Per le crypto, puoi scrivere solo `BTC` — il sistema aggiunge automaticamente `USDT` per Binance.

---

## Interfaccia

### Dashboard

La schermata principale mostra:

- **Grafico a candele** — dati storici del titolo selezionato. Usa i pulsanti in alto a destra per cambiare periodo (1mo, 3mo, 6mo, 1y, 2y).
- **RSI / MACD** — attiva o disattiva gli overlay degli indicatori con i pulsanti sotto al grafico.
- **Segnale** — riquadro colorato con l'indicazione BUY / SELL / HOLD, la confidenza in percentuale e le motivazioni principali.
- **Sentiment** — punteggio aggregato delle notizie recenti (positivo = verde, negativo = rosso).
- **Livelli S/R** — supporti (in verde) e resistenze (in rosso) calcolati sui minimi e massimi locali.

### Analisi

Pagina di dettaglio con:

- Tabella degli ultimi valori di tutti gli indicatori (RSI, MACD, ATR, SMA 20/50/200, Bollinger)
- Grafici RSI e MACD espansi
- **Previsione ML** — direzione e probabilità di XGBoost e LSTM in ensemble
- Pulsante **Addestra modello** per avviare il training (vedi sezione ML)
- Feed notizie con sentiment per ogni articolo

### Impostazioni

Configura il comportamento dei segnali:

| Parametro | Opzioni | Descrizione |
|---|---|---|
| **Lingua** | 🇮🇹 Italiano / 🇬🇧 English | Cambia la lingua dell'interfaccia |
| **Simbolo** | testo libero | Titolo analizzato (es. `AAPL`) |
| **Arco temporale** | short / medium / long | Finestra dati usata per l'analisi |
| **Livello di rischio** | low / medium / high | Soglia minima per generare un segnale |
| **Tipo di strategia** | scalping / swing / long_term | Pesi dei tre motori di analisi |

**Arco temporale:**

| Valore | Dati scaricati | Intervallo candele |
|---|---|---|
| short | 1 mese | 1 ora |
| medium | 6 mesi | 1 giorno |
| long | 2 anni | 1 settimana |

**Livello di rischio (soglia segnale):**

| Valore | Soglia composita |
|---|---|
| low | 0.60 (segnali solo quando c'è forte accordo) |
| medium | 0.40 |
| high | 0.25 (segnali anche con accordo parziale) |

**Tipo di strategia (pesi dei motori):**

| Strategia | Tecnica | Fondamentale | ML |
|---|---|---|---|
| scalping | 70% | 10% | 20% |
| swing | 40% | 30% | 30% |
| long_term | 20% | 50% | 30% |

### Avvisi

Storico di tutti i segnali ricevuti (persistito nel browser). Ogni segnale mostra azione, confidenza e motivazioni. I segnali vengono aggiunti automaticamente ogni volta che il Dashboard calcola un nuovo segnale.

---

## Notifiche in tempo reale

### Toast in-app

Quando arriva un nuovo segnale (BUY o SELL) appare un popup in basso a destra con:
- Azione colorata (verde = compra, rosso = vendi)
- Barra di confidenza
- Prime due motivazioni
- Si chiude da solo dopo 6 secondi

### Notifiche esterne (Telegram, Email, Push)

Configurabili nel file `backend/.env`:

```env
# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=987654321

# Email (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tua@gmail.com
SMTP_PASSWORD=app-password-gmail
ALERT_EMAIL_TO=destinatario@email.com

# Push via ntfy.sh (no account richiesto)
NTFY_TOPIC=financebot-mio-topic

# Soglia minima per inviare notifiche (0-100)
NOTIFY_MIN_CONFIDENCE=70.0
```

Le notifiche scattano automaticamente quando:
1. Chiami manualmente `GET /api/v1/signals/{SYMBOL}`
2. Il WebSocket ricalcola il segnale ogni 5 minuti (mentre il frontend è aperto)

Solo i segnali BUY o SELL con confidenza ≥ `NOTIFY_MIN_CONFIDENCE` vengono inviati. I segnali HOLD vengono ignorati.

**Come configurare Telegram:**
1. Apri Telegram → cerca `@BotFather` → `/newbot` → copia il token
2. Scrivi un messaggio al tuo nuovo bot
3. Apri `https://api.telegram.org/bot<TOKEN>/getUpdates` nel browser
4. Copia il valore `"id"` dentro `"chat"` → è il tuo `TELEGRAM_CHAT_ID`

---

## Machine Learning

### Come funziona

Per ogni simbolo il sistema può addestrare due modelli:

- **XGBoost** — classificatore + regressore su 13 feature (RSI, MACD, Bollinger %, ATR, rendimenti, sentiment…)
- **LSTM** — rete neurale ricorrente PyTorch a 2 layer, addestrata su sequenze di 60 candele

La previsione finale è la media delle probabilità dei due modelli. La confidenza è la distanza dal 50% (es. prob=0.75 → confidenza=75%).

### Addestrare un modello

1. Vai su **Analisi** nella sidebar
2. Cerca il simbolo che ti interessa (es. `AAPL`)
3. Clicca **Addestra modello**
4. Guarda il terminale del backend — compariranno righe ogni 10 epoch:
   ```
   LSTM AAPL epoch 10/50 loss=0.6821
   LSTM AAPL epoch 20/50 loss=0.6543
   ...
   XGBoost AAPL accuracy: 0.523
   ```
5. Il training richiede **2–5 minuti** su CPU
6. Al termine, i modelli vengono salvati in `ml_models/xgboost/AAPL.joblib` e `ml_models/lstm/AAPL.pt`
7. Da quel momento il segnale includerà il contributo ML

> Prima di addestrare il modello, il segnale funziona comunque usando solo analisi tecnica e fondamentale (il peso ML viene azzerato automaticamente).

---

## WebSocket — prezzi live

Quando il frontend è aperto e connesso al backend, viene mantenuta una connessione WebSocket su `/ws/live/{SYMBOL}` che:

- Aggiorna il prezzo ogni **30 secondi**
- Ricalcola e invia il segnale ogni **5 minuti**

L'indicatore in alto a destra nella barra mostra lo stato della connessione:
- 🟢 **In diretta** — connesso, prezzi aggiornati in tempo reale
- ⚫ **Disconnesso** — backend non raggiungibile o connessione persa

---

## API REST

Il backend espone le seguenti route (documentazione completa su `/docs`):

| Metodo | Endpoint | Descrizione |
|---|---|---|
| GET | `/api/v1/market/{symbol}/history` | Candele storiche |
| GET | `/api/v1/market/{symbol}/latest` | Ultima candela |
| GET | `/api/v1/analysis/{symbol}/technical` | Indicatori tecnici |
| GET | `/api/v1/analysis/{symbol}/fundamental` | Notizie + sentiment |
| GET | `/api/v1/predictions/{symbol}` | Previsione ML |
| POST | `/api/v1/predictions/{symbol}/train` | Avvia training (202) |
| GET | `/api/v1/signals/{symbol}` | Segnale strategia completo |
| WS | `/ws/live/{symbol}` | Stream prezzi + segnali |

**Parametri del segnale:**

```
GET /api/v1/signals/AAPL?timeframe=medium&risk_level=medium&strategy_type=swing
```

---

## Variabili d'ambiente

Copia `backend/.env.example` in `backend/.env` e compila i valori:

```env
# Fonti dati (opzionali — Yahoo funziona senza chiavi)
ALPHA_VANTAGE_API_KEY=
BINANCE_API_KEY=
BINANCE_SECRET_KEY=

# Database (non richiesto per l'avvio base)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/financebot
REDIS_URL=redis://localhost:6379

# Reddit (per notizie aggiuntive)
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=

# Sentiment (vader = veloce, finbert = più preciso ma lento)
SENTIMENT_PROVIDER=vader

# Notifiche
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
SMTP_USER=
SMTP_PASSWORD=
ALERT_EMAIL_TO=
NTFY_TOPIC=
NOTIFY_MIN_CONFIDENCE=70.0
```

> Il backend si avvia correttamente anche con tutte le chiavi vuote. Le fonti non configurate vengono saltate in silenzio.

---

## Docker (opzionale)

Per avviare tutto con Docker Compose (richiede Docker Desktop installato):

```powershell
cd docker
docker compose up --build
```

Questo avvia: PostgreSQL, Redis, backend, worker Celery e frontend nginx su un unico comando.

---

## Risoluzione problemi comuni

| Problema | Causa | Soluzione |
|---|---|---|
| `uvicorn: command not found` | uvicorn non nel PATH | Usa `py -m uvicorn main:app --reload` |
| `npm: command not found` | npm non nel PATH | Eseguire dal terminale Node.js o aggiungere Node al PATH |
| `503 Service Unavailable` sul grafico | Backend non avviato | Avvia il backend prima del frontend |
| Simbolo non trovato (delisted) | Nome azienda invece del ticker | Usa il ticker (es. `NVDA` non `NVIDIA`) |
| `Model not trained yet` in Analisi | Nessun modello salvato | Clicca "Addestra modello" e aspetta 2–5 minuti |
| Alert History vuoto | Nessun segnale ancora generato | Naviga su Dashboard — il primo segnale viene salvato automaticamente |
| Toast non appare | Segnale HOLD o confidence bassa | Normale: i toast appaiono solo per BUY/SELL |
| Binance 400 Bad Request | Ticker crypto senza USDT | Usa `BTC` o `BTCUSDT` — entrambi funzionano |
