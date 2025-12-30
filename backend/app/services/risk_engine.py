"""
Risk Calculation Engine
Calculate risk scores (0-10) for cryptocurrencies
Based on: Volatility, Liquidity, Trend, Market Cap
"""

import numpy as np
from typing import Dict, List, Optional
import logging
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)


class RiskEngine:
    """
    Calculate risk scores for cryptocurrencies
    Score: 0-10 (0 = safest, 10 = riskiest)
    """
    
    def __init__(self):
        # Risk calculation weights from config
        self.weights = settings.RISK_WEIGHTS
        self.low_threshold = settings.RISK_LOW_THRESHOLD
        self.medium_threshold = settings.RISK_MEDIUM_THRESHOLD
        
        logger.info("🎯 Risk Engine initialized")
        logger.info(f"   Weights: {self.weights}")
    
    def calculate_risk_score(self, coin_data: Dict) -> Dict:
        """
        Main function: Calculate overall risk score
        
        Args:
            coin_data: Dictionary with coin information
                Required keys: symbol, price, change_24h, volume_24h
                Optional: historical_prices, market_cap
        
        Returns:
            Dictionary with detailed risk analysis
            
        Example:
            >>> coin_data = {
            ...     'symbol': 'BTC',
            ...     'price': 37890,
            ...     'change_24h': 2.5,
            ...     'volume_24h': 28000000000,
            ...     'market_cap': 740000000000
            ... }
            >>> risk = engine.calculate_risk_score(coin_data)
            >>> print(risk)
            {
                'risk_score': 3.2,
                'risk_level': 'low',
                'factors': {...},
                'recommendation': 'safe_investment'
            }
        """
        try:
            symbol = coin_data.get('symbol', 'UNKNOWN')
            logger.info(f"📊 Calculating risk for {symbol}...")
            
            # Calculate individual risk factors
            volatility_score = self._calculate_volatility(coin_data)
            liquidity_score = self._calculate_liquidity(coin_data)
            trend_score = self._calculate_trend(coin_data)
            market_cap_score = self._calculate_market_cap_risk(coin_data)
            
            # Calculate weighted risk score
            risk_score = (
                volatility_score * self.weights['volatility'] +
                liquidity_score * self.weights['liquidity'] +
                trend_score * self.weights['trend'] +
                market_cap_score * self.weights['market_cap']
            )
            
            # Determine risk level
            risk_level = self._get_risk_level(risk_score)
            
            # Generate recommendation
            recommendation = self._get_recommendation(risk_score)
            
            result = {
                'symbol': symbol,
                'risk_score': round(risk_score, 2),
                'risk_level': risk_level,
                'factors': {
                    'volatility': round(volatility_score, 2),
                    'liquidity': round(liquidity_score, 2),
                    'trend': round(trend_score, 2),
                    'market_cap': round(market_cap_score, 2)
                },
                'recommendation': recommendation,
                'analysis': self._generate_analysis(risk_score, risk_level, coin_data),
                'calculated_at': datetime.now().isoformat()
            }
            
            logger.info(f"✅ {symbol} Risk Score: {risk_score:.2f} ({risk_level})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error calculating risk: {e}")
            return self._get_default_risk(coin_data.get('symbol', 'UNKNOWN'))
    
    def _calculate_volatility(self, coin_data: Dict) -> float:
        """
        Calculate volatility score (0-10)
        Higher volatility = Higher risk
        
        Based on:
        - 24h price change
        - Historical price swings (if available)
        - Price range (high-low)
        """
        try:
            # Method 1: Use 24h change percentage
            change_24h = abs(coin_data.get('change_24h', 0))
            
            # Method 2: Use price range if available
            high_24h = coin_data.get('high_24h', 0)
            low_24h = coin_data.get('low_24h', 0)
            price = coin_data.get('price', 0)
            
            if high_24h and low_24h and price > 0:
                # Calculate price range percentage
                price_range = ((high_24h - low_24h) / price) * 100
                volatility_from_range = self._map_to_score(
                    price_range,
                    ranges=[(0, 2), (2, 5), (5, 10), (10, 15), (15, 100)],
                    scores=[1, 3, 5, 7, 10]
                )
            else:
                volatility_from_range = 5  # Default
            
            # Method 3: Use historical data if available
            historical_prices = coin_data.get('historical_prices', [])
            if historical_prices and len(historical_prices) > 1:
                returns = np.diff(historical_prices) / historical_prices[:-1]
                std_dev = np.std(returns) * 100
                volatility_from_history = self._map_to_score(
                    std_dev,
                    ranges=[(0, 2), (2, 5), (5, 10), (10, 20), (20, 100)],
                    scores=[1, 3, 5, 8, 10]
                )
            else:
                volatility_from_history = None
            
            # Map 24h change to score
            volatility_from_change = self._map_to_score(
                change_24h,
                ranges=[(0, 2), (2, 5), (5, 10), (10, 15), (15, 100)],
                scores=[2, 4, 6, 8, 10]
            )
            
            # Average available methods
            scores = [volatility_from_change, volatility_from_range]
            if volatility_from_history is not None:
                scores.append(volatility_from_history)
            
            volatility_score = np.mean(scores)
            
            return float(volatility_score)
            
        except Exception as e:
            logger.error(f"❌ Error calculating volatility: {e}")
            return 5.0  # Default medium risk
    
    def _calculate_liquidity(self, coin_data: Dict) -> float:
        """
        Calculate liquidity score (0-10)
        Lower liquidity = Higher risk
        
        Based on:
        - 24h trading volume
        - Market cap (if available)
        """
        try:
            volume_24h = coin_data.get('volume_24h', 0)
            
            # Map volume to risk score (inverse: high volume = low risk)
            if volume_24h > 10_000_000_000:  # >10B
                return 1.0  # Very liquid, very low risk
            elif volume_24h > 5_000_000_000:  # >5B
                return 2.0
            elif volume_24h > 1_000_000_000:  # >1B
                return 3.0
            elif volume_24h > 500_000_000:   # >500M
                return 4.0
            elif volume_24h > 100_000_000:   # >100M
                return 5.0
            elif volume_24h > 50_000_000:    # >50M
                return 6.5
            elif volume_24h > 10_000_000:    # >10M
                return 8.0
            else:
                return 9.5  # Very low liquidity, very high risk
            
        except Exception as e:
            logger.error(f"❌ Error calculating liquidity: {e}")
            return 7.0  # Default high risk for unknown
    
    def _calculate_trend(self, coin_data: Dict) -> float:
        """
        Calculate trend score (0-10)
        Strong downtrend = Higher risk
        
        Based on:
        - 24h change
        - 7d change (if available)
        """
        try:
            change_24h = coin_data.get('change_24h', 0)
            change_7d = coin_data.get('change_7d', None)
            
            # Calculate from 24h change
            if change_24h > 10:
                trend_24h = 2  # Strong uptrend (low risk)
            elif change_24h > 5:
                trend_24h = 3  # Uptrend
            elif change_24h > 0:
                trend_24h = 4  # Slight uptrend
            elif change_24h > -5:
                trend_24h = 6  # Slight downtrend
            elif change_24h > -10:
                trend_24h = 7  # Downtrend
            else:
                trend_24h = 9  # Strong downtrend (high risk)
            
            # Calculate from 7d change if available
            if change_7d is not None:
                if change_7d > 15:
                    trend_7d = 2
                elif change_7d > 5:
                    trend_7d = 4
                elif change_7d > -5:
                    trend_7d = 5
                elif change_7d > -15:
                    trend_7d = 7
                else:
                    trend_7d = 9
                
                # Average both trends
                trend_score = (trend_24h + trend_7d) / 2
            else:
                trend_score = trend_24h
            
            return float(trend_score)
            
        except Exception as e:
            logger.error(f"❌ Error calculating trend: {e}")
            return 5.0
    
    def _calculate_market_cap_risk(self, coin_data: Dict) -> float:
        """
        Calculate market cap risk (0-10)
        Lower market cap = Higher risk
        """
        try:
            market_cap = coin_data.get('market_cap', 0)
            market_cap_rank = coin_data.get('market_cap_rank', None)
            
            # Method 1: Use rank if available
            if market_cap_rank:
                if market_cap_rank <= 10:
                    return 1.0  # Top 10, very safe
                elif market_cap_rank <= 50:
                    return 3.0  # Top 50, safe
                elif market_cap_rank <= 100:
                    return 5.0  # Top 100, medium
                elif market_cap_rank <= 200:
                    return 7.0  # Top 200, risky
                else:
                    return 9.0  # Below 200, very risky
            
            # Method 2: Use absolute market cap
            if market_cap > 100_000_000_000:  # >100B
                return 1.0
            elif market_cap > 10_000_000_000:  # >10B
                return 2.0
            elif market_cap > 1_000_000_000:  # >1B
                return 4.0
            elif market_cap > 100_000_000:  # >100M
                return 6.0
            else:
                return 8.0
            
        except Exception as e:
            logger.error(f"❌ Error calculating market cap risk: {e}")
            return 5.0
    
    def _map_to_score(self, value: float, ranges: List, scores: List) -> float:
        """
        Helper: Map a value to a score based on ranges
        """
        for i, (low, high) in enumerate(ranges):
            if low <= value < high:
                return scores[i]
        return scores[-1]  # Return highest score if above all ranges
    
    def _get_risk_level(self, risk_score: float) -> str:
        """
        Convert risk score to risk level
        """
        if risk_score <= self.low_threshold:
            return "low"
        elif risk_score <= self.medium_threshold:
            return "medium"
        else:
            return "high"
    
    def _get_recommendation(self, risk_score: float) -> str:
        """
        Get investment recommendation based on risk score
        """
        if risk_score <= 3:
            return "safe_investment"
        elif risk_score <= 5:
            return "moderate_investment"
        elif risk_score <= 7:
            return "risky_investment"
        else:
            return "avoid_investment"
    
    def _generate_analysis(self, risk_score: float, risk_level: str, coin_data: Dict) -> str:
        """
        Generate human-readable analysis
        """
        symbol = coin_data.get('symbol', 'This coin')
        
        if risk_level == "low":
            return f"{symbol} shows low risk with stable price action and high liquidity. Suitable for conservative investors."
        elif risk_level == "medium":
            return f"{symbol} has moderate risk with average volatility. Suitable for investors with balanced risk tolerance."
        else:
            return f"{symbol} carries high risk due to volatility or low liquidity. Only for aggressive investors."
    
    def _get_default_risk(self, symbol: str) -> Dict:
        """
        Return default risk data when calculation fails
        """
        return {
            'symbol': symbol,
            'risk_score': 5.0,
            'risk_level': 'medium',
            'factors': {
                'volatility': 5.0,
                'liquidity': 5.0,
                'trend': 5.0,
                'market_cap': 5.0
            },
            'recommendation': 'moderate_investment',
            'analysis': 'Unable to calculate detailed risk. Assume medium risk.',
            'calculated_at': datetime.now().isoformat()
        }
    
    def compare_risks(self, coin_data_list: List[Dict]) -> List[Dict]:
        """
        Calculate and compare risks for multiple coins
        Returns sorted by risk (lowest first)
        """
        results = []
        for coin_data in coin_data_list:
            risk = self.calculate_risk_score(coin_data)
            results.append(risk)
        
        # Sort by risk score (ascending)
        results.sort(key=lambda x: x['risk_score'])
        return results
    
    def is_suitable_for_user(self, coin_risk_score: float, user_risk_tolerance: int) -> Dict:
        """
        Check if coin is suitable for user's risk tolerance
        
        Args:
            coin_risk_score: Coin's risk score (0-10)
            user_risk_tolerance: User's risk tolerance (1-10)
        
        Returns:
            Suitability analysis
        """
        risk_diff = coin_risk_score - user_risk_tolerance
        
        if risk_diff <= -2:
            return {
                "suitable": True,
                "confidence": "high",
                "message": f"Well below your risk tolerance. Very safe choice."
            }
        elif risk_diff <= 0:
            return {
                "suitable": True,
                "confidence": "medium",
                "message": f"Matches your risk profile. Good investment option."
            }
        elif risk_diff <= 2:
            return {
                "suitable": False,
                "confidence": "low",
                "message": f"Slightly above your risk tolerance. Proceed with caution."
            }
        else:
            return {
                "suitable": False,
                "confidence": "high",
                "message": f"Significantly exceeds your risk tolerance. Consider safer alternatives."
            }


# Create global instance
risk_engine = RiskEngine()


# ==================== TESTING ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Risk Engine")
    print("=" * 60)
    
    # Test coins with different risk profiles
    test_coins = [
        {
            'symbol': 'BTC',
            'price': 37890,
            'change_24h': 2.5,
            'volume_24h': 28_000_000_000,
            'high_24h': 38500,
            'low_24h': 37200,
            'market_cap': 740_000_000_000,
            'market_cap_rank': 1
        },
        {
            'symbol': 'ETH',
            'price': 2320,
            'change_24h': 3.2,
            'volume_24h': 15_000_000_000,
            'high_24h': 2380,
            'low_24h': 2280,
            'market_cap': 280_000_000_000,
            'market_cap_rank': 2
        },
        {
            'symbol': 'DOGE',
            'price': 0.085,
            'change_24h': 8.5,
            'volume_24h': 500_000_000,
            'high_24h': 0.092,
            'low_24h': 0.078,
            'market_cap': 12_000_000_000,
            'market_cap_rank': 15
        }
    ]
    
    engine = RiskEngine()
    
    print("\n📊 Risk Analysis:")
    print("-" * 60)
    
    for coin in test_coins:
        risk = engine.calculate_risk_score(coin)
        print(f"\n{risk['symbol']}:")
        print(f"  Risk Score: {risk['risk_score']}/10 ({risk['risk_level'].upper()})")
        print(f"  Factors:")
        print(f"    - Volatility: {risk['factors']['volatility']}")
        print(f"    - Liquidity: {risk['factors']['liquidity']}")
        print(f"    - Trend: {risk['factors']['trend']}")
        print(f"    - Market Cap: {risk['factors']['market_cap']}")
        print(f"  Recommendation: {risk['recommendation']}")
    
    # Test user suitability
    print("\n" + "=" * 60)
    print("User Suitability Test (User Risk Tolerance: 5/10)")
    print("-" * 60)
    
    for coin in test_coins:
        risk = engine.calculate_risk_score(coin)
        suitability = engine.is_suitable_for_user(risk['risk_score'], 5)
        print(f"\n{coin['symbol']}: {suitability['message']}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)