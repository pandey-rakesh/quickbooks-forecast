"""
Unit tests for model inference.

This module contains tests for the model inference functionality,
including loading the model and making predictions.
"""

import unittest
import pandas as pd
import numpy as np
import pickle
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to allow importing from model
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.features import build_features_for_inference


class MockModel:
    """Mock model for testing inference."""
    
    def __init__(self, return_value=None):
        """Initialize with a fixed return value."""
        self.return_value = return_value if return_value is not None else np.array([100.0])
        self.predict_called = False
        self.predict_args = None
    
    def predict(self, X):
        """Mock predict method."""
        self.predict_called = True
        self.predict_args = X
        
        # Return a fixed value or an array of the same length as X
        if isinstance(self.return_value, (int, float)):
            return np.array([self.return_value] * len(X))
        else:
            return self.return_value


class TestModelInference(unittest.TestCase):
    """Test cases for model inference."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample sales data
        self.sales_data = pd.DataFrame({
            'date': [
                '2023-01-01', '2023-01-01', '2023-01-02', '2023-01-02', '2023-01-03',
                '2023-01-03', '2023-01-04', '2023-01-04', '2023-01-05', '2023-01-05'
            ],
            'category': [
                'Electronics', 'Clothing', 'Electronics', 'Food', 'Electronics',
                'Home', 'Clothing', 'Food', 'Electronics', 'Clothing'
            ],
            'amount': [
                100.0, 50.0, 200.0, 30.0, 150.0,
                75.0, 60.0, 40.0, 180.0, 70.0
            ],
            'customer_id': [
                'C001', 'C002', 'C003', 'C004', 'C005',
                'C006', 'C007', 'C008', 'C009', 'C010'
            ],
            'transaction_id': [
                'T001', 'T002', 'T003', 'T004', 'T005',
                'T006', 'T007', 'T008', 'T009', 'T010'
            ]
        })
        
        # Convert date to datetime
        self.sales_data['date'] = pd.to_datetime(self.sales_data['date'])
        
        # Define feature columns
        self.feature_columns = [
            'year', 'month', 'day', 'day_of_week', 'is_weekend',
            'total_sales_lag_1d', 'Electronics', 'Clothing'
        ]
        
        # Create mock model
        self.mock_model = MockModel(return_value=150.0)
        
        # Create temporary model file
        self.model_path = os.path.join(os.path.dirname(__file__), 'temp_model.pkl')
        self.feature_columns_path = os.path.join(os.path.dirname(__file__), 'temp_feature_columns.pkl')
        
        # Save mock model and feature columns
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.mock_model, f)
        
        with open(self.feature_columns_path, 'wb') as f:
            pickle.dump(self.feature_columns, f)
    
    def tearDown(self):
        """Clean up temporary files."""
        # Remove temporary files
        if os.path.exists(self.model_path):
            os.remove(self.model_path)
        
        if os.path.exists(self.feature_columns_path):
            os.remove(self.feature_columns_path)
    
    def test_build_features_for_inference(self):
        """Test building features for inference."""
        # Build features
        features_df = build_features_for_inference(self.sales_data, self.feature_columns)
        
        # Check that features were built correctly
        self.assertEqual(set(features_df.columns), set(self.feature_columns + ['date']))
        self.assertEqual(len(features_df), 5)  # One row per day
    
    def test_model_prediction(self):
        """Test model prediction."""
        # Build features
        features_df = build_features_for_inference(self.sales_data, self.feature_columns)
        
        # Make predictions
        predictions = self.mock_model.predict(features_df[self.feature_columns])
        
        # Check predictions
        self.assertEqual(len(predictions), 5)  # One prediction per day
        self.assertTrue(np.all(predictions == 150.0))  # All predictions should be the mock value
        self.assertTrue(self.mock_model.predict_called)
        self.assertEqual(self.mock_model.predict_args.shape, (5, len(self.feature_columns)))
    
    def test_load_model_and_predict(self):
        """Test loading model from file and making predictions."""
        # Load model and feature columns
        with open(self.model_path, 'rb') as f:
            model = pickle.load(f)
        
        with open(self.feature_columns_path, 'rb') as f:
            feature_columns = pickle.load(f)
        
        # Build features
        features_df = build_features_for_inference(self.sales_data, feature_columns)
        
        # Make predictions
        predictions = model.predict(features_df[feature_columns])
        
        # Check predictions
        self.assertEqual(len(predictions), 5)  # One prediction per day
        self.assertTrue(np.all(predictions == 150.0))  # All predictions should be the mock value
    
    def test_prediction_with_future_dates(self):
        """Test making predictions for future dates."""
        # Create future dates
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        future_dates = [today + timedelta(days=i) for i in range(5)]
        
        # Create future sales data (empty amounts)
        future_sales = pd.DataFrame({
            'date': future_dates * 2,  # Repeat each date twice
            'category': ['Electronics', 'Clothing'] * 5,  # Alternate categories
            'amount': [0.0] * 10,  # Empty amounts
            'customer_id': [''] * 10,
            'transaction_id': [''] * 10
        })
        
        # Combine with historical data
        combined_sales = pd.concat([self.sales_data, future_sales]).sort_values('date').reset_index(drop=True)
        
        # Build features
        features_df = build_features_for_inference(combined_sales, self.feature_columns)
        
        # Filter to future dates
        future_features = features_df[features_df['date'] >= today]
        
        # Make predictions
        predictions = self.mock_model.predict(future_features[self.feature_columns])
        
        # Check predictions
        self.assertEqual(len(predictions), 5)  # One prediction per future day
        self.assertTrue(np.all(predictions == 150.0))  # All predictions should be the mock value
    
    def test_prediction_with_missing_features(self):
        """Test handling of missing features."""
        # Define a subset of feature columns
        subset_columns = self.feature_columns[:3]  # Only year, month, day
        
        # Try to build features with missing columns
        with self.assertRaises(ValueError):
            build_features_for_inference(self.sales_data, self.feature_columns, subset_columns)


if __name__ == '__main__':
    unittest.main()