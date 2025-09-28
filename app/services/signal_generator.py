"""Signal Generator Service - Computes aggregated daily signals for assets."""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from database import SessionLocal
from models import Asset, DailyPrice, NewsArticle, NewsSentiment, AssetDailySignals, QuarterlyFundamental

logger = logging.getLogger(__name__)


class SignalGenerator:
    """
    Service for generating aggregated daily signals from sentiment, price, and fundamental data.
    """
    
    def __init__(self):
        """Initialize signal generator."""
        pass
    
    def calculate_sentiment_signals(self, db: Session, asset_id: int, target_date: date) -> Dict[str, float]:
        """
        Calculate sentiment signals for an asset on a specific date.
        
        Args:
            db: Database session
            asset_id: Asset ID
            target_date: Date to calculate signals for
            
        Returns:
            Dictionary with sentiment signals
        """
        signals = {
            'avg_sentiment': None,
            'article_count': 0,
            'sentiment_7d_avg': None,
            'sentiment_30d_avg': None
        }
        
        try:
            # Daily sentiment (articles published on target_date)
            daily_query = db.query(
                func.avg(NewsSentiment.polarity).label('avg_sentiment'),
                func.count(NewsSentiment.id).label('article_count')
            ).join(NewsArticle).filter(
                NewsSentiment.asset_id == asset_id,
                func.date(NewsArticle.published_at) == target_date
            ).first()
            
            if daily_query.article_count > 0:
                signals['avg_sentiment'] = float(daily_query.avg_sentiment or 0.0)
                signals['article_count'] = int(daily_query.article_count or 0)
            
            # 7-day rolling average
            week_ago = target_date - timedelta(days=7)
            weekly_query = db.query(
                func.avg(NewsSentiment.polarity).label('avg_sentiment_7d')
            ).join(NewsArticle).filter(
                NewsSentiment.asset_id == asset_id,
                func.date(NewsArticle.published_at) >= week_ago,
                func.date(NewsArticle.published_at) <= target_date
            ).first()
            
            if weekly_query.avg_sentiment_7d is not None:
                signals['sentiment_7d_avg'] = float(weekly_query.avg_sentiment_7d)
            
            # 30-day rolling average
            month_ago = target_date - timedelta(days=30)
            monthly_query = db.query(
                func.avg(NewsSentiment.polarity).label('avg_sentiment_30d')
            ).join(NewsArticle).filter(
                NewsSentiment.asset_id == asset_id,
                func.date(NewsArticle.published_at) >= month_ago,
                func.date(NewsArticle.published_at) <= target_date
            ).first()
            
            if monthly_query.avg_sentiment_30d is not None:
                signals['sentiment_30d_avg'] = float(monthly_query.avg_sentiment_30d)
            
        except Exception as e:
            logger.error(f"Error calculating sentiment signals for asset {asset_id}, date {target_date}: {e}")
        
        return signals
    
    def calculate_price_signals(self, db: Session, asset_id: int, target_date: date) -> Dict[str, float]:
        """
        Calculate price-based signals for an asset.
        
        Args:
            db: Database session
            asset_id: Asset ID  
            target_date: Date to calculate signals for
            
        Returns:
            Dictionary with price signals
        """
        signals = {
            'volatility_30d': None,
            'return_30d': None,
            'return_365d': None
        }
        
        try:
            # Get price data for calculations
            # 30-day volatility and return
            thirty_days_ago = target_date - timedelta(days=30)
            price_30d = db.query(DailyPrice).filter(
                DailyPrice.asset_id == asset_id,
                DailyPrice.date >= thirty_days_ago,
                DailyPrice.date <= target_date
            ).order_by(DailyPrice.date).all()
            
            if len(price_30d) > 1:
                # Calculate 30-day return
                start_price = price_30d[0].close
                end_price = price_30d[-1].close
                if start_price and end_price and start_price > 0:
                    signals['return_30d'] = (end_price - start_price) / start_price
                
                # Calculate 30-day volatility (standard deviation of daily returns)
                daily_returns = []
                for i in range(1, len(price_30d)):
                    prev_close = price_30d[i-1].close
                    curr_close = price_30d[i].close
                    if prev_close and curr_close and prev_close > 0:
                        daily_return = (curr_close - prev_close) / prev_close
                        daily_returns.append(daily_return)
                
                if len(daily_returns) > 1:
                    import statistics
                    signals['volatility_30d'] = statistics.stdev(daily_returns)
            
            # 365-day return
            year_ago = target_date - timedelta(days=365)
            price_start = db.query(DailyPrice).filter(
                DailyPrice.asset_id == asset_id,
                DailyPrice.date >= year_ago
            ).order_by(DailyPrice.date).first()
            
            price_end = db.query(DailyPrice).filter(
                DailyPrice.asset_id == asset_id,
                DailyPrice.date <= target_date
            ).order_by(desc(DailyPrice.date)).first()
            
            if price_start and price_end and price_start.close and price_end.close and price_start.close > 0:
                signals['return_365d'] = (price_end.close - price_start.close) / price_start.close
            
        except Exception as e:
            logger.error(f"Error calculating price signals for asset {asset_id}, date {target_date}: {e}")
        
        return signals
    
    def calculate_fundamental_score(self, db: Session, asset_id: int, target_date: date) -> Optional[float]:
        """
        Calculate a composite fundamental score for an asset.
        
        Args:
            db: Database session
            asset_id: Asset ID
            target_date: Date to calculate score for
            
        Returns:
            Fundamental score or None
        """
        try:
            # Get the most recent fundamental data before target_date
            fundamental = db.query(QuarterlyFundamental).filter(
                QuarterlyFundamental.asset_id == asset_id,
                QuarterlyFundamental.quarter_end <= target_date
            ).order_by(desc(QuarterlyFundamental.quarter_end)).first()
            
            if not fundamental:
                return None
            
            # Simple composite score based on key metrics
            # This is a basic implementation - you can make it more sophisticated
            score_components = []
            
            # ROE (positive is good)
            if fundamental.roe is not None:
                score_components.append(min(fundamental.roe / 20.0, 1.0))  # Normalize to 20% ROE = 1.0
            
            # P/E ratio (lower is generally better, but not too low)
            if fundamental.pe_ratio is not None and fundamental.pe_ratio > 0:
                # Optimal P/E around 15, score decreases as it gets higher or lower than 10-25 range
                pe_score = max(0, 1.0 - abs(fundamental.pe_ratio - 15.0) / 15.0)
                score_components.append(pe_score)
            
            # Debt to equity (lower is generally better)
            if fundamental.debt_to_equity is not None:
                debt_score = max(0, 1.0 - fundamental.debt_to_equity / 2.0)  # 2.0 D/E = 0 score
                score_components.append(debt_score)
            
            # Revenue growth (positive is good)
            if fundamental.revenue_growth is not None:
                growth_score = min(fundamental.revenue_growth / 0.20, 1.0)  # 20% growth = 1.0
                score_components.append(growth_score)
            
            if score_components:
                return sum(score_components) / len(score_components)
            
        except Exception as e:
            logger.error(f"Error calculating fundamental score for asset {asset_id}: {e}")
        
        return None
    
    def generate_signals_for_date(self, db: Session, asset_id: int, target_date: date) -> bool:
        """
        Generate all signals for a specific asset and date.
        
        Args:
            db: Database session
            asset_id: Asset ID
            target_date: Date to generate signals for
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Calculate all signal types
            sentiment_signals = self.calculate_sentiment_signals(db, asset_id, target_date)
            price_signals = self.calculate_price_signals(db, asset_id, target_date)
            fundamental_score = self.calculate_fundamental_score(db, asset_id, target_date)
            
            # Check if record already exists
            existing = db.query(AssetDailySignals).filter(
                AssetDailySignals.asset_id == asset_id,
                AssetDailySignals.date == target_date
            ).first()
            
            if existing:
                # Update existing record
                existing.avg_sentiment = sentiment_signals['avg_sentiment']
                existing.article_count = sentiment_signals['article_count']
                existing.sentiment_7d_avg = sentiment_signals['sentiment_7d_avg']
                existing.sentiment_30d_avg = sentiment_signals['sentiment_30d_avg']
                existing.volatility_30d = price_signals['volatility_30d']
                existing.return_30d = price_signals['return_30d']
                existing.return_365d = price_signals['return_365d']
                existing.fundamental_score = fundamental_score
                existing.updated_at = func.now()
                
                logger.debug(f"Updated signals for asset {asset_id}, date {target_date}")
            else:
                # Create new record
                signals = AssetDailySignals(
                    asset_id=asset_id,
                    date=target_date,
                    avg_sentiment=sentiment_signals['avg_sentiment'],
                    article_count=sentiment_signals['article_count'],
                    sentiment_7d_avg=sentiment_signals['sentiment_7d_avg'],
                    sentiment_30d_avg=sentiment_signals['sentiment_30d_avg'],
                    volatility_30d=price_signals['volatility_30d'],
                    return_30d=price_signals['return_30d'],
                    return_365d=price_signals['return_365d'],
                    fundamental_score=fundamental_score
                )
                db.add(signals)
                
                logger.debug(f"Created signals for asset {asset_id}, date {target_date}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating signals for asset {asset_id}, date {target_date}: {e}")
            return False
    
    def generate_signals_batch(self, days_back: int = 7, asset_ids: Optional[List[int]] = None) -> Dict[str, int]:
        """
        Generate signals for multiple assets and dates.
        
        Args:
            days_back: Number of days back to generate signals for
            asset_ids: List of specific asset IDs to process (None = all active assets)
            
        Returns:
            Dictionary with processing statistics
        """
        logger.info(f"Starting signal generation for last {days_back} days")
        
        stats = {
            'assets_processed': 0,
            'signals_generated': 0,
            'errors': 0
        }
        
        db = SessionLocal()
        try:
            # Get assets to process
            if asset_ids:
                assets = db.query(Asset.id).filter(
                    Asset.id.in_(asset_ids),
                    Asset.is_active == True
                ).all()
            else:
                assets = db.query(Asset.id).filter(Asset.is_active == True).all()
            
            asset_ids_to_process = [asset.id for asset in assets]
            logger.info(f"Processing {len(asset_ids_to_process)} assets")
            
            # Generate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back-1)
            
            dates_to_process = []
            current_date = start_date
            while current_date <= end_date:
                dates_to_process.append(current_date)
                current_date += timedelta(days=1)
            
            # Process each asset for each date
            for asset_id in asset_ids_to_process:
                asset_processed = False
                for target_date in dates_to_process:
                    try:
                        success = self.generate_signals_for_date(db, asset_id, target_date)
                        if success:
                            stats['signals_generated'] += 1
                            asset_processed = True
                        else:
                            stats['errors'] += 1
                            
                    except Exception as e:
                        logger.error(f"Error processing asset {asset_id}, date {target_date}: {e}")
                        stats['errors'] += 1
                        db.rollback()
                        continue
                
                if asset_processed:
                    stats['assets_processed'] += 1
                
                # Commit after each asset to avoid losing work
                db.commit()
            
            logger.info(f"Signal generation completed: {stats}")
            
        except Exception as e:
            logger.error(f"Error in signal generation batch: {e}")
            db.rollback()
            stats['errors'] += 1
            
        finally:
            db.close()
        
        return stats


def main():
    """Main function for CLI usage."""
    logging.basicConfig(level=logging.INFO)
    
    generator = SignalGenerator()
    results = generator.generate_signals_batch(days_back=7)
    
    print(f"Signal Generation Results:")
    print(f"  Assets processed: {results['assets_processed']}")
    print(f"  Signals generated: {results['signals_generated']}")
    print(f"  Errors: {results['errors']}")


if __name__ == "__main__":
    main()