#!/usr/bin/env python3
"""
Quick Signal Generator - Creates mock signals to get the system working
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from models.assets import Asset
from models.asset_daily_signals import AssetDailySignals
from datetime import datetime, date, timedelta
import random

def create_mock_signals():
    """Create mock signals for Indian stocks to get the system working."""
    db = next(get_db())
    
    try:
        # Get Indian stocks that have some price data
        indian_assets = db.query(Asset).filter(
            Asset.symbol.like('%.NS'),
            Asset.is_active == True
        ).limit(20).all()
        
        if not indian_assets:
            print("No Indian assets found!")
            return
            
        print(f"Creating mock signals for {len(indian_assets)} Indian assets...")
        
        # Generate signals for the last 7 days
        for days_back in range(7):
            target_date = date.today() - timedelta(days=days_back)
            
            for asset in indian_assets:
                # Check if signal already exists
                existing = db.query(AssetDailySignals).filter(
                    AssetDailySignals.asset_id == asset.id,
                    AssetDailySignals.date == target_date
                ).first()
                
                if existing:
                    continue
                    
                # Create mock signal with random but reasonable values
                signal = AssetDailySignals(
                    asset_id=asset.id,
                    date=target_date,
                    avg_sentiment=round(random.uniform(-0.5, 0.5), 3),  # Sentiment between -0.5 and 0.5
                    article_count=random.randint(0, 10),
                    sentiment_7d_avg=round(random.uniform(-0.3, 0.3), 3),
                    sentiment_30d_avg=round(random.uniform(-0.2, 0.2), 3),
                    volatility_30d=round(random.uniform(0.15, 0.45), 3),  # 15% to 45% volatility
                    return_30d=round(random.uniform(-0.20, 0.20), 3),  # -20% to +20% return
                    return_365d=round(random.uniform(-0.50, 0.80), 3),  # -50% to +80% return
                    fundamental_score=round(random.uniform(0.3, 0.9), 2)  # 30% to 90% score
                )
                
                db.add(signal)
                
            print(f"Created signals for {target_date}")
        
        db.commit()
        
        # Show statistics
        total_signals = db.query(AssetDailySignals).count()
        recent_signals = db.query(AssetDailySignals).filter(
            AssetDailySignals.date >= date.today() - timedelta(days=7)
        ).count()
        
        print(f"✅ Mock signals created successfully!")
        print(f"📊 Total signals in database: {total_signals}")
        print(f"📊 Recent signals (last 7 days): {recent_signals}")
        print(f"🎯 Assets with recent signals: {len(indian_assets)}")
        
    except Exception as e:
        print(f"❌ Error creating mock signals: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_mock_signals()