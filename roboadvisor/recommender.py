# roboadvisor/recommender.py
"""
ROBO-ADVISOR RECOMMENDATION ENGINE
Main orchestration module that brings everything together
"""

import numpy as np
from typing import Dict, List
from sqlalchemy.orm import Session

from .user_profile import UserProfile, RiskType
from .portfolio_strategy import asset_allocation, calculate_portfolio_metrics, get_sector_diversification
from .asset_selector import select_top_assets
from .optimizer import optimize_portfolio, calculate_var

def generate_recommendation(
    db: Session,
    profile: UserProfile,
    optimize: bool = True
) -> Dict:
    """
    Generate comprehensive investment recommendation
    
    Args:
        db: Database session
        profile: User investment profile
        optimize: Whether to run portfolio optimization
    
    Returns:
        Complete recommendation with allocation, metrics, and reasoning
    """
    
    print("\n🔬 ANALYZING MARKET DATA...")
    print("="*70)
    
    # STEP 1: Get strategic asset allocation (now using expected_return!)
    allocation_percentages = asset_allocation(
        profile.risk_type, 
        profile.years,
        expected_return=profile.expected_return  # 🔥 NOW USED!
    )
    
    # Apply user exclusions
    for excluded in profile.exclusions:
        if excluded in allocation_percentages:
            del allocation_percentages[excluded]
    
    # Renormalize after exclusions
    total = sum(allocation_percentages.values())
    if total > 0:
        allocation_percentages = {k: v/total for k, v in allocation_percentages.items()}
    
    print(f"\n📊 Strategic Allocation ({profile.risk_type.value.title()}):")
    for asset_type, percentage in allocation_percentages.items():
        print(f"   {asset_type.title()}: {percentage*100:.1f}%")
    
    # STEP 2: Select specific assets within each category
    print("\n\n🎯 SELECTING OPTIMAL ASSETS...")
    print("="*70)
    
    sector_div = get_sector_diversification(profile.risk_type)
    portfolio = {}
    all_selected_assets = []
    
    for asset_type, percentage in allocation_percentages.items():
        if percentage == 0:
            continue
        
        print(f"\n{asset_type.title()}:")
        
        # 🔥 CRITICAL FIX: Normalize asset_type to match database
        # Portfolio strategy uses: "stocks", "mutual_funds"
        # Database uses: "stock", "mutual_fund"
        db_asset_type = asset_type.rstrip('s')  # Remove trailing 's'
        if db_asset_type == 'mutual_fund':
            db_asset_type = 'mutual_fund'  # Already correct
        
        print(f"   [DEBUG NORMALIZE] '{asset_type}' → '{db_asset_type}'")
        
        # Determine number of assets to select
        if asset_type == 'crypto':
            n_assets = min(3, max(1, int(5 * percentage)))
        elif asset_type == 'mutual_funds':
            n_assets = min(5, max(2, int(10 * percentage)))
        else:
            n_assets = min(8, max(3, int(15 * percentage)))
        
        # Select top assets with appropriate minimum score thresholds
        # Lower thresholds to work with current data (many assets score 50-60)
        # 🔥 SPECIAL: Even lower thresholds for stocks/mutual_funds (data quality issues)
        if profile.risk_type == RiskType.VERY_AGGRESSIVE:
            min_score = 45.0  # Most aggressive
        elif profile.risk_type == RiskType.AGGRESSIVE:
            min_score = 48.0  # Moderately aggressive
        elif profile.risk_type == RiskType.MODERATE:
            min_score = 50.0  # Balanced
        else:  # CONSERVATIVE
            min_score = 52.0  # More selective
        
        # Further reduce threshold for stocks and mutual funds (incomplete data)
        # 🔥 NOTE: asset_type might be 'mutual_funds' (underscore!) not 'mutual-funds'
        if db_asset_type in ['stock', 'mutual_fund']:
            min_score = max(45.0, min_score - 5.0)  # 5 points lower
            print(f"   [DEBUG] Reduced threshold: {db_asset_type} → {min_score:.1f}")
        
        # Debug: Show what we're requesting
        print(f"   [DEBUG] Requesting {n_assets} assets with min_score={min_score:.1f}, db_asset_type='{db_asset_type}'")
        
        selected = select_top_assets(
            db,
            db_asset_type,  # 🔥 Use normalized type!
            limit=n_assets,
            min_score=min_score,
            sector_diversification=sector_div if db_asset_type == 'stock' else None
        )
        
        print(f"   [DEBUG] Received {len(selected)} assets")
        
        if not selected:
            print(f"   ⚠️  No {asset_type} found meeting criteria")
            continue
        
        # Calculate allocation amount
        category_amount = profile.capital * percentage
        
        # Distribute equally among selected assets
        per_asset_amount = category_amount / len(selected)
        
        portfolio[asset_type] = []
        for item in selected:
            asset_data = {
                "symbol": item["symbol"],
                "name": item["name"],
                "allocation_amount": per_asset_amount,
                "allocation_percentage": percentage / len(selected),
                "score": item["score"],
                "breakdown": item["breakdown"],
                "sector": item.get("sector", "N/A")
            }
            portfolio[asset_type].append(asset_data)
            all_selected_assets.append(asset_data)
            
            print(f"   ✓ {item['symbol']}: Score {item['score']:.1f}/100 - ₹{per_asset_amount:,.0f} ({percentage/len(selected)*100:.1f}%)")
    
    # STEP 3: Calculate portfolio metrics
    print("\n\n⚙️  CALCULATING PORTFOLIO METRICS...")
    print("="*70)
    
    # Use estimates for portfolio metrics
    portfolio_metrics = calculate_portfolio_metrics(
        allocation_percentages,
        {
            'stocks': 0.15,
            'etf': 0.12,
            'mutual_funds': 0.11,
            'crypto': 0.25,
            'bonds': 0.06
        }
    )
    
    print(f"✓ Metrics calculated")
    print(f"  Expected Return: {portfolio_metrics['expected_return']*100:.2f}%")
    print(f"  Expected Risk: {portfolio_metrics['expected_risk']*100:.2f}%")
    print(f"  Sharpe Ratio: {portfolio_metrics['sharpe_ratio']:.2f}")
    
    # STEP 4: Generate summary and reasoning
    summary = generate_summary(profile, portfolio, portfolio_metrics)
    
    return {
        "profile": profile.to_dict(),
        "summary": summary,
        "portfolio": portfolio,
        "metrics": portfolio_metrics,
        "total_assets": len(all_selected_assets),
        "asset_types_count": len(portfolio)
    }

def generate_summary(profile: UserProfile, portfolio: Dict, metrics: Dict) -> str:
    """Generate human-readable investment summary"""
    
    risk_description = {
        RiskType.CONSERVATIVE: "stable and low-risk",
        RiskType.MODERATE: "balanced with moderate risk",
        RiskType.AGGRESSIVE: "growth-focused with higher risk",
        RiskType.VERY_AGGRESSIVE: "maximum growth with high volatility"
    }
    
    goal_description = {
        "wealth": "wealth creation",
        "growth": "capital growth",
        "retirement": "retirement planning",
        "income": "income generation"
    }
    
    summary = f"""
    Your {risk_description[profile.risk_type]} portfolio has been created for {profile.years}-year 
    {goal_description.get(profile.investment_goal, 'investment')} with a capital of ₹{profile.capital:,.0f}.
    
    Expected Performance:
    - Annual Return: {metrics['expected_return']*100:.2f}%
    - Portfolio Risk: {metrics['expected_risk']*100:.2f}%
    - Risk-Adjusted Return (Sharpe): {metrics['sharpe_ratio']:.2f}
    
    Your portfolio is diversified across {len(portfolio)} asset classes with {sum(len(items) for items in portfolio.values())} 
    carefully selected investments based on fundamentals, technical analysis, and market sentiment.
    """
    
    return summary.strip()
