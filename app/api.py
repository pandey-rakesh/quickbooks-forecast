"""
API endpoints for the QuickBooks Sales Forecasting API.

This module defines the FastAPI routes for the sales forecasting API,
including the `/predict-top-categories` endpoint.
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, date

from app.config import DEFAULT_FORECAST_DAYS, DEFAULT_TOP_CATEGORIES, API_PREFIX
from app.service import forecasting_service
from app.utils import setup_logger

# Set up logger
logger = setup_logger(__name__)

# Create API router
router = APIRouter(prefix=API_PREFIX)


# Define response models
class Period(BaseModel):
    start_date: str
    end_date: str
    days: int


class Category(BaseModel):
    category: str
    amount: float
    percentage: float


class PredictedCategory(Category):
    confidence: float = Field(..., description="Confidence score for the prediction")


class ModelInfo(BaseModel):
    model_type: str
    training_date: str
    feature_count: int


class HistoricalData(BaseModel):
    period: Period
    total_sales: float
    total_sales_formatted: str
    top_categories: List[Category]


class GrowthData(BaseModel):
    total_sales: float
    total_sales_formatted: str


class TopCategoriesPredictionResponse(BaseModel):
    period: Period
    total_predicted_sales: float
    total_predicted_sales_formatted: str
    predicted_top_categories: List[PredictedCategory]
    model_info: ModelInfo
    historical: Optional[HistoricalData] = None
    growth: Optional[GrowthData] = None


class HistoricalTopCategoriesResponse(BaseModel):
    period: Period
    total_sales: float
    total_sales_formatted: str
    top_categories: List[Category]
    data_points: int


class ModelInfoResponse(BaseModel):
    model_type: str
    training_date: str
    feature_count: int
    description: str
    is_loaded: bool


@router.get("/predict-top-categories", response_model=TopCategoriesPredictionResponse)
async def predict_top_categories(
    start_date: Optional[str] = Query(None, description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date in ISO format (YYYY-MM-DD)"),
    days: int = Query(DEFAULT_FORECAST_DAYS, description="Number of days to forecast"),
    top_n: int = Query(DEFAULT_TOP_CATEGORIES, description="Number of top categories to return"),
    include_historical: bool = Query(True, description="Include historical data for comparison")
):
    """
    Predict the top categories by sales amount for a future period.
    
    This endpoint uses the trained model to predict the top-selling categories
    for the specified date range. If no dates are provided, it predicts for the
    next 30 days by default.
    
    Args:
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        days: Number of days to forecast if start_date is not provided
        top_n: Number of top categories to return
        include_historical: Include historical data for comparison
        
    Returns:
        TopCategoriesPredictionResponse: Prediction results
    """
    try:
        logger.info(f"Predicting top {top_n} categories for period: {start_date} to {end_date} ({days} days)")
        
        result = forecasting_service.predict_top_categories(
            start_date=start_date,
            end_date=end_date,
            days=days,
            top_n=top_n,
            include_historical=include_historical
        )
        
        logger.info(f"Prediction successful, returning {len(result.get('predicted_top_categories', []))} categories")
        return result
    
    except Exception as e:
        logger.error(f"Error predicting top categories: {e}")
        raise HTTPException(status_code=500, detail=f"Error predicting top categories: {str(e)}")


@router.get("/historical-top-categories", response_model=HistoricalTopCategoriesResponse)
async def get_historical_top_categories(
    start_date: Optional[str] = Query(None, description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date in ISO format (YYYY-MM-DD)"),
    days: int = Query(DEFAULT_FORECAST_DAYS, description="Number of days to include"),
    top_n: int = Query(DEFAULT_TOP_CATEGORIES, description="Number of top categories to return")
):
    """
    Get the top categories by sales amount for a historical period.
    
    This endpoint retrieves historical sales data and returns the top-selling
    categories for the specified date range.
    
    Args:
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        days: Number of days to include if start_date is not provided
        top_n: Number of top categories to return
        
    Returns:
        HistoricalTopCategoriesResponse: Historical results
    """
    try:
        logger.info(f"Getting historical top {top_n} categories for period: {start_date} to {end_date} ({days} days)")
        
        result = forecasting_service.get_historical_top_categories(
            start_date=start_date,
            end_date=end_date,
            days=days,
            top_n=top_n
        )
        
        logger.info(f"Historical query successful, returning {len(result.get('top_categories', []))} categories")
        return result
    
    except Exception as e:
        logger.error(f"Error getting historical top categories: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting historical top categories: {str(e)}")


@router.get("/model-info", response_model=ModelInfoResponse)
async def get_model_info():
    """
    Get information about the loaded model.
    
    This endpoint returns metadata about the trained model being used for predictions.
    
    Returns:
        ModelInfoResponse: Model information
    """
    try:
        logger.info("Getting model info")
        
        result = forecasting_service.get_model_info()
        
        logger.info(f"Model info retrieved: {result.get('model_type', 'Unknown')}")
        return result
    
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")