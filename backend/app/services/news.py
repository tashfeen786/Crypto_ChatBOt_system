
"""
Crypto News Service
CryptoPanic API - FREE tier: 100 requests/day
Get news with sentiment analysis
"""

import aiohttp
from typing import List, Dict, Optional
import logging
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)


class NewsService:
    """
    Crypto news service with sentiment analysis
    """
    
    def __init__(self):
        self.base_url = settings.CRYPTOPANIC_BASE_URL
        self.api_key = settings.CRYPTOPANIC_API_KEY
    
    async def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """Make async HTTP request"""
        url = f"{self.base_url}{endpoint}"
        
        if params is None:
            params = {}
        
        # Add auth token
        if self.api_key:
            params['auth_token'] = self.api_key
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error = await response.text()
                        logger.error(f"❌ News API error {response.status}: {error}")
                        return None
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            return None
    
    async def get_latest_news(
        self,
        limit: int = 10,
        currencies: Optional[str] = None,
        filter_type: str = "all"
    ) -> List[Dict]:
        """
        Get latest crypto news
        
        Args:
            limit: Number of news items
            currencies: Filter by coins (e.g., "BTC,ETH")
            filter_type: "all", "rising", "hot", "bullish", "bearish"
        """
        try:
            params = {
                'public': 'true'
            }
            
            if currencies:
                params['currencies'] = currencies
            
            if filter_type != "all":
                params['filter'] = filter_type
            
            data = await self._make_request("/posts/", params)
            
            if not data or 'results' not in data:
                return []
            
            news_list = []
            for item in data['results'][:limit]:
                news_list.append({
                    'id': item.get('id'),
                    'title': item.get('title'),
                    'url': item.get('url'),
                    'published_at': item.get('published_at'),
                    'source': item.get('source', {}).get('title', 'Unknown'),
                    'currencies': [c.get('code') for c in item.get('currencies', [])],
                    'kind': item.get('kind', 'news'),  # news, media, blog
                    'votes': {
                        'positive': item.get('votes', {}).get('positive', 0),
                        'negative': item.get('votes', {}).get('negative', 0),
                        'important': item.get('votes', {}).get('important', 0),
                        'liked': item.get('votes', {}).get('liked', 0),
                        'disliked': item.get('votes', {}).get('disliked', 0)
                    }
                })
            
            logger.info(f"📰 Fetched {len(news_list)} news items")
            return news_list
            
        except Exception as e:
            logger.error(f"❌ Error fetching news: {e}")
            return []
    
    async def get_coin_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Get news for specific coin
        
        Args:
            symbol: Coin symbol (BTC, ETH, etc.)
            limit: Number of news items
        """
        return await self.get_latest_news(limit=limit, currencies=symbol)
    
    def calculate_sentiment(self, news_item: Dict) -> Dict:
        """
        Calculate sentiment from votes
        
        Returns:
            Sentiment analysis: bullish/bearish/neutral
        """
        try:
            votes = news_item.get('votes', {})
            positive = votes.get('positive', 0)
            negative = votes.get('negative', 0)
            
            total_votes = positive + negative
            
            if total_votes == 0:
                return {
                    'sentiment': 'neutral',
                    'score': 0,
                    'confidence': 'low'
                }
            
            # Calculate score (-100 to +100)
            score = ((positive - negative) / total_votes) * 100
            
            # Determine sentiment
            if score > 20:
                sentiment = 'bullish'
                confidence = 'high' if total_votes > 10 else 'medium'
            elif score < -20:
                sentiment = 'bearish'
                confidence = 'high' if total_votes > 10 else 'medium'
            else:
                sentiment = 'neutral'
                confidence = 'medium'
            
            return {
                'sentiment': sentiment,
                'score': round(score, 2),
                'confidence': confidence,
                'total_votes': total_votes
            }
            
        except Exception as e:
            logger.error(f"❌ Sentiment calculation error: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0,
                'confidence': 'error'
            }
    
    async def get_market_sentiment(self, symbols: List[str] = None) -> Dict:
        """
        Get overall market sentiment
        
        Args:
            symbols: List of symbols to analyze (default: BTC, ETH, SOL)
        """
        try:
            if symbols is None:
                symbols = ['BTC', 'ETH', 'SOL']
            
            sentiment_scores = []
            coin_sentiments = {}
            
            for symbol in symbols:
                news = await self.get_coin_news(symbol, limit=20)
                
                if not news:
                    continue
                
                # Calculate average sentiment
                scores = []
                for item in news:
                    sent = self.calculate_sentiment(item)
                    scores.append(sent['score'])
                
                if scores:
                    avg_score = sum(scores) / len(scores)
                    sentiment_scores.append(avg_score)
                    
                    coin_sentiments[symbol] = {
                        'score': round(avg_score, 2),
                        'sentiment': 'bullish' if avg_score > 20 else 'bearish' if avg_score < -20 else 'neutral',
                        'news_count': len(news)
                    }
            
            # Overall market sentiment
            if sentiment_scores:
                overall_score = sum(sentiment_scores) / len(sentiment_scores)
                overall_sentiment = 'bullish' if overall_score > 20 else 'bearish' if overall_score < -20 else 'neutral'
            else:
                overall_score = 0
                overall_sentiment = 'neutral'
            
            return {
                'overall': {
                    'sentiment': overall_sentiment,
                    'score': round(overall_score, 2)
                },
                'coins': coin_sentiments,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Market sentiment error: {e}")
            return {
                'overall': {'sentiment': 'neutral', 'score': 0},
                'coins': {},
                'error': str(e)
            }
    
    async def get_trending_news(self, limit: int = 10) -> List[Dict]:
        """Get trending/hot news"""
        return await self.get_latest_news(limit=limit, filter_type="hot")
    
    async def get_bullish_news(self, limit: int = 10) -> List[Dict]:
        """Get bullish news"""
        return await self.get_latest_news(limit=limit, filter_type="bullish")
    
    async def get_bearish_news(self, limit: int = 10) -> List[Dict]:
        """Get bearish news"""
        return await self.get_latest_news(limit=limit, filter_type="bearish")


# Global instance
news_service = NewsService()


# ==================== HELPER FUNCTIONS ====================

async def get_news(limit: int = 10) -> List[Dict]:
    """Quick helper for latest news"""
    return await news_service.get_latest_news(limit)


async def get_sentiment(symbols: List[str] = None) -> Dict:
    """Quick helper for market sentiment"""
    return await news_service.get_market_sentiment(symbols)


# ==================== TESTING ====================

async def test_news_service():
    print("=" * 60)
    print("Testing News Service")
    print("=" * 60)
    
    # Test 1: Latest news
    print("\n📰 Test 1: Get latest news")
    news = await news_service.get_latest_news(limit=5)
    for i, item in enumerate(news, 1):
        print(f"{i}. {item['title'][:60]}...")
        sentiment = news_service.calculate_sentiment(item)
        print(f"   Sentiment: {sentiment['sentiment']} ({sentiment['score']:+.1f})")
    
    # Test 2: Coin-specific news
    print("\n📊 Test 2: Bitcoin news")
    btc_news = await news_service.get_coin_news('BTC', limit=3)
    print(f"Found {len(btc_news)} BTC news items")
    
    # Test 3: Market sentiment
    print("\n💭 Test 3: Market sentiment")
    sentiment = await news_service.get_market_sentiment(['BTC', 'ETH'])
    print(f"Overall: {sentiment['overall']['sentiment']} ({sentiment['overall']['score']:+.1f})")
    for coin, data in sentiment['coins'].items():
        print(f"{coin}: {data['sentiment']} ({data['score']:+.1f})")
    
    # Test 4: Trending
    print("\n🔥 Test 4: Trending news")
    trending = await news_service.get_trending_news(limit=3)
    for item in trending:
        print(f"- {item['title'][:60]}...")
    
    print("\n" + "=" * 60)
    print("✅ Tests complete!")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_news_service())
