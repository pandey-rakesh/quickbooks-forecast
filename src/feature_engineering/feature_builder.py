
from datetime import timedelta
import pandas as pd
import numpy as np
import pickle
import os
from app.config import FEATURE_COLUMNS_PATH

LAG_DAYS = [1, 7, 14, 28]
ROLLING_WINDOWS = [7, 14, 28]


class FeatureBuilder:
    def __init__(self, feature_config_path=FEATURE_COLUMNS_PATH):
        if os.path.exists(feature_config_path):
            with open(feature_config_path, 'rb') as f:
                self.feature_columns = ['date'] + pickle.load(f)  # Add 'date' to front
        else:
            raise FileNotFoundError("Feature columns definition not found.")

    def generate_features(self, start_date, end_date, historical_data):
        historical_data = historical_data.copy()
        historical_data.reset_index(inplace=True)
        historical_data['date'] = pd.to_datetime(historical_data['date'])
        historical_data.set_index('date', inplace=True)

        feature_rows = []
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')

        for current_date in date_range:
            row = self.build_feature_row(current_date, historical_data, feature_rows)
            feature_rows.append(row)

        features_df = pd.DataFrame(feature_rows)
        features_df['date'] = pd.to_datetime(features_df['date'])
        features_df.set_index('date', inplace=True)
        features_df = features_df[[col for col in self.feature_columns if col in features_df.columns]]
        return features_df

    def build_feature_row(self, date, historical_data, previous_rows):
        row = {
            'date': date,
            'year': date.year,
            'month': date.month,
            'day_of_week': date.weekday(),
            'week_of_year': date.isocalendar()[1],
            'quarter': (date.month - 1) // 3 + 1,
            'is_weekend': int(date.weekday() >= 5),
            'is_month_end': int(date.is_month_end),
            'is_month_start': int(date.is_month_start),
            'is_november': int(date.month == 11),
        }

        DATE_COLUMNS = ['date', 'year', 'month', 'day_of_week', 'week_of_year',
                        'quarter', 'is_weekend', 'is_month_end', 'is_month_start', 'is_november']

        # Combine previous rows with historical data
        prev_df = pd.DataFrame(previous_rows)
        if not prev_df.empty:
            prev_df['date'] = pd.to_datetime(prev_df['date'])
            prev_df.set_index('date', inplace=True)

        combined_data = pd.concat([historical_data, prev_df], axis=0)
        combined_data.sort_index(inplace=True)

        for col in self.feature_columns:
            if col in row or col in DATE_COLUMNS:
                continue

            if '_lag_' in col:
                base, lag = col.rsplit('_lag_', 1)
                lag_days = int(lag.rstrip('d'))
                ref_date = date - timedelta(days=lag_days)
                row[col] = (
                    combined_data.at[ref_date, col]
                    if ref_date in combined_data.index and col in combined_data.columns
                    else 0.0
                )

            elif '_rolling_avg_' in col:
                base, win = col.rsplit('_rolling_avg_', 1)
                window = int(win.rstrip('d'))
                past_vals = [
                    combined_data.at[d, col]
                    for d in [date - timedelta(days=i) for i in range(1, window + 1)]
                    if d in combined_data.index and col in combined_data.columns
                ]
                row[col] = float(np.mean(past_vals)) if past_vals else 0.0

            elif '_rolling_std_' in col:
                base, win = col.rsplit('_rolling_std_', 1)
                window = int(win.rstrip('d'))
                past_vals = [
                    combined_data.at[d, col]
                    for d in [date - timedelta(days=i) for i in range(1, window + 1)]
                    if d in combined_data.index and col in combined_data.columns
                ]
                row[col] = float(np.std(past_vals)) if past_vals else 0.0

            else:
                row[col] = 0.0  # Default fallback

        return row
