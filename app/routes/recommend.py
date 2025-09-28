"""Recommendation API endpoint for portfolio optimization."""

import logging
from datetime import date, timedelta, datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from database import SessionLocal
from models import Asset, AssetDailySignals, DailyPrice, QuarterlyFundamental
from models.news_article import NewsArticle
from models.news_sentiment import NewsSentiment

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response models
class RecommendationRequest(BaseModel):
    capital: float = Field(..., gt=0, description="Total investment capital")
    risk: float = Field(..., ge=0, le=1, description="Risk tolerance (0=Conservative, 1=Aggressive)")
    horizon_years: int = Field(..., gt=0, le=50, description="Investment horizon in years")
    exclusions: List[str] = Field(default=[], description="List of asset symbols to exclude")

class AssetRecommendation(BaseModel):
    symbol: str
    name: str
    allocated: float
    percentage: float
    score: float
    breakdown: Dict[str, float]

class RecommendationBuckets(BaseModel):
    stocks: List[AssetRecommendation]
    etfs: List[AssetRecommendation]

class RecommendationResponse(BaseModel):
    buckets: RecommendationBuckets
    total_allocated: float
    explanation_text: str


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RecommendationEngine:
    """Portfolio recommendation engine with risk-based scoring."""
    
    # Risk-based weight presets
    WEIGHT_PRESETS = {
        'conservative': {  # Risk 0.0-0.33
            'sentiment': 0.15,
            'fundamental': 0.40,
            'momentum': 0.20,
            'volatility': 0.25  # Lower volatility preferred
        },
        'balanced': {  # Risk 0.34-0.66
            'sentiment': 0.25,
            'fundamental': 0.30,
            'momentum': 0.30,
            'volatility': 0.15
        },
        'aggressive': {  # Risk 0.67-1.0
            'sentiment': 0.35,
            'fundamental': 0.20,
            'momentum': 0.35,
            'volatility': 0.10
        }
    }
    
    def __init__(self, db: Session):
        """Initialize recommendation engine."""
        self.db = db
    
    def get_risk_profile(self, risk: float) -> str:
        """Get risk profile name from risk score."""
        if risk <= 0.33:
            return 'conservative'
        elif risk <= 0.66:
            return 'balanced'
        else:
            return 'aggressive'
    
    def build_universe(self, exclusions: List[str]) -> List[Dict[str, Any]]:
        """
        Build investment universe with latest signals and fundamental data.
        
        Args:
            exclusions: List of symbols to exclude
            
        Returns:
            List of asset dictionaries with computed metrics
        """
        # Get recent date for signals
        recent_date = date.today() - timedelta(days=1)  # Yesterday's data
        
        # Base query for active assets with recent signals
        query = self.db.query(
            Asset.id,
            Asset.symbol,
            Asset.name,
            Asset.type,
            Asset.market_cap,
            AssetDailySignals.avg_sentiment,
            AssetDailySignals.sentiment_30d_avg,
            AssetDailySignals.return_30d,
            AssetDailySignals.return_365d,
            AssetDailySignals.volatility_30d,
            AssetDailySignals.fundamental_score
        ).join(
            AssetDailySignals,
            and_(
                AssetDailySignals.asset_id == Asset.id,
                AssetDailySignals.date >= recent_date - timedelta(days=7)  # Within last week
            )
        ).filter(
            Asset.is_active == True,
            Asset.type.in_(['stock', 'etf', 'mutual_fund'])
        )
        
        # Exclude specified symbols
        if exclusions:
            query = query.filter(~Asset.symbol.in_(exclusions))
        
        # Get latest signals for each asset (in case of multiple dates)
        results = query.order_by(Asset.id, desc(AssetDailySignals.date)).all()
        
        # Process results into universe
        universe = []
        seen_assets = set()
        
        for row in results:
            if row.id in seen_assets:
                continue
            seen_assets.add(row.id)
            
            # Calculate derived metrics
            expected_return = self._calculate_expected_return(
                row.return_30d, row.return_365d, row.sentiment_30d_avg
            )
            
            universe.append({
                'asset_id': row.id,
                'symbol': row.symbol,
                'name': row.name,
                'type': row.type,
                'market_cap': row.market_cap or 0,
                'expected_return': expected_return,
                'volatility': row.volatility_30d or 0.2,  # Default volatility if missing
                'sentiment': row.sentiment_30d_avg or 0.0,
                'fundamental_score': row.fundamental_score or 0.5,
                'momentum': row.return_30d or 0.0
            })
        
        logger.info(f"Built universe with {len(universe)} assets")
        return universe
    
    def _calculate_expected_return(self, return_30d: Optional[float], 
                                 return_365d: Optional[float], 
                                 sentiment: Optional[float]) -> float:
        """
        Calculate expected return based on historical returns and sentiment.
        
        This is a simplified model - in practice you'd use more sophisticated methods.
        """
        expected_return = 0.0
        
        # Base return from historical data
        if return_365d is not None:
            expected_return += return_365d * 0.6  # 60% weight on annual return
        
        if return_30d is not None:
            expected_return += return_30d * 0.3  # 30% weight on monthly return (annualized)
        
        # Sentiment adjustment
        if sentiment is not None:
            expected_return += sentiment * 0.1  # 10% sentiment boost/penalty
        
        return expected_return
    
    def normalize_signals(self, universe: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize signals to 0-1 range for fair comparison.
        """
        if not universe:
            return universe
        
        # Extract values for normalization
        sentiments = [asset.get('sentiment', 0.0) for asset in universe]
        fundamentals = [asset.get('fundamental_score', 0.5) for asset in universe]
        momentums = [asset.get('momentum', 0.0) for asset in universe]
        volatilities = [asset.get('volatility', 0.2) for asset in universe]
        
        # Calculate ranges (avoid division by zero)
        sentiment_range = max(sentiments) - min(sentiments) if max(sentiments) != min(sentiments) else 1.0
        fundamental_range = max(fundamentals) - min(fundamentals) if max(fundamentals) != min(fundamentals) else 1.0
        momentum_range = max(momentums) - min(momentums) if max(momentums) != min(momentums) else 1.0
        volatility_range = max(volatilities) - min(volatilities) if max(volatilities) != min(volatilities) else 1.0
        
        # Normalize each asset
        for asset in universe:
            # Sentiment: higher is better (0-1)
            asset['sentiment_normalized'] = (asset.get('sentiment', 0.0) - min(sentiments)) / sentiment_range
            
            # Fundamental: higher is better (0-1)
            asset['fundamental_normalized'] = (asset.get('fundamental_score', 0.5) - min(fundamentals)) / fundamental_range
            
            # Momentum: higher is better (0-1)
            asset['momentum_normalized'] = (asset.get('momentum', 0.0) - min(momentums)) / momentum_range
            
            # Volatility: lower is better, so invert (0-1 where 1 is low volatility)
            asset['volatility_normalized'] = 1.0 - ((asset.get('volatility', 0.2) - min(volatilities)) / volatility_range)
        
        return universe
    
    def compute_scores(self, universe: List[Dict[str, Any]], risk_profile: str) -> List[Dict[str, Any]]:
        """
        Compute weighted scores for each asset based on risk profile.
        """
        weights = self.WEIGHT_PRESETS[risk_profile]
        
        for asset in universe:
            # Calculate weighted score
            score = (
                weights['sentiment'] * asset.get('sentiment_normalized', 0.5) +
                weights['fundamental'] * asset.get('fundamental_normalized', 0.5) +
                weights['momentum'] * asset.get('momentum_normalized', 0.5) +
                weights['volatility'] * asset.get('volatility_normalized', 0.5)
            )
            
            asset['score'] = score
            asset['breakdown'] = {
                'sentiment': asset.get('sentiment_normalized', 0.5),
                'fundamental': asset.get('fundamental_normalized', 0.5), 
                'momentum': asset.get('momentum_normalized', 0.5),
                'volatility': asset.get('volatility_normalized', 0.5)
            }
        
        # Sort by score descending
        universe.sort(key=lambda x: x['score'], reverse=True)
        
        return universe
    
    def allocate_capital(self, universe: List[Dict[str, Any]], capital: float) -> Dict[str, List[Dict[str, Any]]]:
        """
        Allocate capital to top assets in each category.
        """
        # Separate by type
        stocks = [asset for asset in universe if asset['type'] == 'stock']
        etfs_mfs = [asset for asset in universe if asset['type'] in ['etf', 'mutual_fund']]
        
        # Select top performers
        top_stocks = stocks[:3] if len(stocks) >= 3 else stocks
        top_etfs = etfs_mfs[:2] if len(etfs_mfs) >= 2 else etfs_mfs
        
        # Calculate allocation weights based on scores
        all_selected = top_stocks + top_etfs
        total_score = sum(asset['score'] for asset in all_selected)
        
        if total_score == 0:
            # Equal allocation if no scores
            allocation_per_asset = capital / len(all_selected) if all_selected else 0
            for asset in all_selected:
                asset['allocated'] = allocation_per_asset
                asset['percentage'] = (allocation_per_asset / capital) * 100 if capital > 0 else 0
        else:
            # Proportional allocation based on scores
            for asset in all_selected:
                asset['allocated'] = capital * (asset['score'] / total_score)
                asset['percentage'] = (asset['allocated'] / capital) * 100 if capital > 0 else 0
        
        return {
            'stocks': top_stocks,
            'etfs': top_etfs
        }
    
    def generate_explanation(self, buckets: Dict[str, List[Dict[str, Any]]], 
                           risk_profile: str, horizon_years: int) -> str:
        """
        Generate explanation text for the recommendations.
        """
        total_assets = len(buckets['stocks']) + len(buckets['etfs'])
        stock_allocation = sum(asset['percentage'] for asset in buckets['stocks'])
        etf_allocation = sum(asset['percentage'] for asset in buckets['etfs'])
        
        explanation = f"Based on your {risk_profile} risk profile and {horizon_years}-year horizon, "
        explanation += f"we recommend a portfolio of {total_assets} assets: "
        explanation += f"{len(buckets['stocks'])} stocks ({stock_allocation:.1f}%) and "
        explanation += f"{len(buckets['etfs'])} ETFs/mutual funds ({etf_allocation:.1f}%). "
        
        weights = self.WEIGHT_PRESETS[risk_profile]
        explanation += f"This allocation emphasizes "
        
        # Describe the weighting strategy
        key_factors = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        for i, (factor, weight) in enumerate(key_factors[:2]):
            if i == 1:
                explanation += " and "
            explanation += f"{factor} ({weight*100:.0f}%)"
        
        explanation += " to match your investment goals."
        
        return explanation


def validate_data_freshness(db: Session) -> Dict[str, Any]:
    """
    Validate that we have fresh data for recommendations.
    
    Returns:
        Dictionary with freshness status and warnings
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    
    status = {
        'is_fresh': True,
        'warnings': [],
        'data_age': {},
        'coverage': {}
    }
    
    try:
        # Check latest signals
        latest_signals = db.query(func.max(AssetDailySignals.date)).scalar()
        if latest_signals:
            days_old = (today - latest_signals).days
            status['data_age']['signals'] = days_old
            
            if days_old > 3:
                status['warnings'].append(f"Latest signals are {days_old} days old")
                if days_old > 7:
                    status['is_fresh'] = False
        else:
            status['warnings'].append("No signal data found")
            status['is_fresh'] = False
        
        # Check signal coverage (assets with recent signals)
        signal_coverage = db.query(func.count(func.distinct(AssetDailySignals.asset_id))).filter(
            AssetDailySignals.date >= week_ago
        ).scalar()
        
        total_active_assets = db.query(func.count(Asset.id)).filter(
            Asset.is_active == True
        ).scalar()
        
        coverage_pct = (signal_coverage / total_active_assets * 100) if total_active_assets > 0 else 0
        status['coverage']['signals'] = {
            'assets_with_signals': signal_coverage,
            'total_active_assets': total_active_assets,
            'coverage_percentage': coverage_pct
        }
        
        if coverage_pct < 50:
            status['warnings'].append(f"Low signal coverage: {coverage_pct:.1f}% of assets")
            if coverage_pct < 20:
                status['is_fresh'] = False
        
        # Check recent news processing
        recent_articles = db.query(func.count(NewsArticle.id)).filter(
            NewsArticle.fetched_at >= week_ago
        ).scalar()
        
        unprocessed_articles = db.query(func.count(NewsArticle.id)).filter(
            NewsArticle.is_processed == False,
            NewsArticle.fetched_at >= week_ago
        ).scalar()
        
        status['coverage']['news'] = {
            'recent_articles': recent_articles,
            'unprocessed_articles': unprocessed_articles
        }
        
        if recent_articles < 100:
            status['warnings'].append(f"Limited recent news data: {recent_articles} articles")
        
        if unprocessed_articles > recent_articles * 0.5:
            status['warnings'].append(f"High unprocessed article backlog: {unprocessed_articles}")
        
        # Check latest price data (if available)
        try:
            latest_price = db.query(func.max(DailyPrice.date)).scalar()
            if latest_price:
                price_days_old = (today - latest_price).days
                status['data_age']['prices'] = price_days_old
                
                if price_days_old > 5:
                    status['warnings'].append(f"Price data is {price_days_old} days old")
        except Exception as e:
            logger.debug(f"Could not check price data freshness: {e}")
        
        logger.info(f"Data freshness check: {'FRESH' if status['is_fresh'] else 'STALE'}, "
                   f"{len(status['warnings'])} warnings")
        
    except Exception as e:
        logger.error(f"Data freshness validation failed: {e}")
        status['is_fresh'] = False
        status['warnings'].append(f"Validation error: {str(e)}")
    
    return status


@router.get("/recommend/health")
async def recommendation_health(db: Session = Depends(get_db)):
    """
    Health check endpoint for recommendation system with data freshness.
    
    Returns:
        System health status and data freshness information
    """
    try:
        freshness = validate_data_freshness(db)
        
        return {
            'status': 'healthy' if freshness['is_fresh'] else 'degraded',
            'timestamp': datetime.utcnow().isoformat(),
            'data_freshness': freshness,
            'recommendation_engine': 'operational'
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate portfolio recommendations based on risk profile and constraints.
    
    Uses the latest available signals, sentiment, and fundamental data to provide
    AI-powered portfolio allocation suggestions.
    
    Args:
        request: Recommendation request parameters
        db: Database session
        
    Returns:
        Portfolio recommendations with allocations
        
    Raises:
        HTTPException: If data is too stale or universe building fails
    """
    try:
        logger.info(f"Generating recommendations for capital={request.capital}, risk={request.risk}")
        
        # Validate data freshness first
        freshness = validate_data_freshness(db)
        if not freshness['is_fresh']:
            logger.warning("Proceeding with stale data - recommendations may be suboptimal")
            # Note: We proceed but warn - in production you might want to fail here
        
        # Log data freshness warnings
        for warning in freshness['warnings']:
            logger.warning(f"Data freshness: {warning}")
        
        # Initialize recommendation engine
        engine = RecommendationEngine(db)
        
        # Determine risk profile
        risk_profile = engine.get_risk_profile(request.risk)
        
        # Build investment universe
        universe = engine.build_universe(request.exclusions)
        
        if not universe:
            raise HTTPException(
                status_code=404,
                detail="No suitable assets found for recommendation. Please check your exclusions or try again later."
            )
        
        # Normalize signals
        universe = engine.normalize_signals(universe)
        
        # Compute scores based on risk profile
        universe = engine.compute_scores(universe, risk_profile)
        
        # Allocate capital
        buckets = engine.allocate_capital(universe, request.capital)
        
        # Generate explanation
        explanation = engine.generate_explanation(buckets, risk_profile, request.horizon_years)
        
        # Format response
        stock_recommendations = [
            AssetRecommendation(
                symbol=asset['symbol'],
                name=asset['name'],
                allocated=round(asset['allocated'], 2),
                percentage=round(asset['percentage'], 2),
                score=round(asset['score'], 3),
                breakdown={k: round(v, 3) for k, v in asset['breakdown'].items()}
            )
            for asset in buckets['stocks']
        ]
        
        etf_recommendations = [
            AssetRecommendation(
                symbol=asset['symbol'],
                name=asset['name'],
                allocated=round(asset['allocated'], 2),
                percentage=round(asset['percentage'], 2),
                score=round(asset['score'], 3),
                breakdown={k: round(v, 3) for k, v in asset['breakdown'].items()}
            )
            for asset in buckets['etfs']
        ]
        
        total_allocated = sum(rec.allocated for rec in stock_recommendations + etf_recommendations)
        
        response = RecommendationResponse(
            buckets=RecommendationBuckets(
                stocks=stock_recommendations,
                etfs=etf_recommendations
            ),
            total_allocated=round(total_allocated, 2),
            explanation_text=explanation
        )
        
        logger.info(f"Generated recommendations: {len(stock_recommendations)} stocks, {len(etf_recommendations)} ETFs")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while generating recommendations"
        )


@router.get("/recommend/health")
async def recommendation_health():
    """Health check for recommendation service."""
    return {"status": "healthy", "service": "recommendation"}


# Additional utility endpoints
@router.get("/recommend/universe")
async def get_universe_stats(db: Session = Depends(get_db)):
    """Get statistics about the current investment universe."""
    try:
        # Count assets by type
        asset_counts = db.query(
            Asset.type,
            func.count(Asset.id).label('count')
        ).filter(Asset.is_active == True).group_by(Asset.type).all()
        
        # Count assets with recent signals
        recent_date = date.today() - timedelta(days=7)
        assets_with_signals = db.query(
            func.count(func.distinct(AssetDailySignals.asset_id))
        ).filter(AssetDailySignals.date >= recent_date).scalar()
        
        return {
            "asset_counts": {row.type: row.count for row in asset_counts},
            "assets_with_recent_signals": assets_with_signals,
            "last_updated": recent_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting universe stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving universe statistics")