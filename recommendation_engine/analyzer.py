"""
ANALYZER MODULE - FinBERT Sentiment Analysis & Data Aggregation

This module integrates FinBERT (Financial BERT) for sentiment analysis of news articles.

WHAT IS FINBERT?
- FinBERT is a pre-trained NLP model specifically trained on financial text
- It understands financial language better than generic models
- Trained on 1.8M sentences from earnings calls, analyst reports, financial news
- Output: Positive/Negative/Neutral sentiment + confidence score

ALGORITHM:
1. Collect news articles for an asset (last 30 days)
2. Feed title + description to FinBERT model
3. Get sentiment label (positive/negative/neutral) and confidence (0-1)
4. Aggregate all sentiments to get overall score
5. Store in database for future use

SENTIMENT SCORE CALCULATION:
- Positive article = +100 points × confidence
- Neutral article = +50 points × confidence
- Negative article = 0 points × confidence
- Final Score = Average of all articles (0-100 scale)
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import os


# ============================================================================
# FINBERT SENTIMENT ANALYZER
# ============================================================================

class FinBERTAnalyzer:
    """
    FinBERT-based sentiment analyzer for financial news
    
    How FinBERT works:
    1. Tokenization: Converts text to tokens (words/subwords)
    2. Embedding: Converts tokens to numerical vectors
    3. BERT layers: 12 transformer layers process the context
    4. Classification head: Outputs probability for 3 classes
       - Positive (bullish, good news)
       - Negative (bearish, bad news)
       - Neutral (factual, no clear sentiment)
    """
    
    def __init__(self):
        """
        Initialize FinBERT model
        
        MODEL DETAILS:
        - Name: ProsusAI/finbert
        - Parameters: 110 million
        - Training data: Financial news, earnings calls, analyst reports
        - Accuracy: ~97% on financial sentiment classification
        """
        self.model = None
        self.tokenizer = None
        self.device = None
        self._load_model()
    
    def _load_model(self):
        """
        Load FinBERT model from HuggingFace
        
        STEPS:
        1. Check if transformers library is available
        2. Load tokenizer (converts text to tokens)
        3. Load model (the neural network)
        4. Set device (GPU preferred, CPU fallback)
        """
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            print("Loading FinBERT model...")
            
            # Load tokenizer and model
            model_name = "ProsusAI/finbert"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Check for GPU availability
            if torch.cuda.is_available():
                self.device = "cuda"
                gpu_name = torch.cuda.get_device_name(0)
                print(f"🎮 GPU detected: {gpu_name}")
                print(f"🎮 CUDA version: {torch.version.cuda}")
                self.model.to(self.device)
                print(f"✓ FinBERT loaded successfully on GPU ({gpu_name})")
            else:
                self.device = "cpu"
                print("⚠️ No GPU detected. Using CPU (slower)")
                print("💡 To use GPU, ensure CUDA is installed: https://pytorch.org/get-started/locally/")
                self.model.to(self.device)
                print(f"✓ FinBERT loaded on CPU")
            
            self.model.eval()  # Set to evaluation mode
            
        except ImportError:
            print("⚠️ transformers library not installed. Using simple sentiment analysis.")
            print("To use FinBERT, install: pip install transformers torch")
            self.model = None
        except Exception as e:
            print(f"⚠️ Error loading FinBERT: {e}")
            print("Falling back to simple sentiment analysis")
            self.model = None
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text
        
        Args:
            text: News title + description
        
        Returns:
            {
                'sentiment': 'positive'/'negative'/'neutral',
                'confidence': 0.95,  # 0-1
                'scores': {
                    'positive': 0.95,
                    'negative': 0.02,
                    'neutral': 0.03
                }
            }
        
        ALGORITHM:
        1. Tokenize text (max 512 tokens)
        2. Pass through BERT layers
        3. Get logits (raw scores) from classification head
        4. Apply softmax to get probabilities
        5. Return highest probability as sentiment
        """
        if not text or len(text) < 10:
            return {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'scores': {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
            }
        
        # If FinBERT not loaded, use simple analysis
        if self.model is None:
            return self._simple_sentiment(text)
        
        try:
            import torch
            
            # Tokenize input text
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
            
            # Convert logits to probabilities using softmax
            probs = torch.nn.functional.softmax(logits, dim=-1)[0]
            
            # Map to sentiment labels
            labels = ['negative', 'neutral', 'positive']
            sentiment_idx = torch.argmax(probs).item()
            sentiment = labels[sentiment_idx]
            confidence = probs[sentiment_idx].item()
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'scores': {
                    'negative': probs[0].item(),
                    'neutral': probs[1].item(),
                    'positive': probs[2].item()
                }
            }
            
        except Exception as e:
            print(f"Error in FinBERT analysis: {e}")
            return self._simple_sentiment(text)
    
    def _simple_sentiment(self, text: str) -> Dict:
        """
        Fallback: Simple keyword-based sentiment analysis
        
        Used when FinBERT is not available
        """
        text_lower = text.lower()
        
        # Positive keywords
        positive_words = [
            'profit', 'growth', 'gain', 'surge', 'rally', 'bullish',
            'beat', 'exceed', 'strong', 'positive', 'up', 'high',
            'success', 'win', 'best', 'top', 'soar', 'jump'
        ]
        
        # Negative keywords
        negative_words = [
            'loss', 'decline', 'fall', 'drop', 'bearish', 'weak',
            'miss', 'fail', 'down', 'low', 'worst', 'crash',
            'concern', 'worry', 'risk', 'threat', 'plunge'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(0.6 + (positive_count * 0.1), 0.9)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(0.6 + (negative_count * 0.1), 0.9)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'scores': {
                'positive': positive_count / max(positive_count + negative_count, 1),
                'negative': negative_count / max(positive_count + negative_count, 1),
                'neutral': 0.5
            }
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """
        Analyze multiple texts in batch (faster than one-by-one)
        
        Args:
            texts: List of news texts
        
        Returns:
            List of sentiment results
        """
        return [self.analyze_text(text) for text in texts]


# ============================================================================
# SENTIMENT AGGREGATION
# ============================================================================

def calculate_sentiment_score(news_articles: List[Dict], analyzer: FinBERTAnalyzer = None) -> Dict:
    """
    Aggregate sentiment from multiple news articles into single score
    
    ALGORITHM:
    1. Analyze each article with FinBERT
    2. Score each article:
       - Positive: 100 × confidence
       - Neutral: 50 × confidence
       - Negative: 0 × confidence
    3. Calculate weighted average (recent news weighted more)
    4. Bonus points for specific events (earnings beat, upgrades, etc.)
    
    Args:
        news_articles: List of {'title': str, 'description': str, 'date': datetime}
        analyzer: FinBERTAnalyzer instance
    
    Returns:
        {
            'sentiment_score': 75,  # 0-100
            'positive_count': 10,
            'negative_count': 2,
            'neutral_count': 5,
            'recent_sentiment': 'Mostly positive',
            'breakdown': {...}
        }
    """
    if not news_articles:
        return {
            'sentiment_score': 50,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'recent_sentiment': 'No news available',
            'breakdown': {}
        }
    
    if analyzer is None:
        analyzer = FinBERTAnalyzer()
    
    article_scores = []
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    
    for article in news_articles:
        # Combine title and description for analysis
        text = f"{article.get('title', '')} {article.get('description', '')}"
        
        # Analyze sentiment
        sentiment_result = analyzer.analyze_text(text)
        
        # Calculate article score (0-100)
        if sentiment_result['sentiment'] == 'positive':
            article_score = 100 * sentiment_result['confidence']
        elif sentiment_result['sentiment'] == 'neutral':
            article_score = 50 * sentiment_result['confidence']
        else:  # negative
            article_score = 0
        
        # Weight recent articles more (last 7 days get 1.5x weight)
        article_date = article.get('date', datetime.now())
        if isinstance(article_date, str):
            article_date = datetime.fromisoformat(article_date.replace('Z', '+00:00'))
        
        days_ago = (datetime.now() - article_date.replace(tzinfo=None)).days
        weight = 1.5 if days_ago <= 7 else 1.0
        
        article_scores.append({
            'score': article_score,
            'weight': weight,
            'sentiment': sentiment_result['sentiment'],
            'confidence': sentiment_result['confidence']
        })
        
        sentiment_counts[sentiment_result['sentiment']] += 1
    
    # Calculate weighted average
    total_weight = sum(a['weight'] for a in article_scores)
    if total_weight > 0:
        weighted_score = sum(a['score'] * a['weight'] for a in article_scores) / total_weight
    else:
        weighted_score = 50
    
    # Apply bonus points for specific keywords
    bonus_keywords = {
        'earnings beat': 10,
        'upgraded': 10,
        'new product': 5,
        'partnership': 5,
        'acquisition': 5,
        'regulatory approval': 10
    }
    
    bonus_points = 0
    for article in news_articles[:5]:  # Check recent 5 articles
        text = f"{article.get('title', '')} {article.get('description', '')}".lower()
        for keyword, points in bonus_keywords.items():
            if keyword in text:
                bonus_points += points
                break  # One bonus per article
    
    final_score = min(weighted_score + bonus_points, 100)
    
    # Determine recent sentiment trend
    total_articles = len(news_articles)
    positive_pct = sentiment_counts['positive'] / total_articles
    negative_pct = sentiment_counts['negative'] / total_articles
    
    if positive_pct > 0.6:
        recent_sentiment = "Mostly positive"
    elif negative_pct > 0.6:
        recent_sentiment = "Mostly negative"
    elif positive_pct > negative_pct:
        recent_sentiment = "Cautiously positive"
    elif negative_pct > positive_pct:
        recent_sentiment = "Cautiously negative"
    else:
        recent_sentiment = "Mixed/Neutral"
    
    return {
        'sentiment_score': final_score,
        'positive_count': sentiment_counts['positive'],
        'negative_count': sentiment_counts['negative'],
        'neutral_count': sentiment_counts['neutral'],
        'recent_sentiment': recent_sentiment,
        'breakdown': {
            'positive_pct': f"{positive_pct:.1%}",
            'negative_pct': f"{negative_pct:.1%}",
            'total_articles': total_articles,
            'bonus_points': bonus_points
        }
    }


# ============================================================================
# DATA AGGREGATION FROM DATABASE
# ============================================================================

def get_asset_news_from_db(db: Session, asset_id: int, days: int = 30) -> List[Dict]:
    """
    Fetch news articles for an asset from database
    
    Args:
        db: Database session
        asset_id: Asset ID
        days: Number of days to look back (default 30)
    
    Returns:
        List of news articles
    """
    try:
        from models.news_article import NewsArticle
        from models import news_asset_map
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Query news articles linked to this asset
        articles = db.query(NewsArticle).join(
            news_asset_map.NewsAssetMap,
            NewsArticle.id == news_asset_map.NewsAssetMap.article_id
        ).filter(
            news_asset_map.NewsAssetMap.asset_id == asset_id,
            NewsArticle.published_at >= cutoff_date
        ).order_by(NewsArticle.published_at.desc()).limit(50).all()
        
        return [{
            'title': article.title,
            'description': article.description or '',
            'date': article.published_at,
            'url': article.url
        } for article in articles]
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []


def get_fundamentals_from_db(db: Session, asset_id: int) -> Dict:
    """
    Fetch latest fundamental data for an asset
    
    Returns:
        Dictionary with all fundamental metrics
    """
    try:
        from models.quarterly_fundamental import QuarterlyFundamental
        from models.assets import Asset
        
        # Get latest 2 quarters for growth calculations
        fundamentals = db.query(QuarterlyFundamental).filter(
            QuarterlyFundamental.asset_id == asset_id
        ).order_by(QuarterlyFundamental.report_date.desc()).limit(2).all()
        
        if not fundamentals:
            return {}
        
        current = fundamentals[0]
        previous = fundamentals[1] if len(fundamentals) > 1 else None
        
        # Get asset data for dividend yield
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        
        return {
            'price_to_earnings_ratio': current.price_to_earnings_ratio,
            'return_on_equity': current.return_on_equity,
            'total_revenue_current': current.total_revenue,
            'total_revenue_previous': previous.total_revenue if previous else None,
            'net_income': current.net_income,
            'total_debt': current.total_debt,
            'total_equity': current.total_revenue - current.total_debt if current.total_revenue and current.total_debt else None,
            'dividend_yield': asset.dividend_yield if asset else None
        }
        
    except Exception as e:
        print(f"Error fetching fundamentals: {e}")
        return {}


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def analyze_asset(db: Session, asset_id: int, asset_type: str = 'stock') -> Dict:
    """
    Complete analysis of an asset
    
    Runs:
    1. Technical analysis (from scoring.py)
    2. Fundamental analysis (from scoring.py)
    3. Sentiment analysis (FinBERT)
    4. Risk analysis (from scoring.py)
    
    Returns:
        Complete analysis with all scores
    """
    from recommendation_engine.scoring import (
        get_asset_prices_from_db,
        calculate_technical_score,
        calculate_fundamental_score_stock,
        calculate_risk_score
    )
    
    # Get price data
    prices_df = get_asset_prices_from_db(db, asset_id, days=365)
    
    if prices_df.empty:
        return {
            'success': False,
            'error': 'No price data available'
        }
    
    # Calculate technical score
    technical = calculate_technical_score(prices_df)
    
    # Calculate fundamental score
    fundamentals_data = get_fundamentals_from_db(db, asset_id)
    if asset_type == 'stock':
        fundamental = calculate_fundamental_score_stock(fundamentals_data)
    else:
        fundamental = {'fundamental_score': 50, 'breakdown': {}}
    
    # Calculate sentiment score
    news_articles = get_asset_news_from_db(db, asset_id, days=30)
    sentiment = calculate_sentiment_score(news_articles)
    
    # Calculate risk score
    risk = calculate_risk_score(prices_df)
    
    # Calculate final weighted score
    final_score = (
        technical['technical_score'] * 0.25 +
        fundamental['fundamental_score'] * 0.30 +
        sentiment['sentiment_score'] * 0.25 +
        risk['risk_score'] * 0.20
    )
    
    return {
        'success': True,
        'final_score': final_score,
        'technical': technical,
        'fundamental': fundamental,
        'sentiment': sentiment,
        'risk': risk
    }
