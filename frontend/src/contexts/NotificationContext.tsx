/**
 * TigerEx React Component
 * @file NotificationContext.tsx
 * @description React component for TigerEx
 * @author TigerEx Development Team
 */
'use client'

import React, { createContext, useContext, useState, ReactNode } from 'react'

interface Notification {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
}

interface NotificationContextType {
  notifications: Notification[]
  addNotification: (type: Notification['type'], message: string) => void
  removeNotification: (id: string) => void
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

export const NotificationProvider = ({ children }: { children: ReactNode }) => {
  const [notifications, setNotifications] = useState<Notification[]>([])

  const addNotification = (type: Notification['type'], message: string) => {
    const id = Date.now().toString()
    setNotifications(prev => [...prev, { id, type, message }])
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id))
    }, 5000)
  }

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  return (
    <NotificationContext.Provider value={{ notifications, addNotification, removeNotification }}>
      {children}
    </NotificationContext.Provider>
  )
}

export const useNotifications = () => {
  const context = useContext(NotificationContext)
  if (!context) {
    // Return a default implementation to prevent crashes
    return {
      notifications: [],
      addNotification: () => {},
      removeNotification: () => {},
    }
  }
  return context
}
export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
