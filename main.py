"""
Lumia Asset Screener - Full Database Analysis
==============================================

Analyzes ALL assets (stocks, ETFs, mutual funds, etc.) in database 
and provides expert recommendations.

Professional tool for portfolio management.

Usage:
    # Analyze individual assets
    python main.py                          # Analyze all assets
    python main.py --risk moderate          # Filter by risk profile
    python main.py --action BUY             # Show only BUY recommendations
    python main.py --top 10                 # Show top 10 recommendations
    python main.py --type stock             # Analyze only stocks
    python main.py --type all               # Analyze all asset types
    
    # FinRobot-style Portfolio Allocation (NEW!)
    python main.py --portfolio --capital 100000 --risk-pct 30
    python main.py --portfolio --capital 100000 --risk-pct 30 --exclude-sectors Tobacco,Alcohol
"""

import sys
import argparse
from typing import List, Dict
import logging

from database import SessionLocal
from models import Asset
from recommendation_engine import ExpertRecommendationEngine, FinRobotPortfolio, display_portfolio

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s'
)

def analyze_all_stocks(
    risk_profile: str = 'moderate',
    filter_action: str = None,
    top_n: int = None,
    asset_type: str = 'stock'
) -> List[Dict]:
    """
    Analyze all assets in database
    
    Args:
        risk_profile: 'conservative', 'moderate', or 'aggressive'
        filter_action: Filter by 'BUY', 'SELL', or 'HOLD'
        top_n: Return only top N recommendations by score
        asset_type: 'stock', 'etf', 'crypto', 'mutual_fund', or 'all'
    
    Returns:
        List of recommendations sorted by score
    """
    db = SessionLocal()
    engine = ExpertRecommendationEngine()
    
    # Get all assets
    query = db.query(Asset)
    if asset_type != 'all':
        query = query.filter(Asset.type == asset_type.lower())  # Types are lowercase in DB
    
    assets = query.all()
    total = len(assets)
    
    asset_label = "ALL assets" if asset_type == 'all' else f"{asset_type} assets"
    
    print(f"\n{'='*120}")
    print(f"LUMIA ASSET SCREENER - Analyzing {total} {asset_label}")
    print(f"Risk Profile: {risk_profile.upper()}")
    print(f"{'='*120}\n")
    
    results = []
    
    # Analyze each asset
    for i, asset in enumerate(assets, 1):
        try:
            # Pass db session to prevent creating new session for each asset
            result = engine.analyze_stock(asset.symbol, risk_profile, db_session=db)
            
            rec = result['recommendation']
            scores = result['scores']
            
            # Filter by action if specified
            if filter_action and rec['action'] != filter_action:
                continue
            
            results.append({
                'symbol': asset.symbol,
                'name': asset.name,
                'type': asset.type,
                'action': rec['action'],
                'score': rec['overall_score'],
                'confidence': rec['confidence'],
                'price': result.get('current_price', 0),
                'technical': scores['technical'],
                'fundamental': scores['fundamental'],
                'sentiment': scores['sentiment'],
                'risk': scores['risk'],
                'target': result.get('targets', {}).get('target'),
                'stop_loss': result.get('targets', {}).get('stop_loss')
            })
            
            # Progress indicator
            if i % 100 == 0 or i == total:
                print(f"Progress: {i}/{total} assets analyzed...", end='\r')
        
        except Exception as e:
            logging.debug(f"Error analyzing {asset.symbol}: {e}")
            continue
    
    db.close()
    
    # Sort by score (descending)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Limit to top N if specified
    if top_n:
        results = results[:top_n]
    
    return results


def display_results(results: List[Dict], show_details: bool = True):
    """Display results in a formatted table"""
    
    if not results:
        print("\n⚠️  No assets match your criteria.\n")
        return
    
    print(f"\n\n{'='*120}")
    print(f"ANALYSIS RESULTS - {len(results)} Recommendations")
    print(f"{'='*120}\n")
    
    # Summary statistics
    buy_count = sum(1 for r in results if r['action'] == 'BUY')
    sell_count = sum(1 for r in results if r['action'] == 'SELL')
    hold_count = sum(1 for r in results if r['action'] == 'HOLD')
    
    print(f"📊 SUMMARY:")
    print(f"   BUY:  {buy_count} assets ({buy_count/len(results)*100:.1f}%)")
    print(f"   SELL: {sell_count} assets ({sell_count/len(results)*100:.1f}%)")
    print(f"   HOLD: {hold_count} assets ({hold_count/len(results)*100:.1f}%)")
    print()
    
    # Table header
    if show_details:
        print(f"{'#':<4} {'Symbol':<15} {'Company':<30} {'Type':<8} {'Action':<6} {'Score':<7} "
              f"{'Tech':<6} {'Fund':<6} {'Sent':<6} {'Risk':<6}")
        print(f"{'-'*120}")
        
        # Table rows
        for i, r in enumerate(results, 1):
            print(f"{i:<4} {r['symbol']:<15} {r['name'][:28]:<30} {r.get('type', 'N/A'):<8} {r['action']:<6} "
                  f"{r['score']:>6.1f} "
                  f"{r['technical']:>5.1f} {r['fundamental']:>5.1f} "
                  f"{r['sentiment']:>5.1f} {r['risk']:>5.1f}")
    else:
        print(f"{'#':<4} {'Symbol':<15} {'Company':<35} {'Type':<8} {'Action':<6} {'Score':<7} {'Confidence':<10}")
        print(f"{'-'*110}")
        
        for i, r in enumerate(results, 1):
            print(f"{i:<4} {r['symbol']:<15} {r['name'][:33]:<35} {r.get('type', 'N/A'):<8} {r['action']:<6} "
                  f"{r['score']:>6.1f} {r['confidence']:>9.1f}%")
    
    print(f"\n{'='*120}\n")


def display_top_picks(results: List[Dict], n: int = 5):
    """Display top N recommendations with details"""
    
    if not results:
        return
    
    top_buys = [r for r in results if r['action'] == 'BUY'][:n]
    
    if not top_buys:
        print("ℹ️  No BUY recommendations found.\n")
        return
    
    print(f"{'='*120}")
    print(f"🎯 TOP {len(top_buys)} BUY RECOMMENDATIONS")
    print(f"{'='*120}\n")
    
    for i, r in enumerate(top_buys, 1):
        upside = ((r['target'] - r['price']) / r['price'] * 100) if r['target'] and r['price'] else 0
        
        print(f"{i}. {r['symbol']} - {r['name']}")
        print(f"   Current Price: ₹{r['price']:.2f}")
        print(f"   Recommendation: {r['action']} (Score: {r['score']:.1f}/100, Confidence: {r['confidence']:.1f}%)")
        print(f"   Category Scores: Tech={r['technical']:.1f}, Fund={r['fundamental']:.1f}, "
              f"Sent={r['sentiment']:.1f}, Risk={r['risk']:.1f}")
        
        if r['target']:
            print(f"   Target: ₹{r['target']:.2f} ({upside:+.1f}% upside)")
        if r['stop_loss']:
            print(f"   Stop Loss: ₹{r['stop_loss']:.2f}")
        print()
    
    print(f"{'='*120}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Lumia Asset Screener - Professional Portfolio Analysis'
    )
    
    parser.add_argument(
        '--portfolio',
        action='store_true',
        help='Generate FinRobot-style portfolio allocation'
    )
    
    parser.add_argument(
        '--capital',
        type=float,
        help='Total investment capital (required with --portfolio)'
    )
    
    parser.add_argument(
        '--risk-pct',
        type=int,
        help='Risk appetite percentage 0-100 (required with --portfolio)'
    )
    
    parser.add_argument(
        '--exclude-sectors',
        help='Comma-separated list of sectors to exclude'
    )
    
    parser.add_argument(
        '--exclude-industries',
        help='Comma-separated list of industries to exclude'
    )
    
    parser.add_argument(
        '--risk',
        choices=['conservative', 'moderate', 'aggressive'],
        default='moderate',
        help='Risk profile (default: moderate)'
    )
    
    parser.add_argument(
        '--action',
        choices=['BUY', 'SELL', 'HOLD'],
        help='Filter by recommendation action'
    )
    
    parser.add_argument(
        '--top',
        type=int,
        help='Show only top N recommendations'
    )
    
    parser.add_argument(
        '--type',
        choices=['stock', 'etf', 'crypto', 'mutual_fund', 'all'],
        default='all',
        help='Asset type to analyze (default: all)'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed scores for all categories'
    )
    
    parser.add_argument(
        '--export',
        help='Export results to CSV file'
    )
    
    args = parser.parse_args()
    
    # Handle portfolio generation
    if args.portfolio:
        if not args.capital or not args.risk_pct:
            print("ERROR: --capital and --risk-pct are required with --portfolio")
            print("Example: python main.py --portfolio --capital 100000 --risk-pct 30")
            sys.exit(1)
        
        # Parse exclusions
        exclude_sectors = None
        if args.exclude_sectors:
            exclude_sectors = [s.strip() for s in args.exclude_sectors.split(',')]
        
        exclude_industries = None
        if args.exclude_industries:
            exclude_industries = [i.strip() for i in args.exclude_industries.split(',')]
        
        # Generate portfolio
        allocator = FinRobotPortfolio()
        portfolio = allocator.build_portfolio(
            total_capital=args.capital,
            risk_appetite=args.risk_pct,
            exclude_sectors=exclude_sectors,
            exclude_industries=exclude_industries
        )
        
        # Display portfolio
        display_portfolio(portfolio)
        
        return
    
    # Run standard analysis
    results = analyze_all_stocks(
        risk_profile=args.risk,
        filter_action=args.action,
        top_n=args.top,
        asset_type=args.type
    )
    
    # Display results
    display_results(results, show_details=args.detailed)
    
    # Show top picks
    if not args.action and len(results) > 5:
        display_top_picks(results, n=5)
    
    # Export if requested
    if args.export:
        import csv
        with open(args.export, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"✅ Results exported to {args.export}\n")


if __name__ == "__main__":
    main()
