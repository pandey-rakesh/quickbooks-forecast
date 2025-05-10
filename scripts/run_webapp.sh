#!/bin/bash

# QuickBooks Sales Forecasting Web App Script
# This script helps run the QuickBooks Sales Forecasting Web UI

# Set default values
PORT=3000
DEV_MODE=true

# Function to display usage information
function show_help {
    echo "QuickBooks Sales Forecasting Web UI"
    echo ""
    echo "Usage: ./run_webapp.sh [options]"
    echo ""
    echo "Options:"
    echo "  --port <port>           Port for Web server (default: 3000)"
    echo "  --prod                  Run in production mode (default: development)"
    echo "  --help                  Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_webapp.sh                       # Run in development mode"
    echo "  ./run_webapp.sh --port 5000           # Run on port 5000"
    echo "  ./run_webapp.sh --prod                # Run production build"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --port)
            PORT="$2"
            shift 2
            ;;
        --prod)
            DEV_MODE=false
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js to run the web application."
    exit 1
fi

# Check if webapp directory exists
if [ ! -d "webapp" ]; then
    echo "Web application directory not found. Please set up the webapp directory first."
    exit 1
fi

# Check if package.json exists
if [ ! -f "webapp/package.json" ]; then
    echo "package.json not found in webapp directory. Please set up the React application first."
    exit 1
fi

# Change to webapp directory
cd webapp

# Check if node_modules exists, otherwise install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the webapp
if [ "$DEV_MODE" = true ]; then
    echo "Starting development server on port $PORT..."
    PORT=$PORT npm start
else
    echo "Building for production..."
    npm run build
    
    # Check if serve is installed
    if ! command -v serve &> /dev/null; then
        echo "Installing serve..."
        npm install -g serve
    fi
    
    echo "Starting production server on port $PORT..."
    serve -s build -l $PORT
fi

