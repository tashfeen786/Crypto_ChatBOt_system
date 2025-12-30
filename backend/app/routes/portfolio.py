"""
Portfolio Management API Routes
Track holdings, calculate P&L, manage portfolio
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
from datetime import datetime

from app.services.binance import binance_service
from app.services.trading import trading_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


# ==================== IN-MEMORY PORTFOLIO STORAGE ====================
# In production, replace with actual database
PORTFOLIOS_DB = {}


# ==================== REQUEST/RESPONSE MODELS ====================

class HoldingModel(BaseModel):
    """Portfolio holding"""
    symbol: str
    quantity: float
    avg_buy_price: float
    current_price: Optional[float] = 0
    current_value: Optional[float] = 0
    profit_loss: Optional[float] = 0
    profit_loss_percent: Optional[float] = 0
    invested_amount: Optional[float] = 0


class AddHoldingRequest(BaseModel):
    """Add holding to portfolio"""
    user_id: str
    symbol: str = Field(..., description="Coin symbol")
    quantity: float = Field(..., gt=0, description="Quantity purchased")
    avg_buy_price: float = Field(..., gt=0, description="Average buy price")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "symbol": "BTC",
                "quantity": 0.0026,
                "avg_buy_price": 37890
            }
        }


# ==================== ENDPOINTS ====================

@router.get("/{user_id}")
async def get_portfolio(user_id: str):
    """
    Get user's complete portfolio with current values
    
    - **user_id**: User's unique ID
    
    Returns all holdings with P&L calculations
    """
    try:
        logger.info(f"📊 Getting portfolio for user {user_id}")
        
        # Get portfolio
        portfolio = PORTFOLIOS_DB.get(user_id, [])
        
        if not portfolio:
            return {
                "success": True,
                "user_id": user_id,
                "holdings": [],
                "total_invested": 0,
                "total_current_value": 0,
                "total_profit_loss": 0,
                "total_profit_loss_percent": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        # Update current prices and calculate P&L
        total_invested = 0
        total_current_value = 0
        updated_holdings = []
        
        for holding in portfolio:
            # Get current price
            coin_data = await binance_service.get_coin_price(holding['symbol'])
            
            if coin_data:
                current_price = coin_data['price']
                invested = holding['quantity'] * holding['avg_buy_price']
                current_value = holding['quantity'] * current_price
                pnl = current_value - invested
                pnl_percent = (pnl / invested * 100) if invested > 0 else 0
                
                updated_holding = {
                    **holding,
                    'current_price': current_price,
                    'invested_amount': invested,
                    'current_value': current_value,
                    'profit_loss': pnl,
                    'profit_loss_percent': pnl_percent
                }
                
                updated_holdings.append(updated_holding)
                total_invested += invested
                total_current_value += current_value
        
        total_pnl = total_current_value - total_invested
        total_pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        
        return {
            "success": True,
            "user_id": user_id,
            "holdings": updated_holdings,
            "total_invested": total_invested,
            "total_current_value": total_current_value,
            "total_profit_loss": total_pnl,
            "total_profit_loss_percent": total_pnl_percent,
            "holdings_count": len(updated_holdings),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Portfolio error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-holding")
async def add_holding(request: AddHoldingRequest):
    """
    Add a new holding to portfolio
    
    Called after successful buy order
    """
    try:
        logger.info(f"➕ Adding holding: {request.symbol} for user {request.user_id}")
        
        # Get or create portfolio
        if request.user_id not in PORTFOLIOS_DB:
            PORTFOLIOS_DB[request.user_id] = []
        
        portfolio = PORTFOLIOS_DB[request.user_id]
        
        # Check if holding already exists
        existing = None
        for i, holding in enumerate(portfolio):
            if holding['symbol'] == request.symbol:
                existing = i
                break
        
        if existing is not None:
            # Update existing holding (average price)
            old_holding = portfolio[existing]
            total_quantity = old_holding['quantity'] + request.quantity
            total_cost = (old_holding['quantity'] * old_holding['avg_buy_price']) + \
                        (request.quantity * request.avg_buy_price)
            new_avg_price = total_cost / total_quantity
            
            portfolio[existing] = {
                'symbol': request.symbol,
                'quantity': total_quantity,
                'avg_buy_price': new_avg_price,
                'last_updated': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Updated holding: {request.symbol}")
        else:
            # Add new holding
            holding = {
                'symbol': request.symbol,
                'quantity': request.quantity,
                'avg_buy_price': request.avg_buy_price,
                'added_at': datetime.now().isoformat()
            }
            portfolio.append(holding)
            
            logger.info(f"✅ Added new holding: {request.symbol}")
        
        return {
            "success": True,
            "user_id": request.user_id,
            "holding": portfolio[existing] if existing is not None else portfolio[-1],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Add holding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/holdings/{symbol}")
async def remove_holding(user_id: str, symbol: str, quantity: Optional[float] = None):
    """
    Remove a holding from portfolio
    
    - **user_id**: User's unique ID
    - **symbol**: Coin symbol
    - **quantity**: Amount to remove (if None, remove all)
    
    Called after successful sell order
    """
    try:
        logger.info(f"➖ Removing {symbol} from portfolio for user {user_id}")
        
        portfolio = PORTFOLIOS_DB.get(user_id, [])
        
        # Find holding
        holding_index = None
        for i, holding in enumerate(portfolio):
            if holding['symbol'] == symbol:
                holding_index = i
                break
        
        if holding_index is None:
            raise HTTPException(status_code=404, detail=f"Holding {symbol} not found")
        
        holding = portfolio[holding_index]
        
        # Remove or update quantity
        if quantity is None or quantity >= holding['quantity']:
            # Remove entire holding
            del portfolio[holding_index]
            logger.info(f"✅ Removed entire holding: {symbol}")
        else:
            # Reduce quantity
            portfolio[holding_index]['quantity'] -= quantity
            logger.info(f"✅ Reduced holding: {symbol} by {quantity}")
        
        return {
            "success": True,
            "user_id": user_id,
            "symbol": symbol,
            "removed_quantity": quantity or holding['quantity'],
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Remove holding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/performance")
async def get_portfolio_performance(user_id: str):
    """
    Get portfolio performance analytics
    
    - **user_id**: User's unique ID
    """
    try:
        logger.info(f"📈 Getting performance for user {user_id}")
        
        # Get portfolio with current values
        portfolio_data = await get_portfolio(user_id)
        
        holdings = portfolio_data.get('holdings', [])
        
        if not holdings:
            return {
                "success": True,
                "user_id": user_id,
                "performance": {
                    "total_return": 0,
                    "total_return_percent": 0,
                    "best_performer": None,
                    "worst_performer": None,
                    "winners": 0,
                    "losers": 0
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Find best and worst performers
        best = max(holdings, key=lambda x: x.get('profit_loss_percent', 0))
        worst = min(holdings, key=lambda x: x.get('profit_loss_percent', 0))
        
        # Count winners and losers
        winners = sum(1 for h in holdings if h.get('profit_loss', 0) > 0)
        losers = sum(1 for h in holdings if h.get('profit_loss', 0) < 0)
        
        return {
            "success": True,
            "user_id": user_id,
            "performance": {
                "total_return": portfolio_data.get('total_profit_loss', 0),
                "total_return_percent": portfolio_data.get('total_profit_loss_percent', 0),
                "best_performer": {
                    "symbol": best['symbol'],
                    "return_percent": best.get('profit_loss_percent', 0)
                },
                "worst_performer": {
                    "symbol": worst['symbol'],
                    "return_percent": worst.get('profit_loss_percent', 0)
                },
                "winners": winners,
                "losers": losers,
                "win_rate": (winners / len(holdings) * 100) if holdings else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Performance error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/alerts")
async def get_portfolio_alerts(user_id: str):
    """
    Get alerts for portfolio (stop-loss, take-profit)
    
    - **user_id**: User's unique ID
    """
    try:
        logger.info(f"🚨 Checking alerts for user {user_id}")
        
        portfolio = PORTFOLIOS_DB.get(user_id, [])
        
        if not portfolio:
            return {
                "success": True,
                "alerts": [],
                "has_alerts": False,
                "timestamp": datetime.now().isoformat()
            }
        
        # Check for alerts
        alerts = await trading_service.check_stop_loss(
            portfolio=portfolio,
            stop_loss_percent=5.0,
            take_profit_percent=15.0
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "alerts": alerts,
            "has_alerts": len(alerts) > 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/summary")
async def get_portfolio_summary(user_id: str):
    """
    Get portfolio summary (quick overview)
    
    - **user_id**: User's unique ID
    """
    try:
        portfolio_data = await get_portfolio(user_id)
        
        return {
            "success": True,
            "summary": {
                "total_value": portfolio_data.get('total_current_value', 0),
                "total_invested": portfolio_data.get('total_invested', 0),
                "total_pnl": portfolio_data.get('total_profit_loss', 0),
                "pnl_percent": portfolio_data.get('total_profit_loss_percent', 0),
                "holdings_count": portfolio_data.get('holdings_count', 0),
                "status": "profit" if portfolio_data.get('total_profit_loss', 0) > 0 else "loss"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/rebalance")
async def suggest_rebalancing(user_id: str):
    """
    Get portfolio rebalancing suggestions
    
    - **user_id**: User's unique ID
    """
    try:
        logger.info(f"⚖️ Rebalancing suggestions for user {user_id}")
        
        portfolio_data = await get_portfolio(user_id)
        holdings = portfolio_data.get('holdings', [])
        
        if not holdings:
            return {
                "success": True,
                "needs_rebalancing": False,
                "suggestions": [],
                "timestamp": datetime.now().isoformat()
            }
        
        # Simple rebalancing logic
        # Check if any single coin is more than 50% of portfolio
        total_value = portfolio_data.get('total_current_value', 0)
        
        suggestions = []
        for holding in holdings:
            allocation_percent = (holding.get('current_value', 0) / total_value * 100) if total_value > 0 else 0
            
            if allocation_percent > 50:
                suggestions.append({
                    "symbol": holding['symbol'],
                    "current_allocation": allocation_percent,
                    "suggested_allocation": 40,
                    "action": "REDUCE",
                    "reason": "Overconcentrated in single asset"
                })
            elif allocation_percent < 5 and len(holdings) > 3:
                suggestions.append({
                    "symbol": holding['symbol'],
                    "current_allocation": allocation_percent,
                    "suggested_allocation": 10,
                    "action": "INCREASE",
                    "reason": "Underweighted position"
                })
        
        return {
            "success": True,
            "needs_rebalancing": len(suggestions) > 0,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Rebalancing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== HEALTH CHECK ====================

@router.get("/health")
async def portfolio_health():
    """Health check for portfolio service"""
    return {
        "status": "healthy",
        "service": "portfolio",
        "active_portfolios": len(PORTFOLIOS_DB),
        "timestamp": datetime.now().isoformat()
    }