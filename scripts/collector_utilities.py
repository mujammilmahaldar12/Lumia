"""
🛠️ LUMIA COLLECTOR UTILITIES 🛠️

Maintenance, monitoring, and utility functions for the collector orchestrator.
Provides data cleanup, health checks, performance optimization, and reporting tools.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import func, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.collector_run import CollectorRun
from models.assets import Asset
from models.daily_price import DailyPrice
from models.crypto import Crypto
from models.etf import ETF
from models.mutual_fund import MutualFund

logger = logging.getLogger('lumia.collector_utilities')

class CollectorMaintenanceManager:
    """🧹 Maintenance and cleanup utilities for collector system"""
    
    def __init__(self):
        self.session = SessionLocal()
    
    def cleanup_old_runs(self, days_to_keep: int = 30) -> Dict:
        """🗑️ Clean up old collector run records"""
        logger.info(f"[CLEANUP] Removing collector runs older than {days_to_keep} days")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Count records to be deleted
        old_runs = self.session.query(CollectorRun)\
            .filter(CollectorRun.started_at < cutoff_date)\
            .all()
        
        count = len(old_runs)
        
        if count > 0:
            # Delete old runs
            self.session.query(CollectorRun)\
                .filter(CollectorRun.started_at < cutoff_date)\
                .delete()
            self.session.commit()
            
            logger.info(f"[OK] Deleted {count} old collector run records")
        else:
            logger.info("[INFO] No old collector runs to clean up")
        
        return {
            'deleted_runs': count,
            'cutoff_date': cutoff_date,
            'remaining_runs': self.session.query(CollectorRun).count()
        }
    
    def cleanup_duplicate_prices(self) -> Dict:
        """🔄 Remove duplicate price records"""
        logger.info("[CLEANUP] Removing duplicate price records")
        
        # Find duplicates (same asset_id and date)
        duplicate_query = text("""
            SELECT asset_id, date, COUNT(*) as count
            FROM daily_prices 
            GROUP BY asset_id, date 
            HAVING COUNT(*) > 1
        """)
        
        duplicates = self.session.execute(duplicate_query).fetchall()
        
        cleaned_count = 0
        for dup in duplicates:
            asset_id, date, count = dup
            
            # Keep the latest record, delete others
            records = self.session.query(DailyPrice)\
                .filter(DailyPrice.asset_id == asset_id)\
                .filter(DailyPrice.date == date)\
                .order_by(DailyPrice.created_at.desc())\
                .all()
            
            # Delete all but the first (newest) record
            for record in records[1:]:
                self.session.delete(record)
                cleaned_count += 1
        
        if cleaned_count > 0:
            self.session.commit()
            logger.info(f"[OK] Removed {cleaned_count} duplicate price records")
        else:
            logger.info("[INFO] No duplicate price records found")
        
        return {
            'duplicates_found': len(duplicates),
            'records_removed': cleaned_count
        }
    
    def optimize_database(self) -> Dict:
        """⚡ Optimize database performance"""
        logger.info("[OPTIMIZE] Analyzing database performance")
        
        results = {}
        
        try:
            # Analyze tables for better query planning
            tables = ['assets', 'daily_prices', 'collector_runs', 'crypto', 'etf', 'mutual_fund']
            
            for table in tables:
                self.session.execute(text(f"ANALYZE {table}"))
                logger.info(f"   [ANALYZE] {table}")
            
            self.session.commit()
            
            # Get table sizes
            size_query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)
            
            table_sizes = self.session.execute(size_query).fetchall()
            results['table_sizes'] = [
                {'table': row[1], 'size': row[2]} 
                for row in table_sizes
            ]
            
            logger.info("[OK] Database optimization completed")
            
        except Exception as e:
            logger.warning(f"[WARN] Database optimization partially failed: {e}")
            results['error'] = str(e)
        
        return results
    
    def validate_data_integrity(self) -> Dict:
        """🔍 Validate data integrity across all tables"""
        logger.info("[VALIDATE] Checking data integrity")
        
        issues = []
        
        # Check for assets without prices (older than 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        assets_without_prices = self.session.query(Asset)\
            .outerjoin(DailyPrice)\
            .filter(DailyPrice.id.is_(None))\
            .filter(Asset.created_at < week_ago)\
            .count()
        
        if assets_without_prices > 0:
            issues.append({
                'type': 'missing_prices',
                'count': assets_without_prices,
                'description': f'{assets_without_prices} assets have no price data'
            })
        
        # Check for price records without assets
        orphan_prices = self.session.query(DailyPrice)\
            .outerjoin(Asset)\
            .filter(Asset.id.is_(None))\
            .count()
        
        if orphan_prices > 0:
            issues.append({
                'type': 'orphan_prices',
                'count': orphan_prices,
                'description': f'{orphan_prices} price records have no corresponding asset'
            })
        
        # Check for failed collector runs in last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_failures = self.session.query(CollectorRun)\
            .filter(CollectorRun.started_at >= yesterday)\
            .filter(CollectorRun.status == 'failed')\
            .count()
        
        if recent_failures > 0:
            issues.append({
                'type': 'recent_failures',
                'count': recent_failures,
                'description': f'{recent_failures} collector runs failed in last 24 hours'
            })
        
        logger.info(f"[VALIDATE] Data integrity check completed - {len(issues)} issues found")
        
        return {
            'issues_found': len(issues),
            'issues': issues,
            'checked_at': datetime.utcnow()
        }

class CollectorReporter:
    """📊 Reporting and analytics for collector system"""
    
    def __init__(self):
        self.session = SessionLocal()
    
    def generate_daily_report(self, date: Optional[datetime] = None) -> Dict:
        """📈 Generate comprehensive daily collection report"""
        if date is None:
            date = datetime.utcnow().date()
        
        logger.info(f"[REPORT] Generating daily report for {date}")
        
        # Get all runs for the specified date
        start_date = datetime.combine(date, datetime.min.time())
        end_date = start_date + timedelta(days=1)
        
        daily_runs = self.session.query(CollectorRun)\
            .filter(CollectorRun.started_at >= start_date)\
            .filter(CollectorRun.started_at < end_date)\
            .all()
        
        # Calculate statistics
        total_runs = len(daily_runs)
        successful_runs = len([r for r in daily_runs if r.status == 'completed'])
        failed_runs = len([r for r in daily_runs if r.status == 'failed'])
        
        total_records = sum(r.records_processed or 0 for r in daily_runs)
        total_duration = sum(r.duration_seconds or 0 for r in daily_runs)
        
        # Collector-specific stats
        collector_stats = {}
        for run in daily_runs:
            name = run.collector_name
            if name not in collector_stats:
                collector_stats[name] = {
                    'runs': 0,
                    'successful': 0,
                    'failed': 0,
                    'total_records': 0,
                    'total_duration': 0,
                    'avg_duration': 0
                }
            
            stats = collector_stats[name]
            stats['runs'] += 1
            stats['total_records'] += run.records_processed or 0
            stats['total_duration'] += run.duration_seconds or 0
            
            if run.status == 'completed':
                stats['successful'] += 1
            elif run.status == 'failed':
                stats['failed'] += 1
        
        # Calculate averages
        for name, stats in collector_stats.items():
            if stats['runs'] > 0:
                stats['avg_duration'] = stats['total_duration'] / stats['runs']
                stats['success_rate'] = (stats['successful'] / stats['runs']) * 100
        
        report = {
            'date': date.isoformat(),
            'summary': {
                'total_runs': total_runs,
                'successful_runs': successful_runs,
                'failed_runs': failed_runs,
                'success_rate': (successful_runs / total_runs * 100) if total_runs > 0 else 0,
                'total_records_processed': total_records,
                'total_duration_seconds': total_duration,
                'avg_duration_per_run': total_duration / total_runs if total_runs > 0 else 0
            },
            'collectors': collector_stats,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return report
    
    def get_performance_trends(self, days: int = 7) -> Dict:
        """📈 Get performance trends over specified days"""
        logger.info(f"[TRENDS] Analyzing performance for last {days} days")
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get daily aggregations - using simpler approach for compatibility
        from sqlalchemy import case
        
        daily_stats = self.session.query(
            func.date(CollectorRun.started_at).label('date'),
            func.count(CollectorRun.id).label('total_runs'),
            func.sum(
                case(
                    (CollectorRun.status == 'completed', 1),
                    else_=0
                )
            ).label('successful_runs'),
            func.sum(CollectorRun.records_processed).label('total_records'),
            func.avg(CollectorRun.duration_seconds).label('avg_duration')
        ).filter(
            CollectorRun.started_at >= start_date
        ).group_by(
            func.date(CollectorRun.started_at)
        ).order_by(
            func.date(CollectorRun.started_at)
        ).all()
        
        trends = {
            'period': {
                'start_date': start_date.date().isoformat(),
                'end_date': end_date.date().isoformat(),
                'days': days
            },
            'daily_stats': [],
            'totals': {
                'total_runs': 0,
                'successful_runs': 0,
                'total_records': 0,
                'avg_success_rate': 0
            }
        }
        
        for stat in daily_stats:
            date_str = stat.date.isoformat()
            total_runs = stat.total_runs or 0
            successful = stat.successful_runs or 0
            
            daily_data = {
                'date': date_str,
                'total_runs': total_runs,
                'successful_runs': successful,
                'success_rate': (successful / total_runs * 100) if total_runs > 0 else 0,
                'total_records': stat.total_records or 0,
                'avg_duration_seconds': float(stat.avg_duration or 0)
            }
            
            trends['daily_stats'].append(daily_data)
            
            # Update totals
            trends['totals']['total_runs'] += total_runs
            trends['totals']['successful_runs'] += successful
            trends['totals']['total_records'] += stat.total_records or 0
        
        # Calculate overall success rate
        if trends['totals']['total_runs'] > 0:
            trends['totals']['avg_success_rate'] = (
                trends['totals']['successful_runs'] / 
                trends['totals']['total_runs'] * 100
            )
        
        return trends
    
    def get_asset_summary(self) -> Dict:
        """Get comprehensive asset summary"""
        logger.info("[REPORT] Generating asset summary")
        
        # Count assets by type
        total_assets = self.session.query(Asset).count()
        total_cryptos = self.session.query(Crypto).count()
        total_etfs = self.session.query(ETF).count()
        total_mutual_funds = self.session.query(MutualFund).count()
        
        # Calculate stocks (assets that aren't crypto/etf/mutual fund)
        total_stocks = total_assets - total_cryptos - total_etfs - total_mutual_funds
        
        # Price data statistics
        total_price_records = self.session.query(DailyPrice).count()
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_assets = self.session.query(Asset)\
            .filter(Asset.created_at >= week_ago)\
            .count()
        
        recent_prices = self.session.query(DailyPrice)\
            .filter(DailyPrice.created_at >= week_ago)\
            .count()
        
        summary = {
            'assets': {
                'total': total_assets,
                'stocks': total_stocks,
                'etfs': total_etfs,
                'mutual_funds': total_mutual_funds,
                'cryptocurrencies': total_cryptos
            },
            'price_data': {
                'total_records': total_price_records,
                'avg_records_per_asset': total_price_records / total_assets if total_assets > 0 else 0
            },
            'recent_activity': {
                'new_assets_7_days': recent_assets,
                'new_prices_7_days': recent_prices
            },
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return summary