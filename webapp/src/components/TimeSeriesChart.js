import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceArea
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { formatCurrency } from '../utils/formatters';
import { Box, Checkbox, FormControlLabel, FormGroup, Typography } from '@mui/material';

const TimeSeriesChart = ({ data }) => {
  // State to track which categories are visible
  const [visibleCategories, setVisibleCategories] = useState({});

  // Initialize visible categories on data change
  useEffect(() => {
    if (data && data.top_categories) {
      const initialVisibility = {};
      data.top_categories.forEach((category) => {
        // By default, show all categories
        initialVisibility[category] = true;
      });
      setVisibleCategories(initialVisibility);
    }
  }, [data]);

  // Basic error handling and loading state
  if (!data) {
    return <div>Loading data...</div>;
  }

  // Check data structure to match API response
  if (!data.time_series_data || !data.top_categories || data.top_categories.length === 0) {
    console.error("Invalid data structure:", data);
    return <div>Invalid data format. Please check console for details.</div>;
  }

  // Toggle category visibility
  const handleCategoryToggle = (category) => {
    setVisibleCategories({
      ...visibleCategories,
      [category]: !visibleCategories[category]
    });
  };

  // Process data for the chart
  const processData = () => {
    const chartData = [];
    const dateSet = new Set();

    // Collect all dates from all categories
    Object.values(data.time_series_data).forEach(categoryData => {
      categoryData.forEach(item => {
        dateSet.add(item.date);
      });
    });

    // Sort dates
    const sortedDates = Array.from(dateSet).sort();

    // Create data points for each date
    sortedDates.forEach(date => {
      const dataPoint = { date };

      // Add data for each category on this date
      data.top_categories.forEach(category => {
        const categoryData = data.time_series_data[category] || [];
        const dateData = categoryData.find(item => item.date === date);

        if (dateData) {
          // Store both amount and source (historical or forecast)
          dataPoint[category] = dateData.amount;
          dataPoint[`${category}_source`] = dateData.source;
        } else {
          dataPoint[category] = 0;
        }
      });

      chartData.push(dataPoint);
    });

    return chartData;
  };

  const chartData = processData();

  // Find the boundary between historical and forecast data
  const findForecastStartDate = () => {
    if (!data.period || !data.period.prediction_start_date) {
      return null;
    }
    return data.period.prediction_start_date;
  };

  // Get forecast start date
  const forecastStartDate = findForecastStartDate();

  // Format date for x-axis
  const formatXAxis = (dateStr) => {
    if (!dateStr) return '';
    try {
      return format(parseISO(dateStr), 'MMM d');
    } catch (e) {
      console.error("Date format error:", e);
      return dateStr;
    }
  };

  // Custom tooltip that shows all category values for a date
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      // Determine if this is historical or predicted data
      const isForecasted = forecastStartDate && label >= forecastStartDate;

      return (
        <div className="custom-tooltip" style={{
          backgroundColor: 'white',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '4px',
          boxShadow: '0 2px 5px rgba(0,0,0,0.15)'
        }}>
          <p style={{ margin: '0 0 5px 0', fontWeight: 'bold' }}>
            {format(parseISO(label), 'MMM d, yyyy')}
            {isForecasted ? ' (Forecast)' : ' (Historical)'}
          </p>
          {payload.map((entry, index) => {
            // Skip the source fields and categories that aren't visible
            if (entry.dataKey.includes('_source') || !visibleCategories[entry.dataKey]) return null;

            return (
              <p key={index} style={{
                margin: '3px 0',
                color: entry.color
              }}>
                {entry.name}: {formatCurrency(entry.value)}
              </p>
            );
          })}
        </div>
      );
    }
    return null;
  };

  // Generate colors for categories
  const getCategoryColor = (index) => {
    const colors = ['#4CAF50', '#2196F3', '#FFC107', '#9C27B0', '#F44336', '#00BCD4', '#FF9800', '#795548'];
    return colors[index % colors.length];
  };

  return (
    <>
      <Box sx={{ mb: 1 }}>  {/* Reduced margin to allow more space for chart */}
        <Typography variant="subtitle2" gutterBottom>
          Toggle Categories:
        </Typography>
        <FormGroup row>
          {data.top_categories.map((category, index) => (
            <FormControlLabel
              key={category}
              control={
                <Checkbox
                  checked={visibleCategories[category] || false}
                  onChange={() => handleCategoryToggle(category)}
                  sx={{
                    color: getCategoryColor(index),
                    '&.Mui-checked': {
                      color: getCategoryColor(index),
                    },
                  }}
                />
              }
              label={category}
            />
          ))}
        </FormGroup>
      </Box>

      <ResponsiveContainer width="100%" height="100%">  {/* Increased from 85% to 90% */}
        <LineChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 70 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tickFormatter={formatXAxis}
            interval="preserveStartEnd"
            angle={-45}
            textAnchor="end"
            height={60}
            tick={{ fontSize: 12 }}
          />
          <YAxis tickFormatter={formatCurrency} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />

          {/* Reference Area for forecast section */}
          {forecastStartDate && (
            <ReferenceArea
              x1={forecastStartDate}
              x2={chartData[chartData.length - 1]?.date}
              fill="#f5f5f5"
              fillOpacity={0.6}
              label={{
                value: "Forecast Period",
                position: "insideTop",
                fill: "#757575",
                fontSize: 12
              }}
            />
          )}

          {/* Draw a line for each visible category */}
          {data.top_categories.map((category, index) => {
            // Only render lines for visible categories
            if (!visibleCategories[category]) return null;

            const color = getCategoryColor(index);

            return (
              <Line
                key={category}
                type="monotone"
                dataKey={category}
                name={category}
                stroke={color}
                strokeWidth={1.5}
                dot={{ r: 2.5 }}
                activeDot={{ r: 4 }}
                connectNulls={true}
              />
            );
          })}
        </LineChart>
      </ResponsiveContainer>
    </>
  );
};

export default TimeSeriesChart;
