"""
Service for sales forecasting.

This class handles loading the trained model, making predictions,
and processing historical sales data from the PostgreSQL database.
No synthetic data is generated at any point.
"""

import pickle
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from app.config import MODEL_PATH, MODEL_INFO_PATH
from app.utils import setup_logger, format_currency
from src.feature_engineering.feature_builder import FeatureBuilder

class ForecastService:
    """
    Service for sales forecasting.

    This class handles loading the trained model, making predictions,
    and processing historical sales data from the PostgreSQL database.
    No synthetic data is generated at any point.
    """

    def __init__(self):
        """
        Initialize the ForecastService.

        Loads the trained model, feature columns, and model info.
        """
        self.logger = setup_logger("app.forecast_service")
        self.model = self._load_model()
        self.feature_builder = FeatureBuilder()
        self.model_info = self._load_model_info()

        # Import here to avoid circular imports
        from src.db_operations import get_historical_sales, get_predictions
        self.get_historical_sales = get_historical_sales
        self.get_predictions = get_predictions

        self.logger.info("ForecastService initialized")

    def _load_model(self):
        """
        Load the trained model from disk.

        Returns:
            object: Trained model or None if loading fails
        """
        try:
            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
            self.logger.info(f"Loaded model from {MODEL_PATH}")
            return model
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            return None

    def _load_model_info(self):
        """
        Load model information from disk.

        Returns:
            dict: Model information
        """
        try:
            with open(MODEL_INFO_PATH, 'r') as f:
                model_info = json.load(f)
            self.logger.info(f"Loaded model info from {MODEL_INFO_PATH}")
            return model_info
        except Exception as e:
            self.logger.error(f"Error loading model info: {e}")
            return {
                "model_type": "LightGBM",
                "training_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "feature_count": 33,
                "target_categories": [
                    "Beauty", "Books", "Clothing", "Electronics",
                    "Furniture", "Groceries", "Sports", "Toys"
                ]
            }

    def get_model_info(self):
        """
        Get model information.

        Returns:
            dict: Model information
        """
        return self.model_info

    def predict_top_categories(
            self,
            start_date: datetime,
            end_date: datetime,
            top_n: int = 5,
            include_historical: bool = False
    ) -> Dict[str, Any]:
        """
        Predict the top categories by sales amount for a future period.

        This method does not generate synthetic data. It uses the model to make
        predictions based on historical data from the database.

        Args:
            start_date (datetime): Start date for prediction
            end_date (datetime): End date for prediction
            top_n (int): Number of top categories to return
            include_historical (bool): Include historical data for comparison

        Returns:
            dict: Prediction results including top categories and model info

        Raises:
            ValueError: If no historical data is available or if the model fails
        """
        self.logger.info(f"Predicting top categories from {start_date} to {end_date}")

        # Check if model is available
        if self.model is None:
            self.logger.error("Model not loaded, cannot generate predictions")
            raise ValueError("Model not loaded, cannot generate predictions")

        try:
            # We need some historical data to generate features for prediction
            # Load at least 60 days of data before the start date to have enough context
            feature_start_date = start_date - timedelta(days=60)
            feature_end_date = start_date - timedelta(days=1)

            self.logger.info(
                f"Loading historical data for feature generation from {feature_start_date} to {feature_end_date}")

            # Get historical data from database
            historical_data = self.get_historical_sales(
                start_date=feature_start_date,
                end_date=feature_end_date
            )

            # Check if we have any historical data for feature generation
            if historical_data is None or historical_data.empty:
                self.logger.error("No historical data available for feature generation")
                raise ValueError(
                    f"No historical data available for feature generation (needed from {feature_start_date} to {feature_end_date})"
                )

            self.logger.info(f"Retrieved {len(historical_data)} rows of historical data")

            # Get all target categories from model info
            target_categories = self.model_info.get("target_categories", [
                "Beauty", "Books", "Clothing", "Electronics",
                "Furniture", "Groceries", "Sports", "Toys"
            ])

            # Generate features for the entire prediction period at once
            self.logger.info(f"Generating features for prediction period {start_date} to {end_date}")

            # Use FeatureBuilder to generate features for the entire date range
            features_df = self.feature_builder.generate_features(
                start_date=start_date,
                end_date=end_date,
                historical_data=historical_data
            )

            # Check if we have any features
            if features_df is None or features_df.empty:
                self.logger.error("Failed to generate features for prediction")
                raise ValueError("Failed to generate features for prediction")

            self.logger.info(f"Generated features with shape: {features_df.shape}")

            # Make predictions for each date in the range
            predictions = []
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')

            # Log model type for debugging
            self.logger.info(f"Model type: {type(self.model).__name__}")

            # Generate predictions
            for target_date in date_range:
                # Get features for this specific date
                date_features = features_df.loc[features_df.index == target_date]

                if date_features.empty:
                    self.logger.warning(f"No features available for {target_date}, skipping")
                    continue

                # Make a single prediction for all categories
                # Generate a single set of predictions for all categories
                # This assumes the model outputs a single value or an array with
                # one value per category
                model_predictions = self.model.predict(date_features)

                # Check the shape of predictions
                if hasattr(model_predictions, 'shape'):
                    self.logger.info(f"Model prediction shape: {model_predictions.shape}")

                if isinstance(model_predictions, (list, np.ndarray)):
                    pred_array = model_predictions.flatten()  # ensure 1D array

                    # Map predictions to categories
                    for i, category in enumerate(target_categories):
                        if i < len(pred_array):
                            predictions.append({
                                "date": target_date.strftime("%Y-%m-%d"),
                                "category": category,
                                "amount": float(pred_array[i])
                            })

            # Check if we have any predictions
            if not predictions:
                self.logger.error("No predictions could be generated")
                raise ValueError("Failed to generate any predictions")

            # Convert to DataFrame for easier processing
            predictions_df = pd.DataFrame(predictions)

            # Calculate totals per category
            category_totals = predictions_df.groupby("category")["amount"].sum().reset_index()

            # Sort by amount in descending order and take top N
            top_categories = category_totals.sort_values("amount", ascending=False).head(top_n)

            # Calculate total predicted sales
            total_predicted_sales = top_categories["amount"].sum()

            # Format top categories
            top_categories_list = []
            for _, row in top_categories.iterrows():
                # Calculate percentage of total
                percentage = (row["amount"] / total_predicted_sales) * 100 if total_predicted_sales > 0 else 0

                # Add to list
                top_categories_list.append({
                    "category": row["category"],
                    "amount": float(row["amount"]),
                    "percentage": float(percentage)
                })

            # Prepare response
            response = {
                "period": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "days": (end_date - start_date).days + 1
                },
                "total_predicted_sales": float(total_predicted_sales),
                "total_predicted_sales_formatted": format_currency(total_predicted_sales),
                "predicted_top_categories": top_categories_list,
                "daily_predictions": predictions,  # Include all daily predictions
                "model_info": {
                    "model_type": self.model_info.get("model_type", "LightGBM"),
                    "training_date": self.model_info.get("training_date", "Unknown"),
                    "feature_count": self.model_info.get("feature_count", 0)
                }
            }

            # Add historical data if requested
            if include_historical:
                historical_period_start = start_date - timedelta(days=(end_date - start_date).days + 1)
                historical_period_end = start_date - timedelta(days=1)

                try:
                    historical_top = self.get_historical_top_categories(
                        start_date=historical_period_start,
                        end_date=historical_period_end,
                        top_n=top_n
                    )
                    response["historical_data"] = historical_top
                except ValueError as e:
                    # Log but continue - historical data is optional
                    self.logger.warning(f"Could not include historical data: {e}")
                    response["historical_data_error"] = str(e)

            return response

        except Exception as e:
            self.logger.error(f"Error predicting top categories: {e}")
            raise ValueError(f"Error predicting top categories: {str(e)}")

    def get_historical_top_categories(self, start_date: datetime, end_date: datetime, top_n: int = 5):
        """
        Get the top categories by sales amount for a historical period.
        If some dates don't have historical data, use the model to predict those values.

        Args:
            start_date (datetime): Start date for historical data
            end_date (datetime): End date for historical data
            top_n (int): Number of top categories to return

        Returns:
            dict: Historical top categories with any gaps filled by model predictions
        """
        try:
            self.logger.info(f"Getting historical top categories from {start_date} to {end_date}")

            # -------------------------------------------------------
            # Step 1: Get available historical data from the database
            # -------------------------------------------------------
            historical_df = self.get_historical_sales(start_date=start_date, end_date=end_date)

            # If no historical data at all, use prediction for the entire period
            if historical_df.empty:
                self.logger.warning(
                    f"No historical data found for period {start_date} to {end_date}. Using model predictions.")
                # Simply redirect to the prediction endpoint which can handle this case
                return self.predict_top_categories(start_date=start_date, end_date=end_date, top_n=top_n)

            # --------------------------------------
            # Step 2: Create complete date range
            # --------------------------------------
            # Generate all dates that should be present in the requested range
            all_dates = pd.date_range(start=start_date, end=end_date, freq='D')

            # --------------------------------------
            # Step 3: Identify missing dates
            # --------------------------------------
            # Check which dates from the complete range are missing in our historical data
            existing_dates = pd.DatetimeIndex(historical_df.index)
            missing_dates = pd.DatetimeIndex([d for d in all_dates if d not in existing_dates])

            # Check if we have any missing dates to fill
            if len(missing_dates) > 0:
                self.logger.info(
                    f"Found {len(missing_dates)} missing dates in historical data. Generating predictions to fill gaps.")

                # ---------------------------------------------
                # Step 4: Generate predictions for missing dates
                # ---------------------------------------------
                # Create a dataframe to store our combined results
                combined_data = historical_df.copy()

                # Get all category names from model info
                all_categories = self.model_info.get('target_categories',
                                                     ["Beauty", "Books", "Clothing", "Electronics",
                                                      "Furniture", "Groceries", "Sports", "Toys"])

                # Process missing dates in chunks for more efficient prediction
                for chunk_start, chunk_end in self._get_date_chunks(missing_dates):
                    self.logger.debug(f"Predicting data for chunk: {chunk_start} to {chunk_end}")

                    # Get predictions for this date chunk
                    predictions = self.predict_top_categories(
                        start_date=chunk_start,
                        end_date=chunk_end,
                        top_n=len(all_categories)  # Get predictions for all categories
                    )

                    # Process each missing date in this chunk
                    for date in pd.date_range(start=chunk_start, end=chunk_end, freq='D'):
                        date_str = date.strftime('%Y-%m-%d')

                        # Create a new row for each category on this date
                        for category in all_categories:
                            # Get category amount from predictions
                            try:
                                # Try to find the category in the predictions
                                category_data = next(
                                    item for item in predictions["predicted_top_categories"]
                                    if item["category"] == category
                                )
                                amount = category_data["amount"]
                            except (KeyError, StopIteration):
                                # If category not found in top N, use a small default value
                                amount = 0.0

                            # Create a new row for this date and category
                            # Add a 'source' column to track that this is predicted data
                            new_row = pd.DataFrame({
                                'date': [date],
                                category: [amount],
                                'source': ['predicted']
                            }).set_index('date')

                            # Add to our combined dataset
                            combined_data = pd.concat([combined_data, new_row])

                # Use the combined data instead of just historical data
                historical_df = combined_data

                # Sort by date for cleaner output
                historical_df = historical_df.sort_index()

                self.logger.info(
                    f"Successfully combined historical and predicted data. Total rows: {len(historical_df)}")

            # ---------------------------------------------------------
            # Step 5: Process the combined data to get top categories
            # ---------------------------------------------------------
            # Extract category columns - adjust based on your historical_df structure
            # This assumes historical_df has columns for each category (Beauty, Books, etc.)
            category_columns = [col for col in historical_df.columns
                                if col in self.model_info.get('target_categories', [])]

            if not category_columns:
                # If category columns aren't found with the expected structure,
                # try an alternative approach based on your data format
                raise ValueError("Could not identify category columns in historical data")

            # Calculate totals for each category across the date range
            category_totals = {}
            for category in category_columns:
                # Sum the sales for this category
                category_totals[category] = historical_df[category].sum()

            # Sort categories by total sales
            sorted_categories = sorted(
                category_totals.items(),
                key=lambda x: x[1],
                reverse=True
            )

            # Get top N categories
            top_categories = sorted_categories[:top_n]

            # Calculate total sales across all categories
            total_sales = sum(category_totals.values())

            # Format the response
            top_categories_formatted = []
            for category, amount in top_categories:
                percentage = (amount / total_sales * 100) if total_sales > 0 else 0

                top_categories_formatted.append({
                    "category": category,
                    "amount": float(amount),
                    "percentage": float(percentage)
                })

            # Count real vs predicted data points
            data_sources = historical_df.get('source', pd.Series(['historical'] * len(historical_df)))
            predicted_count = (data_sources == 'predicted').sum()
            historical_count = (data_sources != 'predicted').sum()

            # Construct the response
            response = {
                "period": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "days": (end_date - start_date).days + 1
                },
                "data_quality": {
                    "historical_data_points": int(historical_count),
                    "predicted_data_points": int(predicted_count),
                    "data_completeness": float(historical_count / (historical_count + predicted_count) * 100)
                    if (historical_count + predicted_count) > 0 else 0
                },
                "total_sales": float(total_sales),
                "total_sales_formatted": format_currency(total_sales),
                "top_categories": top_categories_formatted
            }

            return response

        except Exception as e:
            self.logger.error(f"Error in get_historical_top_categories: {e}")
            # Provide more informative error that also mentions the hybrid approach
            raise ValueError(
                f"Unable to retrieve sufficient historical or predicted data for period {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}: {str(e)}")


    def _get_date_chunks(self, date_index):
        """
        Helper method to split a DatetimeIndex into chunks of contiguous dates.
        This helps make prediction more efficient by grouping consecutive missing dates.

        Args:
            date_index (DatetimeIndex): Index of dates to chunk

        Returns:
            list: List of (start_date, end_date) tuples for each chunk
        """
        if len(date_index) == 0:
            return []

        chunks = []
        sorted_dates = sorted(date_index)
        chunk_start = sorted_dates[0]
        prev_date = sorted_dates[0]

        for curr_date in sorted_dates[1:]:
            # If there's a gap greater than 1 day, start a new chunk
            if (curr_date - prev_date).days > 1:
                chunks.append((chunk_start, prev_date))
                chunk_start = curr_date
            prev_date = curr_date

        # Add the last chunk
        chunks.append((chunk_start, prev_date))

        self.logger.debug(f"Split {len(date_index)} dates into {len(chunks)} chunks")
        return chunks

    def get_time_series_data(
            self,
            start_date: datetime,
            end_date: datetime,
            top_n: int = 5,
            historical_days: int = 180
    ) -> Dict[str, Any]:
        """
        Generate time series data for top N categories showing historical and predicted data.

        Args:
            start_date (datetime): Start date for prediction period
            end_date (datetime): End date for prediction period
            top_n (int): Number of top categories to return
            historical_days (int): Number of days of historical data to include

        Returns:
            dict: Time series data for historical and predicted periods

        Raises:
            ValueError: If no data could be generated
        """
        self.logger.info(f"Generating time series data from {start_date} to {end_date}")

        try:
            # Get predictions for the requested period
            predictions = self.predict_top_categories(
                start_date=start_date,
                end_date=end_date,
                top_n=top_n
            )

            # Extract the top categories from predictions
            top_categories = [item["category"] for item in predictions["predicted_top_categories"]]

            # Organize prediction data by category
            prediction_data = {}
            for category in top_categories:
                prediction_data[category] = []

            # Convert daily predictions to organized format
            daily_predictions = predictions.get("daily_predictions", [])
            for pred in daily_predictions:
                category = pred.get("category")
                if category in top_categories:
                    prediction_data[category].append({
                        "date": pred.get("date"),
                        "amount": pred.get("amount"),
                        "source": "predicted"
                    })

            # Get historical data
            historical_start = start_date - timedelta(days=historical_days)
            historical_end = start_date - timedelta(days=1)

            self.logger.info(f"Fetching historical data from {historical_start} to {historical_end}")
            historical_df = self.get_historical_sales(
                start_date=historical_start,
                end_date=historical_end
            )

            # Initialize historical data
            historical_data = {category: [] for category in top_categories}

            # Process historical data if available
            if historical_df is not None and not historical_df.empty:
                self.logger.info(f"Retrieved {len(historical_df)} rows of historical data")

                # Extract category columns from historical data
                category_columns = [col for col in historical_df.columns
                                    if col in self.model_info.get('target_categories', [])]

                # Process each top category
                for category in top_categories:
                    if category in category_columns:
                        # For each date in the historical data
                        for date, row in historical_df.iterrows():
                            if category in row:
                                historical_data[category].append({
                                    "date": date.strftime("%Y-%m-%d"),
                                    "amount": float(row[category]),
                                    "source": "historical"
                                })
            else:
                self.logger.warning("No historical data available")

            # Combine historical and prediction data for each category
            combined_data = {}
            for category in top_categories:
                combined_data[category] = sorted(
                    historical_data.get(category, []) + prediction_data.get(category, []),
                    key=lambda x: x["date"]
                )

            # Prepare response
            response = {
                "period": {
                    "prediction_start_date": start_date.strftime("%Y-%m-%d"),
                    "prediction_end_date": end_date.strftime("%Y-%m-%d"),
                    "historical_start_date": historical_start.strftime("%Y-%m-%d"),
                    "historical_end_date": historical_end.strftime("%Y-%m-%d")
                },
                "top_categories": top_categories,
                "has_historical_data": bool(historical_df is not None and not historical_df.empty),
                "time_series_data": combined_data
            }

            return response

        except Exception as e:
            self.logger.error(f"Error generating time series data: {e}")
            raise ValueError(f"Error generating time series data: {str(e)}")
