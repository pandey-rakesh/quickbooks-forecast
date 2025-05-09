"""
Unit tests for the feature builder module.

This module contains tests for the FeatureBuilder class and related functions
in the model.features module.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to allow importing from model
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.features import FeatureBuilder, build_features_for_inference


class TestFeatureBuilder(unittest.TestCase):
    """Test cases for the FeatureBuilder class."""
    
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
        
        # Create feature builder
        self.feature_builder = FeatureBuilder(lag_days=[1, 2], rolling_windows=[2, 3])
    
    def test_prepare_data(self):
        """Test prepare_data method."""
        # Test with datetime column
        result = self.feature_builder.prepare_data(self.sales_data)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['date']))
        
        # Test with string column
        sales_data_str = self.sales_data.copy()
        sales_data_str['date'] = sales_data_str['date'].astype(str)
        result = self.feature_builder.prepare_data(sales_data_str)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['date']))
    
    def test_create_time_features(self):
        """Test create_time_features method."""
        result = self.feature_builder.create_time_features(self.sales_data)
        
        # Check that time features were created
        self.assertIn('year', result.columns)
        self.assertIn('month', result.columns)
        self.assertIn('day', result.columns)
        self.assertIn('day_of_week', result.columns)
        self.assertIn('is_weekend', result.columns)
        self.assertIn('quarter', result.columns)
        
        # Check values for first row
        first_row = result.iloc[0]
        self.assertEqual(first_row['year'], 2023)
        self.assertEqual(first_row['month'], 1)
        self.assertEqual(first_row['day'], 1)
        # January 1, 2023 was a Sunday (day_of_week = 6)
        self.assertEqual(first_row['day_of_week'], 6)
        self.assertEqual(first_row['is_weekend'], 1)
        self.assertEqual(first_row['quarter'], 1)
    
    def test_create_daily_aggregates(self):
        """Test create_daily_aggregates method."""
        result = self.feature_builder.create_daily_aggregates(self.sales_data)
        
        # Check that daily aggregates were created
        self.assertIn('date', result.columns)
        self.assertIn('total_sales', result.columns)
        self.assertIn('avg_transaction', result.columns)
        self.assertIn('transaction_count', result.columns)
        self.assertIn('unique_categories', result.columns)
        
        # Check number of rows (should be one per day)
        self.assertEqual(len(result), 5)
        
        # Check values for first day
        first_day = result[result['date'] == pd.Timestamp('2023-01-01')]
        self.assertEqual(first_day['total_sales'].values[0], 150.0)  # 100 + 50
        self.assertEqual(first_day['transaction_count'].values[0], 2)
        self.assertEqual(first_day['unique_categories'].values[0], 2)
    
    def test_add_lag_features(self):
        """Test add_lag_features method."""
        # Create daily aggregates
        daily_df = self.feature_builder.create_daily_aggregates(self.sales_data)
        
        # Add lag features
        result = self.feature_builder.add_lag_features(daily_df, ['total_sales'])
        
        # Check that lag features were created
        self.assertIn('total_sales_lag_1d', result.columns)
        self.assertIn('total_sales_lag_2d', result.columns)
        
        # Check values (day 3 should have lag 1 = day 2, lag 2 = day 1)
        day3 = result[result['date'] == pd.Timestamp('2023-01-03')]
        day2_sales = daily_df[daily_df['date'] == pd.Timestamp('2023-01-02')]['total_sales'].values[0]
        day1_sales = daily_df[daily_df['date'] == pd.Timestamp('2023-01-01')]['total_sales'].values[0]
        
        self.assertEqual(day3['total_sales_lag_1d'].values[0], day2_sales)
        self.assertEqual(day3['total_sales_lag_2d'].values[0], day1_sales)
    
    def test_add_rolling_features(self):
        """Test add_rolling_features method."""
        # Create daily aggregates
        daily_df = self.feature_builder.create_daily_aggregates(self.sales_data)
        
        # Add rolling features
        result = self.feature_builder.add_rolling_features(daily_df, ['total_sales'])
        
        # Check that rolling features were created
        self.assertIn('total_sales_rolling_2d_mean', result.columns)
        self.assertIn('total_sales_rolling_2d_std', result.columns)
        self.assertIn('total_sales_rolling_3d_mean', result.columns)
        self.assertIn('total_sales_rolling_3d_std', result.columns)
        
        # Check values for day 3 (should include days 1-3 for 3d window)
        day3 = result[result['date'] == pd.Timestamp('2023-01-03')]
        day1to3_sales = daily_df[daily_df['date'].isin([
            pd.Timestamp('2023-01-01'),
            pd.Timestamp('2023-01-02'),
            pd.Timestamp('2023-01-03')
        ])]['total_sales']
        
        expected_mean = day1to3_sales.mean()
        expected_std = day1to3_sales.std()
        
        self.assertAlmostEqual(day3['total_sales_rolling_3d_mean'].values[0], expected_mean)
        self.assertAlmostEqual(day3['total_sales_rolling_3d_std'].values[0], expected_std)
    
    def test_create_category_features(self):
        """Test create_category_features method."""
        result = self.feature_builder.create_category_features(self.sales_data)
        
        # Check that category features were created
        self.assertIn('date', result.columns)
        self.assertIn('Electronics', result.columns)
        self.assertIn('Clothing', result.columns)
        self.assertIn('Food', result.columns)
        self.assertIn('Home', result.columns)
        
        # Check values for first day
        first_day = result[result['date'] == pd.Timestamp('2023-01-01')]
        self.assertEqual(first_day['Electronics'].values[0], 100.0)
        self.assertEqual(first_day['Clothing'].values[0], 50.0)
        self.assertTrue(pd.isna(first_day['Food'].values[0]) or first_day['Food'].values[0] == 0)
        self.assertTrue(pd.isna(first_day['Home'].values[0]) or first_day['Home'].values[0] == 0)
    
    def test_build_features(self):
        """Test build_features method."""
        result = self.feature_builder.build_features(self.sales_data)
        
        # Check that all feature types are present
        # Time features
        self.assertIn('year', result.columns)
        self.assertIn('month', result.columns)
        self.assertIn('day', result.columns)
        
        # Lag features
        self.assertIn('total_sales_lag_1d', result.columns)
        self.assertIn('total_sales_lag_2d', result.columns)
        
        # Rolling features
        self.assertIn('total_sales_rolling_2d_mean', result.columns)
        self.assertIn('total_sales_rolling_3d_mean', result.columns)
        
        # Category features
        self.assertIn('Electronics', result.columns)
        self.assertIn('Clothing', result.columns)
        
        # Check number of rows (should be one per day)
        self.assertEqual(len(result), 5)
    
    def test_build_features_for_inference(self):
        """Test build_features_for_inference function."""
        # Define feature columns
        feature_cols = [
            'year', 'month', 'day', 'day_of_week', 'is_weekend',
            'total_sales_lag_1d', 'Electronics', 'Clothing'
        ]
        
        # Build features
        result = build_features_for_inference(self.sales_data, feature_cols)
        
        # Check that only requested features are present
        self.assertEqual(set(result.columns), set(feature_cols + ['date']))
        
        # Check that all rows are present
        self.assertEqual(len(result), 5)


if __name__ == '__main__':
    unittest.main()