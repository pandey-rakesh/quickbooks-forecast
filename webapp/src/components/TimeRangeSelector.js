import React, { useState } from 'react';
import { TextField } from '@mui/material';
import {
  Paper,
  ToggleButtonGroup,
  ToggleButton,
  Box,
  Typography,
  Button
} from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';

const TimeRangeSelector = ({ selectedRange, onRangeChange }) => {
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [showDatePickers, setShowDatePickers] = useState(selectedRange === 'custom');

  const handleRangeChange = (event, newRange) => {
    if (newRange === null) {
      return;
    }

    setShowDatePickers(newRange === 'custom');
    onRangeChange(newRange);

    if (newRange === 'custom' && startDate && endDate) {
      onRangeChange(newRange, { startDate: formatDate(startDate), endDate: formatDate(endDate) });
    }
  };

  const formatDate = (date) => {
    if (!date) return null;
    return date.toISOString().split('T')[0];
  };

  const handleDateSubmit = () => {
    if (startDate && endDate) {
      onRangeChange('custom', {
        startDate: formatDate(startDate),
        endDate: formatDate(endDate)
      });
    }
  };

  return (
    <Paper elevation={1} sx={{ p: 2 }}>
      <Typography variant="subtitle2" gutterBottom>
        Select Time Range
      </Typography>

      <ToggleButtonGroup
        value={selectedRange}
        exclusive
        onChange={handleRangeChange}
        aria-label="time range"
        size="small"
        sx={{ mb: showDatePickers ? 2 : 0 }}
      >
        <ToggleButton value="week" aria-label="week">
          Week
        </ToggleButton>
        <ToggleButton value="month" aria-label="month">
          Month
        </ToggleButton>
        <ToggleButton value="quarter" aria-label="quarter">
          Quarter
        </ToggleButton>
        <ToggleButton value="year" aria-label="year">
          Year
        </ToggleButton>
        <ToggleButton value="custom" aria-label="custom">
          Custom
        </ToggleButton>
      </ToggleButtonGroup>

      {showDatePickers && (
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 2, flexWrap: 'wrap' }}>
            <DatePicker
              label="Start Date"
              value={startDate}
              onChange={(newDate) => setStartDate(newDate)}
              slotProps={{ textField: { size: 'small', sx: { mr: 2, mb: { xs: 2, sm: 0 } } } }}
            />
            <DatePicker
              label="End Date"
              value={endDate}
              onChange={(newDate) => setEndDate(newDate)}
              slotProps={{ textField: { size: 'small', sx: { mr: 2, mb: { xs: 2, sm: 0 } } } }}
              minDate={startDate}
            />
            <Button
              variant="contained"
              onClick={handleDateSubmit}
              disabled={!startDate || !endDate}
              size="small"
            >
              Apply
            </Button>
          </Box>
        </LocalizationProvider>
      )}
    </Paper>
  );
};

export default TimeRangeSelector;
