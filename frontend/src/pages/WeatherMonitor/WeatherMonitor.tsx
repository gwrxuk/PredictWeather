import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const WeatherMonitor: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Weather Monitor
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Real-time weather monitoring dashboard coming soon...
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default WeatherMonitor;
