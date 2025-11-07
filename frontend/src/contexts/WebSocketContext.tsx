'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode, useRef } from 'react'

interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: Date
}

interface WebSocketContextType {
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'
  notifications: Notification[]
  subscribeToSymbol: (symbol: string) => void
  unsubscribeFromSymbol: (symbol: string) => void
  sendOrder: (order: any) => void
  clearNotifications: () => void
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined)

export const useWebSocket = () => {
  const context = useContext(WebSocketContext)
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}

interface WebSocketProviderProps {
  children: ReactNode
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  const [notifications, setNotifications] = useState<Notification[]>([])
  const ws = useRef<WebSocket | null>(null)
  const subscriptions = useRef<Set<string>>(new Set())
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  useEffect(() => {
    connect()
    return () => {
      if (ws.current) {
        ws.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [])

  const connect = () => {
    try {
      setConnectionStatus('connecting')
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/ws`
      
      ws.current = new WebSocket(wsUrl)

      ws.current.onopen = () => {
        setConnectionStatus('connected')
        console.log('WebSocket connected')
        
        // Resubscribe to symbols after reconnection
        if (subscriptions.current.size > 0) {
          const subscribeMessage = {
            type: 'subscribe',
            symbols: Array.from(subscriptions.current)
          }
          ws.current?.send(JSON.stringify(subscribeMessage))
        }
      }

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          handleMessage(data)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.current.onclose = (event) => {
        setConnectionStatus('disconnected')
        console.log('WebSocket disconnected:', event.code, event.reason)
        
        // Attempt to reconnect after 5 seconds
        if (event.code !== 1000) { // Not a normal closure
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, 5000)
        }
      }

      ws.current.onerror = (error) => {
        setConnectionStatus('error')
        console.error('WebSocket error:', error)
      }

    } catch (error) {
      setConnectionStatus('error')
      console.error('Failed to create WebSocket connection:', error)
    }
  }

  const handleMessage = (data: any) => {
    switch (data.type) {
      case 'order_update':
        // Handle order updates
        addNotification({
          id: Date.now().toString(),
          type: 'info',
          title: 'Order Update',
          message: `Order ${data.data.id} status: ${data.data.status}`,
          timestamp: new Date()
        })
        break
      
      case 'trade':
        // Handle trade executions
        addNotification({
          id: Date.now().toString(),
          type: 'success',
          title: 'Trade Executed',
          message: `Trade ${data.data.id} completed`,
          timestamp: new Date()
        })
        break
      
      case 'price_update':
        // Handle price updates (managed by components)
        break
      
      case 'system_notification':
        // Handle system notifications
        addNotification({
          id: data.data.id,
          type: data.data.severity,
          title: data.data.title,
          message: data.data.message,
          timestamp: new Date(data.data.timestamp)
        })
        break
      
      default:
        console.log('Unhandled WebSocket message:', data)
    }
  }

  const addNotification = (notification: Notification) => {
    setNotifications(prev => [notification, ...prev.slice(0, 9)]) // Keep last 10 notifications
  }

  const subscribeToSymbol = (symbol: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      const message = {
        type: 'subscribe',
        symbols: [symbol]
      }
      ws.current.send(JSON.stringify(message))
      subscriptions.current.add(symbol)
    }
  }

  const unsubscribeFromSymbol = (symbol: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      const message = {
        type: 'unsubscribe',
        symbols: [symbol]
      }
      ws.current.send(JSON.stringify(message))
      subscriptions.current.delete(symbol)
    }
  }

  const sendOrder = (order: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      const message = {
        type: 'create_order',
        data: order
      }
      ws.current.send(JSON.stringify(message))
    }
  }

  const clearNotifications = () => {
    setNotifications([])
  }

  const value: WebSocketContextType = {
    connectionStatus,
    notifications,
    subscribeToSymbol,
    unsubscribeFromSymbol,
    sendOrder,
    clearNotifications
  }

  return <WebSocketContext.Provider value={value}>{children}</WebSocketContext.Provider>
}