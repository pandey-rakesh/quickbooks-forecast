"""
Feature builder module for QuickBooks sales forecasting.

This module provides a FeatureBuilder class that creates model-ready features
for the sales forecasting model using historical sales data and predictions.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import pickle
import os
import re
import sys
from pathlib import Path

# Add the project root directory to the Python path when run as a script
if __name__ == "__main__":
    # Get the absolute path of the current file
    current_file = Path(__file__).resolve()
    # Get the project root directory (two levels up from the current file)
    project_root = current_file.parent.parent.parent
    # Add the project root to the Python path
    sys.path.append(str(project_root))

# Import database operations
try:
    from src.db_operations import get_historical_sales, get_predictions
except ImportError:
    # When run as a script, try importing with a different path
    from db_operations import get_historical_sales, get_predictions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FeatureBuilder:
    """
    A class to build features for the sales forecasting model.

    This class loads historical sales data and predictions from the database,
    and creates features for a specified date range. It handles time-based features,
    lagged features, and category-based features.
    """

    def __init__(self, categories=None, lag_days=None, feature_columns_path=None):
        """
        Initialize the FeatureBuilder.

        Args:
            categories (list, optional): List of product categories to include.
                If None, categories will be extracted from feature_columns.pkl.
            lag_days (list, optional): Days to lag for creating lag features.
                If None, lag days will be extracted from feature_columns.pkl.
            feature_columns_path (str, optional): Path to the feature columns pickle file.
                If None, defaults to 'model/feature_columns.pkl'.
        """
        # Load feature columns from pickle file
        self.feature_columns_path = feature_columns_path or 'model/feature_columns.pkl'
        self.feature_columns = self._load_feature_columns()

        # Extract categories and lag days from feature columns if not provided
        if categories is None or lag_days is None:
            extracted_categories, extracted_lag_days = self._extract_from_feature_columns()

            # Use extracted values if not provided
            self.categories = categories or extracted_categories
            self.lag_days = lag_days or extracted_lag_days
        else:
            self.categories = categories
            self.lag_days = lag_days

        logger.info(f"Initialized FeatureBuilder with categories: {self.categories}")
        logger.info(f"Lag days: {self.lag_days}")
        logger.info(f"Loaded {len(self.feature_columns)} feature columns from {self.feature_columns_path}")

    def _load_feature_columns(self):
        """
        Load feature columns from pickle file.

        Returns:
            list: List of feature column names
        """
        try:
            if os.path.exists(self.feature_columns_path):
                with open(self.feature_columns_path, 'rb') as f:
                    feature_columns = pickle.load(f)
                logger.info(f"Loaded {len(feature_columns)} feature columns from {self.feature_columns_path}")
                return feature_columns
            else:
                logger.warning(f"Feature columns file not found: {self.feature_columns_path}")
                return []
        except Exception as e:
            logger.error(f"Error loading feature columns: {e}")
            return []

    def _extract_from_feature_columns(self):
        """
        Extract categories and lag days from feature columns.

        Returns:
            tuple: (categories, lag_days)
        """
        if not self.feature_columns:
            # Default values if feature columns couldn't be loaded
            return (
                ['Beauty', 'Books', 'Clothing', 'Electronics', 'Furniture', 'Groceries', 'Sports', 'Toys'],
                [1, 7, 14]
            )

        # Extract categories and lag days from lag feature columns
        # Example: 'Beauty_lag_1' -> category='Beauty', lag=1
        categories = set()
        lag_days = set()

        lag_pattern = re.compile(r'(.+)_lag_(\d+)')

        for col in self.feature_columns:
            match = lag_pattern.match(col)
            if match:
                category, lag = match.groups()
                categories.add(category)
                lag_days.add(int(lag))

        # Convert to sorted lists
        categories_list = sorted(list(categories))
        lag_days_list = sorted(list(lag_days))

        # If no categories or lag days were found, use defaults
        if not categories_list:
            categories_list = ['Beauty', 'Books', 'Clothing', 'Electronics', 'Furniture', 'Groceries', 'Sports', 'Toys']
        if not lag_days_list:
            lag_days_list = [1, 7, 14]

        logger.info(f"Extracted categories from feature columns: {categories_list}")
        logger.info(f"Extracted lag days from feature columns: {lag_days_list}")

        return categories_list, lag_days_list

    def load_historical_data(self, days_to_load=60, end_date=None):
        """
        Load historical sales data and predictions from the database.

        Args:
            days_to_load (int): Number of days of historical data to load
            end_date (datetime, optional): End date for historical data.
                If None, uses the current date.

        Returns:
            DataFrame: Combined historical sales and predictions data with date as index
        """
        # Determine end date if not provided
        if end_date is None:
            end_date = datetime.now().date()
        else:
            if isinstance(end_date, str):
                end_date = pd.to_datetime(end_date).date()

        # Calculate start date based on days_to_load
        start_date = end_date - timedelta(days=days_to_load)

        logger.info(f"Loading historical data from {start_date} to {end_date}")

        # Load historical sales data (date is already set as index by get_historical_sales)
        historical_df = get_historical_sales(start_date=start_date, end_date=end_date)
        logger.info(f"Loaded {len(historical_df)} rows of historical sales data")

        # Load predictions data
        predictions_df = get_predictions(start_date=start_date, end_date=end_date)
        logger.info(f"Loaded {len(predictions_df)} rows of predictions data")

        # Ensure date is the index for predictions_df if it's not empty
        if not predictions_df.empty:
            # If date is a column, set it as the index
            if 'date' in predictions_df.columns:
                predictions_df = predictions_df.set_index('date')
                logger.info("Set 'date' as index for predictions DataFrame")

        # Combine historical and predictions data
        if not predictions_df.empty:
            # Both DataFrames should have date as index at this point
            combined_df = pd.concat([historical_df, predictions_df])
            # Remove duplicates, keeping historical data when there's a conflict
            combined_df = combined_df[~combined_df.index.duplicated(keep='first')]
        else:
            combined_df = historical_df

        # Sort by date index
        if not combined_df.empty:
            combined_df = combined_df.sort_index()

        logger.info(f"Combined data has {len(combined_df)} rows")
        return combined_df

    def create_date_features(self, date):
        """
        Create date-derived features for a specific date.

        Args:
            date (datetime): The date to create features for

        Returns:
            dict: Dictionary of date features
        """
        # Convert to pandas Timestamp for easier feature extraction
        ts = pd.Timestamp(date)

        # Create date features
        features = {
            'date': ts,
            'year': ts.year,
            'month': ts.month,
            'day_of_week': ts.dayofweek,
            'is_weekend': 1 if ts.dayofweek >= 5 else 0,
            'week_of_year': ts.weekofyear,
            'quarter': ts.quarter,
            'is_month_end': 1 if ts.is_month_end else 0,
            'is_month_start': 1 if ts.is_month_start else 0,
            'is_november': 1 if ts.month == 11 else 0
        }

        return features

    def get_lag_value(self, historical_df, date, category, lag_days, feature_rows=None):
        """
        Get lagged value for a specific category and date.

        Args:
            historical_df (DataFrame): Historical data with date as index
            date (datetime): The date to get lag for
            category (str): The category to get lag for
            lag_days (int): Number of days to lag
            feature_rows (list, optional): List of feature dictionaries generated so far.
                Used to find lag values not present in historical_df.

        Returns:
            float: The lagged value or 0 if not available
        """
        lag_date = date - timedelta(days=lag_days)

        logger.debug(f"Getting lag value for date={date}, category={category}, lag_days={lag_days}")
        logger.debug(f"Lag date: {lag_date}")
        logger.debug(f"Feature rows count: {len(feature_rows) if feature_rows is not None else 0}")

        # Ensure historical_df is not empty
        if historical_df.empty and (feature_rows is None or len(feature_rows) == 0):
            logger.debug("Both historical_df and feature_rows are empty, returning 0")
            return 0.0

        # Try different approaches to get the lag value from historical_df
        try:
            # Try to get the value directly from the index
            if lag_date in historical_df.index:
                value = historical_df.loc[lag_date, category]
                logger.debug(f"Found value in historical_df index: {value}")
                return value

            # Try with string format
            lag_date_str = lag_date.strftime('%Y-%m-%d')
            if lag_date_str in historical_df.index:
                value = historical_df.loc[lag_date_str, category]
                logger.debug(f"Found value in historical_df string index: {value}")
                return value

            # Try with just the date part if index contains timestamps
            if not historical_df.empty and hasattr(historical_df.index[0], 'date'):
                # Convert index to date objects for comparison
                date_index = historical_df.index.map(lambda x: x.date() if hasattr(x, 'date') else x)
                if lag_date in date_index:
                    idx = date_index.get_loc(lag_date)
                    value = historical_df.iloc[idx][category]
                    logger.debug(f"Found value in historical_df date index: {value}")
                    return value

            # If not found in historical_df, try to find in feature_rows
            if feature_rows is not None and len(feature_rows) > 0:
                logger.debug(f"Checking {len(feature_rows)} feature rows for lag date {lag_date}")
                for i, row in enumerate(feature_rows):
                    # Check if the row has a date key and it matches the lag date
                    if 'date' in row:
                        row_date = row['date']
                        # Convert to date object if it's a datetime
                        if hasattr(row_date, 'date'):
                            row_date = row_date.date()
                        # Convert lag_date to date object if it's a datetime
                        lag_date_obj = lag_date
                        if hasattr(lag_date, 'date'):
                            lag_date_obj = lag_date.date()
                        # Compare dates
                        logger.debug(f"Comparing row_date={row_date} with lag_date_obj={lag_date_obj}")
                        if row_date == lag_date_obj:
                            if category in row:
                                value = row[category]
                                logger.debug(f"Found value in feature_rows[{i}]: {value}")
                                return value
                            else:
                                logger.debug(f"Category {category} not found in feature_rows[{i}]")
                logger.debug(f"Lag date {lag_date} not found in any feature row")
            else:
                logger.debug("No feature rows to check")

            # If all attempts fail, return 0
            logger.debug("All attempts failed, returning 0")
            return 0.0

        except (KeyError, TypeError, ValueError) as e:
            # If any error occurs, log it and return 0
            logger.debug(f"Error getting lag value for {lag_date}, {category}, {lag_days}: {e}")
            return 0.0

    def build_features(self, start_date, end_date, historical_data=None):
        """
        Build features for a specified date range.

        Args:
            start_date (datetime or str): Start date for feature generation
            end_date (datetime or str): End date for feature generation
            historical_data (DataFrame, optional): Historical data to use.
                If None, data will be loaded from the database.

        Returns:
            DataFrame: Features for the specified date range
        """
        # Convert dates to datetime if they are strings
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date).date()
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date).date()

        logger.info(f"Building features from {start_date} to {end_date}")

        # Load historical data if not provided
        if historical_data is None:
            # Load enough historical data to compute all lags
            max_lag = max(self.lag_days)
            days_to_load = (end_date - start_date).days + max_lag + 10  # Add buffer
            historical_data = self.load_historical_data(days_to_load=days_to_load, end_date=end_date)

        # Create a copy of historical data to update with newly generated data
        working_data = historical_data.copy()

        # Ensure date is the index for working_data
        if 'date' in working_data.columns:
            logger.info("Converting 'date' column to index in historical data")
            working_data = working_data.set_index('date')

        # Create date range for feature generation
        future_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        logger.info(f"Generating features for {len(future_dates)} days")

        # Initialize empty list to store feature rows
        feature_rows = []

        # Loop through each future date
        for future_date in future_dates:
            future_date = future_date.date()  # Convert to date object

            # Create base features from date
            features = self.create_date_features(future_date)

            # Initialize category values and lag features
            for category in self.categories:
                # First, try to get the category value from historical data (1-day lag)
                category_value = self.get_lag_value(
                    working_data, future_date, category, 1, feature_rows
                )

                # If we found a value, use it; otherwise, use a random value for testing
                # In a real scenario, this would be filled by model prediction
                if category_value != 0.0:
                    features[category] = category_value
                else:
                    # For testing purposes, use a random value
                    # This ensures that feature_rows will have non-zero category values
                    # that can be used for lag calculations in subsequent iterations
                    features[category] = np.random.randint(100, 1000)
                    logger.debug(f"Using random value {features[category]} for {category} on {future_date}")

                # Add lag features for each category
                for lag in self.lag_days:
                    lag_key = f"{category}_lag_{lag}"
                    features[lag_key] = self.get_lag_value(
                        working_data, future_date, category, lag, feature_rows
                    )

            # Add row to features list
            feature_rows.append(features)

            # Update working data with the newly generated features
            # This allows subsequent dates to use previously generated data for lag calculations
            new_row = features.copy()

            # Create a new DataFrame with the current date as index
            new_df = pd.DataFrame([new_row]).set_index('date')

            # Append to working data
            working_data = pd.concat([working_data, new_df])

            # Sort by date index to ensure chronological order
            working_data = working_data.sort_index()

        # Convert to DataFrame
        features_df = pd.DataFrame(feature_rows)

        # Set date as index
        features_df.set_index('date', inplace=True)

        # Fill any missing values with 0
        features_df.fillna(0, inplace=True)

        logger.info(f"Generated features DataFrame with shape: {features_df.shape}")

        return features_df

    def get_model_features(self, start_date, end_date, feature_columns=None, historical_data=None):
        """
        Get model-ready features for the specified date range.

        Args:
            start_date (datetime or str): Start date for feature generation
            end_date (datetime or str): End date for feature generation
            feature_columns (list, optional): List of columns to include in the output.
                If None, uses the columns loaded from feature_columns.pkl.
            historical_data (DataFrame, optional): Historical data to use for feature generation.
                If None, data will be loaded from the database.

        Returns:
            DataFrame: Model-ready features
        """
        # Build features
        features_df = self.build_features(start_date, end_date, historical_data=historical_data)

        # Use loaded feature columns if none are specified
        if feature_columns is None and self.feature_columns:
            feature_columns = self.feature_columns
            logger.info(f"Using {len(feature_columns)} feature columns from {self.feature_columns_path}")
        elif feature_columns is None:
            # If no feature columns are loaded or specified, remove target categories
            logger.warning("No feature columns specified or loaded, removing target categories")
            feature_columns = [col for col in features_df.columns if col not in self.categories]

        # Check if all required columns are present
        missing_cols = set(feature_columns) - set(features_df.columns)
        if missing_cols:
            logger.warning(f"Missing columns in features: {missing_cols}")
            # Add missing columns with zeros
            for col in missing_cols:
                features_df[col] = 0

        # Select only the required columns
        features_df = features_df[feature_columns]

        logger.info(f"Final model features shape: {features_df.shape}")
        return features_df


if __name__ == "__main__":
    # Example usage
    try:
        # Create feature builder with feature columns from pickle file
        builder = FeatureBuilder()

        # Define date range for features
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=7)

        # Build features using the columns from feature_columns.pkl
        features = builder.get_model_features(start_date, end_date)

        print(f"Successfully built features with shape: {features.shape}")
        print(f"First 10 feature columns: {features.columns.tolist()[:10]}")

        # You can also specify a custom path to the feature columns file
        custom_path = 'model/feature_columns.pkl'  # Change this to your custom path if needed
        if os.path.exists(custom_path) and custom_path != 'model/feature_columns.pkl':
            print(f"\nUsing custom feature columns from {custom_path}")
            custom_builder = FeatureBuilder(feature_columns_path=custom_path)
            custom_features = custom_builder.get_model_features(start_date, end_date)
            print(f"Custom features shape: {custom_features.shape}")

        # You can also provide explicit categories and lag days
        print("\nUsing explicit categories and lag days")
        explicit_builder = FeatureBuilder(
            categories=['Beauty', 'Electronics', 'Clothing'],
            lag_days=[1, 7]
        )
        # But still use the feature columns from the pickle file for the final output
        explicit_features = explicit_builder.get_model_features(start_date, end_date)
        print(f"Explicit features shape: {explicit_features.shape}")

    except Exception as e:
        print(f"Error building features: {e}")
