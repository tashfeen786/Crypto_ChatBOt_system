"""
Price Alerts API Routes - PostgreSQL Version
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os

logger = logging.getLogger(__name__)
router = APIRouter()

def get_db():
    """Get PostgreSQL database connection"""
    try:
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:0000@localhost:5432/crypto_rag")
        conn = psycopg2.connect(database_url)
        logger.info("✅ Database connected successfully")
        return conn
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        return None

class AlertCreate(BaseModel):
    """Create new alert"""
    user_id: str = Field(..., description="User ID")
    symbol: str = Field(..., description="Coin symbol (BTC, ETH, etc.)")
    target_price: float = Field(..., gt=0, description="Target price")
    condition: str = Field(..., description="'above' or 'below'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "3",
                "symbol": "BTC",
                "target_price": 45000,
                "condition": "above"
            }
        }

@router.post("/")
async def create_alert(alert: AlertCreate):
    """Create new price alert"""
    conn = None
    try:
        logger.info(f"🔔 Creating alert: {alert.symbol} {alert.condition} ${alert.target_price} for user {alert.user_id}")
        
        if alert.condition not in ['above', 'below']:
            raise HTTPException(status_code=400, detail="Condition must be 'above' or 'below'")
        
        conn = get_db()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            INSERT INTO price_alerts 
            (user_id, symbol, target_price, condition, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (str(alert.user_id), alert.symbol.upper(), float(alert.target_price), 
              alert.condition, True, datetime.now()))
        
        result = cursor.fetchone()
        alert_id = result['id']
        conn.commit()
        
        logger.info(f"✅ Alert created with ID: {alert_id}")
        
        return {
            "success": True,
            "alert_id": alert_id,
            "message": f"Alert set for {alert.symbol} when price goes {alert.condition} ${alert.target_price}",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Create alert error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.get("/{user_id}")
async def get_user_alerts(user_id: str, include_triggered: bool = False):
    """Get all alerts for a user"""
    conn = None
    try:
        logger.info(f"📋 Getting alerts for user: {user_id}")
        
        conn = get_db()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if include_triggered:
            cursor.execute("""
                SELECT id, user_id, symbol, target_price, condition, is_active, created_at, triggered_at
                FROM price_alerts 
                WHERE user_id = %s AND is_active = true
                ORDER BY created_at DESC
            """, (str(user_id),))
        else:
            cursor.execute("""
                SELECT id, user_id, symbol, target_price, condition, is_active, created_at, triggered_at
                FROM price_alerts 
                WHERE user_id = %s AND is_active = true AND triggered_at IS NULL
                ORDER BY created_at DESC
            """, (str(user_id),))
        
        alerts = []
        rows = cursor.fetchall()
        
        for row in rows:
            alert = dict(row)
            if alert.get('target_price'):
                alert['target_price'] = float(alert['target_price'])
            if alert.get('created_at'):
                alert['created_at'] = alert['created_at'].isoformat()
            if alert.get('triggered_at'):
                alert['triggered_at'] = alert['triggered_at'].isoformat()
            alerts.append(alert)
        
        logger.info(f"✅ Found {len(alerts)} alerts for user {user_id}")
        
        return {
            "success": True,
            "user_id": user_id,
            "alerts": alerts,
            "count": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get alerts error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.delete("/{alert_id}")
async def delete_alert(alert_id: int):
    """Delete an alert"""
    conn = None
    try:
        logger.info(f"🗑️  Deleting alert: {alert_id}")
        
        conn = get_db()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        cursor.execute("UPDATE price_alerts SET is_active = false WHERE id = %s", (alert_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        conn.commit()
        logger.info(f"✅ Alert deleted: {alert_id}")
        
        return {
            "success": True,
            "alert_id": alert_id,
            "message": "Alert deleted successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete alert error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete alert: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.post("/{alert_id}/toggle")
async def toggle_alert(alert_id: int):
    """Toggle alert active status on/off"""
    conn = None
    try:
        logger.info(f"🔄 Toggling alert: {alert_id}")
        
        conn = get_db()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT is_active FROM price_alerts WHERE id = %s", (alert_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        new_state = not result['is_active']
        cursor.execute("UPDATE price_alerts SET is_active = %s WHERE id = %s", (new_state, alert_id))
        conn.commit()
        
        logger.info(f"✅ Alert toggled: {alert_id} -> {new_state}")
        
        return {
            "success": True,
            "alert_id": alert_id,
            "is_active": new_state,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Toggle alert error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to toggle alert: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.get("/health")
async def alerts_health():
    """Health check for alerts service"""
    conn = None
    try:
        conn = get_db()
        if not conn:
            return {
                "status": "unhealthy", 
                "message": "Database connection failed",
                "timestamp": datetime.now().isoformat()
            }
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT COUNT(*) as count FROM price_alerts WHERE is_active = true")
        result = cursor.fetchone()
        
        return {
            "status": "healthy",
            "service": "alerts",
            "database": "connected",
            "active_alerts": result['count'],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    finally:
        if conn:
            conn.close()