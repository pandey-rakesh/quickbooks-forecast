"""
Test script for the feature_engineering module.

This script tests the FeatureBuilder class in the src.feature_engineering.feature_builder module
to ensure it correctly generates features for the sales forecasting model.
"""

import sys
import os
import logging
from datetime import datetime, timedelta
import pandas as pd
import pickle

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the feature_builder module
from src.feature_engineering.feature_builder import FeatureBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_feature_builder():
    """
    Test the FeatureBuilder class.
    
    This function tests the following:
    1. Loading historical data from the database
    2. Building features for a specified date range
    3. Ensuring the features match the expected format for the model
    """
    try:
        logger.info("Testing FeatureBuilder...")
        
        # Create feature builder
        builder = FeatureBuilder()
        
        # Define date range for features (next 7 days)
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=7)
        
        logger.info(f"Building features for date range: {start_date} to {end_date}")
        
        # Build features
        features = builder.build_features(start_date, end_date)
        
        # Check that features were generated for each day in the range
        expected_days = (end_date - start_date).days + 1
        actual_days = len(features)
        
        logger.info(f"Expected {expected_days} days of features, got {actual_days}")
        assert actual_days == expected_days, f"Expected {expected_days} days of features, got {actual_days}"
        
        # Check that all required columns are present
        required_columns = [
            'year', 'month', 'day_of_week', 'is_weekend', 'week_of_year',
            'quarter', 'is_month_end', 'is_month_start', 'is_november'
        ]
        
        # Add category columns
        categories = [
            'Beauty', 'Books', 'Clothing', 'Electronics',
            'Furniture', 'Groceries', 'Sports', 'Toys'
        ]
        
        # Add lag columns
        lag_days = [1, 7, 14]
        for category in categories:
            for lag in lag_days:
                required_columns.append(f"{category}_lag_{lag}")
        
        # Check that all required columns are present
        missing_columns = set(required_columns) - set(features.columns)
        if missing_columns:
            logger.error(f"Missing columns: {missing_columns}")
            assert not missing_columns, f"Missing columns: {missing_columns}"
        
        logger.info("All required columns are present")
        
        # Try loading the feature columns from the model
        try:
            with open('model/feature_columns.pkl', 'rb') as f:
                model_feature_columns = pickle.load(f)
                
            logger.info(f"Loaded {len(model_feature_columns)} feature columns from model")
            
            # Get model-ready features
            model_features = builder.get_model_features(start_date, end_date, feature_columns=model_feature_columns)
            
            # Check that the features match the expected format
            assert set(model_features.columns) == set(model_feature_columns), \
                "Model features do not match expected columns"
                
            logger.info("Model features match expected format")
        except FileNotFoundError:
            logger.warning("Could not find feature_columns.pkl, skipping model feature test")
        
        logger.info("FeatureBuilder tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing FeatureBuilder: {e}")
        return False

if __name__ == "__main__":
    success = test_feature_builder()
    sys.exit(0 if success else 1)