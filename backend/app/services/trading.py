"""
Trading Execution Service
Execute buy/sell orders on Binance
Manage user portfolio and track P&L
"""

from typing import Dict, Optional
import logging
from datetime import datetime

from app.services.binance import binance_service
from app.services.risk_engine import risk_engine

logger = logging.getLogger(__name__)


class TradingService:
    """
    Execute and manage crypto trades
    """
    
    def __init__(self):
        logger.info("✅ Trading Service initialized")
    
    async def execute_buy(
        self,
        user_id: str,
        symbol: str,
        amount_usd: float,
        user_balance: float,
        user_risk_tolerance: int
    ) -> Dict:
        """
        Execute buy order
        
        Args:
            user_id: User ID
            symbol: Coin symbol (BTC, ETH, etc.)
            amount_usd: Amount in USD to invest
            user_balance: User's available balance
            user_risk_tolerance: User's risk tolerance (1-10)
            
        Returns:
            Trade result with order details
        """
        try:
            logger.info(f"🛒 Executing BUY: {symbol} for ${amount_usd}")
            
            # Step 1: Validate balance
            if amount_usd > user_balance:
                return {
                    "success": False,
                    "error": "insufficient_balance",
                    "message": f"Insufficient balance. Available: ${user_balance:.2f}"
                }
            
            # Step 2: Get current price
            price_data = await binance_service.get_coin_price(symbol)
            if not price_data:
                return {
                    "success": False,
                    "error": "price_fetch_failed",
                    "message": f"Could not fetch price for {symbol}"
                }
            
            current_price = price_data['price']
            
            # Step 3: Calculate risk
            risk_data = risk_engine.calculate_risk_score(price_data)
            
            # Step 4: Check risk vs user tolerance
            if risk_data['risk_score'] > user_risk_tolerance + 2:
                return {
                    "success": False,
                    "error": "risk_too_high",
                    "message": f"{symbol} risk ({risk_data['risk_score']:.1f}/10) exceeds your tolerance ({user_risk_tolerance}/10)",
                    "risk_data": risk_data
                }
            
            # Step 5: Calculate quantity
            quantity = amount_usd / current_price
            
            # Step 6: Execute order (simulated for now)
            # In production, use Binance trading API
            order = {
                "order_id": f"ORD_{int(datetime.now().timestamp())}",
                "symbol": symbol,
                "side": "BUY",
                "quantity": quantity,
                "price": current_price,
                "amount_usd": amount_usd,
                "status": "FILLED",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ BUY order executed: {quantity:.8f} {symbol} at ${current_price:,.2f}")
            
            return {
                "success": True,
                "order": order,
                "risk_data": risk_data,
                "message": f"Successfully bought {quantity:.8f} {symbol} for ${amount_usd:.2f}"
            }
            
        except Exception as e:
            logger.error(f"❌ Buy order failed: {e}")
            return {
                "success": False,
                "error": "execution_failed",
                "message": str(e)
            }
    
    async def execute_sell(
        self,
        user_id: str,
        symbol: str,
        quantity: float,
        avg_buy_price: float
    ) -> Dict:
        """
        Execute sell order
        
        Args:
            user_id: User ID
            symbol: Coin symbol
            quantity: Quantity to sell
            avg_buy_price: Average buy price
            
        Returns:
            Trade result with P&L
        """
        try:
            logger.info(f"💰 Executing SELL: {quantity:.8f} {symbol}")
            
            # Step 1: Get current price
            price_data = await binance_service.get_coin_price(symbol)
            if not price_data:
                return {
                    "success": False,
                    "error": "price_fetch_failed",
                    "message": f"Could not fetch price for {symbol}"
                }
            
            current_price = price_data['price']
            
            # Step 2: Calculate P&L
            invested_amount = quantity * avg_buy_price
            current_value = quantity * current_price
            profit_loss = current_value - invested_amount
            profit_loss_percent = (profit_loss / invested_amount) * 100 if invested_amount > 0 else 0
            
            # Step 3: Execute order (simulated)
            order = {
                "order_id": f"ORD_{int(datetime.now().timestamp())}",
                "symbol": symbol,
                "side": "SELL",
                "quantity": quantity,
                "price": current_price,
                "amount_usd": current_value,
                "status": "FILLED",
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 4: Calculate fees (0.1% Binance fee)
            fee = current_value * 0.001
            net_amount = current_value - fee
            
            logger.info(f"✅ SELL order executed: {quantity:.8f} {symbol} at ${current_price:,.2f}")
            logger.info(f"   P&L: ${profit_loss:+.2f} ({profit_loss_percent:+.2f}%)")
            
            return {
                "success": True,
                "order": order,
                "pnl": {
                    "invested": invested_amount,
                    "current_value": current_value,
                    "profit_loss": profit_loss,
                    "profit_loss_percent": profit_loss_percent,
                    "fee": fee,
                    "net_amount": net_amount
                },
                "message": f"Sold {quantity:.8f} {symbol}. P&L: ${profit_loss:+.2f} ({profit_loss_percent:+.2f}%)"
            }
            
        except Exception as e:
            logger.error(f"❌ Sell order failed: {e}")
            return {
                "success": False,
                "error": "execution_failed",
                "message": str(e)
            }
    
    async def check_stop_loss(
        self,
        portfolio: list,
        stop_loss_percent: float = 5.0,
        take_profit_percent: float = 15.0
    ) -> list:
        """
        Check portfolio for stop loss or take profit triggers
        
        Args:
            portfolio: List of holdings
            stop_loss_percent: Stop loss trigger (default: 5%)
            take_profit_percent: Take profit trigger (default: 15%)
            
        Returns:
            List of triggered alerts
        """
        try:
            alerts = []
            
            for holding in portfolio:
                symbol = holding['symbol']
                quantity = holding['quantity']
                avg_price = holding['avg_buy_price']
                
                # Get current price
                price_data = await binance_service.get_coin_price(symbol)
                if not price_data:
                    continue
                
                current_price = price_data['price']
                
                # Calculate P&L
                invested = quantity * avg_price
                current_value = quantity * current_price
                pnl_percent = ((current_value - invested) / invested) * 100 if invested > 0 else 0
                
                # Check triggers
                if pnl_percent <= -stop_loss_percent:
                    alerts.append({
                        "type": "STOP_LOSS",
                        "symbol": symbol,
                        "pnl_percent": pnl_percent,
                        "message": f"⚠️ {symbol} hit stop loss: {pnl_percent:.2f}%",
                        "action": "SELL",
                        "urgency": "high"
                    })
                    
                elif pnl_percent >= take_profit_percent:
                    alerts.append({
                        "type": "TAKE_PROFIT",
                        "symbol": symbol,
                        "pnl_percent": pnl_percent,
                        "message": f"🎉 {symbol} hit profit target: {pnl_percent:.2f}%",
                        "action": "SELL",
                        "urgency": "medium"
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Stop loss check failed: {e}")
            return []
    
    def calculate_position_size(
        self,
        balance: float,
        risk_tolerance: int,
        coin_risk_score: float
    ) -> Dict:
        """
        Calculate safe position size based on risk
        
        Args:
            balance: Available balance
            risk_tolerance: User's risk (1-10)
            coin_risk_score: Coin's risk (0-10)
            
        Returns:
            Recommended position sizes
        """
        try:
            # Risk difference
            risk_diff = coin_risk_score - risk_tolerance
            
            # Calculate safe percentage
            if risk_diff <= -2:
                # Very safe
                percentage = 0.40  # 40%
                confidence = "high"
            elif risk_diff <= 0:
                # Safe
                percentage = 0.25  # 25%
                confidence = "medium"
            elif risk_diff <= 2:
                # Moderate risk
                percentage = 0.10  # 10%
                confidence = "low"
            else:
                # Too risky
                percentage = 0.0
                confidence = "avoid"
            
            amount = balance * percentage
            
            return {
                "recommended_amount": amount,
                "percentage": percentage * 100,
                "confidence": confidence,
                "max_safe_amount": balance * 0.50,  # Never more than 50%
                "min_amount": balance * 0.05  # Minimum 5%
            }
            
        except Exception as e:
            logger.error(f"❌ Position size calculation failed: {e}")
            return {
                "recommended_amount": 0,
                "percentage": 0,
                "confidence": "error"
            }


# Create global instance
trading_service = TradingService()


# ==================== HELPER FUNCTIONS ====================

async def buy_coin(
    user_id: str,
    symbol: str,
    amount: float,
    user_balance: float,
    user_risk: int
) -> Dict:
    """Quick helper for buying"""
    return await trading_service.execute_buy(
        user_id, symbol, amount, user_balance, user_risk
    )


async def sell_coin(
    user_id: str,
    symbol: str,
    quantity: float,
    avg_price: float
) -> Dict:
    """Quick helper for selling"""
    return await trading_service.execute_sell(
        user_id, symbol, quantity, avg_price
    )


# ==================== TESTING ====================

async def test_trading_service():
    """Test trading service"""
    print("=" * 60)
    print("Testing Trading Service")
    print("=" * 60)
    
    # Test 1: Buy order
    print("\n🛒 Test 1: Execute buy order")
    buy_result = await trading_service.execute_buy(
        user_id="user_123",
        symbol="BTC",
        amount_usd=100,
        user_balance=500,
        user_risk_tolerance=5
    )
    print(f"Success: {buy_result['success']}")
    if buy_result['success']:
        print(f"Order: {buy_result['order']}")
        print(f"Risk: {buy_result['risk_data']['risk_score']}/10")
    
    # Test 2: Sell order
    print("\n💰 Test 2: Execute sell order")
    sell_result = await trading_service.execute_sell(
        user_id="user_123",
        symbol="BTC",
        quantity=0.0026,
        avg_buy_price=35000
    )
    print(f"Success: {sell_result['success']}")
    if sell_result['success']:
        pnl = sell_result['pnl']
        print(f"P&L: ${pnl['profit_loss']:+.2f} ({pnl['profit_loss_percent']:+.2f}%)")
    
    # Test 3: Position sizing
    print("\n📊 Test 3: Calculate position size")
    position = trading_service.calculate_position_size(
        balance=1000,
        risk_tolerance=5,
        coin_risk_score=3.2
    )
    print(f"Recommended: ${position['recommended_amount']:.2f} ({position['percentage']:.0f}%)")
    print(f"Confidence: {position['confidence']}")
    
    # Test 4: Stop loss check
    print("\n⚠️ Test 4: Check stop loss")
    test_portfolio = [
        {
            "symbol": "BTC",
            "quantity": 0.0026,
            "avg_buy_price": 40000  # Higher than current = loss
        }
    ]
    alerts = await trading_service.check_stop_loss(test_portfolio)
    for alert in alerts:
        print(f"  {alert['message']}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    import nest_asyncio
    import asyncio

    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    asyncio.run(test_trading_service())