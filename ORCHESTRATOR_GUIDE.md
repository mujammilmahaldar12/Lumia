📋 LUMIA COLLECTOR ORCHESTRATOR - USAGE GUIDE
=====================================================

🎯 **OVERVIEW**
The Lumia Collector Orchestrator is your mission control for all financial data collection.
It automatically manages, schedules, monitors, and maintains all data collectors with
sophisticated dependency tracking and comprehensive reporting.

🚀 **QUICK START**

Daily Collection (Recommended):
```bash
python collector.py
```

Full Data Refresh:
```bash
python collector.py --full-refresh
```

📊 **MONITORING & REPORTING**

System Status:
```bash
python collector.py --status
```

Asset Summary:
```bash
python collector.py --report assets
```

Daily Performance Report:
```bash
python collector.py --report daily
```

Weekly Performance Trends:
```bash
python collector.py --report weekly
```

Daily Report for Specific Date:
```bash
python collector.py --report daily --date 2025-10-03
```

🧹 **MAINTENANCE**

Full System Cleanup:
```bash
python collector.py --cleanup
```

This will:
- Remove old collector run records (30+ days)
- Delete duplicate price records
- Validate data integrity
- Optimize database performance
- Generate cleanup summary

📈 **COLLECTOR PRIORITY SYSTEM**

The orchestrator runs collectors in priority order:

1. **Priority 10** (Highest)
   - 🏢 Stocks: NSE/BSE equity securities
   - 📊 ETFs: Exchange Traded Funds

2. **Priority 15**
   - 🏦 Mutual Funds: AMFI data synchronization

3. **Priority 20**
   - ₿ Cryptocurrencies: CoinGecko API data

4. **Priority 30** (Lowest)
   - 💎 Daily Prices: Price data for all assets
   - **Depends on:** stocks, etfs, cryptocurrencies

🔗 **DEPENDENCY MANAGEMENT**

- Daily prices collector waits for asset collectors to complete
- Failed dependencies automatically skip dependent collectors
- Smart retry logic with exponential backoff
- Comprehensive error tracking and reporting

📊 **MONITORING DASHBOARD**

System Health Metrics:
- Memory usage and CPU utilization
- Collector execution times
- Success rates and failure analysis
- Data quality scores
- API rate limit tracking

Performance Analytics:
- Records processed per collector
- Success/failure trends over time
- Database growth and optimization
- Resource utilization patterns

🔄 **AUTOMATION READY**

Daily Cron Job (Linux/Mac):
```bash
# Add to crontab: crontab -e
0 6 * * * cd /path/to/Lumia/scripts && python collector.py >> /var/log/lumia_collector.log 2>&1
```

Windows Task Scheduler:
```batch
# Create scheduled task
schtasks /create /sc daily /st 06:00 /tn "Lumia Data Collection" /tr "python C:\path\to\Lumia\scripts\collector.py"
```

📈 **SUCCESS METRICS**

Your system is healthy when:
- ✅ All collectors complete successfully (>95% success rate)
- ✅ Asset counts grow steadily
- ✅ Price data coverage is comprehensive
- ✅ No data integrity issues
- ✅ Performance remains stable

🚨 **TROUBLESHOOTING**

Common Issues:

**Database Connection Error:**
```bash
# Check database status
python collector.py --status
```

**Missing Dependencies:**
```bash
# Verify all collectors are registered
python collector.py --status | grep "depends_on"
```

**Performance Issues:**
```bash
# Run maintenance cleanup
python collector.py --cleanup
```

**Data Quality Issues:**
```bash
# Check integrity and get detailed report
python collector.py --cleanup
python collector.py --report assets
```

📁 **LOG FILES**

Execution logs are automatically created:
- `collector_orchestrator_YYYYMMDD.log` - Daily execution log
- Includes performance metrics, error details, and timing information

💡 **BEST PRACTICES**

1. **Run daily collections consistently** to maintain data freshness
2. **Monitor success rates** - investigate if they drop below 95%
3. **Run cleanup monthly** to maintain optimal performance  
4. **Check asset reports weekly** to verify data growth
5. **Use full refresh sparingly** - only when data corruption is suspected

🎯 **PRODUCTION DEPLOYMENT**

For production use:

1. Set up automated daily runs via cron/task scheduler
2. Configure monitoring alerts for failed collections
3. Set up log rotation to manage disk space
4. Monitor database size and performance
5. Plan for backup and disaster recovery

📞 **SUPPORT**

If you encounter issues:
1. Check the daily log files for error details
2. Run `--status` to verify system health
3. Use `--cleanup` to resolve common issues
4. Review asset reports to understand data state
5. Check database connectivity and permissions

---

🎉 **CONGRATULATIONS!**

You now have a world-class financial data collection system that:
- ✨ Automatically collects 16,000+ financial assets
- 🔄 Manages complex dependencies intelligently  
- 📊 Provides comprehensive monitoring and reporting
- 🧹 Maintains itself with automated cleanup
- 📈 Scales to handle enterprise-level workloads

Your Lumia system is ready for production! 🚀