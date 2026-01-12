"""
News Routes - CryptoPanic v2 API Integration
"""
from fastapi import APIRouter, HTTPException
import logging
import requests
import os
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# CryptoPanic v2 API
CRYPTOPANIC_API = "https://cryptopanic.com/api/developer/v2"
API_KEY = os.getenv("CRYPTOPANIC_API_KEY")


# ✅ CORRECT: Just "/latest" (not "/news/latest")
@router.get("/latest")
async def get_latest_news(limit: int = 10, filter: str = "hot"):
    """
    Get latest crypto news from CryptoPanic v2 API
    
    Query params:
    - limit: Number of news items (default: 10)
    - filter: hot, rising, bullish, bearish, important, saved, lol
    """
    try:
        logger.info(f"📰 Fetching latest crypto news (filter: {filter})")
        
        # Call CryptoPanic v2 API
        response = requests.get(
            f"{CRYPTOPANIC_API}/posts/",
            params={
                "auth_token": API_KEY,
                "filter": filter,
                "currencies": "BTC,ETH,BNB,SOL,XRP,ADA",
                "kind": "news"
            },
            timeout=10
        )
        
        logger.info(f"📡 API Response Status: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        
        # Format news items
        news_items = []
        results = data.get("results", [])
        
        logger.info(f"📰 Raw results count: {len(results)}")
        
        for post in results[:limit]:
            news_items.append({
                "id": post.get("id"),
                "title": post.get("title"),
                "url": post.get("url"),
                "description": post.get("description", ""),
                "source": post.get("source", {}).get("title", "CryptoNews") if isinstance(post.get("source"), dict) else "CryptoNews",
                "published_at": post.get("published_at", post.get("created_at")),
                "domain": post.get("domain", ""),
                "currencies": [c.get("code") if isinstance(c, dict) else c for c in post.get("currencies", [])],
            })
        
        logger.info(f"✅ Fetched {len(news_items)} news items")
        
        return {
            "status": "success",
            "source": "cryptopanic_v2",
            "timestamp": datetime.utcnow().isoformat(),
            "news": news_items,
            "count": len(news_items)
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ CryptoPanic API error: {e}")
        # Return fallback news
        return {
            "status": "fallback",
            "news": get_fallback_news(),
            "count": len(get_fallback_news())
        }
    except Exception as e:
        logger.error(f"❌ Error fetching news: {e}")
        return {
            "status": "fallback",
            "news": get_fallback_news(),
            "count": len(get_fallback_news())
        }


# ✅ CORRECT: Just "/by-coin/{symbol}" (not "/news/by-coin/{symbol}")
@router.get("/by-coin/{symbol}")
async def get_news_by_coin(symbol: str, limit: int = 10):
    """Get news for specific coin (v2 API)"""
    try:
        symbol = symbol.upper()
        logger.info(f"📰 Fetching news for: {symbol}")
        
        response = requests.get(
            f"{CRYPTOPANIC_API}/posts/",
            params={
                "auth_token": API_KEY,
                "currencies": symbol,
                "kind": "news"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        news_items = []
        for post in data.get("results", [])[:limit]:
            news_items.append({
                "id": post.get("id"),
                "title": post.get("title"),
                "url": post.get("url"),
                "source": post.get("source", {}).get("title", "CryptoNews") if isinstance(post.get("source"), dict) else "CryptoNews",
                "published_at": post.get("published_at", post.get("created_at")),
            })
        
        return {
            "status": "success",
            "symbol": symbol,
            "news": news_items,
            "count": len(news_items)
        }
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {
            "status": "fallback",
            "news": get_fallback_news(),
            "count": len(get_fallback_news())
        }


def get_fallback_news():
    """Fallback news if API fails"""
    return [
        {
            "id": 1,
            "title": "Bitcoin reaches new milestone in 2025",
            "url": "https://cryptonews.com",
            "description": "Bitcoin continues its upward trend",
            "source": "CryptoNews",
            "published_at": datetime.utcnow().isoformat(),
            "currencies": ["BTC"]
        },
        {
            "id": 2,
            "title": "Ethereum upgrade brings new features",
            "url": "https://coindesk.com",
            "description": "Network improvements announced",
            "source": "CoinDesk",
            "published_at": datetime.utcnow().isoformat(),
            "currencies": ["ETH"]
        },
        {
            "id": 3,
            "title": "Solana network performance improves significantly",
            "url": "https://cryptonews.com",
            "description": "Transaction speeds reach new highs",
            "source": "CryptoNews",
            "published_at": datetime.utcnow().isoformat(),
            "currencies": ["SOL"]
        }
    ]