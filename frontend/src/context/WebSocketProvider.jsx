// src/context/WebSocketProvider.jsx
import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { WebSocketContext } from './WebSocketContext';

export const WebSocketProvider = ({ children }) => {
  const { user, accessToken } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const wsRef = useRef(null);
  const reconnectTimeout = useRef(null);
  const connectRef = useRef(null);

  const connect = useCallback(() => {
    if (!accessToken || !user) return;

    if (wsRef.current) {
      wsRef.current.close();
    }

    const ws = new WebSocket(`ws://localhost:8000/ws/notifications/?token=${accessToken}`);

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setMessages((prev) => [...prev, data]);
      } catch (e) {
        console.error('WebSocket message parse error:', e);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      reconnectTimeout.current = setTimeout(() => {
        if (connectRef.current) {
          connectRef.current();
        }
      }, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      ws.close();
    };

    wsRef.current = ws;
  }, [accessToken, user]);

  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
    };
  }, [connect]);

  const sendMessage = useCallback((data) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  return (
    <WebSocketContext.Provider value={{ isConnected, messages, sendMessage }}>
      {children}
    </WebSocketContext.Provider>
  );
};