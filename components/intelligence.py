"""
🧠 LUMIA INTELLIGENCE ENGINE
Smart analysis and decision-making components
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger('lumia.intelligence')

class DatabaseState(Enum):
    """Database state analysis results"""
    EMPTY = "empty"
    MINIMAL = "minimal"
    INCOMPLETE = "incomplete"
    MATURE = "mature"
    STALE = "stale"

class CollectionMode(Enum):
    """Different collection modes"""
    FIRST_TIME_SETUP = "first_time_setup"
    FULL_REFRESH = "full_refresh"
    INCREMENTAL_UPDATE = "incremental_update"
    PRICE_ONLY = "price_only"
    MAINTENANCE = "maintenance"

@dataclass
class IntelligenceReport:
    """Smart analysis report"""
    database_state: DatabaseState
    collection_mode: CollectionMode
    total_assets: int = 0
    total_prices: int = 0
    asset_breakdown: Dict[str, int] = None
    price_coverage: Dict[str, any] = None
    last_run_date: Optional[date] = None
    last_successful_runs: Dict[str, datetime] = None
    failed_recent_runs: List[str] = None
    collectors_to_run: List[str] = None
    optimal_date_range: Optional[Dict[str, str]] = None
    estimated_time_minutes: int = 0
    priority_reasoning: str = ""
    expected_new_assets: int = 0
    expected_new_prices: int = 0

class IntelligenceEngine:
    """Smart analysis engine"""
    
    def __init__(self):
        self.min_assets_for_mature_db = 5000
        self.max_days_before_stale = 2
        self.price_coverage_threshold = 0.7
        self.min_history_years = 25
        self.default_history_days = 25 * 365  # 25 years
    
    def analyze_database(self, session) -> IntelligenceReport:
        """Analyze database state and generate intelligence report"""
        
        logger.info("[AI] Starting database intelligence analysis...")
        
        from models.assets import Asset
        from models.daily_price import DailyPrice
        from models.collector_run import CollectorRun
        
        report = IntelligenceReport(
            database_state=DatabaseState.EMPTY,
            collection_mode=CollectionMode.FIRST_TIME_SETUP,
            asset_breakdown={},
            price_coverage={},
            last_successful_runs={},
            failed_recent_runs=[],
            collectors_to_run=[],
        )
        
        # Asset Analysis
        report.total_assets = session.query(Asset).filter(Asset.is_active == True).count()
        
        asset_types = ['stock', 'etf', 'mutual_fund', 'crypto']
        for asset_type in asset_types:
            count = session.query(Asset).filter(
                Asset.type == asset_type,
                Asset.is_active == True
            ).count()
            report.asset_breakdown[asset_type] = count
        
        # Price Analysis
        report.total_prices = session.query(DailyPrice).count()
        
        if report.total_prices > 0:
            latest_price = session.query(DailyPrice.date).order_by(DailyPrice.date.desc()).first()
            oldest_price = session.query(DailyPrice.date).order_by(DailyPrice.date.asc()).first()
            
            if latest_price:
                report.price_coverage['latest_date'] = latest_price[0]
                report.price_coverage['oldest_date'] = oldest_price[0] if oldest_price else latest_price[0]
                report.price_coverage['days_since_update'] = (date.today() - latest_price[0]).days
                
                assets_with_recent_prices = session.query(DailyPrice.asset_id).filter(
                    DailyPrice.date >= date.today() - timedelta(days=7)
                ).distinct().count()
                
                if report.total_assets > 0:
                    report.price_coverage['coverage_percentage'] = assets_with_recent_prices / report.total_assets
                else:
                    report.price_coverage['coverage_percentage'] = 0.0
        
        # Collection History Analysis
        total_runs = session.query(CollectorRun).count()
        
        if total_runs > 0:
            collector_types = ['stocks', 'etfs', 'mutual_funds', 'cryptocurrencies', 'daily_prices']
            
            for collector_type in collector_types:
                last_run = session.query(CollectorRun).filter(
                    CollectorRun.collector_name == collector_type,
                    CollectorRun.status == 'completed'
                ).order_by(CollectorRun.completed_at.desc()).first()
                
                if last_run:
                    report.last_successful_runs[collector_type] = last_run.completed_at
            
            recent_failures = session.query(CollectorRun).filter(
                CollectorRun.status == 'failed',
                CollectorRun.started_at >= datetime.utcnow() - timedelta(days=7)
            ).all()
            
            report.failed_recent_runs = [run.collector_name for run in recent_failures]
            
            last_any_run = session.query(CollectorRun).order_by(
                CollectorRun.completed_at.desc()
            ).first()
            
            if last_any_run and last_any_run.completed_at:
                report.last_run_date = last_any_run.completed_at.date()
        
        # Decision Making
        report = self._make_intelligent_decisions(report)
        
        return report
    
    def _make_intelligent_decisions(self, report: IntelligenceReport) -> IntelligenceReport:
        """Make intelligent collection decisions"""
        
        # Determine database state
        if report.total_assets == 0:
            report.database_state = DatabaseState.EMPTY
            report.priority_reasoning = "Database is empty - first time setup required"
            
        elif report.total_assets < 1000:
            report.database_state = DatabaseState.MINIMAL
            report.priority_reasoning = f"Only {report.total_assets} assets - needs more data"
            
        elif any(count < 100 for count in report.asset_breakdown.values()):
            report.database_state = DatabaseState.INCOMPLETE
            missing_types = [k for k, v in report.asset_breakdown.items() if v < 100]
            report.priority_reasoning = f"Missing asset types: {', '.join(missing_types)}"
            
        elif (report.price_coverage.get('days_since_update', 999) > self.max_days_before_stale or
              report.price_coverage.get('coverage_percentage', 0) < self.price_coverage_threshold):
            report.database_state = DatabaseState.STALE
            report.priority_reasoning = "Data exists but is stale - needs refresh"
            
        else:
            report.database_state = DatabaseState.MATURE
            report.priority_reasoning = "Database is mature - incremental updates only"
        
        # Determine collection strategy
        report = self._determine_strategy(report)
        
        return report
    
    def _determine_strategy(self, report: IntelligenceReport) -> IntelligenceReport:
        """Determine optimal collection strategy"""
        
        if report.database_state == DatabaseState.EMPTY:
            # First time - 25 years of data
            report.collection_mode = CollectionMode.FIRST_TIME_SETUP
            report.collectors_to_run = ['stocks', 'etfs', 'mutual_funds', 'cryptocurrencies', 'daily_prices']
            report.estimated_time_minutes = 240
            report.expected_new_assets = 15000
            report.expected_new_prices = 500000
            report.optimal_date_range = {
                'from_date': (date.today() - timedelta(days=self.default_history_days)).strftime('%Y-%m-%d'),
                'to_date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'reasoning': f'Initial {self.min_history_years}-year history for all assets'
            }
            
        elif report.database_state == DatabaseState.MINIMAL:
            report.collection_mode = CollectionMode.FULL_REFRESH
            report.collectors_to_run = ['stocks', 'etfs', 'mutual_funds', 'cryptocurrencies', 'daily_prices']
            report.estimated_time_minutes = 180
            
        elif report.database_state == DatabaseState.INCOMPLETE:
            report.collection_mode = CollectionMode.FULL_REFRESH
            missing_collectors = []
            
            if report.asset_breakdown.get('stock', 0) < 2000:
                missing_collectors.append('stocks')
            if report.asset_breakdown.get('etf', 0) < 100:
                missing_collectors.append('etfs')
            if report.asset_breakdown.get('mutual_fund', 0) < 500:
                missing_collectors.append('mutual_funds')
            if report.asset_breakdown.get('crypto', 0) < 50:
                missing_collectors.append('cryptocurrencies')
            
            missing_collectors.append('daily_prices')
            report.collectors_to_run = missing_collectors
            report.estimated_time_minutes = len(missing_collectors) * 30
            
        elif report.database_state == DatabaseState.STALE:
            days_stale = report.price_coverage.get('days_since_update', 0)
            
            if days_stale > 7:
                report.collection_mode = CollectionMode.FULL_REFRESH
                report.collectors_to_run = ['stocks', 'etfs', 'mutual_funds', 'cryptocurrencies', 'daily_prices']
                report.estimated_time_minutes = 120
            else:
                report.collection_mode = CollectionMode.PRICE_ONLY
                report.collectors_to_run = ['daily_prices']
                report.estimated_time_minutes = 30
                
            # Smart date range
            if report.price_coverage.get('latest_date'):
                from_date = report.price_coverage['latest_date']
                report.optimal_date_range = {
                    'from_date': from_date.strftime('%Y-%m-%d'),
                    'to_date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'reasoning': f'Update from last known price date ({from_date})'
                }
            else:
                from_date = date.today() - timedelta(days=self.default_history_days)
                report.optimal_date_range = {
                    'from_date': from_date.strftime('%Y-%m-%d'),
                    'to_date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'reasoning': '25 years of historical data for stale database'
                }
            
        else:  # MATURE
            report.collection_mode = CollectionMode.INCREMENTAL_UPDATE
            collectors_needed = []
            
            for collector in ['stocks', 'etfs', 'mutual_funds', 'cryptocurrencies']:
                last_run = report.last_successful_runs.get(collector)
                if not last_run or (datetime.utcnow() - last_run).days >= 7:
                    collectors_needed.append(collector)
            
            last_price_run = report.last_successful_runs.get('daily_prices')
            if not last_price_run or (datetime.utcnow() - last_price_run).days >= 1:
                collectors_needed.append('daily_prices')
            
            report.collectors_to_run = collectors_needed if collectors_needed else ['daily_prices']
            report.estimated_time_minutes = len(report.collectors_to_run) * 15
            
            report.optimal_date_range = {
                'from_date': (date.today() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'to_date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'reasoning': 'Incremental update - last 7 days'
            }
        
        return report