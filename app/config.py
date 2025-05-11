"""
Central configuration for the QuickBooks Sales Forecasting API.

This module contains configuration settings for paths, thresholds, and other parameters
used throughout the application.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'model')

# Model files
MODEL_PATH = os.path.join(MODEL_DIR, 'model.pkl')
FEATURE_COLUMNS_PATH = os.path.join(MODEL_DIR, 'feature_columns.pkl')
MODEL_INFO_PATH = os.path.join(MODEL_DIR, 'model_info.json')

# Data files
SALES_DATA_PATH = os.path.join(DATA_DIR, 'raw', 'sales.csv')
ENGINEERED_FEATURES_PATH = os.path.join(DATA_DIR, 'processed', 'sales_engineered_features.csv')

# API settings
API_TITLE = "QuickBooks Sales Forecasting API"
API_DESCRIPTION = "API for predicting top-selling categories based on historical sales data"
API_VERSION = "1.0.0"
API_PREFIX = "/api/v1"

# Prediction settings
DEFAULT_FORECAST_DAYS = 30
DEFAULT_TOP_CATEGORIES = 5

# Feature engineering settings
LAG_DAYS = [1, 7, 30]  # Days to lag for creating lag features
ROLLING_WINDOWS = [7, 14, 28]  # Window sizes for rolling statistics

# Cache settings
CACHE_EXPIRATION = 3600  # Cache expiration time in seconds (1 hour)

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
