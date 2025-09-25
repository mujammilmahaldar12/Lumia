# Lumia - Stock Market Data Management System

A Python application for managing stock market data using SQLAlchemy and Alembic for database migrations.

## 📁 Project Structure

```
Lumia/
├── alembic/                    # Database migration files
│   ├── versions/               # Migration version files
│   ├── env.py                 # Alembic environment configuration
│   └── ...
├── models/                     # SQLAlchemy model definitions
│   ├── __init__.py
│   ├── company.py             # Company model
│   ├── user.py                # User model
│   ├── daily_price.py         # Daily price data model
│   └── quarterly_fundamental.py # Quarterly fundamentals model
├── alembic.ini               # Alembic configuration
├── database.py               # Database connection and Base
├── config.py                 # Application configuration
├── check_metadata.py         # Utility to verify model metadata
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🚀 Setup Instructions

### 1. Environment Setup

```bash
# Navigate to the app directory
cd "C:\Users\mujammil maldar\Desktop\New folder (4)\app"

# Activate the virtual environment
.\env\Scripts\Activate.ps1

# Navigate to the Lumia project
cd Lumia
```

### 2. Database Configuration

Make sure PostgreSQL is running and update the database URL in `database.py`:
```python
DATABASE_URL = "postgresql+psycopg2://postgres:root@localhost/lumia"
```

## 📊 Database Models

The project includes the following models:

- **Company**: Stock company information (symbol, name, sector, market cap, etc.)
- **User**: User management
- **DailyPrice**: Daily stock price data
- **QuarterlyFundamental**: Quarterly financial fundamentals

## 🔧 Database Migrations with Alembic

### Initial Setup (One-time only)

If starting fresh, Alembic is already initialized. The configuration is in `alembic.ini` and the environment setup is in `alembic/env.py`.

### Creating Migrations

#### 1. Check Your Models
Before creating migrations, verify all models are properly loaded:

```bash
python check_metadata.py
```

**Expected output:**
```
--- Starting metadata check ---

SUCCESS: Found the following tables in metadata:
- companies
- daily_prices
- quarterly_fundamentals
- users

--- Metadata check finished ---
```

#### 2. Generate Migration Files

When you add/modify models, create a new migration:

```bash
# Generate migration automatically based on model changes
alembic revision --autogenerate -m "Description of changes"

# Example:
alembic revision --autogenerate -m "Add new column to company model"
alembic revision --autogenerate -m "Create initial tables"
```

#### 3. Review Generated Migration

Always review the generated migration file in `alembic/versions/` before applying:

```python
# Example migration file: alembic/versions/xxxxx_create_initial_tables.py
def upgrade() -> None:
    # Operations to apply the migration
    op.create_table('companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=10), nullable=False),
        # ... more columns
    )

def downgrade() -> None:
    # Operations to reverse the migration
    op.drop_table('companies')
```

### Applying Migrations

#### Apply All Pending Migrations
```bash
alembic upgrade head
```

#### Apply Specific Migration
```bash
alembic upgrade <revision_id>
```

#### Rollback Migrations
```bash
# Rollback to previous migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

### Migration Management Commands

#### Check Current Migration Status
```bash
alembic current
```

#### View Migration History
```bash
alembic history
alembic history --verbose
```

#### Show SQL Without Executing
```bash
alembic upgrade head --sql
alembic downgrade -1 --sql
```

## 🔄 Complete Workflow Example

### First Time Setup
```bash
# 1. Activate environment
.\env\Scripts\Activate.ps1
cd Lumia

# 2. Check models are loaded
python check_metadata.py

# 3. Create initial migration
alembic revision --autogenerate -m "Initial migration"

# 4. Apply migration to database
alembic upgrade head
```

### Adding New Model/Column
```bash
# 1. Modify your model files (e.g., add new column to Company)
# 2. Check metadata
python check_metadata.py

# 3. Generate migration
alembic revision --autogenerate -m "Add business_summary to companies"

# 4. Review the generated file in alembic/versions/
# 5. Apply migration
alembic upgrade head
```

### Rollback Changes
```bash
# Check current status
alembic current

# Rollback last migration
alembic downgrade -1

# Or rollback to specific version
alembic downgrade abc123ef456
```

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the Lumia directory and the virtual environment is activated
2. **No tables found**: Run `python check_metadata.py` to verify models are loading correctly
3. **Migration conflicts**: Check `alembic history` and resolve any branching issues

### Useful Commands

```bash
# Verify database connection
python -c "from database import engine; print(engine.execute('SELECT 1').scalar())"

# Check what tables exist in database
python -c "from database import engine; print(engine.table_names())"
```

## 📝 Notes

- Always run `python check_metadata.py` before creating migrations
- Review generated migration files before applying them
- Keep migration messages descriptive and meaningful
- Test migrations on a copy of production data before applying to production
- Regular backups are recommended before applying migrations

## 🔗 Dependencies

See `requirements.txt` for full list of dependencies:
- SQLAlchemy: ORM and database toolkit
- Alembic: Database migration tool
- psycopg2: PostgreSQL adapter
- And more...

---

**Happy coding! 🚀**
