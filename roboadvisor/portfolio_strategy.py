# roboadvisor/portfolio_strategy.py
"""
PORTFOLIO STRATEGY MODULE
Modern Portfolio Theory (MPT) based asset allocation
"""

from typing import Dict
from .user_profile import RiskType, UserProfile

def asset_allocation(risk_type: RiskType, years: int = 10, expected_return: float = None) -> Dict[str, float]:
    """
    Calculate optimal asset allocation based on risk profile
    Uses Modern Portfolio Theory principles
    
    Args:
        risk_type: User's risk tolerance
        years: Investment horizon (affects equity/debt ratio)
        expected_return: Expected annual return percentage (adjusts growth vs safety)
    
    Returns:
        Dictionary of asset_type -> allocation percentage (sum = 1.0)
    """
    
    # Base allocation matrices
    allocation_matrix = {
        RiskType.CONSERVATIVE: {
            "stocks": 0.20,
            "etf": 0.35,
            "mutual_funds": 0.35,
            "crypto": 0.05,
            "bonds": 0.05
        },
        RiskType.MODERATE: {
            "stocks": 0.40,
            "etf": 0.30,
            "mutual_funds": 0.20,
            "crypto": 0.10,
            "bonds": 0.00
        },
        RiskType.AGGRESSIVE: {
            "stocks": 0.55,
            "etf": 0.25,
            "mutual_funds": 0.10,
            "crypto": 0.10,
            "bonds": 0.00
        },
        RiskType.VERY_AGGRESSIVE: {
            "stocks": 0.60,
            "etf": 0.15,
            "mutual_funds": 0.05,
            "crypto": 0.20,
            "bonds": 0.00
        }
    }
    
    base_allocation = allocation_matrix.get(risk_type, allocation_matrix[RiskType.MODERATE])
    
    # Adjust for investment horizon (longer horizon = more equity)
    if years > 15:
        # Long term: Increase equity exposure
        adjustment_factor = 1.1
        base_allocation["stocks"] = min(0.70, base_allocation["stocks"] * adjustment_factor)
        base_allocation["etf"] = min(0.40, base_allocation["etf"] * adjustment_factor)
        # Reduce safer assets
        base_allocation["mutual_funds"] *= 0.9
        base_allocation["bonds"] *= 0.8
    elif years < 5:
        # Short term: Reduce volatility
        adjustment_factor = 0.8
        base_allocation["stocks"] *= adjustment_factor
        base_allocation["crypto"] *= 0.5
        # Increase safer assets
        base_allocation["mutual_funds"] = min(0.50, base_allocation["mutual_funds"] * 1.2)
        base_allocation["bonds"] = max(0.10, base_allocation["bonds"] + 0.05)
    
    # Normalize to ensure sum = 1.0
    total = sum(base_allocation.values())
    normalized_allocation = {k: v/total for k, v in base_allocation.items()}
    
    # 🔥 NEW: Adjust based on expected return (if provided)
    if expected_return is not None:
        if expected_return > 20:  # Aggressive growth target (>20% per year)
            # Increase growth assets (stocks, crypto)
            normalized_allocation["stocks"] = min(0.70, normalized_allocation["stocks"] * 1.3)
            normalized_allocation["crypto"] = min(0.25, normalized_allocation["crypto"] * 1.5)
            # Decrease safety assets (bonds, mutual funds)
            normalized_allocation["bonds"] *= 0.5
            normalized_allocation["mutual_funds"] *= 0.8
        elif expected_return > 15:  # High growth target (15-20%)
            normalized_allocation["stocks"] = min(0.60, normalized_allocation["stocks"] * 1.15)
            normalized_allocation["etf"] = min(0.40, normalized_allocation["etf"] * 1.1)
            normalized_allocation["mutual_funds"] *= 0.9
        elif expected_return < 8:  # Conservative returns (<8%)
            # Increase safety assets
            normalized_allocation["mutual_funds"] = min(0.50, normalized_allocation["mutual_funds"] * 1.2)
            normalized_allocation["bonds"] = max(0.15, normalized_allocation["bonds"] + 0.10)
            # Decrease volatile assets
            normalized_allocation["stocks"] *= 0.8
            normalized_allocation["crypto"] *= 0.5
        
        # Re-normalize after adjustment
        total = sum(normalized_allocation.values())
        normalized_allocation = {k: v/total for k, v in normalized_allocation.items()}
    
    return normalized_allocation

def get_sector_diversification(risk_type: RiskType) -> Dict[str, float]:
    """
    Recommend sector diversification within equities
    
    Returns:
        Dictionary of sector -> maximum allocation percentage
    """
    if risk_type in [RiskType.CONSERVATIVE, RiskType.MODERATE]:
        return {
            "Technology": 0.25,
            "Healthcare": 0.20,
            "Financial Services": 0.20,
            "Consumer Defensive": 0.15,
            "Industrials": 0.10,
            "Energy": 0.10
        }
    else:  # Aggressive
        return {
            "Technology": 0.35,
            "Healthcare": 0.20,
            "Financial Services": 0.15,
            "Consumer Cyclical": 0.15,
            "Communication Services": 0.15
        }

def get_geographic_diversification(risk_type: RiskType) -> Dict[str, float]:
    """
    Recommend geographic diversification
    
    Returns:
        Dictionary of region -> allocation percentage
    """
    if risk_type == RiskType.CONSERVATIVE:
        return {
            "India": 0.70,
            "US": 0.20,
            "International": 0.10
        }
    elif risk_type == RiskType.MODERATE:
        return {
            "India": 0.60,
            "US": 0.30,
            "International": 0.10
        }
    else:  # Aggressive
        return {
            "India": 0.50,
            "US": 0.35,
            "International": 0.15
        }

def calculate_portfolio_metrics(allocation: Dict[str, float], expected_returns: Dict[str, float]) -> Dict:
    """
    Calculate portfolio-level expected return
    
    Args:
        allocation: Asset allocation dictionary
        expected_returns: Expected return for each asset class
    
    Returns:
        Dictionary with portfolio metrics
    """
    portfolio_return = sum(allocation.get(asset, 0) * expected_returns.get(asset, 0) 
                          for asset in allocation.keys())
    
    # Rough risk estimates (standard deviation) by asset class
    risk_levels = {
        "stocks": 0.20,      # 20% volatility
        "etf": 0.15,         # 15% volatility
        "mutual_funds": 0.12,  # 12% volatility
        "crypto": 0.60,      # 60% volatility (very high)
        "bonds": 0.05        # 5% volatility (very low)
    }
    
    portfolio_risk = sum(allocation.get(asset, 0) * risk_levels.get(asset, 0.15)
                        for asset in allocation.keys())
    
    # Sharpe ratio (assuming risk-free rate of 6%)
    risk_free_rate = 0.06
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk if portfolio_risk > 0 else 0
    
    return {
        "expected_return": portfolio_return,
        "expected_risk": portfolio_risk,
        "sharpe_ratio": sharpe_ratio,
        "risk_adjusted_return": portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
    }
