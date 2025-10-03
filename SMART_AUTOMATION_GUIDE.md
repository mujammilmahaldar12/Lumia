# 🧠 Lumia Smart Data Collection Automation

Your intelligent data collection system that learns and adapts! No more guessing what to collect - the AI decides for you.

## ✨ What Makes It Smart?

### 🔍 **Intelligence Analysis**
- Automatically analyzes your database state
- Checks `collector_runs` table for collection history  
- Determines optimal collection strategy
- Calculates date ranges for efficient updates

### 🎯 **Adaptive Modes**
- **First Time Setup**: New user? Collects everything (90 days history)
- **Incremental Update**: Daily maintenance with smart date ranges
- **Price Only**: Just update prices when assets are sufficient
- **Full Refresh**: Comprehensive update when data is stale
- **Maintenance**: Data quality fixes and cleanup

### ⚡ **Performance Optimized**
- Only collects what's needed
- Smart date ranges (3 days vs 90 days vs full history)
- Skips collectors when data is current
- Batch processing for efficiency

## 🚀 Quick Start

### New User (First Time)
```bash
# The AI will detect this is your first run and collect everything
python scripts/auto_collector.py

# Or force first-time mode explicitly
python scripts/auto_collector.py --first-time
```

### Daily Updates
```bash
# Smart mode - AI decides what to collect
python scripts/auto_collector.py

# The AI will:
# - Check when you last ran collectors
# - Analyze price data coverage
# - Only collect what's needed (usually just prices)
# - Use optimal date ranges
```

### Analysis Mode
```bash
# See what the AI would do without actually collecting
python scripts/auto_collector.py --analysis
```

## 🧠 How The AI Thinks

### Database State Detection
```
EMPTY       → First time setup (collect everything)
MINIMAL     → <1,000 assets (refresh all)
INCOMPLETE  → Missing asset classes (fill gaps)
STALE       → Data exists but old (smart refresh)
MATURE      → >5,000 assets (incremental only)
```

### Smart Date Ranges
```
First Run:   90 days of price history
Stale Data:  From last price date to today
Daily Run:   Last 3 days only
Gaps:        Exact missing date range
```

### Collection Decisions
```
No collector runs found     → Run all collectors
Assets < 1,000             → Refresh assets + prices
Price coverage < 70%       → Focus on price collection
Last run > 7 days ago      → Full refresh
Last run yesterday         → Prices only
```

## 📋 Usage Examples

### Smart Automation (Recommended)
```bash
# Let AI decide what to collect
python scripts/auto_collector.py

# Example outputs:
# "Database is empty - running first-time setup"
# "Found 5,000 assets - collecting prices only"  
# "Data is stale - refreshing assets and prices"
```

### Force Specific Modes
```bash
# Force complete data collection
python scripts/auto_collector.py --first-time

# Only update daily prices
python scripts/auto_collector.py --daily-only

# Just show analysis without collecting
python scripts/auto_collector.py --analysis

# Show current database status
python scripts/auto_collector.py --status
```

### Quiet Mode for Automation
```bash
# Minimal output (good for cron jobs)
python scripts/auto_collector.py --quiet

# JSON output for parsing
python scripts/auto_collector.py --json
```

## 📊 Example Scenarios

### Scenario 1: New User
```
📅 Day 1: First run
🧠 AI Analysis: "Database is empty"
🎯 Decision: FIRST_TIME_SETUP mode
📋 Plan: stocks → etfs → mutual_funds → crypto → prices (90 days)
⏱️ Time: ~120 minutes
📈 Result: 15,000 assets, 50,000 prices
```

### Scenario 2: Daily Maintenance
```
📅 Day 2: Regular run  
🧠 AI Analysis: "Database mature, last run yesterday"
🎯 Decision: INCREMENTAL_UPDATE mode
📋 Plan: daily_prices only (last 3 days)
⏱️ Time: ~10 minutes
📈 Result: 5,000 new prices
```

### Scenario 3: After Vacation
```
📅 Day 10: Back from vacation
🧠 AI Analysis: "Data stale, 7 days since last run"
🎯 Decision: FULL_REFRESH mode
📋 Plan: assets + prices (last 7 days)
⏱️ Time: ~60 minutes
📈 Result: 1,000 new assets, 35,000 prices
```

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Customize intelligence parameters
export LUMIA_MIN_ASSETS_MATURE=5000      # Assets needed for mature DB
export LUMIA_MAX_DAYS_STALE=2            # Days before data considered stale
export LUMIA_PRICE_COVERAGE_THRESHOLD=0.7 # Required price coverage %
```

### Database Requirements
- Requires `collector_runs` table for tracking
- Automatically created if missing
- Stores execution history and performance metrics

## 📈 Monitoring & Logs

### Log Files
```
lumia_automation_YYYYMMDD.log    # Main automation log
smart_collector_YYYYMMDD.log     # Detailed collection log
```

### Status Monitoring
```bash
# Quick status check
python scripts/auto_collector.py --status

# Detailed analysis
python scripts/auto_collector.py --analysis
```

### Database Insights
The system tracks in `collector_runs` table:
- Last run dates for each collector
- Success/failure rates
- Performance metrics
- Data quality scores

## 🆚 vs Original Collector

| Feature | Original | Smart System |
|---------|----------|--------------|
| Decision Making | Manual/Fixed | AI-Powered |
| Date Ranges | Fixed (1 year) | Dynamic (3-90 days) |
| Collection Strategy | All or Nothing | Adaptive |
| New User Experience | Overwhelming | Guided |
| Daily Updates | Slow | Optimized |
| Error Recovery | Manual | Automatic |

## 🔄 Migration from Original

### Simple Migration
```bash
# Replace your old collector.py calls with:
python scripts/auto_collector.py

# The smart system will:
# 1. Analyze your existing data
# 2. Determine optimal strategy
# 3. Fill any gaps intelligently
```

### Cron Job Example
```bash
# Daily automation (replace in crontab)
0 6 * * * cd /path/to/lumia && python scripts/auto_collector.py --quiet
```

## ⚠️ Important Notes

### First Run Behavior
- **Empty Database**: Collects 90 days of price history (be patient!)
- **Existing Data**: Analyzes and fills gaps intelligently
- **API Limits**: Respects rate limits with smart delays

### Performance Tips
- First run: 1-2 hours (one-time only)
- Daily runs: 5-15 minutes
- Use `--analysis` to preview before running
- Monitor logs for optimization insights

### Error Handling
- Automatic retries with exponential backoff
- Continues on partial failures
- Detailed error logging
- Graceful degradation

## 🎯 Best Practices

1. **Let AI Decide**: Use default mode for best results
2. **Regular Schedule**: Run daily for optimal performance  
3. **Monitor Logs**: Check for optimization opportunities
4. **Use Analysis**: Preview before long collections
5. **Status Checks**: Monitor database health regularly

## 🚨 Troubleshooting

### Common Issues
```bash
# If you see "No collectors to run"
python scripts/auto_collector.py --analysis  # Check reasoning

# Force refresh if needed
python scripts/auto_collector.py --first-time

# Check database status
python scripts/auto_collector.py --status
```

### Debug Mode
```bash
# Enable debug logging
export PYTHONPATH=. && python -u scripts/auto_collector.py
```

---

## 🎉 Success! 

You now have an intelligent automation system that:
- ✅ Detects if you're a new user or returning user
- ✅ Only collects what's actually needed  
- ✅ Uses optimal date ranges for speed
- ✅ Learns from previous runs
- ✅ Adapts to your database state
- ✅ Provides detailed insights and reasoning

**Just run `python scripts/auto_collector.py` and let the AI handle everything!** 🧠✨