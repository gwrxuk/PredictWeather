import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const Emergency: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Emergency Response
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Emergency resource allocation and coordination platform coming soon...
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Emergency;
