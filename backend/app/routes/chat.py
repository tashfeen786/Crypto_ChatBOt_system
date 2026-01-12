from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Union
import logging
import os
from groq import Groq
import requests
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError

from app.database.base import get_db

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
    logger.warning("⚠️ GROQ_API_KEY not found - using fallback responses")
    groq_client = None

def normalize_user_id(user_id: Union[str, int]) -> int:
    """Convert user_id to integer, handling various formats"""
    try:
        if isinstance(user_id, int):
            return user_id
        if isinstance(user_id, str):
            # Handle "user_123" format
            if user_id.startswith('user_'):
                return int(user_id.replace('user_', ''))
            # Handle numeric string
            return int(user_id)
        return 4  # Default fallback
    except (ValueError, TypeError):
        logger.warning(f"⚠️ Invalid user_id format: {user_id}, using default: 4")
        return 4

def get_user_from_db(user_id: Union[str, int], db: Session) -> Dict:
    """Fetch user profile from PostgreSQL with better error handling"""
    try:
        numeric_id = normalize_user_id(user_id)
        
        result = db.execute(
            text("SELECT balance, risk_tolerance FROM users WHERE id = :user_id"),
            {"user_id": numeric_id}
        ).fetchone()
        
        if result:
            logger.info(f"✅ User {numeric_id} found in DB: balance=${result.balance}, risk={result.risk_tolerance}")
            return {
                "balance": float(result.balance), 
                "risk_tolerance": int(result.risk_tolerance)
            }
        else:
            logger.warning(f"⚠️ User {numeric_id} not found, using defaults")
            return {"balance": 1000.0, "risk_tolerance": 5}
            
    except ProgrammingError as e:
        logger.error(f"❌ Table doesn't exist: {e}")
        return {"balance": 1000.0, "risk_tolerance": 5}
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error fetching user: {e}")
        return {"balance": 1000.0, "risk_tolerance": 5}
    except Exception as e:
        logger.error(f"❌ Unexpected error fetching user: {e}")
        return {"balance": 1000.0, "risk_tolerance": 5}

def save_chat_to_db(user_id: Union[str, int], message: str, response: str, coins: List[str], db: Session):
    """Save chat history to PostgreSQL with error handling"""
    try:
        numeric_id = normalize_user_id(user_id)
        
        # Check if table exists first
        table_check = db.execute(
            text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'chat_history'
                )
            """)
        ).scalar()
        
        if not table_check:
            logger.warning("⚠️ chat_history table doesn't exist, skipping save")
            return
        
        db.execute(
            text("""
                INSERT INTO chat_history (user_id, message, response, coins_mentioned, timestamp)
                VALUES (:user_id, :message, :response, :coins, NOW())
            """),
            {
                "user_id": numeric_id,
                "message": message[:1000],  # Limit length
                "response": response[:2000],  # Limit length
                "coins": ','.join(coins) if coins else ''
            }
        )
        db.commit()
        logger.info(f"✅ Chat saved for user: {numeric_id}")
        
    except ProgrammingError as e:
        logger.error(f"❌ Table structure error: {e}")
        db.rollback()
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error saving chat: {e}")
        db.rollback()
    except Exception as e:
        logger.error(f"❌ Unexpected error saving chat: {e}")
        db.rollback()

class ChatRequest(BaseModel):
    message: str
    user_id: Union[str, int]  # Accept both string and int
    user_risk_tolerance: Optional[int] = None
    user_balance: Optional[float] = None
    include_trading: bool = False

class ChatResponse(BaseModel):
    response: str
    coins_mentioned: List[str] = []
    risk_analysis: Optional[dict] = None
    status: str = "success"

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
    """Fetch live prices from Binance with fallback"""
    try:
        response = requests.get(
            "https://api.binance.com/api/v3/ticker/24hr",
            timeout=5
        )
        
        if response.status_code != 200:
            logger.warning("⚠️ Binance API failed, using cached prices")
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
        mentioned_coins = ['BTC', 'ETH', 'BNB']
    
    context_lines = ["📊 CURRENT MARKET DATA:"]
    
    for coin in mentioned_coins[:5]:
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
    if any(word in msg_lower for word in ['hi', 'hello', 'hey', 'salam']):
        return f"""Hello! 👋 I'm your crypto investment advisor.

**Your Profile:**
💰 Balance: ${balance:,.2f}
🎯 Risk Tolerance: {risk}/10

**You can ask me:**
• "What's Bitcoin's current price?"
• "Should I invest in Ethereum?"
• "Which coin is best for my risk level?"
• "Give me portfolio allocation advice"

How can I help you today?"""
    
    # Specific coin queries
    if mentioned_coins:
        coin = mentioned_coins[0]
        if coin in market_data:
            data = market_data[coin]
            trend = "upward" if data['change'] >= 0 else "downward"
            
            risk_multiplier = 0.3 if risk <= 3 else 0.5 if risk <= 6 else 0.7
            suggested_amount = balance * risk_multiplier
            
            return f"""**{coin} Market Analysis**

📊 **Current Price:** ${data['price']:,.2f}
📈 **24h Change:** {data['change']:+.2f}%
📊 **24h Range:** ${data['low']:,.2f} - ${data['high']:,.2f}

**Market Status:** {trend.capitalize()} trend

**Investment Recommendation (Risk {risk}/10):**
• Suggested Amount: ${suggested_amount:.2f} ({risk_multiplier*100:.0f}% of balance)
• Keep Reserved: ${balance - suggested_amount:.2f}

**Analysis:**
{coin} is showing a {trend} trend. {"This could be a good entry point for gradual accumulation." if abs(data['change']) < 3 else "High volatility detected - consider dollar-cost averaging to reduce risk."} 

Given your {'conservative' if risk <= 3 else 'moderate' if risk <= 6 else 'aggressive'} risk profile, {'I recommend starting with a small test position' if risk <= 3 else 'balanced approach with gradual entries is advisable' if risk <= 6 else 'you can consider taking advantage of this volatility'}.

💡 **Pro Tip:** Never invest more than you can afford to lose!"""
    
    # General market query
    return f"""**Crypto Market Overview**

I'm here to help with investment advice! Here's what I can do:

**Your Profile:**
💰 Available: ${balance:,.2f}
🎯 Risk Level: {risk}/10 ({'Conservative' if risk <= 3 else 'Moderate' if risk <= 6 else 'Aggressive'})

**Popular Questions:**
• "What's the price of Bitcoin?"
• "Should I buy Ethereum right now?"
• "Which altcoin matches my risk level?"
• "How should I split my investment?"

Try asking about a specific cryptocurrency!"""

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Main chat endpoint - Professional investment advice with database integration"""
    try:
        # Normalize user_id
        numeric_user_id = normalize_user_id(request.user_id)
        logger.info(f"💬 Chat from user {numeric_user_id}: {request.message[:50]}...")
        
        # Get user profile from PostgreSQL
        user_data = get_user_from_db(numeric_user_id, db)
        user_balance = request.user_balance if request.user_balance is not None else user_data['balance']
        user_risk = request.user_risk_tolerance if request.user_risk_tolerance is not None else user_data['risk_tolerance']
        
        logger.info(f"👤 Profile: ${user_balance} | Risk: {user_risk}/10")
        
        # Get live market data
        market_data = await get_live_market_data()
        
        # Extract mentioned coins
        mentioned_coins = extract_mentioned_coins(request.message)
        if mentioned_coins:
            logger.info(f"🪙 Coins mentioned: {mentioned_coins}")
        
        # Generate response
        response_text = ""
        try:
            if groq_client:
                response_text = await generate_ai_response(
                    request.message,
                    user_balance,
                    user_risk,
                    market_data,
                    mentioned_coins
                )
                logger.info("✅ AI response generated")
            else:
                response_text = generate_fallback_response(
                    request.message,
                    user_balance,
                    user_risk,
                    market_data,
                    mentioned_coins
                )
                logger.info("✅ Fallback response generated")
        except Exception as ai_error:
            logger.error(f"❌ AI generation failed: {ai_error}")
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
        
        # Save to database (non-blocking)
        try:
            save_chat_to_db(numeric_user_id, request.message, response_text, mentioned_coins, db)
        except Exception as db_error:
            logger.error(f"⚠️ Failed to save chat to DB (non-critical): {db_error}")
        
        logger.info(f"✅ Response sent ({len(response_text)} chars)")
        
        return ChatResponse(
            response=response_text,
            coins_mentioned=mentioned_coins,
            risk_analysis=risk_analysis,
            status="success"
        )
        
    except Exception as e:
        logger.error(f"❌ Critical chat error: {str(e)}", exc_info=True)
        return ChatResponse(
            response="I apologize, but I encountered an error processing your request. Please try again or rephrase your question. If the issue persists, please check the backend logs.",
            coins_mentioned=[],
            risk_analysis={"risk_score": 5, "risk_level": "moderate", "recommendation": "System error"},
            status="error"
        )

@router.get("/history/{user_id}")
async def get_chat_history(user_id: Union[str, int], limit: int = 10, db: Session = Depends(get_db)):
    """Get user's chat history from PostgreSQL"""
    try:
        numeric_id = normalize_user_id(user_id)
        
        # Check if table exists
        table_check = db.execute(
            text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'chat_history'
                )
            """)
        ).scalar()
        
        if not table_check:
            return {
                "user_id": numeric_id,
                "history": [],
                "count": 0,
                "message": "Chat history table not yet created"
            }
        
        result = db.execute(
            text("""
                SELECT * FROM chat_history 
                WHERE user_id = :user_id 
                ORDER BY timestamp DESC 
                LIMIT :limit
            """),
            {"user_id": numeric_id, "limit": limit}
        ).fetchall()
        
        history = [dict(row._mapping) for row in result]
        
        return {
            "user_id": numeric_id,
            "history": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error(f"❌ History error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@router.get("/health")
async def chat_health():
    """Health check endpoint"""
    return {
        "status": "operational",
        "ai_model": GROQ_MODEL if groq_client else "fallback",
        "ai_available": groq_client is not None,
        "language": "English Only",
        "features": [
            "live_prices",
            "risk_analysis",
            "portfolio_recommendations",
            "database_persistence",
            "fallback_responses"
        ]
    }

def get_cached_prices() -> Dict:
    """Fallback cached prices when Binance API is unavailable"""
    return {
        "API is unavailable"
    }