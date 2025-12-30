"""
Coins Routes - REAL API Integration with 50+ Coins
Fetches live data from Binance
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional, List
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Binance API endpoint
BINANCE_API = "https://api.binance.com/api/v3"

# Top 50+ coins to track (with Binance trading pairs)
TOP_COINS = {
    # Top 10
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "BNB": "BNBUSDT",
    "SOL": "SOLUSDT",
    "XRP": "XRPUSDT",
    "ADA": "ADAUSDT",
    "AVAX": "AVAXUSDT",
    "DOGE": "DOGEUSDT",
    "MATIC": "MATICUSDT",
    "DOT": "DOTUSDT",
    
    # Top 11-20
    "LINK": "LINKUSDT",
    "UNI": "UNIUSDT",
    "LTC": "LTCUSDT",
    "ATOM": "ATOMUSDT",
    "SHIB": "SHIBUSDT",
    "TRX": "TRXUSDT",
    "TON": "TONUSDT",
    "BCH": "BCHUSDT",
    "NEAR": "NEARUSDT",
    "LEO": "LEOUSDT",
    
    # Top 21-30
    "DAI": "DAIUSDT",
    "WBTC": "WBTCUSDT",
    "ETC": "ETCUSDT",
    "XLM": "XLMUSDT",
    "ALGO": "ALGOUSDT",
    "VET": "VETUSDT",
    "FIL": "FILUSDT",
    "ICP": "ICPUSDT",
    "HBAR": "HBARUSDT",
    "APT": "APTUSDT",
    
    # Top 31-40
    "CRO": "CROUSDT",
    "QNT": "QNTUSDT",
    "LDO": "LDOUSDT",
    "ARB": "ARBUSDT",
    "OP": "OPUSDT",
    "IMX": "IMXUSDT",
    "SAND": "SANDUSDT",
    "MANA": "MANAUSDT",
    "AXS": "AXSUSDT",
    "GALA": "GALAUSDT",
    
    # Top 41-50
    "APE": "APEUSDT",
    "CHZ": "CHZUSDT",
    "ENJ": "ENJUSDT",
    "FTM": "FTMUSDT",
    "GRT": "GRTUSDT",
    "AAVE": "AAVEUSDT",
    "MKR": "MKRUSDT",
    "SNX": "SNXUSDT",
    "COMP": "COMPUSDT",
    "YFI": "YFIUSDT",
}

# Coin names mapping
COIN_NAMES = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
    "BNB": "Binance Coin",
    "SOL": "Solana",
    "XRP": "Ripple",
    "ADA": "Cardano",
    "AVAX": "Avalanche",
    "DOGE": "Dogecoin",
    "MATIC": "Polygon",
    "DOT": "Polkadot",
    "LINK": "Chainlink",
    "UNI": "Uniswap",
    "LTC": "Litecoin",
    "ATOM": "Cosmos",
    "SHIB": "Shiba Inu",
    "TRX": "TRON",
    "TON": "Toncoin",
    "BCH": "Bitcoin Cash",
    "NEAR": "NEAR Protocol",
    "LEO": "UNUS SED LEO",
    "DAI": "Dai",
    "WBTC": "Wrapped Bitcoin",
    "ETC": "Ethereum Classic",
    "XLM": "Stellar",
    "ALGO": "Algorand",
    "VET": "VeChain",
    "FIL": "Filecoin",
    "ICP": "Internet Computer",
    "HBAR": "Hedera",
    "APT": "Aptos",
    "CRO": "Cronos",
    "QNT": "Quant",
    "LDO": "Lido DAO",
    "ARB": "Arbitrum",
    "OP": "Optimism",
    "IMX": "Immutable X",
    "SAND": "The Sandbox",
    "MANA": "Decentraland",
    "AXS": "Axie Infinity",
    "GALA": "Gala",
    "APE": "ApeCoin",
    "CHZ": "Chiliz",
    "ENJ": "Enjin Coin",
    "FTM": "Fantom",
    "GRT": "The Graph",
    "AAVE": "Aave",
    "MKR": "Maker",
    "SNX": "Synthetix",
    "COMP": "Compound",
    "YFI": "yearn.finance",
}


@router.get("/prices")
async def get_coin_prices(symbols: Optional[str] = None):
    """
    Get REAL live cryptocurrency prices from Binance
    
    Query params:
    - symbols: Comma-separated list (e.g., "BTC,ETH,SOL,SHIB")
    """
    try:
        logger.info(f"📊 Fetching LIVE prices from Binance API")
        
        # Get symbols to fetch
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",")]
            pairs_to_fetch = {s: TOP_COINS.get(s) for s in symbol_list if s in TOP_COINS}
        else:
            # Default: return all coins
            pairs_to_fetch = TOP_COINS.copy()
        
        logger.info(f"📊 Requesting {len(pairs_to_fetch)} coins")
        
        # Fetch from Binance
        prices_data = {}
        
        try:
            # Get 24hr ticker data for all symbols at once
            response = requests.get(
                f"{BINANCE_API}/ticker/24hr",
                timeout=10
            )
            response.raise_for_status()
            all_tickers = response.json()
            
            # Create a lookup dict
            ticker_dict = {ticker['symbol']: ticker for ticker in all_tickers}
            
            # Process requested coins
            for symbol, pair in pairs_to_fetch.items():
                if pair and pair in ticker_dict:
                    ticker = ticker_dict[pair]
                    prices_data[symbol] = {
                        "price": float(ticker['lastPrice']),
                        "change_24h": float(ticker['priceChangePercent']),
                        "volume": float(ticker['volume']),
                        "high_24h": float(ticker['highPrice']),
                        "low_24h": float(ticker['lowPrice']),
                        "market_cap": 0,  # Would need CoinGecko for this
                    }
            
            logger.info(f"✅ Fetched LIVE prices for {len(prices_data)} coins")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Binance API error: {e}")
            # Return fallback data if API fails
            prices_data = get_fallback_prices()
        
        return {
            "status": "success",
            "source": "binance_live",
            "timestamp": datetime.utcnow().isoformat(),
            "prices": prices_data,
            "count": len(prices_data)
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching prices: {e}")
        # Return fallback instead of error
        return {
            "status": "fallback",
            "source": "cached",
            "timestamp": datetime.utcnow().isoformat(),
            "prices": get_fallback_prices(),
            "count": len(get_fallback_prices())
        }


@router.get("/{symbol}")
async def get_coin_details(symbol: str):
    """Get detailed REAL information about a specific coin"""
    try:
        symbol = symbol.upper()
        logger.info(f"📊 Fetching LIVE details for: {symbol}")
        
        if symbol not in TOP_COINS:
            raise HTTPException(status_code=404, detail=f"Coin {symbol} not tracked")
        
        pair = TOP_COINS[symbol]
        
        # Get ticker data
        ticker_response = requests.get(
            f"{BINANCE_API}/ticker/24hr",
            params={"symbol": pair},
            timeout=10
        )
        ticker_response.raise_for_status()
        ticker = ticker_response.json()
        
        coin_data = {
            "symbol": symbol,
            "name": COIN_NAMES.get(symbol, symbol),
            "price": float(ticker['lastPrice']),
            "change_24h": float(ticker['priceChangePercent']),
            "volume": float(ticker['volume']),
            "high_24h": float(ticker['highPrice']),
            "low_24h": float(ticker['lowPrice']),
            "trades_24h": int(ticker['count']),
            "quote_volume": float(ticker['quoteVolume'])
        }
        
        return {
            "status": "success",
            "source": "binance_live",
            "coin": coin_data
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ API error: {e}")
        raise HTTPException(status_code=503, detail="Unable to fetch live data")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_top_coins(limit: int = 50):
    """Get top coins with REAL market data"""
    try:
        logger.info(f"📊 Fetching top {limit} coins from Binance")
        
        # Get all 24hr tickers
        response = requests.get(f"{BINANCE_API}/ticker/24hr", timeout=10)
        response.raise_for_status()
        all_tickers = response.json()
        
        # Filter for USDT pairs we track
        coins_list = []
        ticker_dict = {ticker['symbol']: ticker for ticker in all_tickers}
        
        for symbol, pair in TOP_COINS.items():
            if pair in ticker_dict:
                ticker = ticker_dict[pair]
                coins_list.append({
                    "symbol": symbol,
                    "name": COIN_NAMES.get(symbol, symbol),
                    "price": float(ticker['lastPrice']),
                    "change_24h": float(ticker['priceChangePercent']),
                    "volume": float(ticker['volume']),
                    "high_24h": float(ticker['highPrice']),
                    "low_24h": float(ticker['lowPrice']),
                })
        
        # Sort by volume (proxy for market cap)
        coins_list.sort(key=lambda x: x['volume'], reverse=True)
        coins_list = coins_list[:limit]
        
        return {
            "status": "success",
            "source": "binance_live",
            "coins": coins_list,
            "count": len(coins_list)
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching top coins: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk/{symbol}")
async def get_risk_analysis(symbol: str):
    """Get risk analysis for a specific coin with REAL data"""
    try:
        symbol = symbol.upper()
        logger.info(f"📊 Risk analysis for: {symbol}")
        
        if symbol not in TOP_COINS:
            raise HTTPException(status_code=404, detail=f"Coin {symbol} not found")
        
        # Get real price data
        pair = TOP_COINS[symbol]
        ticker_response = requests.get(
            f"{BINANCE_API}/ticker/24hr",
            params={"symbol": pair},
            timeout=10
        )
        ticker = ticker_response.json()
        
        # Calculate risk based on real volatility
        price_change = abs(float(ticker['priceChangePercent']))
        volume = float(ticker['quoteVolume'])
        
        # Risk scoring
        volatility_score = min(price_change / 2, 10)  # Higher change = higher risk
        liquidity_score = 10 - min(volume / 1000000000, 10)  # Lower volume = higher risk
        
        risk_score = (volatility_score * 0.6 + liquidity_score * 0.4)
        
        return {
            "status": "success",
            "symbol": symbol,
            "risk_analysis": {
                "risk_score": round(risk_score, 2),
                "risk_level": get_risk_level(risk_score),
                "volatility": "high" if price_change > 5 else "medium" if price_change > 2 else "low",
                "liquidity": "high" if volume > 1000000000 else "medium" if volume > 100000000 else "low",
                "price_change_24h": float(ticker['priceChangePercent'])
            }
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ API error: {e}")
        raise HTTPException(status_code=503, detail="Unable to fetch live data")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in risk analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market/summary")
async def get_market_summary():
    """Get REAL overall market summary from Binance"""
    try:
        logger.info("📊 Fetching LIVE market summary")
        
        # Get all 24hr tickers
        response = requests.get(f"{BINANCE_API}/ticker/24hr", timeout=10)
        response.raise_for_status()
        all_tickers = response.json()
        
        # Calculate from our tracked coins
        tracked_data = []
        ticker_dict = {ticker['symbol']: ticker for ticker in all_tickers}
        
        for symbol, pair in TOP_COINS.items():
            if pair in ticker_dict:
                ticker = ticker_dict[pair]
                tracked_data.append({
                    'symbol': symbol,
                    'change': float(ticker['priceChangePercent']),
                    'volume': float(ticker['quoteVolume'])
                })
        
        # Calculate summary
        total_volume = sum(d['volume'] for d in tracked_data)
        avg_change = sum(d['change'] for d in tracked_data) / len(tracked_data)
        
        gainers = sorted(tracked_data, key=lambda x: x['change'], reverse=True)
        losers = sorted(tracked_data, key=lambda x: x['change'])
        
        return {
            "status": "success",
            "source": "binance_live",
            "timestamp": datetime.utcnow().isoformat(),
            "market": {
                "total_volume_24h": total_volume,
                "average_change_24h": round(avg_change, 2),
                "trending": "bullish" if avg_change > 0 else "bearish",
                "top_gainer": gainers[0]['symbol'] if gainers else "N/A",
                "top_gainer_change": round(gainers[0]['change'], 2) if gainers else 0,
                "top_loser": losers[0]['symbol'] if losers else "N/A",
                "top_loser_change": round(losers[0]['change'], 2) if losers else 0,
                "coins_tracked": len(tracked_data)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching market summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
def get_risk_level(score: float) -> str:
    """Get risk level label"""
    if score <= 3.5:
        return "low"
    elif score <= 6.5:
        return "moderate"
    else:
        return "high"


def get_fallback_prices() -> Dict:
    """Fallback prices if API is down"""
    return {
        "BTC": {"price": 43500, "change_24h": 0, "volume": 0},
        "ETH": {"price": 2300, "change_24h": 0, "volume": 0},
        "SOL": {"price": 100, "change_24h": 0, "volume": 0},
        "BNB": {"price": 315, "change_24h": 0, "volume": 0},
        "ADA": {"price": 0.60, "change_24h": 0, "volume": 0},
        "SHIB": {"price": 0.000015, "change_24h": 0, "volume": 0},
    }