"""
Users Routes - FIXED with user_id
Handles user profile and portfolio data
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from datetime import datetime

from app.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    balance: float
    risk_tolerance: int
    full_name: Optional[str] = None

class PortfolioResponse(BaseModel):
    holdings: Dict[str, float]
    total_value: float
    total_invested: float

# ==================== ROUTES ====================

@router.get("/{user_id}")
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile with portfolio - FIXED with user_id"""
    try:
        logger.info(f"📥 Fetching profile for user: {user_id}")
        
        # Get user data - FIXED: using user_id
        user = db.execute(
            text("""
                SELECT user_id, username, email, balance, risk_tolerance, full_name
                FROM users 
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        ).fetchone()
        
        if not user:
            logger.error(f"❌ User {user_id} not found")
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        # Get portfolio holdings - FIXED: using user_id
        holdings = db.execute(
            text("""
                SELECT symbol, amount, avg_buy_price
                FROM portfolio
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        ).fetchall()
        
        # Convert holdings to dict
        portfolio_dict = {}
        for holding in holdings:
            symbol = holding[0]
            amount = float(holding[1])
            portfolio_dict[symbol] = amount
        
        # Get all transactions for invested calculation - FIXED: using timestamp not created_at
        transactions = db.execute(
            text("""
                SELECT trade_type, total_value, fee
                FROM trades
                WHERE user_id = :user_id
                ORDER BY timestamp DESC
            """),
            {"user_id": user_id}
        ).fetchall()
        
        # Calculate total invested
        total_invested = 0
        for tx in transactions:
            trade_type = tx[0]
            total_value = float(tx[1])
            fee = float(tx[2]) if tx[2] else 0
            
            if trade_type == 'BUY':
                total_invested += (total_value + fee)
            elif trade_type == 'SELL':
                total_invested -= (total_value - fee)
        
        logger.info(f"✅ Profile fetched for user {user_id}")
        
        return {
            "user_id": user[0],
            "username": user[1],
            "email": user[2],
            "balance": float(user[3]),
            "risk_tolerance": user[4],
            "full_name": user[5],
            "portfolio": {
                "holdings": portfolio_dict,
                "total_value": sum(portfolio_dict.values()),
                "total_invested": total_invested
            },
            "transactions": [
                {
                    "type": tx[0],
                    "amount": float(tx[1]),
                    "price": float(tx[1]) / float(tx[2]) if tx[2] else 0
                } for tx in transactions[:10]  # Last 10 transactions
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch user profile: {str(e)}")

@router.get("/{user_id}/balance")
async def get_user_balance(user_id: int, db: Session = Depends(get_db)):
    """Get user balance - FIXED with user_id"""
    try:
        # FIXED: using user_id instead of id
        result = db.execute(
            text("SELECT balance FROM users WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        return {
            "user_id": user_id,
            "balance": float(result[0])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/portfolio")
async def get_user_portfolio(user_id: int, db: Session = Depends(get_db)):
    """Get user portfolio holdings - FIXED with user_id"""
    try:
        # FIXED: using user_id
        holdings = db.execute(
            text("""
                SELECT symbol, amount, avg_buy_price, current_value, profit_loss
                FROM portfolio
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        ).fetchall()
        
        portfolio = []
        total_value = 0
        total_invested = 0
        
        for holding in holdings:
            symbol = holding[0]
            amount = float(holding[1])
            avg_buy_price = float(holding[2])
            current_value = float(holding[3]) if holding[3] else 0
            profit_loss = float(holding[4]) if holding[4] else 0
            
            invested = amount * avg_buy_price
            total_invested += invested
            total_value += current_value
            
            portfolio.append({
                "symbol": symbol,
                "amount": amount,
                "avg_buy_price": avg_buy_price,
                "current_value": current_value,
                "invested": invested,
                "profit_loss": profit_loss,
                "profit_loss_percentage": (profit_loss / invested * 100) if invested > 0 else 0
            })
        
        return {
            "user_id": user_id,
            "holdings": portfolio,
            "summary": {
                "total_value": total_value,
                "total_invested": total_invested,
                "total_profit_loss": total_value - total_invested,
                "total_profit_loss_percentage": ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/transactions")
async def get_user_transactions(
    user_id: int, 
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user transaction history - FIXED with user_id and timestamp"""
    try:
        # FIXED: using user_id, id instead of trade_id, timestamp instead of created_at
        transactions = db.execute(
            text("""
                SELECT id, symbol, trade_type, amount, price, total_value, fee, timestamp
                FROM trades
                WHERE user_id = :user_id
                ORDER BY timestamp DESC
                LIMIT :limit
            """),
            {"user_id": user_id, "limit": limit}
        ).fetchall()
        
        result = []
        for tx in transactions:
            result.append({
                "trade_id": tx[0],
                "symbol": tx[1],
                "type": tx[2],
                "amount": float(tx[3]),
                "price": float(tx[4]),
                "total_value": float(tx[5]),
                "fee": float(tx[6]) if tx[6] else 0,
                "timestamp": tx[7].isoformat() if tx[7] else None
            })
        
        return {
            "user_id": user_id,
            "transactions": result,
            "count": len(result)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}/balance")
async def update_user_balance(
    user_id: int,
    amount: float,
    db: Session = Depends(get_db)
):
    """Update user balance - FIXED with user_id"""
    try:
        # FIXED: using user_id
        db.execute(
            text("UPDATE users SET balance = :amount WHERE user_id = :user_id"),
            {"amount": amount, "user_id": user_id}
        )
        db.commit()
        
        return {
            "status": "success",
            "user_id": user_id,
            "new_balance": amount
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to update balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/performance")
async def get_portfolio_performance(user_id: int, db: Session = Depends(get_db)):
    """Get portfolio performance metrics - FIXED with user_id"""
    try:
        # Get user balance - FIXED: using user_id
        user = db.execute(
            text("SELECT balance FROM users WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        balance = float(user[0])
        
        # Get all transactions - FIXED: using user_id and timestamp
        trades = db.execute(
            text("""
                SELECT trade_type, amount, price, total_value, fee
                FROM trades
                WHERE user_id = :user_id
                ORDER BY timestamp
            """),
            {"user_id": user_id}
        ).fetchall()
        
        total_invested = 0
        total_withdrawn = 0
        
        for trade in trades:
            trade_type = trade[0]
            total_value = float(trade[3])
            fee = float(trade[4]) if trade[4] else 0
            
            if trade_type == 'BUY':
                total_invested += (total_value + fee)
            elif trade_type == 'SELL':
                total_withdrawn += (total_value - fee)
        
        # Get current portfolio value - FIXED: using user_id
        portfolio = db.execute(
            text("""
                SELECT SUM(current_value)
                FROM portfolio
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        ).fetchone()
        
        portfolio_value = float(portfolio[0]) if portfolio and portfolio[0] else 0
        
        # Calculate metrics
        current_value = balance + portfolio_value
        net_invested = total_invested - total_withdrawn
        total_pnl = current_value - (1000 + net_invested)  # Assuming 1000 starting balance
        pnl_percentage = (total_pnl / 1000 * 100) if net_invested > 0 else 0
        
        return {
            "status": "success",
            "user_id": user_id,
            "balance": balance,
            "portfolio_value": portfolio_value,
            "total_value": current_value,
            "total_invested": total_invested,
            "total_withdrawn": total_withdrawn,
            "net_invested": net_invested,
            "total_pnl": total_pnl,
            "pnl_percentage": pnl_percentage
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to calculate performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def users_health():
    """Users service health check"""
    return {
        "status": "operational",
        "service": "users",
        "endpoints": {
            "profile": "enabled",
            "balance": "enabled",
            "portfolio": "enabled",
            "transactions": "enabled",
            "performance": "enabled"
        }
    }