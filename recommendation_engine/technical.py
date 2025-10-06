"""
Technical Indicators Calculator
================================

Calculates 20+ technical indicators and combines them into a single score (0-100).
See TECHNICAL.md for detailed explanation of each indicator.

CATEGORIES (with weights):
- Momentum (35%): RSI, Stochastic, Momentum
- Trend (35%): MACD, Moving Averages, ADX  
- Volatility (20%): Bollinger Bands, ATR
- Volume (10%): OBV, Volume trends
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Asset, DailyPrice
import logging

logger = logging.getLogger(__name__)

# Try to import ta-lib (best), fallback to pandas-ta or manual
try:
    import talib
    USE_TALIB = True
    logger.info("[TECH] Using TA-Lib for technical indicators")
except ImportError:
    USE_TALIB = False
    logger.warning("[TECH] TA-Lib not available, using pandas calculations")


class TechnicalAnalyzer:
    """
    Technical Analysis Calculator
    
    Calculates multiple technical indicators and combines them into:
    - Overall technical score (0-100)
    - BUY/SELL/HOLD signal
    - Detailed breakdown by category
    - Individual indicator values
    """
    
    def __init__(self, lookback_days: int = 200):
        """
        Initialize Technical Analyzer
        
        Args:
            lookback_days: How many days of historical data to analyze
                          200 minimum (for 200-day MA)
        """
        self.lookback_days = lookback_days
        
        # Weights for each category (must sum to 1.0)
        self.weights = {
            'momentum': 0.35,
            'trend': 0.35,
            'volatility': 0.20,
            'volume': 0.10
        }
    
    def analyze(self, symbol: str) -> Dict:
        """
        Analyze technical indicators for a stock
        
        Args:
            symbol: Stock symbol (e.g., 'TCS.NS')
        
        Returns:
            Dict with:
                - score: Overall technical score (0-100)
                - signal: 'BUY', 'SELL', or 'HOLD'
                - confidence: Confidence level (0-100)
                - indicators: Individual indicator scores
                - categories: Category scores (momentum, trend, etc.)
                - latest_values: Current indicator values
                - signals: Specific buy/sell signals detected
        """
        logger.info(f"[TECH] Analyzing technical indicators for {symbol}")
        
        # Get price data from database
        df = self._get_price_data(symbol)
        
        if df is None or len(df) < 50:
            logger.warning(f"[TECH] Insufficient data for {symbol}")
            return self._insufficient_data_result()
        
        # Calculate all indicators
        indicators = self._calculate_all_indicators(df)
        
        # Score each category
        momentum_score = self._score_momentum(indicators)
        trend_score = self._score_trend(indicators)
        volatility_score = self._score_volatility(indicators)
        volume_score = self._score_volume(indicators)
        
        # Calculate overall score
        overall_score = (
            momentum_score * self.weights['momentum'] +
            trend_score * self.weights['trend'] +
            volatility_score * self.weights['volatility'] +
            volume_score * self.weights['volume']
        )
        
        # Determine signal and confidence
        signal, confidence = self._determine_signal(overall_score, indicators)
        
        # Detect specific patterns/signals
        detected_signals = self._detect_signals(indicators)
        
        result = {
            'symbol': symbol,
            'score': round(overall_score, 1),
            'signal': signal,
            'confidence': round(confidence, 1),
            'categories': {
                'momentum': round(momentum_score, 1),
                'trend': round(trend_score, 1),
                'volatility': round(volatility_score, 1),
                'volume': round(volume_score, 1)
            },
            'indicators': {
                'rsi': indicators.get('rsi_score', 50),
                'macd': indicators.get('macd_score', 50),
                'stochastic': indicators.get('stoch_score', 50),
                'sma': indicators.get('sma_score', 50),
                'ema': indicators.get('ema_score', 50),
                'adx': indicators.get('adx_score', 50),
                'bollinger': indicators.get('bb_score', 50),
                'atr': indicators.get('atr_score', 50),
                'obv': indicators.get('obv_score', 50)
            },
            'latest_values': {
                'rsi': indicators.get('rsi', None),
                'macd': indicators.get('macd', None),
                'macd_signal': indicators.get('macd_signal', None),
                'price': indicators.get('price', None),
                'sma_20': indicators.get('sma_20', None),
                'sma_50': indicators.get('sma_50', None),
                'sma_200': indicators.get('sma_200', None),
                'bb_upper': indicators.get('bb_upper', None),
                'bb_lower': indicators.get('bb_lower', None),
                'volume': indicators.get('volume', None)
            },
            'signals': detected_signals,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"[TECH] {symbol} Score: {overall_score:.1f}/100 → {signal}")
        return result
    
    def _get_price_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Fetch price data from database
        
        Returns DataFrame with columns: date, open, high, low, close, volume
        """
        try:
            db = SessionLocal()
            
            # Get asset
            asset = db.query(Asset).filter(Asset.symbol == symbol).first()
            if not asset:
                logger.warning(f"[TECH] Asset not found: {symbol}")
                return None
            
            # Get price data
            cutoff_date = datetime.now() - timedelta(days=self.lookback_days)
            prices = db.query(DailyPrice).filter(
                DailyPrice.asset_id == asset.id,
                DailyPrice.date >= cutoff_date
            ).order_by(DailyPrice.date.asc()).all()
            
            if not prices:
                logger.warning(f"[TECH] No price data for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'date': p.date,
                'open': float(p.open_price) if p.open_price else None,
                'high': float(p.high_price) if p.high_price else None,
                'low': float(p.low_price) if p.low_price else None,
                'close': float(p.close_price),
                'volume': int(p.volume) if p.volume else 0
            } for p in prices])
            
            db.close()
            
            logger.info(f"[TECH] Loaded {len(df)} days of data for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"[TECH] Error fetching data: {e}")
            return None
    
    def _calculate_all_indicators(self, df: pd.DataFrame) -> Dict:
        """
        Calculate all technical indicators
        
        Returns dict with all indicator values and their scores
        """
        indicators = {}
        
        # Get latest price info
        latest = df.iloc[-1]
        indicators['price'] = latest['close']
        indicators['volume'] = latest['volume']
        
        # Calculate momentum indicators
        if USE_TALIB:
            indicators.update(self._calculate_talib_indicators(df))
        else:
            indicators.update(self._calculate_pandas_indicators(df))
        
        return indicators
    
    def _calculate_talib_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate indicators using TA-Lib (faster)"""
        ind = {}
        
        close = df['close'].values
        high = df['high'].fillna(df['close']).values
        low = df['low'].fillna(df['close']).values
        volume = df['volume'].values
        
        try:
            # Momentum indicators
            ind['rsi'] = talib.RSI(close, timeperiod=14)[-1]
            ind['stoch_k'], ind['stoch_d'] = talib.STOCH(high, low, close)
            ind['stoch_k'] = ind['stoch_k'][-1]
            ind['mom'] = talib.MOM(close, timeperiod=10)[-1]
            
            # Trend indicators
            ind['macd'], ind['macd_signal'], ind['macd_hist'] = talib.MACD(close)
            ind['macd'] = ind['macd'][-1]
            ind['macd_signal'] = ind['macd_signal'][-1]
            ind['macd_hist'] = ind['macd_hist'][-1]
            
            ind['sma_20'] = talib.SMA(close, timeperiod=20)[-1]
            ind['sma_50'] = talib.SMA(close, timeperiod=50)[-1]
            ind['sma_200'] = talib.SMA(close, timeperiod=200)[-1] if len(close) >= 200 else None
            
            ind['ema_12'] = talib.EMA(close, timeperiod=12)[-1]
            ind['ema_26'] = talib.EMA(close, timeperiod=26)[-1]
            
            ind['adx'] = talib.ADX(high, low, close, timeperiod=14)[-1]
            
            # Volatility indicators
            ind['bb_upper'], ind['bb_middle'], ind['bb_lower'] = talib.BBANDS(close)
            ind['bb_upper'] = ind['bb_upper'][-1]
            ind['bb_middle'] = ind['bb_middle'][-1]
            ind['bb_lower'] = ind['bb_lower'][-1]
            
            ind['atr'] = talib.ATR(high, low, close, timeperiod=14)[-1]
            
            # Volume indicators
            ind['obv'] = talib.OBV(close, volume)[-1]
            ind['mfi'] = talib.MFI(high, low, close, volume, timeperiod=14)[-1]
            
        except Exception as e:
            logger.error(f"[TECH] TA-Lib calculation error: {e}")
        
        return ind
    
    def _calculate_pandas_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate indicators using pandas (fallback)"""
        ind = {}
        
        close = df['close']
        high = df['high'].fillna(df['close'])
        low = df['low'].fillna(df['close'])
        volume = df['volume']
        
        try:
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            ind['rsi'] = float((100 - (100 / (1 + rs))).iloc[-1])
            
            # MACD
            ema_12 = close.ewm(span=12, adjust=False).mean()
            ema_26 = close.ewm(span=26, adjust=False).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            
            ind['macd'] = float(macd_line.iloc[-1])
            ind['macd_signal'] = float(signal_line.iloc[-1])
            ind['macd_hist'] = float((macd_line - signal_line).iloc[-1])
            
            # Moving Averages
            ind['sma_20'] = float(close.rolling(window=20).mean().iloc[-1])
            ind['sma_50'] = float(close.rolling(window=50).mean().iloc[-1])
            if len(close) >= 200:
                ind['sma_200'] = float(close.rolling(window=200).mean().iloc[-1])
            
            ind['ema_12'] = float(ema_12.iloc[-1])
            ind['ema_26'] = float(ema_26.iloc[-1])
            
            # Bollinger Bands
            sma_20 = close.rolling(window=20).mean()
            std_20 = close.rolling(window=20).std()
            ind['bb_upper'] = float((sma_20 + 2 * std_20).iloc[-1])
            ind['bb_middle'] = float(sma_20.iloc[-1])
            ind['bb_lower'] = float((sma_20 - 2 * std_20).iloc[-1])
            
            # ATR
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            ind['atr'] = float(tr.rolling(window=14).mean().iloc[-1])
            
            # Stochastic
            low_14 = low.rolling(window=14).min()
            high_14 = high.rolling(window=14).max()
            ind['stoch_k'] = float(((close - low_14) / (high_14 - low_14) * 100).iloc[-1])
            
            # OBV
            obv = (volume * (~close.diff().le(0) * 2 - 1)).cumsum()
            ind['obv'] = float(obv.iloc[-1])
            
        except Exception as e:
            logger.error(f"[TECH] Pandas calculation error: {e}")
        
        return ind
    
    def _score_momentum(self, ind: Dict) -> float:
        """Score momentum indicators (0-100)"""
        scores = []
        
        # RSI Score (0-100)
        rsi = ind.get('rsi')
        if rsi is not None:
            if rsi < 30:
                rsi_score = 80  # Oversold = potential buy
            elif rsi > 70:
                rsi_score = 20  # Overbought = potential sell
            else:
                rsi_score = 50 + (rsi - 50) * 0.5  # Scale 30-70 to 40-60
            scores.append(rsi_score)
            ind['rsi_score'] = rsi_score
        
        # Stochastic Score
        stoch_k = ind.get('stoch_k')
        if stoch_k is not None:
            if stoch_k < 20:
                stoch_score = 80
            elif stoch_k > 80:
                stoch_score = 20
            else:
                stoch_score = 50 + (stoch_k - 50) * 0.5
            scores.append(stoch_score)
            ind['stoch_score'] = stoch_score
        
        # Momentum Score
        mom = ind.get('mom')
        if mom is not None:
            mom_score = 50 + (mom * 5)  # Scale momentum to 0-100
            mom_score = max(0, min(100, mom_score))  # Clamp
            scores.append(mom_score)
            ind['mom_score'] = mom_score
        
        return np.mean(scores) if scores else 50
    
    def _score_trend(self, ind: Dict) -> float:
        """Score trend indicators (0-100)"""
        scores = []
        
        # MACD Score
        macd = ind.get('macd')
        macd_signal = ind.get('macd_signal')
        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                macd_score = 70 + min(30, abs(macd - macd_signal) * 10)  # Bullish
            else:
                macd_score = 30 - min(30, abs(macd - macd_signal) * 10)  # Bearish
            scores.append(macd_score)
            ind['macd_score'] = macd_score
        
        # Moving Average Score
        price = ind.get('price')
        sma_50 = ind.get('sma_50')
        sma_200 = ind.get('sma_200')
        
        if price and sma_50:
            # Price position relative to MAs
            if sma_200 and sma_50 > sma_200:
                # Golden cross
                if price > sma_50:
                    sma_score = 90
                else:
                    sma_score = 70
            elif sma_200 and sma_50 < sma_200:
                # Death cross
                if price < sma_50:
                    sma_score = 10
                else:
                    sma_score = 30
            else:
                # No 200-day MA or neutral
                sma_score = 50 + (price - sma_50) / sma_50 * 100
                sma_score = max(0, min(100, sma_score))
            
            scores.append(sma_score)
            ind['sma_score'] = sma_score
        
        # ADX Score (trend strength)
        adx = ind.get('adx')
        if adx is not None:
            if adx > 25:
                adx_score = min(100, 50 + adx)  # Strong trend
            else:
                adx_score = adx * 2  # Weak trend
            scores.append(adx_score)
            ind['adx_score'] = adx_score
        
        return np.mean(scores) if scores else 50
    
    def _score_volatility(self, ind: Dict) -> float:
        """Score volatility indicators (0-100)"""
        scores = []
        
        # Bollinger Bands Score
        price = ind.get('price')
        bb_upper = ind.get('bb_upper')
        bb_lower = ind.get('bb_lower')
        bb_middle = ind.get('bb_middle')
        
        if all([price, bb_upper, bb_lower, bb_middle]):
            # Position within bands
            if price >= bb_upper:
                bb_score = 20  # Overbought
            elif price <= bb_lower:
                bb_score = 80  # Oversold
            else:
                # Scale position in bands to score
                band_position = (price - bb_lower) / (bb_upper - bb_lower)
                bb_score = 80 - (band_position * 60)  # Lower = better score
            
            scores.append(bb_score)
            ind['bb_score'] = bb_score
        
        # ATR Score (lower volatility = higher score for safety)
        atr = ind.get('atr')
        if atr and price:
            atr_percent = (atr / price) * 100
            if atr_percent < 2:
                atr_score = 80  # Low volatility
            elif atr_percent > 5:
                atr_score = 40  # High volatility
            else:
                atr_score = 80 - (atr_percent - 2) * 13  # Scale 2-5% to 80-40
            
            scores.append(atr_score)
            ind['atr_score'] = atr_score
        
        return np.mean(scores) if scores else 50
    
    def _score_volume(self, ind: Dict) -> float:
        """Score volume indicators (0-100)"""
        scores = []
        
        # OBV Score (simple: positive trend = good)
        obv = ind.get('obv')
        if obv is not None:
            # This is simplified - ideally compare to OBV trend
            obv_score = 60  # Neutral default
            scores.append(obv_score)
            ind['obv_score'] = obv_score
        
        # MFI Score (like RSI for volume)
        mfi = ind.get('mfi')
        if mfi is not None:
            if mfi < 20:
                mfi_score = 80  # Oversold
            elif mfi > 80:
                mfi_score = 20  # Overbought
            else:
                mfi_score = 50 + (mfi - 50) * 0.5
            scores.append(mfi_score)
            ind['mfi_score'] = mfi_score
        
        return np.mean(scores) if scores else 50
    
    def _determine_signal(self, score: float, indicators: Dict) -> Tuple[str, float]:
        """
        Determine BUY/SELL/HOLD signal and confidence
        
        Returns: (signal, confidence)
        """
        # Base signal on score
        if score >= 70:
            signal = 'BUY'
            confidence = score
        elif score >= 55:
            signal = 'BUY'
            confidence = score - 10  # Lower confidence for weak buy
        elif score <= 30:
            signal = 'SELL'
            confidence = 100 - score
        elif score <= 45:
            signal = 'SELL'
            confidence = 55 - score  # Lower confidence for weak sell
        else:
            signal = 'HOLD'
            confidence = 100 - abs(50 - score) * 2
        
        return signal, confidence
    
    def _detect_signals(self, indicators: Dict) -> List[str]:
        """Detect specific technical patterns/signals"""
        signals = []
        
        # Golden/Death Cross
        sma_50 = indicators.get('sma_50')
        sma_200 = indicators.get('sma_200')
        if sma_50 and sma_200:
            if sma_50 > sma_200 * 1.01:  # 1% above
                signals.append('golden_cross')
            elif sma_50 < sma_200 * 0.99:  # 1% below
                signals.append('death_cross')
        
        # MACD Crossover
        macd = indicators.get('macd')
        macd_signal = indicators.get('macd_signal')
        if macd and macd_signal:
            if macd > macd_signal:
                signals.append('macd_bullish')
            else:
                signals.append('macd_bearish')
        
        # RSI Extremes
        rsi = indicators.get('rsi')
        if rsi:
            if rsi < 30:
                signals.append('rsi_oversold')
            elif rsi > 70:
                signals.append('rsi_overbought')
        
        # Bollinger Bands
        price = indicators.get('price')
        bb_upper = indicators.get('bb_upper')
        bb_lower = indicators.get('bb_lower')
        if price and bb_upper and bb_lower:
            if price >= bb_upper:
                signals.append('bb_overbought')
            elif price <= bb_lower:
                signals.append('bb_oversold')
        
        return signals
    
    def _insufficient_data_result(self) -> Dict:
        """Return neutral result when data insufficient"""
        return {
            'score': 50.0,
            'signal': 'HOLD',
            'confidence': 0.0,
            'categories': {
                'momentum': 50.0,
                'trend': 50.0,
                'volatility': 50.0,
                'volume': 50.0
            },
            'indicators': {},
            'latest_values': {},
            'signals': [],
            'error': 'Insufficient price data'
        }


# Convenience function
def analyze_technical(symbol: str) -> Dict:
    """Quick analysis function"""
    analyzer = TechnicalAnalyzer()
    return analyzer.analyze(symbol)


if __name__ == "__main__":
    """Test script"""
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*80)
    print("TECHNICAL INDICATORS CALCULATOR TEST")
    print("="*80 + "\n")
    
    # Test with a stock
    result = analyze_technical('TCS.NS')
    
    print(f"Symbol: {result.get('symbol', 'N/A')}")
    print(f"Technical Score: {result['score']}/100")
    print(f"Signal: {result['signal']}")
    print(f"Confidence: {result['confidence']}%\n")
    
    print("Category Scores:")
    for cat, score in result['categories'].items():
        print(f"  {cat.capitalize()}: {score}/100")
    
    print("\nLatest Indicator Values:")
    for ind, val in result['latest_values'].items():
        if val is not None:
            print(f"  {ind}: {val:.2f}" if isinstance(val, float) else f"  {ind}: {val}")
    
    print("\nDetected Signals:")
    for sig in result['signals']:
        print(f"  • {sig}")
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETE")
    print("="*80 + "\n")
