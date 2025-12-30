"""
User database model
SQLAlchemy ORM model for users table
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.database.base import Base


class User(Base):
    """
    User model for storing user information and preferences
    """
    __tablename__ = "users"
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    
    # User Information
    email = Column(
        String(255), 
        unique=True, 
        index=True, 
        nullable=False
    )
    
    name = Column(
        String(255), 
        nullable=False
    )
    
    # Investment Profile
    risk_tolerance = Column(
        Integer,
        nullable=False,
        default=5,
        comment="Risk tolerance level (1-10): 1=Very Conservative, 10=Very Aggressive"
    )
    
    investment_amount = Column(
        Float,
        nullable=True,
        comment="Total investment amount in USD"
    )
    
    experience_level = Column(
        String(50),
        nullable=False,
        default="beginner",
        comment="Investment experience: beginner, intermediate, advanced"
    )
    
    # Preferences
    preferred_coins = Column(
        String,
        nullable=True,
        comment="Comma-separated list of preferred coin symbols"
    )
    
    notification_enabled = Column(
        Boolean,
        default=True,
        comment="Enable/disable notifications"
    )
    
    # Account Status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )
    
    is_verified = Column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    last_login = Column(
        DateTime(timezone=True),
        nullable=True
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, risk={self.risk_tolerance})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "risk_tolerance": self.risk_tolerance,
            "investment_amount": self.investment_amount,
            "experience_level": self.experience_level,
            "preferred_coins": self.preferred_coins.split(",") if self.preferred_coins else [],
            "notification_enabled": self.notification_enabled,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
    
    def get_risk_category(self) -> str:
        """Get risk category based on risk_tolerance"""
        if self.risk_tolerance <= 3:
            return "conservative"
        elif self.risk_tolerance <= 6:
            return "moderate"
        else:
            return "aggressive"
    
    def can_invest_in_coin(self, coin_risk_score: float) -> dict:
        """
        Check if user can invest in a coin based on risk tolerance
        
        Args:
            coin_risk_score: Risk score of coin (0-10)
            
        Returns:
            dict with recommendation
        """
        user_risk = self.risk_tolerance
        risk_diff = coin_risk_score - user_risk
        
        if risk_diff <= -1:
            return {
                "can_invest": True,
                "recommendation": "safe_investment",
                "message": "This coin is well within your risk tolerance. Safe to invest."
            }
        elif risk_diff <= 1:
            return {
                "can_invest": True,
                "recommendation": "moderate_investment",
                "message": "This coin matches your risk profile. Consider investing."
            }
        else:
            return {
                "can_invest": False,
                "recommendation": "avoid_investment",
                "message": f"This coin's risk ({coin_risk_score}) exceeds your tolerance ({user_risk}). Consider safer options."
            }


class Conversation(Base):
    """
    Conversation model for storing chat history
    """
    __tablename__ = "conversations"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    user_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Foreign key to users table"
    )
    
    # Message content
    message = Column(
        String,
        nullable=False,
        comment="User's message"
    )
    
    response = Column(
        String,
        nullable=False,
        comment="Bot's response"
    )
    
    # Metadata
    coins_mentioned = Column(
        String,
        nullable=True,
        comment="Comma-separated list of coins mentioned"
    )
    
    risk_scores = Column(
        String,
        nullable=True,
        comment="JSON string of risk scores"
    )
    
    sentiment = Column(
        String(20),
        nullable=True,
        comment="Message sentiment: positive, negative, neutral"
    )
    
    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "message": self.message,
            "response": self.response,
            "coins_mentioned": self.coins_mentioned.split(",") if self.coins_mentioned else [],
            "risk_scores": self.risk_scores,
            "sentiment": self.sentiment,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class UserPortfolio(Base):
    """
    User portfolio model for tracking investments
    """
    __tablename__ = "user_portfolio"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    user_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )
    
    coin_symbol = Column(
        String(20),
        nullable=False,
        index=True
    )
    
    quantity = Column(
        Float,
        nullable=False,
        default=0.0
    )
    
    avg_buy_price = Column(
        Float,
        nullable=False
    )
    
    current_value = Column(
        Float,
        nullable=True,
        comment="Current portfolio value (auto-calculated)"
    )
    
    profit_loss = Column(
        Float,
        nullable=True,
        comment="Profit/Loss amount"
    )
    
    profit_loss_percentage = Column(
        Float,
        nullable=True,
        comment="Profit/Loss percentage"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    def __repr__(self):
        return f"<Portfolio(user={self.user_id}, coin={self.coin_symbol}, qty={self.quantity})>"
    
    def calculate_pnl(self, current_price: float):
        """Calculate profit/loss"""
        investment = self.quantity * self.avg_buy_price
        self.current_value = self.quantity * current_price
        self.profit_loss = self.current_value - investment
        self.profit_loss_percentage = (self.profit_loss / investment) * 100 if investment > 0 else 0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "coin_symbol": self.coin_symbol,
            "quantity": self.quantity,
            "avg_buy_price": self.avg_buy_price,
            "current_value": self.current_value,
            "profit_loss": self.profit_loss,
            "profit_loss_percentage": self.profit_loss_percentage,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }