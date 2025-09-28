"""Sentiment Worker Service - Analyzes sentiment of news articles using FinBERT or VADER."""

import os
import logging
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from database import SessionLocal
from models import NewsArticle, NewsAssetMap, NewsSentiment

logger = logging.getLogger(__name__)


class SentimentWorker:
    """
    Service for analyzing sentiment of news articles.
    Uses FinBERT as primary model with VADER as fallback.
    """
    
    def __init__(self):
        """Initialize sentiment analysis models."""
        self.use_finbert = os.getenv("USE_FINBERT", "true").lower() == "true"
        self.finbert_pipeline = None
        self.vader_analyzer = None
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize sentiment analysis models."""
        if self.use_finbert:
            try:
                from transformers import pipeline
                self.finbert_pipeline = pipeline(
                    "sentiment-analysis",
                    model="yiyanghkust/finbert-tone",
                    tokenizer="yiyanghkust/finbert-tone"
                )
                logger.info("FinBERT model initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize FinBERT: {e}. Falling back to VADER.")
                self.use_finbert = False
        
        if not self.use_finbert:
            try:
                import nltk
                from nltk.sentiment import SentimentIntensityAnalyzer
                
                # Download VADER lexicon if not present
                try:
                    nltk.data.find('vader_lexicon')
                except LookupError:
                    logger.info("Downloading VADER lexicon...")
                    nltk.download('vader_lexicon', quiet=True)
                
                self.vader_analyzer = SentimentIntensityAnalyzer()
                logger.info("VADER sentiment analyzer initialized")
            except Exception as e:
                logger.error(f"Failed to initialize VADER: {e}")
                raise ValueError("No sentiment analysis model available")
    
    def analyze_with_finbert(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using FinBERT model.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        if not self.finbert_pipeline:
            raise ValueError("FinBERT model not initialized")
        
        try:
            # Truncate text to avoid token limits
            text = text[:512] if len(text) > 512 else text
            
            result = self.finbert_pipeline(text)
            
            # FinBERT returns labels: positive, negative, neutral
            label = result[0]['label'].lower()
            confidence = result[0]['score']
            
            # Convert to standard format
            if label == 'positive':
                return {
                    'polarity': confidence,
                    'pos': confidence,
                    'neg': 0.0,
                    'neu': 1.0 - confidence
                }
            elif label == 'negative':
                return {
                    'polarity': -confidence,
                    'pos': 0.0,
                    'neg': confidence,
                    'neu': 1.0 - confidence
                }
            else:  # neutral
                return {
                    'polarity': 0.0,
                    'pos': 0.0,
                    'neg': 0.0,
                    'neu': confidence
                }
                
        except Exception as e:
            logger.error(f"FinBERT analysis error: {e}")
            # Fallback to neutral
            return {
                'polarity': 0.0,
                'pos': 0.0,
                'neg': 0.0,
                'neu': 1.0
            }
    
    def analyze_with_vader(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using VADER.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        if not self.vader_analyzer:
            raise ValueError("VADER analyzer not initialized")
        
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            return {
                'polarity': scores['compound'],
                'pos': scores['pos'],
                'neg': scores['neg'],
                'neu': scores['neu']
            }
        except Exception as e:
            logger.error(f"VADER analysis error: {e}")
            # Fallback to neutral
            return {
                'polarity': 0.0,
                'pos': 0.0,
                'neg': 0.0,
                'neu': 1.0
            }
    
    def analyze_sentiment(self, text: str) -> Tuple[str, Dict[str, float]]:
        """
        Analyze sentiment using available model.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (model_name, sentiment_scores)
        """
        if self.use_finbert and self.finbert_pipeline:
            return "finbert", self.analyze_with_finbert(text)
        else:
            return "vader", self.analyze_with_vader(text)
    
    def get_unprocessed_articles(self, db: Session, limit: int = 100) -> List[Tuple[NewsArticle, List[int]]]:
        """
        Get articles that need sentiment analysis.
        
        Args:
            db: Database session
            limit: Maximum number of articles to process
            
        Returns:
            List of (article, asset_ids) tuples
        """
        # Get articles that have asset mappings but no sentiment analysis
        query = db.query(NewsArticle).join(NewsAssetMap).outerjoin(
            NewsSentiment,
            and_(
                NewsSentiment.article_id == NewsArticle.id,
                NewsSentiment.asset_id == NewsAssetMap.asset_id
            )
        ).filter(
            NewsSentiment.id.is_(None)  # No sentiment record exists
        ).distinct().limit(limit)
        
        articles_with_assets = []
        for article in query.all():
            # Get asset IDs for this article
            asset_ids = [
                mapping.asset_id 
                for mapping in article.asset_mappings
            ]
            if asset_ids:
                articles_with_assets.append((article, asset_ids))
        
        logger.info(f"Found {len(articles_with_assets)} articles needing sentiment analysis")
        return articles_with_assets
    
    def store_sentiment_result(self, db: Session, article_id: int, asset_id: int, model_name: str, scores: Dict[str, float]):
        """
        Store sentiment analysis result in database.
        
        Args:
            db: Database session
            article_id: Article ID
            asset_id: Asset ID
            model_name: Name of the model used
            scores: Sentiment scores dictionary
        """
        try:
            sentiment = NewsSentiment(
                article_id=article_id,
                asset_id=asset_id,
                model_name=model_name,
                polarity=scores['polarity'],
                pos=scores['pos'],
                neg=scores['neg'],
                neu=scores['neu']
            )
            db.add(sentiment)
            
        except Exception as e:
            logger.error(f"Error storing sentiment for article {article_id}, asset {asset_id}: {e}")
            raise
    
    def process_article_sentiment(self, db: Session, article: NewsArticle, asset_ids: List[int]) -> int:
        """
        Process sentiment analysis for a single article.
        
        Args:
            db: Database session
            article: NewsArticle to process
            asset_ids: List of asset IDs to create sentiment records for
            
        Returns:
            Number of sentiment records created
        """
        # Prepare text for analysis
        text = article.title
        if article.summary:
            text += f". {article.summary}"
        
        if not text.strip():
            logger.warning(f"Article {article.id} has no text content")
            return 0
        
        try:
            # Analyze sentiment
            model_name, scores = self.analyze_sentiment(text)
            
            # Store sentiment for each mapped asset
            records_created = 0
            for asset_id in asset_ids:
                self.store_sentiment_result(db, article.id, asset_id, model_name, scores)
                records_created += 1
            
            # Mark article as processed
            article.is_processed = True
            
            return records_created
            
        except Exception as e:
            logger.error(f"Error processing sentiment for article {article.id}: {e}")
            return 0
    
    def process_sentiment_batch(self, limit: int = 100) -> Dict[str, int]:
        """
        Process sentiment analysis for a batch of articles.
        
        Args:
            limit: Maximum number of articles to process
            
        Returns:
            Dictionary with processing statistics
        """
        logger.info(f"Starting sentiment processing for up to {limit} articles")
        
        stats = {
            'articles_processed': 0,
            'sentiment_records_created': 0,
            'errors': 0
        }
        
        db = SessionLocal()
        try:
            # Get unprocessed articles
            articles_with_assets = self.get_unprocessed_articles(db, limit)
            
            if not articles_with_assets:
                logger.info("No articles need sentiment processing")
                return stats
            
            # Process each article
            for article, asset_ids in articles_with_assets:
                try:
                    records_created = self.process_article_sentiment(db, article, asset_ids)
                    stats['articles_processed'] += 1
                    stats['sentiment_records_created'] += records_created
                    
                    # Commit after each article to avoid losing work
                    db.commit()
                    
                except Exception as e:
                    logger.error(f"Error processing article {article.id}: {e}")
                    stats['errors'] += 1
                    db.rollback()
                    continue
            
            logger.info(f"Sentiment processing completed: {stats}")
            
        except Exception as e:
            logger.error(f"Error in sentiment processing batch: {e}")
            db.rollback()
            stats['errors'] += 1
            
        finally:
            db.close()
        
        return stats


def main():
    """Main function for CLI usage."""
    logging.basicConfig(level=logging.INFO)
    
    try:
        worker = SentimentWorker()
        results = worker.process_sentiment_batch(limit=100)
        
        print(f"Sentiment Processing Results:")
        print(f"  Articles processed: {results['articles_processed']}")
        print(f"  Sentiment records created: {results['sentiment_records_created']}")
        print(f"  Errors: {results['errors']}")
        
    except Exception as e:
        print(f"Error initializing sentiment worker: {e}")
        print("Make sure you have either:")
        print("1. transformers library installed and USE_FINBERT=true")
        print("2. nltk library installed for VADER fallback")


if __name__ == "__main__":
    main()