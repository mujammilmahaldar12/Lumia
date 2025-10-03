# 🚀 LUMIA COLLECTOR - SINGLE SCRIPT SYSTEM

## ✨ What Changed?

- ✅ **25 YEARS** minimum historical data (not 90 days)
- ✅ **SINGLE SCRIPT** to run everything: `lumia_collector.py`
- ✅ **COMPONENTS** for reusable functions
- ✅ **CLEANED UP** - removed 4 old scripts, kept only utilities

## 🎯 ONE SCRIPT TO RULE THEM ALL

### New User (First Time):
```bash
python scripts/lumia_collector.py --first-time
```
**What it does:**
- ✅ Detects empty database
- ✅ Collects ALL assets (stocks, ETFs, mutual funds, crypto)
- ✅ Downloads **25 YEARS** of price history
- ✅ Takes 3-4 hours (one-time only!)

### Daily Updates:
```bash
python scripts/lumia_collector.py
```
**What it does:**
- ✅ AI analyzes what you already have
- ✅ Only collects what changed since last run
- ✅ Smart date ranges (days, not years)
- ✅ Takes 10-20 minutes

### Check What It Would Do:
```bash
python scripts/lumia_collector.py --analysis
```

### Database Status:
```bash
python scripts/lumia_collector.py --status
```

## 📁 New File Structure

```
Lumia/
├── scripts/
│   ├── lumia_collector.py       # 🎯 MAIN SCRIPT (only one you need!)
│   └── collector_utilities.py  # 🔧 Utilities (kept)
├── components/
│   ├── intelligence.py         # 🧠 Smart analysis
│   └── execution.py            # 🚀 Collection execution
├── collectors/                 # 📊 Individual collectors
└── models/                     # 📋 Database models
```

## 🧠 Smart Features

### AI Intelligence:
- **Empty Database** → "First time setup - collect 25 years"
- **5,000+ Assets** → "Mature database - just update prices"
- **Stale Data** → "Refresh assets + prices"
- **Recent Run** → "Quick price update only"

### Date Range Optimization:
- **First Run**: 25 years of history
- **Daily Updates**: Last 7 days only
- **Gap Filling**: Exact missing date range
- **Stale Recovery**: From last known date

## ⚡ Quick Start

### For New Users:
```bash
# First time - get 25 years of data
python scripts/lumia_collector.py --first-time

# Let it run for 3-4 hours (one-time setup)
```

### For Daily Use:
```bash
# Smart mode - AI decides everything
python scripts/lumia_collector.py

# Usually takes 10-20 minutes
```

### For Automation:
```bash
# Add to cron/task scheduler
python scripts/lumia_collector.py --quiet
```

## 🎉 Benefits

1. **SIMPLE**: One command does everything
2. **SMART**: AI decides what to collect
3. **FAST**: Optimized date ranges
4. **COMPLETE**: 25 years of historical data
5. **CLEAN**: No more multiple scripts confusion

## 🚨 Important Notes

- **First run takes 3-4 hours** (25 years of data!)
- **Daily runs take 10-20 minutes** (smart updates)
- **AI learns from your database** (gets smarter over time)
- **All tracking in `collector_runs` table**

---

## 🎯 TLDR

### Old Way (4 scripts, confusing):
```bash
python scripts/collector.py          # Which one?
python scripts/auto_collector.py     # Too many options
python scripts/smart_collector.py    # Overwhelming
```

### New Way (1 script, simple):
```bash
python scripts/lumia_collector.py    # That's it!
```

**Just run it and the AI handles everything!** 🧠✨