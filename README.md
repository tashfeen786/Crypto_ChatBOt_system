# 🤖 Crypto AI Advisor

> AI-powered cryptocurrency investment platform with real-time trading and portfolio management

![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js)
![React](https://img.shields.io/badge/React-18-blue?style=flat-square&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-Python-green?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?style=flat-square&logo=postgresql)

## ✨ Features

- 💬 **AI Chatbot** - Natural language crypto investment advice
- 📊 **Real-time Trading** - Buy/sell 644+ cryptocurrencies with live Binance data
- 💼 **Portfolio Management** - Track holdings, P&L, and performance
- 🎯 **Risk Analysis** - Intelligent recommendations based on user risk tolerance
- 📰 **Market News** - Latest crypto news with sentiment categorization
- 🔔 **Price Alerts** - Custom notifications for tracked coins
- 🔐 **Secure Auth** - User authentication and session management

## 🚀 Tech Stack

**Frontend:** Next.js 14, React 18, Tailwind CSS, Lucide Icons  
**Backend:** FastAPI, PostgreSQL, SQLAlchemy  
**APIs:** Binance (prices), Groq, CryptoNews

## 📦 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.13+
- PostgreSQL 14+

### Installation

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
DATABASE_URL=postgresql://user:password@localhost:5432/crypto_advisor
SECRET_KEY=your-secret-key
BINANCE_API_KEY=your-key
OPENAI_API_KEY=your-key

# Initialize database
python init_db.py

# Run server
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install

# Create .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# Run dev server
npm run dev
```

Visit `http://localhost:3000` 🎉

## 📁 Project Structure

```
crypto-rag-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py                 
│   │   ├── config.py               
│   │   │
│   │   ├── models/
│   │   │   ├── user.py             
│   │   │   ├── coin.py             
│   │   │   └── alert.py            
│   │   │
│   │   ├── services/
│   │   │   ├── binance.py          
│   │   │   ├── news.py             
│   │   │   ├── risk_engine.py      
│   │   │   ├── trading.py          
│   │   │   └── alerts_checker.py   
│   │   │
│   │   └── routes/
│   │       ├── auth.py           
│   │       ├── chat.py             
│   │       ├── coins.py            
│   │       ├── trading.py          
│   │       ├── portfolio.py        
│   │       ├── news.py             
│   │       └── alerts.py           
│   │
│   └── requirements.txt            
│
└── frontend/
    ├── app/
    │   ├── page.js                  
    │   ├── login/page.js           
    │   ├── signup/page.js          
    │   ├── charts/page.js          
    │   ├── trading/page.js         
    │   ├── portfolio/page.js       
    │   ├── alerts/page.js        
    │   └── news/page.js            
    │
    ├── components/
    │   ├── Navbar.js              
    │   ├── Sidebar.js              
    │   ├── ChatInterface.js        
    │   ├── TradingCard.js          
    │   ├── PortfolioTable.js       
    │   ├── AlertCard.js            
    │   └── NewsCard.js             
    │
    ├── lib/
    │   └── api.js                  
    │
    └── package.json                
```

## 🔌 Key API Endpoints

```
POST   /api/chat/                    # Send chat message
GET    /api/coins/prices             # Get live prices
POST   /api/trading/buy              # Execute buy order
GET    /api/portfolio/{userId}       # Get portfolio
POST   /api/auth/login               # User login
```

Full API docs: `http://localhost:8000/docs`

## 🎨 Screenshots

| Feature | Description |
|---------|-------------|
| **Sign In** | Beautiful auth with gradient design |
| **Chat Interface** | AI chatbot with live price updates |
| **Trading Dashboard** | 644+ coins with Binance integration |
| **Portfolio** | Track holdings and P&L |
| **News Feed** | Latest market news |
| **Price Alerts** | Custom notifications |
| **Profile** | Account settings & risk tolerance |

## 🚢 Deployment

**Frontend (Vercel):**
```bash
vercel --prod
```

**Backend (Railway):**
- Connect GitHub repo
- Add environment variables
- Deploy automatically

## 🤝 Contributing

1. Fork the repo
2. Create your branch: `git checkout -b feature/NewFeature`
3. Commit changes: `git commit -m 'Add NewFeature'`
4. Push: `git push origin feature/NewFeature`
5. Open a Pull Request

## 👨‍💻 Author

**Tashfeen Aziz**  
GitHub: https://github.com/tashfeen786
Email: tashfeen247@gmail.com
---

⭐ **Star this repo if you find it helpful!**

*Made with ❤️ and ☕*
