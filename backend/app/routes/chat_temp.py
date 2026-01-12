"""
Temporary Simple Chat Route - GUARANTEED TO WORK
This bypasses all complex imports and uses basic fallback logic
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    user_id: str
    user_risk_tolerance: int = 5
    user_balance: float = 1000.0
    include_trading: bool = False


class ChatResponse(BaseModel):
    response: str
    coins_mentioned: List[str] = []
    risk_analysis: Optional[dict] = None


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Simple chat endpoint with basic investment advice"""
    try:
        logger.info(f"📨 Chat request: {request.message[:50]}...")
        
        # Generate response based on risk level
        response_text = generate_simple_advice(
            request.message,
            request.user_balance,
            request.user_risk_tolerance
        )
        
        # Extract coins mentioned
        coins = extract_coins(response_text)
        
        # Risk analysis
        risk_analysis = {
            "risk_score": request.user_risk_tolerance,
            "risk_level": get_risk_level(request.user_risk_tolerance),
            "recommendation": get_risk_recommendation(request.user_risk_tolerance)
        }
        
        logger.info("✅ Chat response generated")
        
        return ChatResponse(
            response=response_text,
            coins_mentioned=coins,
            risk_analysis=risk_analysis
        )
        
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        return ChatResponse(
            response="Sorry boss! Kuch issue aa gaya. Thodi der baad try karo.",
            coins_mentioned=[],
            risk_analysis={"risk_score": 5, "risk_level": "moderate"}
        )


@router.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "message": "Chat service is working!"}


def generate_simple_advice(query: str, balance: float, risk: int) -> str:
    """Generate investment advice based on risk level"""
    
    query_lower = query.lower()
    
    # Check if asking about specific coin
    if "bitcoin" in query_lower or "btc" in query_lower:
        return f"""Bitcoin ke baare mein advice:

**Current Status:** Bitcoin market leader hai aur sabse stable crypto.

**Recommendation for your profile:**
- Balance: ${balance}
- Risk: {risk}/10

{get_btc_advice(balance, risk)}

💡 Bitcoin long-term investment ke liye best hai!"""

    elif "ethereum" in query_lower or "eth" in query_lower:
        return f"""Ethereum analysis:

**Current Status:** Second largest crypto, strong fundamentals.

**Your Profile:**
- Balance: ${balance}
- Risk: {risk}/10

{get_eth_advice(balance, risk)}

💡 Smart contracts ka leader hai Ethereum!"""

    elif "solana" in query_lower or "sol" in query_lower:
        return f"""Solana information:

**Current Status:** Fast blockchain, high growth potential.

**Your Profile:**
- Balance: ${balance}
- Risk: {risk}/10

{get_sol_advice(balance, risk)}

⚠️ Higher risk but good potential!"""

    # General investment advice
    else:
        return generate_portfolio_advice(balance, risk)


def generate_portfolio_advice(balance: float, risk: int) -> str:
    """Generate general portfolio advice"""
    
    if risk <= 3:
        # Conservative
        return f"""Salam boss! Aapka balance ${balance} hai aur risk LOW ({risk}/10).

**Recommended Portfolio:**

1. **Bitcoin (BTC)** - 50% (${balance * 0.5:.2f})
   - Safest option, market leader
   - Long-term hold perfect
   - Price stable rehti hai relatively

2. **Ethereum (ETH)** - 30% (${balance * 0.3:.2f})
   - Second largest, proven track record
   - Smart contracts platform
   - Good growth potential

3. **Stablecoins (USDT/USDC)** - 20% (${balance * 0.2:.2f})
   - Emergency backup
   - No volatility
   - Liquidity maintain karne ke liye

**Risk Level:** Low ✅
**Expected Returns:** 10-30% yearly
**Strategy:** Buy and hold for 1+ years

⚠️ Market research zaroori hai before investing!"""

    elif risk <= 6:
        # Moderate
        return f"""Salam boss! Balance ${balance} hai, risk MODERATE ({risk}/10).

**Balanced Portfolio Suggestion:**

1. **Bitcoin (BTC)** - 40% (${balance * 0.4:.2f})
   - Foundation strong
   - Safe bet for portfolio

2. **Ethereum (ETH)** - 35% (${balance * 0.35:.2f})
   - Growth potential high
   - Solid fundamentals

3. **Altcoins Mix** - 25% (${balance * 0.25:.2f})
   - Solana (SOL): Fast, scalable
   - Cardano (ADA): Research-based
   - Polygon (MATIC): Layer-2 solution

**Risk Level:** Moderate ⚡
**Expected Returns:** 30-100% yearly
**Strategy:** Diversification is key

💡 Portfolio quarterly review karo!"""

    else:
        # Aggressive
        return f"""Boss! ${balance} ke saath AGGRESSIVE strategy ({risk}/10)! 🚀

**High Risk Portfolio:**

1. **Bitcoin (BTC)** - 30% (${balance * 0.3:.2f})
   - Baseline ke liye
   - Market benchmark

2. **Ethereum (ETH)** - 30% (${balance * 0.3:.2f})
   - Major altcoin position
   - Strong ecosystem

3. **High Growth Altcoins** - 40% (${balance * 0.4:.2f})
   - Solana (SOL): Speed leader
   - Avalanche (AVAX): DeFi powerhouse
   - Polygon (MATIC): Scaling solution
   - Small caps (10%): High risk/reward

**Risk Level:** High 🔥
**Expected Returns:** 100-500% (or losses!)
**Strategy:** Active monitoring required

⚠️ IMPORTANT:
- Stop-loss zaroor lagao
- Daily market check karo
- Profit booking ka plan banao
- Only invest what you can afford to lose!"""


def get_btc_advice(balance: float, risk: int) -> str:
    """BTC specific advice"""
    allocation = 0.5 if risk <= 3 else (0.4 if risk <= 6 else 0.3)
    amount = balance * allocation
    return f"""✅ Bitcoin mein invest karo: ${amount:.2f} ({allocation*100:.0f}% of portfolio)
- Safest crypto asset
- Proven track record since 2009
- Institutional adoption badh raha hai"""


def get_eth_advice(balance: float, risk: int) -> str:
    """ETH specific advice"""
    allocation = 0.3 if risk <= 3 else (0.35 if risk <= 6 else 0.3)
    amount = balance * allocation
    return f"""✅ Ethereum good choice: ${amount:.2f} ({allocation*100:.0f}% of portfolio)
- Smart contract leader
- Large developer community
- Upcoming upgrades promising hain"""


def get_sol_advice(balance: float, risk: int) -> str:
    """SOL specific advice"""
    if risk <= 3:
        return "❌ Aapke low risk profile ke liye Solana risky hai. BTC/ETH better option."
    allocation = 0.15 if risk <= 6 else 0.25
    amount = balance * allocation
    return f"""⚡ Solana consider karo: ${amount:.2f} ({allocation*100:.0f}% of portfolio)
- Fastest blockchain
- Growing ecosystem
- Higher risk but good potential"""


def extract_coins(text: str) -> List[str]:
    """Extract coin symbols from text"""
    coins = []
    text_upper = text.upper()
    
    symbols = ['BTC', 'ETH', 'SOL', 'ADA', 'AVAX', 'MATIC', 'DOT', 'LINK', 'USDT', 'USDC']
    
    for symbol in symbols:
        if symbol in text_upper:
            coins.append(symbol)
    
    return list(set(coins))  # Remove duplicates


def get_risk_level(risk: int) -> str:
    """Get risk level label"""
    if risk <= 3:
        return "low"
    elif risk <= 6:
        return "moderate"
    else:
        return "high"


def get_risk_recommendation(risk: int) -> str:
    """Get risk recommendation"""
    if risk <= 3:
        return "Conservative - Focus on BTC, ETH"
    elif risk <= 6:
        return "Balanced - Mix of stable and growth coins"
    else:
        return "Aggressive - Higher risk, higher potential"