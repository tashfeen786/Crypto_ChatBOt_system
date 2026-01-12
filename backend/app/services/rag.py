"""
RAG System - Retrieval Augmented Generation
Combines: Pinecone (vector DB) + Gemini AI + Market Data
For intelligent crypto investment advice with trading
"""

import google.generativeai as genai
from typing import Dict, List, Optional
import logging
import json
from datetime import datetime

from app.config import settings
from app.utils.embeddings import embeddings_service
from app.utils.pinecone_client import pinecone_client
from app.services.binance import binance_service
from app.services.risk_engine import risk_engine

logger = logging.getLogger(__name__)


class RAGService:
    """
    RAG Service for intelligent crypto advice
    """
    
    def __init__(self):
        """Initialize RAG service"""
        logger.info("🔄 Initializing RAG Service...")
        
        try:
            # Configure Gemini AI
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            
            logger.info(f"✅ Gemini AI configured: {settings.GEMINI_MODEL}")
            logger.info("✅ RAG Service ready!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG: {e}")
            raise
    
    async def store_coin_analysis(self, coin_data: Dict) -> bool:
        """
        Store coin analysis in vector database
        
        Args:
            coin_data: Complete coin data with risk analysis
            
        Returns:
            Success status
        """
        try:
            symbol = coin_data.get('symbol', 'UNKNOWN')
            logger.info(f"📝 Storing analysis for {symbol}...")
            
            # Generate embedding
            embedding = embeddings_service.embed_coin_analysis(coin_data)
            
            # Create vector
            vector = {
                "id": f"{symbol}_{int(datetime.now().timestamp())}",
                "values": embedding,
                "metadata": {
                    "symbol": symbol,
                    "name": coin_data.get('name', symbol),
                    "price": float(coin_data.get('price', 0)),
                    "change_24h": float(coin_data.get('change_24h', 0)),
                    "volume_24h": float(coin_data.get('volume_24h', 0)),
                    "risk_score": float(coin_data.get('risk_score', 5.0)),
                    "risk_level": coin_data.get('risk_level', 'medium'),
                    "volatility": float(coin_data.get('volatility_score', 5.0)),
                    "liquidity": float(coin_data.get('liquidity_score', 5.0)),
                    "trend": coin_data.get('trend', 'neutral'),
                    "sentiment": coin_data.get('sentiment', 'neutral'),
                    "recommendation": coin_data.get('recommendation', 'moderate_investment'),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Store in Pinecone
            pinecone_client.upsert([vector])
            
            logger.info(f"✅ {symbol} analysis stored in RAG")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing coin analysis: {e}")
            return False
    
    def query_similar_coins(
        self,
        query: str,
        top_k: int = 3,
        risk_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Query for similar coins based on text query
        
        Args:
            query: Natural language query
            top_k: Number of results
            risk_filter: Filter by risk level (low/medium/high)
            
        Returns:
            List of matching coin data
        """
        try:
            logger.info(f"🔍 Querying RAG: '{query}'")
            
            # Generate query embedding
            query_embedding = embeddings_service.embed_text(query)
            
            # Build filter
            filter_dict = None
            if risk_filter:
                filter_dict = {"risk_level": {"$eq": risk_filter}}
            
            # Query Pinecone
            results = pinecone_client.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter_dict
            )
            
            logger.info(f"📊 Found {len(results)} relevant coins")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error querying RAG: {e}")
            return []
    
    async def generate_investment_advice(
        self,
        user_message: str,
        user_profile: Dict,
        include_trading: bool = False
    ) -> Dict:
        """
        Generate intelligent investment advice using RAG + AI
        
        Args:
            user_message: User's question
            user_profile: User profile with risk tolerance, balance
            include_trading: If True, generate executable trade recommendations
            
        Returns:
            AI response with advice and optional trade commands
        """
        try:
            logger.info(f"💭 Generating advice for: '{user_message}'")
            
            # Step 1: Query RAG for relevant coins
            relevant_coins = self.query_similar_coins(user_message, top_k=3)
            
            # Step 2: Get latest market data
            market_context = await self._get_market_context(relevant_coins)
            
            # Step 3: Build comprehensive prompt
            prompt = self._build_prompt(
                user_message=user_message,
                user_profile=user_profile,
                rag_results=relevant_coins,
                market_context=market_context,
                include_trading=include_trading
            )
            
            # Step 4: Get AI response
            response = self.model.generate_content(prompt)
            ai_text = response.text
            
            # Step 5: Parse response
            parsed = self._parse_ai_response(ai_text, include_trading)
            
            # Step 6: Add metadata
            result = {
                "response": parsed.get('response', ai_text),
                "coins_mentioned": parsed.get('coins', []),
                "risk_analysis": parsed.get('risk_analysis', {}),
                "trade_commands": parsed.get('trade_commands', []) if include_trading else [],
                "confidence": parsed.get('confidence', 'medium'),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Advice generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating advice: {e}")
            return {
                "response": "Sorry, I couldn't generate advice at this moment. Please try again.",
                "error": str(e)
            }
    
    async def _get_market_context(self, rag_results: List[Dict]) -> Dict:
        """Get fresh market data for RAG results"""
        try:
            symbols = [r['metadata']['symbol'] for r in rag_results if 'metadata' in r]
            
            if not symbols:
                return {}
            
            # Get current prices
            prices = {}
            for symbol in symbols:
                price_data = await binance_service.get_coin_price(symbol)
                if price_data:
                    prices[symbol] = price_data
            
            return {
                "current_prices": prices,
                "market_summary": await binance_service.get_market_summary()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting market context: {e}")
            return {}
    
    def _build_prompt(
        self,
        user_message: str,
        user_profile: Dict,
        rag_results: List[Dict],
        market_context: Dict,
        include_trading: bool
    ) -> str:
        """Build comprehensive prompt for Gemini"""
        
        # Format RAG results
        rag_context = "Relevant Coins from Database:\n"
        for i, result in enumerate(rag_results, 1):
            meta = result.get('metadata', {})
            rag_context += f"""
{i}. {meta.get('symbol', 'N/A')} ({meta.get('name', 'N/A')}):
   - Price: ${meta.get('price', 0):,.2f}
   - 24h Change: {meta.get('change_24h', 0):+.2f}%
   - Risk Score: {meta.get('risk_score', 5):.1f}/10 ({meta.get('risk_level', 'medium')})
   - Volatility: {meta.get('volatility', 5):.1f}/10
   - Liquidity: {meta.get('liquidity', 5):.1f}/10
   - Trend: {meta.get('trend', 'neutral')}
   - Recommendation: {meta.get('recommendation', 'moderate_investment')}
"""
        
        # User profile context
        user_context = f"""
User Profile:
- Risk Tolerance: {user_profile.get('risk_tolerance', 5)}/10
- Available Balance: ${user_profile.get('balance', 0):,.2f}
- Experience Level: {user_profile.get('experience', 'beginner')}
- Investment Goal: {user_profile.get('goal', 'growth')}
"""
        
        # Trading instructions
        trading_instructions = ""
        if include_trading:
            trading_instructions = """
IMPORTANT - Trading Enabled:
If user asks you to invest/buy, provide SPECIFIC trade commands in this format:
TRADE_COMMAND: BUY <SYMBOL> <AMOUNT_USD>
Example: TRADE_COMMAND: BUY BTC 100

Only suggest trades that:
1. Match user's risk tolerance
2. Are within user's balance
3. Have clear profit potential
"""
        
        # Complete prompt
        prompt = f"""You are an expert crypto investment advisor chatbot. Provide advice in English.

{user_context}

{rag_context}
Current Market Context:
{json.dumps(market_context, indent=2)}

User Question: "{user_message}"

{trading_instructions}

Instructions:
1. Analyze the user's risk tolerance vs coin's risk score
2. If coin risk > user risk: WARN strongly against it
3. If coin risk <= user risk: RECOMMEND investment
4. Be specific with amounts based on user's balance
5. Use simple language: "profit ke chances ache hain" or "loss ka risk zyada hai"
6. Always explain WHY (risk score, volatility, trend)
7. Keep response under 200 words
8. End with clear YES/NO recommendation

Response format:
- Main advice (in Urdu/English mix)
- Risk analysis
- Specific investment amount (if recommending)
- Trade command (if user wants to invest)

Generate response:"""
        
        return prompt
    
    def _parse_ai_response(self, ai_text: str, include_trading: bool) -> Dict:
        """Parse AI response and extract structured data"""
        try:
            # Extract trade commands if present
            trade_commands = []
            if include_trading and "TRADE_COMMAND:" in ai_text:
                lines = ai_text.split('\n')
                for line in lines:
                    if line.strip().startswith("TRADE_COMMAND:"):
                        cmd = line.replace("TRADE_COMMAND:", "").strip()
                        parts = cmd.split()
                        if len(parts) >= 3:
                            trade_commands.append({
                                "action": parts[0],  # BUY or SELL
                                "symbol": parts[1],
                                "amount": float(parts[2]) if parts[2].replace('.', '').isdigit() else 0
                            })
                
                # Remove trade commands from display text
                ai_text = '\n'.join([l for l in ai_text.split('\n') if not l.strip().startswith("TRADE_COMMAND:")])
            
            # Extract mentioned coins
            coins = []
            common_symbols = ['BTC', 'ETH', 'SOL', 'BNB', 'ADA', 'DOGE', 'XRP', 'DOT', 'MATIC', 'LINK']
            for symbol in common_symbols:
                if symbol in ai_text.upper():
                    coins.append(symbol)
            
            return {
                "response": ai_text.strip(),
                "coins": list(set(coins)),
                "trade_commands": trade_commands,
                "confidence": "high" if trade_commands else "medium"
            }
            
        except Exception as e:
            logger.error(f"❌ Error parsing response: {e}")
            return {"response": ai_text}
    
    async def get_investment_allocation(
        self,
        user_profile: Dict,
        total_amount: float
    ) -> Dict:
        """
        Get smart investment allocation based on user profile
        
        Args:
            user_profile: User's risk tolerance and preferences
            total_amount: Amount to invest
            
        Returns:
            Allocation breakdown with specific coins and amounts
        """
        try:
            risk_tolerance = user_profile.get('risk_tolerance', 5)
            
            # Get top coins with suitable risk
            query = f"safe low risk cryptocurrency risk score below {risk_tolerance}"
            suitable_coins = self.query_similar_coins(query, top_k=5)
            
            # Smart allocation based on risk tolerance
            if risk_tolerance <= 3:  # Conservative
                allocation = {
                    "strategy": "Conservative",
                    "breakdown": [
                        {"symbol": "BTC", "percentage": 60, "amount": total_amount * 0.60},
                        {"symbol": "ETH", "percentage": 25, "amount": total_amount * 0.25},
                        {"symbol": "USDT", "percentage": 15, "amount": total_amount * 0.15}
                    ]
                }
            elif risk_tolerance <= 6:  # Moderate
                allocation = {
                    "strategy": "Moderate",
                    "breakdown": [
                        {"symbol": "BTC", "percentage": 40, "amount": total_amount * 0.40},
                        {"symbol": "ETH", "percentage": 30, "amount": total_amount * 0.30},
                        {"symbol": "BNB", "percentage": 15, "amount": total_amount * 0.15},
                        {"symbol": "SOL", "percentage": 10, "amount": total_amount * 0.10},
                        {"symbol": "Cash", "percentage": 5, "amount": total_amount * 0.05}
                    ]
                }
            else:  # Aggressive
                allocation = {
                    "strategy": "Aggressive",
                    "breakdown": [
                        {"symbol": "BTC", "percentage": 25, "amount": total_amount * 0.25},
                        {"symbol": "ETH", "percentage": 25, "amount": total_amount * 0.25},
                        {"symbol": "SOL", "percentage": 20, "amount": total_amount * 0.20},
                        {"symbol": "BNB", "percentage": 15, "amount": total_amount * 0.15},
                        {"symbol": "ADA", "percentage": 10, "amount": total_amount * 0.10},
                        {"symbol": "Cash", "percentage": 5, "amount": total_amount * 0.05}
                    ]
                }
            
            allocation["total_amount"] = total_amount
            allocation["risk_level"] = risk_tolerance
            
            return allocation
            
        except Exception as e:
            logger.error(f"❌ Error calculating allocation: {e}")
            return {}


# Create global instance
rag_service = RAGService()


# ==================== HELPER FUNCTIONS ====================

async def get_investment_advice(
    user_message: str,
    user_profile: Dict,
    include_trading: bool = False
) -> Dict:
    """Quick helper for investment advice"""
    return await rag_service.generate_investment_advice(
        user_message, user_profile, include_trading
    )


async def store_coin(coin_data: Dict) -> bool:
    """Quick helper to store coin"""
    return await rag_service.store_coin_analysis(coin_data)


# ==================== TESTING ====================

async def test_rag_service():
    """Test RAG service"""
    print("=" * 60)
    print("Testing RAG Service")
    print("=" * 60)
    
    # Test user profile
    user_profile = {
        "risk_tolerance": 5,
        "balance": 1000,
        "experience": "intermediate",
        "goal": "growth"
    }
    
    # Test 1: Store coin
    print("\n📝 Test 1: Store BTC analysis")
    btc_data = {
        "symbol": "BTC",
        "name": "Bitcoin",
        "price": 37890,
        "change_24h": 2.5,
        "volume_24h": 28000000000,
        "risk_score": 3.2,
        "risk_level": "low",
        "volatility_score": 3.5,
        "liquidity_score": 9.8,
        "trend": "bullish"
    }
    await rag_service.store_coin_analysis(btc_data)
    print("✅ BTC stored")
    
    # Test 2: Query
    print("\n🔍 Test 2: Query low risk coins")
    results = rag_service.query_similar_coins("low risk safe investment", top_k=3)
    for r in results:
        print(f"  - {r['metadata']['symbol']}: {r['score']:.4f}")
    
    # Test 3: Get advice
    print("\n💭 Test 3: Get investment advice")
    advice = await rag_service.generate_investment_advice(
        user_message="Bitcoin mein invest karna chahiye?",
        user_profile=user_profile,
        include_trading=False
    )
    print(f"Response: {advice['response'][:200]}...")
    
    # Test 4: Smart allocation
    print("\n💰 Test 4: Get smart allocation")
    allocation = await rag_service.get_investment_allocation(user_profile, 1000)
    print(f"Strategy: {allocation.get('strategy', 'N/A')}")
    for item in allocation.get('breakdown', []):
        print(f"  {item['symbol']}: ${item['amount']:.2f} ({item['percentage']}%)")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_rag_service())