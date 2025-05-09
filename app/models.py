"""
Data models for QuickBooks Sales Forecasting API.

This module defines the data models used for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class Period(BaseModel):
    """Date period model."""
    start_date: str
    end_date: str
    days: int

class CategorySales(BaseModel):
    """Category sales model."""
    category: str
    amount: float
    percentage: float
    confidence: Optional[float] = None

class ModelInfo(BaseModel):
    """Model information model."""
    model_type: str
    training_date: str
    feature_count: int

class PredictionResponse(BaseModel):
    """Response model for prediction endpoints."""
    period: Period
    total_predicted_sales: float
    total_predicted_sales_formatted: str
    predicted_top_categories: List[CategorySales]
    model_info: ModelInfo
    historical_data: Optional[Dict[str, Any]] = None

class HistoricalResponse(BaseModel):
    """Response model for historical endpoints."""
    period: Period
    total_historical_sales: float
    total_historical_sales_formatted: str
    historical_top_categories: List[CategorySales]

class TopCategoriesResponse(BaseModel):
    """Response model for top categories endpoint."""
    range: str
    start_date: str
    end_date: str
    top_categories: List[Dict[str, Any]]
