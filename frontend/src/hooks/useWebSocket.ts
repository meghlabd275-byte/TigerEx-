"use client"
import { useWebSocket as useWebSocketContext } from '@/contexts/WebSocketContext';

export const useWebSocket = (url?: string) => {
  const context = useWebSocketContext();
  
  return {
    isConnected: context.connectionStatus === 'connected',
    subscribe: context.subscribeToSymbol,
    unsubscribe: context.unsubscribeFromSymbol,
    sendMessage: context.sendOrder,
    connectionStatus: context.connectionStatus,
    notifications: context.notifications,
    clearNotifications: context.clearNotifications,
  };
};
