#!/bin/bash

# QuickBooks Sales Forecasting Demo Script
# This script helps run the QuickBooks Sales Forecasting application
# in different modes: API, CLI, or generate mock data.

# Set default values
MODE="api"
PORT=8000
HOST="0.0.0.0"
RELOAD=true
MOCK_DATA=false
START_DATE="2020-01-01"
END_DATE=$(date +%Y-%m-%d)
NUM_CATEGORIES=10
TRANSACTIONS_PER_DAY=50

# Function to display usage information
function show_help {
    echo "QuickBooks Sales Forecasting Demo"
    echo ""
    echo "Usage: ./run_demo.sh [options]"
    echo ""
    echo "Options:"
    echo "  --mode <mode>           Run mode: api, cli, or mock (default: api)"
    echo "  --port <port>           Port for API server (default: 8000)"
    echo "  --host <host>           Host for API server (default: 0.0.0.0)"
    echo "  --no-reload             Disable auto-reload for API server"
    echo "  --mock-data             Generate mock data before starting"
    echo "  --start-date <date>     Start date for mock data (default: 2020-01-01)"
    echo "  --end-date <date>       End date for mock data (default: today)"
    echo "  --num-categories <num>  Number of categories for mock data (default: 10)"
    echo "  --transactions <num>    Average transactions per day for mock data (default: 50)"
    echo "  --help                  Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_demo.sh                          # Run API server with default settings"
    echo "  ./run_demo.sh --mode cli               # Run CLI interface"
    echo "  ./run_demo.sh --mode mock              # Generate mock data only"
    echo "  ./run_demo.sh --mock-data              # Generate mock data and run API server"
    echo "  ./run_demo.sh --port 5000              # Run API server on port 5000"
    echo "  ./run_demo.sh --mode cli predict       # Run CLI predict command"
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
        --mock-data)
            MOCK_DATA=true
            shift
            ;;
        --start-date)
            START_DATE="$2"
            shift 2
            ;;
        --end-date)
            END_DATE="$2"
            shift 2
            ;;
        --num-categories)
            NUM_CATEGORIES="$2"
            shift 2
            ;;
        --transactions)
            TRANSACTIONS_PER_DAY="$2"
            shift 2
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

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if required directories exist
if [ ! -d "app" ] || [ ! -d "model" ] || [ ! -d "data" ]; then
    echo "Error: Required directories not found. Make sure you're running this script from the project root."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Generate mock data if requested
if [ "$MOCK_DATA" = true ] || [ "$MODE" = "mock" ]; then
    echo "Generating mock sales data..."
    python3 scripts/generate_mock_data.py \
        --start-date "$START_DATE" \
        --end-date "$END_DATE" \
        --num-categories "$NUM_CATEGORIES" \
        --transactions-per-day "$TRANSACTIONS_PER_DAY"
    
    # Exit if mode is mock
    if [ "$MODE" = "mock" ]; then
        echo "Mock data generation complete."
        exit 0
    fi
fi

# Run the application based on the selected mode
case "$MODE" in
    api)
        echo "Starting API server on $HOST:$PORT..."
        if [ "$RELOAD" = true ]; then
            uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
        else
            uvicorn app.main:app --host "$HOST" --port "$PORT"
        fi
        ;;
    cli)
        echo "Running CLI command..."
        python3 -m ui.cli $CLI_ARGS
        ;;
    *)
        echo "Error: Unknown mode '$MODE'. Use --help for usage information."
        exit 1
        ;;
esac