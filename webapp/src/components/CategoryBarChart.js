import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LabelList
} from 'recharts';
import { formatCurrency } from '../utils/formatters';

const CategoryBarChart = ({ data }) => {
  // Format data for the chart
  const chartData = data.map(item => ({
    name: item.category,
    value: item.revenue ? item.revenue : item.amount,
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip" style={{
          backgroundColor: 'white',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '4px'
        }}>
          <p className="value" style={{ margin: 0 }}>{`Revenue: ${formatCurrency(payload[0].value)}`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="95%" height="100%">
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 20, right: 60, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
        <XAxis type="number" tickFormatter={formatCurrency} />
        <YAxis dataKey="name" type="category" tick={{ fontSize: 12 }} width={90} />
        <Tooltip content={<CustomTooltip />} />
        <Bar
          dataKey="value"
          fill="#8884d8"
          radius={[0, 4, 4, 0]}
          barSize={30}
        >
          <LabelList
           dataKey="value"
           position="right"
           formatter={formatCurrency}
           style={{ fontSize: 14, fill: '#333', fontWeight: 'bold'}}
           offset={10}
         />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

export default CategoryBarChart;
