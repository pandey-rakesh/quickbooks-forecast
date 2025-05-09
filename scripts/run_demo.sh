#!/bin/bash

# QuickBooks Sales Forecasting Demo Script
# This script helps run the QuickBooks Sales Forecasting application
# in either API or CLI mode.

# Set default values
MODE="api"
PORT=8000
HOST="0.0.0.0"
RELOAD=true

# Function to display usage information
function show_help {
    echo "QuickBooks Sales Forecasting Demo"
    echo ""
    echo "Usage: ./scripts/run_demo.sh [options]"
    echo ""
    echo "Options:"
    echo "  --mode <mode>           Run mode: api or cli (default: api)"
    echo "  --port <port>           Port for API server (default: 8000)"
    echo "  --host <host>           Host for API server (default: 0.0.0.0)"
    echo "  --no-reload             Disable auto-reload for API server"
    echo "  --help                  Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./scripts/run_demo.sh                          # Run API server with default settings"
    echo "  ./scripts/run_demo.sh --mode cli               # Run CLI interface"
    echo "  ./scripts/run_demo.sh --port 5000              # Run API server on port 5000"
    echo "  ./scripts/run_demo.sh --mode cli predict       # Run CLI predict command"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --no-reload)
            RELOAD=false
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            # Save remaining arguments for CLI mode
            CLI_ARGS="$@"
            break
            ;;
    esac
done

# Create necessary directories
mkdir -p model logs data/raw data/processed

# Generate model_info.json if it doesn't exist
if [ ! -f "model/model_info.json" ]; then
    echo "Creating default model_info.json..."
    cat > model/model_info.json << EOL
{
    "model_type": "LightGBM",
    "training_date": "2025-05-08 21:03:01",
    "metrics": {
        "test_rmse": 515.7500859296204,
        "cv_rmse": 490.72013957336645,
        "top1_accuracy": 0.9666666666666667,
        "top3_accuracy": 0.8629629629629629
    },
    "parameters": {
        "learning_rate": 0.01,
        "max_depth": 8,
        "n_estimators": 500
    },
    "feature_count": 33,
    "training_samples": 1722,
    "target_categories": [
        "Beauty",
        "Books",
        "Clothing",
        "Electronics",
        "Furniture",
        "Groceries",
        "Sports",
        "Toys"
    ]
}
EOL
fi

# Check for required Python packages
python3 -c "
import importlib.util
missing_packages = []
for package in ['fastapi', 'uvicorn']:
    if importlib.util.find_spec(package) is None:
        missing_packages.append(package)
if missing_packages:
    print('MISSING_PACKAGES:' + ','.join(missing_packages))
"

# Install missing packages if needed
MISSING_PACKAGES=$(python3 -c "
import importlib.util
missing_packages = []
for package in ['fastapi', 'uvicorn']:
    if importlib.util.find_spec(package) is None:
        missing_packages.append(package)
print(','.join(missing_packages))
")

if [ ! -z "$MISSING_PACKAGES" ]; then
    echo "Installing missing packages: $MISSING_PACKAGES"
    pip install $MISSING_PACKAGES
fi

# Run the application based on the selected mode
case "$MODE" in
    api)
        echo "Starting API server on $HOST:$PORT..."
        if [ "$RELOAD" = true ]; then
            python3 -m uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
        else
            python3 -m uvicorn app.main:app --host "$HOST" --port "$PORT"
        fi
        ;;
    cli)
        echo "Running CLI command..."
        if [ ! -d "ui" ]; then
            echo "Warning: CLI mode requires the 'ui' directory, which was not found."
            echo "Falling back to API mode."
            python3 -m uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
        else
            python3 -m ui.cli $CLI_ARGS
        fi
        ;;
    *)
        echo "Error: Unknown mode '$MODE'. Use --help for usage information."
        exit 1
        ;;
esac
