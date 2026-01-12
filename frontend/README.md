# 🤖 Crypto AI Advisor - Frontend

AI-powered cryptocurrency investment advisor chatbot built with Next.js 14

## 📁 Project Structure

```
crypto-ai-advisor/
├── app/
│   ├── globals.css          # Global styles & animations
│   ├── layout.js            # Root layout
│   └── page.js              # Main page
├── components/
│   ├── ChatInterface.js     # Chat UI & message handling
│   ├── Navbar.js            # Top navigation bar
│   └── Sidebar.js           # Market info & portfolio
├── lib/
│   └── api.js               # API client & endpoints
├── .env.local               # Environment variables
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # Tailwind CSS config
├── package.json             # Dependencies
└── README.md                # Ye file
```

## 🚀 Quick Setup

### Step 1: Dependencies Install Karo

```bash
npm install
```

### Step 2: Environment Variables Setup

`.env.local` file banao aur backend URL add karo:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 3: Development Server Start Karo

```bash
npm run dev
```

App `http://localhost:3000` par chal jayegi

## 🔧 Backend Integration

### API Configuration

Backend URL ko change karne ke liye:

1. `.env.local` file mein `NEXT_PUBLIC_API_URL` update karo
2. Ya directly `lib/api.js` mein `API_URL` change karo

### Backend Requirements

Ye frontend expect kar raha hai ke backend in endpoints provide kare:

#### Chat Endpoints

- `POST /api/chat/` - Main chat endpoint
- `POST /api/chat/quick-advice` - Quick coin advice
- `POST /api/chat/smart-allocation` - Portfolio allocation

#### Coins Endpoints

- `GET /api/coins/prices` - Live coin prices
- `GET /api/coins/:symbol` - Coin details
- `GET /api/coins/` - Top coins list
- `GET /api/coins/risk/:symbol` - Risk analysis
- `GET /api/coins/market/summary` - Market summary

#### Trading Endpoints

- `POST /api/trading/buy` - Execute buy
- `POST /api/trading/sell` - Execute sell
- `POST /api/trading/simulate-buy` - Simulate trade
- `POST /api/trading/position-size` - Calculate position

#### Portfolio Endpoints

- `GET /api/portfolio/:userId` - Get portfolio
- `POST /api/portfolio/add-holding` - Add holding
- `GET /api/portfolio/:userId/performance` - Performance

#### User Endpoints

- `POST /api/users/register` - Register user
- `GET /api/users/:userId` - Get profile
- `PUT /api/users/:userId` - Update profile
- `GET /api/users/:userId/balance` - Get balance

## 🎨 Features

### ✅ Implemented

- 💬 Real-time chat interface with AI bot
- 📊 Live cryptocurrency prices sidebar
- 📱 Fully responsive (mobile + desktop)
- 🎭 Beautiful glass-morphism UI
- ⚡ Fast & smooth animations
- 🔄 Auto-refresh prices every 10s
- 📈 Risk analysis display
- 💰 Portfolio summary

### 🔜 Coming Soon

- User authentication
- Real portfolio tracking
- Trade execution
- Price alerts
- Historical charts

## 🎯 Usage Examples

### Chat with Bot

```javascript
// User types: "Bitcoin mein invest karna chahiye?"
// Bot responds with analysis + risk score
```

### Check Live Prices

Sidebar mein top 5 coins ki live prices show hoti hain with 24h change

### View Portfolio

Sidebar mein portfolio balance, P&L aur risk profile

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State**: React Hooks

## 📝 Important Notes

1. **Backend Connection**: Frontend backend se independently chal sakta hai, but features limited rahenge
2. **API URL**: Production mein proper HTTPS URL use karo
3. **CORS**: Backend mein CORS properly configure karo
4. **Error Handling**: API errors automatically handle hoti hain

## 🐛 Common Issues

### Backend Not Connected

```
Error: "Sorry, kuch error aa gayi. Backend running hai?"
```

**Solution**: Check karo backend running hai ya nahi port 8000 par

### CORS Error

```
Error: "CORS policy blocked"
```

**Solution**: Backend mein CORS enable karo for frontend URL

### Environment Variables Not Working

**Solution**: Server restart karo after changing `.env.local`

## 📦 Build for Production

```bash
# Production build
npm run build

# Start production server
npm start
```

## 🤝 Contributing

Issues aur improvements ke liye PR welcome hai!

## 📄 License

MIT License - Free to use!

---

Made with ❤️ by Tashfeen Aziz
