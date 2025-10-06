"""
Expert Recommendation Engine
=============================

Combines all components to generate comprehensive stock recommendations:
- Technical Analysis (finbert.py)
- Sentiment Analysis (finbert.py) 
- AI Reasoning (fingpt.py)
- Fundamental Analysis (from database)
- Risk Assessment

This is the MAIN ENGINE that orchestrates everything.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Optional
import logging
from datetime import datetime

from database import SessionLocal
from models import Asset, QuarterlyFundamental, DailyPrice
from recommendation_engine.technical import TechnicalAnalyzer
from recommendation_engine.finbert import get_finbert_analyzer
from recommendation_engine.fingpt import get_fingpt_engine, RecommendationContext

logger = logging.getLogger(__name__)


class ExpertRecommendationEngine:
    """
    Main Expert Recommendation Engine
    
    Combines:
    - Technical Analysis (25%)
    - Fundamental Analysis (30%)
    - Sentiment Analysis (25%)
    - Risk Assessment (20%)
    
    Returns:
    - BUY/SELL/HOLD recommendation
    - Confidence score
    - Detailed reasoning
    - Target prices
    """
    
    def __init__(self):
        """Initialize the expert engine"""
        self.weights = {
            'technical': 0.25,
            'fundamental': 0.30,
            'sentiment': 0.25,
            'risk': 0.20
        }
        
        # Initialize analyzers (lazy loading)
        self.technical_analyzer = None
        self.sentiment_analyzer = None
        self.reasoning_engine = None
        
        logger.info("[EXPERT] Expert Recommendation Engine initialized")
    
    def analyze_stock(
        self, 
        symbol: str, 
        user_risk_profile: str = 'moderate',
        news_headlines: Optional[list] = None,
        fetch_live_news: bool = False,  # DISABLED: DuckDuckGo is blocking/slow
        db_session = None  # NEW: Allow passing existing session
    ) -> Dict:
        """
        Generate complete recommendation for a stock
        
        Args:
            symbol: Stock symbol (e.g., 'TCS.NS')
            user_risk_profile: 'conservative', 'moderate', or 'aggressive'
            news_headlines: Optional list of recent news headlines
            fetch_live_news: Whether to fetch live news if none provided
            db_session: Optional database session to reuse (prevents pool exhaustion)
        
        Returns:
            Complete recommendation dictionary with scores, reasoning, targets
        """
        logger.info(f"[EXPERT] Analyzing {symbol} for {user_risk_profile} risk profile")
        
        # Track if we need to close the session
        close_session = False
        
        try:
            # Get basic stock info
            if db_session is None:
                db = SessionLocal()
                close_session = True  # We created it, we close it
            else:
                db = db_session  # Reuse provided session
            
            asset = db.query(Asset).filter(Asset.symbol == symbol).first()
            
            if not asset:
                if close_session:
                    db.close()
                return self._stock_not_found_result(symbol)
            
            # Get current price
            latest_price = db.query(DailyPrice).filter(
                DailyPrice.asset_id == asset.id
            ).order_by(DailyPrice.date.desc()).first()
            
            if not latest_price:
                if close_session:
                    db.close()
                return self._no_price_data_result(symbol)
            
            current_price = float(latest_price.close_price)
            company_name = asset.name
            
            # Fetch news if not provided
            # NOTE: Live news fetching disabled due to DuckDuckGo blocking/rate limiting
            # Use database news only or provide headlines manually
            if news_headlines is None and fetch_live_news:
                try:
                    from news_collector.search_api import search
                    # Search for news using DuckDuckGo
                    query = f"{company_name} stock news"
                    search_results = search(query, max_results=5)
                    news_headlines = [r['title'] for r in search_results if r.get('title')]
                    if news_headlines:
                        logger.info(f"[NEWS] Fetched {len(news_headlines)} headlines for {symbol}")
                except Exception as e:
                    logger.debug(f"[NEWS] Could not fetch news for {symbol}: {e}")
                    news_headlines = None
            
            # 1. Technical Analysis (25%)
            technical_result = self._analyze_technical(symbol)
            technical_score = technical_result.get('score', 50)
            
            # 2. Fundamental Analysis (30%)
            fundamental_result = self._analyze_fundamental(asset.id, db)
            fundamental_score = fundamental_result.get('score', 50)
            
            # 3. Sentiment Analysis (25%)
            sentiment_result = self._analyze_sentiment(symbol, news_headlines)
            sentiment_score = sentiment_result.get('score', 50)
            
            # 4. Risk Assessment (20%)
            risk_result = self._analyze_risk(technical_result, user_risk_profile)
            risk_score = risk_result.get('score', 50)
            
            # Close database session if we created it
            if close_session:
                db.close()
            
            # Calculate overall score
            overall_score = (
                technical_score * self.weights['technical'] +
                fundamental_score * self.weights['fundamental'] +
                sentiment_score * self.weights['sentiment'] +
                risk_score * self.weights['risk']
            )
            
            # Determine action and confidence
            action, confidence = self._determine_action(overall_score, {
                'technical': technical_score,
                'fundamental': fundamental_score,
                'sentiment': sentiment_score,
                'risk': risk_score
            })
            
            # Generate AI reasoning
            reasoning = self._generate_reasoning(
                symbol=symbol,
                company_name=company_name,
                current_price=current_price,
                overall_score=overall_score,
                technical_score=technical_score,
                fundamental_score=fundamental_score,
                sentiment_score=sentiment_score,
                risk_score=risk_score,
                technical_data=technical_result.get('latest_values', {}),
                fundamental_data=fundamental_result.get('data', {}),
                sentiment_data=sentiment_result.get('data', {}),
                risk_data=risk_result.get('data', {}),
                news_headlines=news_headlines or [],
                user_risk_profile=user_risk_profile,
                action=action,
                confidence=confidence
            )
            
            # Calculate targets
            targets = self._calculate_targets(current_price, action, overall_score)
            
            # Return complete recommendation
            result = {
                'symbol': symbol,
                'company_name': company_name,
                'current_price': current_price,
                'recommendation': {
                    'action': action,
                    'confidence': round(confidence, 1),
                    'overall_score': round(overall_score, 1)
                },
                'scores': {
                    'technical': round(technical_score, 1),
                    'fundamental': round(fundamental_score, 1),
                    'sentiment': round(sentiment_score, 1),
                    'risk': round(risk_score, 1)
                },
                'reasoning': reasoning,
                'targets': targets,
                'details': {
                    'technical': technical_result,
                    'fundamental': fundamental_result,
                    'sentiment': sentiment_result,
                    'risk': risk_result
                },
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"[EXPERT] {symbol} → {action} (Score: {overall_score:.1f}, Confidence: {confidence:.1f}%)")
            return result
            
        except Exception as e:
            logger.error(f"[EXPERT] Error analyzing {symbol}: {e}")
            # Make sure to close database session on error
            try:
                if 'db' in locals() and db:
                    db.close()
            except:
                pass
            return self._error_result(symbol, str(e))
    
    def _analyze_technical(self, symbol: str) -> Dict:
        """Run technical analysis"""
        try:
            if self.technical_analyzer is None:
                self.technical_analyzer = TechnicalAnalyzer()
            
            result = self.technical_analyzer.analyze(symbol)
            return result
            
        except Exception as e:
            logger.error(f"[TECHNICAL] Error: {e}")
            return {'score': 50, 'error': str(e)}
    
    def _analyze_fundamental(self, asset_id: int, db) -> Dict:
        """Analyze fundamental data from database"""
        try:
            # Get latest fundamental data
            fundamental = db.query(QuarterlyFundamental).filter(
                QuarterlyFundamental.asset_id == asset_id
            ).order_by(QuarterlyFundamental.report_date.desc()).first()
            
            if not fundamental:
                logger.warning("[FUNDAMENTAL] No fundamental data available")
                return {'score': 50, 'data': {}, 'message': 'No fundamental data'}
            
            # Extract key metrics
            pe_ratio = float(fundamental.price_to_earnings_ratio) if fundamental.price_to_earnings_ratio else None
            roe = float(fundamental.return_on_equity) * 100 if fundamental.return_on_equity else None
            debt_to_equity = float(fundamental.debt_to_equity_ratio) if fundamental.debt_to_equity_ratio else None
            revenue_growth = float(fundamental.revenue_growth) * 100 if fundamental.revenue_growth else None
            profit_margin = float(fundamental.profit_margin) * 100 if fundamental.profit_margin else None
            
            # Score fundamentals (MORE REALISTIC)
            score = 50  # Base score
            
            # P/E Ratio scoring (lower is better, typically 15-25 is good)
            if pe_ratio:
                if 15 <= pe_ratio <= 25:
                    score += 15
                elif pe_ratio < 15:
                    score += 10  # Might be undervalued
                elif pe_ratio > 40:
                    score -= 20  # Very overvalued
                elif pe_ratio > 30:
                    score -= 10  # Overvalued
            
            # ROE scoring (higher is better, >15% is good)
            # FIXED: Check from low to high to avoid logic errors
            if roe is not None:
                if roe < 0:
                    score -= 25  # Losing money
                elif roe < 5:
                    score -= 15  # Poor
                elif roe < 10:
                    score += 0   # Below average
                elif roe < 15:
                    score += 5   # Acceptable
                elif roe < 25:
                    score += 12  # Good
                else:  # roe >= 25
                    score += 20  # Excellent
            
            # Debt scoring (lower is better, <0.5 is good)
            if debt_to_equity:
                if debt_to_equity < 0.3:
                    score += 15  # Very safe
                elif debt_to_equity < 0.5:
                    score += 10  # Good
                elif debt_to_equity > 5.0:
                    score -= 25  # Very high debt
                elif debt_to_equity > 2.0:
                    score -= 15  # High debt
            
            # Growth scoring (positive is good)
            if revenue_growth:
                if revenue_growth > 20:
                    score += 15  # High growth
                elif revenue_growth > 10:
                    score += 10  # Good growth
                elif revenue_growth > 5:
                    score += 5   # Moderate growth
                elif revenue_growth < -10:
                    score -= 20  # Declining badly
                elif revenue_growth < 0:
                    score -= 10  # Declining
            
            # Clamp score to 0-100
            score = max(0, min(100, score))
            
            return {
                'score': score,
                'data': {
                    'pe_ratio': pe_ratio,
                    'roe': roe,
                    'debt_to_equity': debt_to_equity,
                    'revenue_growth': revenue_growth,
                    'profit_margin': profit_margin
                }
            }
            
        except Exception as e:
            logger.error(f"[FUNDAMENTAL] Error: {e}")
            return {'score': 50, 'error': str(e)}
    
    def _analyze_sentiment(self, symbol: str, news_headlines: Optional[list]) -> Dict:
        """Analyze news sentiment"""
        try:
            if not news_headlines:
                # No news provided, return neutral
                # Suppressed warning to reduce noise (was: logger.warning)
                return {
                    'score': 50,
                    'data': {
                        'overall_sentiment': 'neutral',
                        'positive_count': 0,
                        'negative_count': 0
                    },
                    'message': 'No news data'
                }
            
            # Get sentiment analyzer
            if self.sentiment_analyzer is None:
                self.sentiment_analyzer = get_finbert_analyzer()
            
            # Analyze headlines
            result = self.sentiment_analyzer.analyze_aggregate(news_headlines)
            
            # Convert sentiment to score (0-100)
            sentiment = result['sentiment']
            confidence = result['confidence']
            
            if sentiment == 'positive':
                score = 50 + (confidence * 50)  # 50-100
            elif sentiment == 'negative':
                score = 50 - (confidence * 50)  # 0-50
            else:  # neutral
                score = 50
            
            # Count positive/negative
            positive_count = sum(1 for r in result.get('breakdown', []) if r['sentiment'] == 'positive')
            negative_count = sum(1 for r in result.get('breakdown', []) if r['sentiment'] == 'negative')
            
            return {
                'score': score,
                'data': {
                    'overall_sentiment': sentiment,
                    'positive_count': positive_count,
                    'negative_count': negative_count,
                    'confidence': confidence
                }
            }
            
        except Exception as e:
            logger.error(f"[SENTIMENT] Error: {e}")
            return {'score': 50, 'error': str(e)}
    
    def _analyze_risk(self, technical_result: Dict, user_risk_profile: str) -> Dict:
        """Assess risk and match to user profile"""
        try:
            # Get volatility indicators from technical analysis
            atr = technical_result.get('latest_values', {}).get('atr')
            price = technical_result.get('latest_values', {}).get('price')
            
            # Calculate volatility if data available
            if atr and price:
                volatility_percent = (atr / price) * 100
            else:
                volatility_percent = None
            
            # Simplified beta calculation (would need market data for real beta)
            # For now, use volatility as proxy
            if volatility_percent:
                if volatility_percent < 2:
                    beta = 0.8  # Low volatility
                    risk_level = 'low'
                elif volatility_percent < 4:
                    beta = 1.0  # Medium volatility
                    risk_level = 'moderate'
                else:
                    beta = 1.3  # High volatility
                    risk_level = 'high'
            else:
                beta = 1.0
                risk_level = 'moderate'
            
            # Match to user profile
            profile_match = {
                'conservative': {'low': 90, 'moderate': 60, 'high': 30},
                'moderate': {'low': 70, 'moderate': 85, 'high': 50},
                'aggressive': {'low': 50, 'moderate': 70, 'high': 90}
            }
            
            score = profile_match.get(user_risk_profile, {}).get(risk_level, 50)
            
            return {
                'score': score,
                'data': {
                    'beta': beta,
                    'volatility': risk_level,
                    'volatility_percent': volatility_percent,
                    'profile_match': 'excellent' if score >= 80 else 'good' if score >= 60 else 'fair'
                }
            }
            
        except Exception as e:
            logger.error(f"[RISK] Error: {e}")
            return {'score': 50, 'error': str(e)}
    
    def _determine_action(self, overall_score: float, scores: Dict) -> tuple:
        """Determine BUY/SELL/HOLD and confidence"""
        # Check if scores are consistent
        score_variance = max(scores.values()) - min(scores.values())
        
        # NEW: More realistic thresholds
        # BUY: Score >= 65 (was 60)
        # SELL: Score <= 40 (was 45) 
        # HOLD: Between 40-65
        
        if overall_score >= 70:
            action = 'BUY'
            confidence = overall_score - (score_variance * 0.2)
        elif overall_score >= 65:
            action = 'BUY'
            confidence = overall_score - (score_variance * 0.3) - 5
        elif overall_score <= 35:
            action = 'SELL'
            confidence = (100 - overall_score) - (score_variance * 0.2)
        elif overall_score <= 40:
            action = 'SELL'
            confidence = (100 - overall_score) - (score_variance * 0.3) - 5
        else:
            action = 'HOLD'
            confidence = 100 - abs(50 - overall_score) * 2 - (score_variance * 0.2)
        
        # Clamp confidence
        confidence = max(30, min(95, confidence))
        
        return action, confidence
    
    def _generate_reasoning(self, **kwargs) -> str:
        """Generate AI-powered reasoning"""
        try:
            # Get reasoning engine
            if self.reasoning_engine is None:
                self.reasoning_engine = get_fingpt_engine()
            
            # Create context
            context = RecommendationContext(
                symbol=kwargs['symbol'],
                company_name=kwargs['company_name'],
                current_price=kwargs['current_price'],
                technical_score=kwargs['technical_score'],
                fundamental_score=kwargs['fundamental_score'],
                sentiment_score=kwargs['sentiment_score'],
                risk_score=kwargs['risk_score'],
                overall_score=kwargs['overall_score'],
                technical_data=kwargs['technical_data'],
                fundamental_data=kwargs['fundamental_data'],
                sentiment_data=kwargs['sentiment_data'],
                risk_data=kwargs['risk_data'],
                news_headlines=kwargs['news_headlines'],
                user_risk_profile=kwargs['user_risk_profile'],
                action=kwargs['action'],
                confidence=kwargs['confidence']
            )
            
            # Generate reasoning
            reasoning = self.reasoning_engine.generate_recommendation(context)
            return reasoning
            
        except Exception as e:
            logger.error(f"[REASONING] Error: {e}")
            # Fallback to simple reasoning
            return f"Based on analysis, {kwargs['symbol']} scores {kwargs['overall_score']:.0f}/100, suggesting a {kwargs['action']} recommendation."
    
    def _calculate_targets(self, current_price: float, action: str, score: float) -> Dict:
        """Calculate entry, target, and stop loss prices"""
        if action == 'BUY':
            # For buy: target is upside, stop loss is downside protection
            upside_percent = 0.10 + (score / 100) * 0.10  # 10-20% based on score
            downside_percent = 0.05  # 5% stop loss
            
            entry = current_price
            target = current_price * (1 + upside_percent)
            stop_loss = current_price * (1 - downside_percent)
            timeframe = "3-6 months"
            
        elif action == 'SELL':
            # For sell: just suggest exit
            entry = current_price
            target = None
            stop_loss = None
            timeframe = "Immediate"
            
        else:  # HOLD
            entry = current_price
            target = current_price * 1.05  # 5% upside to reassess
            stop_loss = current_price * 0.95  # 5% downside to reassess
            timeframe = "Monitor"
        
        return {
            'entry': round(entry, 2),
            'target': round(target, 2) if target else None,
            'stop_loss': round(stop_loss, 2) if stop_loss else None,
            'timeframe': timeframe
        }
    
    def _stock_not_found_result(self, symbol: str) -> Dict:
        """Return result when stock not found"""
        return {
            'symbol': symbol,
            'error': 'Stock not found in database',
            'recommendation': {
                'action': 'HOLD',
                'confidence': 0,
                'overall_score': 0
            }
        }
    
    def _no_price_data_result(self, symbol: str) -> Dict:
        """Return result when no price data"""
        return {
            'symbol': symbol,
            'error': 'No price data available',
            'recommendation': {
                'action': 'HOLD',
                'confidence': 0,
                'overall_score': 0
            }
        }
    
    def _error_result(self, symbol: str, error: str) -> Dict:
        """Return result when error occurs"""
        return {
            'symbol': symbol,
            'error': error,
            'recommendation': {
                'action': 'HOLD',
                'confidence': 0,
                'overall_score': 0
            }
        }


# Convenience function
def get_recommendation(symbol: str, user_risk_profile: str = 'moderate', news_headlines: list = None) -> Dict:
    """
    Quick recommendation function
    
    Usage:
        result = get_recommendation('TCS.NS', 'moderate')
        print(result['recommendation']['action'])
        print(result['reasoning'])
    """
    engine = ExpertRecommendationEngine()
    return engine.analyze_stock(symbol, user_risk_profile, news_headlines)


if __name__ == "__main__":
    """Test the expert engine"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*80)
    print("EXPERT RECOMMENDATION ENGINE TEST")
    print("="*80 + "\n")
    
    # Test with a stock
    symbol = "TCS.NS"
    risk_profile = "moderate"
    
    # Sample news headlines
    news = [
        "TCS wins major contract with Microsoft",
        "Q2 earnings beat analyst estimates",
        "Stock price surges on positive outlook"
    ]
    
    print(f"Analyzing {symbol} for {risk_profile} risk profile...\n")
    
    result = get_recommendation(symbol, risk_profile, news)
    
    # Print results
    print(f"{'='*80}")
    print(f"RECOMMENDATION FOR {result.get('symbol', symbol)}")
    print(f"{'='*80}\n")
    
    print(f"Company: {result.get('company_name', 'N/A')}")
    print(f"Current Price: ₹{result.get('current_price', 0):.2f}\n")
    
    rec = result.get('recommendation', {})
    print(f"🎯 RECOMMENDATION: {rec.get('action', 'N/A')}")
    print(f"Confidence: {rec.get('confidence', 0):.1f}%")
    print(f"Overall Score: {rec.get('overall_score', 0):.1f}/100\n")
    
    scores = result.get('scores', {})
    print(f"📊 CATEGORY SCORES:")
    print(f"  Technical:    {scores.get('technical', 0):.1f}/100")
    print(f"  Fundamental:  {scores.get('fundamental', 0):.1f}/100")
    print(f"  Sentiment:    {scores.get('sentiment', 0):.1f}/100")
    print(f"  Risk Match:   {scores.get('risk', 0):.1f}/100\n")
    
    targets = result.get('targets', {})
    if targets:
        print(f"🎯 TARGETS:")
        print(f"  Entry:     ₹{targets.get('entry', 0):.2f}")
        if targets.get('target'):
            print(f"  Target:    ₹{targets.get('target', 0):.2f}")
        if targets.get('stop_loss'):
            print(f"  Stop Loss: ₹{targets.get('stop_loss', 0):.2f}")
        print(f"  Timeframe: {targets.get('timeframe', 'N/A')}\n")
    
    print(f"💡 REASONING:")
    print(f"{result.get('reasoning', 'No reasoning available')}\n")
    
    print("="*80)
    print("✅ TEST COMPLETE")
    print("="*80 + "\n")
