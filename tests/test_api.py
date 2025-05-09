"""
Unit tests for the API endpoints.

This module contains tests for the FastAPI endpoints in the app.api module.
"""

import unittest
from fastapi.testclient import TestClient
import json
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add parent directory to path to allow importing from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import app
from app.service import ForecastingService
from app.config import API_PREFIX


class TestAPI(unittest.TestCase):
    """Test cases for the API endpoints."""
    
    def setUp(self):
        """Set up test client and mock data."""
        self.client = TestClient(app)
        
        # Mock response data for historical top categories
        self.mock_historical_response = {
            "period": {
                "start_date": "2023-01-01",
                "end_date": "2023-01-31",
                "days": 31
            },
            "total_sales": 10000.0,
            "total_sales_formatted": "$10,000.00",
            "top_categories": [
                {
                    "category": "Electronics",
                    "amount": 5000.0,
                    "percentage": 50.0
                },
                {
                    "category": "Clothing",
                    "amount": 3000.0,
                    "percentage": 30.0
                },
                {
                    "category": "Food",
                    "amount": 2000.0,
                    "percentage": 20.0
                }
            ],
            "data_points": 100
        }
        
        # Mock response data for predicted top categories
        self.mock_prediction_response = {
            "period": {
                "start_date": "2023-02-01",
                "end_date": "2023-02-28",
                "days": 28
            },
            "total_predicted_sales": 12000.0,
            "total_predicted_sales_formatted": "$12,000.00",
            "predicted_top_categories": [
                {
                    "category": "Electronics",
                    "amount": 6000.0,
                    "percentage": 50.0,
                    "confidence": 0.9
                },
                {
                    "category": "Clothing",
                    "amount": 3600.0,
                    "percentage": 30.0,
                    "confidence": 0.85
                },
                {
                    "category": "Food",
                    "amount": 2400.0,
                    "percentage": 20.0,
                    "confidence": 0.8
                }
            ],
            "model_info": {
                "model_type": "XGBRegressor",
                "training_date": "2023-01-15",
                "feature_count": 20
            },
            "historical": {
                "period": {
                    "start_date": "2023-01-01",
                    "end_date": "2023-01-31",
                    "days": 31
                },
                "total_sales": 10000.0,
                "total_sales_formatted": "$10,000.00",
                "top_categories": [
                    {
                        "category": "Electronics",
                        "amount": 5000.0,
                        "percentage": 50.0
                    },
                    {
                        "category": "Clothing",
                        "amount": 3000.0,
                        "percentage": 30.0
                    },
                    {
                        "category": "Food",
                        "amount": 2000.0,
                        "percentage": 20.0
                    }
                ]
            },
            "growth": {
                "total_sales": 20.0,
                "total_sales_formatted": "20.00%"
            }
        }
        
        # Mock response data for model info
        self.mock_model_info_response = {
            "model_type": "XGBRegressor",
            "training_date": "2023-01-15",
            "feature_count": 20,
            "description": "XGBoost model for QuickBooks sales forecasting",
            "is_loaded": True
        }
    
    @patch('app.service.forecasting_service.get_historical_top_categories')
    def test_get_historical_top_categories(self, mock_get_historical):
        """Test the historical-top-categories endpoint."""
        # Set up mock
        mock_get_historical.return_value = self.mock_historical_response
        
        # Make request
        response = self.client.get(f"{API_PREFIX}/historical-top-categories")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.mock_historical_response)
        
        # Check that service method was called
        mock_get_historical.assert_called_once()
    
    @patch('app.service.forecasting_service.get_historical_top_categories')
    def test_get_historical_top_categories_with_params(self, mock_get_historical):
        """Test the historical-top-categories endpoint with parameters."""
        # Set up mock
        mock_get_historical.return_value = self.mock_historical_response
        
        # Make request with parameters
        response = self.client.get(
            f"{API_PREFIX}/historical-top-categories",
            params={
                "start_date": "2023-01-01",
                "end_date": "2023-01-31",
                "days": 31,
                "top_n": 3
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.mock_historical_response)
        
        # Check that service method was called with correct parameters
        mock_get_historical.assert_called_once_with(
            start_date="2023-01-01",
            end_date="2023-01-31",
            days=31,
            top_n=3
        )
    
    @patch('app.service.forecasting_service.predict_top_categories')
    def test_predict_top_categories(self, mock_predict):
        """Test the predict-top-categories endpoint."""
        # Set up mock
        mock_predict.return_value = self.mock_prediction_response
        
        # Make request
        response = self.client.get(f"{API_PREFIX}/predict-top-categories")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.mock_prediction_response)
        
        # Check that service method was called
        mock_predict.assert_called_once()
    
    @patch('app.service.forecasting_service.predict_top_categories')
    def test_predict_top_categories_with_params(self, mock_predict):
        """Test the predict-top-categories endpoint with parameters."""
        # Set up mock
        mock_predict.return_value = self.mock_prediction_response
        
        # Make request with parameters
        response = self.client.get(
            f"{API_PREFIX}/predict-top-categories",
            params={
                "start_date": "2023-02-01",
                "end_date": "2023-02-28",
                "days": 28,
                "top_n": 3,
                "include_historical": True
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.mock_prediction_response)
        
        # Check that service method was called with correct parameters
        mock_predict.assert_called_once_with(
            start_date="2023-02-01",
            end_date="2023-02-28",
            days=28,
            top_n=3,
            include_historical=True
        )
    
    @patch('app.service.forecasting_service.get_model_info')
    def test_get_model_info(self, mock_get_model_info):
        """Test the model-info endpoint."""
        # Set up mock
        mock_get_model_info.return_value = self.mock_model_info_response
        
        # Make request
        response = self.client.get(f"{API_PREFIX}/model-info")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.mock_model_info_response)
        
        # Check that service method was called
        mock_get_model_info.assert_called_once()
    
    @patch('app.service.forecasting_service.get_historical_top_categories')
    def test_get_historical_top_categories_error(self, mock_get_historical):
        """Test error handling in the historical-top-categories endpoint."""
        # Set up mock to raise an exception
        mock_get_historical.side_effect = Exception("Test error")
        
        # Make request
        response = self.client.get(f"{API_PREFIX}/historical-top-categories")
        
        # Check response
        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())
        self.assertIn("Test error", response.json()["detail"])
    
    @patch('app.service.forecasting_service.predict_top_categories')
    def test_predict_top_categories_error(self, mock_predict):
        """Test error handling in the predict-top-categories endpoint."""
        # Set up mock to raise an exception
        mock_predict.side_effect = Exception("Test error")
        
        # Make request
        response = self.client.get(f"{API_PREFIX}/predict-top-categories")
        
        # Check response
        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())
        self.assertIn("Test error", response.json()["detail"])
    
    def test_health_check(self):
        """Test the health check endpoint."""
        # Make request
        response = self.client.get("/health")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
    
    def test_root(self):
        """Test the root endpoint."""
        # Make request
        response = self.client.get("/")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertIn("documentation", response.json())


if __name__ == '__main__':
    unittest.main()