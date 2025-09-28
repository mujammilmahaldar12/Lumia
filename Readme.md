# 🚀 Lumia - AI-Powered Financial Analytics System

A comprehensive financial analytics platform that combines **news sentiment analysis**, **technical indicators**, and **fundamental analysis** to provide AI-powered portfolio recommendations.

## ✨ Key Features

- 📰 **Real-time News Collection** - Automated news gathering from financial sources
- 🤖 **AI Sentiment Analysis** - FinBERT + VADER dual-model sentiment processing  
- 📊 **Signal Generation** - Daily aggregated signals combining multiple data sources
- 💼 **Portfolio Optimization** - Risk-adjusted recommendations with automated allocation
- ⏰ **Background Automation** - Scheduled data collection and processing
- 🎯 **Interactive Test UI** - Streamlit-based frontend for testing recommendations

## 📁 Project Structure

```
Lumia/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration version files
│   └── env.py                 # Migration environment
├── app/                       # Core application
│   ├── routes/                # FastAPI endpoints
│   │   └── recommend.py       # Portfolio recommendation API
│   ├── services/              # Business logic services
│   │   ├── news_collector.py  # News collection service
│   │   ├── sentiment_worker.py # Sentiment analysis service
│   │   ├── signal_generator.py # Signal aggregation service
│   │   └── scheduler.py       # Background automation
│   └── test_ui.py            # Streamlit test interface
├── models/                    # SQLAlchemy models
│   ├── news_article.py       # News article storage
│   ├── news_sentiment.py     # Sentiment analysis results
│   ├── news_asset_map.py     # Article-asset mapping
│   ├── asset_daily_signals.py # Aggregated daily signals
│   ├── company.py            # Company/asset information
│   ├── daily_price.py        # Price data
│   └── quarterly_fundamental.py # Fundamental data
├── scripts/                   # CLI automation scripts
│   ├── collect_news.py       # News collection CLI
│   ├── process_sentiment.py  # Sentiment processing CLI
│   ├── generate_signals.py   # Signal generation CLI
│   └── README.md            # Scripts documentation
├── tests/                    # Unit tests
│   ├── test_news_collector.py
│   ├── test_sentiment_worker.py
│   └── test_recommendation.py
├── config.py                 # System configuration
├── database.py              # Database connection
├── start_scheduler.py       # Automation manager
└── requirements.txt         # Dependencies
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone and navigate to the project
cd "C:\Users\mujammil maldar\Desktop\New folder (4)\app\Lumia"

# Activate virtual environment
..\env\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your settings:
```bash
# Generate sample configuration
python start_scheduler.py create-env

# Edit .env file with your settings
cp .env.sample .env
```

Required environment variables:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/lumia_db
NEWSAPI_KEY=your_newsapi_key_here
SCHEDULER_TIMEZONE=America/New_York
```

### 3. Database Setup

```bash
# Run migrations to create tables
alembic upgrade head

# Verify setup
python start_scheduler.py status
```

### 4. Start the System

```bash
# Option 1: Full automation system
python start_scheduler.py start

# Option 2: Manual API server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Option 3: Test UI only
streamlit run app/test_ui.py --server.port 8501
```

## 🤖 Automation System

Lumia includes a comprehensive background automation system that handles data collection, processing, and signal generation automatically.

### Scheduler Features

- **News Collection**: Every hour during market hours (9 AM - 6 PM EST)
- **Sentiment Processing**: Every hour, offset by 30 minutes  
- **Signal Generation**: Daily at market close (4:30 PM EST)
- **Weekend Maintenance**: Saturday at 2 AM (cleanup and statistics)
- **Emergency Recovery**: Twice daily at off-hours (7 AM, 7 PM)

### Automation Commands

```bash
# Start the full automation system
python start_scheduler.py start

# Validate configuration without starting
python start_scheduler.py start --config-check

# Check system status and data freshness
python start_scheduler.py status

# Test individual jobs manually
python start_scheduler.py test-job collect_news
python start_scheduler.py test-job process_sentiment
python start_scheduler.py test-job generate_signals

# Manual script execution
python scripts/collect_news.py --all-assets --days 7
python scripts/process_sentiment.py --unprocessed --batch-size 25
python scripts/generate_signals.py --all --backfill --days 30
```

### Configuration Options

Key environment variables for automation:
```env
# Scheduler timing
NEWS_COLLECTION_INTERVAL_HOURS=1
SENTIMENT_PROCESSING_INTERVAL_HOURS=1
MARKET_CLOSE_HOUR=16
MARKET_CLOSE_MINUTE=0

# Processing limits
SENTIMENT_BATCH_SIZE=25
MAX_SENTIMENT_ARTICLES_PER_RUN=200
NEWS_ARTICLES_PER_SYMBOL=50

# Model settings
USE_FINBERT=True
MIN_FUZZY_MATCH_SCORE=0.7
```

## 🎯 Test UI (Streamlit)

Interactive web interface for testing the recommendation system:

```bash
# Start the UI (requires API server running)
streamlit run app/test_ui.py --server.port 8501
```

### UI Features

- **Portfolio Configuration**: Set capital, risk tolerance, horizon
- **Real-time Health Monitoring**: API status and data freshness
- **Interactive Visualizations**: Allocation charts and breakdowns
- **Risk Analysis**: Scenario modeling and diversification metrics  
- **Export Capabilities**: Download results as JSON/CSV
- **AI Explanations**: Detailed reasoning behind recommendations

## 📡 API Endpoints

### Portfolio Recommendations
```bash
# Get portfolio recommendations
POST /api/recommend
{
    "capital": 50000,
    "risk": 0.5,
    "horizon_years": 5,
    "exclusions": ["TSLA", "GME"]
}

# Check system health
GET /api/recommend/health
```

### Example Response
```json
{
    "buckets": {
        "stocks": [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "allocated": 15000.0,
                "percentage": 30.0,
                "score": 0.847,
                "breakdown": {
                    "sentiment": 0.82,
                    "fundamental": 0.91,
                    "momentum": 0.76,
                    "volatility": 0.89
                }
            }
        ],
        "etfs": [...]
    },
    "total_allocated": 50000.0,
    "explanation_text": "Based on your balanced risk profile..."
}
```

## � Database Models

### Core Models
- **Company**: Asset information (symbols, names, sectors, market cap)
- **DailyPrice**: Historical price data and technical indicators
- **QuarterlyFundamental**: Financial metrics and ratios

### News & Sentiment Models  
- **NewsArticle**: Article storage with deduplication
- **NewsAssetMap**: Fuzzy-matched article-asset relationships
- **NewsSentiment**: FinBERT + VADER sentiment analysis results
- **AssetDailySignals**: Aggregated daily metrics and signals

## 🔧 Database Management

If starting fresh, Alembic is already initialized. The configuration is in `alembic.ini` and the environment setup is in `alembic/env.py`.

### Creating Migrations

#### 1. Check Your Models
Before creating migrations, verify all models are properly loaded:

```bash
python check_metadata.py
```

**Expected output:**
```
--- Starting metadata check ---

SUCCESS: Found the following tables in metadata:
- companies
- daily_prices
- quarterly_fundamentals
- users

--- Metadata check finished ---
```

#### 2. Generate Migration Files

When you add/modify models, create a new migration:

```bash
# Generate migration automatically based on model changes
alembic revision --autogenerate -m "Description of changes"

# Example:
alembic revision --autogenerate -m "Add new column to company model"
alembic revision --autogenerate -m "Create initial tables"
```

#### 3. Review Generated Migration

Always review the generated migration file in `alembic/versions/` before applying:

```python
# Example migration file: alembic/versions/xxxxx_create_initial_tables.py
def upgrade() -> None:
    # Operations to apply the migration
    op.create_table('companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=10), nullable=False),
        # ... more columns
    )

def downgrade() -> None:
    # Operations to reverse the migration
    op.drop_table('companies')
```

### Applying Migrations

#### Apply All Pending Migrations
```bash
alembic upgrade head
```

#### Apply Specific Migration
```bash
alembic upgrade <revision_id>
```

#### Rollback Migrations
```bash
# Rollback to previous migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

### Migration Management Commands

#### Check Current Migration Status
```bash
alembic current
```

#### View Migration History
```bash
alembic history
alembic history --verbose
```

#### Show SQL Without Executing
```bash
alembic upgrade head --sql
alembic downgrade -1 --sql
```

## 🔄 Complete Workflow Example

### First Time Setup
```bash
# 1. Activate environment
.\env\Scripts\Activate.ps1
cd Lumia

# 2. Check models are loaded
python check_metadata.py

# 3. Create initial migration
alembic revision --autogenerate -m "Initial migration"

# 4. Apply migration to database
alembic upgrade head
```

### Adding New Model/Column
```bash
# 1. Modify your model files (e.g., add new column to Company)
# 2. Check metadata
python check_metadata.py

# 3. Generate migration
alembic revision --autogenerate -m "Add business_summary to companies"

# 4. Review the generated file in alembic/versions/
# 5. Apply migration
alembic upgrade head
```

### Rollback Changes
```bash
# Check current status
alembic current

# Rollback last migration
alembic downgrade -1

# Or rollback to specific version
alembic downgrade abc123ef456
```

## 🛠️ Troubleshooting

### Common Issues

**Environment Setup**
```bash
# Virtual environment issues
.\..\..\env\Scripts\Activate.ps1
pip install -r requirements.txt

# Database connection errors  
python start_scheduler.py status
```

**Data Processing Issues**
```bash
# Check system health
python start_scheduler.py status

# Manual data processing
python scripts/collect_news.py --general --limit 10
python scripts/process_sentiment.py --unprocessed --batch-size 5
python scripts/generate_signals.py --symbols SPY --force
```

**API Problems**
```bash
# Test API connectivity
curl http://localhost:8000/api/recommend/health

# Check logs
tail -f logs/scheduler.log
tail -f logs/automation_manager.log
```

**Model Loading Issues**
```bash
# Test sentiment models
python -c "from app.services.sentiment_worker import SentimentWorker; print('Models OK')"

# Skip model download in development
export SKIP_MODEL_DOWNLOAD=True
export MOCK_EXTERNAL_APIS=True
```

### Performance Optimization

**For Large Datasets:**
- Reduce `SENTIMENT_BATCH_SIZE` to 10-15
- Increase `NEWS_COLLECTION_INTERVAL_HOURS` to 2-4
- Use `MAX_SENTIMENT_ARTICLES_PER_RUN` limit

**For Limited Resources:**  
- Set `USE_FINBERT=False` to use only VADER
- Enable `MOCK_EXTERNAL_APIS=True` for testing
- Reduce `NEWS_ARTICLES_PER_SYMBOL` to 25

## 🔒 Production Deployment

### Environment Variables
```env
# Production settings
DEBUG_MODE=False
LOG_LEVEL=WARNING
SCHEDULER_LOG_LEVEL=INFO

# Security
DATABASE_URL=postgresql://user:pass@prod-db:5432/lumia
NEWSAPI_KEY=prod_api_key_here

# Performance
SENTIMENT_BATCH_SIZE=50
NEWS_COLLECTION_INTERVAL_HOURS=2
MAX_PORTFOLIO_ASSETS=15
```

### Monitoring & Alerting
```bash
# System health checks
curl -f http://localhost:8000/api/recommend/health || alert

# Data freshness monitoring  
python start_scheduler.py status | grep "STALE" && alert

# Log monitoring
grep ERROR logs/scheduler.log | tail -10
```

### Backup & Recovery
```bash
# Database backup
pg_dump lumia_db > backup_$(date +%Y%m%d).sql

# Configuration backup
tar -czf config_backup.tar.gz .env alembic.ini config.py

# Recovery procedure
psql lumia_db < backup_20240928.sql
alembic upgrade head
```

## 📚 Advanced Usage

### Custom Risk Profiles
```python
# Modify app/routes/recommend.py
RISK_PROFILES = {
    'custom_conservative': {
        'sentiment': 0.10,
        'fundamental': 0.60, 
        'momentum': 0.10,
        'volatility': 0.20
    }
}
```

### Extended Data Sources
```python
# Add new collector in collectors/
class CustomNewsCollector(BaseCollector):
    def collect_from_source(self, symbol):
        # Custom implementation
        pass
```

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
