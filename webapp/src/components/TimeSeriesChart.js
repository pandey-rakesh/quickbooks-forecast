import React, { useState } from 'react';
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
import {
  Box,
  FormControlLabel,
  Checkbox,
  Typography
} from '@mui/material';
import { formatCurrency } from '../utils/formatters';

const TimeSeriesChart = ({ data }) => {
  const [selectedCategories, setSelectedCategories] = useState({});

  // Initialize selected categories if not set
  React.useEffect(() => {
    if (Object.keys(selectedCategories).length === 0 && data && data.top_categories) {
      const initialSelected = {};
      data.top_categories.forEach(category => {
        initialSelected[category] = true;
      });
      setSelectedCategories(initialSelected);
    }
  }, [data, selectedCategories]);

  // Format data for the chart
  const formatChartData = () => {
    if (!data || !data.time_series_data) return [];

    // Get all dates from all categories
    const allDates = new Set();
    Object.values(data.time_series_data).forEach(categoryData => {
      categoryData.forEach(point => {
        allDates.add(point.date);
      });
    });

    // Create data points for all dates
    const formattedData = Array.from(allDates).sort().map(date => {
      const dataPoint = { date };

      // Add values for each category
      Object.entries(data.time_series_data).forEach(([category, categoryData]) => {
        const point = categoryData.find(p => p.date === date);
        if (point) {
          dataPoint[category] = point.amount;
          dataPoint[`${category}_source`] = point.source;
        } else {
          dataPoint[category] = null;
        }
      });

      return dataPoint;
    });

    return formattedData;
  };

  const chartData = formatChartData();

  // Find date where predictions start
  const findPredictionStartDate = () => {
    if (!data || !data.period) return null;
    return data.period.prediction_start_date;
  };

  const predictionStartDate = findPredictionStartDate();

  // Handle category toggle
  const handleCategoryToggle = (category) => {
    setSelectedCategories({
      ...selectedCategories,
      [category]: !selectedCategories[category]
    });
  };

  // Generate a different color for each category
  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#0088fe', '#00C49F', '#FFBB28', '#FF8042'];

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip" style={{
          backgroundColor: 'white',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '4px'
        }}>
          <p className="label">{`Date: ${label}`}</p>
          {payload.map((entry, index) => {
            const isHistorical = entry.payload[`${entry.name}_source`] === 'historical';
            return (
              <p key={`item-${index}`} style={{ color: entry.color }}>
                {`${entry.name}: ${formatCurrency(entry.value)}`}
                <span style={{
                  fontSize: '0.8em',
                  marginLeft: '5px',
                  color: isHistorical ? 'green' : 'blue'
                }}>
                  ({isHistorical ? 'Historical' : 'Predicted'})
                </span>
              </p>
            );
          })}
        </div>
      );
    }
    return null;
  };

  if (!data || !chartData.length) {
    return <Typography>No time series data available</Typography>;
  }

  return (
    <Box sx={{ width: '100%', height: '100%' }}>
      <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap' }}>
        {data.top_categories && data.top_categories.map((category, index) => (
          <FormControlLabel
            key={category}
            control={
              <Checkbox
                checked={selectedCategories[category] || false}
                onChange={() => handleCategoryToggle(category)}
                style={{ color: COLORS[index % COLORS.length] }}
              />
            }
            label={category}
            sx={{ mr: 2 }}
          />
        ))}
      </Box>

      <ResponsiveContainer width="100%" height="90%">
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis tickFormatter={formatCurrency} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />

          {/* Historical vs prediction divider */}
          {predictionStartDate && (
            <ReferenceArea
              x1={predictionStartDate}
              x2={chartData[chartData.length - 1].date}
              fill="#f5f5f5"
              fillOpacity={0.3}
            />
          )}

          {data.top_categories && data.top_categories.map((category, index) => {
            if (!selectedCategories[category]) return null;

            return (
              <Line
                key={category}
                type="monotone"
                dataKey={category}
                stroke={COLORS[index % COLORS.length]}
                activeDot={{ r: 8 }}
                connectNulls
                strokeWidth={2}
                dot={(props) => {
                  if (!props.payload) return null;
                  const source = props.payload[`${category}_source`];
                  // Different dot styles for historical vs predicted
                  if (source === 'predicted') {
                    return (
                      <circle
                        cx={props.cx}
                        cy={props.cy}
                        r={4}
                        fill={props.stroke}
                        stroke="white"
                        strokeWidth={2}
                      />
                    );
                  }
                  return (
                    <circle
                      cx={props.cx}
                      cy={props.cy}
                      r={4}
                      fill={props.stroke}
                    />
                  );
                }}
              />
            );
          })}
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default TimeSeriesChart;
