"""
Portfolio API Routes - FIXED to match exact database schema
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from datetime import datetime
import httpx

from app.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

# ==================== HELPER FUNCTIONS ====================

async def get_binance_price(symbol: str) -> float:
    """Get current price from Binance"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"https://api.binance.com/api/v3/ticker/price",
                params={'symbol': f'{symbol.upper()}USDT'}
            )
            
            if response.status_code == 200:
                data = response.json()
                return float(data['price'])
            return 0.0
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        return 0.0

# ==================== ROUTES ====================

@router.get("/{user_id}")
async def get_portfolio(user_id: int, db: Session = Depends(get_db)):
    """
    Get user's portfolio with real-time P&L calculations
    Matches exact database schema with current_value and profit_loss columns
    """
    try:
        logger.info(f"📊 Fetching portfolio for user {user_id}")
        
        # Get all holdings from database
        holdings = db.execute(
            text("""
                SELECT id, symbol, amount, avg_buy_price, current_value, profit_loss, created_at, updated_at
                FROM portfolio
                WHERE user_id = :user_id
                ORDER BY created_at DESC
            """),
            {"user_id": user_id}
        ).fetchall()
        
        if not holdings:
            logger.info(f"ℹ️ No holdings found for user {user_id}")
            return {
                "success": True,
                "user_id": user_id,
                "holdings": [],
                "total_invested": 0.0,
                "total_current_value": 0.0,
                "total_profit_loss": 0.0,
                "total_profit_loss_percent": 0.0,
                "holdings_count": 0
            }
        
        # Process each holding and get current prices
        updated_holdings = []
        total_invested = 0.0
        total_current_value = 0.0
        
        for holding in holdings:
            symbol = holding[1]
            amount = float(holding[2])
            avg_buy_price = float(holding[3])
            
            # Get live price from Binance
            current_price = await get_binance_price(symbol)
            
            # Calculate values
            invested_amount = amount * avg_buy_price
            current_value = amount * current_price if current_price > 0 else float(holding[4])
            profit_loss = current_value - invested_amount
            profit_loss_percent = (profit_loss / invested_amount * 100) if invested_amount > 0 else 0
            
            # Update totals
            total_invested += invested_amount
            total_current_value += current_value
            
            # Prepare holding data
            holding_data = {
                "id": holding[0],
                "symbol": symbol,
                "quantity": amount,
                "avg_buy_price": avg_buy_price,
                "current_price": current_price,
                "invested_amount": invested_amount,
                "current_value": current_value,
                "profit_loss": profit_loss,
                "profit_loss_percent": profit_loss_percent,
                "created_at": holding[6].isoformat() if holding[6] else None,
                "updated_at": holding[7].isoformat() if holding[7] else None
            }
            
            updated_holdings.append(holding_data)
            
            # Update database with latest values
            db.execute(
                text("""
                    UPDATE portfolio
                    SET current_value = :current_value,
                        profit_loss = :profit_loss,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """),
                {
                    "id": holding[0],
                    "current_value": current_value,
                    "profit_loss": profit_loss
                }
            )
        
        db.commit()
        
        # Calculate total P&L
        total_profit_loss = total_current_value - total_invested
        total_profit_loss_percent = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
        
        logger.info(f"✅ Portfolio loaded: {len(updated_holdings)} holdings, Total: ${total_current_value:.2f}, P&L: ${total_profit_loss:.2f}")
        
        return {
            "success": True,
            "user_id": user_id,
            "holdings": updated_holdings,
            "total_invested": round(total_invested, 2),
            "total_current_value": round(total_current_value, 2),
            "total_profit_loss": round(total_profit_loss, 2),
            "total_profit_loss_percent": round(total_profit_loss_percent, 2),
            "holdings_count": len(updated_holdings)
        }
        
    except Exception as e:
        logger.error(f"❌ Portfolio fetch error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch portfolio: {str(e)}")

@router.get("/{user_id}/summary")
async def get_portfolio_summary(user_id: int, db: Session = Depends(get_db)):
    """Get quick portfolio summary"""
    try:
        portfolio_data = await get_portfolio(user_id, db)
        
        return {
            "success": True,
            "user_id": user_id,
            "total_value": portfolio_data.get("total_current_value", 0),
            "total_invested": portfolio_data.get("total_invested", 0),
            "total_pnl": portfolio_data.get("total_profit_loss", 0),
            "pnl_percent": portfolio_data.get("total_profit_loss_percent", 0),
            "holdings_count": portfolio_data.get("holdings_count", 0)
        }
        
    except Exception as e:
        logger.error(f"❌ Summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def portfolio_health():
    """Portfolio service health check"""
    return {
        "status": "operational",
        "service": "portfolio",
        "features": {
            "get_portfolio": "enabled",
            "real_time_prices": "enabled",
            "pnl_tracking": "enabled"
        }
    }