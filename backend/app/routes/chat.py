# app/routes/chat.py - ENGLISH ONLY VERSION
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
import os
from groq import Groq
import requests
import sqlite3

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info(f"✅ Groq AI initialized: {GROQ_MODEL}")
    except Exception as e:
        logger.error(f"❌ Groq init failed: {e}")
        groq_client = None
else:
    logger.warning("⚠️ GROQ_API_KEY not found")
    groq_client = None

# Database connection
def get_db_connection():
    """Get SQLite database connection"""
    try:
        conn = sqlite3.connect('crypto_advisor.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Database error: {e}")
        return None

def get_user_from_db(user_id: str) -> Dict:
    """Fetch user profile from database"""
    try:
        conn = get_db_connection()
        if not conn:
            return {"balance": 1000.0, "risk_tolerance": 5}
        
        cursor = conn.cursor()
        cursor.execute(
            "SELECT balance, risk_tolerance FROM users WHERE user_id = ?",
            (user_id,)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {"balance": user['balance'], "risk_tolerance": user['risk_tolerance']}
        else:
            return {"balance": 1000.0, "risk_tolerance": 5}
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return {"balance": 1000.0, "risk_tolerance": 5}

def save_chat_to_db(user_id: str, message: str, response: str, coins: List[str]):
    """Save chat history to database"""
    try:
        conn = get_db_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_history (user_id, message, response, coins_mentioned)
            VALUES (?, ?, ?, ?)
        """, (user_id, message, response, ','.join(coins)))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Chat saved for user: {user_id}")
    except Exception as e:
        logger.error(f"Error saving chat: {e}")

class ChatRequest(BaseModel):
    message: str
    user_id: str
    user_risk_tolerance: Optional[int] = None
    user_balance: Optional[float] = None
    include_trading: bool = False

class ChatResponse(BaseModel):
    response: str
    coins_mentioned: List[str] = []
    risk_analysis: Optional[dict] = None

# Professional English-only system prompt
SYSTEM_PROMPT = """You are a professional cryptocurrency investment advisor. 

🎯 YOUR ROLE:
- Provide accurate, data-driven investment advice
- Analyze market conditions objectively
- Consider user's risk tolerance and balance
- Give practical, actionable recommendations

📊 RESPONSE GUIDELINES:
1. Always mention current market prices when discussing coins
2. Explain risks clearly and honestly
3. Keep responses concise (under 200 words)
4. Use professional yet friendly tone
5. Include specific numbers and percentages
6. Give clear buy/sell/hold recommendations when asked

💼 RESPONSE STRUCTURE:
- Start with direct answer to the question
- Include relevant market data (prices, 24h changes)
- Consider user's profile (balance, risk tolerance)
- End with clear recommendation

❗ IMPORTANT:
- Use ONLY English language
- Be conversational but professional
- Provide honest analysis, not just hype
- Warn about high volatility when relevant
- Give portfolio allocation suggestions based on risk level

Example Response:
"Bitcoin is currently trading at $67,855, up 1.88% in the last 24 hours. Given your balance of $100 and risk tolerance of 4/10, I'd recommend a conservative approach. Consider investing 30-40% ($30-40) in Bitcoin as it's the most stable cryptocurrency. The recent uptrend looks promising, but remember crypto is volatile. Start small and dollar-cost average your entries."

Remember: Provide real value, not generic advice. Use the live market data provided!"""

async def get_live_market_data() -> Dict:
    """Fetch live prices from Binance"""
    try:
        response = requests.get(
            "https://api.binance.com/api/v3/ticker/24hr",
            timeout=3
        )
        
        if response.status_code != 200:
            logger.warning("Binance API failed, using cached prices")
            return get_cached_prices()
        
        tickers = response.json()
        top_pairs = {
            "BTCUSDT": "BTC", "ETHUSDT": "ETH", "BNBUSDT": "BNB",
            "SOLUSDT": "SOL", "XRPUSDT": "XRP", "ADAUSDT": "ADA",
            "DOGEUSDT": "DOGE", "MATICUSDT": "MATIC", "DOTUSDT": "DOT",
            "AVAXUSDT": "AVAX"
        }
        
        market_data = {}
        ticker_dict = {t['symbol']: t for t in tickers}
        
        for pair, symbol in top_pairs.items():
            if pair in ticker_dict:
                ticker = ticker_dict[pair]
                market_data[symbol] = {
                    "price": float(ticker['lastPrice']),
                    "change": float(ticker['priceChangePercent']),
                    "high": float(ticker['highPrice']),
                    "low": float(ticker['lowPrice']),
                    "volume": float(ticker['volume'])
                }
        
        logger.info(f"✅ Fetched live data for {len(market_data)} coins")
        return market_data
        
    except Exception as e:
        logger.error(f"❌ Market data error: {e}")
        return get_cached_prices()

def extract_mentioned_coins(text: str) -> List[str]:
    """Extract cryptocurrency symbols from text"""
    coins = []
    text_upper = text.upper()
    
    # Common crypto symbols and names
    crypto_keywords = {
        'BITCOIN': 'BTC', 'BTC': 'BTC',
        'ETHEREUM': 'ETH', 'ETH': 'ETH',
        'BINANCE': 'BNB', 'BNB': 'BNB',
        'SOLANA': 'SOL', 'SOL': 'SOL',
        'RIPPLE': 'XRP', 'XRP': 'XRP',
        'CARDANO': 'ADA', 'ADA': 'ADA',
        'DOGECOIN': 'DOGE', 'DOGE': 'DOGE',
        'POLYGON': 'MATIC', 'MATIC': 'MATIC',
        'POLKADOT': 'DOT', 'DOT': 'DOT',
        'AVALANCHE': 'AVAX', 'AVAX': 'AVAX'
    }
    
    for keyword, symbol in crypto_keywords.items():
        if keyword in text_upper:
            coins.append(symbol)
    
    return list(set(coins))

def create_market_context(market_data: Dict, mentioned_coins: List[str]) -> str:
    """Create formatted market data context"""
    if not mentioned_coins:
        # Show top 3 coins if none mentioned
        mentioned_coins = ['BTC', 'ETH', 'BNB']
    
    context_lines = ["📊 CURRENT MARKET DATA:"]
    
    for coin in mentioned_coins[:5]:  # Max 5 coins
        if coin in market_data:
            data = market_data[coin]
            trend = "📈" if data['change'] >= 0 else "📉"
            context_lines.append(
                f"{coin}: ${data['price']:,.2f} "
                f"({trend} {data['change']:+.2f}% 24h) "
                f"[High: ${data['high']:,.2f}, Low: ${data['low']:,.2f}]"
            )
    
    return "\n".join(context_lines)

async def generate_ai_response(
    user_message: str,
    user_balance: float,
    user_risk: int,
    market_data: Dict,
    mentioned_coins: List[str]
) -> str:
    """Generate AI response using Groq"""
    
    market_context = create_market_context(market_data, mentioned_coins)
    
    user_prompt = f"""USER PROFILE:
💰 Balance: ${user_balance:,.2f}
🎯 Risk Tolerance: {user_risk}/10 ({'Conservative' if user_risk <= 3 else 'Moderate' if user_risk <= 6 else 'Aggressive'})

{market_context}

USER QUESTION: {user_message}

Provide a clear, professional investment analysis in English."""

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"❌ Groq error: {e}")
        raise

def generate_fallback_response(
    message: str,
    balance: float,
    risk: int,
    market_data: Dict,
    mentioned_coins: List[str]
) -> str:
    """Smart fallback when AI is unavailable"""
    
    msg_lower = message.lower()
    
    # Greeting
    if any(word in msg_lower for word in ['hi', 'hello', 'hey']):
        return f"""Hello! I'm your crypto investment advisor.

Your Profile:
💰 Balance: ${balance:,.2f}
🎯 Risk Tolerance: {risk}/10

You can ask me:
• "What's Bitcoin's current price?"
• "Should I invest in Ethereum?"
• "Which coin is best for my risk level?"

How can I help you today?"""
    
    # Specific coin queries
    if mentioned_coins:
        coin = mentioned_coins[0]
        if coin in market_data:
            data = market_data[coin]
            trend = "upward" if data['change'] >= 0 else "downward"
            
            # Calculate suggested investment
            risk_multiplier = 0.3 if risk <= 3 else 0.5 if risk <= 6 else 0.7
            suggested_amount = balance * risk_multiplier
            
            return f"""**{coin} Analysis**

📊 Current Price: ${data['price']:,.2f}
📈 24h Change: {data['change']:+.2f}%
📊 24h Range: ${data['low']:,.2f} - ${data['high']:,.2f}

**Market Status:** {trend.capitalize()} trend

**For Your Profile (Risk {risk}/10):**
• Recommended Investment: ${suggested_amount:.2f} ({risk_multiplier*100:.0f}% of balance)
• Remaining Balance: ${balance - suggested_amount:.2f}

**Recommendation:**
{coin} shows a {trend} trend. {"This could be a good entry point." if abs(data['change']) < 3 else "High volatility - consider dollar-cost averaging."} 

Given your {'conservative' if risk <= 3 else 'moderate' if risk <= 6 else 'aggressive'} risk profile, {'proceed with caution' if risk <= 3 else 'balanced approach recommended' if risk <= 6 else 'you can take advantage of the volatility'}.

Need more specific advice? Just ask!"""
    
    # General market query
    if any(word in msg_lower for word in ['market', 'today', 'now', 'currently']):
        top_coins = []
        for coin in ['BTC', 'ETH', 'BNB']:
            if coin in market_data:
                data = market_data[coin]
                top_coins.append(f"• {coin}: ${data['price']:,.2f} ({data['change']:+.2f}%)")
        
        return f"""**Current Market Overview**

{chr(10).join(top_coins)}

**Market Sentiment:** {"Bullish 📈" if sum(market_data[c]['change'] for c in ['BTC', 'ETH'] if c in market_data) > 0 else "Bearish 📉"}

**Your Profile:**
Balance: ${balance:,.2f} | Risk: {risk}/10

Ask about specific coins for detailed analysis!"""
    
    # Default
    return f"""I'm here to help with crypto investment advice!

Your Profile:
💰 ${balance:,.2f} available
🎯 Risk Level: {risk}/10

Try asking:
• "What's Bitcoin's price?"
• "Should I buy Ethereum now?"
• "Which coin matches my risk level?"

What would you like to know?"""

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint - English only, professional advice"""
    try:
        logger.info(f"💬 Chat from {request.user_id}: {request.message[:50]}...")
        
        # Get user profile from database
        user_data = get_user_from_db(request.user_id)
        user_balance = request.user_balance or user_data['balance']
        user_risk = request.user_risk_tolerance or user_data['risk_tolerance']
        
        logger.info(f"👤 Profile: ${user_balance} | Risk: {user_risk}/10")
        
        # Get live market data
        market_data = await get_live_market_data()
        
        # Extract mentioned coins
        mentioned_coins = extract_mentioned_coins(request.message)
        logger.info(f"🪙 Coins mentioned: {mentioned_coins}")
        
        # Generate response
        if groq_client:
            try:
                response_text = await generate_ai_response(
                    request.message,
                    user_balance,
                    user_risk,
                    market_data,
                    mentioned_coins
                )
            except Exception as e:
                logger.error(f"AI generation failed, using fallback: {e}")
                response_text = generate_fallback_response(
                    request.message,
                    user_balance,
                    user_risk,
                    market_data,
                    mentioned_coins
                )
        else:
            response_text = generate_fallback_response(
                request.message,
                user_balance,
                user_risk,
                market_data,
                mentioned_coins
            )
        
        # Risk analysis
        risk_analysis = {
            "risk_score": user_risk,
            "risk_level": "low" if user_risk <= 3 else "moderate" if user_risk <= 6 else "high",
            "recommendation": "Conservative approach" if user_risk <= 3 else "Balanced strategy" if user_risk <= 6 else "Aggressive trading"
        }
        
        # Save to database
        save_chat_to_db(request.user_id, request.message, response_text, mentioned_coins)
        
        logger.info(f"✅ Response generated ({len(response_text)} chars)")
        
        return ChatResponse(
            response=response_text,
            coins_mentioned=mentioned_coins,
            risk_analysis=risk_analysis
        )
        
    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}", exc_info=True)
        return ChatResponse(
            response=f"I apologize, but I encountered an error. Please try again or rephrase your question.",
            coins_mentioned=[],
            risk_analysis={"risk_score": 5, "risk_level": "moderate"}
        )

def get_cached_prices() -> Dict:
    """Fallback cached prices"""
    return {
        "BTC": {"price": 87000, "change": 0.5, "high": 88000, "low": 86000, "volume": 0},
        "ETH": {"price": 2900, "change": -0.3, "high": 2950, "low": 2850, "volume": 0},
        "BNB": {"price": 310, "change": 0.8, "high": 315, "low": 305, "volume": 0},
        "SOL": {"price": 98, "change": -1.2, "high": 100, "low": 95, "volume": 0},
        "XRP": {"price": 1.84, "change": 2.1, "high": 1.90, "low": 1.80, "volume": 0},
        "ADA": {"price": 0.35, "change": -0.5, "high": 0.36, "low": 0.34, "volume": 0},
        "DOGE": {"price": 0.12, "change": 3.2, "high": 0.13, "low": 0.11, "volume": 0},
        "MATIC": {"price": 0.38, "change": -0.3, "high": 0.39, "low": 0.37, "volume": 0},
        "DOT": {"price": 1.87, "change": 1.5, "high": 1.90, "low": 1.85, "volume": 0},
        "AVAX": {"price": 12.65, "change": 0.9, "high": 12.80, "low": 12.50, "volume": 0}
    }

@router.get("/health")
async def chat_health():
    """Health check endpoint"""
    return {
        "status": "operational",
        "ai_model": GROQ_MODEL if groq_client else "fallback",
        "language": "English Only",
        "features": ["live_prices", "risk_analysis", "portfolio_recommendations"]
    }

@router.get("/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 10):
    """Get user's chat history"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database unavailable")
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM chat_history 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        history = [dict(row) for row in rows]
        conn.close()
        
        return {"user_id": user_id, "history": history, "count": len(history)}
        
    except Exception as e:
        logger.error(f"History error: {e}")
        raise HTTPException(status_code=500, detail=str(e))