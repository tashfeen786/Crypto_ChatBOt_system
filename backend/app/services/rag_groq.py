"""
RAG Service with Groq (Free & Fast Alternative to Gemini)
Simplified version - No startup testing
"""
import os
from groq import Groq
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """RAG Service using Groq AI (Free)"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("❌ GROQ_API_KEY not found in environment!")
            raise ValueError("GROQ_API_KEY is required")
            
        self.client = Groq(api_key=api_key)
        
        # Use best model directly (no testing)
        self.model = "llama-3.3-70b-versatile"
        
        # Fallback models to try if primary fails
        self.fallback_models = [
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
        ]
        
        logger.info(f"✅ Groq AI configured with model: {self.model}")
    
    def generate_investment_advice(
        self,
        query: str,
        user_balance: float,
        user_risk: int,
        coins_data: Optional[List[Dict]] = None
    ) -> str:
        """Generate personalized investment advice"""
        
        # Build context from coins data
        context = self._build_coin_context(coins_data) if coins_data else ""
        
        # Create investment-focused prompt
        prompt = f"""You are a crypto investment advisor. Provide advice in Urdu/Roman Urdu mix.

User Details:
- Balance: ${user_balance}
- Risk Tolerance: {user_risk}/10
- Query: {query}

Available Market Data:
{context}

Instructions:
1. Suggest 2-3 coins based on their balance and risk
2. Explain WHY each coin is good/bad
3. Give specific allocation (e.g., 40% BTC, 30% ETH, 30% SOL)
4. Mention current prices and trends
5. Be conversational and friendly (Roman Urdu style)

Response in this style:
"Dekho boss, tumhare ${user_balance} balance ke saath main ye suggest karta hoon:

1. Bitcoin (BTC) - ${'{price}'}: Sabse safe option, market leader hai. Tumhare portfolio ka 40% yahan rakho.

2. Ethereum (ETH) - ${'{price}'}: Second largest, strong fundamentals. 30% allocation sahi rahega.

3. [Third coin] - Baaki 30% diversification ke liye.

Risk: Tumhara risk {user_risk}/10 hai, to ye allocation perfect hai!"

Keep it under 300 words, friendly tone."""

        # Try primary model first, then fallbacks
        models_to_try = [self.model] + self.fallback_models
        
        for model in models_to_try:
            try:
                logger.info(f"🔄 Trying model: {model}")
                
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a friendly crypto investment advisor who speaks in Urdu/Roman Urdu mix. Give practical, actionable advice."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=800,
                )
                
                advice = response.choices[0].message.content
                logger.info(f"✅ Generated advice with {model} ({len(advice)} chars)")
                return advice
                
            except Exception as e:
                logger.warning(f"⚠️ Model {model} failed: {str(e)[:100]}")
                continue
        
        # If all models fail, use fallback advice
        logger.error("❌ All Groq models failed, using fallback advice")
        return self._fallback_advice(user_balance, user_risk)
    
    def _build_coin_context(self, coins_data: List[Dict]) -> str:
        """Build context from coin data"""
        if not coins_data:
            return "No specific coin data available."
        
        context_parts = []
        for coin in coins_data[:5]:  # Top 5 coins
            symbol = coin.get('symbol', 'UNKNOWN')
            price = coin.get('price', 0)
            change = coin.get('change_24h', 0)
            
            context_parts.append(
                f"{symbol}: ${price:.2f} ({change:+.2f}% 24h)"
            )
        
        return "\n".join(context_parts)
    
    def _fallback_advice(self, balance: float, risk: int) -> str:
        """Fallback advice if AI fails"""
        
        if risk <= 3:
            # Low risk
            advice = f"""Salam boss! Tumhara balance ${balance} hai aur risk tolerance low ({risk}/10) hai.

Main tumhe stable coins recommend karta hoon:

1. **Bitcoin (BTC)** - 50% allocation
   - Sabse safe crypto, market leader
   - Long-term hold karo

2. **Ethereum (ETH)** - 30% allocation  
   - Strong fundamentals
   - Smart contracts leader

3. **Stablecoins (USDT/USDC)** - 20%
   - Price stable rahti hai
   - Emergency ke liye

⚠️ Low risk = Low returns, but safe investment!"""

        elif risk <= 6:
            # Moderate risk
            advice = f"""Salam boss! Balance ${balance} hai, risk moderate ({risk}/10).

Ye portfolio try karo:

1. **Bitcoin (BTC)** - 40%
   - Foundation strong hai

2. **Ethereum (ETH)** - 35%
   - Growth potential zyada

3. **Solana/Cardano** - 25%
   - High potential coins
   - Market trends dekh kar select karo

💡 Diversification se risk kam hota hai!"""

        else:
            # High risk
            advice = f"""Arre boss! ${balance} balance hai aur risk appetite high ({risk}/10)! 🚀

Aggressive portfolio:

1. **Bitcoin (BTC)** - 30%
   - Baseline ke liye

2. **Ethereum (ETH)** - 30%
   - Strong bet

3. **Altcoins (SOL/AVAX/MATIC)** - 40%
   - High risk, high reward
   - Market research kar ke choose karo

⚠️ High risk = Zyada profit YA zyada loss!
Stop-loss zaroor lagao!"""

        return advice
    
    def extract_coins_mentioned(self, text: str) -> List[str]:
        """Extract coin symbols from text"""
        common_coins = [
            'BTC', 'ETH', 'SOL', 'ADA', 'AVAX', 'MATIC', 
            'DOT', 'LINK', 'UNI', 'DOGE', 'SHIB', 'XRP',
            'BNB', 'USDT', 'USDC', 'XLM', 'ATOM', 'NEAR'
        ]
        
        mentioned = []
        text_upper = text.upper()
        
        for coin in common_coins:
            if coin in text_upper:
                mentioned.append(coin)
        
        return mentioned


# Singleton instance
_rag_service = None

def get_rag_service() -> RAGService:
    """Get RAG service singleton"""
    global _rag_service
    if _rag_service is None:
        try:
            _rag_service = RAGService()
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG service: {e}")
            raise
    return _rag_service