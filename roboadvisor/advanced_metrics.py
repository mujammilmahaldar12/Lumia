# roboadvisor/advanced_metrics.py
"""
ADVANCED FINANCIAL METRICS CALCULATOR
Calculates comprehensive metrics: CAGR, Max Drawdown, Beta, Alpha, Sortino, etc.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.daily_price import DailyPrice
from models.assets import Asset


class AdvancedMetricsCalculator:
    """Calculate advanced financial metrics for assets"""
    
    def __init__(self, db: Session):
        self.db = db
        self.benchmark_returns = None  # Will cache market benchmark returns
    
    def calculate_all_metrics(self, asset: Asset, lookback_days: int = 365) -> Dict:
        """
        Calculate comprehensive metrics for an asset
        
        Args:
            asset: Asset to analyze
            lookback_days: Number of days of historical data to use
        
        Returns:
            Dictionary with all calculated metrics
        """
        # Get price data
        cutoff_date = datetime.now() - timedelta(days=lookback_days + 100)  # Extra buffer
        prices = self.db.query(DailyPrice).filter(
            DailyPrice.asset_id == asset.id,
            DailyPrice.date >= cutoff_date
        ).order_by(DailyPrice.date).all()
        
        if len(prices) < 30:  # Need minimum data
            return self._get_default_metrics()
        
        close_prices = np.array([p.close_price for p in prices if p.close_price])
        dates = [p.date for p in prices if p.close_price]
        
        if len(close_prices) < 30:
            return self._get_default_metrics()
        
        # Calculate daily returns
        returns = np.diff(close_prices) / close_prices[:-1]
        
        metrics = {}
        
        # 1. CAGR (Compound Annual Growth Rate)
        metrics['cagr'] = self._calculate_cagr(close_prices, dates)
        
        # 2. Total Return
        metrics['total_return'] = (close_prices[-1] - close_prices[0]) / close_prices[0]
        
        # 3. Volatility (Annualized)
        metrics['volatility'] = np.std(returns) * np.sqrt(252)
        
        # 4. Sharpe Ratio
        metrics['sharpe_ratio'] = self._calculate_sharpe(returns)
        
        # 5. Sortino Ratio (only downside volatility)
        metrics['sortino_ratio'] = self._calculate_sortino(returns)
        
        # 6. Maximum Drawdown
        metrics['max_drawdown'] = self._calculate_max_drawdown(close_prices)
        
        # 7. Calmar Ratio (CAGR / Max Drawdown)
        if metrics['max_drawdown'] != 0:
            metrics['calmar_ratio'] = abs(metrics['cagr'] / metrics['max_drawdown'])
        else:
            metrics['calmar_ratio'] = 0
        
        # 8. Beta (relative to market)
        metrics['beta'] = self._calculate_beta(returns, dates)
        
        # 9. Alpha (excess return vs expected)
        metrics['alpha'] = self._calculate_alpha(
            metrics['total_return'], 
            metrics['beta'], 
            len(dates)
        )
        
        # 10. Value at Risk (95% confidence)
        metrics['var_95'] = self._calculate_var(returns, confidence=0.95)
        
        # 11. Conditional VaR (Expected Shortfall)
        metrics['cvar_95'] = self._calculate_cvar(returns, confidence=0.95)
        
        # 12. Downside Deviation
        metrics['downside_deviation'] = self._calculate_downside_deviation(returns)
        
        # 13. Up/Down Capture Ratios
        up_capture, down_capture = self._calculate_capture_ratios(returns, dates)
        metrics['up_capture_ratio'] = up_capture
        metrics['down_capture_ratio'] = down_capture
        
        # 14. Win Rate (% of positive days)
        metrics['win_rate'] = np.sum(returns > 0) / len(returns) if len(returns) > 0 else 0
        
        # 15. Average Win/Loss
        wins = returns[returns > 0]
        losses = returns[returns < 0]
        metrics['avg_win'] = np.mean(wins) if len(wins) > 0 else 0
        metrics['avg_loss'] = np.mean(losses) if len(losses) > 0 else 0
        
        # 16. Profit Factor
        total_wins = np.sum(wins) if len(wins) > 0 else 0
        total_losses = abs(np.sum(losses)) if len(losses) > 0 else 1
        metrics['profit_factor'] = total_wins / total_losses if total_losses > 0 else 0
        
        return metrics
    
    def _calculate_cagr(self, prices: np.ndarray, dates: List[datetime]) -> float:
        """Calculate Compound Annual Growth Rate"""
        if len(prices) < 2 or len(dates) < 2:
            return 0.0
        
        start_price = prices[0]
        end_price = prices[-1]
        
        # Calculate years
        start_date = dates[0]
        end_date = dates[-1]
        years = (end_date - start_date).days / 365.25
        
        if years <= 0 or start_price <= 0:
            return 0.0
        
        # CAGR formula: (End/Start)^(1/years) - 1
        cagr = (end_price / start_price) ** (1 / years) - 1
        return cagr
    
    def _calculate_sharpe(self, returns: np.ndarray, risk_free_rate: float = 0.06) -> float:
        """Calculate Sharpe Ratio"""
        if len(returns) < 2:
            return 0.0
        
        # Annualize returns
        avg_return = np.mean(returns) * 252
        volatility = np.std(returns) * np.sqrt(252)
        
        if volatility == 0:
            return 0.0
        
        sharpe = (avg_return - risk_free_rate) / volatility
        return sharpe
    
    def _calculate_sortino(self, returns: np.ndarray, risk_free_rate: float = 0.06) -> float:
        """
        Calculate Sortino Ratio (Sharpe with only downside deviation)
        Better measure as it only penalizes downside volatility
        """
        if len(returns) < 2:
            return 0.0
        
        # Annualize returns
        avg_return = np.mean(returns) * 252
        
        # Calculate downside deviation (only negative returns)
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            return 0.0  # No downside = infinite Sortino
        
        downside_std = np.std(downside_returns) * np.sqrt(252)
        
        if downside_std == 0:
            return 0.0
        
        sortino = (avg_return - risk_free_rate) / downside_std
        return sortino
    
    def _calculate_max_drawdown(self, prices: np.ndarray) -> float:
        """
        Calculate Maximum Drawdown (worst peak-to-trough decline)
        Negative value indicates loss
        """
        if len(prices) < 2:
            return 0.0
        
        # Calculate running maximum
        running_max = np.maximum.accumulate(prices)
        
        # Calculate drawdown at each point
        drawdown = (prices - running_max) / running_max
        
        # Return worst drawdown (most negative)
        max_dd = np.min(drawdown)
        return max_dd
    
    def _calculate_beta(self, returns: np.ndarray, dates: List[datetime]) -> float:
        """
        Calculate Beta (sensitivity to market movements)
        Beta > 1: More volatile than market
        Beta < 1: Less volatile than market
        """
        try:
            # Get benchmark returns (e.g., NIFTY 50 or S&P 500)
            benchmark_returns = self._get_benchmark_returns(dates)
            
            if benchmark_returns is None or len(benchmark_returns) != len(returns):
                return 1.0  # Default beta
            
            # Calculate covariance and variance
            covariance = np.cov(returns, benchmark_returns)[0, 1]
            market_variance = np.var(benchmark_returns)
            
            if market_variance == 0:
                return 1.0
            
            beta = covariance / market_variance
            return beta
            
        except Exception:
            return 1.0  # Default beta
    
    def _calculate_alpha(self, total_return: float, beta: float, n_days: int) -> float:
        """
        Calculate Alpha (excess return vs expected)
        Alpha > 0: Outperforming expectations
        Alpha < 0: Underperforming expectations
        """
        # Annualize total return
        years = n_days / 365.25
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # Expected return using CAPM: Rf + Beta * (Rm - Rf)
        risk_free_rate = 0.06  # 6%
        market_return = 0.12   # Assumed 12% market return
        expected_return = risk_free_rate + beta * (market_return - risk_free_rate)
        
        # Alpha = Actual - Expected
        alpha = annualized_return - expected_return
        return alpha
    
    def _calculate_var(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR)
        Maximum expected loss at given confidence level
        """
        if len(returns) < 10:
            return 0.0
        
        # Calculate percentile (5th percentile for 95% confidence)
        var = np.percentile(returns, (1 - confidence) * 100)
        return var
    
    def _calculate_cvar(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """
        Calculate Conditional VaR (Expected Shortfall)
        Average of losses beyond VaR threshold
        """
        if len(returns) < 10:
            return 0.0
        
        var = self._calculate_var(returns, confidence)
        
        # Average of returns worse than VaR
        tail_losses = returns[returns <= var]
        if len(tail_losses) == 0:
            return var
        
        cvar = np.mean(tail_losses)
        return cvar
    
    def _calculate_downside_deviation(self, returns: np.ndarray, target: float = 0) -> float:
        """Calculate downside deviation (volatility of negative returns)"""
        downside_returns = returns[returns < target]
        if len(downside_returns) == 0:
            return 0.0
        
        downside_std = np.std(downside_returns) * np.sqrt(252)  # Annualized
        return downside_std
    
    def _calculate_capture_ratios(
        self, 
        returns: np.ndarray, 
        dates: List[datetime]
    ) -> Tuple[float, float]:
        """
        Calculate Up/Down Capture Ratios
        Up > 100%: Captures more upside than market
        Down < 100%: Loses less than market in downturns
        """
        try:
            benchmark_returns = self._get_benchmark_returns(dates)
            
            if benchmark_returns is None or len(benchmark_returns) != len(returns):
                return 1.0, 1.0
            
            # Up capture: asset return / market return when market is up
            up_mask = benchmark_returns > 0
            if np.sum(up_mask) > 0:
                asset_up = np.mean(returns[up_mask])
                market_up = np.mean(benchmark_returns[up_mask])
                up_capture = asset_up / market_up if market_up != 0 else 1.0
            else:
                up_capture = 1.0
            
            # Down capture: asset return / market return when market is down
            down_mask = benchmark_returns < 0
            if np.sum(down_mask) > 0:
                asset_down = np.mean(returns[down_mask])
                market_down = np.mean(benchmark_returns[down_mask])
                down_capture = asset_down / market_down if market_down != 0 else 1.0
            else:
                down_capture = 1.0
            
            return up_capture, down_capture
            
        except Exception:
            return 1.0, 1.0
    
    def _get_benchmark_returns(self, dates: List[datetime]) -> Optional[np.ndarray]:
        """
        Get benchmark (market index) returns for comparison
        Uses NIFTY 50 or S&P 500 as proxy
        """
        try:
            # Try to find NIFTY 50 ETF as benchmark
            benchmark_symbol = "^NSEI"  # NIFTY 50
            
            benchmark_asset = self.db.query(Asset).filter(
                Asset.symbol == benchmark_symbol
            ).first()
            
            if not benchmark_asset:
                # Try S&P 500 as alternative
                benchmark_symbol = "^GSPC"
                benchmark_asset = self.db.query(Asset).filter(
                    Asset.symbol == benchmark_symbol
                ).first()
            
            if not benchmark_asset:
                return None
            
            # Get benchmark prices for same dates
            start_date = min(dates)
            end_date = max(dates)
            
            benchmark_prices = self.db.query(DailyPrice).filter(
                DailyPrice.asset_id == benchmark_asset.id,
                DailyPrice.date >= start_date,
                DailyPrice.date <= end_date
            ).order_by(DailyPrice.date).all()
            
            if len(benchmark_prices) < 10:
                return None
            
            # Calculate returns
            close_prices = np.array([p.close_price for p in benchmark_prices if p.close_price])
            returns = np.diff(close_prices) / close_prices[:-1]
            
            return returns
            
        except Exception:
            return None
    
    def _get_default_metrics(self) -> Dict:
        """Return default metrics when calculation fails"""
        return {
            'cagr': 0.0,
            'total_return': 0.0,
            'volatility': 0.15,
            'sharpe_ratio': 0.0,
            'sortino_ratio': 0.0,
            'max_drawdown': 0.0,
            'calmar_ratio': 0.0,
            'beta': 1.0,
            'alpha': 0.0,
            'var_95': 0.0,
            'cvar_95': 0.0,
            'downside_deviation': 0.0,
            'up_capture_ratio': 1.0,
            'down_capture_ratio': 1.0,
            'win_rate': 0.5,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'profit_factor': 1.0
        }


def score_with_advanced_metrics(metrics: Dict) -> float:
    """
    Score an asset using advanced metrics (bonus points)
    Can add up to 10 bonus points to total score
    
    Args:
        metrics: Dictionary from calculate_all_metrics()
    
    Returns:
        Bonus score (0-10 points)
    """
    score = 0
    
    # 1. CAGR (3 points)
    cagr = metrics.get('cagr', 0)
    if cagr > 0.25:  # >25% annual growth
        score += 3
    elif cagr > 0.15:  # >15%
        score += 2
    elif cagr > 0.10:  # >10%
        score += 1
    
    # 2. Sortino Ratio (2 points) - Better than Sharpe
    sortino = metrics.get('sortino_ratio', 0)
    if sortino > 1.5:
        score += 2
    elif sortino > 1.0:
        score += 1
    
    # 3. Max Drawdown (2 points) - Lower is better
    max_dd = abs(metrics.get('max_drawdown', 1))
    if max_dd < 0.10:  # <10% drawdown
        score += 2
    elif max_dd < 0.20:  # <20%
        score += 1
    
    # 4. Alpha (2 points) - Positive alpha
    alpha = metrics.get('alpha', 0)
    if alpha > 0.05:  # >5% excess return
        score += 2
    elif alpha > 0:
        score += 1
    
    # 5. Capture Ratios (1 point)
    up_capture = metrics.get('up_capture_ratio', 1)
    down_capture = metrics.get('down_capture_ratio', 1)
    
    # Good: High up capture, low down capture
    if up_capture > 1.0 and down_capture < 1.0:
        score += 1
    
    return min(score, 10)  # Cap at 10 bonus points
