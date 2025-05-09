"""
Core business logic for the QuickBooks Sales Forecasting API.

This module provides the service layer that handles the business logic for
sales forecasting, including data loading, feature engineering, model inference,
and result processing.
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
import logging

from app.config import (
    MODEL_PATH, FEATURE_COLUMNS_PATH, MODEL_INFO_PATH,
    SALES_DATA_PATH, DEFAULT_FORECAST_DAYS, DEFAULT_TOP_CATEGORIES,
    CONFIDENCE_THRESHOLD, LAG_DAYS, ROLLING_WINDOWS
)
from app.utils import (
    setup_logger, parse_date_range, filter_dataframe_by_date,
    get_top_categories, format_currency, format_percentage,
    calculate_growth_rate, create_empty_dataframe_with_dates
)

# Import feature builder from model module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.features import FeatureBuilder, build_features_for_inference

# Set up logger
logger = setup_logger(__name__)


class ForecastingService:
    """
    Service for sales forecasting operations.
    
    This class handles loading the model, processing data, making predictions,
    and formatting results for the API.
    """
    
    def __init__(self):
        """
        Initialize the forecasting service.
        
        Loads the trained model, feature columns, and model info.
        """
        self.model = None
        self.feature_columns = None
        self.model_info = None
        self.feature_builder = FeatureBuilder(lag_days=LAG_DAYS, rolling_windows=ROLLING_WINDOWS)
        
        # Load model and related artifacts
        self._load_model()
    
    def _load_model(self):
        """
        Load the trained model and related artifacts.
        
        Raises:
            FileNotFoundError: If model files are not found
        """
        try:
            # Load model
            with open(MODEL_PATH, 'rb') as f:
                self.model = pickle.load(f)
            
            # Load feature columns
            with open(FEATURE_COLUMNS_PATH, 'rb') as f:
                self.feature_columns = pickle.load(f)
            
            # Load model info
            with open(MODEL_INFO_PATH, 'r') as f:
                self.model_info = json.load(f)
            
            logger.info(f"Loaded model: {self.model_info.get('model_type', 'Unknown')}")
            logger.info(f"Feature count: {len(self.feature_columns)}")
        
        except FileNotFoundError as e:
            logger.error(f"Model files not found: {e}")
            # Create empty model info for graceful degradation
            self.model_info = {
                'model_type': 'None',
                'feature_count': 0,
                'features': [],
                'training_date': datetime.now().strftime('%Y-%m-%d'),
                'description': 'Model not loaded'
            }
            raise
    
    def load_sales_data(self) -> pd.DataFrame:
        """
        Load the sales data from the data file.
        
        Returns:
            DataFrame: Sales data
        """
        try:
            sales_df = pd.read_csv(SALES_DATA_PATH)
            
            # Ensure date is datetime
            sales_df['date'] = pd.to_datetime(sales_df['date'])
            
            logger.info(f"Loaded sales data with shape: {sales_df.shape}")
            return sales_df
        
        except Exception as e:
            logger.error(f"Error loading sales data: {e}")
            # Return empty DataFrame with correct columns
            return pd.DataFrame(columns=['date', 'category', 'amount', 'customer_id', 'transaction_id'])
    
    def get_historical_top_categories(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: int = DEFAULT_FORECAST_DAYS,
        top_n: int = DEFAULT_TOP_CATEGORIES
    ) -> Dict[str, Any]:
        """
        Get the top categories by sales amount for a historical period.
        
        Args:
            start_date (str, optional): Start date in ISO format (YYYY-MM-DD)
            end_date (str, optional): End date in ISO format (YYYY-MM-DD)
            days (int): Number of days to include if start_date is not provided
            top_n (int): Number of top categories to return
            
        Returns:
            dict: Results with top categories and metadata
        """
        # Parse date range
        start_dt, end_dt = parse_date_range(start_date, end_date, days)
        
        # Load sales data
        sales_df = self.load_sales_data()
        
        # Filter by date range
        filtered_df = filter_dataframe_by_date(sales_df, start_dt, end_dt)
        
        # Get top categories
        top_categories = get_top_categories(filtered_df, top_n)
        
        # Calculate total sales
        total_sales = filtered_df['amount'].sum()
        
        # Prepare result
        result = {
            'period': {
                'start_date': start_dt.strftime('%Y-%m-%d'),
                'end_date': end_dt.strftime('%Y-%m-%d'),
                'days': (end_dt - start_dt).days + 1
            },
            'total_sales': float(total_sales),
            'total_sales_formatted': format_currency(total_sales),
            'top_categories': top_categories,
            'data_points': len(filtered_df)
        }
        
        return result
    
    def predict_top_categories(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: int = DEFAULT_FORECAST_DAYS,
        top_n: int = DEFAULT_TOP_CATEGORIES,
        include_historical: bool = True
    ) -> Dict[str, Any]:
        """
        Predict the top categories by sales amount for a future period.
        
        Args:
            start_date (str, optional): Start date in ISO format (YYYY-MM-DD)
            end_date (str, optional): End date in ISO format (YYYY-MM-DD)
            days (int): Number of days to include if start_date is not provided
            top_n (int): Number of top categories to return
            include_historical (bool): Whether to include historical data for comparison
            
        Returns:
            dict: Results with predicted top categories and metadata
        """
        # Parse date range for prediction period
        start_dt, end_dt = parse_date_range(start_date, end_date, days)
        
        # Load sales data
        sales_df = self.load_sales_data()
        
        # Check if model is loaded
        if self.model is None:
            logger.warning("Model not loaded, returning historical data only")
            return self.get_historical_top_categories(
                start_date=start_dt.strftime('%Y-%m-%d'),
                end_date=end_dt.strftime('%Y-%m-%d'),
                top_n=top_n
            )
        
        # Get unique categories from sales data
        categories = sales_df['category'].unique().tolist()
        
        # Create empty DataFrame for prediction period with all categories
        prediction_df = create_empty_dataframe_with_dates(start_dt, end_dt, categories)
        
        # Combine historical data with empty prediction data
        combined_df = pd.concat([sales_df, prediction_df]).sort_values('date').reset_index(drop=True)
        
        try:
            # Build features for prediction
            features_df = build_features_for_inference(combined_df, self.feature_columns)
            
            # Filter features to prediction period
            pred_features = filter_dataframe_by_date(features_df, start_dt, end_dt)
            
            # Make predictions
            predictions = self.model.predict(pred_features[self.feature_columns])
            
            # Add predictions to DataFrame
            pred_features['predicted_amount'] = predictions
            
            # Group by category and sum predicted amounts
            category_totals = pred_features.groupby('category')['predicted_amount'].sum().reset_index()
            
            # Sort by predicted amount and take top N
            top_categories = category_totals.sort_values('predicted_amount', ascending=False).head(top_n)
            
            # Convert to list of dictionaries
            predicted_categories = []
            total_predicted = category_totals['predicted_amount'].sum()
            
            for _, row in top_categories.iterrows():
                predicted_categories.append({
                    'category': row['category'],
                    'amount': float(row['predicted_amount']),
                    'percentage': float(row['predicted_amount'] / total_predicted * 100),
                    'confidence': 0.9  # Placeholder for confidence score
                })
            
            # Prepare result
            result = {
                'period': {
                    'start_date': start_dt.strftime('%Y-%m-%d'),
                    'end_date': end_dt.strftime('%Y-%m-%d'),
                    'days': (end_dt - start_dt).days + 1
                },
                'total_predicted_sales': float(total_predicted),
                'total_predicted_sales_formatted': format_currency(total_predicted),
                'predicted_top_categories': predicted_categories,
                'model_info': {
                    'model_type': self.model_info.get('model_type', 'Unknown'),
                    'training_date': self.model_info.get('training_date', 'Unknown'),
                    'feature_count': self.model_info.get('feature_count', 0)
                }
            }
            
            # Include historical data if requested
            if include_historical:
                # Get historical period of same length
                hist_start_dt = start_dt - timedelta(days=days)
                hist_end_dt = end_dt - timedelta(days=days)
                
                # Get historical top categories
                historical_result = self.get_historical_top_categories(
                    start_date=hist_start_dt.strftime('%Y-%m-%d'),
                    end_date=hist_end_dt.strftime('%Y-%m-%d'),
                    top_n=top_n
                )
                
                # Add historical data to result
                result['historical'] = {
                    'period': historical_result['period'],
                    'total_sales': historical_result['total_sales'],
                    'total_sales_formatted': historical_result['total_sales_formatted'],
                    'top_categories': historical_result['top_categories']
                }
                
                # Calculate growth rates
                result['growth'] = {
                    'total_sales': calculate_growth_rate(
                        result['total_predicted_sales'],
                        historical_result['total_sales']
                    ),
                    'total_sales_formatted': format_percentage(calculate_growth_rate(
                        result['total_predicted_sales'],
                        historical_result['total_sales']
                    ))
                }
            
            return result
        
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            # Fall back to historical data
            return self.get_historical_top_categories(
                start_date=start_dt.strftime('%Y-%m-%d'),
                end_date=end_dt.strftime('%Y-%m-%d'),
                top_n=top_n
            )
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            dict: Model information
        """
        return {
            'model_type': self.model_info.get('model_type', 'Unknown'),
            'training_date': self.model_info.get('training_date', 'Unknown'),
            'feature_count': self.model_info.get('feature_count', 0),
            'description': self.model_info.get('description', ''),
            'is_loaded': self.model is not None
        }


# Create singleton instance
forecasting_service = ForecastingService()