from database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        versions = [row[0] for row in result]
        print(f"Current Alembic versions in database: {versions}")
except Exception as e:
    print(f"Error checking alembic_version table: {e}")