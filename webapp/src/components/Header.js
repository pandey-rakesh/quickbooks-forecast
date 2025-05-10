import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box
} from '@mui/material';
import { Link } from 'react-router-dom';
import ShowChartIcon from '@mui/icons-material/ShowChart';

const Header = () => {
  return (
    <AppBar position="static" color="primary" elevation={0}>
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <ShowChartIcon sx={{ mr: 1 }} />
          <Typography variant="h4" component={Link} to="/" sx={{ textDecoration: 'none', color: 'white' }}>
            QuickBooks
          </Typography>
        </Box>

        <Box sx={{ flexGrow: 1 }} />

        <Box>
          <Button color="inherit" component={Link} to="/">
            Dashboard
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
