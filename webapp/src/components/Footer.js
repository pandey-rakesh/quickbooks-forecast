import React from 'react';
import { Box, Typography, Link } from '@mui/material';

const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: (theme) => theme.palette.grey[100]
      }}
    >
      <Typography variant="body2" color="text.secondary" align="center">
        {'© '}
        {new Date().getFullYear()}
        {' '}
        <Link color="inherit" href="#">
          QuickBooks Commerce
        </Link>
        {' | Sales Forecasting Dashboard'}
      </Typography>
    </Box>
  );
};

export default Footer;
