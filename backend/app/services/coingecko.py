"""
CoinGecko API Service
FREE tier - Backup for Binance data
Market cap, coin details, historical data
"""

import aiohttp
from typing import List, Dict, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class CoinGeckoService:
    """
    CoinGecko API service for market data
    FREE tier: 10-30 calls/minute
    """
    
    def __init__(self):
        self.base_url = settings.COINGECKO_BASE_URL
        self.api_key = settings.COINGECKO_API_KEY
    
    async def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """Make async HTTP request"""
        url = f"{self.base_url}{endpoint}"
        
        # Add API key if available
        if self.api_key:
            if params is None:
                params = {}
            params['x_cg_demo_api_key'] = self.api_key
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error = await response.text()
                        logger.error(f"❌ CoinGecko error {response.status}: {error}")
                        return None
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            return None
    
    async def get_coin_details(self, coin_id: str) -> Optional[Dict]:
        """
        Get detailed coin information
        
        Args:
            coin_id: CoinGecko coin ID (bitcoin, ethereum, etc.)
        """
        try:
            params = {
                'localization': 'false',
                'tickers': 'false',
                'community_data': 'false',
                'developer_data': 'false'
            }
            
            data = await self._make_request(f"/coins/{coin_id}", params)
            
            if not data:
                return None
            
            return {
                'id': data.get('id'),
                'symbol': data.get('symbol', '').upper(),
                'name': data.get('name'),
                'market_cap_rank': data.get('market_cap_rank'),
                'market_data': {
                    'current_price': data.get('market_data', {}).get('current_price', {}).get('usd', 0),
                    'market_cap': data.get('market_data', {}).get('market_cap', {}).get('usd', 0),
                    'total_volume': data.get('market_data', {}).get('total_volume', {}).get('usd', 0),
                    'price_change_24h': data.get('market_data', {}).get('price_change_percentage_24h', 0),
                    'price_change_7d': data.get('market_data', {}).get('price_change_percentage_7d', 0),
                    'price_change_30d': data.get('market_data', {}).get('price_change_percentage_30d', 0),
                    'ath': data.get('market_data', {}).get('ath', {}).get('usd', 0),
                    'ath_change_percentage': data.get('market_data', {}).get('ath_change_percentage', {}).get('usd', 0),
                    'circulating_supply': data.get('market_data', {}).get('circulating_supply', 0),
                    'total_supply': data.get('market_data', {}).get('total_supply', 0),
                    'max_supply': data.get('market_data', {}).get('max_supply')
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting coin details: {e}")
            return None
    
    async def get_market_data(self, coin_ids: List[str] = None) -> List[Dict]:
        """
        Get market data for multiple coins
        
        Args:
            coin_ids: List of coin IDs (default: top 50)
        """
        try:
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 50,
                'page': 1,
                'sparkline': 'false'
            }
            
            if coin_ids:
                params['ids'] = ','.join(coin_ids)
            
            data = await self._make_request("/coins/markets", params)
            
            if not data:
                return []
            
            formatted = []
            for coin in data:
                formatted.append({
                    'id': coin.get('id'),
                    'symbol': coin.get('symbol', '').upper(),
                    'name': coin.get('name'),
                    'price': coin.get('current_price', 0),
                    'market_cap': coin.get('market_cap', 0),
                    'market_cap_rank': coin.get('market_cap_rank', 0),
                    'volume_24h': coin.get('total_volume', 0),
                    'change_24h': coin.get('price_change_percentage_24h', 0),
                    'ath': coin.get('ath', 0),
                    'ath_change_percentage': coin.get('ath_change_percentage', 0)
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"❌ Error getting market data: {e}")
            return []
    
    async def get_trending_coins(self) -> List[Dict]:
        """Get trending coins"""
        try:
            data = await self._make_request("/search/trending")
            
            if not data:
                return []
            
            trending = []
            for item in data.get('coins', [])[:10]:
                coin = item.get('item', {})
                trending.append({
                    'id': coin.get('id'),
                    'symbol': coin.get('symbol', '').upper(),
                    'name': coin.get('name'),
                    'market_cap_rank': coin.get('market_cap_rank'),
                    'price_btc': coin.get('price_btc', 0)
                })
            
            return trending
            
        except Exception as e:
            logger.error(f"❌ Error getting trending coins: {e}")
            return []
    
    def map_symbol_to_id(self, symbol: str) -> str:
        """Map common symbols to CoinGecko IDs"""
        mapping = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'ADA': 'cardano',
            'XRP': 'ripple',
            'DOT': 'polkadot',
            'DOGE': 'dogecoin',
            'MATIC': 'matic-network',
            'LINK': 'chainlink'
        }
        return mapping.get(symbol.upper(), symbol.lower())


# Global instance
coingecko_service = CoinGeckoService()


# ==================== TESTING ====================

async def test_coingecko():
    print("=" * 60)
    print("Testing CoinGecko Service")
    print("=" * 60)
    
    # Test 1: Get coin details
    print("\n📊 Test 1: Get Bitcoin details")
    btc = await coingecko_service.get_coin_details('bitcoin')
    if btc:
        print(f"BTC: ${btc['market_data']['current_price']:,.2f}")
        print(f"Market Cap Rank: #{btc['market_cap_rank']}")
    
    # Test 2: Get market data
    print("\n📈 Test 2: Get top 5 coins")
    coins = await coingecko_service.get_market_data()
    for coin in coins[:5]:
        print(f"{coin['symbol']}: ${coin['price']:,.2f}")
    
    # Test 3: Trending
    print("\n🔥 Test 3: Trending coins")
    trending = await coingecko_service.get_trending_coins()
    for coin in trending[:5]:
        print(f"{coin['symbol']}: {coin['name']}")
    
    print("\n" + "=" * 60)
    print("✅ Tests complete!")
    print("=" * 60)



if __name__ == "__main__":
    import nest_asyncio
    import asyncio

    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_coingecko())
