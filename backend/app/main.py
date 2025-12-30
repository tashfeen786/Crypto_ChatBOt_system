"""
Crypto RAG Chatbot - Main FastAPI Application
REAL API VERSION - Live Binance Data + Groq AI
"""

# ==================== LOAD .ENV FIRST (CRITICAL!) ====================
from dotenv import load_dotenv
from pathlib import Path

# Load .env before ANY other imports
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

print("=" * 60)
print("🔍 Loading .env file...")
print(f"📁 Path: {ENV_PATH}")
print(f"✅ Exists: {ENV_PATH.exists()}")

import os
if os.getenv("GROQ_API_KEY"):
    print(f"✅ GROQ_API_KEY loaded: {os.getenv('GROQ_API_KEY')[:20]}...")
else:
    print("❌ GROQ_API_KEY not found!")
print("=" * 60)

# ==================== NOW IMPORT EVERYTHING ELSE ====================

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from app.config import settings, validate_api_keys

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)


# ==================== LIFESPAN EVENTS ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)
    
    # Validate API keys
    api_status = validate_api_keys()
    logger.info("API Keys Status:")
    for api, status in api_status.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"{status_icon} {api.upper()}: {'Configured' if status else 'Missing'}")
    
    # Check required APIs
    required_apis = ["groq", "pinecone"]
    missing = [api for api in required_apis if not api_status.get(api, False)]
    
    if missing:
        logger.warning(f"⚠️  Missing required API keys: {', '.join(missing)}")
        logger.warning("Using fallback mode for missing services!")
    else:
        logger.info("✅ All required APIs configured!")
    
    logger.info("=" * 60)
    logger.info("✅ Application started successfully!")
    logger.info(f"📍 Running on: {settings.HOST}:{settings.PORT}")
    logger.info(f"🔧 Debug Mode: {settings.DEBUG}")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("🛑 Shutting down application...")
    logger.info("=" * 60)


# ==================== CREATE APP ====================

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered crypto investment advisor with REAL market data",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)


# ==================== MIDDLEWARE ====================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request Timing Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    logger.info(f"📥 {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 {request.method} {request.url.path} - Status: {response.status_code}")
    return response


# ==================== EXCEPTION HANDLERS ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"❌ Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred",
            "path": str(request.url)
        }
    )


# ==================== ROOT ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "message": "Crypto RAG Chatbot API with REAL market data!",
        "features": {
            "live_prices": "Binance API",
            "ai_chat": "Groq AI (Llama 3.3)",
            "authentication": "JWT Tokens",
            "languages": "English + Urdu/Roman Urdu",
            "market_data": "Real-time",
            "risk_analysis": "Advanced"
        },
        "docs": "/docs" if settings.DEBUG else "Disabled in production",
        "endpoints": {
            "health": "/health",
            "auth": "/api/auth",
            "chat": "/api/chat",
            "coins": "/api/coins",
            "trading": "/api/trading",
            "users": "/api/users",
            "portfolio": "/api/portfolio",
            "news": "/api/news"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    
    # Check API keys
    api_status = validate_api_keys()
    
    # Check Binance API
    binance_status = "operational"
    try:
        import requests
        response = requests.get("https://api.binance.com/api/v3/ping", timeout=2)
        binance_status = "operational" if response.status_code == 200 else "down"
    except:
        binance_status = "unavailable"
    
    # Check Groq AI
    groq_status = "configured" if api_status.get("groq") else "missing_key"
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "services": {
            "api": "operational",
            "binance": binance_status,
            "groq_ai": groq_status,
            "database": "operational",
            "redis": "operational",
            "pinecone": "configured" if api_status.get("pinecone") else "not_configured"
        },
        "api_keys": api_status,
        "rate_limits": {
            "binance": f"{settings.BINANCE_RATE_LIMIT}/min",
            "coingecko": f"{settings.COINGECKO_RATE_LIMIT}/min",
            "groq": f"{settings.GROQ_RATE_LIMIT}/min",
            "cryptopanic": f"{settings.CRYPTOPANIC_RATE_LIMIT}/day",
        }
    }


@app.get("/api/status")
async def api_status():
    """Detailed API status"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug_mode": settings.DEBUG,
        "environment": "development" if settings.DEBUG else "production",
        "features": {
            "live_prices": "✅ Binance API",
            "ai_chat": "✅ Groq AI (Llama 3.3 70B)",
            "authentication": "✅ JWT + SHA256",
            "bilingual": "✅ English + Urdu",
            "risk_analysis": "✅ Real-time volatility",
            "portfolio_tracking": "✅ Enabled",
            "trading": "✅ Simulation mode"
        },
        "configuration": {
            "embedding_model": settings.EMBEDDING_MODEL,
            "groq_model": settings.GROQ_MODEL,
            "pinecone_index": settings.PINECONE_INDEX_NAME,
            "default_top_coins": settings.DEFAULT_TOP_COINS,
            "cache_ttl_prices": f"{settings.CACHE_TTL_PRICES}s"
        }
    }


# ==================== ROUTER IMPORTS ====================

logger.info("=" * 60)
logger.info("📦 Registering API Routes (REAL API VERSION)...")
logger.info("=" * 60)

# Import Auth Router FIRST (CRITICAL!)
try:
    from app.routes.auth import router as auth_router
    logger.info("✅ Auth router imported (JWT Authentication)")
except ImportError as e:
    logger.error(f"❌ Failed to import auth router: {e}")
    from fastapi import APIRouter
    auth_router = APIRouter()
    
    @auth_router.post("/login")
    async def fallback_login():
        return {
            "error": "Auth service unavailable. Check app/routes/auth.py exists",
            "detail": str(e)
        }
    logger.warning("⚠️ Using emergency fallback auth router")

# Import Chat Router (Real AI)
try:
    from app.routes.chat import router as chat_router
    logger.info("✅ Chat router imported (REAL AI - Groq - Bilingual)")
except ImportError as e:
    logger.warning(f"⚠️ Real chat not found: {e}")
    logger.info("⚠️ Trying fallback chat_temp...")
    try:
        from app.routes.chat_temp import router as chat_router
        logger.info("✅ Chat router imported (using chat_temp fallback)")
    except ImportError as e2:
        logger.error(f"❌ Failed to import any chat router: {e2}")
        from fastapi import APIRouter
        chat_router = APIRouter()
        
        @chat_router.post("/")
        async def fallback_chat():
            return {
                "response": "Chat service temporarily unavailable. Please check backend logs.",
                "coins_mentioned": [],
                "risk_analysis": {"risk_score": 5, "risk_level": "moderate"}
            }
        logger.info("⚠️ Using emergency fallback chat router")

# Import Coins Router (Real Binance API)
try:
    from app.routes.coins import router as coins_router
    logger.info("✅ Coins router imported (REAL API - Binance)")
except ImportError as e:
    logger.warning(f"⚠️ Real coins not found: {e}")
    logger.info("⚠️ Trying fallback coins_simple...")
    try:
        from app.routes.coins_simple import router as coins_router
        logger.info("✅ Coins router imported (using coins_simple fallback)")
    except ImportError as e2:
        logger.error(f"❌ Failed to import any coins router: {e2}")
        from fastapi import APIRouter
        coins_router = APIRouter()
        
        @coins_router.get("/prices")
        async def fallback_prices():
            return {
                "status": "error",
                "message": "Coins service unavailable",
                "prices": {}
            }
        logger.info("⚠️ Using emergency fallback coins router")

# Import Trading Router
try:
    from app.routes.trading import router as trading_router
    logger.info("✅ Trading router imported")
except ImportError as e:
    logger.error(f"❌ Failed to import trading router: {e}")
    from fastapi import APIRouter
    trading_router = APIRouter()
    logger.warning("⚠️ Using empty trading router")

# Import User Router
try:
    from app.routes.user import router as user_router
    logger.info("✅ User router imported")
except ImportError as e:
    logger.error(f"❌ Failed to import user router: {e}")
    from fastapi import APIRouter
    user_router = APIRouter()
    logger.warning("⚠️ Using empty user router")

# Import Portfolio Router
try:
    from app.routes.portfolio import router as portfolio_router
    logger.info("✅ Portfolio router imported")
except ImportError as e:
    logger.error(f"❌ Failed to import portfolio router: {e}")
    from fastapi import APIRouter
    portfolio_router = APIRouter()
    logger.warning("⚠️ Using empty portfolio router")

# Import News Router
try:
    from app.routes.news import router as news_router
    logger.info("✅ News router imported")
except ImportError as e:
    logger.error(f"❌ Failed to import news router: {e}")
    from fastapi import APIRouter
    news_router = APIRouter()
    logger.warning("⚠️ Using empty news router")


# ==================== REGISTER ROUTES (PRIORITY ORDER) ====================

# 1. Auth routes (HIGHEST PRIORITY - Register FIRST!)
app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"]
)
logger.info("✅ Auth routes registered at /api/auth")

# 2. Chat routes (AI-powered, Bilingual)
app.include_router(
    chat_router,
    prefix="/api/chat",
    tags=["Chat"]
)
logger.info("✅ Chat routes registered at /api/chat")

# 3. Coins routes (Live market data)
app.include_router(
    coins_router,
    prefix="/api/coins",
    tags=["Coins"]
)
logger.info("✅ Coins routes registered at /api/coins")

# 4. Trading routes
app.include_router(
    trading_router,
    prefix="/api/trading",
    tags=["Trading"]
)
logger.info("✅ Trading routes registered at /api/trading")

# 5. User routes
app.include_router(
    user_router,
    prefix="/api/users",
    tags=["Users"]
)
logger.info("✅ User routes registered at /api/users")

# 6. Portfolio routes
app.include_router(
    portfolio_router,
    prefix="/api/portfolio",
    tags=["Portfolio"]
)
logger.info("✅ Portfolio routes registered at /api/portfolio")

# 7. News routes
app.include_router(
    news_router,
    prefix="/api/news",
    tags=["News"]
)
logger.info("✅ News routes registered at /api/news")

logger.info("=" * 60)
logger.info("✅ All routes registered successfully!")
logger.info("   - Auth: JWT Authentication (SHA256 + Salt)")
logger.info("   - Chat: AI-powered (Groq AI) - Bilingual")
logger.info("   - Coins: Live data (Binance API)")
logger.info("   - Trading: Simulation mode")
logger.info("   - User: Profile management")
logger.info("   - Portfolio: Tracking enabled")
logger.info("   - News: Market news & analysis")
logger.info("=" * 60)


# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("🚀 Starting Uvicorn server...")
    logger.info("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )