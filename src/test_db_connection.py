"""
Test script to verify database connection.

This script tests the database connection using the configuration from db_config.py.
"""

import sys
import logging
from pathlib import Path

# Add the project root directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import the database operations module
from src.db_operations import get_db_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Test database connection.
    """
    try:
        # Get database connection
        logger.info("Testing database connection...")
        conn = get_db_connection()

        # Test connection using SQLAlchemy
        from sqlalchemy import text
        result = conn.execute(text("SELECT 1")).scalar()

        if result == 1:
            logger.info("Database connection successful!")

        # Close connection
        conn.close()
        logger.info("Connection closed.")

        return 0

    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
