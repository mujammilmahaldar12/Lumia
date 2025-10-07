# roboadvisor/asset_selector.py
"""
ASSET SELECTION MODULE
Intelligent asset selection using fundamentals, technicals, and sentiment analysis
"""

from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from datetime import datetime, timedelta
import numpy as np

# Import models
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.assets import Asset
from models.daily_price import DailyPrice
from models.quarterly_fundamental import QuarterlyFundamental
from models.news_article import NewsArticle
from roboadvisor.advanced_metrics import AdvancedMetricsCalculator, score_with_advanced_metrics

class AssetScorer:
    """Comprehensive asset scoring system"""
    
    def __init__(self, db: Session):
        self.db = db
        self.advanced_calculator = AdvancedMetricsCalculator(db)
    
    def score_stock(self, asset: Asset) -> Tuple[float, Dict]:
        """
        Score a stock using multiple factors:
        
        - Fundamentals (40%): 
          • Valuation: P/E ratio, P/B ratio (12 points)
          • Profitability: ROE, ROA, Profit Margin (12 points)
          • Financial Health: Debt/Equity, Current Ratio, Quick Ratio (10 points)
          • Growth: Revenue Growth, Earnings Growth (6 points)
        
        - Technicals (30%): 
          • Momentum, Volatility, Moving Averages
        
        - Sentiment (30%): 
          • News sentiment analysis from recent articles
        
        - Advanced Metrics (BONUS 10%):
          • CAGR, Sortino, Max Drawdown, Alpha, Capture Ratios
        
        Returns:
            (score, breakdown_dict)
        """
        breakdown = {
            "fundamental_score": 0,
            "technical_score": 0,
            "sentiment_score": 0,
            "advanced_bonus": 0,
            "advanced_metrics": {},
            "details": {}
        }
        
        # 1. FUNDAMENTAL ANALYSIS (40 points)
        fundamental_score = self._score_fundamentals(asset)
        breakdown["fundamental_score"] = fundamental_score
        
        # 2. TECHNICAL ANALYSIS (30 points)
        technical_score = self._score_technicals(asset)
        breakdown["technical_score"] = technical_score
        
        # 3. SENTIMENT ANALYSIS (30 points)
        sentiment_score = self._score_sentiment(asset)
        breakdown["sentiment_score"] = sentiment_score
        
        # 4. ADVANCED METRICS (BONUS 10 points)
        try:
            advanced_metrics = self.advanced_calculator.calculate_all_metrics(asset)
            advanced_bonus = score_with_advanced_metrics(advanced_metrics)
            breakdown["advanced_bonus"] = advanced_bonus
            breakdown["advanced_metrics"] = advanced_metrics
        except Exception as e:
            # If advanced metrics fail, just skip the bonus
            advanced_bonus = 0
            breakdown["advanced_metrics"] = {}
        
        # Total score (out of 110 with bonus, but cap at 100)
        total_score = fundamental_score + technical_score + sentiment_score + advanced_bonus
        total_score = min(total_score, 100)  # Cap at 100
        
        return total_score, breakdown
    
    def _score_fundamentals(self, asset: Asset) -> float:
        """
        Score based on fundamental metrics (40 points max)
        
        Uses quarterly fundamental data:
        - Valuation: P/E, P/B ratios
        - Profitability: ROE, ROA, Profit Margin
        - Financial Health: Debt/Equity, Current Ratio, Quick Ratio
        - Growth: Revenue Growth, Earnings Growth
        """
        try:
            # Get latest fundamental data
            fundamental = self.db.query(QuarterlyFundamental).filter(
                QuarterlyFundamental.asset_id == asset.id
            ).order_by(desc(QuarterlyFundamental.report_date)).first()
            
            if not fundamental:
                # Return 25/40 as neutral when no fundamental data
                # This allows assets with good technicals to pass
                return 25.0
            
            score = 0
            details = {}
            
            # 1. VALUATION METRICS (12 points total)
            
            # P/E Ratio (6 points) - Lower is better (10-25 is good)
            pe = fundamental.price_to_earnings_ratio
            if pe and 10 <= pe <= 25:
                score += 6
                details['pe'] = 'Excellent'
            elif pe and 25 < pe <= 35:
                score += 4
                details['pe'] = 'Good'
            elif pe and 5 < pe < 10:
                score += 3
                details['pe'] = 'Low (might be value)'
            elif pe and pe > 35:
                score += 1
                details['pe'] = 'High (overvalued?)'
            
            # P/B Ratio (6 points) - Lower is generally better
            pb = fundamental.price_to_book_ratio
            if pb and 1.0 <= pb <= 3.0:
                score += 6
                details['pb'] = 'Excellent'
            elif pb and 3.0 < pb <= 5.0:
                score += 4
                details['pb'] = 'Good'
            elif pb and pb < 1.0:
                score += 5
                details['pb'] = 'Value (below book)'
            elif pb and pb > 5.0:
                score += 2
                details['pb'] = 'High'
            
            # 2. PROFITABILITY METRICS (12 points total)
            
            # ROE - Return on Equity (6 points) - Higher is better (>15% is good)
            roe = fundamental.return_on_equity
            if roe and roe > 0.20:  # 20%+
                score += 6
                details['roe'] = 'Excellent (>20%)'
            elif roe and roe > 0.15:  # 15-20%
                score += 5
                details['roe'] = 'Very Good (15-20%)'
            elif roe and roe > 0.10:  # 10-15%
                score += 3
                details['roe'] = 'Good (10-15%)'
            elif roe and roe > 0.05:
                score += 1
                details['roe'] = 'Fair (5-10%)'
            
            # ROA - Return on Assets (3 points) - Higher is better
            roa = fundamental.return_on_assets
            if roa and roa > 0.15:  # 15%+
                score += 3
                details['roa'] = 'Excellent'
            elif roa and roa > 0.10:
                score += 2
                details['roa'] = 'Good'
            elif roa and roa > 0.05:
                score += 1
                details['roa'] = 'Fair'
            
            # Profit Margin (3 points) - Higher is better
            pm = fundamental.profit_margin
            if pm and pm > 0.20:  # 20%+
                score += 3
                details['profit_margin'] = 'Excellent (>20%)'
            elif pm and pm > 0.10:
                score += 2
                details['profit_margin'] = 'Good (>10%)'
            elif pm and pm > 0.05:
                score += 1
                details['profit_margin'] = 'Fair (>5%)'
            
            # 3. FINANCIAL HEALTH (10 points total)
            
            # Debt to Equity (5 points) - Lower is better (<1.0 is good)
            de = fundamental.debt_to_equity_ratio
            if de is not None:
                if de < 0.3:
                    score += 5
                    details['debt_equity'] = 'Excellent (<0.3)'
                elif de < 0.5:
                    score += 4
                    details['debt_equity'] = 'Very Good (<0.5)'
                elif de < 1.0:
                    score += 3
                    details['debt_equity'] = 'Good (<1.0)'
                elif de < 2.0:
                    score += 1
                    details['debt_equity'] = 'Moderate (1-2)'
            
            # Current Ratio (3 points) - 1.5-3.0 is healthy
            cr = fundamental.current_ratio
            if cr and 1.5 <= cr <= 3.0:
                score += 3
                details['current_ratio'] = 'Excellent (1.5-3.0)'
            elif cr and 1.0 <= cr < 1.5:
                score += 2
                details['current_ratio'] = 'Good (1.0-1.5)'
            elif cr and cr > 3.0:
                score += 2
                details['current_ratio'] = 'High (>3.0)'
            elif cr and cr < 1.0:
                score += 0
                details['current_ratio'] = 'Low risk (<1.0)'
            
            # Quick Ratio (2 points) - More conservative liquidity measure
            qr = fundamental.quick_ratio
            if qr and qr >= 1.0:
                score += 2
                details['quick_ratio'] = 'Excellent (≥1.0)'
            elif qr and qr >= 0.5:
                score += 1
                details['quick_ratio'] = 'Adequate (≥0.5)'
            
            # 4. GROWTH METRICS (6 points total)
            
            # Revenue Growth (3 points) - Higher is better
            rev_growth = fundamental.revenue_growth
            if rev_growth and rev_growth > 0.20:  # 20%+
                score += 3
                details['revenue_growth'] = 'Excellent (>20%)'
            elif rev_growth and rev_growth > 0.10:
                score += 2
                details['revenue_growth'] = 'Good (>10%)'
            elif rev_growth and rev_growth > 0.05:
                score += 1
                details['revenue_growth'] = 'Moderate (>5%)'
            elif rev_growth and rev_growth < 0:
                score += 0
                details['revenue_growth'] = 'Negative'
            
            # Earnings Growth (3 points) - Higher is better
            earn_growth = fundamental.earnings_growth
            if earn_growth and earn_growth > 0.20:  # 20%+
                score += 3
                details['earnings_growth'] = 'Excellent (>20%)'
            elif earn_growth and earn_growth > 0.10:
                score += 2
                details['earnings_growth'] = 'Good (>10%)'
            elif earn_growth and earn_growth > 0.05:
                score += 1
                details['earnings_growth'] = 'Moderate (>5%)'
            elif earn_growth and earn_growth < 0:
                score += 0
                details['earnings_growth'] = 'Negative'
            
            # Store details for debugging
            fundamental.scoring_details = details
            
            return min(score, 40)  # Cap at 40
            
        except Exception as e:
            return 20.0  # Neutral score on error
    
    def _score_technicals(self, asset: Asset) -> float:
        """Score based on technical indicators (30 points max)"""
        try:
            # Get 200 days of price data
            cutoff_date = datetime.now() - timedelta(days=300)
            prices = self.db.query(DailyPrice).filter(
                DailyPrice.asset_id == asset.id,
                DailyPrice.date >= cutoff_date
            ).order_by(DailyPrice.date).all()
            
            if len(prices) < 50:
                return 15.0  # Neutral score if insufficient data
            
            score = 0
            close_prices = [p.close_price for p in prices if p.close_price]
            
            if len(close_prices) < 50:
                return 15.0
            
            # 1. Momentum (10 points) - Positive trend
            returns = np.diff(close_prices) / close_prices[:-1]
            avg_return = np.mean(returns[-60:])  # Last 60 days
            
            if avg_return > 0.002:  # >0.2% daily
                score += 10
            elif avg_return > 0:
                score += 7
            elif avg_return > -0.002:
                score += 3
            
            # 2. Volatility (10 points) - Moderate is good
            volatility = np.std(returns[-60:]) * np.sqrt(252)  # Annualized
            
            if 0.10 <= volatility <= 0.25:  # 10-25% (moderate)
                score += 10
            elif 0.25 < volatility <= 0.40:  # 25-40% (acceptable)
                score += 7
            elif volatility < 0.10:  # Too low (boring)
                score += 5
            else:  # Too high (risky)
                score += 3
            
            # 3. Moving Average Signal (10 points)
            if len(close_prices) >= 200:
                sma_20 = np.mean(close_prices[-20:])
                sma_50 = np.mean(close_prices[-50:])
                sma_200 = np.mean(close_prices[-200:])
                current_price = close_prices[-1]
                
                # Golden cross: Price above all MAs
                if current_price > sma_20 > sma_50 > sma_200:
                    score += 10
                elif current_price > sma_50:
                    score += 7
                elif current_price > sma_200:
                    score += 5
            else:
                score += 5  # Neutral
            
            return min(score, 30)  # Cap at 30
            
        except Exception as e:
            return 15.0  # Neutral score on error
    
    def _score_sentiment(self, asset: Asset) -> float:
        """Score based on news sentiment (30 points max)"""
        try:
            # Get news from last 30 days linked to this asset
            cutoff_date = datetime.now() - timedelta(days=30)
            
            # Use asset_id for direct linking (much more accurate!)
            news_items = self.db.query(NewsArticle).filter(
                NewsArticle.asset_id == asset.id,
                NewsArticle.published_at >= cutoff_date
            ).all()
            
            if not news_items:
                return 15.0  # Neutral score if no news
            
            # Calculate average sentiment
            sentiments = [n.sentiment_score for n in news_items if n.sentiment_score is not None]
            
            if not sentiments:
                return 15.0
            
            avg_sentiment = np.mean(sentiments)  # 0-1 scale
            
            # Convert to 0-30 scale
            score = avg_sentiment * 30
            
            # Bonus for positive news volume
            if len(sentiments) > 10:
                score += 2
            if len(sentiments) > 20:
                score += 3
            
            return min(score, 30)  # Cap at 30
            
        except Exception as e:
            return 15.0  # Neutral score on error

def select_top_assets(
    db: Session,
    asset_type: str,
    limit: int = 10,
    min_score: float = 20.0,  # LOWERED from 60 to work with partial data
    sector_diversification: Dict[str, float] = None
) -> List[Dict]:
    """
    Select top-performing assets of a specific type
    
    Args:
        db: Database session
        asset_type: Type of asset ('stock', 'etf', 'mutual_fund', 'crypto')
        limit: Maximum number of assets to return
        min_score: Minimum score threshold (0-100) - Default 20 for partial data
        sector_diversification: Optional sector allocation limits
    
    Returns:
        List of dictionaries with asset details and scores
    """
    scorer = AssetScorer(db)
    
    # Get all assets of this type with recent price data
    from datetime import datetime, timedelta
    from models.daily_price import DailyPrice
    
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    # Only get assets that have recent price data
    asset_ids_with_prices = db.query(DailyPrice.asset_id).filter(
        DailyPrice.date >= thirty_days_ago
    ).distinct().subquery()
    
    # Get diverse set of assets - order by market cap for stocks/ETFs
    query = db.query(Asset).filter(
        Asset.type == asset_type,
        Asset.is_active == True,
        Asset.id.in_(asset_ids_with_prices)
    )
    
    # Order differently based on type for diversity
    if asset_type in ['stock', 'etf']:
        # Prioritize larger market cap (more liquid, stable)
        query = query.order_by(desc(Asset.market_cap))
    else:
        # For others, use symbol for consistent ordering
        query = query.order_by(Asset.symbol)
    
    assets = query.limit(200).all()  # Increased from 100 to get more variety
    
    # Score each asset
    scored_assets = []
    sector_counts = {}
    
    for asset in assets:
        if asset_type == 'stock':
            score, breakdown = scorer.score_stock(asset)
        elif asset_type == 'etf':
            score, breakdown = scorer.score_stock(asset)  # Similar scoring
        elif asset_type == 'mutual_fund':
            score, breakdown = scorer.score_stock(asset)  # Similar scoring
        elif asset_type == 'crypto':
            # For crypto, focus more on technicals and sentiment
            score, breakdown = scorer.score_stock(asset)
        else:
            continue
        
        if score >= min_score:
            # Check sector diversification limits
            sector = asset.sector or "Unknown"
            
            # 🔥 CRITICAL: Skip ALL diversification checks for Unknown sectors
            # (Most Indian stocks/MFs have Unknown sector)
            if sector in ["Unknown", "Other", None, ""]:
                # Always allow Unknown sectors (no limits, no checks)
                pass
            elif sector_diversification:
                # For KNOWN sectors: Apply strict diversification
                max_count = int(limit * sector_diversification.get(sector, 0.2))
                current_count = sector_counts.get(sector, 0)
                if current_count >= max_count:
                    continue  # Skip to maintain diversification
            
            scored_assets.append({
                "asset": asset,
                "symbol": asset.symbol,
                "name": asset.name,
                "score": score,
                "breakdown": breakdown,
                "sector": asset.sector,
                "market_cap": asset.market_cap
            })
            
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
    
    # Sort by score (descending), with smart randomization
    # 🔥 SMART: Only randomize if we have ABUNDANT assets (3x+ what we need)
    # Otherwise use actual scores to ensure consistency
    import random
    
    if len(scored_assets) >= limit * 3:
        # Abundant assets: Add ±2 random variation for variety
        for item in scored_assets:
            item["adjusted_score"] = item["score"] + random.uniform(-2, 2)
    else:
        # Scarce assets: Use actual scores (no randomization)
        for item in scored_assets:
            item["adjusted_score"] = item["score"]
    
    scored_assets.sort(key=lambda x: x["adjusted_score"], reverse=True)
    
    # Ensure diversity - no duplicate sectors if possible
    selected = []
    used_sectors = set()
    used_symbols_prefix = set()  # Prevent similar symbols
    
    for item in scored_assets:
        if len(selected) >= limit:
            break
        
        sector = item["sector"] or "Unknown"
        symbol_prefix = item["symbol"][:3]  # First 3 chars
        
        # For small limits, enforce sector diversity ONLY for known sectors
        if limit <= 5 and sector not in ["Unknown", "Other", None, ""]:
            if sector in used_sectors and len(scored_assets) > limit:
                continue  # Skip duplicate sector (only for known sectors)
        
        # Prevent very similar symbols (XLE, XLF, XLK → only pick one)
        if symbol_prefix in used_symbols_prefix and len(scored_assets) > limit:
            continue
        
        selected.append(item)
        used_sectors.add(sector)
        used_symbols_prefix.add(symbol_prefix)
    
    # If we didn't get enough, fill remaining with any qualified assets
    if len(selected) < limit:
        for item in scored_assets:
            if item not in selected and len(selected) < limit:
                selected.append(item)
    
    return selected[:limit]
