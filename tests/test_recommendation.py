"""Unit tests for Recommendation API endpoint."""

import pytest
from unittest.mock import Mock, patch
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.routes.recommend import router, RecommendationEngine, RecommendationRequest


class TestRecommendationAPI:
    """Test cases for Recommendation API."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_universe(self):
        """Sample investment universe for testing."""
        return [
            {
                'asset_id': 1,
                'symbol': 'AAPL',
                'name': 'Apple Inc.',
                'type': 'stock',
                'market_cap': 3000000000000,
                'expected_return': 0.12,
                'volatility': 0.15,
                'sentiment': 0.3,
                'fundamental_score': 0.8,
                'momentum': 0.05
            },
            {
                'asset_id': 2,
                'symbol': 'TSLA',
                'name': 'Tesla Inc.',
                'type': 'stock',
                'market_cap': 800000000000,
                'expected_return': 0.15,
                'volatility': 0.35,
                'sentiment': 0.1,
                'fundamental_score': 0.6,
                'momentum': 0.10
            },
            {
                'asset_id': 3,
                'symbol': 'SPY',
                'name': 'SPDR S&P 500 ETF',
                'type': 'etf',
                'market_cap': 400000000000,
                'expected_return': 0.08,
                'volatility': 0.12,
                'sentiment': 0.0,
                'fundamental_score': 0.7,
                'momentum': 0.03
            }
        ]
    
    def test_recommendation_request_validation(self):
        """Test request model validation."""
        # Valid request
        valid_request = RecommendationRequest(
            capital=10000.0,
            risk=0.5,
            horizon_years=5,
            exclusions=['TSLA']
        )
        assert valid_request.capital == 10000.0
        assert valid_request.risk == 0.5
        
        # Invalid capital (negative)
        with pytest.raises(ValueError):
            RecommendationRequest(
                capital=-1000.0,
                risk=0.5,
                horizon_years=5
            )
        
        # Invalid risk (out of range)
        with pytest.raises(ValueError):
            RecommendationRequest(
                capital=10000.0,
                risk=1.5,  # > 1.0
                horizon_years=5
            )
    
    @patch('app.routes.recommend.get_db')
    def test_get_recommendations_success(self, mock_get_db, client):
        """Test successful recommendation generation."""
        # Mock database session
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock the recommendation engine methods
        with patch.object(RecommendationEngine, 'build_universe') as mock_build_universe:
            with patch.object(RecommendationEngine, 'normalize_signals') as mock_normalize:
                with patch.object(RecommendationEngine, 'compute_scores') as mock_compute:
                    with patch.object(RecommendationEngine, 'allocate_capital') as mock_allocate:
                        with patch.object(RecommendationEngine, 'generate_explanation') as mock_explain:
                            
                            # Setup mock returns
                            mock_universe = [
                                {
                                    'asset_id': 1, 'symbol': 'AAPL', 'name': 'Apple Inc.', 'type': 'stock',
                                    'score': 0.85, 'breakdown': {'sentiment': 0.8, 'fundamental': 0.9, 'momentum': 0.8, 'volatility': 0.9}
                                }
                            ]
                            mock_build_universe.return_value = mock_universe
                            mock_normalize.return_value = mock_universe
                            mock_compute.return_value = mock_universe
                            mock_allocate.return_value = {
                                'stocks': [{'symbol': 'AAPL', 'name': 'Apple Inc.', 'allocated': 10000.0, 'percentage': 100.0, 'score': 0.85, 'breakdown': {}}],
                                'etfs': []
                            }
                            mock_explain.return_value = "Test explanation"
                            
                            # Make request
                            response = client.post("/recommend", json={
                                "capital": 10000.0,
                                "risk": 0.5,
                                "horizon_years": 5,
                                "exclusions": []
                            })
                            
                            assert response.status_code == 200
                            data = response.json()
                            assert data['total_allocated'] == 10000.0
                            assert len(data['buckets']['stocks']) == 1
                            assert data['buckets']['stocks'][0]['symbol'] == 'AAPL'
    
    @patch('app.routes.recommend.get_db')
    def test_get_recommendations_no_universe(self, mock_get_db, client):
        """Test recommendation when no suitable assets found."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        with patch.object(RecommendationEngine, 'build_universe', return_value=[]):
            response = client.post("/recommend", json={
                "capital": 10000.0,
                "risk": 0.5,
                "horizon_years": 5,
                "exclusions": []
            })
            
            assert response.status_code == 404
            assert "No suitable assets found" in response.json()['detail']
    
    def test_health_endpoint(self, client):
        """Test recommendation health endpoint."""
        response = client.get("/recommend/health")
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'


class TestRecommendationEngine:
    """Test cases for RecommendationEngine class."""
    
    @pytest.fixture
    def engine(self, mock_db_session):
        """Create RecommendationEngine instance."""
        return RecommendationEngine(mock_db_session)
    
    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        return Mock(spec=Session)
    
    def test_get_risk_profile(self, engine):
        """Test risk profile determination."""
        assert engine.get_risk_profile(0.2) == 'conservative'
        assert engine.get_risk_profile(0.5) == 'balanced'
        assert engine.get_risk_profile(0.8) == 'aggressive'
        assert engine.get_risk_profile(0.0) == 'conservative'
        assert engine.get_risk_profile(1.0) == 'aggressive'
    
    def test_build_universe(self, engine):
        """Test universe building with mock data."""
        # Mock database query
        mock_results = [
            Mock(
                id=1, symbol='AAPL', name='Apple Inc.', type='stock', market_cap=3000000000000,
                avg_sentiment=0.3, sentiment_30d_avg=0.2, return_30d=0.05, return_365d=0.12, 
                volatility_30d=0.15, fundamental_score=0.8
            ),
            Mock(
                id=2, symbol='SPY', name='SPDR S&P 500 ETF', type='etf', market_cap=400000000000,
                avg_sentiment=0.0, sentiment_30d_avg=0.0, return_30d=0.03, return_365d=0.08,
                volatility_30d=0.12, fundamental_score=0.7
            )
        ]
        
        # Mock the complex query chain
        mock_query = Mock()
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_results
        
        engine.db.query.return_value = mock_query
        
        universe = engine.build_universe(['TSLA'])
        
        assert len(universe) == 2
        assert universe[0]['symbol'] == 'AAPL'
        assert universe[1]['symbol'] == 'SPY'
        assert all('expected_return' in asset for asset in universe)
    
    def test_normalize_signals(self, engine, sample_universe):
        """Test signal normalization."""
        normalized = engine.normalize_signals(sample_universe.copy())
        
        # Check that normalized fields exist
        for asset in normalized:
            assert 'sentiment_normalized' in asset
            assert 'fundamental_normalized' in asset
            assert 'momentum_normalized' in asset
            assert 'volatility_normalized' in asset
            
            # Check range (should be 0-1)
            assert 0 <= asset['sentiment_normalized'] <= 1
            assert 0 <= asset['fundamental_normalized'] <= 1
            assert 0 <= asset['momentum_normalized'] <= 1
            assert 0 <= asset['volatility_normalized'] <= 1
    
    def test_compute_scores_conservative(self, engine, sample_universe):
        """Test score computation for conservative risk profile."""
        normalized_universe = engine.normalize_signals(sample_universe.copy())
        scored_universe = engine.compute_scores(normalized_universe, 'conservative')
        
        # Check that scores are computed
        for asset in scored_universe:
            assert 'score' in asset
            assert 'breakdown' in asset
            assert 0 <= asset['score'] <= 1
        
        # Check that universe is sorted by score
        scores = [asset['score'] for asset in scored_universe]
        assert scores == sorted(scores, reverse=True)
    
    def test_allocate_capital(self, engine, sample_universe):
        """Test capital allocation."""
        # Prepare universe with scores
        for i, asset in enumerate(sample_universe):
            asset['score'] = 0.8 - (i * 0.1)  # Decreasing scores
        
        allocation = engine.allocate_capital(sample_universe, 10000.0)
        
        # Check structure
        assert 'stocks' in allocation
        assert 'etfs' in allocation
        
        # Check allocations
        stocks = allocation['stocks']
        etfs = allocation['etfs']
        
        # Should have selected top stocks and ETFs
        assert len(stocks) <= 3
        assert len(etfs) <= 2
        
        # Check that allocations sum to capital (approximately)
        total_allocated = sum(asset['allocated'] for asset in stocks + etfs)
        assert abs(total_allocated - 10000.0) < 0.01  # Allow for rounding errors
        
        # Check that all assets have allocation info
        for asset in stocks + etfs:
            assert 'allocated' in asset
            assert 'percentage' in asset
            assert asset['allocated'] > 0
    
    def test_generate_explanation(self, engine):
        """Test explanation generation."""
        buckets = {
            'stocks': [
                {'symbol': 'AAPL', 'percentage': 60.0},
                {'symbol': 'MSFT', 'percentage': 20.0}
            ],
            'etfs': [
                {'symbol': 'SPY', 'percentage': 20.0}
            ]
        }
        
        explanation = engine.generate_explanation(buckets, 'balanced', 10)
        
        assert isinstance(explanation, str)
        assert 'balanced' in explanation
        assert '10-year' in explanation
        assert 'stocks' in explanation
        assert 'ETFs' in explanation
    
    def test_empty_universe_handling(self, engine):
        """Test handling of empty universe."""
        normalized = engine.normalize_signals([])
        assert normalized == []
        
        scored = engine.compute_scores([], 'balanced')
        assert scored == []
        
        allocation = engine.allocate_capital([], 10000.0)
        assert allocation['stocks'] == []
        assert allocation['etfs'] == []


# Integration test fixture
@pytest.fixture
def test_app():
    """Create test FastAPI app."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return app


# Example integration test (commented out - requires actual database)
"""
def test_recommendation_integration(test_app, test_database):
    # This would be a full integration test that:
    # 1. Uses real database with test data
    # 2. Makes actual HTTP requests
    # 3. Verifies end-to-end functionality
    
    client = TestClient(test_app)
    response = client.post("/recommend", json={
        "capital": 50000.0,
        "risk": 0.6,
        "horizon_years": 7,
        "exclusions": ["TSLA"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data['total_allocated'] <= 50000.0
    assert len(data['buckets']['stocks']) <= 3
    assert len(data['buckets']['etfs']) <= 2
"""