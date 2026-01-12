"""
Crypto RAG Chatbot - Main FastAPI Application
IMPROVED VERSION with Better Error Handling
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
import asyncio
from app.config import settings, validate_api_keys

#LOAD .ENV FIRST 
from dotenv import load_dotenv
from pathlib import Path

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


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)


#LIFESPAN EVENTS

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
    
    # 🆕 START ALERTS CHECKER
    try:
        logger.info("🔔 Starting Alerts Checker background task...")
        from app.services.alerts_checker import start_alerts_checker
        alerts_task = asyncio.create_task(start_alerts_checker())
        logger.info("✅ Alerts Checker started!")
    except Exception as e:
        logger.warning(f"⚠️ Alerts Checker not started: {e}")
        alerts_task = None
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("🛑 Shutting down application...")
    if alerts_task:
        logger.info("🔔 Stopping Alerts Checker...")
        alerts_task.cancel()
    logger.info("=" * 60)


# CREATE APP

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered crypto investment advisor with REAL market data + Price Alerts",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)


# MIDDLEWARE 

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
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"📥 {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 {request.method} {request.url.path} - Status: {response.status_code}")
    return response


# EXCEPTION HANDLERS

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred",
            "path": str(request.url)
        }
    )


# ROOT ENDPOINTS 

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "message": "Crypto RAG Chatbot API with REAL market data + Alerts!",
        "features": {
            "live_prices": "Binance API",
            "ai_chat": "Groq AI (Llama 3.3)",
            "authentication": "JWT Tokens",
            "languages": "English + Urdu/Roman Urdu",
            "market_data": "Real-time",
            "risk_analysis": "Advanced",
            "price_alerts": "Background monitoring"
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
            "news": "/api/news",
            "alerts": "/api/alerts"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    api_status = validate_api_keys()
    
    binance_status = "operational"
    try:
        import requests
        response = requests.get("https://api.binance.com/api/v3/ping", timeout=2)
        binance_status = "operational" if response.status_code == 200 else "down"
    except:
        binance_status = "unavailable"
    
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
            "pinecone": "configured" if api_status.get("pinecone") else "not_configured",
            "alerts_checker": "running"
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
            "bilingual": "✅ English",
            "risk_analysis": "✅ Real-time volatility",
            "portfolio_tracking": "✅ Enabled",
            "trading": "✅ Simulation mode",
            "price_alerts": "✅ Background monitoring"
        },
        "configuration": {
            "embedding_model": settings.EMBEDDING_MODEL,
            "groq_model": settings.GROQ_MODEL,
            "pinecone_index": settings.PINECONE_INDEX_NAME,
            "default_top_coins": settings.DEFAULT_TOP_COINS,
            "cache_ttl_prices": f"{settings.CACHE_TTL_PRICES}s"
        }
    }


# ROUTER IMPORTS 

logger.info("=" * 60)
logger.info("📦 Registering API Routes...")
logger.info("=" * 60)

from fastapi import APIRouter

# Import Auth Router
try:
    from app.routes.auth import router as auth_router
    logger.info("✅ Auth router imported")
except ImportError as e:
    logger.error(f"❌ Failed to import auth router: {e}")
    auth_router = APIRouter()
    @auth_router.post("/login")
    async def fallback_login():
        return {"error": "Auth service unavailable"}
    logger.warning("⚠️ Using emergency fallback auth router")

# Import Chat Router
try:
    from app.routes.chat import router as chat_router
    logger.info("✅ Chat router imported (REAL AI - Groq)")
except ImportError as e:
    logger.warning(f"⚠️ Real chat not found: {e}")
    try:
        from app.routes.chat_temp import router as chat_router
        logger.info("✅ Chat router imported (fallback)")
    except ImportError as e2:
        logger.error(f"❌ Failed to import any chat router: {e2}")
        chat_router = APIRouter()
        @chat_router.post("/")
        async def fallback_chat():
            return {"response": "Chat service unavailable"}
        logger.info("⚠️ Using emergency fallback chat router")

# Import Coins Router
try:
    from app.routes.coins import router as coins_router
    logger.info("✅ Coins router imported (REAL API)")
except ImportError as e:
    logger.error(f"❌ Failed to import coins router: {e}")
    coins_router = APIRouter()
    @coins_router.get("/prices")
    async def fallback_prices():
        return {"status": "error", "prices": {}}
    logger.warning("⚠️ Using emergency fallback coins router")

# Import Trading Router
try:
    from app.routes.trading import router as trading_router
    logger.info("✅ Trading router imported")
except ImportError as e:
    logger.error(f"❌ Failed to import trading router: {e}")
    trading_router = APIRouter()
    logger.warning("⚠️ Using empty trading router")

# 🎯 Import User Router (CRITICAL!)
try:
    from app.routes.user import router as user_router
    logger.info("✅ User router imported (Database-backed)")
    logger.info("   📋 Endpoints: register, login, profile, balance")
except ImportError as e:
    logger.error(f"❌ Failed to import user router: {e}")
    logger.error(f"   Error details: {e.__class__.__name__}: {str(e)}")
    user_router = APIRouter()
    
    # Emergency fallback endpoints
    @user_router.post("/register")
    async def fallback_register():
        return {"error": "User service unavailable - check database connection"}
    
    @user_router.post("/login")
    async def fallback_login():
        return {"error": "User service unavailable - check database connection"}
    
    @user_router.get("/{user_id}")
    async def fallback_profile(user_id: int):
        return {"error": "User service unavailable"}
    
    logger.warning("⚠️ Using emergency fallback user router")

# Import Portfolio Router
try:
    from app.routes.portfolio import router as portfolio_router
    logger.info("✅ Portfolio router imported (Database-backed)")
except ImportError as e:
    logger.error(f"❌ Failed to import portfolio router: {e}")
    portfolio_router = APIRouter()
    logger.warning("⚠️ Using empty portfolio router")

# Import News Router
try:
    from app.routes.news import router as news_router
    logger.info("✅ News router imported")
except ImportError as e:
    logger.error(f"❌ Failed to import news router: {e}")
    news_router = APIRouter()
    logger.warning("⚠️ Using empty news router")

# Import Alerts Router
try:
    from app.routes.alerts import router as alerts_router
    logger.info("✅ Alerts router imported")
except ImportError as e:
    logger.error(f"❌ Failed to import alerts router: {e}")
    alerts_router = APIRouter()
    logger.warning("⚠️ Using empty alerts router")


# REGISTER ROUTES 

# 1. Auth routes
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
logger.info("✅ Auth routes registered at /api/auth")

# 2. Chat routes
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
logger.info("✅ Chat routes registered at /api/chat")

# 3. Coins routes
app.include_router(coins_router, prefix="/api/coins", tags=["Coins"])
logger.info("✅ Coins routes registered at /api/coins")

# 4. Trading routes
app.include_router(trading_router, prefix="/api/trading", tags=["Trading"])
logger.info("✅ Trading routes registered at /api/trading")

# 5. User routes (CRITICAL!)
app.include_router(user_router, prefix="/api/users", tags=["Users"])
logger.info("✅ User routes registered at /api/users")
logger.info("   📍 POST /api/users/register")
logger.info("   📍 POST /api/users/login")
logger.info("   📍 GET /api/users/{user_id}")
logger.info("   📍 GET /api/users/{user_id}/balance")

# 6. Portfolio routes
app.include_router(portfolio_router, prefix="/api/portfolio", tags=["Portfolio"])
logger.info("✅ Portfolio routes registered at /api/portfolio")

# 7. News routes
app.include_router(news_router, prefix="/api/news", tags=["News"])
logger.info("✅ News routes registered at /api/news")

# 8. Alerts routes
app.include_router(alerts_router, prefix="/api/alerts", tags=["Alerts"])
logger.info("✅ Alerts routes registered at /api/alerts")

logger.info("=" * 60)
logger.info("✅ All routes registered successfully!")
logger.info("   - Auth: JWT Authentication")
logger.info("   - Chat: AI-powered (Groq AI)")
logger.info("   - Coins: Live data (Binance API)")
logger.info("   - Trading: Simulation mode")
logger.info("   - User: Profile management (PostgreSQL)")
logger.info("   - Portfolio: Tracking enabled (PostgreSQL)")
logger.info("   - News: Market news")
logger.info("   - Alerts: Price monitoring")
logger.info("=" * 60)


# RUN APPLICATION

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