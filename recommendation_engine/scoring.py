"""
SCORING MODULE - Calculate Technical & Fundamental Scores

This module calculates scores (0-100) for different aspects of an asset:
1. Technical Score - Based on price patterns, momentum, indicators
2. Fundamental Score - Based on financial health, ratios, growth
3. Risk Score - Based on volatility, beta, drawdown

ALGORITHM EXPLANATION:
- Each metric contributes points (max 100 total)
- Higher score = Better investment opportunity
- Scores are normalized to 0-100 scale
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Dict, List, Optional


# ============================================================================
# TECHNICAL ANALYSIS SCORING
# ============================================================================

def calculate_technical_score(prices_df: pd.DataFrame) -> Dict:
    """
    Calculate Technical Analysis Score (0-100)
    
    ALGORITHM:
    1. Moving Average (MA) Crossover → 30 points
       - If SMA(50) > SMA(200) = Bullish = +30
       - If price > SMA(50) = Additional +10
    
    2. RSI (Relative Strength Index) → 20 points
       - RSI < 30 = Oversold = +20 (good buy opportunity)
       - RSI 30-70 = Neutral = +10
       - RSI > 70 = Overbought = +0
    
    3. MACD (Moving Average Convergence Divergence) → 20 points
       - MACD line > Signal line = Bullish = +20
    
    4. Volume Trend → 15 points
       - Recent volume > avg volume = +15
    
    5. Price Momentum (3-month return) → 15 points
       - Positive return = +15
       - Scaled by magnitude
    
    Args:
        prices_df: DataFrame with columns [date, close_price, volume]
    
    Returns:
        Dict with technical_score and breakdown
    """
    if len(prices_df) < 200:
        return {'technical_score': 50, 'reason': 'Insufficient data', 'breakdown': {}}
    
    scores = {}
    breakdown = {}
    
    # 1. MOVING AVERAGE CROSSOVER (30 points)
    prices_df['sma_50'] = prices_df['close_price'].rolling(window=50).mean()
    prices_df['sma_200'] = prices_df['close_price'].rolling(window=200).mean()
    
    latest_price = prices_df['close_price'].iloc[-1]
    latest_sma_50 = prices_df['sma_50'].iloc[-1]
    latest_sma_200 = prices_df['sma_200'].iloc[-1]
    
    ma_score = 0
    if pd.notna(latest_sma_50) and pd.notna(latest_sma_200):
        if latest_sma_50 > latest_sma_200:  # Golden Cross
            ma_score += 30
            breakdown['ma_signal'] = 'Bullish (Golden Cross)'
        else:
            ma_score += 10
            breakdown['ma_signal'] = 'Bearish'
        
        if latest_price > latest_sma_50:
            ma_score += 10
            breakdown['price_vs_ma'] = f'Price above SMA(50)'
    
    scores['moving_average'] = min(ma_score, 30)
    
    # 2. RSI - RELATIVE STRENGTH INDEX (20 points)
    delta = prices_df['close_price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    latest_rsi = rsi.iloc[-1]
    
    if pd.notna(latest_rsi):
        if latest_rsi < 30:  # Oversold - Good buying opportunity
            rsi_score = 20
            breakdown['rsi'] = f'{latest_rsi:.1f} (Oversold - Buy signal)'
        elif latest_rsi > 70:  # Overbought
            rsi_score = 0
            breakdown['rsi'] = f'{latest_rsi:.1f} (Overbought - Caution)'
        else:  # Neutral
            rsi_score = 10
            breakdown['rsi'] = f'{latest_rsi:.1f} (Neutral)'
    else:
        rsi_score = 10
        breakdown['rsi'] = 'Insufficient data'
    
    scores['rsi'] = rsi_score
    
    # 3. MACD - MOMENTUM INDICATOR (20 points)
    ema_12 = prices_df['close_price'].ewm(span=12, adjust=False).mean()
    ema_26 = prices_df['close_price'].ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    
    latest_macd = macd_line.iloc[-1]
    latest_signal = signal_line.iloc[-1]
    
    if pd.notna(latest_macd) and pd.notna(latest_signal):
        if latest_macd > latest_signal:  # Bullish
            macd_score = 20
            breakdown['macd'] = 'Bullish crossover'
        else:
            macd_score = 5
            breakdown['macd'] = 'Bearish'
    else:
        macd_score = 10
        breakdown['macd'] = 'Insufficient data'
    
    scores['macd'] = macd_score
    
    # 4. VOLUME TREND (15 points)
    avg_volume = prices_df['volume'].rolling(window=20).mean().iloc[-1]
    recent_volume = prices_df['volume'].iloc[-5:].mean()
    
    if pd.notna(avg_volume) and pd.notna(recent_volume) and avg_volume > 0:
        if recent_volume > avg_volume * 1.2:  # 20% higher
            volume_score = 15
            breakdown['volume'] = f'Strong volume ({recent_volume/avg_volume:.1%} above avg)'
        elif recent_volume > avg_volume:
            volume_score = 10
            breakdown['volume'] = 'Above average volume'
        else:
            volume_score = 5
            breakdown['volume'] = 'Below average volume'
    else:
        volume_score = 7
        breakdown['volume'] = 'Normal'
    
    scores['volume'] = volume_score
    
    # 5. PRICE MOMENTUM - 3 MONTH RETURN (15 points)
    if len(prices_df) >= 63:  # ~3 months of trading days
        price_3m_ago = prices_df['close_price'].iloc[-63]
        momentum_return = (latest_price - price_3m_ago) / price_3m_ago
        
        if momentum_return > 0.15:  # >15% gain
            momentum_score = 15
            breakdown['momentum'] = f'Strong uptrend ({momentum_return:.1%})'
        elif momentum_return > 0:
            momentum_score = 10 + (momentum_return * 33)  # Scale 0-10% to 10-15 points
            breakdown['momentum'] = f'Positive momentum ({momentum_return:.1%})'
        else:
            momentum_score = max(0, 5 + (momentum_return * 50))  # Scale negative to 0-5
            breakdown['momentum'] = f'Negative momentum ({momentum_return:.1%})'
    else:
        momentum_score = 7
        breakdown['momentum'] = 'Insufficient data'
    
    scores['momentum'] = min(momentum_score, 15)
    
    # CALCULATE FINAL TECHNICAL SCORE
    technical_score = sum(scores.values())
    
    return {
        'technical_score': min(technical_score, 100),
        'breakdown': breakdown,
        'individual_scores': scores
    }


# ============================================================================
# FUNDAMENTAL ANALYSIS SCORING
# ============================================================================

def calculate_fundamental_score_stock(fundamentals: Dict) -> Dict:
    """
    Calculate Fundamental Score for STOCKS (0-100)
    
    ALGORITHM:
    1. P/E Ratio (20 points)
       - Compare to industry average
       - Lower P/E = better value = higher score
    
    2. Revenue Growth YoY (20 points)
       - >20% growth = +20
       - >10% growth = +15
       - Positive growth = +10
    
    3. Profit Margin (15 points)
       - Net Income / Revenue
       - >20% = +15
       - >10% = +10
    
    4. Debt-to-Equity Ratio (15 points)
       - <0.5 = +15 (low debt)
       - <1.0 = +10
       - >2.0 = +0 (high debt)
    
    5. ROE - Return on Equity (15 points)
       - >20% = +15
       - >15% = +10
    
    6. Dividend Yield (15 points)
       - >4% = +15
       - >2% = +10
    """
    scores = {}
    breakdown = {}
    
    # 1. P/E RATIO (20 points) - Lower is better (up to a point)
    pe_ratio = fundamentals.get('price_to_earnings_ratio')
    if pe_ratio and pe_ratio > 0:
        if pe_ratio < 15:
            scores['pe_ratio'] = 20
            breakdown['pe_ratio'] = f'{pe_ratio:.1f} (Undervalued)'
        elif pe_ratio < 25:
            scores['pe_ratio'] = 15
            breakdown['pe_ratio'] = f'{pe_ratio:.1f} (Fair value)'
        elif pe_ratio < 35:
            scores['pe_ratio'] = 10
            breakdown['pe_ratio'] = f'{pe_ratio:.1f} (Slightly overvalued)'
        else:
            scores['pe_ratio'] = 5
            breakdown['pe_ratio'] = f'{pe_ratio:.1f} (Overvalued)'
    else:
        scores['pe_ratio'] = 10
        breakdown['pe_ratio'] = 'Not available'
    
    # 2. REVENUE GROWTH (20 points)
    revenue_current = fundamentals.get('total_revenue_current')
    revenue_previous = fundamentals.get('total_revenue_previous')
    
    if revenue_current and revenue_previous and revenue_previous > 0:
        growth = (revenue_current - revenue_previous) / revenue_previous
        
        if growth > 0.20:  # >20% growth
            scores['revenue_growth'] = 20
            breakdown['revenue_growth'] = f'{growth:.1%} (Excellent)'
        elif growth > 0.10:  # >10% growth
            scores['revenue_growth'] = 15
            breakdown['revenue_growth'] = f'{growth:.1%} (Strong)'
        elif growth > 0:
            scores['revenue_growth'] = 10
            breakdown['revenue_growth'] = f'{growth:.1%} (Positive)'
        else:
            scores['revenue_growth'] = 5
            breakdown['revenue_growth'] = f'{growth:.1%} (Declining)'
    else:
        scores['revenue_growth'] = 10
        breakdown['revenue_growth'] = 'Not available'
    
    # 3. PROFIT MARGIN (15 points)
    net_income = fundamentals.get('net_income')
    revenue = fundamentals.get('total_revenue_current')
    
    if net_income and revenue and revenue > 0:
        profit_margin = net_income / revenue
        
        if profit_margin > 0.20:  # >20%
            scores['profit_margin'] = 15
            breakdown['profit_margin'] = f'{profit_margin:.1%} (Excellent)'
        elif profit_margin > 0.10:  # >10%
            scores['profit_margin'] = 10
            breakdown['profit_margin'] = f'{profit_margin:.1%} (Good)'
        elif profit_margin > 0:
            scores['profit_margin'] = 5
            breakdown['profit_margin'] = f'{profit_margin:.1%} (Positive)'
        else:
            scores['profit_margin'] = 0
            breakdown['profit_margin'] = f'{profit_margin:.1%} (Negative)'
    else:
        scores['profit_margin'] = 7
        breakdown['profit_margin'] = 'Not available'
    
    # 4. DEBT-TO-EQUITY RATIO (15 points) - Lower is better
    total_debt = fundamentals.get('total_debt')
    total_equity = fundamentals.get('total_equity')
    
    if total_debt is not None and total_equity and total_equity > 0:
        debt_ratio = total_debt / total_equity
        
        if debt_ratio < 0.5:
            scores['debt_ratio'] = 15
            breakdown['debt_ratio'] = f'{debt_ratio:.2f} (Low debt - Excellent)'
        elif debt_ratio < 1.0:
            scores['debt_ratio'] = 10
            breakdown['debt_ratio'] = f'{debt_ratio:.2f} (Moderate debt)'
        elif debt_ratio < 2.0:
            scores['debt_ratio'] = 5
            breakdown['debt_ratio'] = f'{debt_ratio:.2f} (High debt)'
        else:
            scores['debt_ratio'] = 0
            breakdown['debt_ratio'] = f'{debt_ratio:.2f} (Very high debt - Risky)'
    else:
        scores['debt_ratio'] = 7
        breakdown['debt_ratio'] = 'Not available'
    
    # 5. ROE - RETURN ON EQUITY (15 points)
    roe = fundamentals.get('return_on_equity')
    
    if roe:
        if roe > 0.20:  # >20%
            scores['roe'] = 15
            breakdown['roe'] = f'{roe:.1%} (Excellent)'
        elif roe > 0.15:  # >15%
            scores['roe'] = 10
            breakdown['roe'] = f'{roe:.1%} (Good)'
        elif roe > 0.10:  # >10%
            scores['roe'] = 7
            breakdown['roe'] = f'{roe:.1%} (Average)'
        else:
            scores['roe'] = 3
            breakdown['roe'] = f'{roe:.1%} (Below average)'
    else:
        scores['roe'] = 7
        breakdown['roe'] = 'Not available'
    
    # 6. DIVIDEND YIELD (15 points)
    dividend_yield = fundamentals.get('dividend_yield')
    
    if dividend_yield:
        if dividend_yield > 0.04:  # >4%
            scores['dividend_yield'] = 15
            breakdown['dividend_yield'] = f'{dividend_yield:.2%} (High income)'
        elif dividend_yield > 0.02:  # >2%
            scores['dividend_yield'] = 10
            breakdown['dividend_yield'] = f'{dividend_yield:.2%} (Good income)'
        elif dividend_yield > 0:
            scores['dividend_yield'] = 5
            breakdown['dividend_yield'] = f'{dividend_yield:.2%} (Some income)'
        else:
            scores['dividend_yield'] = 0
            breakdown['dividend_yield'] = 'No dividend'
    else:
        scores['dividend_yield'] = 0
        breakdown['dividend_yield'] = 'No dividend'
    
    fundamental_score = sum(scores.values())
    
    return {
        'fundamental_score': min(fundamental_score, 100),
        'breakdown': breakdown,
        'individual_scores': scores
    }


def calculate_fundamental_score_etf(asset_data: Dict) -> Dict:
    """
    Calculate Fundamental Score for ETFs (0-100)
    
    ALGORITHM:
    1. Expense Ratio (30 points) - Lower is better
    2. AUM - Assets Under Management (25 points) - Higher is better
    3. 5-Year Return (25 points)
    4. Tracking Error (20 points) - Lower is better
    """
    scores = {}
    breakdown = {}
    
    # 1. EXPENSE RATIO (30 points)
    expense_ratio = asset_data.get('expense_ratio')
    if expense_ratio:
        if expense_ratio < 0.002:  # <0.2%
            scores['expense_ratio'] = 30
            breakdown['expense_ratio'] = f'{expense_ratio:.2%} (Very low)'
        elif expense_ratio < 0.005:  # <0.5%
            scores['expense_ratio'] = 20
            breakdown['expense_ratio'] = f'{expense_ratio:.2%} (Low)'
        elif expense_ratio < 0.01:  # <1%
            scores['expense_ratio'] = 10
            breakdown['expense_ratio'] = f'{expense_ratio:.2%} (Moderate)'
        else:
            scores['expense_ratio'] = 5
            breakdown['expense_ratio'] = f'{expense_ratio:.2%} (High)'
    else:
        scores['expense_ratio'] = 15
    
    # 2. AUM (25 points)
    aum = asset_data.get('total_assets')
    if aum:
        if aum > 10_000_000_000:  # >$10B
            scores['aum'] = 25
            breakdown['aum'] = f'${aum/1e9:.1f}B (Large fund)'
        elif aum > 1_000_000_000:  # >$1B
            scores['aum'] = 20
            breakdown['aum'] = f'${aum/1e9:.1f}B (Medium fund)'
        elif aum > 100_000_000:  # >$100M
            scores['aum'] = 10
            breakdown['aum'] = f'${aum/1e6:.0f}M (Small fund)'
        else:
            scores['aum'] = 5
            breakdown['aum'] = 'Very small fund'
    else:
        scores['aum'] = 12
    
    # 3 & 4: Would need historical return data
    scores['returns'] = 15  # Placeholder
    scores['tracking'] = 10  # Placeholder
    
    fundamental_score = sum(scores.values())
    
    return {
        'fundamental_score': min(fundamental_score, 100),
        'breakdown': breakdown,
        'individual_scores': scores
    }


# ============================================================================
# RISK SCORING
# ============================================================================

def calculate_risk_score(prices_df: pd.DataFrame, market_prices_df: pd.DataFrame = None) -> Dict:
    """
    Calculate Risk Score (0-100)
    Higher score = Lower risk (safer investment)
    
    ALGORITHM:
    1. Beta (25 points) - Volatility vs market
       - Beta < 0.8 = Low volatility = +25
       - Beta 0.8-1.2 = Average = +15
       - Beta > 1.2 = High volatility = +5
    
    2. Max Drawdown (20 points)
       - Max decline from peak in last 12 months
       - < 10% = +20
       - 10-20% = +10
       - > 20% = +0
    
    3. Volatility - Standard Deviation (20 points)
    4. Sharpe Ratio (20 points) - Risk-adjusted returns
    5. Liquidity - Average Volume (15 points)
    """
    scores = {}
    breakdown = {}
    
    if len(prices_df) < 30:
        return {'risk_score': 50, 'breakdown': {}, 'individual_scores': {}}
    
    returns = prices_df['close_price'].pct_change().dropna()
    
    # 1. BETA (25 points)
    if market_prices_df is not None and len(market_prices_df) > 0:
        market_returns = market_prices_df['close_price'].pct_change().dropna()
        
        # Align dates
        common_dates = returns.index.intersection(market_returns.index)
        if len(common_dates) > 30:
            asset_returns_aligned = returns.loc[common_dates]
            market_returns_aligned = market_returns.loc[common_dates]
            
            covariance = asset_returns_aligned.cov(market_returns_aligned)
            market_variance = market_returns_aligned.var()
            
            if market_variance > 0:
                beta = covariance / market_variance
                
                if beta < 0.8:
                    scores['beta'] = 25
                    breakdown['beta'] = f'{beta:.2f} (Low volatility)'
                elif beta < 1.2:
                    scores['beta'] = 15
                    breakdown['beta'] = f'{beta:.2f} (Average volatility)'
                else:
                    scores['beta'] = 5
                    breakdown['beta'] = f'{beta:.2f} (High volatility)'
            else:
                scores['beta'] = 15
        else:
            scores['beta'] = 15
    else:
        scores['beta'] = 15
        breakdown['beta'] = 'Market data not available'
    
    # 2. MAX DRAWDOWN (20 points)
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    
    if max_drawdown > -0.10:  # Less than 10% drawdown
        scores['drawdown'] = 20
        breakdown['drawdown'] = f'{max_drawdown:.1%} (Low drawdown - Stable)'
    elif max_drawdown > -0.20:  # 10-20%
        scores['drawdown'] = 10
        breakdown['drawdown'] = f'{max_drawdown:.1%} (Moderate drawdown)'
    else:  # >20%
        scores['drawdown'] = 0
        breakdown['drawdown'] = f'{max_drawdown:.1%} (High drawdown - Volatile)'
    
    # 3. VOLATILITY (20 points)
    annual_volatility = returns.std() * np.sqrt(252)  # Annualized
    
    if annual_volatility < 0.15:  # <15%
        scores['volatility'] = 20
        breakdown['volatility'] = f'{annual_volatility:.1%} (Low - Stable)'
    elif annual_volatility < 0.25:  # 15-25%
        scores['volatility'] = 10
        breakdown['volatility'] = f'{annual_volatility:.1%} (Moderate)'
    else:  # >25%
        scores['volatility'] = 5
        breakdown['volatility'] = f'{annual_volatility:.1%} (High - Risky)'
    
    # 4. SHARPE RATIO (20 points)
    mean_return = returns.mean() * 252  # Annualized
    risk_free_rate = 0.065  # 6.5% from .env
    
    if annual_volatility > 0:
        sharpe_ratio = (mean_return - risk_free_rate) / annual_volatility
        
        if sharpe_ratio > 1.5:
            scores['sharpe'] = 20
            breakdown['sharpe'] = f'{sharpe_ratio:.2f} (Excellent risk-adjusted return)'
        elif sharpe_ratio > 1.0:
            scores['sharpe'] = 15
            breakdown['sharpe'] = f'{sharpe_ratio:.2f} (Good)'
        elif sharpe_ratio > 0.5:
            scores['sharpe'] = 10
            breakdown['sharpe'] = f'{sharpe_ratio:.2f} (Average)'
        else:
            scores['sharpe'] = 5
            breakdown['sharpe'] = f'{sharpe_ratio:.2f} (Below average)'
    else:
        scores['sharpe'] = 10
    
    # 5. LIQUIDITY (15 points)
    avg_volume = prices_df['volume'].mean()
    
    if avg_volume > 1_000_000:  # >1M shares
        scores['liquidity'] = 15
        breakdown['liquidity'] = f'{avg_volume:,.0f} avg volume (Highly liquid)'
    elif avg_volume > 100_000:  # >100K
        scores['liquidity'] = 10
        breakdown['liquidity'] = f'{avg_volume:,.0f} avg volume (Good liquidity)'
    else:
        scores['liquidity'] = 5
        breakdown['liquidity'] = f'{avg_volume:,.0f} avg volume (Low liquidity)'
    
    risk_score = sum(scores.values())
    
    return {
        'risk_score': min(risk_score, 100),
        'breakdown': breakdown,
        'individual_scores': scores
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_asset_prices_from_db(db: Session, asset_id: int, days: int = 365) -> pd.DataFrame:
    """Fetch historical prices from database"""
    from models.daily_price import DailyPrice
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    prices = db.query(DailyPrice).filter(
        DailyPrice.asset_id == asset_id,
        DailyPrice.date >= cutoff_date
    ).order_by(DailyPrice.date).all()
    
    if not prices:
        return pd.DataFrame()
    
    data = [{
        'date': p.date,
        'close_price': p.close_price,
        'volume': p.volume,
        'high_price': p.high_price,
        'low_price': p.low_price
    } for p in prices]
    
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    
    return df
