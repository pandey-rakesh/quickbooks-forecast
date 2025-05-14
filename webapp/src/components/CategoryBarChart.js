import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LabelList,
  Legend
} from 'recharts';
import { formatCurrency } from '../utils/formatters';

const CategoryBarChart = ({ data, showYoYComparison = false }) => {
  // Format data for the chart based on the data type
  const chartData = showYoYComparison
    ? data.map(item => ({
        name: item.category,
        current: item.current_revenue,
        lastYear: item.last_year_revenue,
        yoyChange: item.yoy_change_percent
      }))
    : data.map(item => ({
        name: item.category,
        value: item.revenue ? item.revenue : item.amount,
      }));

  // Custom tooltip for YoY comparison
  const CustomTooltipYoY = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const current = payload.find(p => p.dataKey === 'current');
      const lastYear = payload.find(p => p.dataKey === 'lastYear');
      const yoyChange = payload[0].payload.yoyChange;

      return (
        <div className="custom-tooltip" style={{
          backgroundColor: 'white',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '4px'
        }}>
          <p style={{ margin: '0 0 5px 0', fontWeight: 'bold' }}>{payload[0].payload.name}</p>
          <p style={{ margin: '0 0 5px 0' }}>{`Current: ${formatCurrency(current?.value || 0)}`}</p>
          <p style={{ margin: '0 0 5px 0' }}>{`Last Year: ${formatCurrency(lastYear?.value || 0)}`}</p>
          {yoyChange !== null && (
            <p style={{
              margin: 0,
              color: yoyChange >= 0 ? 'green' : 'red'
            }}>
              {`YoY Change: ${yoyChange >= 0 ? '+' : ''}${yoyChange?.toFixed(1)}%`}
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  // Regular tooltip
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

  // Render different chart based on data type
  if (showYoYComparison) {
    return (
      <ResponsiveContainer width="95%" height={data.length * 70}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 20, right: 60, left: 20, bottom: 5 }}
          barGap={0} // No gap between bars in the same category
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} />
          <XAxis type="number" tickFormatter={formatCurrency} />
          <YAxis
            dataKey="name"
            type="category"
            tick={{ fontSize: 14, fontWeight: 'bold' }} // Increased font size and made bold
            width={110} // Increased width to accommodate larger text
            axisLine={true}
          />
          <Tooltip content={<CustomTooltipYoY />} />
          <Legend />
          <Bar
            dataKey="current"
            name="Current Forecast"
            fill="#8884d8"
            radius={[0, 4, 4, 0]}
            barSize={24}
          >
            <LabelList
              dataKey="current"
              position="right"
              formatter={formatCurrency}
              style={{ fontSize: 12, fill: '#333', fontWeight: 'bold'}}
              offset={10}
            />
          </Bar>
          <Bar
            dataKey="lastYear"
            name="Last Year"
            fill="#82ca9d"
            radius={[0, 4, 4, 0]}
            barSize={24}
          />
        </BarChart>
      </ResponsiveContainer>
    );
  }

  // Original chart
  return (
    <ResponsiveContainer width="95%" height={data.length * 70}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 20, right: 60, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
        <XAxis type="number" tickFormatter={formatCurrency} />
        <YAxis
          dataKey="name"
          type="category"
          tick={{ fontSize: 14, fontWeight: 'bold' }} // Increased font size and made bold
          width={110} // Increased width to accommodate larger text
          axisLine={true}
        />
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
