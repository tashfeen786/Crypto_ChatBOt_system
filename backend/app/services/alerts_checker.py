"""
Alerts Checker Service - PostgreSQL Version
Background task to check price alerts
"""
import asyncio
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

# Create PostgreSQL engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class AlertsChecker:
    def __init__(self):
        self.is_running = False
        self.check_interval = 30  # seconds
        
    async def start(self):
        """Start the alerts checker"""
        logger.info("🔔 Starting Alerts Checker...")
        self.is_running = True
        logger.info("🚀 Alerts Checker started!")
        logger.info(f"⏱️  Check interval: {self.check_interval} seconds")
        
        while self.is_running:
            try:
                await self.check_alerts()
            except Exception as e:
                logger.error(f"❌ Process alerts error: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    async def check_alerts(self):
        """Check all active alerts"""
        db = SessionLocal()
        
        try:
            # Get active alerts
            alerts = db.execute(
                text("""
                    SELECT id, user_id, symbol, condition, target_price
                    FROM price_alerts
                    WHERE is_active = TRUE AND triggered_at IS NULL
                """)
            ).fetchall()
            
            if not alerts:
                logger.debug("No active alerts to check")
                return
            
            logger.info(f"🔍 Checking {len(alerts)} alerts...")
            
            for alert in alerts:
                alert_id, user_id, symbol, condition, target_price = alert
                
                # Get current price (you'll need to implement this)
                current_price = await self.get_current_price(symbol)
                
                if current_price is None:
                    continue
                
                # Check condition
                triggered = False
                if condition == "above" and current_price > target_price:
                    triggered = True
                elif condition == "below" and current_price < target_price:
                    triggered = True
                
                if triggered:
                    logger.info(f"🔔 Alert triggered! {symbol} {condition} ${target_price}")
                    
                    # Mark as triggered
                    db.execute(
                        text("""
                            UPDATE price_alerts
                            SET triggered_at = CURRENT_TIMESTAMP
                            WHERE id = :alert_id
                        """),
                        {"alert_id": alert_id}
                    )
                    db.commit()
                    
                    # Here you could send notification (email, push, etc.)
                    logger.info(f"✅ Alert {alert_id} marked as triggered")
            
        except Exception as e:
            logger.error(f"❌ Check alerts error: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def get_current_price(self, symbol: str) -> float:
        """Get current price for symbol"""
        try:
            # Import here to avoid circular dependency
            from app.services.market_data import get_coin_price
            price_data = await get_coin_price(symbol)
            return price_data.get('price')
        except Exception as e:
            logger.error(f"❌ Get price error for {symbol}: {e}")
            return None
    
    def stop(self):
        """Stop the alerts checker"""
        logger.info("🛑 Stopping Alerts Checker...")
        self.is_running = False

# Global instance
alerts_checker = AlertsChecker()

async def start_alerts_checker():
    """Start the alerts checker background task"""
    logger.info("🔔 Alerts Checker initialized")
    await alerts_checker.start()