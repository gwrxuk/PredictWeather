import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Alert,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Cloud,
  Thermostat,
  Water,
  Air,
  Warning,
  Security,
  AccountBalance,
  Emergency,
  Refresh,
  TrendingUp,
  LocationOn,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

import WeatherMap from '../../components/WeatherMap/WeatherMap';
import WeatherChart from '../../components/Charts/WeatherChart';
import AlertsList from '../../components/Alerts/AlertsList';
import { useWeatherData } from '../../hooks/useWeatherData';
import { useBlockchainData } from '../../hooks/useBlockchainData';
import { useWebSocket } from '../../contexts/WebSocketContext';

const Dashboard: React.FC = () => {
  const [selectedLocation, setSelectedLocation] = useState('New York, NY');
  const { weatherData, isLoading: weatherLoading, refetch: refetchWeather } = useWeatherData(selectedLocation);
  const { blockchainStatus, isLoading: blockchainLoading } = useBlockchainData();
  const { isConnected, lastMessage } = useWebSocket();

  const [systemStats, setSystemStats] = useState({
    totalStations: 0,
    verifiedData: 0,
    activePolicies: 0,
    emergencyRequests: 0,
  });

  useEffect(() => {
    // Simulate fetching system statistics
    setSystemStats({
      totalStations: 45,
      verifiedData: 1247,
      activePolicies: 89,
      emergencyRequests: 3,
    });
  }, []);

  const currentWeather = weatherData?.current;
  const riskAssessment = weatherData?.risk_assessment || {};

  const getRiskColor = (risk: number) => {
    if (risk >= 0.8) return 'error';
    if (risk >= 0.6) return 'warning';
    if (risk >= 0.3) return 'info';
    return 'success';
  };

  const getRiskLabel = (risk: number) => {
    if (risk >= 0.8) return 'Critical';
    if (risk >= 0.6) return 'High';
    if (risk >= 0.3) return 'Medium';
    return 'Low';
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          WeatherGuard Dashboard
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Chip
            icon={<div className={`status-indicator ${isConnected ? 'status-online' : 'status-offline'}`} />}
            label={isConnected ? 'Connected' : 'Disconnected'}
            color={isConnected ? 'success' : 'error'}
            variant="outlined"
          />
          <Tooltip title="Refresh Data">
            <IconButton onClick={() => refetchWeather()}>
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* System Status Alert */}
      {riskAssessment.flood_risk > 0.7 && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="fade-in"
        >
          <Alert severity="error" sx={{ mb: 3 }}>
            <Typography variant="h6">High Flood Risk Detected</Typography>
            <Typography>
              Current flood risk level is {(riskAssessment.flood_risk * 100).toFixed(1)}% in {selectedLocation}.
              Emergency protocols have been activated.
            </Typography>
          </Alert>
        </motion.div>
      )}

      <Grid container spacing={3}>
        {/* Current Weather Card */}
        <Grid item xs={12} md={6} lg={3}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="interactive-card">
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Thermostat sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">Current Weather</Typography>
                </Box>
                {weatherLoading ? (
                  <LinearProgress />
                ) : currentWeather ? (
                  <>
                    <Typography variant="h3" component="div" sx={{ mb: 1 }}>
                      {currentWeather.temperature}°C
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {currentWeather.weather_description}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <LocationOn sx={{ fontSize: 16, mr: 0.5 }} />
                      <Typography variant="body2">{selectedLocation}</Typography>
                    </Box>
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2">
                        Humidity: {currentWeather.humidity}%
                      </Typography>
                      <Typography variant="body2">
                        Wind: {currentWeather.wind_speed} km/h
                      </Typography>
                    </Box>
                  </>
                ) : (
                  <Typography>No weather data available</Typography>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Risk Assessment Card */}
        <Grid item xs={12} md={6} lg={3}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="interactive-card">
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Warning sx={{ mr: 1, color: 'warning.main' }} />
                  <Typography variant="h6">Risk Assessment</Typography>
                </Box>
                <Box sx={{ space: 1 }}>
                  {Object.entries(riskAssessment).map(([risk, value]) => (
                    <Box key={risk} sx={{ mb: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                          {risk.replace('_risk', '').replace('_', ' ')}
                        </Typography>
                        <Chip
                          label={getRiskLabel(value as number)}
                          color={getRiskColor(value as number)}
                          size="small"
                        />
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={(value as number) * 100}
                        color={getRiskColor(value as number)}
                        sx={{ height: 6, borderRadius: 3 }}
                      />
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Blockchain Status Card */}
        <Grid item xs={12} md={6} lg={3}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="interactive-card">
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Security sx={{ mr: 1, color: 'success.main' }} />
                  <Typography variant="h6">Blockchain</Typography>
                </Box>
                {blockchainLoading ? (
                  <LinearProgress />
                ) : (
                  <>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <div className={`status-indicator ${blockchainStatus?.connected ? 'status-online' : 'status-offline'}`} />
                      <Typography variant="body2">
                        {blockchainStatus?.connected ? 'Connected' : 'Disconnected'}
                      </Typography>
                    </Box>
                    {blockchainStatus?.connected && (
                      <>
                        <Typography variant="body2" sx={{ mb: 0.5 }}>
                          Balance: {blockchainStatus.balance?.toFixed(4)} ETH
                        </Typography>
                        <Typography variant="body2">
                          Network: {blockchainStatus.network?.includes('localhost') ? 'Local' : 'Testnet'}
                        </Typography>
                      </>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* System Statistics Card */}
        <Grid item xs={12} md={6} lg={3}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="interactive-card">
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <TrendingUp sx={{ mr: 1, color: 'info.main' }} />
                  <Typography variant="h6">System Stats</Typography>
                </Box>
                <Box sx={{ space: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Weather Stations</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {systemStats.totalStations}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Verified Data</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {systemStats.verifiedData}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Active Policies</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {systemStats.activePolicies}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Emergency Requests</Typography>
                    <Chip
                      label={systemStats.emergencyRequests}
                      color={systemStats.emergencyRequests > 0 ? 'warning' : 'success'}
                      size="small"
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Weather Map */}
        <Grid item xs={12} lg={8}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Weather Map
                </Typography>
                <WeatherMap
                  center={[40.7128, -74.0060]} // New York coordinates
                  zoom={10}
                  onLocationSelect={setSelectedLocation}
                />
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Active Alerts */}
        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Active Alerts
                </Typography>
                <AlertsList />
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Weather Trends Chart */}
        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Weather Trends (Last 7 Days)
                </Typography>
                <WeatherChart location={selectedLocation} />
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
