import axios from 'axios';

// Configure API base URL - uses proxy in development, direct URL in production
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'http://localhost:8000/api/v1'
  : '/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service functions
export const ApiService = {
  // Get top categories for a time period
  getTopCategories: async (range = 'month', startDate = null, endDate = null, topN = 5) => {
    try {
      const params = { range, top_n: topN };

      // Add date parameters if provided
      if (range === 'custom') {
        if (!startDate || !endDate) {
          throw new Error('Start and end dates are required for custom range');
        }
        params.start_date = startDate;
        params.end_date = endDate;
      }

      const response = await api.get('/categories/top', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching top categories:', error);
      throw error;
    }
  },

  // Get time series data for categories
  getTimeSeriesData: async (startDate = null, endDate = null, days = 30, topN = 5, historicalDays = 180) => {
    try {
      const params = {
        top_n: topN,
        historical_days: historicalDays,
        days
      };

      // Add date parameters if provided
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      const response = await api.get('/categories/time-series-plot', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching time series data:', error);
      throw error;
    }
  },

  // Get model info
  getModelInfo: async () => {
    try {
      const response = await api.get('/model-info');
      return response.data;
    } catch (error) {
      console.error('Error fetching model info:', error);
      throw error;
    }
  }
};

export default ApiService;
