'use client'

import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'

interface SystemStats {
  totalOrders: number
  totalVolume: string
  activeUsers: number
  tradingStatus: string
  systemHealth: 'healthy' | 'warning' | 'critical'
}

interface User {
  id: string
  email: string
  username: string
  role: string
  status: 'active' | 'suspended' | 'banned'
  kycVerified: boolean
  twoFactorEnabled: boolean
  lastLogin: string
  totalVolume: string
}

interface Order {
  id: string
  user: string
  symbol: string
  side: 'buy' | 'sell'
  type: string
  quantity: string
  price: string
  status: string
  timestamp: string
}

export const AdminDashboard: React.FC = () => {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState('overview')
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [orders, setOrders] = useState<Order[]>([])
  const [tradingControls, setTradingControls] = useState({
    status: 'active',
    pausedSymbols: [] as string[]
  })

  useEffect(() => {
    if (user?.role !== 'admin') {
      // Redirect or show unauthorized message
      return
    }
    
    loadSystemStats()
    loadUsers()
    loadOrders()
    loadTradingControls()
  }, [user])

  const loadSystemStats = async () => {
    try {
      const response = await fetch('/admin/stats')
      const data = await response.json()
      setSystemStats(data)
    } catch (error) {
      console.error('Failed to load system stats:', error)
    }
  }

  const loadUsers = async () => {
    try {
      const response = await fetch('/admin/users')
      const data = await response.json()
      setUsers(data.users || [])
    } catch (error) {
      console.error('Failed to load users:', error)
    }
  }

  const loadOrders = async () => {
    try {
      const response = await fetch('/admin/orders')
      const data = await response.json()
      setOrders(data.orders || [])
    } catch (error) {
      console.error('Failed to load orders:', error)
    }
  }

  const loadTradingControls = async () => {
    try {
      const response = await fetch('/admin/trading/status')
      const data = await response.json()
      setTradingControls(data)
    } catch (error) {
      console.error('Failed to load trading controls:', error)
    }
  }

  const handleTradingControl = async (action: string, symbol?: string) => {
    try {
      const response = await fetch('/admin/trading/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, symbol, reason: 'Admin action' })
      })
      
      if (response.ok) {
        loadTradingControls()
        loadSystemStats()
      }
    } catch (error) {
      console.error('Failed to control trading:', error)
    }
  }

  const handleUserAction = async (userId: string, action: string) => {
    try {
      const response = await fetch(`/admin/users/${userId}/${action}`, {
        method: 'POST'
      })
      
      if (response.ok) {
        loadUsers()
      }
    } catch (error) {
      console.error('Failed to perform user action:', error)
    }
  }

  const handleOrderCancel = async (orderId: string) => {
    try {
      const response = await fetch(`/admin/orders/${orderId}/cancel`, {
        method: 'POST'
      })
      
      if (response.ok) {
        loadOrders()
      }
    } catch (error) {
      console.error('Failed to cancel order:', error)
    }
  }

  if (!user || user.role !== 'admin') {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 max-w-md w-full">
          <h1 className="text-2xl font-bold text-center mb-4 text-red-600">
            Access Denied
          </h1>
          <p className="text-center text-gray-600 dark:text-gray-300">
            You don't have permission to access the admin dashboard.
          </p>
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
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              🐅 TigerEx Admin Dashboard
            </h1>
            <div className="flex items-center space-x-4">
              <span className={`px-3 py-1 rounded text-sm font-medium ${
                systemStats?.systemHealth === 'healthy' 
                  ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                  : systemStats?.systemHealth === 'warning'
                  ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
                  : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
              }`}>
                System: {systemStats?.systemHealth?.toUpperCase()}
              </span>
            </div>
          </div>
        </div>
      </header>

import WalletManagerDashboard from '../components/admin/WalletManagerDashboard';
import UserManagementDashboard from '../components/admin/UserManagementDashboard';

      {/* Navigation Tabs */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {['overview', 'users', 'orders', 'trading', 'wallets', 'security'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* System Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Orders</h3>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {systemStats?.totalOrders?.toLocaleString() || '0'}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Volume</h3>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  ${systemStats?.totalVolume || '0'}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Active Users</h3>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {systemStats?.activeUsers?.toLocaleString() || '0'}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Trading Status</h3>
                <p className="text-2xl font-bold text-gray-900 dark:text-white capitalize">
                  {systemStats?.tradingStatus || 'Unknown'}
                </p>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Recent Activity
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-600">
                  <span className="text-sm text-gray-600 dark:text-gray-300">New user registration</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">2 minutes ago</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-600">
                  <span className="text-sm text-gray-600 dark:text-gray-300">Large trade executed</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">5 minutes ago</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-600">
                  <span className="text-sm text-gray-600 dark:text-gray-300">Security alert triggered</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">12 minutes ago</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
            <UserManagementDashboard />
        )}

        {activeTab === 'orders' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Order Management
              </h3>
              <div className="mb-4">
                <button
                  onClick={() => handleTradingControl('cancel_all')}
                  className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                >
                  Cancel All Orders
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-600">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Order ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        User
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Symbol
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Side
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Quantity
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Price
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-600">
                    {orders.map((order) => (
                      <tr key={order.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {order.id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {order.user}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {order.symbol}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            order.side === 'buy'
                              ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                              : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                          }`}>
                            {order.side}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {order.type}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {order.quantity}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {order.price}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            order.status === 'filled'
                              ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                              : order.status === 'open'
                              ? 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100'
                              : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                          }`}>
                            {order.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button
                            onClick={() => handleOrderCancel(order.id)}
                            className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                          >
                            Cancel
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'trading' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Trading Controls
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Trading Status
                  </span>
                  <span className={`px-3 py-1 rounded text-sm font-medium ${
                    tradingControls.status === 'active'
                      ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                      : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                  }`}>
                    {tradingControls.status}
                  </span>
                </div>
                <div className="flex space-x-4">
                  <button
                    onClick={() => handleTradingControl('pause')}
                    className="bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700"
                  >
                    Pause Trading
                  </button>
                  <button
                    onClick={() => handleTradingControl('resume')}
                    className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                  >
                    Resume Trading
                  </button>
                  <button
                    onClick={() => handleTradingControl('emergency_stop')}
                    className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                  >
                    Emergency Stop
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'wallets' && (
            <WalletManagerDashboard />
        )}

        {activeTab === 'security' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Security Settings
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Enable 2FA Requirement
                </span>
                <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                  Configure
                </button>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  API Rate Limiting
                </span>
                <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                  Configure
                </button>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  IP Whitelist
                </span>
                <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                  Configure
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}