"""
User Routes - Complete with Database Integration
Handles user registration, profile management, and persistence
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Database connection
def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(
            os.getenv("DATABASE_URL"),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None


# Pydantic Models
class UserCreate(BaseModel):
    user_id: str
    name: str = "User"
    email: Optional[EmailStr] = None
    balance: float = 1000.0
    risk_tolerance: int = 5
    experience_level: str = "Beginner"
    investment_goal: str = "Long-term Growth"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    balance: Optional[float] = None
    risk_tolerance: Optional[int] = None
    experience_level: Optional[str] = None
    investment_goal: Optional[str] = None


class UserResponse(BaseModel):
    user_id: str
    name: str
    email: Optional[str]
    balance: float
    risk_tolerance: int
    experience_level: str
    investment_goal: str
    created_at: datetime
    updated_at: datetime


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """Register new user"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute(
            "SELECT user_id FROM users WHERE user_id = %s OR email = %s",
            (user.user_id, user.email)
        )
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Insert new user
        cursor.execute("""
            INSERT INTO users (user_id, name, email, balance, risk_tolerance, experience_level, investment_goal)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            user.user_id,
            user.name,
            user.email,
            user.balance,
            user.risk_tolerance,
            user.experience_level,
            user.investment_goal
        ))
        
        new_user = cursor.fetchone()
        
        # Create portfolio for user
        cursor.execute("""
            INSERT INTO portfolios (user_id, total_value, invested_amount)
            VALUES (%s, 0, 0)
        """, (user.user_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ User registered: {user.user_id}")
        return UserResponse(**new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: str):
    """Get user profile"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"✅ Retrieved profile: {user_id}")
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_profile(user_id: str, updates: UserUpdate):
    """Update user profile"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        if updates.name is not None:
            update_fields.append("name = %s")
            values.append(updates.name)
        if updates.email is not None:
            update_fields.append("email = %s")
            values.append(updates.email)
        if updates.balance is not None:
            update_fields.append("balance = %s")
            values.append(updates.balance)
        if updates.risk_tolerance is not None:
            update_fields.append("risk_tolerance = %s")
            values.append(updates.risk_tolerance)
        if updates.experience_level is not None:
            update_fields.append("experience_level = %s")
            values.append(updates.experience_level)
        if updates.investment_goal is not None:
            update_fields.append("investment_goal = %s")
            values.append(updates.investment_goal)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(user_id)
        query = f"""
            UPDATE users 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING *
        """
        
        cursor.execute(query, values)
        updated_user = cursor.fetchone()
        
        if not updated_user:
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Profile updated: {user_id}")
        return UserResponse(**updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Update profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/balance")
async def get_user_balance(user_id: str):
    """Get user balance"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"user_id": user_id, "balance": float(result['balance'])}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get balance error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/balance")
async def update_user_balance(user_id: str, amount: float, operation: str = "set"):
    """
    Update user balance
    operation: 'set', 'add', or 'subtract'
    """
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        
        if operation == "set":
            cursor.execute(
                "UPDATE users SET balance = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s RETURNING balance",
                (amount, user_id)
            )
        elif operation == "add":
            cursor.execute(
                "UPDATE users SET balance = balance + %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s RETURNING balance",
                (amount, user_id)
            )
        elif operation == "subtract":
            cursor.execute(
                "UPDATE users SET balance = balance - %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s RETURNING balance",
                (amount, user_id)
            )
        else:
            conn.close()
            raise HTTPException(status_code=400, detail="Invalid operation")
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Balance updated: {user_id} - {operation} {amount}")
        return {"user_id": user_id, "balance": float(result['balance'])}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Update balance error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """Delete user account"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = %s RETURNING user_id", (user_id,))
        deleted = cursor.fetchone()
        
        if not deleted:
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ User deleted: {user_id}")
        return {"message": "User deleted successfully", "user_id": user_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_users(limit: int = 10, offset: int = 0):
    """List all users (admin feature)"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (limit, offset)
        )
        users = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total = cursor.fetchone()['count']
        
        conn.close()
        
        return {
            "users": [UserResponse(**user) for user in users],
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"❌ List users error: {e}")
        raise HTTPException(status_code=500, detail=str(e))