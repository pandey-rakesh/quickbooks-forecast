"""
Utility functions for the QuickBooks Sales Forecasting API.

This module provides helper functions for date filtering, data transformation,
and other utility operations used throughout the application.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any, Optional, Tuple, Union

from app.config import LOG_LEVEL, LOG_FORMAT

# Set up logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger with the specified name.
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    return logger


def parse_date_range(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: int = 30
) -> Tuple[datetime, datetime]:
    """
    Parse and validate date range parameters.

    Args:
        start_date (str, optional): Start date in ISO format (YYYY-MM-DD)
        end_date (str, optional): End date in ISO format (YYYY-MM-DD)
        days (int): Number of days to include if start_date is not provided

    Returns:
        tuple: (start_date, end_date) as datetime objects
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    if end_date:
        try:
            end_dt = pd.to_datetime(end_date)
        except ValueError:
            logger.warning(f"Invalid end_date format: {end_date}, using today")
            end_dt = today
    else:
        end_dt = today

    if start_date:
        try:
            start_dt = pd.to_datetime(start_date)
        except ValueError:
            logger.warning(f"Invalid start_date format: {start_date}, using {days} days before end_date")
            start_dt = end_dt - timedelta(days=days)
    else:
        start_dt = end_dt - timedelta(days=days)

    # Ensure start_date is before end_date
    if start_dt > end_dt:
        logger.warning(f"start_date {start_dt} is after end_date {end_dt}, swapping dates")
        start_dt, end_dt = end_dt, start_dt

    return start_dt, end_dt


def filter_dataframe_by_date(
    df: pd.DataFrame,
    start_date: datetime,
    end_date: datetime,
    date_column: str = 'date'
) -> pd.DataFrame:
    """
    Filter a DataFrame by date range.
    
    Args:
        df (DataFrame): Input DataFrame
        start_date (datetime): Start date
        end_date (datetime): End date
        date_column (str): Name of the date column
        
    Returns:
        DataFrame: Filtered DataFrame
    """
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
        df[date_column] = pd.to_datetime(df[date_column])
    
    # Filter by date range
    mask = (df[date_column] >= start_date) & (df[date_column] <= end_date)
    filtered_df = df.loc[mask].copy()
    
    logger.debug(f"Filtered DataFrame from {len(df)} to {len(filtered_df)} rows")
    
    return filtered_df


def get_top_categories(
    df: pd.DataFrame,
    n: int = 5,
    amount_column: str = 'amount',
    category_column: str = 'category'
) -> List[Dict[str, Any]]:
    """
    Get the top N categories by sales amount.
    
    Args:
        df (DataFrame): Input DataFrame
        n (int): Number of top categories to return
        amount_column (str): Name of the amount column
        category_column (str): Name of the category column
        
    Returns:
        list: List of dictionaries with category and amount
    """
    # Group by category and sum amounts
    category_totals = df.groupby(category_column)[amount_column].sum().reset_index()
    
    # Sort by amount in descending order and take top N
    top_categories = category_totals.sort_values(amount_column, ascending=False).head(n)
    
    # Convert to list of dictionaries
    result = []
    for _, row in top_categories.iterrows():
        result.append({
            'category': row[category_column],
            'amount': float(row[amount_column]),
            'percentage': float(row[amount_column] / category_totals[amount_column].sum() * 100)
        })
    
    return result


def format_currency(amount: float) -> str:
    """
    Format a number as currency.
    
    Args:
        amount (float): Amount to format
        
    Returns:
        str: Formatted currency string
    """
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """
    Format a number as percentage.
    
    Args:
        value (float): Value to format
        
    Returns:
        str: Formatted percentage string
    """
    return f"{value:.2f}%"


def format_date(date: Union[str, datetime]) -> str:
    """
    Format a date as a string.
    
    Args:
        date (str or datetime): Date to format
        
    Returns:
        str: Formatted date string
    """
    if isinstance(date, str):
        date = pd.to_datetime(date)
    
    return date.strftime('%Y-%m-%d')


def calculate_growth_rate(
    current_value: float,
    previous_value: float
) -> float:
    """
    Calculate growth rate between two values.
    
    Args:
        current_value (float): Current value
        previous_value (float): Previous value
        
    Returns:
        float: Growth rate as percentage
    """
    if previous_value == 0:
        return float('inf') if current_value > 0 else 0
    
    return (current_value - previous_value) / previous_value * 100


def generate_date_range(
    start_date: datetime,
    end_date: datetime
) -> List[datetime]:
    """
    Generate a list of dates between start_date and end_date.
    
    Args:
        start_date (datetime): Start date
        end_date (datetime): End date
        
    Returns:
        list: List of dates
    """
    date_range = []
    current_date = start_date
    
    while current_date <= end_date:
        date_range.append(current_date)
        current_date += timedelta(days=1)
    
    return date_range


def create_empty_dataframe_with_dates(
    start_date: datetime,
    end_date: datetime,
    categories: List[str]
) -> pd.DataFrame:
    """
    Create an empty DataFrame with dates and categories.
    
    Args:
        start_date (datetime): Start date
        end_date (datetime): End date
        categories (list): List of category names
        
    Returns:
        DataFrame: Empty DataFrame with dates and categories
    """
    # Generate date range
    date_range = generate_date_range(start_date, end_date)
    
    # Create empty DataFrame
    df = pd.DataFrame({
        'date': date_range,
        'category': [categories[0]] * len(date_range),
        'amount': [0.0] * len(date_range),
        'customer_id': [''] * len(date_range),
        'transaction_id': [''] * len(date_range)
    })
    
    # Add rows for each category
    for category in categories[1:]:
        temp_df = df.copy()
        temp_df['category'] = category
        df = pd.concat([df, temp_df])
    
    return df.sort_values(['date', 'category']).reset_index(drop=True)