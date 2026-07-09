# 🤖 CryptoChat — AI-Powered Crypto Investment Platform

![Python](https://img.shields.io/badge/Python-3.13-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-latest-green) ![Next.js](https://img.shields.io/badge/Next.js-14-black) ![LangChain](https://img.shields.io/badge/LangChain-latest-purple) ![Groq](https://img.shields.io/badge/Groq-LLaMA3-orange) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue) ![Pinecone](https://img.shields.io/badge/Pinecone-VectorDB-green)

> A full-stack AI investment platform that combines RAG-based LLM reasoning, real-time Binance market data, and trained ML prediction models to deliver personalized cryptocurrency investment guidance.

---

## 🎯 Problem Statement

Retail crypto investors make emotional, uninformed decisions:

- ❌ No personalized guidance based on individual risk tolerance
- ❌ Real-time market data and AI reasoning are siloed — not combined
- ❌ No accessible tool that shows data, gives advice, AND predicts market direction simultaneously

**CryptoChat solves this** by fusing live Binance data with RAG-powered LLM reasoning and trained ML models to give users personalized, context-aware investment recommendations in plain language.

---

## 📸 Screenshots

### AI Investment Chatbot — Live Market Analysis
![Chat Interface](screenshots/chat.png)
*RAG chatbot analyzing SOL in real-time — current price, 24h range, risk-based investment recommendation*

### ML Market Prediction Dashboard
![ML Predictions](screenshots/predictions.png)
*3 trained ML models predicting ATR Regime, Trend Label, and Trend Inversion using live Birdeye data*

### Trading Dashboard — 681+ Coins
![Trading Dashboard](screenshots/trading.png)
*Live prices for 681+ cryptocurrencies via Binance API with buy/sell execution and portfolio tracking*

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🧠 RAG Chatbot | LangChain + Groq LLaMA3 — investment advice with live market context |
| 📊 Live Prices | Real-time data for 681+ cryptocurrencies via Binance API |
| 🔍 Vector Search | Pinecone vector database for semantic context retrieval |
| 🤖 ML Predictions | 3 trained models: ATR Regime, Trend Label, Trend Inversion |
| 💼 Portfolio Tracker | Real-time P&L tracking and holdings management |
| ⚡ Risk Engine | Personalized recommendations based on user risk tolerance (1-10) |
| 📰 Market News | Latest crypto news with sentiment categorization |
| 🔔 Price Alerts | Custom notifications for tracked coins |
| 🔐 Auth System | Secure user authentication and session management |

---

## 🧠 RAG Architecture

```
User Query (e.g. "I have $500, low risk — what should I buy?")
        ↓
HuggingFace Embedding Model
(sentence-transformers — converts query to vector)
        ↓
Pinecone Vector Search
(retrieves relevant crypto knowledge context)
        ↓
Binance API
(fetches live prices for relevant coins)
        ↓
LangChain RAG Pipeline
(combines context + live data into prompt)
        ↓
Groq API — LLaMA 3
(ultra-fast LLM inference)
        ↓
Personalized Investment Recommendation
```

---

## 🤖 ML Prediction Models

Three models trained on real Birdeye SOL token data:

| Model | Task | Input Features |
|-------|------|----------------|
| ATR Regime Classifier | Volatility detection (Low/Medium/High) | Price, Volume, ATR indicators |
| Trend Label Classifier | Market direction (Bullish/Bearish/Neutral) | OHLCV + momentum features |
| Trend Inversion Detector | Reversal risk (Likely/Unlikely) | Price action patterns |

Live data is fetched from Birdeye API → features engineered → models predict in real-time.

---

## 🛠️ Tech Stack

### Backend
| Layer | Technology |
|-------|-----------|
| 🧠 LLM Inference | Groq API (LLaMA 3) |
| 🔗 RAG Framework | LangChain |
| 🔍 Vector Database | Pinecone |
| 🔍 Embeddings | HuggingFace (sentence-transformers) |
| 📈 Market Data | Binance API + Birdeye API |
| ⚙️ API Framework | FastAPI + Python 3.13 |
| 🗄️ Database | PostgreSQL + SQLAlchemy |
| 🛡️ Validation | Pydantic v2 |

### Frontend
| Layer | Technology |
|-------|-----------|
| 🎨 Framework | Next.js 14 + React 18 |
| 💅 Styling | Tailwind CSS |

---

## 💬 Example Interaction

```
👤 User: "I have $500 and I'm a low-risk investor. 
         What crypto should I buy right now?"

🤖 CryptoChat: "Based on your $500 budget and low-risk profile,
               here's my analysis using current market data:

               ✅ Bitcoin (BTC) — $62,945 | Market dominance 52%
               Most stable option. Recommended allocation: $300

               ✅ Ethereum (ETH) — $1,772 | Strong fundamentals  
               Second most stable. Recommended allocation: $150

               ⚠️ Avoid high-volatility altcoins with your risk level.

               [Based on live Binance data + risk analysis]"
```

---

## 🏗️ Project Structure

```
Crypto_ChatBOt_system/
│
├── backend/
│   └── app/
│       ├── main.py                   # FastAPI entry point
│       ├── config.py                 # Environment & settings
│       │
│       ├── models/
│       │   ├── user.py               # User data model
│       │   ├── coin.py               # Cryptocurrency model
│       │   └── alert.py              # Price alert model
│       │
│       ├── services/
│       │   ├── binance.py            # Live price fetching
│       │   ├── birdeye.py            # ML model data source
│       │   ├── risk_engine.py        # Risk analysis logic
│       │   ├── trading.py            # Buy/sell execution
│       │   ├── news.py               # Market news service
│       │   └── alerts_checker.py     # Alert monitoring
│       │
│       └── routes/
│           ├── auth.py               # Authentication endpoints
│           ├── chat.py               # RAG chatbot endpoints
│           ├── coins.py              # Coin data endpoints
│           ├── trading.py            # Trading endpoints
│           ├── portfolio.py          # Portfolio endpoints
│           ├── predictions.py        # ML prediction endpoints
│           ├── news.py               # News endpoints
│           └── alerts.py             # Alert endpoints
│
└── frontend/
    ├── app/
    │   ├── page.js                   # Main dashboard
    │   ├── login/page.js             # Authentication
    │   ├── trading/page.js           # Trading interface
    │   ├── portfolio/page.js         # Portfolio tracker
    │   ├── predictions/page.js       # ML predictions
    │   ├── alerts/page.js            # Price alerts
    │   └── news/page.js              # Market news
    │
    └── components/
        ├── ChatInterface.js          # AI chatbot UI
        ├── TradingCard.js            # Trading component
        ├── PortfolioTable.js         # Portfolio display
        ├── AlertCard.js              # Alert management
        └── NewsCard.js               # News display
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- Node.js 18+
- PostgreSQL 14+
- Pinecone account (free tier)
- Groq API key (free tier)
- Binance API key

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/crypto_advisor
SECRET_KEY=your-secret-key
GROQ_API_KEY=your-groq-api-key
BINANCE_API_KEY=your-binance-api-key
PINECONE_API_KEY=your-pinecone-api-key
BIRDEYE_API_KEY=your-birdeye-api-key
HUGGINGFACE_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

```bash
python init_db.py          # Initialize database
uvicorn main:app --reload  # Start server
```

### Frontend Setup
```bash
cd frontend
npm install
```

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
npm run dev
```

Visit `http://localhost:3000` 🎉

---

## 🔌 Key API Endpoints

```
POST   /api/chat/               # RAG chatbot — AI investment advice
GET    /api/coins/prices        # Live prices (681+ coins via Binance)
POST   /api/trading/buy         # Execute buy order
GET    /api/portfolio/{userId}  # Get user portfolio & P&L
POST   /api/auth/login          # User authentication
GET    /api/news/               # Latest crypto news
POST   /api/alerts/             # Set price alert
GET    /api/predictions/{token} # ML market predictions
```

📖 Full interactive API docs: `http://localhost:8000/docs`

---

## 👨‍💻 Author

**Tashfeen Aziz** — AI/ML Engineer & Python Developer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/tashfeen-aziz)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/tashfeen786)
[![Email](https://img.shields.io/badge/Email-Contact-red)](mailto:tashfeen247@gmail.com)

---

⭐ If you found this project helpful, please give it a star!

*Built combining Generative AI + FinTech for smarter investing*
