import React, { useState, useEffect } from 'react';
import { Container, Box, Typography, Grid, Paper } from '@mui/material';
import { format, parseISO } from 'date-fns';
import ApiService from '../services/api';
import TimeRangeSelector from './TimeRangeSelector';
import CategoryBarChart from './CategoryBarChart';
import TimeSeriesChart from './TimeSeriesChart';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

const Dashboard = () => {
  // State
  const [timeRange, setTimeRange] = useState('month');
  const [customDateRange, setCustomDateRange] = useState({ startDate: null, endDate: null });
  const [topCategories, setTopCategories] = useState(null);
  const [topCategoriesYoY, setTopCategoriesYoY] = useState(null);
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

        // Get top categories with last year comparison
        try {
          const categoriesYoYData = await ApiService.getTopCategoriesWithLastYear(
            timeRange,
            customDateRange.startDate,
            customDateRange.endDate,
            5
          );
          setTopCategoriesYoY(categoriesYoYData);
        } catch (yoyError) {
          console.warn('Could not load YoY comparison data:', yoyError);
          // Fallback to regular top categories
          const categoriesData = await ApiService.getTopCategories(
            timeRange,
            customDateRange.startDate,
            customDateRange.endDate,
            5
          );
          setTopCategories(categoriesData);
        }

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
      return format(parseISO(dateString), 'dd/MM/yyyy');  // Format as "13/05/2025"
    } catch (e) {
      console.error("Date format error:", e);
      return dateString;
    }
  };

  // Format date range in a compact way
  const formatDateRange = (startDate, endDate) => {
    if (!startDate || !endDate) return '';
    try {
      return `${format(parseISO(startDate), 'dd/MM/yyyy')} - ${format(parseISO(endDate), 'dd/MM/yyyy')}`;
    } catch (e) {
      console.error("Date range format error:", e);
      return `${startDate} - ${endDate}`;
    }
  };

  // Calculate chart height based on number of categories
  const getChartHeight = () => {
    if (!topCategoriesYoY && !topCategories) return 300;

    const dataLength = topCategoriesYoY
      ? topCategoriesYoY.top_categories.length
      : topCategories.top_categories.length;

    // Calculate height based on number of categories plus space for legend
    return Math.max(300, dataLength * 70 + 40); // Add 40px for legend
  };

  return (
    <Container maxWidth="lg" sx={{ mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Sales Forecasting
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
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Top Categories by Sales
                </Typography>
                {topCategoriesYoY && (
                  <Typography variant="body2" color="textSecondary">
                    <strong>Total Forecast:</strong> {topCategoriesYoY.totals.current.formatted}
                    {topCategoriesYoY.totals.yoy_change_percent !== null && (
                      <span style={{
                        color: topCategoriesYoY.totals.yoy_change_percent >= 0 ? 'green' : 'red',
                        marginLeft: '8px'
                      }}>
                        ({topCategoriesYoY.totals.yoy_change_percent > 0 ? '+' : ''}
                        {topCategoriesYoY.totals.yoy_change_percent.toFixed(1)}% vs last year)
                      </span>
                    )}
                  </Typography>
                )}
              </Box>
              {topCategoriesYoY ? (
                <Box sx={{ height: getChartHeight() }}>
                  <CategoryBarChart
                    data={topCategoriesYoY.top_categories}
                    showYoYComparison={true}
                  />
                </Box>
              ) : topCategories && (
                <Box sx={{ height: getChartHeight() }}>
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
              {topCategoriesYoY ? (
                <Box>
                  <Typography variant="body1">
                    <strong>Current Period:</strong> {formatDateRange(
                      topCategoriesYoY.period.current.start_date,
                      topCategoriesYoY.period.current.end_date
                    )}
                  </Typography>
                  <Typography variant="body1" sx={{ mt: 1 }}>
                    <strong>Last Year Period:</strong> {formatDateRange(
                      topCategoriesYoY.period.last_year.start_date,
                      topCategoriesYoY.period.last_year.end_date
                    )}
                  </Typography>
                  <Typography variant="body1" sx={{ mt: 1 }}>
                    <strong>Range:</strong> {topCategoriesYoY.range.charAt(0).toUpperCase() + topCategoriesYoY.range.slice(1)}
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
              ) : topCategories && (
                <Box>
                  <Typography variant="body1">
                    <strong>Period:</strong> {formatDateRange(
                      topCategories.start_date,
                      topCategories.end_date
                    )}
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
                <Box sx={{ height: 480 }}> {/* Increased from 450px to 480px */}
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
