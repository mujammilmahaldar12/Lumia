"""
Lumia Recommendation Engine

A professional-grade investment recommendation system powered by AI.

NEW EXPERT ENGINE (RECOMMENDED):
- Technical Analysis (25%)
- Fundamental Analysis (30%) 
- AI Sentiment Analysis (25%)
- Risk Assessment (20%)

OLD SYSTEM (LEGACY):
- Multi-asset portfolio optimization
- Modern Portfolio Theory (MPT)
- Detailed asset-level analysis

Usage (NEW - Single Stock Recommendation):
    from recommendation_engine import get_recommendation
    
    result = get_recommendation('TCS.NS', 'moderate', news_headlines)
    print(result['recommendation']['action'])  # BUY/SELL/HOLD
    print(result['reasoning'])

Usage (OLD - Portfolio Optimization):
    from recommendation_engine.engine import get_recommendations
    
    recommendations = get_recommendations(
        db=db,
        capital=100000,
        risk_profile='moderate',
        timeline_months=12
    )
"""

# NEW Expert System
from recommendation_engine.expert_engine import (
    get_recommendation,
    ExpertRecommendationEngine
)

# OLD Legacy System
from recommendation_engine.engine import (
    LumiaRecommendationEngine,
    get_recommendations,
    analyze_single_asset
)

from recommendation_engine.portfolio import (
    FinRobotPortfolio,
    display_portfolio
)

from recommendation_engine.analyzer import (
    FinBERTAnalyzer,
    calculate_sentiment_score
)

from recommendation_engine.scoring import (
    calculate_technical_score,
    calculate_fundamental_score_stock,
    calculate_fundamental_score_etf,
    calculate_risk_score
)

from recommendation_engine.reasoning import (
    generate_asset_reasoning,
    generate_portfolio_summary,
    generate_complete_report
)


__all__ = [
    # Main engine
    'LumiaRecommendationEngine',
    'get_recommendations',
    'analyze_single_asset',
    
    # Portfolio
    'build_portfolio',
    'RISK_PROFILES',
    
    # Analyzer
    'FinBERTAnalyzer',
    'calculate_sentiment_score',
    
    # Scoring
    'calculate_technical_score',
    'calculate_fundamental_score_stock',
    'calculate_fundamental_score_etf',
    'calculate_risk_score',
    
    # Reasoning
    'generate_asset_reasoning',
    'generate_portfolio_summary',
    'generate_complete_report'
]

__version__ = '1.0.0'
__author__ = 'Lumia Team'
