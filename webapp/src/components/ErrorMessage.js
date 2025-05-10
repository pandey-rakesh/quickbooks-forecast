import React from 'react';
import { Alert, AlertTitle, Box, Button } from '@mui/material';

const ErrorMessage = ({ message, retryFunction }) => {
  return (
    <Box sx={{ mt: 2, mb: 2 }}>
      <Alert
        severity="error"
        action={
          retryFunction ? (
            <Button color="inherit" size="small" onClick={retryFunction}>
              Retry
            </Button>
          ) : undefined
        }
      >
        <AlertTitle>Error</AlertTitle>
        {message || 'An unexpected error occurred.'}
      </Alert>
    </Box>
  );
};

export default ErrorMessage;
