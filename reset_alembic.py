from database import engine
from sqlalchemy import text

print("Resetting Alembic version table...")

try:
    with engine.connect() as conn:
        # Delete the old revision
        conn.execute(text("DELETE FROM alembic_version"))
        conn.commit()
        print("✅ Cleared alembic_version table")
except Exception as e:
    print(f"Error: {e}")
