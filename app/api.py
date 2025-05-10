"""
API endpoints for QuickBooks Sales Forecasting.

This module defines the API endpoints for predicting top sales categories
and retrieving historical data.
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional, List, Dict, Any
import json
import logging
from datetime import datetime, timedelta
import pandas as pd

from app.service import ForecastService
from app.utils import parse_date_range, format_currency, format_percentage
from app.config import DEFAULT_FORECAST_DAYS, DEFAULT_TOP_CATEGORIES, MODEL_INFO_PATH

# Create router
router = APIRouter()

# Create service instance
forecast_service = ForecastService()


@router.get("/predict-top-categories")
async def predict_top_categories(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: int = DEFAULT_FORECAST_DAYS,
        top_n: int = DEFAULT_TOP_CATEGORIES,
        include_historical: bool = False
):
    """
    Predict the top categories by sales amount for a future period.

    Args:
        start_date (str, optional): Start date in ISO format (YYYY-MM-DD)
        end_date (str, optional): End date in ISO format (YYYY-MM-DD)
        days (int, optional): Number of days to forecast if start_date is not provided
        top_n (int, optional): Number of top categories to return
        include_historical (bool, optional): Include historical data for comparison

    Returns:
        dict: Prediction results including top categories and model info
    """
    try:
        # Parse and validate date range
        start_dt, end_dt = parse_date_range(start_date, end_date, days)

        # Get predictions from service
        predictions = forecast_service.predict_top_categories(
            start_date=start_dt,
            end_date=end_dt,
            top_n=top_n,
            include_historical=include_historical
        )

        return predictions
    except ValueError as e:
        # Handle specific ValueError exceptions from the service
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle any other unexpected exceptions
        logging.error(f"Error in predict-top-categories endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/historical-top-categories")
async def historical_top_categories(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: int = DEFAULT_FORECAST_DAYS,
        top_n: int = DEFAULT_TOP_CATEGORIES
):
    """
    Get the top categories by sales amount for a historical period.

    Args:
        start_date (str, optional): Start date in ISO format (YYYY-MM-DD)
        end_date (str, optional): End date in ISO format (YYYY-MM-DD)
        days (int, optional): Number of days to include if start_date is not provided
        top_n (int, optional): Number of top categories to return

    Returns:
        dict: Historical top categories
    """
    try:
        # Parse and validate date range
        start_dt, end_dt = parse_date_range(start_date, end_date, days)

        # Get historical data from service
        historical = forecast_service.get_historical_top_categories(
            start_date=start_dt,
            end_date=end_dt,
            top_n=top_n
        )

        return historical
    except ValueError as e:
        # Handle specific ValueError exceptions from the service
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle any other unexpected exceptions
        logging.error(f"Error in historical-top-categories endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/model-info")
async def model_info():
    """
    Get information about the loaded model.

    Returns:
        dict: Model information
    """
    try:
        model_info = forecast_service.get_model_info()
        return model_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model info: {str(e)}")


@router.get("/categories/top")
async def get_top_categories_for_range(
        range: str = Query("month", description="Time range (week, month, quarter, year, custom)"),
        start_date: Optional[str] = Query(None, description="Start date for custom range (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date for custom range (YYYY-MM-DD)"),
        top_n: int = Query(DEFAULT_TOP_CATEGORIES, description="Number of top categories to return")
):
    """
    Get top-N predicted categories for a time frame.

    Args:
        range (str, optional): Time range (week, month, quarter, year, custom). Defaults to "month".
        start_date (str, optional): Start date for custom range (YYYY-MM-DD)
        end_date (str, optional): End date for custom range (YYYY-MM-DD)
        top_n (int, optional): Number of top categories to return

    Returns:
        dict: Top categories for the specified time range
    """
    try:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Calculate date range based on specified time frame
        if range == "week":
            start_dt = today
            end_dt = today + timedelta(days=6)
        elif range == "month":
            # Get the first day of next month
            if today.month == 12:
                next_month = datetime(today.year + 1, 1, 1)
            else:
                next_month = datetime(today.year, today.month + 1, 1)

            # Calculate days in current month
            days_in_month = (next_month - today).days

            start_dt = today
            end_dt = today + timedelta(days=days_in_month - 1)
        elif range == "quarter":
            # Calculate a quarter (3 months) from today
            month = today.month
            year = today.year

            # Calculate the end month and year
            end_month = month + 3
            end_year = year
            if end_month > 12:
                end_month -= 12
                end_year += 1

            # Get the first day of the month after the quarter ends
            if end_month == 12:
                quarter_end = datetime(end_year + 1, 1, 1)
            else:
                quarter_end = datetime(end_year, end_month + 1, 1)

            # Calculate days in the quarter
            days_in_quarter = (quarter_end - today).days

            start_dt = today
            end_dt = today + timedelta(days=days_in_quarter - 1)
        elif range == "year":
            # Get the first day of next year
            next_year = datetime(today.year + 1, 1, 1)

            # Calculate days in current year
            days_in_year = (next_year - today).days

            start_dt = today
            end_dt = today + timedelta(days=days_in_year - 1)
        elif range == "custom":
            if not start_date or not end_date:
                raise HTTPException(
                    status_code=400,
                    detail="start_date and end_date are required for custom range"
                )
            start_dt, end_dt = parse_date_range(start_date, end_date)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid range. Must be one of: week, month, quarter, year, custom"
            )

        # Get predictions for the calculated date range
        predictions = forecast_service.predict_top_categories(
            start_date=start_dt,
            end_date=end_dt,
            top_n=top_n
        )

        # Format response
        response = {
            "range": range,
            "start_date": start_dt.strftime("%Y-%m-%d"),
            "end_date": end_dt.strftime("%Y-%m-%d"),
            "top_categories": [
                {
                    "category": item["category"],
                    "revenue": item["amount"]
                }
                for item in predictions["predicted_top_categories"]
            ]
        }

        return response
    except ValueError as e:
        # Handle specific ValueError exceptions from the service
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle any other unexpected exceptions
        logging.error(f"Error in categories/top endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/categories/time-series-plot")
async def time_series_plot(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: int = DEFAULT_FORECAST_DAYS,
        top_n: int = DEFAULT_TOP_CATEGORIES,
        historical_days: int = 180
):
    """
    Generate time series data for top N categories showing historical and predicted data.

    Args:
        start_date (str, optional): Start date for prediction in ISO format (YYYY-MM-DD)
        end_date (str, optional): End date for prediction in ISO format (YYYY-MM-DD)
        days (int, optional): Number of days to forecast if start_date is not provided
        top_n (int, optional): Number of top categories to show
        historical_days (int, optional): Number of days of historical data to include

    Returns:
        dict: Time series data for historical and predicted periods
    """
    try:
        # Parse and validate date range for prediction period
        start_dt, end_dt = parse_date_range(start_date, end_date, days)

        # Get time series data from service
        time_series_data = forecast_service.get_time_series_data(
            start_date=start_dt,
            end_date=end_dt,
            top_n=top_n,
            historical_days=historical_days
        )

        return time_series_data

    except ValueError as e:
        # Handle specific ValueError exceptions from the service
        logging.error(f"Value error in time-series-plot endpoint: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle any other unexpected exceptions
        logging.error(f"Error in time-series-plot endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
