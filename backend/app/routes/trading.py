"""
Trading Routes - Binance Integration (FIXED with user_id)
Handles buy, sell, and simulation operations
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from datetime import datetime
import httpx
from decimal import Decimal

from app.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class BuyRequest(BaseModel):
    user_id: int
    symbol: str
    amount_usd: float

class SellRequest(BaseModel):
    user_id: int
    symbol: str
    amount_coins: float

class SimulateBuyRequest(BaseModel):
    user_id: int
    symbol: str
    amount_usd: float

class PositionSizeRequest(BaseModel):
    balance: float
    risk_tolerance: int
    symbol: str

# ==================== HELPER FUNCTIONS ====================

async def get_binance_prices() -> Dict[str, float]:
    """Fetch ALL prices from Binance API"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.binance.com/api/v3/ticker/price"
            )
            
            if response.status_code != 200:
                raise Exception(f"Binance API error: {response.status_code}")
            
            data = response.json()
            
            # Convert to dict with clean symbols (remove USDT suffix)
            prices = {}
            for item in data:
                symbol = item['symbol']
                if symbol.endswith('USDT'):
                    clean_symbol = symbol.replace('USDT', '')
                    prices[clean_symbol] = float(item['price'])
            
            logger.info(f"✅ Fetched {len(prices)} prices from Binance")
            return prices
            
    except Exception as e:
        logger.error(f"❌ Binance API error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch prices: {str(e)}")

async def get_current_price(symbol: str) -> float:
    """Get current price for a specific symbol from Binance"""
    try:
        symbol_upper = symbol.upper()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"https://api.binance.com/api/v3/ticker/price",
                params={'symbol': f'{symbol_upper}USDT'}
            )
            
            if response.status_code != 200:
                raise Exception(f"Symbol {symbol} not found on Binance")
            
            data = response.json()
            price = float(data['price'])
            
            logger.info(f"✅ Fetched price for {symbol_upper}: ${price}")
            return price
            
    except Exception as e:
        logger.error(f"❌ Get price error for {symbol}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get price for {symbol}. Make sure it's listed on Binance."
        )

def calculate_fee(amount: float, fee_percentage: float = 0.001) -> float:
    """Calculate trading fee (0.1% default)"""
    return float(amount * fee_percentage)

# ==================== ROUTES ====================

@router.post("/buy")
async def execute_buy(request: BuyRequest, db: Session = Depends(get_db)):
    """Execute a buy order - FIXED with user_id"""
    try:
        logger.info(f"💰 Buy request: {request.symbol} for ${request.amount_usd} (User: {request.user_id})")
        
        # Get current price from Binance
        current_price = await get_current_price(request.symbol)
        
        # Calculate fee
        fee = calculate_fee(request.amount_usd)
        total_cost = request.amount_usd + fee
        
        # Check user balance - FIXED: using user_id instead of id
        user = db.execute(
            text("SELECT balance FROM users WHERE user_id = :user_id"),
            {"user_id": request.user_id}
        ).fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User {request.user_id} not found")
        
        # Convert Decimal to float for comparison
        user_balance = float(user[0])
        
        if user_balance < total_cost:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient balance. Need ${total_cost:.2f}, have ${user_balance:.2f}"
            )
        
        # Calculate coins received
        coins_received = request.amount_usd / current_price
        
        # Update user balance - FIXED: using user_id
        db.execute(
            text("UPDATE users SET balance = balance - :total_cost WHERE user_id = :user_id"),
            {"total_cost": total_cost, "user_id": request.user_id}
        )
        
        # Record trade - FIXED: using user_id
        db.execute(
            text("""
                INSERT INTO trades (user_id, symbol, trade_type, amount, price, total_value, fee)
                VALUES (:user_id, :symbol, 'BUY', :amount, :price, :total_value, :fee)
            """),
            {
                "user_id": request.user_id,
                "symbol": request.symbol.upper(),
                "amount": coins_received,
                "price": current_price,
                "total_value": request.amount_usd,
                "fee": fee
            }
        )
        
        # Update or create portfolio entry - FIXED: using user_id and id, with current_value and profit_loss
        existing_holding = db.execute(
            text("""
                SELECT id, amount, avg_buy_price 
                FROM portfolio 
                WHERE user_id = :user_id AND symbol = :symbol
            """),
            {"user_id": request.user_id, "symbol": request.symbol.upper()}
        ).fetchone()
        
        if existing_holding:
            # Update existing holding
            old_amount = float(existing_holding[1])
            old_avg_price = float(existing_holding[2])
            
            new_amount = old_amount + coins_received
            new_avg_price = ((old_amount * old_avg_price) + request.amount_usd) / new_amount
            
            # Calculate current value and P&L
            current_value = new_amount * current_price
            profit_loss = current_value - (new_amount * new_avg_price)
            
            db.execute(
                text("""
                    UPDATE portfolio 
                    SET amount = :new_amount,
                        avg_buy_price = :new_avg_price,
                        current_value = :current_value,
                        profit_loss = :profit_loss,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """),
                {
                    "new_amount": new_amount,
                    "new_avg_price": new_avg_price,
                    "current_value": current_value,
                    "profit_loss": profit_loss,
                    "id": existing_holding[0]
                }
            )
        else:
            # Create new holding
            current_value = coins_received * current_price
            profit_loss = 0  # No profit/loss on first purchase
            
            db.execute(
                text("""
                    INSERT INTO portfolio (user_id, symbol, amount, avg_buy_price, current_value, profit_loss)
                    VALUES (:user_id, :symbol, :amount, :avg_buy_price, :current_value, :profit_loss)
                """),
                {
                    "user_id": request.user_id,
                    "symbol": request.symbol.upper(),
                    "amount": coins_received,
                    "avg_buy_price": current_price,
                    "current_value": current_value,
                    "profit_loss": profit_loss
                }
            )
        
        db.commit()
        
        # Get updated balance - FIXED: using user_id
        new_balance_row = db.execute(
            text("SELECT balance FROM users WHERE user_id = :user_id"),
            {"user_id": request.user_id}
        ).fetchone()
        new_balance = float(new_balance_row[0])
        
        logger.info(f"✅ Buy order executed: {coins_received:.6f} {request.symbol}")
        
        return {
            "status": "success",
            "message": f"Successfully bought {coins_received:.6f} {request.symbol}",
            "order": {
                "type": "BUY",
                "symbol": request.symbol.upper(),
                "price": current_price,
                "amount_usd": request.amount_usd,
                "coins_received": coins_received,
                "fee": fee,
                "total_cost": total_cost
            },
            "updated_balance": new_balance
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Buy order failed: {e}")
        raise HTTPException(status_code=500, detail=f"Trade failed: {str(e)}")

@router.post("/sell")
async def execute_sell(request: SellRequest, db: Session = Depends(get_db)):
    """Execute a sell order - FIXED with user_id"""
    try:
        logger.info(f"💰 Sell request: {request.amount_coins} {request.symbol} (User: {request.user_id})")
        
        # Get current price from Binance
        current_price = await get_current_price(request.symbol)
        
        # Check if user has enough coins - FIXED: using user_id and id, get avg_buy_price
        holding = db.execute(
            text("""
                SELECT id, amount, avg_buy_price 
                FROM portfolio 
                WHERE user_id = :user_id AND symbol = :symbol
            """),
            {"user_id": request.user_id, "symbol": request.symbol.upper()}
        ).fetchone()
        
        if not holding:
            raise HTTPException(
                status_code=400, 
                detail=f"You don't own any {request.symbol}"
            )
        
        # Convert Decimal to float
        available_coins = float(holding[1])
        avg_buy_price = float(holding[2])
        
        if available_coins < request.amount_coins:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient coins. Need {request.amount_coins:.6f}, have {available_coins:.6f}"
            )
        
        # Calculate proceeds
        proceeds_usd = request.amount_coins * current_price
        fee = calculate_fee(proceeds_usd)
        net_proceeds = proceeds_usd - fee
        
        # Update user balance - FIXED: using user_id
        db.execute(
            text("UPDATE users SET balance = balance + :net_proceeds WHERE user_id = :user_id"),
            {"net_proceeds": net_proceeds, "user_id": request.user_id}
        )
        
        # Record trade - FIXED: using user_id
        db.execute(
            text("""
                INSERT INTO trades (user_id, symbol, trade_type, amount, price, total_value, fee)
                VALUES (:user_id, :symbol, 'SELL', :amount, :price, :total_value, :fee)
            """),
            {
                "user_id": request.user_id,
                "symbol": request.symbol.upper(),
                "amount": request.amount_coins,
                "price": current_price,
                "total_value": proceeds_usd,
                "fee": fee
            }
        )
        
        # Update portfolio
        new_amount = available_coins - request.amount_coins
        
        if new_amount <= 0.00000001:  # Close to zero
            # Remove holding - FIXED: using id
            db.execute(
                text("DELETE FROM portfolio WHERE id = :id"),
                {"id": holding[0]}
            )
            logger.info(f"Removed {request.symbol} from portfolio (sold all)")
        else:
            # Update holding - FIXED: using id, with current_value and profit_loss
            current_value = new_amount * current_price
            profit_loss = current_value - (new_amount * avg_buy_price)
            
            db.execute(
                text("""
                    UPDATE portfolio 
                    SET amount = :new_amount,
                        current_value = :current_value,
                        profit_loss = :profit_loss,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """),
                {
                    "new_amount": new_amount,
                    "current_value": current_value,
                    "profit_loss": profit_loss,
                    "id": holding[0]
                }
            )
        
        db.commit()
        
        # Get updated balance - FIXED: using user_id
        new_balance_row = db.execute(
            text("SELECT balance FROM users WHERE user_id = :user_id"),
            {"user_id": request.user_id}
        ).fetchone()
        new_balance = float(new_balance_row[0])
        
        logger.info(f"✅ Sell order executed: {request.amount_coins:.6f} {request.symbol}")
        
        return {
            "status": "success",
            "message": f"Successfully sold {request.amount_coins:.6f} {request.symbol}",
            "order": {
                "type": "SELL",
                "symbol": request.symbol.upper(),
                "price": current_price,
                "amount_coins": request.amount_coins,
                "proceeds_usd": proceeds_usd,
                "fee": fee,
                "net_proceeds": net_proceeds
            },
            "updated_balance": new_balance
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Sell order failed: {e}")
        raise HTTPException(status_code=500, detail=f"Trade failed: {str(e)}")

@router.post("/simulate-buy")
async def simulate_buy(request: SimulateBuyRequest, db: Session = Depends(get_db)):
    """Simulate a buy order without executing - FIXED with user_id"""
    try:
        logger.info(f"🔮 Simulating buy: {request.symbol} for ${request.amount_usd} (User: {request.user_id})")
        
        # Get current price from Binance
        current_price = await get_current_price(request.symbol)
        
        # Calculate values
        fee = calculate_fee(request.amount_usd)
        total_cost = request.amount_usd + fee
        coins_received = request.amount_usd / current_price
        
        # Get user balance - FIXED: using user_id
        user = db.execute(
            text("SELECT balance FROM users WHERE user_id = :user_id"),
            {"user_id": request.user_id}
        ).fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User {request.user_id} not found")
        
        current_balance = float(user[0])
        new_balance = current_balance - total_cost
        
        # Get portfolio percentage
        total_portfolio_value = current_balance
        impact_percentage = (request.amount_usd / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
        
        return {
            "status": "success",
            "simulation": {
                "coins_received": coins_received,
                "current_price": current_price,
                "fee": fee,
                "total_cost": total_cost,
                "impact": {
                    "portfolio_percentage": impact_percentage,
                    "current_balance": current_balance,
                    "new_balance": max(new_balance, 0)
                },
                "can_afford": new_balance >= 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@router.post("/simulate-sell")
async def simulate_sell(request: SellRequest, db: Session = Depends(get_db)):
    """Simulate a sell order without executing - FIXED with user_id"""
    try:
        logger.info(f"🔮 Simulating sell: {request.amount_coins} {request.symbol} (User: {request.user_id})")
        
        # Get current price from Binance
        current_price = await get_current_price(request.symbol)
        
        # Check if user has enough coins - FIXED: using user_id
        holding = db.execute(
            text("""
                SELECT amount 
                FROM portfolio 
                WHERE user_id = :user_id AND symbol = :symbol
            """),
            {"user_id": request.user_id, "symbol": request.symbol.upper()}
        ).fetchone()
        
        if not holding:
            raise HTTPException(
                status_code=400, 
                detail=f"You don't own any {request.symbol}"
            )
        
        available_coins = float(holding[0])
        
        if available_coins < request.amount_coins:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient coins. Need {request.amount_coins:.6f}, have {available_coins:.6f}"
            )
        
        # Calculate proceeds
        proceeds_usd = request.amount_coins * current_price
        fee = calculate_fee(proceeds_usd)
        net_proceeds = proceeds_usd - fee
        
        # Get user balance - FIXED: using user_id
        user = db.execute(
            text("SELECT balance FROM users WHERE user_id = :user_id"),
            {"user_id": request.user_id}
        ).fetchone()
        
        current_balance = float(user[0]) if user else 0
        new_balance = current_balance + net_proceeds
        
        return {
            "status": "success",
            "simulation": {
                "usd_received": net_proceeds,
                "current_price": current_price,
                "fee": fee,
                "gross_proceeds": proceeds_usd,
                "impact": {
                    "current_balance": current_balance,
                    "new_balance": new_balance
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@router.post("/position-size")
async def calculate_position_size(request: PositionSizeRequest):
    """Calculate recommended position size based on risk"""
    try:
        # Risk-based allocation (conservative approach)
        risk_multipliers = {
            1: 0.02, 2: 0.03, 3: 0.05, 4: 0.07, 5: 0.10,
            6: 0.15, 7: 0.20, 8: 0.25, 9: 0.30, 10: 0.40
        }
        
        multiplier = risk_multipliers.get(request.risk_tolerance, 0.10)
        recommended_amount = request.balance * multiplier
        
        return {
            "recommended_amount_usd": recommended_amount,
            "percentage_of_balance": multiplier * 100,
            "risk_level": "low" if request.risk_tolerance <= 3 else "medium" if request.risk_tolerance <= 6 else "high"
        }
        
    except Exception as e:
        logger.error(f"❌ Position size calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/price/{symbol}")
async def get_trading_price(symbol: str):
    """Get current trading price for a symbol from Binance"""
    try:
        price = await get_current_price(symbol)
        return {
            "symbol": symbol.upper(),
            "price": price,
            "source": "Binance",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Get price failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prices")
async def get_all_prices():
    """Get ALL prices from Binance"""
    try:
        prices = await get_binance_prices()
        return {
            "status": "success",
            "count": len(prices),
            "prices": prices,
            "source": "Binance",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Get prices failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fees")
async def get_trading_fees():
    """Get current trading fee structure"""
    return {
        "maker_fee": 0.001,  # 0.1%
        "taker_fee": 0.001,  # 0.1%
        "fee_currency": "USD",
        "minimum_trade": 1.0
    }

@router.get("/health")
async def trading_health():
    """Trading service health check"""
    return {
        "status": "operational",
        "exchange": "Binance",
        "features": {
            "buy": "enabled",
            "sell": "enabled",
            "simulation": "enabled",
            "all_coins": "enabled"
        }
    }