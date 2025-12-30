"""
Configuration settings - FIXED Complete Version
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

# ==================== LOAD .ENV FILE ====================
from dotenv import load_dotenv
from pathlib import Path

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load .env file
load_dotenv(dotenv_path=ENV_PATH)

print(f"🔍 Loading .env from: {ENV_PATH}")
print(f"📁 File exists: {ENV_PATH.exists()}")

# Verify GROQ_API_KEY loaded
if os.getenv("GROQ_API_KEY"):
    print(f"✅ GROQ_API_KEY loaded: {os.getenv('GROQ_API_KEY')[:20]}...")
else:
    print("❌ GROQ_API_KEY not found in .env!")


class Settings(BaseSettings):
    """Application settings"""
    
    # ==================== APPLICATION ====================
    APP_NAME: str = "Crypto RAG Chatbot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=True)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    

    SECRET_KEY: str = Field(default=True)
    # ==================== API KEYS ====================
    
    # Binance (Optional)
    BINANCE_API_KEY: str = Field(default="")
    BINANCE_API_SECRET: str = Field(default="")
    
    # CoinGecko (Optional)
    COINGECKO_API_KEY: str = Field(default="")
    
    # CryptoPanic (Optional)
    CRYPTOPANIC_API_KEY: str = Field(default="")
    
    # AI Models
    GEMINI_API_KEY: Optional[str] = Field(default=None)
    GROQ_API_KEY: str = Field(default="")  # Primary AI
    
    # Vector Database
    PINECONE_API_KEY: str = Field(default="")
    PINECONE_ENVIRONMENT: str = Field(default="us-east-1-aws")
    PINECONE_CLOUD: str = Field(default="aws") 
    PINECONE_REGION: str = Field(default="us-east-1")  
    
    # ==================== DATABASE ====================
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/crypto_rag"
    )
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # ==================== PINECONE ====================
    PINECONE_INDEX_NAME: str = Field(default="crypto-rag-index")
    PINECONE_DIMENSION: int = Field(default=384)
    PINECONE_METRIC: str = Field(default="cosine")
    
    # ==================== MODELS ====================
    EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile")
    GROQ_TEMPERATURE: float = Field(default=0.7)
    GROQ_MAX_TOKENS: int = Field(default=800)
    
    GEMINI_MODEL: str = Field(default="gemini-1.5-flash")
    GEMINI_TEMPERATURE: float = Field(default=0.3)
    GEMINI_MAX_TOKENS: int = Field(default=1000)
    
    # ==================== RATE LIMITS ====================
    BINANCE_RATE_LIMIT: int = Field(default=1200)
    COINGECKO_RATE_LIMIT: int = Field(default=30)
    GROQ_RATE_LIMIT: int = Field(default=30)
    CRYPTOPANIC_RATE_LIMIT: int = Field(default=100)
    GEMINI_RATE_LIMIT: int = Field(default=1500)
    
    # ==================== API ENDPOINTS ====================
    BINANCE_BASE_URL: str = Field(default="https://api.binance.com/api/v3")
    BINANCE_WS_URL: str = Field(default="wss://stream.binance.com:9443/ws")
    COINGECKO_BASE_URL: str = Field(default="https://api.coingecko.com/api/v3")
    CRYPTOPANIC_BASE_URL: str = Field(default="https://cryptopanic.com/api/v1")
    
    # ==================== CACHE ====================
    CACHE_TTL_PRICES: int = Field(default=300)
    CACHE_TTL_COIN_DATA: int = Field(default=600)
    CACHE_TTL_NEWS: int = Field(default=3600)
    
    # ==================== RISK ENGINE ====================
    RISK_WEIGHTS: dict = Field(
        default={
            "volatility": 0.35,
            "liquidity": 0.30,
            "trend": 0.20,
            "market_cap": 0.15
        }
    )
    RISK_LOW_THRESHOLD: float = Field(default=3.0)
    RISK_MEDIUM_THRESHOLD: float = Field(default=6.0)
    
    # ==================== INTERVALS ====================
    UPDATE_INTERVAL_MARKET: int = Field(default=300)
    UPDATE_INTERVAL_NEWS: int = Field(default=3600)
    
    # ==================== CORS ====================
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "https://your-frontend-domain.com"
        ]
    )
    
    # ==================== LOGGING ====================
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # ==================== DEFAULTS ====================
    DEFAULT_USER_RISK: int = Field(default=5)
    DEFAULT_TOP_COINS: int = Field(default=50)
    MAX_PAGE_SIZE: int = Field(default=100)
    DEFAULT_PAGE_SIZE: int = Field(default=20)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Don't use extra="forbid" - allow extra fields


# Create settings instance
settings = Settings()


# ==================== HELPER FUNCTIONS ====================

def get_database_url() -> str:
    """Get database URL"""
    return settings.DATABASE_URL


def get_redis_url() -> str:
    """Get Redis URL"""
    return settings.REDIS_URL


def is_production() -> bool:
    """Check if running in production"""
    return not settings.DEBUG


def get_binance_headers() -> dict:
    """Get headers for Binance API"""
    headers = {"Content-Type": "application/json"}
    if settings.BINANCE_API_KEY:
        headers["X-MBX-APIKEY"] = settings.BINANCE_API_KEY
    return headers


def get_coingecko_params() -> dict:
    """Get params for CoinGecko API"""
    params = {}
    if settings.COINGECKO_API_KEY:
        params["x_cg_demo_api_key"] = settings.COINGECKO_API_KEY
    return params


def validate_api_keys() -> dict:
    """Validate API keys"""
    return {
        "binance": bool(settings.BINANCE_API_KEY) or True,
        "coingecko": bool(settings.COINGECKO_API_KEY) or True,
        "cryptopanic": bool(settings.CRYPTOPANIC_API_KEY),
        "gemini": bool(settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else False,
        "groq": bool(settings.GROQ_API_KEY),
        "pinecone": bool(settings.PINECONE_API_KEY),
    }


# Debug print on import
if settings.DEBUG:
    print("=" * 50)
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION}")
    print("=" * 50)
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"Host: {settings.HOST}:{settings.PORT}")
    print(f"Database: {settings.DATABASE_URL[:30]}...")
    print(f"Redis: {settings.REDIS_URL[:30]}...")
    print("\nAPI Keys Status:")
    for api, status in validate_api_keys().items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {api.upper()}")
    print("=" * 50)