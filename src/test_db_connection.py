"""
Test script to verify database connection.

This script tests the database connection using the configuration from db_config.py.
"""

import sys
from pathlib import Path

# Add the project root directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import the database operations module
from src.db_operations import get_db_connection

def main():
    """
    Test database connection.
    """
    try:
        # Get database connection
        print("Testing database connection...")
        conn = get_db_connection()

        # Test connection using SQLAlchemy
        from sqlalchemy import text
        result = conn.execute(text("SELECT 1")).scalar()

        if result == 1:
            print("Database connection successful!")

        # Close connection
        conn.close()
        print("Connection closed.")

        return 0

    except Exception as e:
        print(f"Error connecting to database: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
