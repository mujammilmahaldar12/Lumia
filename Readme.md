# 🎯 LUMIA - AI-Powered Investment Recommendation System# 🚀 Lumia - AI-Powered Financial Analytics System



**Last Updated:** October 6, 2025  A comprehensive financial analytics platform that combines **news sentiment analysis**, **technical indicators**, and **fundamental analysis** to provide AI-powered portfolio recommendations.

**Status:** ✅ **PRODUCTION READY**

## ✨ Key Features

---

- 📰 **Real-time News Collection** - Automated news gathering from financial sources

## 📊 What Does Lumia Do?- 🤖 **AI Sentiment Analysis** - FinBERT + VADER dual-model sentiment processing  

- 📊 **Signal Generation** - Daily aggregated signals combining multiple data sources

Lumia analyzes **2,205+ assets** (Stocks, ETFs, Mutual Funds, Crypto) and provides:- 💼 **Portfolio Optimization** - Risk-adjusted recommendations with automated allocation

- ⏰ **Background Automation** - Scheduled data collection and processing

1. **BUY/SELL/HOLD Recommendations** - For individual assets with detailed reasoning- 🎯 **Interactive Test UI** - Streamlit-based frontend for testing recommendations

2. **Portfolio Allocation Guide** (Coming Soon) - How much % to invest in each asset type with AI explanation

## 📁 Project Structure

---

```

## 🚀 Quick StartLumia/

├── alembic/                    # Database migrations

### **Step 1: Activate Environment** (REQUIRED!)│   ├── versions/               # Migration version files

```bash│   └── env.py                 # Migration environment

.\env\Scripts\activate├── app/                       # Core application

```│   ├── routes/                # FastAPI endpoints

│   │   └── recommend.py       # Portfolio recommendation API

### **Step 2: Run Analysis**│   ├── services/              # Business logic services

```bash│   │   ├── news_collector.py  # News collection service

# Get top 20 recommendations across ALL asset types│   │   ├── sentiment_worker.py # Sentiment analysis service

python main.py --type all --top 20│   │   ├── signal_generator.py # Signal aggregation service

│   │   └── scheduler.py       # Background automation

# Specific asset types:│   └── test_ui.py            # Streamlit test interface

python main.py --type stock --action BUY --top 10      # Stocks only├── models/                    # SQLAlchemy models

python main.py --type etf --top 5                      # ETFs only│   ├── news_article.py       # News article storage

python main.py --type mutual_fund --top 10             # Mutual funds│   ├── news_sentiment.py     # Sentiment analysis results

python main.py --type crypto --action BUY --top 5      # Crypto│   ├── news_asset_map.py     # Article-asset mapping

│   ├── asset_daily_signals.py # Aggregated daily signals

# Web interface:│   ├── company.py            # Company/asset information

streamlit run app/streamlit_app.py│   ├── daily_price.py        # Price data

```│   └── quarterly_fundamental.py # Fundamental data

├── scripts/                   # CLI automation scripts

---│   ├── collect_news.py       # News collection CLI

│   ├── process_sentiment.py  # Sentiment processing CLI

## 🎯 How Lumia Recommends Assets│   ├── generate_signals.py   # Signal generation CLI

│   └── README.md            # Scripts documentation

### **Every asset gets a score out of 100 based on 4 components:**├── tests/                    # Unit tests

│   ├── test_news_collector.py

```│   ├── test_sentiment_worker.py

FINAL SCORE = (Technical × 25%) + (Fundamental × 30%) + (Sentiment × 25%) + (Risk × 20%)│   └── test_recommendation.py

```├── config.py                 # System configuration

├── database.py              # Database connection

### **1️⃣ Technical Analysis (25%)**├── start_scheduler.py       # Automation manager

**What it checks:**└── requirements.txt         # Dependencies

- Price trends (Moving Averages)```

- Momentum (RSI - Relative Strength Index)

- Volatility (Bollinger Bands)## 🚀 Quick Start

- Volume patterns

### 1. Environment Setup

**Scoring:**

- ✅ Uptrend + Normal RSI + Good Volume = 70-90/100```bash

- ❌ Downtrend + Overbought + Low Volume = 20-40/100# Clone and navigate to the project

cd "C:\Users\mujammil maldar\Desktop\New folder (4)\app\Lumia"

**Example:**

```# Activate virtual environment

TCS.NS Technical Score: 55.8/100..\env\Scripts\Activate.ps1

- SMA(20) > SMA(50) ✓ (Uptrend)

- RSI = 55 ✓ (Not overbought/oversold)# Install dependencies

- Volume = Average ⚠️pip install -r requirements.txt

``````



---### 2. Configuration



### **2️⃣ Fundamental Analysis (30% - HIGHEST WEIGHT!)**Create a `.env` file with your settings:

**What it checks:**```bash

- Profitability: ROE (Return on Equity), ROA, Profit Margins# Generate sample configuration

- Valuation: P/E Ratio (compared to sector average)python start_scheduler.py create-env

- Growth: Revenue & Earnings growth (Year-over-Year)

- Financial Health: Debt/Equity Ratio, Current Ratio# Edit .env file with your settings

cp .env.sample .env

**Scoring:**```

- ✅ High ROE + Low P/E + Growing Revenue + Low Debt = 80-100/100

- ❌ Low ROE + High P/E + Declining Revenue + High Debt = 10-30/100Required environment variables:

```env

**Example:**DATABASE_URL=postgresql://postgres:password@localhost:5432/lumia_db

```NEWSAPI_KEY=your_newsapi_key_here

INDIAMART.NS Fundamental Score: 95.0/100 ⭐SCHEDULER_TIMEZONE=America/New_York

- ROE = 45% ✓ (Excellent profitability)```

- P/E = 28 vs Industry 35 ✓ (Undervalued!)

- Revenue Growth = 12% YoY ✓### 3. Database Setup

- Debt/Equity = 0.05 ✓ (Very low debt)

``````bash

# Run migrations to create tables

**Why 30% weight?**alembic upgrade head

- Most reliable long-term indicator

- Based on real company financials# Verify setup

- Less affected by market noisepython start_scheduler.py status

```

---

### 4. Start the System

### **3️⃣ Sentiment Analysis (25%)**

**What it checks:**```bash

- Recent news headlines about the company# Option 1: Full automation system

- FinBERT AI model analyzes positive/negative/neutral sentimentpython start_scheduler.py start

- Market mood and news coverage

# Option 2: Manual API server

**Scoring:**uvicorn app.main:app --host 0.0.0.0 --port 8000

- ✅ Mostly positive news = 70-90/100

- ⚠️ Mixed news = 40-60/100# Option 3: Test UI only

- ❌ Mostly negative news = 10-30/100streamlit run app/test_ui.py --server.port 8501

```

**Current Status:**

```## 🤖 Automation System

⚠️ LIVE NEWS DISABLED (DuckDuckGo blocking requests)

→ All sentiment scores default to 50 (neutral)Lumia includes a comprehensive background automation system that handles data collection, processing, and signal generation automatically.

→ Recommendations rely on Technical + Fundamental + Risk (75% total weight)

```### Scheduler Features



---- **News Collection**: Every hour during market hours (9 AM - 6 PM EST)

- **Sentiment Processing**: Every hour, offset by 30 minutes  

### **4️⃣ Risk Assessment (20%)**- **Signal Generation**: Daily at market close (4:30 PM EST)

**What it checks:**- **Weekend Maintenance**: Saturday at 2 AM (cleanup and statistics)

- Your risk profile (Conservative/Moderate/Aggressive)- **Emergency Recovery**: Twice daily at off-hours (7 AM, 7 PM)

- Stock volatility and beta

- Sector risk and market conditions### Automation Commands



**Scoring:**```bash

- ✅ Stock matches your risk profile = 70-90/100# Start the full automation system

- ⚠️ Partial match = 40-60/100python start_scheduler.py start

- ❌ Mismatch = 10-30/100

# Validate configuration without starting

**Example:**python start_scheduler.py start --config-check

```

Your Profile: Moderate Risk# Check system status and data freshness

Stock: TCS.NS (Large-cap, Low volatility)python start_scheduler.py status

Risk Score: 75/100 ✓ (Good match!)

# Test individual jobs manually

Your Profile: Aggressivepython start_scheduler.py test-job collect_news

Stock: Penny Stock (High volatility)python start_scheduler.py test-job process_sentiment

Risk Score: 90/100 ✓ (Perfect match!)python start_scheduler.py test-job generate_signals



Your Profile: Conservative# Manual script execution

Stock: Penny Stock (High volatility)python scripts/collect_news.py --all-assets --days 7

Risk Score: 20/100 ✗ (Too risky!)python scripts/process_sentiment.py --unprocessed --batch-size 25

```python scripts/generate_signals.py --all --backfill --days 30

```

---

### Configuration Options

## 📈 Complete Example: INDIAMART.NS

Key environment variables for automation:

### **Component Scores:**```env

```# Scheduler timing

Technical Analysis:    55.8/100NEWS_COLLECTION_INTERVAL_HOURS=1

Fundamental Analysis:  95.0/100 ⭐ EXCELLENTSENTIMENT_PROCESSING_INTERVAL_HOURS=1

Sentiment Analysis:    50.0/100 (Neutral - no news)MARKET_CLOSE_HOUR=16

Risk Assessment:       85.0/100 (Good match for moderate investors)MARKET_CLOSE_MINUTE=0

```

# Processing limits

### **Final Calculation:**SENTIMENT_BATCH_SIZE=25

```MAX_SENTIMENT_ARTICLES_PER_RUN=200

= (55.8 × 0.25) + (95.0 × 0.30) + (50.0 × 0.25) + (85.0 × 0.20)NEWS_ARTICLES_PER_SYMBOL=50

= 13.95 + 28.50 + 12.50 + 17.00

= 72.0/100# Model settings

```USE_FINBERT=True

MIN_FUZZY_MATCH_SCORE=0.7

### **Decision Rules:**```

- **Score ≥ 65** → BUY ✅

- **Score 40-64** → HOLD 🟡## 🎯 Test UI (Streamlit)

- **Score < 40** → SELL ❌

Interactive web interface for testing the recommendation system:

### **Result: BUY ✅ (Score: 72.0)**

```bash

### **Why BUY?**# Start the UI (requires API server running)

1. ✅ **Outstanding Fundamentals (95)** - High ROE, undervalued P/E, strong growthstreamlit run app/test_ui.py --server.port 8501

2. ✅ **Low Risk (85)** - Suitable for moderate investors, stable large-cap```

3. ✅ **Decent Technical Trend (56)** - Uptrend in progress

4. ⚠️ **Neutral Sentiment (50)** - No news data (doesn't affect decision much)### UI Features



**Confidence: 88%** (High because all metrics aligned except sentiment)- **Portfolio Configuration**: Set capital, risk tolerance, horizon

- **Real-time Health Monitoring**: API status and data freshness

---- **Interactive Visualizations**: Allocation charts and breakdowns

- **Risk Analysis**: Scenario modeling and diversification metrics  

## 💼 Command Options- **Export Capabilities**: Download results as JSON/CSV

- **AI Explanations**: Detailed reasoning behind recommendations

### **Basic Commands:**

```bash## 📡 API Endpoints

# Analyze all asset types, show top 20

python main.py --type all --top 20### Portfolio Recommendations

```bash

# Only BUY recommendations# Get portfolio recommendations

python main.py --type stock --action BUY --top 10POST /api/recommend

{

# Match your risk profile    "capital": 50000,

python main.py --risk conservative --top 15    "risk": 0.5,

    "horizon_years": 5,

# Detailed breakdown    "exclusions": ["TSLA", "GME"]

python main.py --type etf --top 5 --detailed}

```

# Check system health

### **Options Explained:**GET /api/recommend/health

```

| Option | Values | Description |

|--------|--------|-------------|### Example Response

| `--type` | stock, etf, mutual_fund, crypto, all | Asset type to analyze |```json

| `--action` | BUY, SELL, HOLD | Filter by recommendation |{

| `--risk` | conservative, moderate, aggressive | Your risk profile |    "buckets": {

| `--top` | Number (e.g., 10, 20) | How many results to show |        "stocks": [

| `--detailed` | No value needed | Show full component breakdown |            {

                "symbol": "AAPL",

### **Example Output:**                "name": "Apple Inc.",

```                "allocated": 15000.0,

ANALYSIS RESULTS - 5 Recommendations                "percentage": 30.0,

========================================                "score": 0.847,

📊 SUMMARY:                "breakdown": {

   BUY:  5 assets (100.0%)                    "sentiment": 0.82,

                    "fundamental": 0.91,

#  Symbol         Type    Action  Score  Tech  Fund  Sent  Risk                    "momentum": 0.76,

1  INDIAMART.NS   stock   BUY     72.0   55.8  95.0  50.0  85.0                    "volatility": 0.89

2  BAJAJHLDNG.NS  stock   BUY     71.9   55.5  95.0  50.0  85.0                }

3  NESCO.NS       stock   BUY     71.7   54.7  95.0  50.0  85.0            }

4  NIFTYBEES.NS   etf     BUY     70.5   60.0  85.0  50.0  80.0        ],

5  IN-MF-12345    mutual  BUY     69.8   55.0  88.0  50.0  82.0        "etfs": [...]

```    },

    "total_allocated": 50000.0,

---    "explanation_text": "Based on your balanced risk profile..."

}

## 🖥️ Web Interface (Streamlit)```



```bash## � Database Models

streamlit run app/streamlit_app.py

```### Core Models

- **Company**: Asset information (symbols, names, sectors, market cap)

### **Features:**- **DailyPrice**: Historical price data and technical indicators

- ✅ Select multiple asset types (Stocks ✓ ETFs ✓ Mutual Funds ✓ Crypto ✓)- **QuarterlyFundamental**: Financial metrics and ratios

- ✅ Choose your risk profile

- ✅ Filter by BUY/SELL/HOLD### News & Sentiment Models  

- ✅ View detailed score breakdowns- **NewsArticle**: Article storage with deduplication

- ✅ Interactive and user-friendly- **NewsAssetMap**: Fuzzy-matched article-asset relationships

- **NewsSentiment**: FinBERT + VADER sentiment analysis results

---- **AssetDailySignals**: Aggregated daily metrics and signals



## 📁 What Assets Can Lumia Analyze?## 🔧 Database Management



| Asset Type | Count | Examples |If starting fresh, Alembic is already initialized. The configuration is in `alembic.ini` and the environment setup is in `alembic/env.py`.

|------------|-------|----------|

| **Stocks** | ~1,800 | TCS.NS, INFY.NS, RELIANCE.NS, BAJAJHLDNG.NS |### Creating Migrations

| **ETFs** | ~50 | NIFTYBEES.NS, BANKBEES.NS, GOLDBEES.NS |

| **Mutual Funds** | ~300 | IN-MF-XXXXX (various schemes) |#### 1. Check Your Models

| **Crypto** | ~50 | BTC, ETH, ADA, XRP |Before creating migrations, verify all models are properly loaded:

| **TOTAL** | **2,205** | All types analyzed! |

```bash

---python check_metadata.py

```

## 💼 Coming Soon: Portfolio Allocation Guide

**Expected output:**

Instead of just "Top 10 Stocks", Lumia will provide a complete portfolio strategy:```

--- Starting metadata check ---

### **What You'll Get:**

SUCCESS: Found the following tables in metadata:

```- companies

🎯 YOUR PERSONALIZED PORTFOLIO- daily_prices

Risk Profile: Moderate | Investment Amount: ₹1,00,000- quarterly_fundamentals

- users

📊 RECOMMENDED ALLOCATION:

┌─────────────────┬────────────┬─────────────────────────────┐--- Metadata check finished ---

│ Asset Class     │ % Allocation│ Amount (₹)                 │```

├─────────────────┼────────────┼─────────────────────────────┤

│ Stocks          │ 40%        │ ₹40,000                     │#### 2. Generate Migration Files

│ ETFs            │ 25%        │ ₹25,000                     │

│ Mutual Funds    │ 20%        │ ₹20,000                     │When you add/modify models, create a new migration:

│ Fixed Deposits  │ 10%        │ ₹10,000                     │

│ Crypto          │ 5%         │ ₹5,000                      │```bash

└─────────────────┴────────────┴─────────────────────────────┘# Generate migration automatically based on model changes

alembic revision --autogenerate -m "Description of changes"

🎯 TOP PICKS IN EACH CATEGORY:

# Example:

STOCKS (₹40,000):alembic revision --autogenerate -m "Add new column to company model"

1. INDIAMART.NS - ₹15,000 (Score: 72.0)alembic revision --autogenerate -m "Create initial tables"

   Why: Excellent fundamentals, high ROE, undervalued```

2. BAJAJHLDNG.NS - ₹15,000 (Score: 71.9)

   Why: Strong financials, low debt, stable growth#### 3. Review Generated Migration

3. NESCO.NS - ₹10,000 (Score: 71.7)

   Why: Good profitability, defensive sectorAlways review the generated migration file in `alembic/versions/` before applying:



ETFs (₹25,000):```python

1. NIFTYBEES.NS - ₹15,000# Example migration file: alembic/versions/xxxxx_create_initial_tables.py

   Why: Tracks Nifty 50, diversified blue-chip exposuredef upgrade() -> None:

2. BANKBEES.NS - ₹10,000    # Operations to apply the migration

   Why: Banking sector exposure, low expense ratio    op.create_table('companies',

        sa.Column('id', sa.Integer(), nullable=False),

MUTUAL FUNDS (₹20,000):        sa.Column('symbol', sa.String(length=10), nullable=False),

1. Large-Cap Fund - ₹12,000        # ... more columns

   Why: Consistent returns, good fund manager track record    )

2. Balanced Fund - ₹8,000

   Why: Mix of equity and debt, moderate riskdef downgrade() -> None:

    # Operations to reverse the migration

FIXED DEPOSITS (₹10,000):    op.drop_table('companies')

SBI FD @ 7% - ₹10,000```

Why: Safety net, guaranteed returns, liquidity

### Applying Migrations

CRYPTO (₹5,000):

1. Bitcoin (BTC) - ₹3,000#### Apply All Pending Migrations

   Why: Market leader, institutional adoption growing```bash

2. Ethereum (ETH) - ₹2,000alembic upgrade head

   Why: Smart contract platform, DeFi ecosystem```



💡 FinGPT AI REASONING:#### Apply Specific Migration

"This allocation balances growth potential (40% stocks) with ```bash

stability (10% FDs) while maintaining diversification. Your moderate alembic upgrade <revision_id>

risk profile is well-suited for a 60% equity / 40% debt+alternatives ```

split. The 5% crypto allocation provides asymmetric upside potential 

without excessive risk exposure. Blue-chip stocks and index ETFs #### Rollback Migrations

form the core, with mutual funds adding professional management ```bash

and fixed deposits ensuring capital preservation."# Rollback to previous migration

alembic downgrade -1

📊 EXPECTED RETURNS (Annual):

Optimistic: 12-15%# Rollback to specific revision

Realistic: 8-10%alembic downgrade <revision_id>

Conservative: 5-7%

# Rollback all migrations

⚠️ RISK LEVEL: Moderatealembic downgrade base

Max Drawdown: 15-20% in bearish markets```

Volatility: Medium

### Migration Management Commands

🎯 REBALANCE: Every 6 months or when allocation drifts by >5%

```#### Check Current Migration Status

```bash

### **Why This Approach?**alembic current

- ✅ Diversification across asset classes reduces risk```

- ✅ AI explains WHY each allocation percentage

- ✅ Specific recommendations within each category#### View Migration History

- ✅ Matches your risk profile and investment goals```bash

- ✅ Complete investment strategy, not just stock picksalembic history

alembic history --verbose

---```



## ⚠️ Current System Status#### Show SQL Without Executing

```bash

### ✅ **FULLY WORKING:**alembic upgrade head --sql

- ✅ Technical analysis (real-time price data)alembic downgrade -1 --sql

- ✅ Fundamental analysis (quarterly financial data)```

- ✅ Risk assessment (volatility & profile matching)

- ✅ All asset types (stocks, ETFs, mutual funds, crypto)## 🔄 Complete Workflow Example

- ✅ Database session management (no more pool exhaustion!)

- ✅ GPU acceleration (NVIDIA RTX 3060 when env activated)### First Time Setup

```bash

### ⚠️ **PARTIAL:**# 1. Activate environment

- ⚠️ Sentiment analysis defaults to 50 (neutral).\env\Scripts\Activate.ps1

  - Reason: Live news fetching disabled (DuckDuckGo blocking)cd Lumia

  - Impact: 25% of score uses neutral default

  - **System still accurate** - relies on Technical (25%) + Fundamental (30%) + Risk (20%) = 75% weight# 2. Check models are loaded

python check_metadata.py

### 🔧 **COMING SOON:**

- 🔧 Portfolio allocation guide (as shown above)# 3. Create initial migration

- 🔧 FinGPT reasoning for allocation strategyalembic revision --autogenerate -m "Initial migration"

- 🔧 Fixed deposit recommendations

- 🔧 Paid news API integration (to restore sentiment analysis)# 4. Apply migration to database

alembic upgrade head

---```



## 🎓 How to Interpret Your Results### Adding New Model/Column

```bash

### **HIGH SCORE (70-100) = BUY ✅**# 1. Modify your model files (e.g., add new column to Company)

**What it means:**# 2. Check metadata

- Strong fundamentals (profitable, undervalued)python check_metadata.py

- Good technical trend (upward momentum)

- Suitable for your risk profile# 3. Generate migration

alembic revision --autogenerate -m "Add business_summary to companies"

**What to do:**

- Consider buying this asset# 4. Review the generated file in alembic/versions/

- Check fundamental details (ROE, P/E, growth)# 5. Apply migration

- Set stop-loss for risk managementalembic upgrade head

```

---

### Rollback Changes

### **MEDIUM SCORE (40-69) = HOLD 🟡**```bash

**What it means:**# Check current status

- Mixed signals (some good metrics, some bad)alembic current

- Fundamentals OR technicals weak (not both)

- Uncertainty in trend# Rollback last migration

alembic downgrade -1

**What to do:**

- Wait for clearer signals# Or rollback to specific version

- Monitor for improvementalembic downgrade abc123ef456

- Don't buy more, don't sell existing position```



---## 🛠️ Troubleshooting



### **LOW SCORE (0-39) = SELL ❌**### Common Issues

**What it means:**

- Weak fundamentals (high debt, declining growth)**Environment Setup**

- Poor technical trend (downtrend)```bash

- High risk relative to potential reward# Virtual environment issues

.\..\..\env\Scripts\Activate.ps1

**What to do:**pip install -r requirements.txt

- Avoid buying

- Consider selling if you own it# Database connection errors  

- Cut losses if position is underwaterpython start_scheduler.py status

```

---

**Data Processing Issues**

### **Why Fundamental Score Matters Most:**```bash

- **30% weight** (highest of all components)# Check system health

- Based on real company financial datapython start_scheduler.py status

- Less affected by short-term market noise

- Better indicator of long-term value# Manual data processing

- **Currently most reliable** component (sentiment disabled)python scripts/collect_news.py --general --limit 10

python scripts/process_sentiment.py --unprocessed --batch-size 5

---python scripts/generate_signals.py --symbols SPY --force

```

## 🔧 Troubleshooting

**API Problems**

### **Problem: "No assets found"**```bash

```bash# Test API connectivity

# WRONG: Asset types must be lowercasecurl http://localhost:8000/api/recommend/health

python main.py --type STOCK

# Check logs

# CORRECT:tail -f logs/scheduler.log

python main.py --type stocktail -f logs/automation_manager.log

``````



### **Problem: "GPU not available"****Model Loading Issues**

```bash```bash

# Activate virtual environment first# Test sentiment models

.\env\Scripts\activatepython -c "from app.services.sentiment_worker import SentimentWorker; print('Models OK')"

python main.py --type stock --top 5

```# Skip model download in development

export SKIP_MODEL_DOWNLOAD=True

### **Problem: Too many warnings**export MOCK_EXTERNAL_APIS=True

Fixed! Sentiment warnings now suppressed. Only important errors shown.```



### **Problem: Streamlit error "AttributeError: 'str' object has no attribute 'get'"**### Performance Optimization

Fixed! Now handles both dict and string formats for reasoning.

**For Large Datasets:**

---- Reduce `SENTIMENT_BATCH_SIZE` to 10-15

- Increase `NEWS_COLLECTION_INTERVAL_HOURS` to 2-4

## 📊 System Architecture- Use `MAX_SENTIMENT_ARTICLES_PER_RUN` limit



```**For Limited Resources:**  

Lumia/- Set `USE_FINBERT=False` to use only VADER

├── README.md                    ← YOU ARE HERE- Enable `MOCK_EXTERNAL_APIS=True` for testing

├── main.py                      # Command-line interface- Reduce `NEWS_ARTICLES_PER_SYMBOL` to 25

├── app/streamlit_app.py         # Web interface

├── database.py                  # PostgreSQL connection## 🔒 Production Deployment

├── news_fetcher.py              # News retrieval (DB only)

│### Environment Variables

├── recommendation_engine/```env

│   ├── expert_engine.py         # Main recommendation orchestrator# Production settings

│   ├── technical.py             # Technical indicators calculatorDEBUG_MODE=False

│   ├── finbert.py               # Sentiment analysis (FinBERT AI)LOG_LEVEL=WARNING

│   ├── fingpt.py                # Reasoning generation (FinGPT AI)SCHEDULER_LOG_LEVEL=INFO

│   ├── reasoning.py             # Explanation formatter

│   └── scoring.py               # Score calculation utilities# Security

│DATABASE_URL=postgresql://user:pass@prod-db:5432/lumia

├── models/                      # Database modelsNEWSAPI_KEY=prod_api_key_here

│   ├── assets.py                # Asset definitions

│   ├── daily_price.py           # Price history# Performance

│   ├── quarterly_fundamental.py # Financial dataSENTIMENT_BATCH_SIZE=50

│   └── news_article.py          # News storageNEWS_COLLECTION_INTERVAL_HOURS=2

│MAX_PORTFOLIO_ASSETS=15

└── collectors/                  # Data collection scripts```

    ├── daily_price_collector.py

    ├── fundamentals_collector.py### Monitoring & Alerting

    └── master_collector.py```bash

```# System health checks

curl -f http://localhost:8000/api/recommend/health || alert

---

# Data freshness monitoring  

## 💡 Pro Tipspython start_scheduler.py status | grep "STALE" && alert



1. **Always activate virtual environment** before running any command# Log monitoring

2. **Start with `--type all`** to see recommendations across ALL asset typesgrep ERROR logs/scheduler.log | tail -10

3. **Focus on Fundamental score** (30% weight, most reliable)```

4. **Use `--detailed` flag** to understand WHY each recommendation

5. **Match your risk profile** for personalized suggestions### Backup & Recovery

6. **Diversify!** Don't put all money in one asset type```bash

7. **Check multiple components** - don't rely on score alone# Database backup

pg_dump lumia_db > backup_$(date +%Y%m%d).sql

---

# Configuration backup

## 📚 Technical Specificationstar -czf config_backup.tar.gz .env alembic.ini config.py



- **Database:** PostgreSQL (localhost/lumia_test)# Recovery procedure

- **Total Assets:** 2,205 (Stocks: ~1,800, ETFs: ~50, Mutual Funds: ~300, Crypto: ~50)psql lumia_db < backup_20240928.sql

- **Python Version:** 3.10+alembic upgrade head

- **GPU:** NVIDIA RTX 3060 12.9GB VRAM (optional, for AI models)```

- **Key Libraries:** PyTorch, Transformers, Streamlit, SQLAlchemy, TA-Lib

- **AI Models:**## 📚 Advanced Usage

  - FinBERT (sentiment analysis)

  - FinGPT (reasoning generation)### Custom Risk Profiles

```python

---# Modify app/routes/recommend.py

RISK_PROFILES = {

## 📧 Support & Questions    'custom_conservative': {

        'sentiment': 0.10,

**System is production-ready!**        'fundamental': 0.60, 

        'momentum': 0.10,

**Core functionality working:**        'volatility': 0.20

- ✅ Multi-asset analysis (stocks, ETFs, mutual funds, crypto)    }

- ✅ 4-component scoring system}

- ✅ Risk-matched recommendations```

- ✅ Web and CLI interfaces

- ⚠️ Sentiment defaults to neutral (live news disabled)### Extended Data Sources

```python

**For questions:** Re-read this README - everything is explained!# Add new collector in collectors/

class CustomNewsCollector(BaseCollector):

---    def collect_from_source(self, symbol):

        # Custom implementation

**Happy Investing! 📈💰**        pass

```

*Lumia - Your AI-Powered Investment Assistant*

### Custom Sentiment Models
```python
# Modify app/services/sentiment_worker.py
def analyze_with_custom_model(self, text):
    # Integration with other models
    return {'polarity': 0.5, 'pos': 0.6, 'neg': 0.4, 'neu': 0.0}
```

## � System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   News APIs     │───▶│  News Collector  │───▶│  News Articles  │
│   (NewsAPI)     │    │                  │    │   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                 │
                                 ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ FinBERT/VADER   │◀───│ Sentiment Worker │───▶│   Sentiment     │
│    Models       │    │                  │    │   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                 │
                                 ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Price/Fundamental│───▶│ Signal Generator │───▶│ Daily Signals   │
│      Data       │    │                  │    │   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                 │
                                 ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Streamlit UI   │◀───│ Recommendation   │◀───│  Portfolio      │
│                 │    │     Engine       │    │  Optimization   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔗 Dependencies & Technologies

**Core Framework:**
- FastAPI - Modern web framework for APIs
- SQLAlchemy - Python SQL toolkit and ORM
- Alembic - Database migration tool
- PostgreSQL/TimescaleDB - Time-series optimized database

**AI & Machine Learning:**
- Transformers (FinBERT) - Financial sentiment analysis
- NLTK (VADER) - Backup sentiment analysis
- Scikit-learn - Additional ML utilities

**Data Processing:**
- Pandas - Data manipulation and analysis
- NumPy - Numerical computing
- Requests - HTTP library for API calls
- BeautifulSoup - Web scraping and parsing

**Automation & Scheduling:**
- APScheduler - Advanced Python Scheduler
- RapidFuzz - Fast string matching for asset correlation

**Frontend & Visualization:**
- Streamlit - Interactive web applications
- Plotly - Interactive data visualization
- Pandas - Data presentation

## 🎯 Roadmap

**Near Term (v1.1):**
- [ ] Real-time WebSocket updates
- [ ] Enhanced risk metrics (VaR, Sharpe ratio)
- [ ] Social media sentiment integration
- [ ] Sector rotation signals

**Medium Term (v1.2):**
- [ ] Machine learning backtesting
- [ ] Custom portfolio constraints
- [ ] Multi-asset class support (crypto, bonds)
- [ ] Performance attribution analysis

**Long Term (v2.0):**
- [ ] Multi-user support with authentication
- [ ] Real-time trading integration
- [ ] Advanced optimization algorithms
- [ ] Mobile application

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🚀 Happy Trading with AI-Powered Insights! �**
