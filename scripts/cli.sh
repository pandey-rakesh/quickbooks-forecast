#!/bin/bash

# QuickBooks Sales Forecasting CLI Script
# This script provides a command-line interface to test all REST APIs

# Set default values
HOST="localhost"
PORT="8000"
BASE_URL="http://$HOST:$PORT/api/v1"
FORMAT="pretty" # pretty or json

# Function to display usage information
function show_help {
    echo "QuickBooks Sales Forecasting CLI"
    echo ""
    echo "Usage: ./scripts/cli.sh [options] <command>"
    echo ""
    echo "Options:"
    echo "  --host <host>           Host for API server (default: localhost)"
    echo "  --port <port>           Port for API server (default: 8000)"
    echo "  --format <format>       Output format: pretty or json (default: pretty)"
    echo "  --help                  Show this help message"
    echo ""
    echo "Commands:"
    echo "  predict                 Test the predict-top-categories endpoint"
    echo "  historical              Test the historical-top-categories endpoint"
    echo "  model-info              Test the model-info endpoint"
    echo "  categories              Test the categories/top endpoint"
    echo "  time-series             Test the categories/time-series-plot endpoint"
    echo "  all                     Test all endpoints"
    echo ""
    echo "Examples:"
    echo "  ./scripts/cli.sh predict                    # Test predict endpoint with default settings"
    echo "  ./scripts/cli.sh --port 5000 historical     # Test historical endpoint on port 5000"
    echo "  ./scripts/cli.sh --format json model-info   # Get model info in JSON format"
    echo "  ./scripts/cli.sh all                        # Test all endpoints"
    echo "  ./scripts/cli.sh predict \"days=60&top_n=10\"  # Test predict with specific parameters"
    echo "  ./scripts/cli.sh categories \"range=week\"     # Test categories with week range"
    echo ""
}

# Function to format JSON output
function format_json {
    if [ "$FORMAT" == "pretty" ]; then
        # Check if python is available for pretty printing
        if command -v python3 &> /dev/null; then
            python3 -m json.tool
        else
            # Fallback to cat if python is not available
            cat
        fi
    else
        # Just output raw JSON
        cat
    fi
}

# Function to test the predict-top-categories endpoint
function test_predict {
    echo "Testing predict-top-categories endpoint..."

    # Check if additional parameters were provided
    if [ -n "$1" ]; then
        echo "With parameters: $1"
        curl -s "$BASE_URL/predict-top-categories?$1" | format_json
    else
        # Default call without parameters
        curl -s "$BASE_URL/predict-top-categories" | format_json
    fi
    echo ""
}

# Function to test the historical-top-categories endpoint
function test_historical {
    echo "Testing historical-top-categories endpoint..."

    # Check if additional parameters were provided
    if [ -n "$1" ]; then
        echo "With parameters: $1"
        curl -s "$BASE_URL/historical-top-categories?$1" | format_json
    else
        # Default call without parameters
        curl -s "$BASE_URL/historical-top-categories" | format_json
    fi
    echo ""
}

# Function to test the model-info endpoint
function test_model_info {
    echo "Testing model-info endpoint..."

    # Check if additional parameters were provided
    if [ -n "$1" ]; then
        echo "With parameters: $1"
        curl -s "$BASE_URL/model-info?$1" | format_json
    else
        # Default call without parameters
        curl -s "$BASE_URL/model-info" | format_json
    fi
    echo ""
}

# Function to test the categories/top endpoint
function test_categories {
    echo "Testing categories/top endpoint..."

    # Check if additional parameters were provided
    if [ -n "$1" ]; then
        echo "With parameters: $1"
        curl -s "$BASE_URL/categories/top?$1" | format_json
    else
        # Default call without parameters
        curl -s "$BASE_URL/categories/top" | format_json
    fi
    echo ""
}

# Function to test the categories/time-series-plot endpoint
function test_time_series {
    echo "Testing categories/time-series-plot endpoint..."

    # Check if additional parameters were provided
    if [ -n "$1" ]; then
        echo "With parameters: $1"
        curl -s "$BASE_URL/categories/time-series-plot?$1" | format_json
    else
        # Default call without parameters
        curl -s "$BASE_URL/categories/time-series-plot" | format_json
    fi
    echo ""
}

# Function to test all endpoints
function test_all {
    # Pass any parameters to each test function
    test_model_info "$1"
    test_predict "$1"
    test_historical "$1"
    test_categories "$1"
    test_time_series "$1"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --host)
            HOST="$2"
            BASE_URL="http://$HOST:$PORT/api/v1"
            shift 2
            ;;
        --port)
            PORT="$2"
            BASE_URL="http://$HOST:$PORT/api/v1"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            # Save the command
            COMMAND="$1"
            shift
            break
            ;;
    esac
done

# Check if a command was provided
if [ -z "$COMMAND" ]; then
    echo "Error: No command provided."
    show_help
    exit 1
fi

# Check for additional parameters
PARAMS=""
if [ $# -gt 0 ]; then
    PARAMS="$*"
fi

# Execute the appropriate function based on the command
case "$COMMAND" in
    predict)
        test_predict "$PARAMS"
        ;;
    historical)
        test_historical "$PARAMS"
        ;;
    model-info)
        test_model_info "$PARAMS"
        ;;
    categories)
        test_categories "$PARAMS"
        ;;
    time-series)
        test_time_series "$PARAMS"
        ;;
    all)
        test_all "$PARAMS"
        ;;
    *)
        echo "Error: Unknown command '$COMMAND'. Use --help for usage information."
        exit 1
        ;;
esac
