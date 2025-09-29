import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const Predictions: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Weather Predictions
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            AI-powered weather predictions and threat analysis coming soon...
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Predictions;
