"""
Lumia Recommendation Engine

A professional-grade investment recommendation system powered by AI.

Features:
- Technical Analysis (RSI, MACD, Moving Averages)
- Fundamental Analysis (P/E, ROE, Debt Ratios)
- AI Sentiment Analysis (FinBERT)
- Risk Analysis (Beta, Volatility, Sharpe Ratio)
- Modern Portfolio Theory (MPT) Optimization
- Multi-Asset Support (Stocks, ETFs, Mutual Funds, Crypto, FDs)
- Detailed Reasoning & Explanations

Usage:
    from database import get_db
    from recommendation_engine import get_recommendations
    
    db = next(get_db())
    
    recommendations = get_recommendations(
        db=db,
        capital=100000,
        risk_profile='moderate',
        timeline_months=12
    )
    
    print(recommendations['report'])
"""

from recommendation_engine.engine import (
    LumiaRecommendationEngine,
    get_recommendations,
    analyze_single_asset
)

from recommendation_engine.portfolio import (
    build_portfolio,
    RISK_PROFILES
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
