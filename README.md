# 🤖 CryptoChat — AI-Powered Crypto Investment Platform

![Python](https://img.shields.io/badge/Python-3.13+-blue?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?style=flat&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat&logo=next.js)
![LangChain](https://img.shields.io/badge/LangChain-RAG-purple?style=flat)
![Groq](https://img.shields.io/badge/Groq-LLaMA3-orange?style=flat)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?style=flat&logo=postgresql)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Embeddings-yellow?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

> 🚀 A production-grade **Generative AI + FinTech** platform that combines
> RAG-based LLM reasoning with real-time market data to deliver
> personalized cryptocurrency investment guidance.

---

## 🎯 Problem Statement

Crypto markets are complex, volatile, and overwhelming for most investors:

- ❌ No personalized guidance based on individual risk tolerance
- ❌ Real-time data and AI reasoning are siloed — not combined
- ❌ Most tools either show data OR give advice — not both simultaneously

**CryptoChat solves this** by fusing live market data from Binance with
RAG-powered LLM reasoning to give users personalized, context-aware
investment recommendations in plain language.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🧠 **RAG Chatbot** | LangChain + Groq LLaMA3 for intelligent investment advice |
| 📊 **Live Prices** | Real-time data for 644+ cryptocurrencies via Binance API |
| 🔍 **Semantic Search** | HuggingFace embeddings for context-aware retrieval |
| 💼 **Portfolio Tracker** | Real-time P&L tracking and holdings management |
| ⚡ **Risk Engine** | Personalized recommendations based on risk tolerance |
| 📰 **Market News** | Latest crypto news with sentiment categorization |
| 🔔 **Price Alerts** | Custom notifications for tracked coins |
| 🔐 **Auth System** | Secure user authentication and session management |

---

## 🧠 RAG Architecture

```
User Query (e.g. "I have $500, low risk — what should I buy?")
        ↓
HuggingFace Embedding Model
(sentence-transformers — converts query to vector)
        ↓
PostgreSQL Vector Search
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

## 🛠️ Tech Stack

### Backend
| Layer | Technology |
|-------|-----------|
| 🧠 LLM Inference | Groq API (LLaMA 3) |
| 🔗 RAG Framework | LangChain |
| 🔍 Embeddings | HuggingFace (sentence-transformers) |
| 📈 Live Market Data | Binance API |
| ⚙️ API Framework | FastAPI + Python 3.13 |
| 🗄️ Database | PostgreSQL + SQLAlchemy |
| 🛡️ Validation | Pydantic v2 |

### Frontend
| Layer | Technology |
|-------|-----------|
| 🎨 Framework | Next.js 14 + React 18 |
| 💅 Styling | Tailwind CSS |
| 🔌 API Client | Custom REST client |

---

## 💬 Example Interaction

```
👤 User: "I have $500 and I'm a low-risk investor. 
         What crypto should I buy right now?"

🤖 CryptoChat: "Based on your $500 budget and low-risk profile,
               here's my analysis using current market data:

               ✅ Bitcoin (BTC) — $XX,XXX | Market dominance 52%
               Most stable option. Recommended allocation: $300

               ✅ Ethereum (ETH) — $X,XXX | Strong fundamentals  
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
│           ├── news.py               # News endpoints
│           └── alerts.py             # Alert endpoints
│
└── frontend/
    ├── app/
    │   ├── page.js                   # Main dashboard
    │   ├── login/page.js             # Authentication
    │   ├── trading/page.js           # Trading interface
    │   ├── portfolio/page.js         # Portfolio tracker
    │   ├── charts/page.js            # Price charts
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
GET    /api/coins/prices        # Live prices (644+ coins via Binance)
POST   /api/trading/buy         # Execute buy order
GET    /api/portfolio/{userId}  # Get user portfolio & P&L
POST   /api/auth/login          # User authentication
GET    /api/news/               # Latest crypto news
POST   /api/alerts/             # Set price alert
```

📖 Full interactive API docs: `http://localhost:8000/docs`

---

## 🚢 Deployment

**Frontend → Vercel:**
```bash
vercel --prod
```

**Backend → Railway:**
- Connect GitHub repo
- Add environment variables
- Auto-deploys on push ✅

---

## 📸 Screenshots

> 🔜 Screenshots coming soon

---

## 👨‍💻 Author

**Tashfeen Aziz** — AI/ML Engineer & Python Developer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://linkedin.com/in/tashfeen-aziz-b51361292)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://github.com/tashfeen786)
[![Email](https://img.shields.io/badge/Email-Contact-red?logo=gmail)](mailto:tashfeen247@gmail.com)

---

⭐ **If you found this project helpful, please give it a star!**

*Built with ❤️ — Combining GenAI + FinTech for smarter investing*
