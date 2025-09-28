# Lumia CLI Scripts

This directory contains command-line interface scripts for managing the Lumia financial news analysis system.

## Scripts Overview

### 1. collect_news.py
Collects financial news articles from external sources (NewsAPI).

```bash
# Collect news for specific symbols
python collect_news.py --symbols AAPL,TSLA,SPY --limit 100

# Collect news for all active assets
python collect_news.py --all-assets --days 7

# Collect general financial news
python collect_news.py --general --limit 200
```

**Key Features:**
- Symbol-specific news collection
- Fuzzy matching for asset association
- Deduplication by URL
- Rate limiting and error handling

### 2. process_sentiment.py
Processes sentiment analysis on collected news articles using FinBERT and VADER models.

```bash
# Process all unprocessed articles
python process_sentiment.py --unprocessed --batch-size 50

# Process specific article IDs
python process_sentiment.py --article-ids 123,456,789

# Reprocess articles for specific symbols
python process_sentiment.py --reprocess --symbols AAPL,TSLA --days-back 30

# Show processing statistics
python process_sentiment.py --stats
```

**Key Features:**
- Dual-model sentiment analysis (FinBERT + VADER fallback)
- Batch processing for efficiency
- Reprocessing capabilities
- Processing statistics and monitoring

### 3. generate_signals.py
Generates aggregated daily signals combining sentiment, price, and fundamental data.

```bash
# Generate signals for all assets today
python generate_signals.py --all --date 2024-01-15

# Backfill signals for specific symbols
python generate_signals.py --symbols AAPL,TSLA --backfill --days 30

# Force regeneration of existing signals
python generate_signals.py --asset-ids 1,2,3 --force

# Show signal generation statistics
python generate_signals.py --stats
```

**Key Features:**
- Rolling sentiment averages (7d, 30d)
- Technical indicators integration
- Backfill capabilities for historical data
- Statistics and coverage monitoring

## Usage Patterns

### Daily Workflow
```bash
# 1. Collect today's news
python collect_news.py --all-assets --days 1

# 2. Process sentiment for new articles
python process_sentiment.py --unprocessed --batch-size 25

# 3. Generate today's signals
python generate_signals.py --all
```

### Backfill Historical Data
```bash
# 1. Collect historical news
python collect_news.py --all-assets --days 30

# 2. Process all sentiment
python process_sentiment.py --unprocessed

# 3. Backfill signals
python generate_signals.py --all --backfill --days 30
```

### Monitor and Maintain
```bash
# Check processing status
python process_sentiment.py --stats
python generate_signals.py --stats

# Reprocess problematic assets
python process_sentiment.py --reprocess --symbols TSLA,GME
python generate_signals.py --symbols TSLA,GME --force
```

## Configuration

All scripts use the same database configuration from `Lumia/config.py` and require:

1. **Database Setup**: PostgreSQL/TimescaleDB with proper schema
2. **API Keys**: NewsAPI key in environment variables
3. **Python Environment**: All dependencies from `requirements.txt`

### Environment Variables
```bash
export NEWSAPI_KEY="your_newsapi_key_here"
export DATABASE_URL="postgresql://user:pass@localhost/lumia_db"
```

### Dependencies
Key packages required:
- `fastapi` - Web framework
- `sqlalchemy` - Database ORM
- `transformers` - FinBERT sentiment model
- `nltk` - VADER sentiment model
- `rapidfuzz` - Fuzzy string matching
- `requests` - HTTP client for news collection

## Error Handling

All scripts include comprehensive error handling:

- **Network Issues**: Automatic retries with exponential backoff
- **Model Loading**: Graceful fallback from FinBERT to VADER
- **Database Errors**: Transaction rollbacks and connection recovery
- **Rate Limiting**: Respect API limits with proper delays

## Logging

Use the `--verbose` flag for detailed logging:

```bash
python collect_news.py --all-assets --verbose
python process_sentiment.py --unprocessed --verbose
python generate_signals.py --all --verbose
```

Log levels:
- **INFO**: Progress updates and summaries
- **DEBUG**: Detailed processing information
- **WARNING**: Non-fatal issues and fallbacks
- **ERROR**: Failed operations and exceptions

## Performance Tips

1. **Batch Processing**: Use appropriate batch sizes (25-50 articles)
2. **Parallel Execution**: Run different scripts concurrently
3. **Resource Management**: Monitor memory usage for large batches
4. **API Limits**: Respect external service rate limits

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Database Connections**: Check PostgreSQL service and credentials
3. **API Limits**: Verify NewsAPI quota and key validity
4. **Model Loading**: Ensure sufficient disk space for transformer models

### Recovery Procedures

1. **Failed Processing**: Use `--force` flag to regenerate signals
2. **Incomplete Batches**: Process specific article IDs
3. **Data Inconsistency**: Use reprocessing commands with date ranges

For detailed help on any script, use the `--help` flag:
```bash
python collect_news.py --help
python process_sentiment.py --help
python generate_signals.py --help
```