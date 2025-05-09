"""
Database operations for QuickBooks sales forecasting.

This module provides functions for interacting with the database,
including storing and retrieving historical sales data.
"""

import pandas as pd
import os
from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, text
from sqlalchemy.orm import relationship

# Import database configuration
from src.db_config import DB_PARAMS, ENGINE, Base, get_db_session

def get_db_connection():
    try:
        # Create connection using SQLAlchemy
        conn = ENGINE.connect()
        print(f"Successfully connected to PostgreSQL database: {DB_PARAMS['connection_string']}")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

# Define SQLAlchemy models
class HistoricalSales(Base):
    """SQLAlchemy model for historical_sales table."""
    __tablename__ = "historical_sales"

    date = Column(Date, primary_key=True)
    total_sales = Column(Float)
    Beauty = Column(Float)
    Books = Column(Float)
    Clothing = Column(Float)
    Electronics = Column(Float)
    Furniture = Column(Float)
    Groceries = Column(Float)
    Sports = Column(Float)
    Toys = Column(Float)
    year = Column(Integer)
    month = Column(Integer)
    day_of_week = Column(Integer)
    is_weekend = Column(Integer)
    week_of_year = Column(Integer)
    quarter = Column(Integer)
    is_month_end = Column(Integer)
    is_month_start = Column(Integer)
    is_november = Column(Integer)
    Beauty_lag_1 = Column(Float)
    Books_lag_1 = Column(Float)
    Clothing_lag_1 = Column(Float)
    Electronics_lag_1 = Column(Float)
    Furniture_lag_1 = Column(Float)
    Groceries_lag_1 = Column(Float)
    Sports_lag_1 = Column(Float)
    Toys_lag_1 = Column(Float)
    Beauty_lag_7 = Column(Float)
    Books_lag_7 = Column(Float)
    Clothing_lag_7 = Column(Float)
    Electronics_lag_7 = Column(Float)
    Furniture_lag_7 = Column(Float)
    Groceries_lag_7 = Column(Float)
    Sports_lag_7 = Column(Float)
    Toys_lag_7 = Column(Float)
    Beauty_lag_14 = Column(Float)
    Books_lag_14 = Column(Float)
    Clothing_lag_14 = Column(Float)
    Electronics_lag_14 = Column(Float)
    Furniture_lag_14 = Column(Float)
    Groceries_lag_14 = Column(Float)
    Sports_lag_14 = Column(Float)
    Toys_lag_14 = Column(Float)

class Predictions(Base):
    """SQLAlchemy model for predictions table."""
    __tablename__ = "predictions"

    date = Column(Date, primary_key=True)
    total_sales = Column(Float)
    Beauty = Column(Float)
    Books = Column(Float)
    Clothing = Column(Float)
    Electronics = Column(Float)
    Furniture = Column(Float)
    Groceries = Column(Float)
    Sports = Column(Float)
    Toys = Column(Float)
    year = Column(Integer)
    month = Column(Integer)
    day_of_week = Column(Integer)
    is_weekend = Column(Integer)
    week_of_year = Column(Integer)
    quarter = Column(Integer)
    is_month_end = Column(Integer)
    is_month_start = Column(Integer)
    is_november = Column(Integer)
    Beauty_lag_1 = Column(Float)
    Books_lag_1 = Column(Float)
    Clothing_lag_1 = Column(Float)
    Electronics_lag_1 = Column(Float)
    Furniture_lag_1 = Column(Float)
    Groceries_lag_1 = Column(Float)
    Sports_lag_1 = Column(Float)
    Toys_lag_1 = Column(Float)
    Beauty_lag_7 = Column(Float)
    Books_lag_7 = Column(Float)
    Clothing_lag_7 = Column(Float)
    Electronics_lag_7 = Column(Float)
    Furniture_lag_7 = Column(Float)
    Groceries_lag_7 = Column(Float)
    Sports_lag_7 = Column(Float)
    Toys_lag_7 = Column(Float)
    Beauty_lag_14 = Column(Float)
    Books_lag_14 = Column(Float)
    Clothing_lag_14 = Column(Float)
    Electronics_lag_14 = Column(Float)
    Furniture_lag_14 = Column(Float)
    Groceries_lag_14 = Column(Float)
    Sports_lag_14 = Column(Float)
    Toys_lag_14 = Column(Float)

class Category(Base):
    """SQLAlchemy model for category table."""
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(String, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(String, server_default=text("CURRENT_TIMESTAMP"))

    # Relationship with Product
    products = relationship("Product", back_populates="category")

class Product(Base):
    """SQLAlchemy model for product table."""
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    created_at = Column(String, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(String, server_default=text("CURRENT_TIMESTAMP"))

    # Relationship with Category
    category = relationship("Category", back_populates="products")


def create_tables(conn=None, force=False):
    """
    Create database tables if they don't exist.
    If force is True, drop existing tables and recreate them.

    Args:
        conn (SQLAlchemy connection, optional): Database connection. If None, a new connection will be created.
        force (bool, optional): If True, drop existing tables and recreate them.
    """
    try:
        # Create connection if not provided
        connection_created = False
        if conn is None:
            conn = get_db_connection()
            connection_created = True

        # Drop tables if force is True
        if force:
            print("Dropping existing tables")
            Base.metadata.drop_all(bind=ENGINE, tables=[
                HistoricalSales.__table__,
                Predictions.__table__
            ])
            print("Tables dropped successfully")

        # Create tables
        print("Creating tables")
        Base.metadata.create_all(bind=ENGINE)
        print("Database tables created successfully")

        # Close connection if we created it
        if connection_created:
            conn.close()

    except Exception as e:
        print(f"Error creating database tables: {e}")
        if 'conn' in locals() and conn and connection_created:
            conn.close()
        raise

def store_historical_sales(csv_path, conn=None, force=False):
    """
    Store historical sales data from a CSV file in the database.

    Args:
        csv_path (str): Path to the CSV file containing historical sales data
        conn (SQLAlchemy connection, optional): Database connection. If None, a new connection will be created.
        force (bool, optional): If True, existing data will be overwritten without prompting.

    Returns:
        int: Number of rows inserted
    """
    try:
        # Create connection if not provided
        connection_created = False
        if conn is None:
            conn = get_db_connection()
            connection_created = True

        # Create tables if they don't exist
        create_tables(conn, force=force)

        # Read CSV file
        print(f"Reading historical sales data from {csv_path}")
        df = pd.read_csv(csv_path, parse_dates=['date'])

        # Remove columns that don't exist in the table
        columns_to_remove = ['avg_transaction', 'transaction_count', 'unique_categories']
        for col in columns_to_remove:
            if col in df.columns:
                df = df.drop(columns=[col])
                print(f"Removed column {col} from DataFrame")

        # Ensure date column is in datetime format for PostgreSQL Date type
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])

        # Create a session
        session = get_db_session()

        # Check if data already exists in the database
        existing_count = session.query(HistoricalSales).count()

        if existing_count > 0:
            print(f"Database already contains {existing_count} rows of data")

            # If force is False, prompt the user
            if not force:
                user_input = input("Do you want to delete existing data and insert new data? (y/n): ")
                if user_input.lower() != 'y':
                    print("Operation cancelled by user")
                    session.close()
                    if connection_created:
                        conn.close()
                    return 0

            # Delete existing data
            session.query(HistoricalSales).delete()
            session.commit()
            print("Existing data deleted")

        # Insert data into database
        print(f"Inserting {len(df)} rows into database")

        # Convert DataFrame to list of dictionaries
        records = df.to_dict('records')

        # Create HistoricalSales objects and add them to the session
        for record in records:
            historical_sales = HistoricalSales(**record)
            session.add(historical_sales)

        # Commit the session
        session.commit()

        # Verify insertion
        inserted_count = session.query(HistoricalSales).count()

        # Close session
        session.close()

        # Close connection if we created it
        if connection_created:
            conn.close()

        print(f"Successfully inserted {inserted_count} rows into database")
        return inserted_count

    except Exception as e:
        print(f"Error storing historical sales data: {e}")
        if 'session' in locals() and session:
            session.rollback()
            session.close()
        if 'conn' in locals() and conn and connection_created:
            conn.close()
        raise

def get_historical_sales(start_date=None, end_date=None, conn=None):
    """
    Retrieve historical sales data from the database.

    Args:
        start_date (str or datetime, optional): Start date for filtering
        end_date (str or datetime, optional): End date for filtering
        conn (SQLAlchemy connection, optional): Database connection. If None, a new connection will be created.

    Returns:
        DataFrame: Historical sales data
    """
    try:
        # Create connection if not provided
        connection_created = False
        if conn is None:
            conn = get_db_connection()
            connection_created = True

        # Create a session
        session = get_db_session()

        # Build query
        query = session.query(HistoricalSales)

        # Add date filters if provided
        if start_date or end_date:
            if start_date:
                # Convert string to datetime if needed
                if isinstance(start_date, str):
                    start_date = pd.to_datetime(start_date).date()
                elif hasattr(start_date, 'date'):
                    start_date = start_date.date()
                query = query.filter(HistoricalSales.date >= start_date)
            if end_date:
                # Convert string to datetime if needed
                if isinstance(end_date, str):
                    end_date = pd.to_datetime(end_date).date()
                elif hasattr(end_date, 'date'):
                    end_date = end_date.date()
                query = query.filter(HistoricalSales.date <= end_date)

        # Order by date
        query = query.order_by(HistoricalSales.date)

        # Execute query
        print(f"Retrieving historical sales data from database")
        results = query.all()

        # Convert results to DataFrame
        data = []
        for result in results:
            # Convert SQLAlchemy object to dictionary
            row = {column.name: getattr(result, column.name) for column in result.__table__.columns}
            data.append(row)

        # Create DataFrame from results
        df = pd.DataFrame(data)

        # Convert date to datetime and set as index
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df.set_index('date', inplace=True)

        # Close session
        session.close()

        # Close connection if we created it
        if connection_created:
            conn.close()

        print(f"Retrieved {len(df)} rows from database")
        print(f"Columns in historical_sales table: {df.columns.tolist()}")
        return df

    except Exception as e:
        print(f"Error retrieving historical sales data: {e}")
        if 'session' in locals() and session:
            session.close()
        if 'conn' in locals() and conn and connection_created:
            conn.close()
        raise

def populate_categories_and_products(sales_csv_path, conn=None, force=False):
    """
    Extract distinct categories and products from sales data and populate the database tables.

    Args:
        sales_csv_path (str): Path to the CSV file containing sales data
        conn (SQLAlchemy connection, optional): Database connection. If None, a new connection will be created.
        force (bool, optional): If True, drop existing tables and recreate them.

    Returns:
        tuple: (Number of categories inserted, Number of products inserted)
    """
    try:
        # Create connection if not provided
        connection_created = False
        if conn is None:
            conn = get_db_connection()
            connection_created = True

        # Create tables if they don't exist
        create_tables(conn, force=force)

        # Read CSV file
        print(f"Reading sales data from {sales_csv_path}")
        df = pd.read_csv(sales_csv_path, parse_dates=['date'])

        # Extract distinct categories
        categories = df['category'].unique().tolist()
        print(f"Found {len(categories)} distinct categories")

        # Create a session
        session = get_db_session()

        # Insert categories into database
        categories_inserted = 0

        for category_name in categories:
            try:
                # Check if category already exists
                existing_category = session.query(Category).filter_by(name=category_name).first()

                if existing_category is None:
                    # Category doesn't exist, insert it
                    new_category = Category(name=category_name)
                    session.add(new_category)
                    categories_inserted += 1
            except Exception as e:
                print(f"Error inserting category {category_name}: {e}")

        # Commit to get IDs for new categories
        session.commit()
        print(f"Inserted {categories_inserted} categories into database")

        # Get category IDs
        category_map = {}
        for category_obj in session.query(Category).all():
            category_map[category_obj.name] = category_obj.id

        # Extract distinct products per category
        products_df = df[['category', 'product']].drop_duplicates()
        print(f"Found {len(products_df)} distinct products")

        # Insert products into database
        products_inserted = 0

        for _, row in products_df.iterrows():
            category_name = row['category']
            product_name = row['product']
            category_id = category_map.get(category_name)

            if category_id:
                try:
                    # Check if product already exists
                    existing_product = session.query(Product).filter_by(
                        name=product_name, 
                        category_id=category_id
                    ).first()

                    if existing_product is None:
                        # Product doesn't exist, insert it
                        new_product = Product(
                            name=product_name,
                            category_id=category_id
                        )
                        session.add(new_product)
                        products_inserted += 1
                except Exception as e:
                    print(f"Error inserting product {product_name} for category {category_name}: {e}")
            else:
                print(f"Category ID not found for category: {category_name}")

        # Commit changes
        session.commit()
        print(f"Inserted {products_inserted} products into database")

        # Close session
        session.close()

        # Close connection if we created it
        if connection_created:
            conn.close()

        return (categories_inserted, products_inserted)

    except Exception as e:
        print(f"Error populating categories and products: {e}")
        if 'session' in locals() and session:
            session.rollback()
            session.close()
        if 'conn' in locals() and conn and connection_created:
            conn.close()
        raise

def get_categories(conn=None):
    """
    Retrieve all categories from the database.

    Args:
        conn (SQLAlchemy connection, optional): Database connection. If None, a new connection will be created.

    Returns:
        DataFrame: Categories data
    """
    try:
        # Create connection if not provided
        connection_created = False
        if conn is None:
            conn = get_db_connection()
            connection_created = True

        # Create a session
        session = get_db_session()

        # Execute query
        print("Retrieving categories from database")
        categories = session.query(Category).order_by(Category.name).all()

        # Convert results to DataFrame
        data = []
        for category in categories:
            # Convert SQLAlchemy object to dictionary
            row = {column.name: getattr(category, column.name) for column in category.__table__.columns}
            data.append(row)

        # Create DataFrame from results
        df = pd.DataFrame(data)

        # Close session
        session.close()

        # Close connection if we created it
        if connection_created:
            conn.close()

        print(f"Retrieved {len(df)} categories from database")
        return df

    except Exception as e:
        print(f"Error retrieving categories: {e}")
        if 'session' in locals() and session:
            session.close()
        if 'conn' in locals() and conn and connection_created:
            conn.close()
        raise

def store_predictions(df, conn=None, force=False):
    """
    Store prediction data in the predictions table.

    Args:
        df (DataFrame): DataFrame containing prediction data
        conn (SQLAlchemy connection, optional): Database connection. If None, a new connection will be created.
        force (bool, optional): If True, existing data will be overwritten without prompting.

    Returns:
        int: Number of rows inserted
    """
    try:
        # Create connection if not provided
        connection_created = False
        if conn is None:
            conn = get_db_connection()
            connection_created = True

        # Create tables if they don't exist
        create_tables(conn, force=force)

        # Create a session
        session = get_db_session()

        # Check if data already exists in the database
        existing_count = session.query(Predictions).count()

        if existing_count > 0:
            print(f"Predictions table already contains {existing_count} rows of data")

            # If force is False, prompt the user
            if not force:
                user_input = input("Do you want to delete existing prediction data and insert new data? (y/n): ")
                if user_input.lower() != 'y':
                    print("Operation cancelled by user")
                    session.close()
                    if connection_created:
                        conn.close()
                    return 0

            # Delete existing data
            session.query(Predictions).delete()
            session.commit()
            print("Existing prediction data deleted")

        # Ensure date column is in datetime format for PostgreSQL Date type
        if 'date' in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df['date']):
                df['date'] = pd.to_datetime(df['date'])

        # Remove columns that don't exist in the table
        columns_to_remove = ['avg_transaction', 'transaction_count', 'unique_categories']
        for col in columns_to_remove:
            if col in df.columns:
                df = df.drop(columns=[col])
                print(f"Removed column {col} from DataFrame")

        # Check for duplicate dates
        duplicate_dates = df['date'].duplicated()
        if duplicate_dates.any():
            print(f"Found {duplicate_dates.sum()} duplicate dates in predictions DataFrame")
            print(f"Example duplicate date: {df.loc[duplicate_dates, 'date'].iloc[0]}")
            print("Dropping duplicate dates from predictions DataFrame")
            df = df.drop_duplicates(subset=['date'])

        # Insert data into database
        print(f"Inserting {len(df)} rows into predictions table")

        # Convert DataFrame to list of dictionaries
        records = df.to_dict('records')

        # Create Predictions objects and add them to the session
        for record in records:
            prediction = Predictions(**record)
            session.add(prediction)

        # Commit the session
        session.commit()

        # Verify insertion
        inserted_count = session.query(Predictions).count()

        # Close session
        session.close()

        # Close connection if we created it
        if connection_created:
            conn.close()

        print(f"Successfully inserted {inserted_count} rows into predictions table")
        return inserted_count

    except Exception as e:
        print(f"Error storing prediction data: {e}")
        if 'session' in locals() and session:
            session.rollback()
            session.close()
        if 'conn' in locals() and conn and connection_created:
            conn.close()
        raise

def get_predictions(start_date=None, end_date=None, conn=None):
    """
    Retrieve prediction data from the database.

    Args:
        start_date (str or datetime, optional): Start date for filtering
        end_date (str or datetime, optional): End date for filtering
        conn (SQLAlchemy connection, optional): Database connection. If None, a new connection will be created.

    Returns:
        DataFrame: Prediction data
    """
    try:
        # Create connection if not provided
        connection_created = False
        if conn is None:
            conn = get_db_connection()
            connection_created = True

        # Create a session
        session = get_db_session()

        # Build query
        query = session.query(Predictions)

        # Add date filters if provided
        if start_date or end_date:
            if start_date:
                # Convert string to datetime if needed
                if isinstance(start_date, str):
                    start_date = pd.to_datetime(start_date).date()
                elif hasattr(start_date, 'date'):
                    start_date = start_date.date()
                query = query.filter(Predictions.date >= start_date)
            if end_date:
                # Convert string to datetime if needed
                if isinstance(end_date, str):
                    end_date = pd.to_datetime(end_date).date()
                elif hasattr(end_date, 'date'):
                    end_date = end_date.date()
                query = query.filter(Predictions.date <= end_date)

        # Order by date
        query = query.order_by(Predictions.date)

        # Execute query
        print(f"Retrieving prediction data from database")
        results = query.all()

        # Convert results to DataFrame
        data = []
        for result in results:
            # Convert SQLAlchemy object to dictionary
            row = {column.name: getattr(result, column.name) for column in result.__table__.columns}
            data.append(row)

        # Create DataFrame from results
        df = pd.DataFrame(data)

        # Convert date to datetime
        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df.set_index('date', inplace=True)

        # Close session
        session.close()

        # Close connection if we created it
        if connection_created:
            conn.close()

        print(f"Retrieved {len(df)} rows from predictions table")
        if not df.empty:
            print(f"Date range: {df['date'].min()} to {df['date'].max()}")
            print(f"Columns in predictions table: {df.columns.tolist()}")
        return df

    except Exception as e:
        print(f"Error retrieving prediction data: {e}")
        if 'session' in locals() and session:
            session.close()
        if 'conn' in locals() and conn and connection_created:
            conn.close()
        raise

def get_products(category_id=None, conn=None):
    """
    Retrieve products from the database, optionally filtered by category.

    Args:
        category_id (int, optional): Category ID to filter by
        conn (SQLAlchemy connection, optional): Database connection. If None, a new connection will be created.

    Returns:
        DataFrame: Products data
    """
    try:
        # Create connection if not provided
        connection_created = False
        if conn is None:
            conn = get_db_connection()
            connection_created = True

        # Create a session
        session = get_db_session()

        # Build query
        query = session.query(Product, Category.name.label('category_name')).\
            join(Category, Product.category_id == Category.id)

        # Add category filter if provided
        if category_id:
            query = query.filter(Product.category_id == category_id)

        # Order by category name and product name
        query = query.order_by(Category.name, Product.name)

        # Execute query
        print(f"Retrieving products from database")
        results = query.all()

        # Convert results to DataFrame
        data = []
        for product, category_name in results:
            # Convert SQLAlchemy object to dictionary
            row = {column.name: getattr(product, column.name) for column in product.__table__.columns}
            row['category_name'] = category_name
            data.append(row)

        # Create DataFrame from results
        df = pd.DataFrame(data)

        # Close session
        session.close()

        # Close connection if we created it
        if connection_created:
            conn.close()

        print(f"Retrieved {len(df)} products from database")
        return df

    except Exception as e:
        print(f"Error retrieving products: {e}")
        if 'session' in locals() and session:
            session.close()
        if 'conn' in locals() and conn and connection_created:
            conn.close()
        raise

if __name__ == "__main__":
    # Example usage
    try:
        # Store historical sales data in database
        csv_path = "data/processed/sales_engineered_features.csv"
        rows_inserted = store_historical_sales(csv_path)
        print(f"Inserted {rows_inserted} rows into historical_sales table")

        # Populate categories and products from raw sales data
        raw_sales_path = "data/raw/sales.csv"
        if os.path.exists(raw_sales_path):
            categories_inserted, products_inserted = populate_categories_and_products(raw_sales_path)
            print(f"Inserted {categories_inserted} categories and {products_inserted} products into database")

            # Retrieve categories and products
            categories_df = get_categories()
            print(f"Categories in database:")
            print(categories_df)

            products_df = get_products()
            print(f"Products in database:")
            print(products_df.head())
        else:
            print(f"Raw sales data file not found: {raw_sales_path}")

        # Retrieve historical sales data from database
        sales_df = get_historical_sales()
        print(f"Retrieved {len(sales_df)} rows from historical_sales table")
        print(sales_df.head())

        # Example of storing and retrieving predictions
        # For demonstration, we'll use the historical sales data as predictions
        if not sales_df.empty:
            # Create a copy of the sales data for predictions (for future dates)
            predictions_df = sales_df.copy()
            # Shift dates forward by 1 year to simulate future predictions
            predictions_df['date'] = predictions_df['date'] + pd.DateOffset(years=1)

            # Store predictions in database
            pred_rows_inserted = store_predictions(predictions_df, force=True)
            print(f"Inserted {pred_rows_inserted} rows into predictions table")

            # Retrieve predictions from database
            pred_df = get_predictions()
            print(f"Retrieved {len(pred_df)} rows from predictions table")
            print(pred_df.head())

    except Exception as e:
        print(f"Error: {e}")
