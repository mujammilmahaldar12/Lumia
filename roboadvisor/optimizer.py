# roboadvisor/optimizer.py
"""
PORTFOLIO OPTIMIZATION MODULE
Modern Portfolio Theory (MPT) optimization
Calculates risk-adjusted returns, Sharpe ratio, and optimal weights
"""

import numpy as np
from typing import Dict, List, Tuple
from scipy.optimize import minimize

def calculate_portfolio_metrics(
    weights: np.ndarray,
    returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float = 0.06
) -> Tuple[float, float, float]:
    """
    Calculate portfolio return, risk, and Sharpe ratio
    
    Args:
        weights: Asset weights (should sum to 1.0)
        returns: Expected returns for each asset
        cov_matrix: Covariance matrix of returns
        risk_free_rate: Risk-free rate (default 6%)
    
    Returns:
        (portfolio_return, portfolio_risk, sharpe_ratio)
    """
    # Portfolio return
    portfolio_return = np.dot(weights, returns)
    
    # Portfolio risk (standard deviation)
    portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    portfolio_risk = np.sqrt(portfolio_variance)
    
    # Sharpe ratio
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk if portfolio_risk > 0 else 0
    
    return portfolio_return, portfolio_risk, sharpe_ratio

def optimize_portfolio(
    returns: np.ndarray,
    cov_matrix: np.ndarray,
    initial_weights: np.ndarray = None,
    risk_free_rate: float = 0.06,
    target_return: float = None
) -> Dict:
    """
    Optimize portfolio using Modern Portfolio Theory
    
    Finds optimal weights that:
    - Maximize Sharpe ratio (risk-adjusted return)
    - OR achieve target return with minimum risk
    
    Args:
        returns: Expected returns for each asset
        cov_matrix: Covariance matrix of returns
        initial_weights: Starting weights (default: equal allocation)
        risk_free_rate: Risk-free rate (default 6%)
        target_return: Target return (if None, maximizes Sharpe)
    
    Returns:
        Dictionary with optimized weights and metrics
    """
    n_assets = len(returns)
    
    if initial_weights is None:
        initial_weights = np.ones(n_assets) / n_assets  # Equal weights
    
    # Constraints: weights sum to 1
    constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
    
    # Bounds: weights between 0 and 1 (no short selling)
    bounds = tuple((0, 1) for _ in range(n_assets))
    
    if target_return is None:
        # Maximize Sharpe ratio (minimize negative Sharpe)
        def objective(w):
            ret, risk, sharpe = calculate_portfolio_metrics(w, returns, cov_matrix, risk_free_rate)
            return -sharpe  # Negative because we minimize
        
        result = minimize(
            objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
    else:
        # Minimize risk for target return
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
            {'type': 'eq', 'fun': lambda w: np.dot(w, returns) - target_return}
        ]
        
        def objective(w):
            variance = np.dot(w.T, np.dot(cov_matrix, w))
            return variance
        
        result = minimize(
            objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
    
    # Get final metrics
    optimal_weights = result.x
    portfolio_return, portfolio_risk, sharpe_ratio = calculate_portfolio_metrics(
        optimal_weights, returns, cov_matrix, risk_free_rate
    )
    
    return {
        "weights": optimal_weights,
        "expected_return": portfolio_return,
        "expected_risk": portfolio_risk,
        "sharpe_ratio": sharpe_ratio,
        "success": result.success,
        "message": result.message if hasattr(result, 'message') else "Optimization complete"
    }

def efficient_frontier(
    returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float = 0.06,
    n_points: int = 50
) -> List[Dict]:
    """
    Calculate efficient frontier (optimal portfolios for different risk levels)
    
    Args:
        returns: Expected returns for each asset
        cov_matrix: Covariance matrix
        risk_free_rate: Risk-free rate
        n_points: Number of points on frontier
    
    Returns:
        List of portfolio configurations on efficient frontier
    """
    min_return = np.min(returns)
    max_return = np.max(returns)
    target_returns = np.linspace(min_return, max_return, n_points)
    
    frontier = []
    
    for target_ret in target_returns:
        try:
            result = optimize_portfolio(
                returns,
                cov_matrix,
                target_return=target_ret,
                risk_free_rate=risk_free_rate
            )
            if result["success"]:
                frontier.append({
                    "target_return": target_ret,
                    "return": result["expected_return"],
                    "risk": result["expected_risk"],
                    "sharpe": result["sharpe_ratio"],
                    "weights": result["weights"]
                })
        except:
            continue
    
    return frontier

def estimate_covariance_matrix(price_data: Dict[str, List[float]]) -> np.ndarray:
    """
    Estimate covariance matrix from historical price data
    
    Args:
        price_data: Dictionary of {symbol: [prices]}
    
    Returns:
        Covariance matrix
    """
    # Calculate returns
    returns_dict = {}
    for symbol, prices in price_data.items():
        if len(prices) < 2:
            returns_dict[symbol] = [0]
        else:
            returns = np.diff(prices) / prices[:-1]
            returns_dict[symbol] = returns
    
    # Find minimum length
    min_len = min(len(r) for r in returns_dict.values())
    
    # Create returns matrix
    returns_matrix = np.array([r[:min_len] for r in returns_dict.values()])
    
    # Calculate covariance
    cov_matrix = np.cov(returns_matrix)
    
    return cov_matrix

def calculate_var(
    weights: np.ndarray,
    returns: np.ndarray,
    cov_matrix: np.ndarray,
    confidence_level: float = 0.95,
    investment_amount: float = 100000
) -> float:
    """
    Calculate Value at Risk (VaR)
    Maximum expected loss at given confidence level
    
    Args:
        weights: Portfolio weights
        returns: Expected returns
        cov_matrix: Covariance matrix
        confidence_level: Confidence level (0.95 = 95%)
        investment_amount: Total investment
    
    Returns:
        VaR amount (expected maximum loss)
    """
    from scipy.stats import norm
    
    portfolio_return = np.dot(weights, returns)
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    
    # Z-score for confidence level
    z_score = norm.ppf(1 - confidence_level)
    
    # VaR calculation
    var = investment_amount * (portfolio_return + z_score * portfolio_std)
    
    return abs(var)
