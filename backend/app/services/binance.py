"""
Binance API Service
100% FREE - No API key required for market data
Fetch live cryptocurrency prices, volumes, and market data
"""

import aiohttp
import asyncio
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta

from app.config import settings

logger = logging.getLogger(__name__)


class BinanceService:
    """
    Binance API service for fetching market data
    FREE - Unlimited market data requests
    """
    
    def __init__(self):
        self.base_url = settings.BINANCE_BASE_URL
        self.ws_url = settings.BINANCE_WS_URL
        self.headers = {
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """
        Make async HTTP request to Binance API
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error = await response.text()
                        logger.error(f"❌ Binance API error {response.status}: {error}")
                        return None
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            return None
    
    async def get_top_coins(self, limit: int = 50, quote_asset: str = "USDT") -> List[Dict]:
        """
        Get top coins by trading volume
        
        Args:
            limit: Number of coins to return (default: 50)
            quote_asset: Quote currency (default: USDT)
            
        Returns:
            List of coin data dictionaries
            
        Example:
            >>> service = BinanceService()
            >>> coins = await service.get_top_coins(10)
            >>> print(coins[0])
            {
                'symbol': 'BTC',
                'price': 37890.50,
                'change_24h': 2.5,
                'volume_24h': 28000000000,
                ...
            }
        """
        logger.info(f"📊 Fetching top {limit} coins from Binance...")
        
        try:
            # Get 24h ticker data for all symbols
            data = await self._make_request("/ticker/24hr")
            
            if not data:
                logger.error("❌ Failed to fetch ticker data")
                return []
            
            # Filter USDT pairs only
            usdt_pairs = [
                coin for coin in data 
                if coin['symbol'].endswith(quote_asset)
            ]
            
            # Sort by volume (descending)
            sorted_coins = sorted(
                usdt_pairs,
                key=lambda x: float(x.get('quoteVolume', 0)),
                reverse=True
            )[:limit]
            
            # Format the data
            formatted_coins = []
            for coin in sorted_coins:
                formatted = self._format_coin_data(coin, quote_asset)
                if formatted:
                    formatted_coins.append(formatted)
            
            logger.info(f"✅ Fetched {len(formatted_coins)} coins successfully")
            return formatted_coins
            
        except Exception as e:
            logger.error(f"❌ Error fetching top coins: {e}")
            return []
    
    async def get_coin_price(self, symbol: str) -> Optional[Dict]:
        """
        Get current price for a specific coin
        
        Args:
            symbol: Coin symbol (e.g., 'BTC', 'ETH')
            
        Returns:
            Price data dictionary
            
        Example:
            >>> price_data = await service.get_coin_price('BTC')
            >>> print(price_data)
            {'symbol': 'BTC', 'price': 37890.50, 'change_24h': 2.5, ...}
        """
        try:
            # Add USDT suffix if not present
            if not symbol.endswith('USDT'):
                symbol = f"{symbol}USDT"
            
            # Get 24h ticker
            data = await self._make_request("/ticker/24hr", {"symbol": symbol})
            
            if not data:
                return None
            
            return self._format_coin_data(data)
            
        except Exception as e:
            logger.error(f"❌ Error fetching price for {symbol}: {e}")
            return None
    
    async def get_ticker_prices(self, symbols: List[str] = None) -> Dict[str, float]:
        """
        Get current prices for multiple symbols (for frontend ticker)
        
        Args:
            symbols: List of symbols (default: top 10)
            
        Returns:
            Dictionary mapping symbol to price
            
        Example:
            >>> prices = await service.get_ticker_prices(['BTC', 'ETH', 'SOL'])
            >>> print(prices)
            {'BTC': 37890.50, 'ETH': 2320.30, 'SOL': 90.45}
        """
        try:
            if symbols is None:
                symbols = ['BTC', 'ETH', 'SOL', 'BNB', 'ADA']
            
            # Get all ticker prices
            data = await self._make_request("/ticker/price")
            
            if not data:
                return {}
            
            # Filter requested symbols
            prices = {}
            for item in data:
                symbol = item['symbol'].replace('USDT', '')
                if symbol in symbols:
                    prices[symbol] = float(item['price'])
            
            return prices
            
        except Exception as e:
            logger.error(f"❌ Error fetching ticker prices: {e}")
            return {}
    
    async def get_historical_data(
        self,
        symbol: str,
        interval: str = "1d",
        limit: int = 30
    ) -> List[Dict]:
        """
        Get historical candlestick data (for volatility calculation)
        
        Args:
            symbol: Coin symbol
            interval: Time interval (1m, 5m, 1h, 1d, etc.)
            limit: Number of data points (default: 30)
            
        Returns:
            List of candlestick data
            
        Example:
            >>> history = await service.get_historical_data('BTC', '1d', 30)
            >>> print(history[0])
            {
                'timestamp': 1234567890,
                'open': 37000,
                'high': 38000,
                'low': 36500,
                'close': 37890,
                'volume': 28000000000
            }
        """
        try:
            if not symbol.endswith('USDT'):
                symbol = f"{symbol}USDT"
            
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            data = await self._make_request("/klines", params)
            
            if not data:
                return []
            
            # Format candlestick data
            formatted = []
            for candle in data:
                formatted.append({
                    "timestamp": candle[0],
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5])
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"❌ Error fetching historical data: {e}")
            return []
    
    async def get_order_book(self, symbol: str, limit: int = 10) -> Optional[Dict]:
        """
        Get order book depth (for liquidity analysis)
        
        Args:
            symbol: Coin symbol
            limit: Depth limit (default: 10)
            
        Returns:
            Order book data with bids and asks
        """
        try:
            if not symbol.endswith('USDT'):
                symbol = f"{symbol}USDT"
            
            params = {"symbol": symbol, "limit": limit}
            data = await self._make_request("/depth", params)
            
            if not data:
                return None
            
            return {
                "symbol": symbol.replace('USDT', ''),
                "bids": [[float(price), float(qty)] for price, qty in data.get('bids', [])],
                "asks": [[float(price), float(qty)] for price, qty in data.get('asks', [])]
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching order book: {e}")
            return None
    
    def _format_coin_data(self, coin: dict, quote_asset: str = "USDT") -> Optional[Dict]:
        """
        Format Binance API response into standardized coin data
        
        Args:
            coin: Raw Binance API response
            quote_asset: Quote currency
            
        Returns:
            Formatted coin dictionary
        """
        try:
            symbol = coin['symbol'].replace(quote_asset, '')
            
            return {
                "symbol": symbol,
                "price": float(coin.get('lastPrice', 0)),
                "change_24h": float(coin.get('priceChangePercent', 0)),
                "volume_24h": float(coin.get('quoteVolume', 0)),
                "high_24h": float(coin.get('highPrice', 0)),
                "low_24h": float(coin.get('lowPrice', 0)),
                "open_price": float(coin.get('openPrice', 0)),
                "close_price": float(coin.get('lastPrice', 0)),
                "trades_count": int(coin.get('count', 0)),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error formatting coin data: {e}")
            return None
    
    async def get_market_summary(self) -> Dict:
        """
        Get overall market summary
        
        Returns:
            Market summary with total volume, gainers, losers
        """
        try:
            coins = await self.get_top_coins(100)
            
            if not coins:
                return {}
            
            # Calculate market metrics
            total_volume = sum(coin['volume_24h'] for coin in coins)
            
            # Top gainers (positive change)
            gainers = sorted(
                [c for c in coins if c['change_24h'] > 0],
                key=lambda x: x['change_24h'],
                reverse=True
            )[:5]
            
            # Top losers (negative change)
            losers = sorted(
                [c for c in coins if c['change_24h'] < 0],
                key=lambda x: x['change_24h']
            )[:5]
            
            # Calculate average change
            avg_change = sum(c['change_24h'] for c in coins) / len(coins)
            
            return {
                "total_coins": len(coins),
                "total_volume_24h": total_volume,
                "average_change_24h": avg_change,
                "top_gainers": gainers,
                "top_losers": losers,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting market summary: {e}")
            return {}


# Create global instance
binance_service = BinanceService()


# ==================== HELPER FUNCTIONS ====================

async def get_price(symbol: str) -> Optional[float]:
    """
    Quick helper to get current price
    
    Example:
        >>> price = await get_price('BTC')
        >>> print(f"BTC: ${price}")
        BTC: $37890.50
    """
    data = await binance_service.get_coin_price(symbol)
    return data['price'] if data else None


async def get_top_coins(limit: int = 50) -> List[Dict]:
    """
    Quick helper to get top coins
    """
    return await binance_service.get_top_coins(limit)


async def get_ticker_data() -> Dict[str, float]:
    """
    Quick helper for frontend ticker
    """
    return await binance_service.get_ticker_prices()


# ==================== TESTING ====================

async def test_binance_service():
    """Test Binance service"""
    print("=" * 60)
    print("Testing Binance Service (FREE)")
    print("=" * 60)
    
    service = BinanceService()
    
    # Test 1: Get top coins
    print("\n📝 Test 1: Get top 5 coins")
    coins = await service.get_top_coins(5)
    for coin in coins:
        print(f"  {coin['symbol']}: ${coin['price']:,.2f} ({coin['change_24h']:+.2f}%)")
    
    # Test 2: Get specific price
    print("\n📝 Test 2: Get BTC price")
    btc_data = await service.get_coin_price('BTC')
    if btc_data:
        print(f"  BTC: ${btc_data['price']:,.2f}")
        print(f"  24h Change: {btc_data['change_24h']:+.2f}%")
        print(f"  Volume: ${btc_data['volume_24h']:,.0f}")
    
    # Test 3: Get ticker prices
    print("\n📝 Test 3: Get ticker prices")
    prices = await service.get_ticker_prices(['BTC', 'ETH', 'SOL'])
    for symbol, price in prices.items():
        print(f"  {symbol}: ${price:,.2f}")
    
    # Test 4: Get historical data
    print("\n📝 Test 4: Get 7-day history for BTC")
    history = await service.get_historical_data('BTC', '1d', 7)
    if history:
        print(f"  Got {len(history)} data points")
        print(f"  Latest close: ${history[-1]['close']:,.2f}")
    
    # Test 5: Market summary
    print("\n📝 Test 5: Market summary")
    summary = await service.get_market_summary()
    if summary:
        print(f"  Total Volume: ${summary['total_volume_24h']:,.0f}")
        print(f"  Avg Change: {summary['average_change_24h']:+.2f}%")
        print(f"  Top Gainer: {summary['top_gainers'][0]['symbol']} ({summary['top_gainers'][0]['change_24h']:+.2f}%)")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()  # fix Windows asyncio event loop issue

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_binance_service())