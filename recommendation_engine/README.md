# 🧠 Lumia Recommendation Engine - Complete Guide

## 📚 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Algorithms Explained](#algorithms-explained)
4. [Modules Breakdown](#modules-breakdown)
5. [Scoring System](#scoring-system)
6. [Installation](#installation)
7. [Usage Examples](#usage-examples)
8. [API Reference](#api-reference)

---

## 🎯 Overview

The Lumia Recommendation Engine is a **professional-grade investment recommendation system** that uses:
- **Technical Analysis** (Price patterns, momentum indicators)
- **Fundamental Analysis** (Financial health, growth metrics)
- **AI Sentiment Analysis** (FinBERT model for news analysis)
- **Risk Analysis** (Volatility, drawdown, beta)
- **Modern Portfolio Theory** (Nobel Prize-winning optimization)

### What Makes It Special?
✅ **Multi-Asset Support**: Stocks, ETFs, Mutual Funds, Crypto, Fixed Deposits  
✅ **AI-Powered**: Uses FinBERT (110M parameters) trained on financial data  
✅ **Transparent**: Every recommendation includes detailed reasoning  
✅ **Risk-Aware**: 3 risk profiles (Conservative/Moderate/Aggressive)  
✅ **Diversified**: Automatic sector and asset type diversification  
✅ **Optimized**: Uses Modern Portfolio Theory for optimal allocation  

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INPUT                                  │
│  - Capital: ₹50,000 - ₹10,00,000+                              │
│  - Risk Profile: Conservative / Moderate / Aggressive           │
│  - Timeline: 3 months - 5 years                                 │
│  - Exclusions: Sectors/Industries to avoid                      │
│  - Preferences: Asset types to include                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│               RECOMMENDATION ENGINE (engine.py)                  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ 1. SCORING MODULE (scoring.py)                            ││
│  │    ┌──────────────────────────────────────────────────┐  ││
│  │    │ Technical Score (25% weight)                     │  ││
│  │    │ - Moving Averages (SMA 50 vs 200)               │  ││
│  │    │ - RSI (Relative Strength Index)                 │  ││
│  │    │ - MACD (Momentum indicator)                     │  ││
│  │    │ - Volume trends                                  │  ││
│  │    │ - 3-month price momentum                        │  ││
│  │    └──────────────────────────────────────────────────┘  ││
│  │                                                            ││
│  │    ┌──────────────────────────────────────────────────┐  ││
│  │    │ Fundamental Score (30% weight)                   │  ││
│  │    │ - P/E Ratio (valuation)                         │  ││
│  │    │ - Revenue Growth (YoY)                          │  ││
│  │    │ - Profit Margin                                  │  ││
│  │    │ - Debt-to-Equity Ratio                          │  ││
│  │    │ - ROE (Return on Equity)                        │  ││
│  │    │ - Dividend Yield                                 │  ││
│  │    └──────────────────────────────────────────────────┘  ││
│  │                                                            ││
│  │    ┌──────────────────────────────────────────────────┐  ││
│  │    │ Risk Score (20% weight)                          │  ││
│  │    │ - Beta (vs market volatility)                    │  ││
│  │    │ - Maximum Drawdown                               │  ││
│  │    │ - Volatility (Standard Deviation)               │  ││
│  │    │ - Sharpe Ratio (risk-adjusted return)           │  ││
│  │    │ - Liquidity (Average volume)                    │  ││
│  │    └──────────────────────────────────────────────────┘  ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ 2. ANALYZER MODULE (analyzer.py)                          ││
│  │    ┌──────────────────────────────────────────────────┐  ││
│  │    │ Sentiment Score (25% weight)                     │  ││
│  │    │                                                   │  ││
│  │    │ FinBERT AI Model:                                │  ││
│  │    │ 1. Collect last 30 days news articles           │  ││
│  │    │ 2. Feed to FinBERT (110M parameters)            │  ││
│  │    │ 3. Get sentiment: Positive/Negative/Neutral     │  ││
│  │    │ 4. Calculate confidence score (0-1)             │  ││
│  │    │                                                   │  ││
│  │    │ Scoring:                                         │  ││
│  │    │ - Positive news: 100 × confidence               │  ││
│  │    │ - Neutral news: 50 × confidence                 │  ││
│  │    │ - Negative news: 0 points                        │  ││
│  │    │ - Recent news (7 days): 1.5x weight            │  ││
│  │    │ - Bonus: Earnings beat (+10), Upgrades (+10)   │  ││
│  │    └──────────────────────────────────────────────────┘  ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ 3. PORTFOLIO MODULE (portfolio.py)                        ││
│  │                                                            ││
│  │    STEP 1: Filter Assets                                  ││
│  │    - Remove excluded sectors/industries                   ││
│  │    - Match risk tolerance                                 ││
│  │    - Calculate final scores                               ││
│  │    - Keep only assets scoring >= threshold                ││
│  │                                                            ││
│  │    STEP 2: Diversify                                      ││
│  │    - Max 2 assets per sector                              ││
│  │    - Balance asset types per risk profile                 ││
│  │    - Conservative: 30% stocks, 30% ETFs, 25% MFs, 15% FDs││
│  │    - Moderate: 45% stocks, 25% ETFs, 15% MFs, 10% crypto ││
│  │    - Aggressive: 60% stocks, 20% ETFs, 15% crypto        ││
│  │                                                            ││
│  │    STEP 3: Optimize (Modern Portfolio Theory)            ││
│  │    - Calculate expected returns                           ││
│  │    - Calculate covariance matrix                          ││
│  │    - Maximize Sharpe Ratio:                               ││
│  │      Sharpe = (Return - Risk_Free_Rate) / Volatility     ││
│  │    - Assign optimal weights                               ││
│  │                                                            ││
│  │    STEP 4: Allocate Capital                               ││
│  │    - Multiply weights × total capital                     ││
│  │    - Round to nearest rupee                               ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ 4. REASONING MODULE (reasoning.py)                        ││
│  │                                                            ││
│  │    For Each Asset, Generate:                              ││
│  │    1. Technical Strength Explanation                      ││
│  │    2. Fundamental Quality Analysis                        ││
│  │    3. Market Sentiment Summary                            ││
│  │    4. Risk Assessment                                      ││
│  │    5. Allocation Rationale                                ││
│  │    6. Risk Warnings                                        ││
│  │    7. Expected Outcome                                     ││
│  └────────────────────────────────────────────────────────────┘│
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     OUTPUT                                       │
│  - Portfolio with 5-10 assets                                   │
│  - Capital allocation for each                                  │
│  - Detailed reasoning (WHY each was chosen)                     │
│  - Risk warnings                                                 │
│  - Expected returns & timeline                                  │
│  - Complete markdown report                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧮 Algorithms Explained

### 1. Technical Analysis

#### Moving Average Crossover
```python
# Golden Cross = Bullish signal
if SMA(50) > SMA(200):
    score += 30  # Strong upward momentum
if current_price > SMA(50):
    score += 10  # Above short-term average
```

**Why it matters**: Moving averages smooth out price noise. When the short-term (50-day) crosses above long-term (200-day), it signals strong upward momentum.

#### RSI (Relative Strength Index)
```python
RSI = 100 - (100 / (1 + RS))
where RS = Average Gain / Average Loss (14 days)

if RSI < 30:
    # Oversold - potential buy opportunity
    score += 20
elif RSI > 70:
    # Overbought - potential overvaluation
    score += 0
```

**Why it matters**: RSI measures speed and magnitude of price changes. Below 30 = oversold (good buy), Above 70 = overbought (risky).

#### MACD (Moving Average Convergence Divergence)
```python
MACD = EMA(12) - EMA(26)
Signal = EMA(MACD, 9)

if MACD > Signal:
    score += 20  # Bullish momentum
```

**Why it matters**: MACD shows momentum changes. When MACD crosses above signal line, it indicates strengthening bullish momentum.

### 2. Fundamental Analysis

#### P/E Ratio (Price-to-Earnings)
```python
P/E = Stock Price / Earnings Per Share

if P/E < 15:
    score += 20  # Undervalued
elif P/E < 25:
    score += 15  # Fair value
else:
    score += 5   # Potentially overvalued
```

**Why it matters**: Lower P/E means you're paying less for each rupee of earnings. P/E < 15 often indicates undervaluation.

#### Revenue Growth
```python
Growth = (Revenue_Current - Revenue_Previous) / Revenue_Previous

if Growth > 20%:
    score += 20  # Excellent growth
elif Growth > 10%:
    score += 15  # Strong growth
```

**Why it matters**: Revenue growth shows business expansion. Consistent 20%+ growth is exceptional.

#### Debt-to-Equity Ratio
```python
Debt_Ratio = Total_Debt / Total_Equity

if Debt_Ratio < 0.5:
    score += 15  # Low debt - financially healthy
elif Debt_Ratio < 1.0:
    score += 10  # Moderate debt
else:
    score += 0   # High debt - risky
```

**Why it matters**: Lower debt = less financial risk. Companies with Debt/Equity < 0.5 are very stable.

### 3. Sentiment Analysis (FinBERT)

#### How FinBERT Works
```
Input: "Apple beats earnings expectations, revenue up 25%"
       ↓
    Tokenization: ["Apple", "beats", "earnings", ...]
       ↓
    BERT Layers (12 transformers): Process context
       ↓
    Classification: Positive (95% confidence)
       ↓
    Score: 100 × 0.95 = 95 points
```

**Training**: FinBERT was trained on 1.8M financial sentences from:
- Earnings call transcripts
- Financial news articles
- Analyst reports
- SEC filings

**Accuracy**: ~97% on financial sentiment classification

#### Sentiment Aggregation
```python
for article in last_30_days_news:
    sentiment = FinBERT.analyze(article)
    
    if sentiment == 'positive':
        score += 100 × confidence
    elif sentiment == 'neutral':
        score += 50 × confidence
    else:  # negative
        score += 0
    
    # Weight recent news more
    if article.days_ago <= 7:
        score × 1.5

final_score = average(all_scores) + bonus_points
```

### 4. Risk Analysis

#### Beta (Market Volatility)
```python
Beta = Covariance(Asset, Market) / Variance(Market)

Beta < 0.8  → Less volatile than market (safer)
Beta = 1.0  → Same volatility as market
Beta > 1.2  → More volatile than market (riskier)
```

**Why it matters**: Beta = 0.5 means the asset moves half as much as the market. Lower beta = more stable investment.

#### Maximum Drawdown
```python
Drawdown = (Current_Price - Peak_Price) / Peak_Price

Max_Drawdown = min(all_drawdowns_in_12_months)

if Max_Drawdown > -10%:
    score += 20  # Stable, small declines
elif Max_Drawdown > -20%:
    score += 10  # Moderate declines
else:
    score += 0   # High risk, large declines
```

**Why it matters**: Max drawdown shows worst-case scenario. If max drawdown is -40%, you could lose 40% at worst.

#### Sharpe Ratio
```python
Sharpe = (Annual_Return - Risk_Free_Rate) / Annual_Volatility

Example:
- Asset A: 15% return, 10% volatility → Sharpe = (15-6.5)/10 = 0.85
- Asset B: 20% return, 20% volatility → Sharpe = (20-6.5)/20 = 0.68

Asset A is better (higher risk-adjusted return)
```

**Why it matters**: Sharpe ratio > 1.0 is good, > 1.5 is excellent. It measures return per unit of risk taken.

### 5. Modern Portfolio Theory (MPT)

#### Portfolio Optimization
```python
Goal: Maximize Sharpe Ratio of entire portfolio

Sharpe_Portfolio = (Portfolio_Return - Risk_Free_Rate) / Portfolio_Volatility

Constraints:
1. All weights sum to 100%
2. No negative weights (no short selling)
3. Respect asset type limits (per risk profile)

Algorithm:
1. Calculate expected returns for each asset
2. Calculate covariance matrix (how assets move together)
3. Find weights that maximize Sharpe ratio
4. Use inverse volatility weighting as starting point
5. Adjust for expected returns
6. Normalize to 100%
```

**Why it works**: MPT won Harry Markowitz the Nobel Prize. It mathematically proves that diversification reduces risk without reducing expected returns.

#### Diversification Benefits
```
Example:
- Asset A: 15% return, 20% volatility
- Asset B: 12% return, 15% volatility
- Correlation: 0.3 (low)

Portfolio (50-50):
- Expected return: 13.5%
- Portfolio volatility: 14.2% (less than both!)

Magic: Because assets don't move together, combined risk is lower.
```

---

## 📦 Modules Breakdown

### 1. `scoring.py` (700 lines)

**Purpose**: Calculate numerical scores for assets

**Key Functions**:
- `calculate_technical_score(prices_df)` → 0-100 score
- `calculate_fundamental_score_stock(fundamentals)` → 0-100 score
- `calculate_fundamental_score_etf(asset_data)` → 0-100 score
- `calculate_risk_score(prices_df, market_prices_df)` → 0-100 score

**What it does**:
1. Takes historical price data
2. Calculates technical indicators (RSI, MACD, MA)
3. Analyzes fundamental ratios (P/E, ROE, Debt)
4. Computes risk metrics (Beta, Volatility, Sharpe)
5. Returns detailed breakdown + scores

### 2. `analyzer.py` (550 lines)

**Purpose**: AI-powered sentiment analysis

**Key Classes**:
- `FinBERTAnalyzer`: Loads and runs FinBERT model

**Key Functions**:
- `analyze_text(text)` → {sentiment, confidence, scores}
- `calculate_sentiment_score(news_articles)` → 0-100 score
- `get_asset_news_from_db(db, asset_id)` → List of news
- `analyze_asset(db, asset_id)` → Complete analysis

**What it does**:
1. Loads FinBERT model (ProsusAI/finbert)
2. Fetches recent news for asset
3. Analyzes each article's sentiment
4. Aggregates into single score
5. Adds bonus for earnings beats, upgrades

### 3. `portfolio.py` (600 lines)

**Purpose**: Build optimized portfolios

**Key Functions**:
- `filter_assets()` → Filter by criteria, calculate scores
- `diversify_portfolio()` → Apply diversification rules
- `optimize_allocation_mpt()` → MPT optimization
- `allocate_capital()` → Assign rupee amounts
- `build_portfolio()` → Complete portfolio builder

**What it does**:
1. Queries all eligible assets from database
2. Removes excluded sectors/industries
3. Calculates final score for each asset
4. Keeps only high-scoring assets
5. Diversifies across sectors (max 2 per sector)
6. Balances asset types per risk profile
7. Optimizes allocation using MPT
8. Assigns capital amounts

### 4. `reasoning.py` (600 lines)

**Purpose**: Generate human-readable explanations

**Key Functions**:
- `generate_asset_reasoning(asset_data)` → Detailed explanation
- `generate_portfolio_summary(portfolio_result)` → Overview
- `generate_complete_report(portfolio_result)` → Full report

**What it does**:
1. Takes analysis results (scores, breakdowns)
2. Converts to natural language
3. Explains WHY each metric matters
4. Adds risk warnings
5. Estimates expected outcomes
6. Formats as markdown report

### 5. `engine.py` (400 lines)

**Purpose**: Main orchestrator

**Key Classes**:
- `LumiaRecommendationEngine`: Main class

**Key Methods**:
- `generate_recommendations()` → Complete recommendations
- `get_asset_analysis()` → Analyze single asset
- `compare_assets()` → Compare multiple assets

**What it does**:
1. Validates user inputs
2. Coordinates all modules
3. Builds portfolio
4. Generates report
5. Returns results

---

## 📊 Scoring System

### Final Score Calculation

```python
Final_Score = (
    Technical_Score × 0.25 +
    Fundamental_Score × 0.30 +
    Sentiment_Score × 0.25 +
    Risk_Score × 0.20
)
```

### Score Interpretation

| Score Range | Grade | Meaning |
|------------|-------|---------|
| 90-100 | A+ | Exceptional - Strong buy |
| 80-89 | A | Excellent - Buy |
| 70-79 | B | Good - Consider buying |
| 60-69 | C | Average - Hold or small position |
| 50-59 | D | Below average - Avoid |
| 0-49 | F | Poor - Do not buy |

### Minimum Thresholds by Risk Profile

| Risk Profile | Min Score | Max Volatility | Max Drawdown |
|-------------|-----------|----------------|--------------|
| Conservative | 65 | 15% | -10% |
| Moderate | 60 | 25% | -20% |
| Aggressive | 55 | 40% | -30% |

---

## 🚀 Installation

### Prerequisites
```bash
# Python 3.10+
python --version

# PostgreSQL database
# Already set up in your Lumia project
```

### Required Packages
```bash
# Core packages (already in requirements.txt)
pip install pandas numpy sqlalchemy psycopg2-binary python-dotenv

# Optional: For FinBERT sentiment analysis
pip install transformers torch
```

### FinBERT Installation (Optional but Recommended)
```bash
# Install transformers and PyTorch
pip install transformers torch

# Model will auto-download on first use (~500MB)
# Or download manually:
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; AutoTokenizer.from_pretrained('ProsusAI/finbert'); AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert')"
```

**Note**: If FinBERT is not installed, the system falls back to simple keyword-based sentiment analysis.

---

## 💻 Usage Examples

### Example 1: Basic Usage
```python
from database import get_db
from recommendation_engine import get_recommendations

db = next(get_db())

recommendations = get_recommendations(
    db=db,
    capital=100000,  # ₹1 Lakh
    risk_profile='moderate'
)

if recommendations['success']:
    print(f"Portfolio has {len(recommendations['portfolio'])} assets")
    
    # Save report
    with open('my_portfolio.md', 'w') as f:
        f.write(recommendations['report'])
```

### Example 2: Conservative Portfolio
```python
recommendations = get_recommendations(
    db=db,
    capital=500000,  # ₹5 Lakh
    risk_profile='conservative',
    timeline_months=24,
    asset_preferences=['stock', 'etf', 'mutual_fund', 'fd'],  # No crypto
    excluded_sectors=['Tobacco', 'Alcohol']  # Ethical investing
)
```

### Example 3: Aggressive Portfolio
```python
recommendations = get_recommendations(
    db=db,
    capital=200000,  # ₹2 Lakh
    risk_profile='aggressive',
    timeline_months=36,
    asset_preferences=['stock', 'crypto', 'etf'],  # Include crypto
    max_assets=12
)
```

### Example 4: Analyze Single Asset
```python
from recommendation_engine import LumiaRecommendationEngine

engine = LumiaRecommendationEngine(db)

analysis = engine.get_asset_analysis(asset_id=123, asset_type='stock')

print(f"Score: {analysis['final_score']:.1f}/100")
print(f"Technical: {analysis['technical']['technical_score']:.1f}")
print(f"Fundamental: {analysis['fundamental']['fundamental_score']:.1f}")
print(f"Sentiment: {analysis['sentiment']['sentiment_score']:.1f}")
print(f"Risk: {analysis['risk']['risk_score']:.1f}")
```

### Example 5: Compare Assets
```python
engine = LumiaRecommendationEngine(db)

comparison = engine.compare_assets([asset_id_1, asset_id_2, asset_id_3])

for item in comparison['comparisons']:
    print(f"{item['symbol']}: {item['final_score']:.1f}/100")
```

---

## 📖 API Reference

### Main Functions

#### `get_recommendations()`
```python
def get_recommendations(
    db: Session,
    capital: float,
    risk_profile: str = 'moderate',
    timeline_months: int = 12,
    excluded_sectors: List[str] = None,
    excluded_industries: List[str] = None,
    asset_preferences: List[str] = None,
    max_assets: int = 10,
    generate_report: bool = True
) -> Dict
```

**Parameters**:
- `db`: Database session
- `capital`: Total investment amount (₹)
- `risk_profile`: 'conservative', 'moderate', or 'aggressive'
- `timeline_months`: Investment horizon
- `excluded_sectors`: Sectors to avoid
- `excluded_industries`: Industries to avoid
- `asset_preferences`: Asset types to include
- `max_assets`: Max portfolio size
- `generate_report`: Generate full markdown report

**Returns**:
```python
{
    'success': True,
    'portfolio': [...],  # List of assets with allocations
    'summary': {
        'total_capital': 100000,
        'num_assets': 8,
        'avg_score': 75.3,
        'avg_sentiment': 68.5
    },
    'report': '...',  # Full markdown report
    'timestamp': '2025-10-05T10:30:00'
}
```

#### `analyze_single_asset()`
```python
def analyze_single_asset(
    db: Session,
    asset_id: int,
    asset_type: str = 'stock'
) -> Dict
```

**Returns**:
```python
{
    'success': True,
    'final_score': 75.3,
    'technical': {...},
    'fundamental': {...},
    'sentiment': {...},
    'risk': {...},
    'reasoning': '...'
}
```

---

## 🎓 Learning Resources

### Understanding the Algorithms

1. **Technical Analysis**:
   - [Investopedia: Technical Analysis](https://www.investopedia.com/technical-analysis-4689657)
   - [RSI Explained](https://www.investopedia.com/terms/r/rsi.asp)
   - [MACD Explained](https://www.investopedia.com/terms/m/macd.asp)

2. **Fundamental Analysis**:
   - [Investopedia: Fundamental Analysis](https://www.investopedia.com/fundamental-analysis-4689757)
   - [P/E Ratio Guide](https://www.investopedia.com/terms/p/price-earningsratio.asp)

3. **Modern Portfolio Theory**:
   - [MPT Explained](https://www.investopedia.com/terms/m/modernportfoliotheory.asp)
   - [Sharpe Ratio](https://www.investopedia.com/terms/s/sharperatio.asp)

4. **FinBERT**:
   - [Paper: FinBERT](https://arxiv.org/abs/1908.10063)
   - [HuggingFace Model](https://huggingface.co/ProsusAI/finbert)

---

## 🔧 Testing

Run the example script:
```bash
python example_recommendation.py
```

This will generate:
- `recommendation_report.md` - Full portfolio report
- `conservative_portfolio.md` - Conservative portfolio
- `aggressive_portfolio.md` - Aggressive portfolio
- `ethical_portfolio.md` - Ethical portfolio
- `analysis_SYMBOL.md` - Single asset analysis

---

## ⚠️ Disclaimer

This recommendation engine is for **educational purposes only**.

- **Not Financial Advice**: This is not personalized financial advice
- **Do Your Research**: Always conduct your own due diligence
- **Risk of Loss**: All investments carry risk of loss
- **Past Performance**: Historical data does not guarantee future results
- **Consult Professionals**: Consult a licensed financial advisor before investing

---

## 🎯 Next Steps

1. ✅ **Test the System**: Run `python example_recommendation.py`
2. ✅ **Review Output**: Read generated reports
3. ✅ **Understand Scores**: Study the scoring breakdowns
4. 🔄 **Integrate with UI**: Add to Streamlit app
5. 🔄 **Add Features**: Reddit API, X API, sentiment tracking
6. 🔄 **Backtest**: Test on historical data
7. 🔄 **Deploy**: Production deployment

---

**Built with ❤️ by the Lumia Team**

*Version 1.0.0 - October 2025*
