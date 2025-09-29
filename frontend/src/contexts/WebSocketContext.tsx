import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { toast } from 'react-toastify';

interface WebSocketMessage {
  type: string;
  data?: any;
  subscription_type?: string;
  timestamp?: string;
  priority?: string;
}

interface WebSocketContextType {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  subscribe: (subscriptionType: string) => void;
  unsubscribe: (subscriptionType: string) => void;
  sendMessage: (message: any) => void;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

interface WebSocketProviderProps {
  children: ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [subscriptions, setSubscriptions] = useState<Set<string>>(new Set());

  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000; // 3 seconds

  const connect = useCallback(() => {
    if (socket?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnectionStatus('connecting');
    
    // Use WebSocket for real-time communication
    // In production, this would be wss:// and the actual backend WebSocket endpoint
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
    const newSocket = new WebSocket(`${wsUrl}/dashboard`);

    newSocket.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      setConnectionStatus('connected');
      setReconnectAttempts(0);
      
      // Resubscribe to previous subscriptions
      subscriptions.forEach(subscription => {
        newSocket.send(JSON.stringify({
          type: 'subscribe',
          subscription_type: subscription
        }));
      });
    };

    newSocket.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        setLastMessage(message);
        
        // Handle different message types
        handleMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    newSocket.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      setIsConnected(false);
      setSocket(null);
      
      if (event.code !== 1000) { // Not a normal closure
        setConnectionStatus('error');
        attemptReconnect();
      } else {
        setConnectionStatus('disconnected');
      }
    };

    newSocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('error');
    };

    setSocket(newSocket);
  }, [socket, subscriptions]);

  const attemptReconnect = useCallback(() => {
    if (reconnectAttempts < maxReconnectAttempts) {
      setTimeout(() => {
        console.log(`Attempting to reconnect... (${reconnectAttempts + 1}/${maxReconnectAttempts})`);
        setReconnectAttempts(prev => prev + 1);
        connect();
      }, reconnectDelay);
    } else {
      console.log('Max reconnection attempts reached');
      setConnectionStatus('error');
      toast.error('Unable to connect to real-time updates. Please refresh the page.');
    }
  }, [reconnectAttempts, connect]);

  const handleMessage = (message: WebSocketMessage) => {
    switch (message.type) {
      case 'weather_update':
        // Handle weather updates
        break;
      
      case 'alert':
        // Handle weather alerts
        if (message.data) {
          const severity = message.data.severity || 'info';
          const alertMessage = message.data.title || 'New weather alert';
          
          if (severity === 'critical') {
            toast.error(alertMessage, { autoClose: false });
          } else if (severity === 'high') {
            toast.warning(alertMessage);
          } else {
            toast.info(alertMessage);
          }
        }
        break;
      
      case 'prediction':
        // Handle weather predictions
        break;
      
      case 'blockchain_event':
        // Handle blockchain events
        if (message.data) {
          toast.success(`Blockchain: ${message.data.message || 'Transaction confirmed'}`);
        }
        break;
      
      case 'emergency_event':
        // Handle emergency events
        if (message.data) {
          toast.error(`Emergency: ${message.data.message || 'Emergency event detected'}`, {
            autoClose: false
          });
        }
        break;
      
      case 'connection':
      case 'subscription':
      case 'unsubscription':
        // Handle connection status messages
        console.log(message.message);
        break;
      
      case 'error':
        console.error('WebSocket error:', message.message);
        toast.error(`Connection error: ${message.message}`);
        break;
      
      default:
        console.log('Unknown message type:', message.type);
    }
  };

  const subscribe = useCallback((subscriptionType: string) => {
    setSubscriptions(prev => new Set([...prev, subscriptionType]));
    
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'subscribe',
        subscription_type: subscriptionType
      }));
    }
  }, [socket]);

  const unsubscribe = useCallback((subscriptionType: string) => {
    setSubscriptions(prev => {
      const newSet = new Set(prev);
      newSet.delete(subscriptionType);
      return newSet;
    });
    
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'unsubscribe',
        subscription_type: subscriptionType
      }));
    }
  }, [socket]);

  const sendMessage = useCallback((message: any) => {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message);
    }
  }, [socket]);

  // Connect on mount
  useEffect(() => {
    connect();
    
    // Cleanup on unmount
    return () => {
      if (socket) {
        socket.close(1000, 'Component unmounting');
      }
    };
  }, []);

  // Subscribe to default channels
  useEffect(() => {
    if (isConnected) {
      // Subscribe to essential channels
      subscribe('weather_updates');
      subscribe('alerts');
      subscribe('emergency_events');
    }
  }, [isConnected, subscribe]);

  const value: WebSocketContextType = {
    isConnected,
    lastMessage,
    subscribe,
    unsubscribe,
    sendMessage,
    connectionStatus,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = (): WebSocketContextType => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};
