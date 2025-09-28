"""Unit tests for Sentiment Worker service."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.services.sentiment_worker import SentimentWorker
from models import NewsArticle, NewsAssetMap, NewsSentiment


class TestSentimentWorker:
    """Test cases for SentimentWorker service."""
    
    @pytest.fixture
    def mock_finbert_worker(self):
        """Create SentimentWorker with mocked FinBERT."""
        with patch.dict('os.environ', {'USE_FINBERT': 'true'}):
            with patch('transformers.pipeline') as mock_pipeline:
                mock_pipeline_instance = Mock()
                mock_pipeline.return_value = mock_pipeline_instance
                
                worker = SentimentWorker()
                worker.finbert_pipeline = mock_pipeline_instance
                return worker
    
    @pytest.fixture
    def mock_vader_worker(self):
        """Create SentimentWorker with mocked VADER."""
        with patch.dict('os.environ', {'USE_FINBERT': 'false'}):
            with patch('nltk.sentiment.SentimentIntensityAnalyzer') as mock_analyzer_class:
                mock_analyzer = Mock()
                mock_analyzer_class.return_value = mock_analyzer
                
                with patch('nltk.data.find'), patch('nltk.download'):
                    worker = SentimentWorker()
                    worker.vader_analyzer = mock_analyzer
                    return worker
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_article(self):
        """Sample article for testing."""
        article = Mock(spec=NewsArticle)
        article.id = 1
        article.title = "Apple reports strong quarterly earnings"
        article.summary = "Technology giant Apple Inc. exceeded expectations"
        article.is_processed = False
        return article
    
    def test_init_finbert_success(self):
        """Test successful FinBERT initialization."""
        with patch.dict('os.environ', {'USE_FINBERT': 'true'}):
            with patch('transformers.pipeline') as mock_pipeline:
                mock_pipeline_instance = Mock()
                mock_pipeline.return_value = mock_pipeline_instance
                
                worker = SentimentWorker()
                
                assert worker.use_finbert is True
                assert worker.finbert_pipeline == mock_pipeline_instance
                mock_pipeline.assert_called_once_with(
                    "sentiment-analysis",
                    model="yiyanghkust/finbert-tone",
                    tokenizer="yiyanghkust/finbert-tone"
                )
    
    def test_init_finbert_fallback_to_vader(self):
        """Test fallback to VADER when FinBERT fails."""
        with patch.dict('os.environ', {'USE_FINBERT': 'true'}):
            with patch('transformers.pipeline', side_effect=ImportError("No transformers")):
                with patch('nltk.sentiment.SentimentIntensityAnalyzer') as mock_analyzer_class:
                    with patch('nltk.data.find'), patch('nltk.download'):
                        mock_analyzer = Mock()
                        mock_analyzer_class.return_value = mock_analyzer
                        
                        worker = SentimentWorker()
                        
                        assert worker.use_finbert is False
                        assert worker.vader_analyzer == mock_analyzer
    
    def test_init_vader_success(self):
        """Test successful VADER initialization."""
        with patch.dict('os.environ', {'USE_FINBERT': 'false'}):
            with patch('nltk.sentiment.SentimentIntensityAnalyzer') as mock_analyzer_class:
                with patch('nltk.data.find'), patch('nltk.download'):
                    mock_analyzer = Mock()
                    mock_analyzer_class.return_value = mock_analyzer
                    
                    worker = SentimentWorker()
                    
                    assert worker.use_finbert is False
                    assert worker.vader_analyzer == mock_analyzer
    
    def test_analyze_with_finbert_positive(self, mock_finbert_worker):
        """Test FinBERT analysis with positive sentiment."""
        # Mock FinBERT response
        mock_finbert_worker.finbert_pipeline.return_value = [
            {'label': 'positive', 'score': 0.85}
        ]
        
        result = mock_finbert_worker.analyze_with_finbert("Great earnings report!")
        
        assert result['polarity'] == 0.85
        assert result['pos'] == 0.85
        assert result['neg'] == 0.0
        assert result['neu'] == 0.15
    
    def test_analyze_with_finbert_negative(self, mock_finbert_worker):
        """Test FinBERT analysis with negative sentiment."""
        mock_finbert_worker.finbert_pipeline.return_value = [
            {'label': 'negative', 'score': 0.75}
        ]
        
        result = mock_finbert_worker.analyze_with_finbert("Disappointing earnings")
        
        assert result['polarity'] == -0.75
        assert result['pos'] == 0.0
        assert result['neg'] == 0.75
        assert result['neu'] == 0.25
    
    def test_analyze_with_finbert_neutral(self, mock_finbert_worker):
        """Test FinBERT analysis with neutral sentiment."""
        mock_finbert_worker.finbert_pipeline.return_value = [
            {'label': 'neutral', 'score': 0.90}
        ]
        
        result = mock_finbert_worker.analyze_with_finbert("Regular earnings report")
        
        assert result['polarity'] == 0.0
        assert result['pos'] == 0.0
        assert result['neg'] == 0.0
        assert result['neu'] == 0.90
    
    def test_analyze_with_finbert_error_handling(self, mock_finbert_worker):
        """Test FinBERT error handling."""
        mock_finbert_worker.finbert_pipeline.side_effect = Exception("Model error")
        
        result = mock_finbert_worker.analyze_with_finbert("Test text")
        
        # Should return neutral scores on error
        assert result['polarity'] == 0.0
        assert result['neu'] == 1.0
    
    def test_analyze_with_vader(self, mock_vader_worker):
        """Test VADER sentiment analysis."""
        # Mock VADER response
        mock_vader_worker.vader_analyzer.polarity_scores.return_value = {
            'compound': 0.6,
            'pos': 0.7,
            'neg': 0.1,
            'neu': 0.2
        }
        
        result = mock_vader_worker.analyze_with_vader("Great news!")
        
        assert result['polarity'] == 0.6
        assert result['pos'] == 0.7
        assert result['neg'] == 0.1
        assert result['neu'] == 0.2
    
    def test_analyze_sentiment_finbert(self, mock_finbert_worker):
        """Test main sentiment analysis with FinBERT."""
        mock_finbert_worker.finbert_pipeline.return_value = [
            {'label': 'positive', 'score': 0.8}
        ]
        
        model_name, scores = mock_finbert_worker.analyze_sentiment("Positive news")
        
        assert model_name == "finbert"
        assert scores['polarity'] == 0.8
    
    def test_analyze_sentiment_vader(self, mock_vader_worker):
        """Test main sentiment analysis with VADER."""
        mock_vader_worker.vader_analyzer.polarity_scores.return_value = {
            'compound': 0.5, 'pos': 0.6, 'neg': 0.1, 'neu': 0.3
        }
        
        model_name, scores = mock_vader_worker.analyze_sentiment("Some news")
        
        assert model_name == "vader"
        assert scores['polarity'] == 0.5
    
    def test_get_unprocessed_articles(self, mock_vader_worker, mock_db_session):
        """Test retrieval of unprocessed articles."""
        # Mock query result
        mock_article = Mock()
        mock_article.asset_mappings = [Mock(asset_id=1), Mock(asset_id=2)]
        
        mock_query = Mock()
        mock_query.join.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.distinct.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_article]
        
        mock_db_session.query.return_value = mock_query
        
        result = mock_vader_worker.get_unprocessed_articles(mock_db_session, limit=100)
        
        assert len(result) == 1
        assert result[0][0] == mock_article
        assert result[0][1] == [1, 2]  # Asset IDs
    
    def test_store_sentiment_result(self, mock_vader_worker, mock_db_session):
        """Test storing sentiment analysis results."""
        scores = {'polarity': 0.5, 'pos': 0.6, 'neg': 0.1, 'neu': 0.3}
        
        with patch('models.NewsSentiment') as mock_sentiment_class:
            mock_sentiment = Mock()
            mock_sentiment_class.return_value = mock_sentiment
            
            mock_vader_worker.store_sentiment_result(
                mock_db_session, 
                article_id=1, 
                asset_id=2, 
                model_name="vader", 
                scores=scores
            )
            
            mock_sentiment_class.assert_called_once_with(
                article_id=1,
                asset_id=2,
                model_name="vader",
                polarity=0.5,
                pos=0.6,
                neg=0.1,
                neu=0.3
            )
            mock_db_session.add.assert_called_once_with(mock_sentiment)
    
    def test_process_article_sentiment(self, mock_vader_worker, mock_db_session, sample_article):
        """Test processing sentiment for a single article."""
        # Mock sentiment analysis
        mock_vader_worker.vader_analyzer.polarity_scores.return_value = {
            'compound': 0.4, 'pos': 0.5, 'neg': 0.1, 'neu': 0.4
        }
        
        with patch.object(mock_vader_worker, 'store_sentiment_result') as mock_store:
            records_created = mock_vader_worker.process_article_sentiment(
                mock_db_session, sample_article, [1, 2]
            )
            
            assert records_created == 2  # Two asset IDs
            assert sample_article.is_processed is True
            assert mock_store.call_count == 2
    
    def test_process_article_sentiment_no_text(self, mock_vader_worker, mock_db_session):
        """Test processing article with no text content."""
        empty_article = Mock()
        empty_article.id = 1
        empty_article.title = ""
        empty_article.summary = None
        
        records_created = mock_vader_worker.process_article_sentiment(
            mock_db_session, empty_article, [1]
        )
        
        assert records_created == 0
    
    @patch('app.services.sentiment_worker.SessionLocal')
    @patch.object(SentimentWorker, 'get_unprocessed_articles')
    @patch.object(SentimentWorker, 'process_article_sentiment')
    def test_process_sentiment_batch(self, mock_process_article, mock_get_unprocessed, 
                                   mock_session_local, mock_vader_worker):
        """Test batch processing of sentiment analysis."""
        # Setup mocks
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        sample_article = Mock()
        sample_article.id = 1
        mock_get_unprocessed.return_value = [(sample_article, [1, 2])]
        mock_process_article.return_value = 2
        
        # Execute
        stats = mock_vader_worker.process_sentiment_batch(limit=100)
        
        # Assertions
        assert stats['articles_processed'] == 1
        assert stats['sentiment_records_created'] == 2
        assert stats['errors'] == 0
        
        # Verify method calls
        mock_get_unprocessed.assert_called_once_with(mock_db, 100)
        mock_process_article.assert_called_once_with(mock_db, sample_article, [1, 2])
        mock_db.commit.assert_called_once()


# Test fixtures for integration tests
@pytest.fixture
def test_database_session():
    """Create test database session (for integration tests)."""
    # This would create a test database session
    # For now, return a mock
    return Mock(spec=Session)


# Integration test examples (commented out - would require actual models and database)
"""
def test_sentiment_worker_integration(test_database_session):
    # This would be an integration test that requires:
    # 1. Real database with test data
    # 2. Actual models imported
    # 3. Sample news articles in database
    
    worker = SentimentWorker()
    stats = worker.process_sentiment_batch(limit=10)
    assert stats['articles_processed'] >= 0
"""