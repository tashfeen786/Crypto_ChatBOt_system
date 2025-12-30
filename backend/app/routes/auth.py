# app/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import sqlite3
import hashlib
import secrets
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Security Configuration
SECRET_KEY = "your-secret-key-change-in-production-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Database helper
def get_db():
    conn = sqlite3.connect('crypto_advisor.db')
    conn.row_factory = sqlite3.Row
    return conn

# ==================== PASSWORD HELPERS (SHA256 + Salt) ====================

def hash_password(password: str) -> str:
    """Hash password using SHA256 with salt"""
    salt = secrets.token_hex(32)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(plain_password: str, stored_password: str) -> bool:
    """Verify password against stored hash"""
    try:
        salt, stored_hash = stored_password.split('$')
        pwd_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
        return pwd_hash == stored_hash
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

# ==================== TOKEN HELPERS ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access"):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ==================== MODELS ====================

class SignupRequest(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    password: str
    balance: float = 1000.0
    risk_tolerance: int = 5

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# ==================== ENDPOINTS ====================

@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest):
    """Register a new user"""
    logger.info(f"📥 Signup request for email: {request.email}")
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Validate password
        if len(request.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        if len(request.password) > 128:
            raise HTTPException(status_code=400, detail="Password too long")
        
        # Check if email exists
        cursor.execute("SELECT user_id FROM users WHERE email = ?", (request.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        logger.info("🔐 Hashing password...")
        hashed_password = hash_password(request.password)
        logger.info("✅ Password hashed")
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (user_id, name, email, password_hash, balance, risk_tolerance)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            request.user_id,
            request.name,
            request.email,
            hashed_password,
            request.balance,
            request.risk_tolerance
        ))
        
        conn.commit()
        logger.info("✅ User created")
        
        # Create tokens
        access_token = create_access_token(data={"sub": request.user_id, "email": request.email})
        refresh_token = create_refresh_token(data={"sub": request.user_id})
        
        user_data = {
            "user_id": request.user_id,
            "name": request.name,
            "email": request.email,
            "balance": request.balance,
            "risk_tolerance": request.risk_tolerance
        }
        
        logger.info(f"✅ Signup successful for {request.email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Signup error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")
    finally:
        conn.close()

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login user"""
    logger.info(f"📥 Login request for: {request.email}")
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Get user
        cursor.execute("""
            SELECT user_id, name, email, password_hash, balance, risk_tolerance
            FROM users WHERE email = ?
        """, (request.email,))
        
        user = cursor.fetchone()
        
        if not user:
            logger.warning(f"❌ User not found: {request.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        logger.info("🔐 Verifying password...")
        if not verify_password(request.password, user['password_hash']):
            logger.warning(f"❌ Invalid password for: {request.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        logger.info("✅ Password verified")
        
        # Create tokens
        access_token = create_access_token(data={"sub": user['user_id'], "email": user['email']})
        refresh_token = create_refresh_token(data={"sub": user['user_id']})
        
        user_data = {
            "user_id": user['user_id'],
            "name": user['name'],
            "email": user['email'],
            "balance": user['balance'],
            "risk_tolerance": user['risk_tolerance']
        }
        
        logger.info(f"✅ Login successful for {request.email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
    finally:
        conn.close()

@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token"""
    try:
        payload = verify_token(request.refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        access_token = create_access_token(data={"sub": user_id, "email": user['email']})
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Logout user"""
    try:
        verify_token(token)
        return {"message": "Logged out successfully"}
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user info"""
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, name, email, balance, risk_tolerance, created_at
            FROM users WHERE user_id = ?
        """, (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user_id": user['user_id'],
            "name": user['name'],
            "email": user['email'],
            "balance": user['balance'],
            "risk_tolerance": user['risk_tolerance'],
            "created_at": user['created_at']
        }
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=401, detail="Invalid token")