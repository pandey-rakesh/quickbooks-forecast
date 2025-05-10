import React, { useState, useEffect } from 'react';
import { Container, Grid, Paper, Typography, Box } from '@mui/material';
import TimeRangeSelector from './TimeRangeSelector';
import CategoryBarChart from './CategoryBarChart';
import TimeSeriesChart from './TimeSeriesChart';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import ApiService from '../services/api';
import { format, parseISO } from 'date-fns'; // Import date-fns functions

const Dashboard = () => {
  // State
  const [timeRange, setTimeRange] = useState('month');
  const [customDateRange, setCustomDateRange] = useState({ startDate: null, endDate: null });
  const [topCategories, setTopCategories] = useState(null);
  const [timeSeriesData, setTimeSeriesData] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data when time range changes
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        // Get model info once
        if (!modelInfo) {
          const modelInfoData = await ApiService.getModelInfo();
          setModelInfo(modelInfoData);
        }

        // Get top categories data
        const categoriesData = await ApiService.getTopCategories(
          timeRange,
          customDateRange.startDate,
          customDateRange.endDate,
          5
        );
        setTopCategories(categoriesData);

        // Get time series data
        const seriesData = await ApiService.getTimeSeriesData(
          timeRange === 'custom' ? customDateRange.startDate : null,
          timeRange === 'custom' ? customDateRange.endDate : null,
          timeRange === 'week' ? 7 : timeRange === 'month' ? 30 : timeRange === 'quarter' ? 90 : 365,
          5,
          180
        );
        setTimeSeriesData(seriesData);

        setLoading(false);
      } catch (err) {
        setError(err.message || 'Failed to fetch data');
        setLoading(false);
      }
    };

    fetchData();
  }, [timeRange, customDateRange.startDate, customDateRange.endDate, modelInfo]);

  // Handle time range change
  const handleTimeRangeChange = (range, customRange = null) => {
    setTimeRange(range);
    if (customRange) {
      setCustomDateRange(customRange);
    }
  };

  // Format date in a user-friendly way
  const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
      return format(parseISO(dateString), 'MMMM dd, yyyy');  // Format as "May 09, 2025"
    } catch (e) {
      console.error("Date format error:", e);
      return dateString;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Sales Forecast
        </Typography>
        <Typography variant="subtitle1" color="textSecondary">
          Predict top-selling categories to optimize your inventory and marketing strategy
        </Typography>
      </Box>

      <TimeRangeSelector
        selectedRange={timeRange}
        onRangeChange={handleTimeRangeChange}
      />

      {loading ? (
        <LoadingSpinner message="Loading forecast data..." />
      ) : error ? (
        <ErrorMessage
          message={error}
          retryFunction={() => handleTimeRangeChange(timeRange, timeRange === 'custom' ? customDateRange : null)}
        />
      ) : (
        <Grid container spacing={3} sx={{ mt: 2 }}>
          {/* Top Categories Overview */}
          <Grid item xs={12} md={8}>
            <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Top Categories by Sales
              </Typography>
              {topCategories && (
                <Box sx={{ height: 300 }}>
                  <CategoryBarChart data={topCategories.top_categories} />
                </Box>
              )}
            </Paper>
          </Grid>

          {/* Time Period Info */}
          <Grid item xs={12} md={4}>
            <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Forecast Details
              </Typography>
              {topCategories && (
                <Box>
                  <Typography variant="body1">
                    <strong>Period:</strong> {formatDate(topCategories.start_date)} to {formatDate(topCategories.end_date)}
                  </Typography>
                  <Typography variant="body1" sx={{ mt: 1 }}>
                    <strong>Range:</strong> {topCategories.range.charAt(0).toUpperCase() + topCategories.range.slice(1)}
                  </Typography>

                  {modelInfo && (
                    <>
                      <Typography variant="body1" sx={{ mt: 3 }}>
                        <strong>Model:</strong> {modelInfo.model_type}
                      </Typography>
                      <Typography variant="body1">
                        <strong>Training Date:</strong> {formatDate(modelInfo.training_date)}
                      </Typography>
                      <Typography variant="body1">
                        <strong>Feature Count:</strong> {modelInfo.feature_count}
                      </Typography>
                    </>
                  )}
                </Box>
              )}
            </Paper>
          </Grid>

          {/* Time Series Chart */}
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Sales Trend Over Time
              </Typography>
              {timeSeriesData && (
                <Box sx={{ height: 450 }}>
                  <TimeSeriesChart data={timeSeriesData} />
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};

export default Dashboard;
