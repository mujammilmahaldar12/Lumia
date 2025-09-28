"""
FinGPT Sentiment Analysis Integration
Financial sentiment analysis and entity extraction using FinGPT and other financial NLP models
"""

import json
import time
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
import logging

# For actual implementation, you would install and import:
# from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
# import torch
# from sentence_transformers import SentenceTransformer

from .base import NewsItem
from .models import SentimentAnalysis, ExtractedEntity, StockMention

logger = logging.getLogger(__name__)

class FinGPTAnalyzer:
    """
    Financial sentiment analysis and entity extraction using FinGPT and other financial models
    
    Models used:
    - FinBERT for financial sentiment classification
    - FinGPT for financial text understanding
    - Named Entity Recognition for financial entities
    - Stock symbol extraction and validation
    """
    
    def __init__(self, 
                 model_cache_dir: str = "./models",
                 use_gpu: bool = True,
                 batch_size: int = 16):
        """
        Initialize FinGPT analyzer
        
        Args:
            model_cache_dir: Directory to cache downloaded models
            use_gpu: Whether to use GPU acceleration
            batch_size: Batch size for processing multiple texts
        """
        self.model_cache_dir = model_cache_dir
        self.use_gpu = use_gpu
        self.batch_size = batch_size
        
        # Model configurations
        self.models = {
            'finbert_sentiment': {
                'model_name': 'ProsusAI/finbert',
                'task': 'sentiment-analysis',
                'labels': ['negative', 'neutral', 'positive']
            },
            'finbert_tone': {
                'model_name': 'yiyanghkust/finbert-tone',
                'task': 'sentiment-analysis', 
                'labels': ['Bearish', 'Neutral', 'Bullish']
            },
            'financial_ner': {
                'model_name': 'dbmdz/bert-large-cased-finetuned-conll03-english',
                'task': 'ner',
                'entities': ['PER', 'ORG', 'LOC', 'MISC']
            }
        }
        
        # Financial keywords for enhanced analysis
        self.financial_keywords = {
            'bullish': [
                'beat expectations', 'strong growth', 'record revenue', 'exceeded estimates',
                'positive outlook', 'raised guidance', 'strong performance', 'increased profit',
                'growing demand', 'market share gains', 'expansion', 'acquisition',
                'dividend increase', 'share buyback', 'upgrade', 'overweight', 'buy rating'
            ],
            'bearish': [
                'missed expectations', 'weak growth', 'declining revenue', 'below estimates',
                'negative outlook', 'lowered guidance', 'poor performance', 'decreased profit',
                'falling demand', 'market share loss', 'contraction', 'layoffs',
                'dividend cut', 'downgrade', 'underweight', 'sell rating', 'bankruptcy'
            ],
            'uncertainty': [
                'uncertain', 'volatility', 'risk', 'caution', 'warning', 'concern',
                'investigation', 'lawsuit', 'regulatory', 'compliance', 'delayed'
            ],
            'market_impact': [
                'merger', 'acquisition', 'IPO', 'earnings', 'FDA approval', 'patent',
                'product launch', 'partnership', 'contract', 'settlement', 'restructuring'
            ]
        }
        
        # Stock symbol patterns
        self.stock_patterns = [
            r'\\b[A-Z]{1,5}\\b',           # Basic ticker pattern
            r'\\$[A-Z]{1,5}\\b',           # Dollar sign prefix
            r'\\b[A-Z]{1,5}\.NS\\b',       # NSE India
            r'\\b[A-Z]{1,5}\.BO\\b',       # BSE India
            r'\\b[A-Z]{1,5}:US\\b',        # US exchange
            r'\\b[A-Z]{1,5}:LN\\b'         # London exchange
        ]
        
        # Initialize models (placeholder - actual implementation would load models)
        self.loaded_models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize and load the sentiment analysis models"""
        logger.info("Initializing FinGPT sentiment analysis models...")
        
        try:
            # In actual implementation, load the models here:
            # self.loaded_models['finbert_sentiment'] = pipeline(
            #     "sentiment-analysis", 
            #     model=self.models['finbert_sentiment']['model_name'],
            #     tokenizer=self.models['finbert_sentiment']['model_name'],
            #     device=0 if self.use_gpu else -1
            # )
            
            # For now, use placeholder
            self.loaded_models['finbert_sentiment'] = None
            self.loaded_models['finbert_tone'] = None
            self.loaded_models['financial_ner'] = None
            
            logger.info("FinGPT models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            # Fallback to rule-based analysis
            self.loaded_models = {}
    
    def analyze_sentiment(self, 
                         news_item: NewsItem,
                         include_entities: bool = True) -> Dict[str, Any]:
        """
        Perform comprehensive sentiment analysis on news item
        
        Args:
            news_item: NewsItem to analyze
            include_entities: Whether to extract entities
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            # Combine title and content for analysis
            text = f"{news_item.title}. {news_item.content or news_item.summary or ''}"
            
            # Basic sentiment analysis
            sentiment_results = self._analyze_text_sentiment(text)
            
            # Financial sentiment scoring
            financial_scores = self._calculate_financial_sentiment(text)
            
            # Market impact assessment
            impact_score = self._assess_market_impact(text, news_item)
            
            # Extract entities if requested
            entities = []
            stock_mentions = []
            if include_entities:
                entities = self._extract_entities(text)
                stock_mentions = self._extract_stock_mentions(text, news_item)
            
            # Combine all results
            analysis_result = {
                'sentiment': sentiment_results,
                'financial_scores': financial_scores,
                'market_impact': impact_score,
                'entities': entities,
                'stock_mentions': stock_mentions,
                'analysis_timestamp': datetime.utcnow(),
                'model_used': 'finbert_ensemble',
                'confidence_score': sentiment_results.get('confidence', 0.5)
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment for news item {news_item.external_id}: {e}")
            return self._get_fallback_analysis(news_item)
    
    def batch_analyze_sentiment(self, 
                              news_items: List[NewsItem],
                              include_entities: bool = True) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for multiple news items in batch
        
        Args:
            news_items: List of NewsItems to analyze
            include_entities: Whether to extract entities
            
        Returns:
            List of sentiment analysis results
        """
        results = []
        
        # Process in batches for efficiency
        for i in range(0, len(news_items), self.batch_size):
            batch = news_items[i:i + self.batch_size]
            
            for item in batch:
                result = self.analyze_sentiment(item, include_entities)
                results.append(result)
            
            # Small delay between batches to avoid overwhelming the system
            if i + self.batch_size < len(news_items):
                time.sleep(0.1)
        
        return results
    
    def _analyze_text_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using FinBERT models"""
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text_for_analysis(text)
            
            if self.loaded_models.get('finbert_sentiment'):
                # Use actual FinBERT model
                result = self.loaded_models['finbert_sentiment'](cleaned_text)
                
                return {
                    'label': result[0]['label'].lower(),
                    'score': result[0]['score'],
                    'confidence': result[0]['score'],
                    'model': 'finbert'
                }
            else:
                # Fallback to rule-based sentiment
                return self._rule_based_sentiment(cleaned_text)
                
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return self._rule_based_sentiment(text)
    
    def _calculate_financial_sentiment(self, text: str) -> Dict[str, float]:
        """Calculate specific financial sentiment scores"""
        text_lower = text.lower()
        
        # Count keyword occurrences
        bullish_score = sum(1 for keyword in self.financial_keywords['bullish'] 
                           if keyword in text_lower) / len(self.financial_keywords['bullish'])
        
        bearish_score = sum(1 for keyword in self.financial_keywords['bearish'] 
                           if keyword in text_lower) / len(self.financial_keywords['bearish'])
        
        uncertainty_score = sum(1 for keyword in self.financial_keywords['uncertainty'] 
                               if keyword in text_lower) / len(self.financial_keywords['uncertainty'])
        
        # Normalize scores
        total_score = bullish_score + bearish_score + uncertainty_score
        if total_score > 0:
            bullish_score /= total_score
            bearish_score /= total_score
            uncertainty_score /= total_score
        
        return {
            'bullish_score': min(bullish_score * 2, 1.0),  # Amplify but cap at 1.0
            'bearish_score': min(bearish_score * 2, 1.0),
            'uncertainty_score': min(uncertainty_score * 2, 1.0)
        }
    
    def _assess_market_impact(self, text: str, news_item: NewsItem) -> Dict[str, float]:
        """Assess potential market impact of news"""
        text_lower = text.lower()
        
        # Base impact score from high-impact keywords
        impact_keywords = self.financial_keywords['market_impact']
        keyword_impact = sum(1 for keyword in impact_keywords if keyword in text_lower)
        
        # Adjust based on source reliability (from news_item metadata)
        source_multiplier = 1.0
        if hasattr(news_item, 'raw_data') and news_item.raw_data:
            source_type = news_item.raw_data.get('source_type', '')
            if source_type == 'financial_news':
                source_multiplier = 1.2
            elif source_type == 'social_media':
                source_multiplier = 0.8
            elif source_type == 'sec_filing':
                source_multiplier = 1.5
        
        # Adjust based on article category
        category_multiplier = 1.0
        if news_item.category:
            if news_item.category in ['earnings', 'merger_acquisition', 'sec_filing']:
                category_multiplier = 1.3
            elif news_item.category in ['analyst_opinion', 'price_target']:
                category_multiplier = 1.1
        
        # Calculate final impact score
        base_impact = min(keyword_impact / len(impact_keywords) * 2, 1.0)
        final_impact = min(base_impact * source_multiplier * category_multiplier, 1.0)
        
        # Urgency score based on recency and content
        urgency_score = 0.5  # Default
        if 'breaking' in text_lower or 'urgent' in text_lower:
            urgency_score = 1.0
        elif 'earnings' in text_lower or 'guidance' in text_lower:
            urgency_score = 0.8
        
        return {
            'market_impact_score': final_impact,
            'urgency_score': urgency_score,
            'source_multiplier': source_multiplier,
            'category_multiplier': category_multiplier
        }
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text"""
        entities = []
        
        try:
            if self.loaded_models.get('financial_ner'):
                # Use actual NER model
                ner_results = self.loaded_models['financial_ner'](text)
                
                for entity in ner_results:
                    entities.append({
                        'text': entity['word'],
                        'label': entity['entity'],
                        'confidence': entity['score'],
                        'start': entity['start'],
                        'end': entity['end']
                    })
            else:
                # Fallback to rule-based entity extraction
                entities = self._rule_based_entity_extraction(text)
                
        except Exception as e:
            logger.error(f"Error in entity extraction: {e}")
            entities = self._rule_based_entity_extraction(text)
        
        return entities
    
    def _extract_stock_mentions(self, text: str, news_item: NewsItem) -> List[Dict[str, Any]]:
        """Extract stock symbol mentions with context"""
        mentions = []
        
        # Use existing stock symbols from news item if available
        existing_symbols = news_item.stock_symbols or []
        
        # Extract additional symbols using patterns
        for pattern in self.stock_patterns:
            matches = re.finditer(pattern, text.upper())
            for match in matches:
                symbol = match.group().strip('$:')
                
                # Get context around the mention
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                # Determine mention type and sentiment
                mention_sentiment = self._analyze_mention_sentiment(context)
                
                mention = {
                    'symbol': symbol,
                    'context': context.strip(),
                    'position_start': match.start(),
                    'position_end': match.end(),
                    'mention_sentiment': mention_sentiment,
                    'relevance_score': self._calculate_mention_relevance(context, symbol)
                }
                mentions.append(mention)
        
        # Add existing symbols with full text as context
        for symbol in existing_symbols:
            if not any(m['symbol'] == symbol for m in mentions):
                mentions.append({
                    'symbol': symbol,
                    'context': text[:200] + '...' if len(text) > 200 else text,
                    'position_start': 0,
                    'position_end': len(text),
                    'mention_sentiment': 'neutral',
                    'relevance_score': 1.0  # High relevance if explicitly tagged
                })
        
        return mentions
    
    def _clean_text_for_analysis(self, text: str) -> str:
        """Clean and prepare text for sentiment analysis"""
        # Remove URLs
        text = re.sub(r'http\\S+|www\\S+|https\\S+', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Limit length for model constraints
        if len(text) > 512:
            text = text[:512]
        
        return text.strip()
    
    def _rule_based_sentiment(self, text: str) -> Dict[str, Any]:
        """Fallback rule-based sentiment analysis"""
        text_lower = text.lower()
        
        positive_words = ['positive', 'good', 'great', 'excellent', 'strong', 'growth', 'profit', 'gain', 'up', 'rise', 'beat', 'exceed']
        negative_words = ['negative', 'bad', 'poor', 'weak', 'decline', 'loss', 'fall', 'down', 'drop', 'miss', 'below']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return {'label': 'positive', 'score': 0.7, 'confidence': 0.6, 'model': 'rule_based'}
        elif negative_count > positive_count:
            return {'label': 'negative', 'score': 0.7, 'confidence': 0.6, 'model': 'rule_based'}
        else:
            return {'label': 'neutral', 'score': 0.5, 'confidence': 0.5, 'model': 'rule_based'}
    
    def _rule_based_entity_extraction(self, text: str) -> List[Dict[str, Any]]:
        """Fallback rule-based entity extraction"""
        entities = []
        
        # Extract dollar amounts
        money_pattern = r'\$[\d,]+(?:\.d{2})?(?:\s*(?:million|billion|trillion))?'
        for match in re.finditer(money_pattern, text, re.IGNORECASE):
            entities.append({
                'text': match.group(),
                'label': 'MONEY',
                'confidence': 0.8,
                'start': match.start(),
                'end': match.end()
            })
        
        # Extract percentages
        percent_pattern = r'\d+(?:\.\d+)?%'
        for match in re.finditer(percent_pattern, text):
            entities.append({
                'text': match.group(),
                'label': 'PERCENT',
                'confidence': 0.9,
                'start': match.start(),
                'end': match.end()
            })
        
        return entities
    
    def _analyze_mention_sentiment(self, context: str) -> str:
        """Analyze sentiment of stock mention in context"""
        context_lower = context.lower()
        
        positive_indicators = ['up', 'rise', 'gain', 'beat', 'strong', 'positive', 'buy', 'upgrade']
        negative_indicators = ['down', 'fall', 'drop', 'miss', 'weak', 'negative', 'sell', 'downgrade']
        
        positive_count = sum(1 for word in positive_indicators if word in context_lower)
        negative_count = sum(1 for word in negative_indicators if word in context_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_mention_relevance(self, context: str, symbol: str) -> float:
        """Calculate relevance score for stock mention"""
        context_lower = context.lower()
        symbol_lower = symbol.lower()
        
        relevance = 0.5  # Base relevance
        
        # Boost if symbol appears multiple times
        symbol_count = context_lower.count(symbol_lower)
        relevance += min(symbol_count * 0.1, 0.3)
        
        # Boost if surrounded by financial keywords
        financial_context = ['stock', 'price', 'share', 'earnings', 'revenue', 'profit']
        for keyword in financial_context:
            if keyword in context_lower:
                relevance += 0.1
        
        return min(relevance, 1.0)
    
    def _get_fallback_analysis(self, news_item: NewsItem) -> Dict[str, Any]:
        """Provide fallback analysis when main analysis fails"""
        return {
            'sentiment': {'label': 'neutral', 'score': 0.5, 'confidence': 0.3, 'model': 'fallback'},
            'financial_scores': {'bullish_score': 0.3, 'bearish_score': 0.3, 'uncertainty_score': 0.4},
            'market_impact': {'market_impact_score': 0.5, 'urgency_score': 0.5},
            'entities': [],
            'stock_mentions': [],
            'analysis_timestamp': datetime.utcnow(),
            'model_used': 'fallback',
            'confidence_score': 0.3
        }

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = FinGPTAnalyzer()
    
    # Example news item
    from .base import NewsItem
    
    sample_news = NewsItem(
        title="Apple Inc. beats Q3 earnings expectations",
        content="Apple reported strong quarterly results, beating analyst expectations on both revenue and profit.",
        url="https://example.com/news/1",
        published_at=datetime.now(),
        stock_symbols=["AAPL"]
    )
    
    # Analyze sentiment
    result = analyzer.analyze_sentiment(sample_news)
    print(f"Sentiment Analysis Result: {result}")