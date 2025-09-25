# check_metadata.py
import sys
import os

# Add the current working directory (Lumia/) to the Python path
# This is the key to solving the import errors
sys.path.append(os.getcwd())

print("--- Starting metadata check ---")

try:
    # Import the Base object that your models inherit from
    from database import Base

    # Import every one of your model classes
    from models.user import User
    from models.company import Company
    from models.daily_price import DailyPrice
    from models.quarterly_fundamental import QuarterlyFundamental

    # Check which tables have been registered with the Base metadata
    registered_tables = Base.metadata.tables.keys()

    if not registered_tables:
        print("\nERROR: No tables were found in Base.metadata!")
        print("This is the root of the problem. Check that your models correctly inherit from the Base object defined in 'models/base.py'.")
    else:
        print("\nSUCCESS: Found the following tables in metadata:")
        for table in sorted(list(registered_tables)): # Sorted for consistent order
            print(f"- {table}")

except ImportError as e:
    print(f"\nIMPORT ERROR: {e}")
    print("Please check that all model files use 'from database import Base'")

print("\n--- Metadata check finished ---")# check_metadata.py
