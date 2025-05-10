import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import { formatCurrency, formatPercentage } from '../utils/formatters';

const CategoryTable = ({ categories }) => {
  return (
    <TableContainer component={Paper} sx={{ maxHeight: 440 }}>
      <Table stickyHeader aria-label="categories table">
        <TableHead>
          <TableRow>
            <TableCell>Rank</TableCell>
            <TableCell>Category</TableCell>
            <TableCell align="right">Revenue</TableCell>
            <TableCell align="right">% of Total</TableCell>
            {categories[0]?.confidence && (
              <TableCell align="right">Confidence</TableCell>
            )}
          </TableRow>
        </TableHead>
        <TableBody>
          {categories.map((category, index) => (
            <TableRow
              key={category.category}
              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
            >
              <TableCell component="th" scope="row">
                {index + 1}
              </TableCell>
              <TableCell>{category.category}</TableCell>
              <TableCell align="right">
                {formatCurrency(category.revenue || category.amount)}
              </TableCell>
              <TableCell align="right">
                {formatPercentage(category.percentage)}
              </TableCell>
              {category.confidence && (
                <TableCell align="right">
                  {formatPercentage(category.confidence * 100)}
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default CategoryTable;
