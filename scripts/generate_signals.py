#!/usr/bin/env python3
"""
CLI script for generating asset daily signals from news sentiment and price data.

Usage:
    python generate_signals.py --help
    python generate_signals.py --all --date 2024-01-15
    python generate_signals.py --symbols AAPL,TSLA --backfill --days 30
    python generate_signals.py --asset-ids 1,2,3 --force
"""

import argparse
import logging
from datetime import datetime, timedelta, date
from typing import List, Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from app.services.signal_generator import SignalGenerator
from models.assets import Asset
from models.asset_daily_signals import AssetDailySignals


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


def parse_ids(ids_str: str) -> List[int]:
    """Parse comma-separated IDs string."""
    if not ids_str:
        return []
    try:
        return [int(id_str.strip()) for id_str in ids_str.split(',') if id_str.strip()]
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid ID format: {e}")


def parse_symbols(symbols_str: str) -> List[str]:
    """Parse comma-separated symbols string."""
    if not symbols_str:
        return []
    return [s.strip().upper() for s in symbols_str.split(',') if s.strip()]


def generate_signals_for_date(
    asset_ids: List[int], 
    target_date: date, 
    force: bool = False
):
    """Generate signals for specific assets and date."""
    db = next(get_db())
    generator = SignalGenerator()
    
    try:
        logging.info(f"Generating signals for {len(asset_ids)} assets on {target_date}")
        
        # Check if signals already exist (unless force is True)
        if not force:
            existing_count = db.query(AssetDailySignals).filter(
                AssetDailySignals.asset_id.in_(asset_ids),
                AssetDailySignals.date == target_date
            ).count()
            
            if existing_count > 0:
                logging.warning(f"Found {existing_count} existing signals for {target_date}")
                if existing_count == len(asset_ids):
                    logging.info("All signals already exist. Use --force to regenerate.")
                    return
        
        # Generate signals
        success_count = 0
        error_count = 0
        
        for asset_id in asset_ids:
            try:
                logging.info(f"Generating signals for asset {asset_id}...")
                
                signals = generator.generate_signals_for_date(db, asset_id, target_date)
                
                if signals:
                    # Delete existing signals if force is True
                    if force:
                        db.query(AssetDailySignals).filter(
                            AssetDailySignals.asset_id == asset_id,
                            AssetDailySignals.date == target_date
                        ).delete()
                    
                    # Save new signals
                    db.add(signals)
                    db.commit()
                    
                    success_count += 1
                    logging.info(f"Generated signals for asset {asset_id}")
                else:
                    logging.warning(f"No signals generated for asset {asset_id}")
                    
            except Exception as e:
                logging.error(f"Error generating signals for asset {asset_id}: {e}")
                error_count += 1
                db.rollback()
                continue
        
        logging.info(f"Signal generation complete. Success: {success_count}, Errors: {error_count}")
        
    except Exception as e:
        logging.error(f"Signal generation failed: {e}")
        raise
    finally:
        db.close()


def backfill_signals(asset_ids: List[int], days: int, force: bool = False):
    """Backfill signals for multiple days."""
    db = next(get_db())
    generator = SignalGenerator()
    
    try:
        logging.info(f"Backfilling {days} days of signals for {len(asset_ids)} assets")
        
        # Generate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
        
        current_date = start_date
        total_generated = 0
        
        while current_date <= end_date:
            logging.info(f"Processing date: {current_date}")
            
            # Skip weekends (assuming markets closed)
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                logging.info(f"Skipping weekend: {current_date}")
                current_date += timedelta(days=1)
                continue
            
            # Check existing signals
            existing_asset_ids = set()
            if not force:
                existing_signals = db.query(AssetDailySignals.asset_id).filter(
                    AssetDailySignals.asset_id.in_(asset_ids),
                    AssetDailySignals.date == current_date
                ).all()
                existing_asset_ids = {row[0] for row in existing_signals}
            
            # Generate signals for assets without existing signals
            assets_to_process = [aid for aid in asset_ids if aid not in existing_asset_ids]
            
            if not assets_to_process:
                logging.info(f"All signals exist for {current_date}")
                current_date += timedelta(days=1)
                continue
            
            # Process each asset
            daily_success = 0
            
            for asset_id in assets_to_process:
                try:
                    signals = generator.generate_signals_for_date(db, asset_id, current_date)
                    
                    if signals:
                        db.add(signals)
                        daily_success += 1
                    
                except Exception as e:
                    logging.error(f"Error generating signals for asset {asset_id} on {current_date}: {e}")
                    continue
            
            # Commit daily batch
            try:
                db.commit()
                total_generated += daily_success
                logging.info(f"Generated {daily_success} signals for {current_date}")
            except Exception as e:
                logging.error(f"Failed to commit signals for {current_date}: {e}")
                db.rollback()
            
            current_date += timedelta(days=1)
        
        logging.info(f"Backfill complete. Total signals generated: {total_generated}")
        
    except Exception as e:
        logging.error(f"Backfill failed: {e}")
        raise
    finally:
        db.close()


def get_all_asset_ids() -> List[int]:
    """Get all active asset IDs from database."""
    db = next(get_db())
    
    try:
        assets = db.query(Asset.id).filter(Asset.is_active == True).all()
        return [asset[0] for asset in assets]
    finally:
        db.close()


def get_asset_ids_by_symbols(symbols: List[str]) -> List[int]:
    """Get asset IDs for given symbols."""
    db = next(get_db())
    
    try:
        assets = db.query(Asset.id).filter(
            Asset.symbol.in_(symbols)
        ).all()
        
        found_symbols = db.query(Asset.symbol).filter(
            Asset.symbol.in_(symbols)
        ).all()
        found_symbols = [row[0] for row in found_symbols]
        
        missing_symbols = set(symbols) - set(found_symbols)
        if missing_symbols:
            logging.warning(f"Symbols not found: {missing_symbols}")
        
        return [asset[0] for asset in assets]
    finally:
        db.close()


def get_signal_stats(days: int = 7):
    """Get and display signal generation statistics."""
    db = next(get_db())
    
    try:
        # Recent signals
        cutoff_date = date.today() - timedelta(days=days)
        
        recent_signals = db.query(AssetDailySignals).filter(
            AssetDailySignals.date >= cutoff_date
        ).count()
        
        # Unique assets with recent signals
        unique_assets = db.query(AssetDailySignals.asset_id).filter(
            AssetDailySignals.date >= cutoff_date
        ).distinct().count()
        
        # Total signals
        total_signals = db.query(AssetDailySignals).count()
        
        # Latest signal date
        latest_signal = db.query(AssetDailySignals.date).order_by(
            AssetDailySignals.date.desc()
        ).first()
        
        # Assets without recent signals
        total_assets = db.query(Asset).filter(Asset.is_active == True).count()
        
        print("\n=== Signal Generation Statistics ===")
        print(f"Total signals: {total_signals}")
        print(f"Recent signals ({days} days): {recent_signals}")
        print(f"Assets with recent signals: {unique_assets}/{total_assets}")
        print(f"Latest signal date: {latest_signal[0] if latest_signal else 'None'}")
        
        # Coverage by date
        if recent_signals > 0:
            print("\nDaily coverage (last 7 days):")
            coverage_query = db.query(
                AssetDailySignals.date,
                db.func.count(AssetDailySignals.asset_id).label('count')
            ).filter(
                AssetDailySignals.date >= cutoff_date
            ).group_by(
                AssetDailySignals.date
            ).order_by(
                AssetDailySignals.date.desc()
            ).limit(7)
            
            for row in coverage_query:
                print(f"  {row[0]}: {row[1]} assets")
        
        print()
        
    except Exception as e:
        logging.error(f"Failed to get statistics: {e}")
    finally:
        db.close()


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Generate asset daily signals from news and price data"
    )
    
    # Asset selection
    asset_group = parser.add_mutually_exclusive_group(required=True)
    asset_group.add_argument(
        '--all',
        action='store_true',
        help='Generate signals for all active assets'
    )
    asset_group.add_argument(
        '--symbols',
        type=str,
        help='Comma-separated list of symbols'
    )
    asset_group.add_argument(
        '--asset-ids',
        type=str,
        help='Comma-separated list of asset IDs'
    )
    asset_group.add_argument(
        '--stats',
        action='store_true',
        help='Show signal generation statistics'
    )
    
    # Date selection
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        '--date',
        type=parse_date,
        default=date.today(),
        help='Specific date to generate signals for (YYYY-MM-DD, default: today)'
    )
    date_group.add_argument(
        '--backfill',
        action='store_true',
        help='Backfill signals for multiple days'
    )
    
    # Backfill parameters
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days for backfill (default: 30)'
    )
    
    # Options
    parser.add_argument(
        '--force',
        action='store_true',
        help='Regenerate existing signals'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Validate arguments
    if args.days <= 0:
        parser.error("Days must be positive")
    if args.backfill and args.date != date.today():
        parser.error("Cannot use --date with --backfill")
    
    try:
        # Handle stats mode
        if args.stats:
            get_signal_stats()
            return 0
        
        # Get asset IDs based on selection
        if args.all:
            asset_ids = get_all_asset_ids()
            logging.info(f"Found {len(asset_ids)} active assets")
        elif args.symbols:
            symbols = parse_symbols(args.symbols)
            asset_ids = get_asset_ids_by_symbols(symbols)
            logging.info(f"Found {len(asset_ids)} assets for symbols: {symbols}")
        else:  # asset_ids
            asset_ids = parse_ids(args.asset_ids)
            logging.info(f"Using {len(asset_ids)} specified asset IDs")
        
        if not asset_ids:
            logging.error("No assets to process")
            return 1
        
        # Generate signals based on mode
        if args.backfill:
            backfill_signals(
                asset_ids=asset_ids,
                days=args.days,
                force=args.force
            )
        else:
            generate_signals_for_date(
                asset_ids=asset_ids,
                target_date=args.date,
                force=args.force
            )
            
        logging.info("Signal generation completed successfully")
        
    except KeyboardInterrupt:
        logging.info("Generation interrupted by user")
    except Exception as e:
        logging.error(f"Generation failed: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())