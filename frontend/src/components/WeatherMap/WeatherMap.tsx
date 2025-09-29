import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import { Icon } from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in react-leaflet
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix default icon
const DefaultIcon = new Icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

interface WeatherMapProps {
  center: [number, number];
  zoom: number;
  onLocationSelect?: (location: string) => void;
}

interface WeatherStation {
  id: number;
  name: string;
  location: string;
  latitude: number;
  longitude: number;
  temperature?: number;
  weather_type?: string;
  risk_level?: 'low' | 'medium' | 'high' | 'critical';
}

const WeatherMap: React.FC<WeatherMapProps> = ({ center, zoom, onLocationSelect }) => {
  const [weatherStations, setWeatherStations] = useState<WeatherStation[]>([]);
  const [selectedPosition, setSelectedPosition] = useState<[number, number] | null>(null);

  useEffect(() => {
    // Mock weather stations data
    setWeatherStations([
      {
        id: 1,
        name: 'Central Park Station',
        location: 'New York, NY',
        latitude: 40.7829,
        longitude: -73.9654,
        temperature: 22,
        weather_type: 'sunny',
        risk_level: 'low'
      },
      {
        id: 2,
        name: 'Brooklyn Station',
        location: 'Brooklyn, NY',
        latitude: 40.6782,
        longitude: -73.9442,
        temperature: 21,
        weather_type: 'cloudy',
        risk_level: 'medium'
      },
      {
        id: 3,
        name: 'Queens Station',
        location: 'Queens, NY',
        latitude: 40.7282,
        longitude: -73.7949,
        temperature: 23,
        weather_type: 'rainy',
        risk_level: 'high'
      },
      {
        id: 4,
        name: 'Manhattan Station',
        location: 'Manhattan, NY',
        latitude: 40.7831,
        longitude: -73.9712,
        temperature: 20,
        weather_type: 'stormy',
        risk_level: 'critical'
      }
    ]);
  }, []);

  const getMarkerColor = (riskLevel?: string) => {
    switch (riskLevel) {
      case 'critical': return '#d32f2f';
      case 'high': return '#f57c00';
      case 'medium': return '#1976d2';
      case 'low': return '#388e3c';
      default: return '#757575';
    }
  };

  const getWeatherEmoji = (weatherType?: string) => {
    switch (weatherType) {
      case 'sunny': return '☀️';
      case 'cloudy': return '☁️';
      case 'rainy': return '🌧️';
      case 'stormy': return '⛈️';
      case 'snowy': return '❄️';
      default: return '🌤️';
    }
  };

  const createCustomIcon = (riskLevel?: string) => {
    const color = getMarkerColor(riskLevel);
    return new Icon({
      iconUrl: `data:image/svg+xml;base64,${btoa(`
        <svg width="25" height="41" viewBox="0 0 25 41" xmlns="http://www.w3.org/2000/svg">
          <path d="M12.5 0C5.6 0 0 5.6 0 12.5c0 12.5 12.5 28.5 12.5 28.5s12.5-16 12.5-28.5C25 5.6 19.4 0 12.5 0z" fill="${color}"/>
          <circle cx="12.5" cy="12.5" r="8" fill="white"/>
        </svg>
      `)}`,
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
    });
  };

  // Component to handle map clicks
  const MapClickHandler = () => {
    useMapEvents({
      click: (e) => {
        const { lat, lng } = e.latlng;
        setSelectedPosition([lat, lng]);
        
        // Reverse geocoding would go here in a real app
        const locationName = `Location ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
        onLocationSelect?.(locationName);
      },
    });
    return null;
  };

  return (
    <div style={{ height: '400px', width: '100%', borderRadius: '12px', overflow: 'hidden' }}>
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapClickHandler />
        
        {/* Weather stations */}
        {weatherStations.map((station) => (
          <Marker
            key={station.id}
            position={[station.latitude, station.longitude]}
            icon={createCustomIcon(station.risk_level)}
          >
            <Popup>
              <div style={{ minWidth: '200px' }}>
                <h3 style={{ margin: '0 0 8px 0', color: getMarkerColor(station.risk_level) }}>
                  {station.name}
                </h3>
                <p style={{ margin: '4px 0' }}>
                  <strong>Location:</strong> {station.location}
                </p>
                {station.temperature && (
                  <p style={{ margin: '4px 0' }}>
                    <strong>Temperature:</strong> {station.temperature}°C
                  </p>
                )}
                {station.weather_type && (
                  <p style={{ margin: '4px 0' }}>
                    <strong>Weather:</strong> {getWeatherEmoji(station.weather_type)} {station.weather_type}
                  </p>
                )}
                <p style={{ margin: '4px 0' }}>
                  <strong>Risk Level:</strong> 
                  <span style={{ 
                    color: getMarkerColor(station.risk_level),
                    fontWeight: 'bold',
                    textTransform: 'capitalize',
                    marginLeft: '4px'
                  }}>
                    {station.risk_level}
                  </span>
                </p>
                <button
                  onClick={() => onLocationSelect?.(station.location)}
                  style={{
                    marginTop: '8px',
                    padding: '4px 8px',
                    backgroundColor: '#1976d2',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Select Location
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
        
        {/* Selected position marker */}
        {selectedPosition && (
          <Marker position={selectedPosition} icon={DefaultIcon}>
            <Popup>
              <div>
                <h4>Selected Location</h4>
                <p>Lat: {selectedPosition[0].toFixed(4)}</p>
                <p>Lng: {selectedPosition[1].toFixed(4)}</p>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
};

export default WeatherMap;
