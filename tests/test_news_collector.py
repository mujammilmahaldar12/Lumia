"""Unit tests for News Collector service."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.news_collector import NewsCollector
from models import NewsArticle, NewsAssetMap, Asset


class TestNewsCollector:
    """Test cases for NewsCollector service."""
    
    @pytest.fixture
    def collector(self):
        """Create a NewsCollector instance for testing."""
        with patch.dict('os.environ', {'NEWSAPI_KEY': 'test-key'}):
            return NewsCollector()
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_newsapi_response(self):
        """Sample NewsAPI response data."""
        return {
            'status': 'ok',
            'articles': [
                {
                    'url': 'https://example.com/article1',
                    'title': 'Apple Reports Strong Earnings',
                    'description': 'Apple Inc. reported better than expected quarterly earnings.',
                    'content': 'Full article content about Apple earnings...',
                    'source': {'name': 'TechNews'},
                    'author': 'John Doe',
                    'publishedAt': '2024-01-15T10:30:00Z'
                },
                {
                    'url': 'https://example.com/article2',
                    'title': 'Tesla Stock Surges on Production News',
                    'description': 'Tesla announces increased production capacity.',
                    'content': 'Tesla stock price increased after...',
                    'source': {'name': 'AutoNews'},
                    'author': 'Jane Smith',
                    'publishedAt': '2024-01-15T11:00:00Z'
                }
            ]
        }
    
    @pytest.fixture
    def sample_assets(self):
        """Sample asset data for testing."""
        return {
            1: ('AAPL', 'Apple Inc.'),
            2: ('TSLA', 'Tesla Inc.'),
            3: ('MSFT', 'Microsoft Corporation')
        }
    
    def test_init_with_api_key(self):
        """Test NewsCollector initialization with API key."""
        with patch.dict('os.environ', {'NEWSAPI_KEY': 'test-key-123'}):
            collector = NewsCollector()
            assert collector.api_key == 'test-key-123'
            assert collector.base_url == "https://newsapi.org/v2"
    
    def test_init_without_api_key(self):
        """Test NewsCollector initialization without API key raises error."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="NEWSAPI_KEY environment variable is required"):
                NewsCollector()
    
    @patch('requests.get')
    def test_fetch_financial_news_success(self, mock_get, collector, sample_newsapi_response):
        """Test successful news fetching from NewsAPI."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = sample_newsapi_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test the method
        articles = collector.fetch_financial_news(hours_back=24, page_size=100)
        
        # Assertions
        assert len(articles) == 2
        assert articles[0]['title'] == 'Apple Reports Strong Earnings'
        assert articles[1]['title'] == 'Tesla Stock Surges on Production News'
        
        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "https://newsapi.org/v2/everything"
        assert call_args[1]['params']['apiKey'] == 'test-key'
    
    @patch('requests.get')
    def test_fetch_financial_news_api_error(self, mock_get, collector):
        """Test handling of API errors."""
        # Mock API error response
        mock_response = Mock()
        mock_response.json.return_value = {'status': 'error', 'message': 'Invalid API key'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        articles = collector.fetch_financial_news()
        
        assert articles == []
    
    @patch('requests.get')
    def test_fetch_financial_news_network_error(self, mock_get, collector):
        """Test handling of network errors."""
        # Mock network error
        mock_get.side_effect = Exception("Network error")
        
        articles = collector.fetch_financial_news()
        
        assert articles == []
    
    def test_deduplicate_articles(self, collector, mock_db_session):
        """Test article deduplication logic."""
        # Mock existing URLs in database
        mock_db_session.query.return_value.all.return_value = [
            ('https://example.com/article1',),
            ('https://existing.com/old-article',)
        ]
        
        # Input articles (one existing, one new)
        articles = [
            {'url': 'https://example.com/article1', 'title': 'Existing Article'},
            {'url': 'https://example.com/article2', 'title': 'New Article'},
            {'url': 'https://example.com/article3', 'title': 'Another New Article'}
        ]
        
        new_articles = collector.deduplicate_articles(mock_db_session, articles)
        
        # Should return only the new articles
        assert len(new_articles) == 2
        assert new_articles[0]['url'] == 'https://example.com/article2'
        assert new_articles[1]['url'] == 'https://example.com/article3'
    
    def test_get_asset_mapping_data(self, collector, mock_db_session):
        """Test retrieval of asset data for mapping."""
        # Mock database query result
        mock_assets = [
            Mock(id=1, symbol='AAPL', name='Apple Inc.'),
            Mock(id=2, symbol='TSLA', name='Tesla Inc.'),
            Mock(id=3, symbol='MSFT', name='Microsoft Corporation')
        ]
        mock_db_session.query.return_value.filter.return_value.all.return_value = mock_assets
        
        asset_data = collector.get_asset_mapping_data(mock_db_session)
        
        expected = {
            1: ('AAPL', 'Apple Inc.'),
            2: ('TSLA', 'Tesla Inc.'),
            3: ('MSFT', 'Microsoft Corporation')
        }
        assert asset_data == expected
    
    def test_fuzzy_match_assets(self, collector, sample_assets):
        """Test fuzzy matching of assets in text."""
        # Test exact symbol match
        text = "AAPL stock price surged today"
        matches = collector.fuzzy_match_assets(text, sample_assets)
        
        assert len(matches) > 0
        assert matches[0][0] == 1  # AAPL asset_id
        assert matches[0][1] == 1.0  # Perfect score for exact match
    
    def test_fuzzy_match_assets_company_name(self, collector, sample_assets):
        """Test fuzzy matching with company names."""
        text = "Apple Inc reported strong earnings"
        matches = collector.fuzzy_match_assets(text, sample_assets)
        
        assert len(matches) > 0
        # Should find Apple match
        apple_matches = [m for m in matches if m[0] == 1]
        assert len(apple_matches) > 0
    
    def test_fuzzy_match_no_matches(self, collector, sample_assets):
        """Test fuzzy matching with no relevant matches."""
        text = "Weather forecast shows sunny skies"
        matches = collector.fuzzy_match_assets(text, sample_assets)
        
        # Should have no matches above threshold
        assert len(matches) == 0
    
    def test_store_article_success(self, collector, mock_db_session):
        """Test successful article storage."""
        article_data = {
            'url': 'https://example.com/test-article',
            'title': 'Test Article Title',
            'description': 'Test article description',
            'content': 'Full test article content',
            'source': {'name': 'TestSource'},
            'author': 'Test Author',
            'publishedAt': '2024-01-15T10:30:00Z'
        }
        
        # Mock the database operations
        mock_article = Mock()
        mock_article.id = 123
        mock_db_session.add = Mock()
        mock_db_session.flush = Mock()
        
        with patch('models.NewsArticle', return_value=mock_article):
            result = collector.store_article(mock_db_session, article_data)
        
        assert result == mock_article
        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()
    
    def test_store_article_invalid_date(self, collector, mock_db_session):
        """Test article storage with invalid date format."""
        article_data = {
            'url': 'https://example.com/test-article',
            'title': 'Test Article Title',
            'publishedAt': 'invalid-date-format'
        }
        
        mock_article = Mock()
        mock_article.id = 123
        mock_db_session.add = Mock()
        mock_db_session.flush = Mock()
        
        with patch('models.NewsArticle', return_value=mock_article):
            result = collector.store_article(mock_db_session, article_data)
        
        # Should still create article with None date
        assert result == mock_article
    
    def test_create_asset_mappings(self, collector, mock_db_session, sample_assets):
        """Test creation of asset mappings for an article."""
        # Mock article
        mock_article = Mock()
        mock_article.id = 123
        mock_article.title = "Apple Inc reports strong quarterly earnings"
        mock_article.summary = "Technology company Apple shows growth"
        
        # Mock database operations
        mock_db_session.add = Mock()
        
        with patch('models.NewsAssetMap') as mock_mapping_class:
            mappings_created = collector.create_asset_mappings(
                mock_db_session, mock_article, sample_assets
            )
        
        # Should create at least one mapping (for Apple)
        assert mappings_created > 0
        assert mock_db_session.add.call_count == mappings_created
    
    @patch('app.services.news_collector.SessionLocal')
    @patch.object(NewsCollector, 'fetch_financial_news')
    @patch.object(NewsCollector, 'deduplicate_articles')
    @patch.object(NewsCollector, 'get_asset_mapping_data')
    @patch.object(NewsCollector, 'store_article')
    @patch.object(NewsCollector, 'create_asset_mappings')
    def test_collect_and_store_news_integration(self, mock_create_mappings, mock_store_article,
                                              mock_get_assets, mock_deduplicate, mock_fetch,
                                              mock_session_local, collector, sample_newsapi_response):
        """Test the main collection and storage workflow."""
        # Setup mocks
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        mock_fetch.return_value = sample_newsapi_response['articles']
        mock_deduplicate.return_value = sample_newsapi_response['articles']
        mock_get_assets.return_value = {1: ('AAPL', 'Apple Inc.')}
        
        mock_article = Mock()
        mock_article.id = 123
        mock_store_article.return_value = mock_article
        mock_create_mappings.return_value = 2
        
        # Execute
        stats = collector.collect_and_store_news(hours_back=24)
        
        # Assertions
        assert stats['articles_fetched'] == 2
        assert stats['articles_new'] == 2
        assert stats['articles_stored'] == 2
        assert stats['mappings_created'] == 4  # 2 articles * 2 mappings each
        assert stats['errors'] == 0
        
        # Verify method calls
        mock_fetch.assert_called_once_with(hours_back=24)
        mock_deduplicate.assert_called_once()
        mock_store_article.call_count == 2
        mock_db.commit.assert_called_once()


# Test fixtures and utilities
@pytest.fixture
def mock_requests_get():
    """Mock requests.get for testing."""
    with patch('requests.get') as mock:
        yield mock


# Integration test (commented out - requires actual database)
"""
def test_news_collector_integration():
    # This would be an integration test that requires:
    # 1. Real database connection
    # 2. NewsAPI key
    # 3. Sample data in database
    
    # Example:
    # collector = NewsCollector()
    # stats = collector.collect_and_store_news(hours_back=1)
    # assert stats['articles_fetched'] >= 0
"""