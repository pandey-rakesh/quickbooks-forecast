import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box
} from '@mui/material';
import {Link} from 'react-router-dom';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

const Header = () => {
  return (
      <AppBar position="static" color="primary" elevation={0}>
        <Toolbar>
          <Box sx={{display: 'flex', alignItems: 'center'}}>
            <TrendingUpIcon sx={{mr: 1, fontSize: 32}}/>
            <Typography variant="h4" component={Link} to="/" sx={{textDecoration: 'none', color: 'white'}}>
              quickbooks
            </Typography>
          </Box>

          <Box sx={{flexGrow: 1}}/>

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
