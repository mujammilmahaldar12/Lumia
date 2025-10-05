"""Quick script to check database status"""
from database import get_db
from models.assets import Asset
from models.daily_price import DailyPrice

db = next(get_db())

# Check assets
asset_count = db.query(Asset).count()
print(f"✓ Total assets: {asset_count}")

if asset_count > 0:
    assets = db.query(Asset).limit(10).all()
    print("\nSample assets:")
    for a in assets:
        print(f"  - {a.symbol:10} | {a.name:30} | {a.asset_type:12}")

# Check prices
price_count = db.query(DailyPrice).count()
print(f"\n✓ Total price records: {price_count}")

if price_count > 0:
    sample = db.query(DailyPrice).limit(3).all()
    print("\nSample price records:")
    for p in sample:
        print(f"  - Asset ID {p.asset_id} | {p.date} | ${p.close_price:.2f}")

db.close()
print("\n✓ Database check complete!")
