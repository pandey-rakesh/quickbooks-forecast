"""
Script to store historical sales data in the database.

This script reads the sales_engineered_features.csv file and stores it in the database
as historical sales data. It also populates the category and product tables from the
raw sales data. It can be run directly from the command line.
"""

import argparse
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import the database operations module
from src.db_operations import (
    store_historical_sales, 
    get_historical_sales,
    populate_categories_and_products,
    get_categories,
    get_products
)

def main():
    """
    Main function to store historical sales data in the database and populate category and product tables.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Store historical sales data in the database and populate category and product tables.')
    parser.add_argument('--csv-path', type=str, default='data/processed/sales_engineered_features.csv',
                        help='Path to the CSV file containing historical sales data')
    parser.add_argument('--raw-sales-path', type=str, default='data/raw/sales.csv',
                        help='Path to the CSV file containing raw sales data')
    parser.add_argument('--force', action='store_true',
                        help='Force overwrite of existing data without prompting')
    parser.add_argument('--skip-categories', action='store_true',
                        help='Skip populating category and product tables')
    args = parser.parse_args()

    # Check if the historical sales CSV file exists
    if not os.path.exists(args.csv_path):
        print(f"Historical sales CSV file not found: {args.csv_path}")
        return 1

    try:
        # Store historical sales data in database
        print(f"Storing historical sales data from {args.csv_path} in database")
        rows_inserted = store_historical_sales(args.csv_path, force=args.force)

        if rows_inserted > 0:
            print(f"Successfully inserted {rows_inserted} rows into database")

            # Retrieve a sample of the data to verify
            sample_df = get_historical_sales()
            print(f"Sample of data in database (first 5 rows):")
            print(f"Shape: {sample_df.shape}")
            print(f"Columns: {sample_df.columns.tolist()[:5]}...")
            print(f"Date range: {sample_df.index.min()} to {sample_df.index.max()}")
        else:
            print("No rows were inserted into the historical_sales table")

        # Populate category and product tables if not skipped
        if not args.skip_categories:
            # Check if the raw sales CSV file exists
            if not os.path.exists(args.raw_sales_path):
                print(f"Raw sales CSV file not found: {args.raw_sales_path}")
                return 1

            print(f"Populating category and product tables from {args.raw_sales_path}")
            categories_inserted, products_inserted = populate_categories_and_products(args.raw_sales_path, force=args.force)

            if categories_inserted > 0 or products_inserted > 0:
                print(f"Successfully inserted {categories_inserted} categories and {products_inserted} products into database")

                # Retrieve categories and products to verify
                categories_df = get_categories()
                print(f"Categories in database: {len(categories_df)}")

                products_df = get_products()
                print(f"Products in database: {len(products_df)}")

                # Show sample of products
                if not products_df.empty:
                    print(f"Sample of products in database (first 5 rows):")
                    for _, row in products_df.head().iterrows():
                        print(f"  {row['category_name']}: {row['name']}")
            else:
                print("No categories or products were inserted into the database")

        return 0

    except Exception as e:
        print(f"Error storing data in database: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
