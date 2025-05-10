# QuickBooks Sales Forecasting Web Application

This is the frontend web application for the QuickBooks Sales Forecasting project. It provides a user-friendly interface to visualize sales forecasts and historical data.

## Features

- Interactive dashboard for sales forecasting visualization
- Time range selector for different forecast periods (week, month, quarter, year, custom)
- Bar chart displaying top categories by sales
- Time series chart showing historical and predicted sales trends
- Forecast details including model information

## Technology Stack

- React.js - Frontend framework
- Material UI - Component library with QuickBooks theming
- Recharts - Data visualization library
- Axios - API client for backend communication
- React Router - Navigation and routing

## Getting Started

### Prerequisites

- Node.js 14.x or higher
- npm 6.x or higher
- Backend API server running on http://localhost:8000

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) to view the application in your browser.

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

## Project Structure

```
webapp/
├── public/                 # Static files
├── src/                    # Source code
│   ├── components/         # React components
│   │   ├── Dashboard.js    # Main dashboard component
│   │   ├── TimeRangeSelector.js # Time range selection component
│   │   ├── CategoryBarChart.js  # Bar chart for categories
│   │   ├── TimeSeriesChart.js   # Time series chart component
│   │   ├── Header.js      # Application header
│   │   └── Footer.js      # Application footer
│   ├── services/          # API services
│   │   └── api.js         # API client for backend communication
│   ├── styles/            # CSS styles
│   ├── App.js             # Main application component
│   └── index.js           # Application entry point
├── package.json           # Project dependencies and scripts
└── README.md              # Project documentation
```

## API Integration

The web application communicates with the backend API to fetch forecast data. The API endpoints used include:

- `/api/v1/categories/top` - Get top categories for a time period
- `/api/v1/categories/time-series-plot` - Get time series data for categories
- `/api/v1/model-info` - Get information about the forecast model

## Deployment

For production deployment:

1. Build the application:
   ```bash
   npm run build
   ```

2. Serve the static files from the `build` directory using a web server of your choice.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
