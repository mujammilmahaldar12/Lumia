"""
LUMIA RECOMMENDATION ENGINE - Main Orchestrator

This is the entry point for the entire recommendation system.
It coordinates all modules to generate personalized investment recommendations.

ARCHITECTURE OVERVIEW:
┌─────────────────────────────────────────────────────────────────┐
│                      USER INPUT                                  │
│  (Capital, Risk, Timeline, Exclusions, Preferences)             │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RECOMMENDATION ENGINE                         │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  1. SCORING MODULE                                        │ │
│  │     - Technical Analysis (RSI, MACD, MA)                  │ │
│  │     - Fundamental Analysis (P/E, ROE, Debt)               │ │
│  │     - Risk Analysis (Beta, Volatility, Sharpe)            │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  2. ANALYZER MODULE                                       │ │
│  │     - FinBERT Sentiment Analysis                          │ │
│  │     - News Aggregation                                    │ │
│  │     - Data Collection                                     │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  3. PORTFOLIO MODULE                                      │ │
│  │     - Asset Filtering                                     │ │
│  │     - Diversification                                     │ │
│  │     - MPT Optimization                                    │ │
│  │     - Capital Allocation                                  │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  4. REASONING MODULE                                      │ │
│  │     - Generate WHY explanations                           │ │
│  │     - Risk warnings                                       │ │
│  │     - Expected outcomes                                   │ │
│  └───────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RECOMMENDATIONS OUTPUT                       │
│  - Portfolio composition                                         │
│  - Detailed reasoning for each asset                            │
│  - Risk warnings                                                 │
│  - Expected returns                                              │
└─────────────────────────────────────────────────────────────────┘
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime


class LumiaRecommendationEngine:
    """
    Main recommendation engine class
    
    This orchestrates all modules to generate investment recommendations.
    
    Usage:
        engine = LumiaRecommendationEngine(db_session)
        recommendations = engine.generate_recommendations(
            capital=100000,
            risk_profile='moderate',
            timeline_months=12
        )
    """
    
    def __init__(self, db: Session):
        """
        Initialize the recommendation engine
        
        Args:
            db: Database session
        """
        self.db = db
        self.finbert_analyzer = None
        
        # Lazy load FinBERT (only when needed)
        self._load_analyzer()
    
    def _load_analyzer(self):
        """Load FinBERT analyzer"""
        try:
            from recommendation_engine.analyzer import FinBERTAnalyzer
            print("Loading FinBERT analyzer...")
            self.finbert_analyzer = FinBERTAnalyzer()
        except Exception as e:
            print(f"Note: FinBERT not loaded ({e}). Using simple sentiment analysis.")
            self.finbert_analyzer = None
    
    def generate_recommendations(
        self,
        capital: float,
        risk_profile: str = 'moderate',
        timeline_months: int = 12,
        excluded_sectors: List[str] = None,
        excluded_industries: List[str] = None,
        asset_preferences: List[str] = None,
        max_assets: int = 10,
        generate_report: bool = True
    ) -> Dict:
        """
        Generate complete investment recommendations
        
        This is the main function that ties everything together.
        
        FULL ALGORITHM:
        1. Validate inputs
        2. Build portfolio using MPT
           a. Filter assets based on criteria
           b. Calculate scores for each (technical, fundamental, sentiment, risk)
           c. Diversify across sectors and asset types
           d. Optimize allocation using Modern Portfolio Theory
           e. Allocate capital amounts
        3. Generate reasoning for each recommendation
        4. Create comprehensive report
        5. Return recommendations
        
        Args:
            capital: Total investment amount (₹)
            risk_profile: 'conservative', 'moderate', or 'aggressive'
            timeline_months: Investment horizon in months
            excluded_sectors: List of sectors to avoid (e.g., ['Tobacco', 'Alcohol'])
            excluded_industries: List of industries to avoid
            asset_preferences: Preferred asset types (e.g., ['stock', 'etf'])
            max_assets: Maximum number of assets in portfolio
            generate_report: Whether to generate full text report
        
        Returns:
            {
                'success': True/False,
                'portfolio': [...],  # List of recommended assets with allocations
                'report': '...',     # Full text report (if generate_report=True)
                'summary': {...},    # Portfolio summary metrics
                'timestamp': '...'   # When recommendations were generated
            }
        """
        print("\n" + "="*70)
        print("LUMIA RECOMMENDATION ENGINE")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
        # Validate inputs
        if not self._validate_inputs(capital, risk_profile, timeline_months):
            return {
                'success': False,
                'error': 'Invalid inputs',
                'timestamp': datetime.now().isoformat()
            }
        
        # Build portfolio
        from recommendation_engine.portfolio import build_portfolio
        
        portfolio_result = build_portfolio(
            db=self.db,
            capital=capital,
            risk_profile=risk_profile,
            timeline_months=timeline_months,
            excluded_sectors=excluded_sectors,
            excluded_industries=excluded_industries,
            asset_preferences=asset_preferences,
            max_assets=max_assets
        )
        
        if not portfolio_result['success']:
            return {
                'success': False,
                'error': portfolio_result.get('error', 'Portfolio building failed'),
                'timestamp': datetime.now().isoformat()
            }
        
        # Generate report if requested
        report = None
        if generate_report:
            from recommendation_engine.reasoning import generate_complete_report
            print("\nGenerating detailed report...")
            report = generate_complete_report(portfolio_result)
            print("✓ Report generated")
        
        # Prepare response
        response = {
            'success': True,
            'portfolio': portfolio_result['portfolio'],
            'summary': {
                'total_capital': portfolio_result['total_capital'],
                'risk_profile': portfolio_result['risk_profile'],
                'timeline_months': portfolio_result['timeline_months'],
                'num_assets': portfolio_result['metrics']['num_assets'],
                'avg_score': portfolio_result['metrics']['avg_score'],
                'avg_sentiment': portfolio_result['metrics']['avg_sentiment']
            },
            'report': report,
            'timestamp': datetime.now().isoformat()
        }
        
        print("\n" + "="*70)
        print("✓ RECOMMENDATIONS COMPLETE")
        print("="*70)
        print(f"Generated {len(portfolio_result['portfolio'])} recommendations")
        print(f"Average score: {portfolio_result['metrics']['avg_score']:.1f}/100")
        print("="*70 + "\n")
        
        return response
    
    def _validate_inputs(
        self,
        capital: float,
        risk_profile: str,
        timeline_months: int
    ) -> bool:
        """
        Validate user inputs
        
        Args:
            capital: Investment amount
            risk_profile: Risk tolerance
            timeline_months: Investment timeline
        
        Returns:
            True if valid, False otherwise
        """
        # Check capital
        if capital <= 0:
            print("❌ Error: Capital must be positive")
            return False
        
        if capital < 10000:
            print("⚠️ Warning: Capital is very low (< ₹10,000)")
        
        # Check risk profile
        valid_profiles = ['conservative', 'moderate', 'aggressive']
        if risk_profile not in valid_profiles:
            print(f"❌ Error: Invalid risk profile. Must be one of: {valid_profiles}")
            return False
        
        # Check timeline
        if timeline_months <= 0:
            print("❌ Error: Timeline must be positive")
            return False
        
        if timeline_months < 6:
            print("⚠️ Warning: Very short timeline (< 6 months). Consider longer-term investment.")
        
        return True
    
    def get_asset_analysis(self, asset_id: int, asset_type: str = 'stock') -> Dict:
        """
        Get detailed analysis for a single asset
        
        Useful for analyzing individual stocks/assets before adding to portfolio.
        
        Args:
            asset_id: Database ID of the asset
            asset_type: Type of asset ('stock', 'etf', etc.)
        
        Returns:
            Complete analysis with all scores
        """
        from recommendation_engine.analyzer import analyze_asset
        from recommendation_engine.reasoning import generate_asset_reasoning
        
        analysis = analyze_asset(self.db, asset_id, asset_type)
        
        if analysis['success']:
            # Get asset details
            from models.assets import Asset
            asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
            
            # Prepare data for reasoning
            asset_data = {
                'asset': asset,
                'score': analysis['final_score'],
                'analysis': analysis,
                'allocation_pct': 100,  # For single asset analysis
                'capital_allocated': 0
            }
            
            # Generate reasoning
            reasoning = generate_asset_reasoning(asset_data)
            
            analysis['reasoning'] = reasoning
        
        return analysis
    
    def compare_assets(self, asset_ids: List[int]) -> Dict:
        """
        Compare multiple assets side-by-side
        
        Args:
            asset_ids: List of asset IDs to compare
        
        Returns:
            Comparison data with scores for each asset
        """
        from recommendation_engine.analyzer import analyze_asset
        from models.assets import Asset
        
        comparisons = []
        
        for asset_id in asset_ids:
            asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
            
            if not asset:
                continue
            
            analysis = analyze_asset(self.db, asset_id, asset.type)
            
            if analysis['success']:
                comparisons.append({
                    'symbol': asset.symbol,
                    'name': asset.name,
                    'type': asset.type,
                    'final_score': analysis['final_score'],
                    'technical_score': analysis['technical']['technical_score'],
                    'fundamental_score': analysis['fundamental']['fundamental_score'],
                    'sentiment_score': analysis['sentiment']['sentiment_score'],
                    'risk_score': analysis['risk']['risk_score']
                })
        
        # Sort by final score
        comparisons.sort(key=lambda x: x['final_score'], reverse=True)
        
        return {
            'success': True,
            'comparisons': comparisons,
            'winner': comparisons[0] if comparisons else None
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_recommendations(
    db: Session,
    capital: float,
    risk_profile: str = 'moderate',
    **kwargs
) -> Dict:
    """
    Quick function to get recommendations
    
    Args:
        db: Database session
        capital: Investment amount
        risk_profile: Risk tolerance
        **kwargs: Additional parameters
    
    Returns:
        Recommendations dictionary
    """
    engine = LumiaRecommendationEngine(db)
    return engine.generate_recommendations(
        capital=capital,
        risk_profile=risk_profile,
        **kwargs
    )


def analyze_single_asset(db: Session, asset_id: int, asset_type: str = 'stock') -> Dict:
    """
    Quick function to analyze a single asset
    
    Args:
        db: Database session
        asset_id: Asset ID
        asset_type: Asset type
    
    Returns:
        Analysis dictionary
    """
    engine = LumiaRecommendationEngine(db)
    return engine.get_asset_analysis(asset_id, asset_type)
