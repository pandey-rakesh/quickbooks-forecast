# QuickBooks Sales Forecasting

A machine learning application for forecasting top-selling product categories based on historical sales data.

## Project Overview

This project provides a complete solution for sales forecasting, including:

- Data exploration and visualization
- Feature engineering for time series data
- Multiple model training (RandomForest, XGBoost, LightGBM) and hyperparameter tuning
- LightGBM selected as best performing model
- REST API for making predictions
- Command-line interface for easy interaction

The application uses historical sales data to predict which product categories will be the top sellers in future periods, helping businesses make informed inventory and marketing decisions.

## Directory Structure

```
quickbooks-forecast/
│
├── data/                                # Static / source data
│   ├── raw/                             # Raw input data
│   │   └── sales.csv                    # Enriched 3-year daily sales dataset
│   └── processed/                       # Processed data for model training
│
├── notebooks/                           # CRISP-DM + EDA workbooks
│   ├── 01_data_exploration.ipynb        # Visualize sales, trends, categories
│   ├── 02_feature_engineering.ipynb     # Derive model-ready features
│   ├── 03_model_training.ipynb          # Train, validate, tune models (RandomForest, XGBoost, LightGBM)
│   └── 04_future_prediction.ipynb       # Make predictions for future periods
│
├── model/                               # Model and feature pipeline
│   ├── feature_columns.pkl              # Saved feature columns for model
│   ├── model.pkl                        # Trained model artifact
│   └── model_info.json                  # Model metadata and information
│
├── app/                                 # REST API microservice
│   ├── main.py                          # FastAPI app instance
│   ├── api.py                           # API endpoints
│   ├── service.py                       # Core business logic
│   ├── utils.py                         # Date filters, helpers, mappers
│   ├── config.py                        # Central config (paths, thresholds)
│   └── models.py                        # Data models for API
│
├── tests/                               # Unit & integration tests
│   └── __pycache__/                     # Python cache directory
│
├── src/                                 # Source code for database operations
│   ├── db_config.py                     # Database configuration
│   ├── db_operations.py                 # Database CRUD operations
│   ├── store_data_in_db.py              # Script to store data in database
│   ├── test_db_connection.py            # Test database connectivity
│   └── feature_engineering/             # Feature engineering modules
│       └── feature_builder.py           # Build features for model
│
├── scripts/                             # Setup helpers
│   └── run_demo.sh                      # Script to run the demo
│
├── Dockerfile                           # Containerize application for deployment
├── requirements.txt                     # Python dependencies
├── run_demo.sh                          # Launch CLI or API locally
└── README.md                            # Project documentation
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/quickbooks-forecast.git
   cd quickbooks-forecast
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up database configuration:
   ```bash
   # Edit the database configuration in src/db_config.py
   # The default configuration uses:
   # - PostgreSQL database
   # - Host: localhost
   # - Database: quickbooks_forecast
   # - Username: postgres
   # - Password: postgres

   # IMPORTANT: Update the credentials for your environment
   # IMPORTANT: Never commit sensitive credentials to version control
   ```

5. Load sample data into the database:
   ```bash
   # Store the sample data in the database
   python src/store_data_in_db.py
   ```

## Usage

### Running the API

Start the FastAPI server:

```bash
./run_demo.sh
```

The API will be available at http://localhost:8000. You can access the interactive API documentation at http://localhost:8000/docs.

### API Endpoints

The API provides the following endpoints:

#### GET /api/v1/predict-top-categories

Predict the top categories by sales amount for a future period.

**Query Parameters:**
- `start_date` (optional): Start date in ISO format (YYYY-MM-DD)
- `end_date` (optional): End date in ISO format (YYYY-MM-DD)
- `days` (optional, default: 30): Number of days to forecast if start_date is not provided
- `top_n` (optional, default: 5): Number of top categories to return
- `include_historical` (optional, default: false): Include historical data for comparison

**Example Response:**
```json
{
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
    }
  ],
  "model_info": {
    "model_type": "XGBRegressor",
    "training_date": "2023-01-15",
    "feature_count": 20
  }
}
```

#### GET /api/v1/historical-top-categories

Get the top categories by sales amount for a historical period.

**Query Parameters:**
- `start_date` (optional): Start date in ISO format (YYYY-MM-DD)
- `end_date` (optional): End date in ISO format (YYYY-MM-DD)
- `days` (optional, default: 30): Number of days to include if start_date is not provided
- `top_n` (optional, default: 5): Number of top categories to return

#### GET /api/v1/model-info

Get information about the loaded model.

#### GET /api/v1/categories/top

Get top-N predicted categories for a time frame.

**Query Parameters:**
- `range` (optional, default: "month"): Time range (week, month, quarter, year, custom)
- `start_date` (required for custom range): Start date for custom range (YYYY-MM-DD)
- `end_date` (required for custom range): End date for custom range (YYYY-MM-DD)
- `top_n` (optional, default: 5): Number of top categories to return

**Example Response:**
```json
{
  "range": "month",
  "start_date": "2025-05-01",
  "end_date": "2025-05-31",
  "top_categories": [
    {"category": "Beauty", "revenue": 45230.45},
    {"category": "Books", "revenue": 38423.11},
    {"category": "Clothing", "revenue": 36891.89}
  ]
}
```

#### GET /api/v1/categories/time-series-plot

Generate time series data for top N categories showing historical and predicted data.

**Query Parameters:**
- `start_date` (optional): Start date for prediction in ISO format (YYYY-MM-DD)
- `end_date` (optional): End date for prediction in ISO format (YYYY-MM-DD)
- `days` (optional, default: 30): Number of days to forecast if start_date is not provided
- `top_n` (optional, default: 5): Number of top categories to show
- `historical_days` (optional, default: 180): Number of days of historical data to include

### Database Operations

The project includes functionality to store and retrieve data from a PostgreSQL database:

1. Install required dependencies:
   ```bash
   # Make sure you have all required dependencies installed
   pip install -r requirements.txt
   ```

2. Set up database configuration:
   ```bash
   # Edit the database configuration in src/db_config.py
   # The default configuration uses:
   # - PostgreSQL database
   # - Host: localhost
   # - Database: quickbooks_forecast
   # - Username: postgres
   # - Password: postgres

   # IMPORTANT: Update the credentials for your environment
   # IMPORTANT: Never commit sensitive credentials to version control
   ```

3. Test the database connection:
   ```bash
   # Test the database connection
   python src/test_db_connection.py
   ```

3. Store engineered features in the database:
   ```bash
   # Store the engineered features in the database
   python src/store_data_in_db.py

   # Specify a different CSV file
   python src/store_data_in_db.py --csv-path path/to/your/file.csv

   # Force overwrite of existing data without prompting
   python src/store_data_in_db.py --force
   ```

### Using the CLI

The command-line interface provides easy access to the forecasting functionality:

```bash
# Get predictions for the next 30 days
./run_demo.sh --mode cli predict

# Get historical top categories
./run_demo.sh --mode cli historical

# Get model information
./run_demo.sh --mode cli model-info

# Show help
./run_demo.sh --mode cli --help
```

### Using Docker

Build and run the Docker container:

```bash
docker build -t quickbooks-forecast .
docker run -p 8000:8000 quickbooks-forecast
```

## Development

### Running Tests

The project includes a test framework, but test files need to be created:

```bash
# Create a test directory if it doesn't exist
mkdir -p tests

# Create test files as needed
# Example: touch tests/test_api.py
```

Once test files are created, you can run the test suite:

```bash
pytest tests/
```

### Notebooks

The Jupyter notebooks in the `notebooks/` directory provide a step-by-step walkthrough of the data science process:

1. Data exploration and visualization
2. Feature engineering
3. Model training and tuning
4. Future prediction

## License

This project is licensed under the MIT License - see the LICENSE file for details.
