import { useQuery } from 'react-query';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

interface WeatherData {
  location: string;
  temperature: number;
  humidity: number;
  pressure: number;
  wind_speed: number;
  wind_direction?: number;
  precipitation: number;
  weather_type: string;
  weather_description?: string;
  timestamp: string;
  source: string;
}

interface WeatherAnalysis {
  summary: {
    total_records: number;
    date_range: {
      start: string;
      end: string;
    };
    locations: string[];
  };
  statistics: Record<string, any>;
  trends: Record<string, any>;
  anomalies: any[];
  risk_assessment: {
    flood_risk: number;
    drought_risk: number;
    storm_risk: number;
    extreme_temperature_risk: number;
  };
}

interface WeatherPrediction {
  location: string;
  prediction_time: string;
  forecast_hours: number;
  predictions: Record<string, any>;
  confidence: number;
  model_version: string;
  risk_assessment: {
    flood_risk: number;
    drought_risk: number;
    storm_risk: number;
    extreme_temperature_risk: number;
  };
}

interface WeatherResponse {
  current?: WeatherData;
  history?: WeatherData[];
  analysis?: WeatherAnalysis;
  prediction?: WeatherPrediction;
  risk_assessment?: {
    flood_risk: number;
    drought_risk: number;
    storm_risk: number;
    extreme_temperature_risk: number;
  };
}

const fetchCurrentWeather = async (location: string): Promise<WeatherData> => {
  const response = await axios.get(`${API_BASE_URL}/weather/current/${encodeURIComponent(location)}`);
  return response.data;
};

const fetchWeatherHistory = async (location: string, days: number = 7): Promise<WeatherData[]> => {
  const response = await axios.get(`${API_BASE_URL}/weather/history/${encodeURIComponent(location)}`, {
    params: { days }
  });
  return response.data.data;
};

const fetchWeatherAnalysis = async (location: string): Promise<WeatherAnalysis> => {
  const response = await axios.get(`${API_BASE_URL}/weather/analysis/${encodeURIComponent(location)}`);
  return response.data.analysis;
};

const fetchWeatherPrediction = async (location: string): Promise<WeatherPrediction> => {
  const response = await axios.get(`${API_BASE_URL}/weather/prediction/${encodeURIComponent(location)}`);
  return response.data;
};

export const useWeatherData = (location: string) => {
  return useQuery(
    ['weather', 'current', location],
    () => fetchCurrentWeather(location),
    {
      enabled: !!location,
      refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
      staleTime: 2 * 60 * 1000, // Consider data stale after 2 minutes
      onError: (error) => {
        console.error('Error fetching weather data:', error);
      },
      select: (data): WeatherResponse => ({
        current: data,
        risk_assessment: {
          flood_risk: Math.random() * 0.8, // Mock data
          drought_risk: Math.random() * 0.6,
          storm_risk: Math.random() * 0.7,
          extreme_temperature_risk: Math.random() * 0.5,
        }
      })
    }
  );
};

export const useWeatherHistory = (location: string, days: number = 7) => {
  return useQuery(
    ['weather', 'history', location, days],
    () => fetchWeatherHistory(location, days),
    {
      enabled: !!location,
      staleTime: 10 * 60 * 1000, // Consider data stale after 10 minutes
      onError: (error) => {
        console.error('Error fetching weather history:', error);
      }
    }
  );
};

export const useWeatherAnalysis = (location: string) => {
  return useQuery(
    ['weather', 'analysis', location],
    () => fetchWeatherAnalysis(location),
    {
      enabled: !!location,
      staleTime: 15 * 60 * 1000, // Consider data stale after 15 minutes
      onError: (error) => {
        console.error('Error fetching weather analysis:', error);
      }
    }
  );
};

export const useWeatherPrediction = (location: string) => {
  return useQuery(
    ['weather', 'prediction', location],
    () => fetchWeatherPrediction(location),
    {
      enabled: !!location,
      staleTime: 30 * 60 * 1000, // Consider data stale after 30 minutes
      onError: (error) => {
        console.error('Error fetching weather prediction:', error);
      }
    }
  );
};

// Hook for submitting weather data
export const useSubmitWeatherData = () => {
  const submitWeatherData = async (weatherData: Partial<WeatherData>) => {
    const response = await axios.post(`${API_BASE_URL}/weather/data`, weatherData);
    return response.data;
  };

  return { submitWeatherData };
};

// Hook for fetching weather alerts
export const useWeatherAlerts = (location?: string) => {
  return useQuery(
    ['weather', 'alerts', location],
    async () => {
      const response = await axios.get(`${API_BASE_URL}/weather/alerts`, {
        params: location ? { location } : {}
      });
      return response.data.alerts;
    },
    {
      refetchInterval: 2 * 60 * 1000, // Refetch every 2 minutes
      staleTime: 1 * 60 * 1000, // Consider data stale after 1 minute
      onError: (error) => {
        console.error('Error fetching weather alerts:', error);
      }
    }
  );
};

// Hook for fetching weather stations
export const useWeatherStations = () => {
  return useQuery(
    ['weather', 'stations'],
    async () => {
      const response = await axios.get(`${API_BASE_URL}/weather/stations`);
      return response.data.stations;
    },
    {
      staleTime: 30 * 60 * 1000, // Consider data stale after 30 minutes
      onError: (error) => {
        console.error('Error fetching weather stations:', error);
      }
    }
  );
};
