import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const Insurance: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Weather Insurance
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Parametric weather insurance platform coming soon...
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Insurance;
