"""
Trading API Routes
Execute buy/sell orders, manage trades
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import logging
from datetime import datetime

from app.services.trading import trading_service
from app.services.binance import binance_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trading", tags=["Trading"])


# ==================== REQUEST/RESPONSE MODELS ====================

class BuyRequest(BaseModel):
    """Buy order request"""
    user_id: str = Field(..., description="User ID")
    symbol: str = Field(..., description="Coin symbol (BTC, ETH, etc.)")
    amount_usd: float = Field(..., ge=10, description="Amount in USD (minimum $10)")
    user_balance: float = Field(..., ge=0, description="User's available balance")
    user_risk_tolerance: int = Field(5, ge=1, le=10, description="User's risk tolerance")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "symbol": "BTC",
                "amount_usd": 100,
                "user_balance": 1000,
                "user_risk_tolerance": 5
            }
        }


class SellRequest(BaseModel):
    """Sell order request"""
    user_id: str = Field(..., description="User ID")
    symbol: str = Field(..., description="Coin symbol")
    quantity: float = Field(..., gt=0, description="Quantity to sell")
    avg_buy_price: float = Field(..., gt=0, description="Average buy price")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "symbol": "BTC",
                "quantity": 0.0026,
                "avg_buy_price": 35000
            }
        }


class PositionSizeRequest(BaseModel):
    """Calculate safe position size"""
    balance: float = Field(..., ge=0)
    risk_tolerance: int = Field(5, ge=1, le=10)
    symbol: str = Field(..., description="Coin symbol")


class StopLossRequest(BaseModel):
    """Stop loss check request"""
    portfolio: list = Field(..., description="List of holdings")
    stop_loss_percent: float = Field(5.0, description="Stop loss trigger %")
    take_profit_percent: float = Field(15.0, description="Take profit trigger %")
    
    class Config:
        json_schema_extra = {
            "example": {
                "portfolio": [
                    {
                        "symbol": "BTC",
                        "quantity": 0.0026,
                        "avg_buy_price": 40000
                    }
                ],
                "stop_loss_percent": 5.0,
                "take_profit_percent": 15.0
            }
        }


# ==================== ENDPOINTS ====================

@router.post("/buy")
async def execute_buy_order(request: BuyRequest):
    """
    Execute a buy order
    
    - **user_id**: Unique user identifier
    - **symbol**: Coin to buy (BTC, ETH, etc.)
    - **amount_usd**: Amount in USD to invest
    - **user_balance**: User's available balance
    - **user_risk_tolerance**: Risk level 1-10
    
    Returns order details and confirmation
    """
    try:
        logger.info(f"🛒 BUY order: {request.symbol} ${request.amount_usd} for user {request.user_id}")
        
        # Validate amount
        if request.amount_usd < 10:
            raise HTTPException(
                status_code=400,
                detail="Minimum investment amount is $10"
            )
        
        if request.amount_usd > request.user_balance:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Available: ${request.user_balance:.2f}"
            )
        
        # Execute trade
        result = await trading_service.execute_buy(
            user_id=request.user_id,
            symbol=request.symbol,
            amount_usd=request.amount_usd,
            user_balance=request.user_balance,
            user_risk_tolerance=request.user_risk_tolerance
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=result.get('message', 'Trade failed')
            )
        
        return {
            "success": True,
            "message": result['message'],
            "order": result['order'],
            "risk_analysis": result.get('risk_data', {}),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Buy order error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sell")
async def execute_sell_order(request: SellRequest):
    """
    Execute a sell order
    
    - **user_id**: Unique user identifier
    - **symbol**: Coin to sell
    - **quantity**: Amount to sell
    - **avg_buy_price**: Average buy price (for P&L calculation)
    
    Returns order details with profit/loss
    """
    try:
        logger.info(f"💰 SELL order: {request.quantity} {request.symbol} for user {request.user_id}")
        
        # Execute trade
        result = await trading_service.execute_sell(
            user_id=request.user_id,
            symbol=request.symbol,
            quantity=request.quantity,
            avg_buy_price=request.avg_buy_price
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=result.get('message', 'Trade failed')
            )
        
        return {
            "success": True,
            "message": result['message'],
            "order": result['order'],
            "pnl": result.get('pnl', {}),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Sell order error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/position-size")
async def calculate_position_size(request: PositionSizeRequest):
    """
    Calculate safe position size for a coin
    
    - **balance**: Available balance
    - **risk_tolerance**: User's risk level
    - **symbol**: Coin symbol
    
    Returns recommended investment amount
    """
    try:
        logger.info(f"📊 Position size calculation for {request.symbol}")
        
        # Get coin data to calculate risk
        coin_data = await binance_service.get_coin_price(request.symbol)
        if not coin_data:
            raise HTTPException(status_code=404, detail=f"Coin {request.symbol} not found")
        
        # Calculate risk
        from app.services.risk_engine import risk_engine
        risk_data = risk_engine.calculate_risk_score(coin_data)
        
        # Calculate position size
        position = trading_service.calculate_position_size(
            balance=request.balance,
            risk_tolerance=request.risk_tolerance,
            coin_risk_score=risk_data['risk_score']
        )
        
        return {
            "success": True,
            "symbol": request.symbol,
            "coin_risk": risk_data['risk_score'],
            "user_risk": request.risk_tolerance,
            "position": position,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Position size error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/price/{symbol}")
async def get_current_price(symbol: str):
    """
    Get current price for a coin (quick check before trade)
    
    - **symbol**: Coin symbol
    """
    try:
        coin_data = await binance_service.get_coin_price(symbol)
        if not coin_data:
            raise HTTPException(status_code=404, detail=f"Coin {symbol} not found")
        
        return {
            "success": True,
            "symbol": symbol,
            "price": coin_data['price'],
            "change_24h": coin_data['change_24h'],
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Price check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate-buy")
async def simulate_buy(request: BuyRequest):
    """
    Simulate a buy order (no actual execution)
    
    Shows what would happen without executing the trade
    """
    try:
        logger.info(f"🎮 Simulating BUY: {request.symbol} ${request.amount_usd}")
        
        # Get current price
        coin_data = await binance_service.get_coin_price(request.symbol)
        if not coin_data:
            raise HTTPException(status_code=404, detail=f"Coin {request.symbol} not found")
        
        # Calculate risk
        from app.services.risk_engine import risk_engine
        risk_data = risk_engine.calculate_risk_score(coin_data)
        
        # Calculate quantity
        quantity = request.amount_usd / coin_data['price']
        
        # Check risk vs user tolerance
        suitable = risk_data['risk_score'] <= request.user_risk_tolerance + 2
        
        return {
            "success": True,
            "simulation": {
                "symbol": request.symbol,
                "amount_usd": request.amount_usd,
                "price": coin_data['price'],
                "quantity": quantity,
                "risk_score": risk_data['risk_score'],
                "risk_level": risk_data['risk_level'],
                "suitable": suitable,
                "warning": None if suitable else "Risk exceeds your tolerance"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop-loss-check")
async def check_stop_loss(request: StopLossRequest):
    """
    Check portfolio for stop-loss or take-profit triggers
    
    - **portfolio**: List of holdings
    - **stop_loss_percent**: Stop loss trigger (default: 5%)
    - **take_profit_percent**: Take profit trigger (default: 15%)
    
    Returns list of triggered alerts
    """
    try:
        logger.info(f"⚠️ Checking stop-loss for {len(request.portfolio)} holdings")
        
        alerts = await trading_service.check_stop_loss(
            portfolio=request.portfolio,
            stop_loss_percent=request.stop_loss_percent,
            take_profit_percent=request.take_profit_percent
        )
        
        return {
            "success": True,
            "alerts": alerts,
            "has_alerts": len(alerts) > 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Stop-loss check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fees")
async def get_trading_fees():
    """
    Get trading fee information
    """
    return {
        "success": True,
        "fees": {
            "maker": 0.1,  # 0.1%
            "taker": 0.1,  # 0.1%
            "description": "Standard Binance fees"
        },
        "timestamp": datetime.now().isoformat()
    }


# ==================== HEALTH CHECK ====================

@router.get("/health")
async def trading_health():
    """Health check for trading service"""
    return {
        "status": "healthy",
        "service": "trading",
        "binance_connected": True,
        "timestamp": datetime.now().isoformat()
    }

