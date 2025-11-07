'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useWebSocket } from '@/contexts/WebSocketContext'
import { DashboardOverview } from '@/components/DashboardOverview'
import { TradingInterface } from '@/components/TradingInterface'
import { PortfolioOverview } from '@/components/PortfolioOverview'
import { MarketOverview } from '@/components/MarketOverview'
import { QuickActions } from '@/components/QuickActions'
import { RecentActivity } from '@/components/RecentActivity'
import { NotificationPanel } from '@/components/NotificationPanel'
import { PriceTicker } from '@/components/PriceTicker'
import { Navigation } from '@/components/Navigation'
import { UserMenu } from '@/components/UserMenu'
import { ThemeToggle } from '@/components/ThemeToggle'

export default function HomePage() {
  const { user, loading } = useAuth()
  const { connectionStatus, notifications } = useWebSocket()
  const [activeView, setActiveView] = useState('dashboard')

  useEffect(() => {
    // Initialize dashboard data
    if (user) {
      console.log('User authenticated:', user)
    }
  }, [user])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-600 to-purple-700 flex items-center justify-center">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 max-w-md w-full">
          <h1 className="text-3xl font-bold text-center mb-6 text-gray-900 dark:text-white">
            Welcome to TigerEx
          </h1>
          <p className="text-center text-gray-600 dark:text-gray-300 mb-8">
            Advanced Cryptocurrency Exchange Platform
          </p>
          <div className="space-y-4">
            <button
              onClick={() => {/* Handle login */}}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition duration-200"
            >
              Sign In
            </button>
            <button
              onClick={() => {/* Handle registration */}}
              className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 transition duration-200"
            >
              Create Account
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                🐅 TigerEx
              </h1>
              <Navigation activeView={activeView} setActiveView={setActiveView} />
            </div>
            <div className="flex items-center space-x-4">
              <ThemeToggle />
              <span className={`text-sm px-2 py-1 rounded ${
                connectionStatus === 'connected' 
                  ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                  : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
              }`}>
                {connectionStatus}
              </span>
              <UserMenu user={user} />
            </div>
          </div>
        </div>
      </header>

      {/* Price Ticker */}
      <PriceTicker />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            <QuickActions />
            <RecentActivity />
            <NotificationPanel notifications={notifications} />
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-2">
            {activeView === 'dashboard' && <DashboardOverview />}
            {activeView === 'trading' && <TradingInterface />}
            {activeView === 'portfolio' && <PortfolioOverview />}
            {activeView === 'markets' && <MarketOverview />}
          </div>

          {/* Right Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Market stats, watchlist, etc. */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Market Stats
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">BTC/USDT</span>
                  <span className="text-green-600 font-semibold">$43,250.00</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">ETH/USDT</span>
                  <span className="text-green-600 font-semibold">$2,245.50</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">BNB/USDT</span>
                  <span className="text-red-600 font-semibold">$312.75</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}