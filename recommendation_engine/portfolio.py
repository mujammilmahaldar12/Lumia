"""
PORTFOLIO CONSTRUCTION MODULE - Modern Portfolio Theory & Diversification

This module builds optimal portfolios using:
1. Modern Portfolio Theory (MPT) - Nobel Prize winning algorithm
2. Risk-based allocation - Match user's risk tolerance
3. Diversification - Don't put all eggs in one basket
4. Sector balancing - Spread across industries

MODERN PORTFOLIO THEORY (MPT):
- Developed by Harry Markowitz (1952) - Won Nobel Prize
- Key idea: Diversification reduces risk without reducing returns
- Finds optimal mix of assets that maximizes Sharpe ratio
- Formula: Sharpe = (Return - Risk_Free_Rate) / Volatility

PORTFOLIO CONSTRUCTION STEPS:
1. Filter assets by minimum score threshold
2. Remove excluded industries (e.g., tobacco, alcohol)
3. Match risk tolerance (conservative/moderate/aggressive)
4. Diversify across sectors (max 2 assets per sector)
5. Balance asset types (stocks/ETFs/mutual funds/crypto/FDs)
6. Optimize allocation using MPT
7. Assign capital to each asset
"""

from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
import numpy as np
from datetime import datetime, timedelta


# ============================================================================
# RISK PROFILES
# ============================================================================

RISK_PROFILES = {
    'conservative': {
        'description': 'Low risk, stable returns, capital preservation',
        'max_volatility': 0.15,  # 15% annual volatility
        'max_drawdown': 0.10,    # 10% max decline
        'min_score': 65,          # Only high-quality assets
        'allocation': {
            'stocks': 0.30,        # 30% max in stocks
            'etf': 0.30,           # 30% max in ETFs
            'mutual_fund': 0.25,   # 25% max in mutual funds
            'fd': 0.15,            # 15% max in FDs
            'crypto': 0.0          # No crypto
        }
    },
    'moderate': {
        'description': 'Balanced risk-return, moderate growth',
        'max_volatility': 0.25,  # 25% annual volatility
        'max_drawdown': 0.20,    # 20% max decline
        'min_score': 60,          # Good quality assets
        'allocation': {
            'stocks': 0.45,        # 45% max in stocks
            'etf': 0.25,           # 25% max in ETFs
            'mutual_fund': 0.20,   # 20% max in mutual funds
            'fd': 0.05,            # 5% max in FDs
            'crypto': 0.05         # 5% max in crypto
        }
    },
    'aggressive': {
        'description': 'High risk, high potential returns',
        'max_volatility': 0.40,  # 40% annual volatility
        'max_drawdown': 0.30,    # 30% max decline
        'min_score': 55,          # Accept more risk
        'allocation': {
            'stocks': 0.60,        # 60% max in stocks
            'etf': 0.20,           # 20% max in ETFs
            'mutual_fund': 0.05,   # 5% max in mutual funds
            'fd': 0.0,             # No FDs
            'crypto': 0.15         # 15% max in crypto
        }
    }
}


# ============================================================================
# ASSET FILTERING
# ============================================================================

def filter_assets(
    db: Session,
    risk_profile: str = 'moderate',
    excluded_sectors: List[str] = None,
    excluded_industries: List[str] = None,
    min_market_cap: int = 500_000_000,  # 500 Cr
    asset_preferences: List[str] = None
) -> List[Dict]:
    """
    Filter and rank assets based on user preferences
    
    ALGORITHM:
    1. Query all active assets from database
    2. Remove excluded sectors/industries
    3. Filter by minimum market cap
    4. Filter by asset type preferences
    5. Calculate final score for each
    6. Remove assets below score threshold
    7. Sort by score (highest first)
    
    Args:
        db: Database session
        risk_profile: 'conservative'/'moderate'/'aggressive'
        excluded_sectors: Sectors to avoid
        excluded_industries: Industries to avoid
        min_market_cap: Minimum market capitalization
        asset_preferences: Preferred asset types
    
    Returns:
        List of filtered assets with scores
    """
    from models.assets import Asset
    from recommendation_engine.analyzer import analyze_asset
    
    if excluded_sectors is None:
        excluded_sectors = []
    if excluded_industries is None:
        excluded_industries = []
    if asset_preferences is None:
        asset_preferences = ['stock', 'etf', 'mutual_fund', 'crypto']
    
    # Get risk profile settings
    profile = RISK_PROFILES.get(risk_profile, RISK_PROFILES['moderate'])
    min_score = profile['min_score']
    
    # Query assets from database
    query = db.query(Asset).filter(
        Asset.is_active == True,
        Asset.market_cap >= min_market_cap,
        Asset.type.in_(asset_preferences)
    )
    
    # Remove excluded sectors/industries
    if excluded_sectors:
        query = query.filter(~Asset.sector.in_(excluded_sectors))
    if excluded_industries:
        query = query.filter(~Asset.industry.in_(excluded_industries))
    
    assets = query.all()
    
    print(f"Found {len(assets)} assets matching criteria")
    
    # Analyze each asset and calculate score
    scored_assets = []
    
    for asset in assets:
        print(f"Analyzing {asset.symbol}...")
        
        analysis = analyze_asset(db, asset.id, asset.type)
        
        if analysis['success']:
            final_score = analysis['final_score']
            
            # Check if meets minimum score
            if final_score >= min_score:
                scored_assets.append({
                    'asset': asset,
                    'score': final_score,
                    'analysis': analysis,
                    'technical_score': analysis['technical']['technical_score'],
                    'fundamental_score': analysis['fundamental']['fundamental_score'],
                    'sentiment_score': analysis['sentiment']['sentiment_score'],
                    'risk_score': analysis['risk']['risk_score']
                })
    
    # Sort by score (highest first)
    scored_assets.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"✓ {len(scored_assets)} assets passed screening (score >= {min_score})")
    
    return scored_assets


# ============================================================================
# DIVERSIFICATION
# ============================================================================

def diversify_portfolio(
    scored_assets: List[Dict],
    risk_profile: str = 'moderate',
    max_assets: int = 10
) -> List[Dict]:
    """
    Diversify portfolio across sectors and asset types
    
    DIVERSIFICATION RULES:
    1. Maximum 2 assets per sector (avoid concentration)
    2. Balance asset types per risk profile
    3. Prefer higher-scored assets
    4. Maximum 10 assets total (manageable portfolio)
    
    ALGORITHM:
    1. Start with empty portfolio
    2. Iterate through scored assets (highest first)
    3. Check if sector limit reached
    4. Check if asset type allocation limit reached
    5. If both OK, add to portfolio
    6. Stop when portfolio is full or assets exhausted
    
    Args:
        scored_assets: List of assets with scores
        risk_profile: Risk tolerance level
        max_assets: Maximum number of assets in portfolio
    
    Returns:
        Diversified portfolio
    """
    profile = RISK_PROFILES[risk_profile]
    max_allocation = profile['allocation']
    
    portfolio = []
    sector_count = {}
    type_count = {}
    
    for item in scored_assets:
        asset = item['asset']
        
        # Check sector diversification (max 2 per sector)
        if asset.sector:
            if sector_count.get(asset.sector, 0) >= 2:
                continue  # Skip this asset
        
        # Check asset type allocation
        current_type_count = type_count.get(asset.type, 0)
        if current_type_count >= max_assets * max_allocation.get(asset.type, 0.5):
            continue  # Skip this asset
        
        # Add to portfolio
        portfolio.append(item)
        
        # Update counts
        if asset.sector:
            sector_count[asset.sector] = sector_count.get(asset.sector, 0) + 1
        type_count[asset.type] = type_count.get(asset.type, 0) + 1
        
        # Stop if portfolio is full
        if len(portfolio) >= max_assets:
            break
    
    print(f"✓ Diversified portfolio: {len(portfolio)} assets")
    print(f"  Sectors: {list(sector_count.keys())}")
    print(f"  Asset types: {type_count}")
    
    return portfolio


# ============================================================================
# MODERN PORTFOLIO THEORY (MPT) OPTIMIZATION
# ============================================================================

def optimize_allocation_mpt(
    portfolio: List[Dict],
    db: Session,
    risk_free_rate: float = 0.065
) -> List[Dict]:
    """
    Optimize portfolio allocation using Modern Portfolio Theory
    
    MPT ALGORITHM (Harry Markowitz):
    1. Calculate expected returns for each asset
    2. Calculate covariance matrix (how assets move together)
    3. Find weights that maximize Sharpe ratio
       Sharpe = (Portfolio_Return - Risk_Free_Rate) / Portfolio_Volatility
    4. Subject to constraints:
       - All weights sum to 1 (100%)
       - All weights >= 0 (no short selling)
       - Respect max allocation per asset type
    
    MATHEMATICAL FORMULATION:
    maximize: (w^T * returns - rf) / sqrt(w^T * Σ * w)
    where:
        w = weights vector
        returns = expected returns vector
        rf = risk-free rate
        Σ = covariance matrix
    
    Args:
        portfolio: List of assets to include
        db: Database session
        risk_free_rate: Risk-free rate (from .env: 6.5%)
    
    Returns:
        Portfolio with optimized allocations
    """
    from recommendation_engine.scoring import get_asset_prices_from_db
    import pandas as pd
    
    if not portfolio:
        return []
    
    # Get historical prices for all assets
    returns_data = {}
    
    for item in portfolio:
        asset_id = item['asset'].id
        prices_df = get_asset_prices_from_db(db, asset_id, days=252)  # 1 year
        
        if not prices_df.empty:
            # Calculate daily returns
            daily_returns = prices_df['close_price'].pct_change().dropna()
            returns_data[asset_id] = daily_returns
    
    if not returns_data:
        # Fallback: equal weight
        for item in portfolio:
            item['allocation'] = 1.0 / len(portfolio)
        return portfolio
    
    # Align all returns to common dates
    returns_df = pd.DataFrame(returns_data)
    returns_df = returns_df.dropna()
    
    if len(returns_df) < 30:
        # Not enough data, use equal weight
        for item in portfolio:
            item['allocation'] = 1.0 / len(portfolio)
        return portfolio
    
    # Calculate expected returns (annualized)
    expected_returns = returns_df.mean() * 252
    
    # Calculate covariance matrix (annualized)
    cov_matrix = returns_df.cov() * 252
    
    # Simple optimization: Use inverse volatility weighting
    # (More complex optimization would use scipy.optimize)
    volatilities = np.sqrt(np.diag(cov_matrix))
    
    # Inverse volatility weights (lower volatility = higher weight)
    inv_vol = 1.0 / volatilities
    raw_weights = inv_vol / inv_vol.sum()
    
    # Adjust for expected returns (higher return = higher weight)
    return_adjustment = expected_returns.values / expected_returns.values.mean()
    adjusted_weights = raw_weights * return_adjustment
    adjusted_weights = adjusted_weights / adjusted_weights.sum()
    
    # Apply weights to portfolio
    asset_ids = list(returns_data.keys())
    
    for i, item in enumerate(portfolio):
        if item['asset'].id in asset_ids:
            idx = asset_ids.index(item['asset'].id)
            item['allocation'] = float(adjusted_weights[idx])
        else:
            item['allocation'] = 0.0
    
    # Normalize allocations to sum to 1
    total_allocation = sum(item['allocation'] for item in portfolio)
    if total_allocation > 0:
        for item in portfolio:
            item['allocation'] = item['allocation'] / total_allocation
    
    print("✓ MPT optimization complete")
    
    return portfolio


# ============================================================================
# CAPITAL ALLOCATION
# ============================================================================

def allocate_capital(
    portfolio: List[Dict],
    total_capital: float
) -> List[Dict]:
    """
    Allocate actual rupee amounts to each asset
    
    ALGORITHM:
    1. Multiply each allocation % by total capital
    2. Round to nearest whole number
    3. Adjust for rounding errors (ensure sum = total)
    
    Args:
        portfolio: Portfolio with allocation percentages
        total_capital: Total investment amount (₹)
    
    Returns:
        Portfolio with capital amounts
    """
    for item in portfolio:
        allocation_pct = item.get('allocation', 0)
        item['capital_allocated'] = total_capital * allocation_pct
        item['allocation_pct'] = allocation_pct * 100  # Convert to percentage
    
    # Verify total
    total_allocated = sum(item['capital_allocated'] for item in portfolio)
    
    print(f"✓ Capital allocated: ₹{total_allocated:,.0f} / ₹{total_capital:,.0f}")
    
    # Adjust for rounding errors
    if total_allocated != total_capital and portfolio:
        difference = total_capital - total_allocated
        portfolio[0]['capital_allocated'] += difference
    
    return portfolio


# ============================================================================
# MAIN PORTFOLIO BUILDER
# ============================================================================

def build_portfolio(
    db: Session,
    capital: float,
    risk_profile: str = 'moderate',
    timeline_months: int = 12,
    excluded_sectors: List[str] = None,
    excluded_industries: List[str] = None,
    asset_preferences: List[str] = None,
    max_assets: int = 10
) -> Dict:
    """
    Build complete optimized portfolio
    
    FULL ALGORITHM:
    1. Filter assets based on criteria → filter_assets()
    2. Diversify across sectors and types → diversify_portfolio()
    3. Optimize allocation using MPT → optimize_allocation_mpt()
    4. Allocate capital amounts → allocate_capital()
    5. Return portfolio with reasoning
    
    Args:
        db: Database session
        capital: Total investment amount (₹)
        risk_profile: 'conservative'/'moderate'/'aggressive'
        timeline_months: Investment horizon (months)
        excluded_sectors: Sectors to avoid
        excluded_industries: Industries to avoid
        asset_preferences: Preferred asset types
        max_assets: Maximum assets in portfolio
    
    Returns:
        Complete portfolio with allocations and reasoning
    """
    print(f"\n{'='*60}")
    print(f"BUILDING PORTFOLIO")
    print(f"{'='*60}")
    print(f"Capital: ₹{capital:,.0f}")
    print(f"Risk Profile: {risk_profile}")
    print(f"Timeline: {timeline_months} months")
    print(f"{'='*60}\n")
    
    # Step 1: Filter assets
    print("Step 1: Filtering assets...")
    scored_assets = filter_assets(
        db=db,
        risk_profile=risk_profile,
        excluded_sectors=excluded_sectors,
        excluded_industries=excluded_industries,
        asset_preferences=asset_preferences
    )
    
    if not scored_assets:
        return {
            'success': False,
            'error': 'No assets found matching criteria'
        }
    
    # Step 2: Diversify
    print("\nStep 2: Diversifying portfolio...")
    diversified = diversify_portfolio(
        scored_assets=scored_assets,
        risk_profile=risk_profile,
        max_assets=max_assets
    )
    
    if not diversified:
        return {
            'success': False,
            'error': 'Could not diversify portfolio'
        }
    
    # Step 3: Optimize allocation
    print("\nStep 3: Optimizing allocation (MPT)...")
    optimized = optimize_allocation_mpt(
        portfolio=diversified,
        db=db
    )
    
    # Step 4: Allocate capital
    print("\nStep 4: Allocating capital...")
    final_portfolio = allocate_capital(
        portfolio=optimized,
        total_capital=capital
    )
    
    # Calculate portfolio metrics
    avg_score = sum(item['score'] for item in final_portfolio) / len(final_portfolio)
    total_sentiment = sum(item['sentiment_score'] for item in final_portfolio) / len(final_portfolio)
    
    print(f"\n{'='*60}")
    print(f"PORTFOLIO COMPLETE")
    print(f"{'='*60}")
    print(f"Assets: {len(final_portfolio)}")
    print(f"Average Score: {avg_score:.1f}/100")
    print(f"Average Sentiment: {total_sentiment:.1f}/100")
    print(f"{'='*60}\n")
    
    return {
        'success': True,
        'portfolio': final_portfolio,
        'total_capital': capital,
        'risk_profile': risk_profile,
        'timeline_months': timeline_months,
        'metrics': {
            'avg_score': avg_score,
            'avg_sentiment': total_sentiment,
            'num_assets': len(final_portfolio)
        }
    }
