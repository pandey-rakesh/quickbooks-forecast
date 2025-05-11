"""
Database operations for QuickBooks sales forecasting.

This module provides functions for interacting with the database,
including storing and retrieving historical sales data.
"""

import pandas as pd
import os
from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Import database configuration
from src.db_config import DB_PARAMS, ENGINE, Base, get_db_session


def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = ENGINE.connect()
        print(f"Successfully connected to PostgreSQL database: {DB_PARAMS['connection_string']}")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise


class HistoricalSales(Base):
    """Model for historical sales data."""
    __tablename__ = 'historical_sales'

    date = Column(Date, primary_key=True)

    # Category sales columns
    Beauty = Column(Float)
    Books = Column(Float)
    Clothing = Column(Float)
    Electronics = Column(Float)
    Furniture = Column(Float)
    Groceries = Column(Float)
    Sports = Column(Float)
    Toys = Column(Float)

    # Category units columns
    Beauty_units = Column(Float)
    Books_units = Column(Float)
    Clothing_units = Column(Float)
    Electronics_units = Column(Float)
    Furniture_units = Column(Float)
    Groceries_units = Column(Float)
    Sports_units = Column(Float)
    Toys_units = Column(Float)

    # Category lag features
    Beauty_lag_1d = Column(Float)
    Books_lag_1d = Column(Float)
    Clothing_lag_1d = Column(Float)
    Electronics_lag_1d = Column(Float)
    Furniture_lag_1d = Column(Float)
    Groceries_lag_1d = Column(Float)
    Sports_lag_1d = Column(Float)
    Toys_lag_1d = Column(Float)

    # Category units lag features
    Beauty_units_lag_1d = Column(Float)
    Books_units_lag_1d = Column(Float)
    Clothing_units_lag_1d = Column(Float)
    Electronics_units_lag_1d = Column(Float)
    Furniture_units_lag_1d = Column(Float)
    Groceries_units_lag_1d = Column(Float)
    Sports_units_lag_1d = Column(Float)
    Toys_units_lag_1d = Column(Float)

    Beauty_lag_7d = Column(Float)
    Books_lag_7d = Column(Float)
    Clothing_lag_7d = Column(Float)
    Electronics_lag_7d = Column(Float)
    Furniture_lag_7d = Column(Float)
    Groceries_lag_7d = Column(Float)
    Sports_lag_7d = Column(Float)
    Toys_lag_7d = Column(Float)

    # Category units lag 7d features
    Beauty_units_lag_7d = Column(Float)
    Books_units_lag_7d = Column(Float)
    Clothing_units_lag_7d = Column(Float)
    Electronics_units_lag_7d = Column(Float)
    Furniture_units_lag_7d = Column(Float)
    Groceries_units_lag_7d = Column(Float)
    Sports_units_lag_7d = Column(Float)
    Toys_units_lag_7d = Column(Float)

    Beauty_lag_14d = Column(Float)
    Books_lag_14d = Column(Float)
    Clothing_lag_14d = Column(Float)
    Electronics_lag_14d = Column(Float)
    Furniture_lag_14d = Column(Float)
    Groceries_lag_14d = Column(Float)
    Sports_lag_14d = Column(Float)
    Toys_lag_14d = Column(Float)

    # Category units lag 14d features
    Beauty_units_lag_14d = Column(Float)
    Books_units_lag_14d = Column(Float)
    Clothing_units_lag_14d = Column(Float)
    Electronics_units_lag_14d = Column(Float)
    Furniture_units_lag_14d = Column(Float)
    Groceries_units_lag_14d = Column(Float)
    Sports_units_lag_14d = Column(Float)
    Toys_units_lag_14d = Column(Float)

    Beauty_lag_28d = Column(Float)
    Books_lag_28d = Column(Float)
    Clothing_lag_28d = Column(Float)
    Electronics_lag_28d = Column(Float)
    Furniture_lag_28d = Column(Float)
    Groceries_lag_28d = Column(Float)
    Sports_lag_28d = Column(Float)
    Toys_lag_28d = Column(Float)

    # Category units lag 28d features
    Beauty_units_lag_28d = Column(Float)
    Books_units_lag_28d = Column(Float)
    Clothing_units_lag_28d = Column(Float)
    Electronics_units_lag_28d = Column(Float)
    Furniture_units_lag_28d = Column(Float)
    Groceries_units_lag_28d = Column(Float)
    Sports_units_lag_28d = Column(Float)
    Toys_units_lag_28d = Column(Float)

    # Rolling average features
    Beauty_rolling_avg_7d = Column(Float)
    Books_rolling_avg_7d = Column(Float)
    Clothing_rolling_avg_7d = Column(Float)
    Electronics_rolling_avg_7d = Column(Float)
    Furniture_rolling_avg_7d = Column(Float)
    Groceries_rolling_avg_7d = Column(Float)
    Sports_rolling_avg_7d = Column(Float)
    Toys_rolling_avg_7d = Column(Float)

    # Units rolling average features
    Beauty_units_rolling_avg_7d = Column(Float)
    Books_units_rolling_avg_7d = Column(Float)
    Clothing_units_rolling_avg_7d = Column(Float)
    Electronics_units_rolling_avg_7d = Column(Float)
    Furniture_units_rolling_avg_7d = Column(Float)
    Groceries_units_rolling_avg_7d = Column(Float)
    Sports_units_rolling_avg_7d = Column(Float)
    Toys_units_rolling_avg_7d = Column(Float)

    Beauty_rolling_avg_14d = Column(Float)
    Books_rolling_avg_14d = Column(Float)
    Clothing_rolling_avg_14d = Column(Float)
    Electronics_rolling_avg_14d = Column(Float)
    Furniture_rolling_avg_14d = Column(Float)
    Groceries_rolling_avg_14d = Column(Float)
    Sports_rolling_avg_14d = Column(Float)
    Toys_rolling_avg_14d = Column(Float)

    # Units rolling average 14d features
    Beauty_units_rolling_avg_14d = Column(Float)
    Books_units_rolling_avg_14d = Column(Float)
    Clothing_units_rolling_avg_14d = Column(Float)
    Electronics_units_rolling_avg_14d = Column(Float)
    Furniture_units_rolling_avg_14d = Column(Float)
    Groceries_units_rolling_avg_14d = Column(Float)
    Sports_units_rolling_avg_14d = Column(Float)
    Toys_units_rolling_avg_14d = Column(Float)

    Beauty_rolling_avg_28d = Column(Float)
    Books_rolling_avg_28d = Column(Float)
    Clothing_rolling_avg_28d = Column(Float)
    Electronics_rolling_avg_28d = Column(Float)
    Furniture_rolling_avg_28d = Column(Float)
    Groceries_rolling_avg_28d = Column(Float)
    Sports_rolling_avg_28d = Column(Float)
    Toys_rolling_avg_28d = Column(Float)

    # Units rolling average 28d features
    Beauty_units_rolling_avg_28d = Column(Float)
    Books_units_rolling_avg_28d = Column(Float)
    Clothing_units_rolling_avg_28d = Column(Float)
    Electronics_units_rolling_avg_28d = Column(Float)
    Furniture_units_rolling_avg_28d = Column(Float)
    Groceries_units_rolling_avg_28d = Column(Float)
    Sports_units_rolling_avg_28d = Column(Float)
    Toys_units_rolling_avg_28d = Column(Float)

    # Rolling standard deviation features
    Beauty_rolling_std_7d = Column(Float)
    Books_rolling_std_7d = Column(Float)
    Clothing_rolling_std_7d = Column(Float)
    Electronics_rolling_std_7d = Column(Float)
    Furniture_rolling_std_7d = Column(Float)
    Groceries_rolling_std_7d = Column(Float)
    Sports_rolling_std_7d = Column(Float)
    Toys_rolling_std_7d = Column(Float)

    # Units rolling std 7d features
    Beauty_units_rolling_std_7d = Column(Float)
    Books_units_rolling_std_7d = Column(Float)
    Clothing_units_rolling_std_7d = Column(Float)
    Electronics_units_rolling_std_7d = Column(Float)
    Furniture_units_rolling_std_7d = Column(Float)
    Groceries_units_rolling_std_7d = Column(Float)
    Sports_units_rolling_std_7d = Column(Float)
    Toys_units_rolling_std_7d = Column(Float)

    Beauty_rolling_std_14d = Column(Float)
    Books_rolling_std_14d = Column(Float)
    Clothing_rolling_std_14d = Column(Float)
    Electronics_rolling_std_14d = Column(Float)
    Furniture_rolling_std_14d = Column(Float)
    Groceries_rolling_std_14d = Column(Float)
    Sports_rolling_std_14d = Column(Float)
    Toys_rolling_std_14d = Column(Float)

    # Units rolling std 14d features
    Beauty_units_rolling_std_14d = Column(Float)
    Books_units_rolling_std_14d = Column(Float)
    Clothing_units_rolling_std_14d = Column(Float)
    Electronics_units_rolling_std_14d = Column(Float)
    Furniture_units_rolling_std_14d = Column(Float)
    Groceries_units_rolling_std_14d = Column(Float)
    Sports_units_rolling_std_14d = Column(Float)
    Toys_units_rolling_std_14d = Column(Float)

    Beauty_rolling_std_28d = Column(Float)
    Books_rolling_std_28d = Column(Float)
    Clothing_rolling_std_28d = Column(Float)
    Electronics_rolling_std_28d = Column(Float)
    Furniture_rolling_std_28d = Column(Float)
    Groceries_rolling_std_28d = Column(Float)
    Sports_rolling_std_28d = Column(Float)
    Toys_rolling_std_28d = Column(Float)

    # Units rolling std 28d features
    Beauty_units_rolling_std_28d = Column(Float)
    Books_units_rolling_std_28d = Column(Float)
    Clothing_units_rolling_std_28d = Column(Float)
    Electronics_units_rolling_std_28d = Column(Float)
    Furniture_units_rolling_std_28d = Column(Float)
    Groceries_units_rolling_std_28d = Column(Float)
    Sports_units_rolling_std_28d = Column(Float)
    Toys_units_rolling_std_28d = Column(Float)

    # Date-related features
    year = Column(Integer)
    month = Column(Integer)
    day_of_week = Column(Integer)
    week_of_year = Column(Integer)
    quarter = Column(Integer)
    is_weekend = Column(Integer)
    is_month_end = Column(Integer)
    is_month_start = Column(Integer)
    is_november = Column(Integer)

    def __repr__(self):
        return f"<HistoricalSales(date='{self.date}')>"


class Predictions(Base):
    """Model for sales predictions."""
    __tablename__ = 'predictions'

    date = Column(Date, primary_key=True)

    # Category sales columns
    Beauty = Column(Float)
    Books = Column(Float)
    Clothing = Column(Float)
    Electronics = Column(Float)
    Furniture = Column(Float)
    Groceries = Column(Float)
    Sports = Column(Float)
    Toys = Column(Float)

    # Category units columns
    Beauty_units = Column(Float)
    Books_units = Column(Float)
    Clothing_units = Column(Float)
    Electronics_units = Column(Float)
    Furniture_units = Column(Float)
    Groceries_units = Column(Float)
    Sports_units = Column(Float)
    Toys_units = Column(Float)

    # Category lag features
    Beauty_lag_1d = Column(Float)
    Books_lag_1d = Column(Float)
    Clothing_lag_1d = Column(Float)
    Electronics_lag_1d = Column(Float)
    Furniture_lag_1d = Column(Float)
    Groceries_lag_1d = Column(Float)
    Sports_lag_1d = Column(Float)
    Toys_lag_1d = Column(Float)

    # Category units lag features
    Beauty_units_lag_1d = Column(Float)
    Books_units_lag_1d = Column(Float)
    Clothing_units_lag_1d = Column(Float)
    Electronics_units_lag_1d = Column(Float)
    Furniture_units_lag_1d = Column(Float)
    Groceries_units_lag_1d = Column(Float)
    Sports_units_lag_1d = Column(Float)
    Toys_units_lag_1d = Column(Float)

    Beauty_lag_7d = Column(Float)
    Books_lag_7d = Column(Float)
    Clothing_lag_7d = Column(Float)
    Electronics_lag_7d = Column(Float)
    Furniture_lag_7d = Column(Float)
    Groceries_lag_7d = Column(Float)
    Sports_lag_7d = Column(Float)
    Toys_lag_7d = Column(Float)

    # Category units lag 7d features
    Beauty_units_lag_7d = Column(Float)
    Books_units_lag_7d = Column(Float)
    Clothing_units_lag_7d = Column(Float)
    Electronics_units_lag_7d = Column(Float)
    Furniture_units_lag_7d = Column(Float)
    Groceries_units_lag_7d = Column(Float)
    Sports_units_lag_7d = Column(Float)
    Toys_units_lag_7d = Column(Float)

    Beauty_lag_14d = Column(Float)
    Books_lag_14d = Column(Float)
    Clothing_lag_14d = Column(Float)
    Electronics_lag_14d = Column(Float)
    Furniture_lag_14d = Column(Float)
    Groceries_lag_14d = Column(Float)
    Sports_lag_14d = Column(Float)
    Toys_lag_14d = Column(Float)

    # Category units lag 14d features
    Beauty_units_lag_14d = Column(Float)
    Books_units_lag_14d = Column(Float)
    Clothing_units_lag_14d = Column(Float)
    Electronics_units_lag_14d = Column(Float)
    Furniture_units_lag_14d = Column(Float)
    Groceries_units_lag_14d = Column(Float)
    Sports_units_lag_14d = Column(Float)
    Toys_units_lag_14d = Column(Float)

    Beauty_lag_28d = Column(Float)
    Books_lag_28d = Column(Float)
    Clothing_lag_28d = Column(Float)
    Electronics_lag_28d = Column(Float)
    Furniture_lag_28d = Column(Float)
    Groceries_lag_28d = Column(Float)
    Sports_lag_28d = Column(Float)
    Toys_lag_28d = Column(Float)

    # Category units lag 28d features
    Beauty_units_lag_28d = Column(Float)
    Books_units_lag_28d = Column(Float)
    Clothing_units_lag_28d = Column(Float)
    Electronics_units_lag_28d = Column(Float)
    Furniture_units_lag_28d = Column(Float)
    Groceries_units_lag_28d = Column(Float)
    Sports_units_lag_28d = Column(Float)
    Toys_units_lag_28d = Column(Float)

    # Rolling average features
    Beauty_rolling_avg_7d = Column(Float)
    Books_rolling_avg_7d = Column(Float)
    Clothing_rolling_avg_7d = Column(Float)
    Electronics_rolling_avg_7d = Column(Float)
    Furniture_rolling_avg_7d = Column(Float)
    Groceries_rolling_avg_7d = Column(Float)
    Sports_rolling_avg_7d = Column(Float)
    Toys_rolling_avg_7d = Column(Float)

    # Units rolling average features
    Beauty_units_rolling_avg_7d = Column(Float)
    Books_units_rolling_avg_7d = Column(Float)
    Clothing_units_rolling_avg_7d = Column(Float)
    Electronics_units_rolling_avg_7d = Column(Float)
    Furniture_units_rolling_avg_7d = Column(Float)
    Groceries_units_rolling_avg_7d = Column(Float)
    Sports_units_rolling_avg_7d = Column(Float)
    Toys_units_rolling_avg_7d = Column(Float)

    Beauty_rolling_avg_14d = Column(Float)
    Books_rolling_avg_14d = Column(Float)
    Clothing_rolling_avg_14d = Column(Float)
    Electronics_rolling_avg_14d = Column(Float)
    Furniture_rolling_avg_14d = Column(Float)
    Groceries_rolling_avg_14d = Column(Float)
    Sports_rolling_avg_14d = Column(Float)
    Toys_rolling_avg_14d = Column(Float)

    # Units rolling average 14d features
    Beauty_units_rolling_avg_14d = Column(Float)
    Books_units_rolling_avg_14d = Column(Float)
    Clothing_units_rolling_avg_14d = Column(Float)
    Electronics_units_rolling_avg_14d = Column(Float)
    Furniture_units_rolling_avg_14d = Column(Float)
    Groceries_units_rolling_avg_14d = Column(Float)
    Sports_units_rolling_avg_14d = Column(Float)
    Toys_units_rolling_avg_14d = Column(Float)

    Beauty_rolling_avg_28d = Column(Float)
    Books_rolling_avg_28d = Column(Float)
    Clothing_rolling_avg_28d = Column(Float)
    Electronics_rolling_avg_28d = Column(Float)
    Furniture_rolling_avg_28d = Column(Float)
    Groceries_rolling_avg_28d = Column(Float)
    Sports_rolling_avg_28d = Column(Float)
    Toys_rolling_avg_28d = Column(Float)

    # Units rolling average 28d features
    Beauty_units_rolling_avg_28d = Column(Float)
    Books_units_rolling_avg_28d = Column(Float)
    Clothing_units_rolling_avg_28d = Column(Float)
    Electronics_units_rolling_avg_28d = Column(Float)
    Furniture_units_rolling_avg_28d = Column(Float)
    Groceries_units_rolling_avg_28d = Column(Float)
    Sports_units_rolling_avg_28d = Column(Float)
    Toys_units_rolling_avg_28d = Column(Float)

    # Rolling standard deviation features
    Beauty_rolling_std_7d = Column(Float)
    Books_rolling_std_7d = Column(Float)
    Clothing_rolling_std_7d = Column(Float)
    Electronics_rolling_std_7d = Column(Float)
    Furniture_rolling_std_7d = Column(Float)
    Groceries_rolling_std_7d = Column(Float)
    Sports_rolling_std_7d = Column(Float)
    Toys_rolling_std_7d = Column(Float)

    # Units rolling std 7d features
    Beauty_units_rolling_std_7d = Column(Float)
    Books_units_rolling_std_7d = Column(Float)
    Clothing_units_rolling_std_7d = Column(Float)
    Electronics_units_rolling_std_7d = Column(Float)
    Furniture_units_rolling_std_7d = Column(Float)
    Groceries_units_rolling_std_7d = Column(Float)
    Sports_units_rolling_std_7d = Column(Float)
    Toys_units_rolling_std_7d = Column(Float)

    Beauty_rolling_std_14d = Column(Float)
    Books_rolling_std_14d = Column(Float)
    Clothing_rolling_std_14d = Column(Float)
    Electronics_rolling_std_14d = Column(Float)
    Furniture_rolling_std_14d = Column(Float)
    Groceries_rolling_std_14d = Column(Float)
    Sports_rolling_std_14d = Column(Float)
    Toys_rolling_std_14d = Column(Float)

    # Units rolling std 14d features
    Beauty_units_rolling_std_14d = Column(Float)
    Books_units_rolling_std_14d = Column(Float)
    Clothing_units_rolling_std_14d = Column(Float)
    Electronics_units_rolling_std_14d = Column(Float)
    Furniture_units_rolling_std_14d = Column(Float)
    Groceries_units_rolling_std_14d = Column(Float)
    Sports_units_rolling_std_14d = Column(Float)
    Toys_units_rolling_std_14d = Column(Float)

    Beauty_rolling_std_28d = Column(Float)
    Books_rolling_std_28d = Column(Float)
    Clothing_rolling_std_28d = Column(Float)
    Electronics_rolling_std_28d = Column(Float)
    Furniture_rolling_std_28d = Column(Float)
    Groceries_rolling_std_28d = Column(Float)
    Sports_rolling_std_28d = Column(Float)
    Toys_rolling_std_28d = Column(Float)

    # Units rolling std 28d features
    Beauty_units_rolling_std_28d = Column(Float)
    Books_units_rolling_std_28d = Column(Float)
    Clothing_units_rolling_std_28d = Column(Float)
    Electronics_units_rolling_std_28d = Column(Float)
    Furniture_units_rolling_std_28d = Column(Float)
    Groceries_units_rolling_std_28d = Column(Float)
    Sports_units_rolling_std_28d = Column(Float)
    Toys_units_rolling_std_28d = Column(Float)

    # Date-related features
    year = Column(Integer)
    month = Column(Integer)
    day_of_week = Column(Integer)
    week_of_year = Column(Integer)
    quarter = Column(Integer)
    is_weekend = Column(Integer)
    is_month_end = Column(Integer)
    is_month_start = Column(Integer)
    is_november = Column(Integer)

    def __repr__(self):
        return f"<Predictions(date='{self.date}')>"


class Category(Base):
    """Model for product categories."""
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(String(255), nullable=True)

    # Relationship to products
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(name='{self.name}')>"


class Product(Base):
    """Model for products."""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    price = Column(Float)

    # Relationship to category
    category = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Product(name='{self.name}', category_id={self.category_id})>"

def create_tables(conn=None, force=False):
    """
    Create database tables if they don't exist.
    If force is True, drop existing tables and recreate them.

    Args:
        conn (SQLAlchemy connection, optional): Database connection
        force (bool, optional): If True, drop existing tables and recreate them
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
                Predictions.__table__,
                Product.__table__,
                Category.__table__
            ])
            print("Tables dropped successfully")

        # Create tables
        print("Creating tables")
        Base.metadata.create_all(bind=ENGINE)
        print("Database tables created successfully")

        # Close connection if we created it
        if connection_created and conn:
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
        conn (SQLAlchemy connection, optional): Database connection
        force (bool, optional): If True, existing data will be overwritten

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

        print(f"CSV data loaded with {len(df)} rows and {len(df.columns)} columns")

        # Ensure date column is in datetime format
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])

        # Fill NaN values
        df = df.fillna(0)

        # Create a session
        session = get_db_session()

        # Check if data already exists in the database
        existing_count = session.query(HistoricalSales).count()

        if existing_count > 0:
            print(f"Database already contains {existing_count} rows of data")

            # If force is True, delete existing data
            if force:
                session.query(HistoricalSales).delete()
                session.commit()
                print("Existing data deleted")
            else:
                print("Use force=True to overwrite existing data")
                session.close()
                if connection_created:
                    conn.close()
                return 0

        # Insert data into database using bulk operations
        print(f"Inserting {len(df)} rows into database")
        records = df.to_dict('records')

        # Use bulk insert for better performance
        session.bulk_insert_mappings(HistoricalSales, records)
        session.commit()

        # Verify insertion
        inserted_count = session.query(HistoricalSales).count()
        print(f"Successfully inserted {inserted_count} rows into historical_sales table")

        # Close session
        session.close()

        # Close connection if we created it
        if connection_created:
            conn.close()

        return inserted_count

    except Exception as e:
        print(f"Error storing historical sales data: {e}")
        import traceback
        traceback.print_exc()
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
        conn (SQLAlchemy connection, optional): Database connection

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

        # Execute query and convert to DataFrame
        records = query.all()

        # Convert to DataFrame
        data = []
        for record in records:
            row = {column.name: getattr(record, column.name) for column in record.__table__.columns}
            data.append(row)

        df = pd.DataFrame(data)

        # Set date as index if present
        if 'date' in df.columns:
            df = df.set_index('date')
            df = df.sort_index()

        # Close session
        session.close()

        # Close connection if we created it
        if connection_created:
            conn.close()

        print(f"Retrieved {len(df)} historical sales records")
        return df

    except Exception as e:
        print(f"Error retrieving historical sales data: {e}")
        import traceback
        traceback.print_exc()
        if 'session' in locals() and session:
            session.close()
        if 'conn' in locals() and conn and connection_created:
            conn.close()
        raise


def store_predictions(predictions_df, conn=None, force=False):
    """
    Store sales predictions in the database.

    Args:
        predictions_df (DataFrame): DataFrame containing predictions with date as index
        conn (SQLAlchemy connection, optional): Database connection
        force (bool, optional): If True, existing predictions will be overwritten

    Returns:
        int: Number of rows inserted
    """
    try:
        # Create connection if not provided
        connection_created = False
        if conn is None:
            conn = get_db_connection()
            connection_created = True

        # Ensure tables exist
        create_tables(conn)

        # Reset index to make date a column
        if isinstance(predictions_df.index, pd.DatetimeIndex):
            predictions_df = predictions_df.reset_index()

        # Ensure date column is in datetime format
        if not pd.api.types.is_datetime64_any_dtype(predictions_df['date']):
            predictions_df['date'] = pd.to_datetime(predictions_df['date'])

        # Fill NaN values
        predictions_df = predictions_df.fillna(0)

        # Create a session
        session = get_db_session()

        # If force is True, delete all existing predictions
        if force:
            session.query(Predictions).delete()
            session.commit()
            print("Deleted all existing predictions")

        # Otherwise, delete predictions for the specific dates in the DataFrame
        else:
            dates = predictions_df['date'].dt.date.tolist()
            if dates:
                deleted = session.query(Predictions).filter(Predictions.date.in_(dates)).delete(
                    synchronize_session='fetch')
                session.commit()
                print(f"Deleted {deleted} existing predictions for the specified date range")

        # Insert data into database using bulk operations
        print(f"Inserting {len(predictions_df)} predictions into database")
        records = predictions_df.to_dict('records')

        # Use bulk insert for better performance
        session.bulk_insert_mappings(Predictions, records)
        session.commit()

        # Verify insertion
        inserted_count = session.query(Predictions).count()
        print(f"Successfully inserted/updated predictions. Total predictions in database: {inserted_count}")

        # Close session
        session.close()

        # Close connection if we created it
        if connection_created:
            conn.close()

        return len(predictions_df)

    except Exception as e:
        print(f"Error storing predictions: {e}")
        import traceback
        traceback.print_exc()
        if 'session' in locals() and session:
            session.rollback()
            session.close()
        if 'conn' in locals() and conn and connection_created:
            conn.close()
        raise


def get_predictions(start_date=None, end_date=None, conn=None):
    """
    Retrieve predictions from the database.

    Args:
        start_date (str or datetime, optional): Start date for filtering
        end_date (str or datetime, optional): End date for filtering
        conn (SQLAlchemy connection, optional): Database connection

    Returns:
        DataFrame: Predictions data
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

        # Execute query and convert to DataFrame
        records = query.all()

        # Convert to DataFrame
        data = []
        for record in records:
            row = {column.name: getattr(record, column.name) for column in record.__table__.columns}
            data.append(row)

        df = pd.DataFrame(data)

        # Set date as index if present
        if 'date' in df.columns:
            df = df.set_index('date')
            df = df.sort_index()

        # Close session
        session.close()

        # Close connection if we created it
        if connection_created:
            conn.close()

        print(f"Retrieved {len(df)} prediction records")
        return df

    except Exception as e:
        print(f"Error retrieving predictions: {e}")
        import traceback
        traceback.print_exc()
        if 'session' in locals() and session:
            session.close()
        if 'conn' in locals() and conn and connection_created:
            conn.close()
        raise


def populate_categories_and_products(sales_csv_path, conn=None, force=False):
    """
    Populate the category and product tables from a sales CSV file.

    Args:
        sales_csv_path (str): Path to the CSV file containing sales data
        conn (SQLAlchemy connection, optional): Database connection
        force (bool, optional): If True, existing data will be overwritten

    Returns:
        tuple: (categories_count, products_count) - Number of categories and products inserted
    """
    try:
        # Create connection if not provided
        connection_created = False
        if conn is None:
            conn = get_db_connection()
            connection_created = True

        # Create tables if they don't exist
        create_tables(conn)

        # Create a session
        session = get_db_session()

        # Check if data already exists in the database
        existing_categories = session.query(Category).count()
        existing_products = session.query(Product).count()

        if existing_categories > 0 or existing_products > 0:
            print(f"Database already contains {existing_categories} categories and {existing_products} products")

            # If force is True, delete existing data
            if force:
                session.query(Product).delete()
                session.query(Category).delete()
                session.commit()
                print("Existing categories and products deleted")
            else:
                print("Use force=True to overwrite existing data")
                session.close()
                if connection_created:
                    conn.close()
                return (existing_categories, existing_products)

        # Read CSV file to extract categories and products
        print(f"Reading sales data from {sales_csv_path}")
        df = pd.read_csv(sales_csv_path)

        if 'category' not in df.columns or 'product' not in df.columns:
            raise ValueError("CSV must contain 'category' and 'product' columns")

        # Extract unique categories and products
        categories_df = df[['category']].drop_duplicates()

        # Insert categories
        print(f"Inserting {len(categories_df)} categories")
        category_map = {}  # To store category_name -> category_id mapping

        for _, row in categories_df.iterrows():
            category_name = row['category']
            category = Category(name=category_name)
            session.add(category)
            session.flush()  # Get the ID before committing
            category_map[category_name] = category.id

        session.commit()

        # Extract unique product-category pairs
        products_df = df[['product', 'category']].drop_duplicates()

        # Insert products
        print(f"Inserting {len(products_df)} products")
        for _, row in products_df.iterrows():
            product_name = row['product']
            category_name = row['category']
            category_id = category_map.get(category_name)

            if category_id:
                product = Product(name=product_name, category_id=category_id)
                session.add(product)
            else:
                print(f"Warning: Category '{category_name}' not found for product '{product_name}'")

        session.commit()

        # Verify insertion
        inserted_categories = session.query(Category).count()
        inserted_products = session.query(Product).count()

        print(f"Successfully inserted {inserted_categories} categories and {inserted_products} products")

        # Close session
        session.close()

        # Close connection if we created it
        if connection_created:
            conn.close()

        return (inserted_categories, inserted_products)

    except Exception as e:
        print(f"Error populating categories and products: {e}")
        import traceback
        traceback.print_exc()
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
        conn (SQLAlchemy connection, optional): Database connection

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

        # Query categories
        categories = session.query(Category).order_by(Category.name).all()

        # Convert to DataFrame
        data = []
        for category in categories:
            row = {column.name: getattr(category, column.name) for column in category.__table__.columns}
            data.append(row)

        # Create DataFrame
        df = pd.DataFrame(data)

        # Close session
        session.close()

        # Close connection if we created it
        if connection_created:
            conn.close()

        print(f"Retrieved {len(df)} categories")
        return df

    except Exception as e:
        print(f"Error retrieving categories: {e}")
        if 'session' in locals() and session:
            session.close()
        if 'conn' in locals() and conn and connection_created:
            conn.close()
        raise


def get_products(category_id=None, conn=None):
    """
    Retrieve products from the database, optionally filtered by category.

    Args:
        category_id (int, optional): Category ID for filtering
        conn (SQLAlchemy connection, optional): Database connection

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
        query = session.query(Product).join(Category)

        # Add category filter if provided
        if category_id:
            query = query.filter(Product.category_id == category_id)

        # Order by category name and product name
        query = query.order_by(Category.name, Product.name)

        # Execute query
        products = query.all()

        # Convert to DataFrame
        data = []
        for product in products:
            row = {column.name: getattr(product, column.name) for column in product.__table__.columns}
            # Add category name
            row['category_name'] = product.category.name
            data.append(row)

        # Create DataFrame
        df = pd.DataFrame(data)

        # Close session
        session.close()

        # Close connection if we created it
        if connection_created:
            conn.close()

        filter_msg = f" for category ID {category_id}" if category_id else ""
        print(f"Retrieved {len(df)} products{filter_msg}")
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