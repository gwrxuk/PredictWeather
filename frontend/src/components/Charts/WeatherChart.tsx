import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import { Box, Typography, CircularProgress } from '@mui/material';
import { useWeatherHistory } from '../../hooks/useWeatherData';
import { format } from 'date-fns';

interface WeatherChartProps {
  location: string;
  days?: number;
  type?: 'line' | 'area';
}

const WeatherChart: React.FC<WeatherChartProps> = ({ 
  location, 
  days = 7, 
  type = 'line' 
}) => {
  const { data: weatherHistory, isLoading, error } = useWeatherHistory(location, days);

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !weatherHistory || weatherHistory.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
        <Typography variant="body1" color="text.secondary">
          No weather data available for {location}
        </Typography>
      </Box>
    );
  }

  // Process data for chart
  const chartData = weatherHistory
    .slice()
    .reverse() // Show oldest to newest
    .map((item, index) => ({
      time: format(new Date(item.timestamp), 'MMM dd HH:mm'),
      temperature: item.temperature,
      humidity: item.humidity,
      pressure: item.pressure / 10, // Scale down for better visualization
      windSpeed: item.wind_speed,
      precipitation: item.precipitation,
    }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          backgroundColor: 'white',
          padding: '12px',
          border: '1px solid #ccc',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <p style={{ margin: '0 0 8px 0', fontWeight: 'bold' }}>{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ 
              margin: '4px 0', 
              color: entry.color,
              fontSize: '14px'
            }}>
              {entry.name}: {entry.value}
              {entry.dataKey === 'temperature' && '°C'}
              {entry.dataKey === 'humidity' && '%'}
              {entry.dataKey === 'pressure' && ' hPa'}
              {entry.dataKey === 'windSpeed' && ' km/h'}
              {entry.dataKey === 'precipitation' && ' mm'}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const ChartComponent = type === 'area' ? AreaChart : LineChart;
  const DataComponent = type === 'area' ? Area : Line;

  return (
    <Box sx={{ width: '100%', height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <ChartComponent
          data={chartData}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="time" 
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {type === 'area' ? (
            <>
              <Area
                type="monotone"
                dataKey="temperature"
                stackId="1"
                stroke="#ff6b6b"
                fill="#ff6b6b"
                fillOpacity={0.3}
                name="Temperature"
              />
              <Area
                type="monotone"
                dataKey="humidity"
                stackId="2"
                stroke="#4ecdc4"
                fill="#4ecdc4"
                fillOpacity={0.3}
                name="Humidity"
              />
            </>
          ) : (
            <>
              <Line
                type="monotone"
                dataKey="temperature"
                stroke="#ff6b6b"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="Temperature (°C)"
              />
              <Line
                type="monotone"
                dataKey="humidity"
                stroke="#4ecdc4"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="Humidity (%)"
              />
              <Line
                type="monotone"
                dataKey="pressure"
                stroke="#45b7d1"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="Pressure (hPa/10)"
              />
              <Line
                type="monotone"
                dataKey="windSpeed"
                stroke="#f9ca24"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="Wind Speed (km/h)"
              />
              <Line
                type="monotone"
                dataKey="precipitation"
                stroke="#6c5ce7"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="Precipitation (mm)"
              />
            </>
          )}
        </ChartComponent>
      </ResponsiveContainer>
    </Box>
  );
};

export default WeatherChart;
