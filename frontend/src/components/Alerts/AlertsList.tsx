import React from 'react';
import {
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  AlertTitle,
  Chip,
  Box,
  Typography,
  CircularProgress,
} from '@mui/material';
import {
  Warning,
  Error,
  Info,
  CheckCircle,
  WaterDrop,
  Air,
  Thermostat,
  Flash,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { useWeatherAlerts } from '../../hooks/useWeatherData';

interface AlertsListProps {
  location?: string;
  maxItems?: number;
}

const AlertsList: React.FC<AlertsListProps> = ({ location, maxItems = 5 }) => {
  const { data: alerts, isLoading, error } = useWeatherAlerts(location);

  const getAlertIcon = (alertType: string) => {
    switch (alertType.toLowerCase()) {
      case 'flood':
        return <WaterDrop />;
      case 'storm':
        return <Flash />;
      case 'drought':
        return <Thermostat />;
      case 'wind':
        return <Air />;
      default:
        return <Warning />;
    }
  };

  const getAlertSeverity = (severity: string): 'error' | 'warning' | 'info' | 'success' => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'error';
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'info';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'error';
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
        <CircularProgress size={24} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        <AlertTitle>Error Loading Alerts</AlertTitle>
        Unable to fetch weather alerts. Please try again later.
      </Alert>
    );
  }

  if (!alerts || alerts.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', p: 2 }}>
        <CheckCircle sx={{ fontSize: 48, color: 'success.main', mb: 1 }} />
        <Typography variant="body2" color="text.secondary">
          No active weather alerts
        </Typography>
        <Typography variant="caption" color="text.secondary">
          All systems normal
        </Typography>
      </Box>
    );
  }

  const displayAlerts = alerts.slice(0, maxItems);

  return (
    <Box>
      {displayAlerts.map((alert, index) => (
        <Alert
          key={alert.id || index}
          severity={getAlertSeverity(alert.severity)}
          sx={{ 
            mb: 1,
            '&:last-child': { mb: 0 }
          }}
          icon={getAlertIcon(alert.type)}
        >
          <AlertTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {alert.title}
            <Chip
              label={alert.severity}
              color={getSeverityColor(alert.severity) as any}
              size="small"
            />
          </AlertTitle>
          
          <Typography variant="body2" sx={{ mb: 1 }}>
            {alert.description}
          </Typography>
          
          {alert.instructions && (
            <Typography variant="body2" sx={{ fontStyle: 'italic', mb: 1 }}>
              <strong>Instructions:</strong> {alert.instructions}
            </Typography>
          )}
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
            <Typography variant="caption" color="text.secondary">
              📍 {alert.location}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {format(new Date(alert.start_time), 'MMM dd, HH:mm')}
            </Typography>
          </Box>
        </Alert>
      ))}
      
      {alerts.length > maxItems && (
        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Typography variant="caption" color="text.secondary">
            +{alerts.length - maxItems} more alerts
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default AlertsList;
