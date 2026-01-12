"""
Coin data model
SQLAlchemy ORM model for coin_data table
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from sqlalchemy.sql import func
from datetime import datetime

from app.database.base import Base


class CoinData(Base):
    """
    Coin data model for caching market data
    """
    __tablename__ = "coin_data"
    
    # Primary Key
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    # Coin Information
    symbol = Column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
        comment="Coin symbol (BTC, ETH, etc.)"
    )
    
    name = Column(
        String(100),
        nullable=False,
        comment="Full coin name (Bitcoin, Ethereum, etc.)"
    )
    
    # Price Information
    price = Column(
        Float,
        nullable=False,
        comment="Current price in USD"
    )
    
    price_change_24h = Column(
        Float,
        nullable=True,
        comment="Price change in last 24 hours (%)"
    )
    
    price_change_7d = Column(
        Float,
        nullable=True,
        comment="Price change in last 7 days (%)"
    )
    
    price_change_30d = Column(
        Float,
        nullable=True,
        comment="Price change in last 30 days (%)"
    )
    
    # Volume & Market Cap
    volume_24h = Column(
        Float,
        nullable=True,
        comment="24h trading volume in USD"
    )
    
    market_cap = Column(
        Float,
        nullable=True,
        comment="Market capitalization in USD"
    )
    
    market_cap_rank = Column(
        Integer,
        nullable=True,
        comment="Market cap ranking"
    )
    
    # Price Range
    high_24h = Column(
        Float,
        nullable=True,
        comment="Highest price in 24h"
    )
    
    low_24h = Column(
        Float,
        nullable=True,
        comment="Lowest price in 24h"
    )
    
    ath = Column(
        Float,
        nullable=True,
        comment="All-time high price"
    )
    
    ath_change_percentage = Column(
        Float,
        nullable=True,
        comment="Distance from ATH (%)"
    )
    
    atl = Column(
        Float,
        nullable=True,
        comment="All-time low price"
    )
    
    # Supply Information
    circulating_supply = Column(
        Float,
        nullable=True,
        comment="Circulating supply"
    )
    
    total_supply = Column(
        Float,
        nullable=True,
        comment="Total supply"
    )
    
    max_supply = Column(
        Float,
        nullable=True,
        comment="Maximum supply"
    )
    
    # Risk Metrics (Calculated)
    risk_score = Column(
        Float,
        nullable=False,
        default=5.0,
        comment="Overall risk score (0-10)"
    )
    
    risk_level = Column(
        String(20),
        nullable=False,
        default="medium",
        comment="Risk level: low, medium, high"
    )
    
    volatility_score = Column(
        Float,
        nullable=True,
        comment="Volatility score (0-10)"
    )
    
    liquidity_score = Column(
        Float,
        nullable=True,
        comment="Liquidity score (0-10)"
    )
    
    trend_score = Column(
        Float,
        nullable=True,
        comment="Trend score (0-10)"
    )
    
    # Sentiment
    sentiment = Column(
        String(20),
        nullable=True,
        comment="Market sentiment: bullish, bearish, neutral"
    )
    
    sentiment_score = Column(
        Float,
        nullable=True,
        comment="Sentiment score (0-100)"
    )
    
    # Additional Data (JSON)
    meta = Column(
    "metadata",  # DB column name rahega 'metadata'
    JSON,
    nullable=True,
    comment="Additional metadata as JSON"
)
    
    # Timestamps
    last_updated = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    def __repr__(self):
        return f"<CoinData(symbol={self.symbol}, price=${self.price}, risk={self.risk_score})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "name": self.name,
            "price": self.price,
            "price_change_24h": self.price_change_24h,
            "price_change_7d": self.price_change_7d,
            "price_change_30d": self.price_change_30d,
            "volume_24h": self.volume_24h,
            "market_cap": self.market_cap,
            "market_cap_rank": self.market_cap_rank,
            "high_24h": self.high_24h,
            "low_24h": self.low_24h,
            "ath": self.ath,
            "ath_change_percentage": self.ath_change_percentage,
            "atl": self.atl,
            "circulating_supply": self.circulating_supply,
            "total_supply": self.total_supply,
            "max_supply": self.max_supply,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "volatility_score": self.volatility_score,
            "liquidity_score": self.liquidity_score,
            "trend_score": self.trend_score,
            "sentiment": self.sentiment,
            "sentiment_score": self.sentiment_score,
            "metadata": self.meta,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def get_risk_category(self) -> dict:
        """
        Get detailed risk category
        """
        if self.risk_score <= 3:
            category = "low"
            description = "Low risk - Suitable for conservative investors"
            color = "green"
        elif self.risk_score <= 6:
            category = "medium"
            description = "Medium risk - Suitable for moderate investors"
            color = "orange"
        else:
            category = "high"
            description = "High risk - Only for aggressive investors"
            color = "red"
        
        return {
            "category": category,
            "score": self.risk_score,
            "description": description,
            "color": color
        }
    
    def get_trend_direction(self) -> str:
        """
        Get trend direction based on price changes
        """
        if not self.price_change_24h:
            return "neutral"
        
        if self.price_change_24h > 5:
            return "strong_bullish"
        elif self.price_change_24h > 0:
            return "bullish"
        elif self.price_change_24h > -5:
            return "bearish"
        else:
            return "strong_bearish"
    
    def is_near_ath(self, threshold: float = 10.0) -> bool:
        """
        Check if coin is near all-time high
        
        Args:
            threshold: Percentage threshold (default 10%)
        """
        if not self.ath_change_percentage:
            return False
        return abs(self.ath_change_percentage) <= threshold
    
    def calculate_volatility_level(self) -> str:
        """
        Calculate volatility level
        """
        if not self.volatility_score:
            return "unknown"
        
        if self.volatility_score <= 3:
            return "very_stable"
        elif self.volatility_score <= 5:
            return "stable"
        elif self.volatility_score <= 7:
            return "moderate"
        else:
            return "highly_volatile"
    
    def get_investment_recommendation(self, user_risk_tolerance: int) -> dict:
        """
        Get investment recommendation for a user
        
        Args:
            user_risk_tolerance: User's risk tolerance (1-10)
        """
        risk_diff = self.risk_score - user_risk_tolerance
        
        if risk_diff <= -2:
            return {
                "action": "strong_buy",
                "confidence": "high",
                "allocation": "40-50%",
                "message": f"{self.symbol} is well below your risk tolerance. Strong buy candidate."
            }
        elif risk_diff <= 0:
            return {
                "action": "buy",
                "confidence": "medium",
                "allocation": "20-30%",
                "message": f"{self.symbol} matches your risk profile. Good investment option."
            }
        elif risk_diff <= 2:
            return {
                "action": "cautious_buy",
                "confidence": "low",
                "allocation": "5-10%",
                "message": f"{self.symbol} is slightly riskier. Consider small allocation."
            }
        else:
            return {
                "action": "avoid",
                "confidence": "high",
                "allocation": "0%",
                "message": f"{self.symbol} exceeds your risk tolerance. Consider safer alternatives."
            }
    
    def to_ticker_format(self) -> dict:
        """
        Format for price ticker display
        """
        return {
            "symbol": self.symbol,
            "price": self.price,
            "change_24h": self.price_change_24h,
            "trend": "positive" if self.price_change_24h and self.price_change_24h > 0 else "negative"
        }