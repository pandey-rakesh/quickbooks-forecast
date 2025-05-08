# QuickBooks Sales Forecasting

A machine learning application for forecasting top-selling product categories based on historical sales data.

## Project Overview

This project provides a complete solution for sales forecasting, including:

- Data exploration and visualization
- Feature engineering for time series data
- XGBoost model training and hyperparameter tuning
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
│   ├── 03_model_training.ipynb          # Train, validate, tune XGBoost
│   └── 04_model_export.ipynb            # Save model.pkl for inference
│
├── model/                               # Model and feature pipeline
│   ├── features.py                      # Feature builder for inference
│   ├── train_model.py                   # Script version of notebook #3
│   └── model.pkl                        # Trained model artifact
│
├── app/                                 # REST API microservice
│   ├── main.py                          # FastAPI app instance
│   ├── api.py                           # `/predict-top-categories` endpoint
│   ├── service.py                       # Core business logic
│   ├── utils.py                         # Date filters, helpers, mappers
│   └── config.py                        # Central config (paths, thresholds)
│
├── ui/                                  # CLI interface
│   └── cli.py                           # Command-line interface
│
├── tests/                               # Unit & integration tests
│   ├── test_feature_builder.py
│   ├── test_model_inference.py
│   └── test_api.py
│
├── scripts/                             # Setup helpers
│   └── generate_mock_data.py            # Generate synthetic sales data
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

4. Generate mock data (if needed):
   ```bash
   python scripts/generate_mock_data.py
   ```

## Usage

### Running the API

Start the FastAPI server:

```bash
./run_demo.sh
```

The API will be available at http://localhost:8000. You can access the interactive API documentation at http://localhost:8000/docs.

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

Run the test suite:

```bash
pytest tests/
```

### Notebooks

The Jupyter notebooks in the `notebooks/` directory provide a step-by-step walkthrough of the data science process:

1. Data exploration and visualization
2. Feature engineering
3. Model training and tuning
4. Model export

## License

This project is licensed under the MIT License - see the LICENSE file for details.
