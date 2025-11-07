'use client'

import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'

interface DashboardStats {
  totalBalance: string
  todayChange: string
  todayChangePercent: string
  totalOrders: number
  activeOrders: number
  completedOrders: number
}

interface Asset {
  symbol: string
  name: string
  balance: string
  value: string
  change24h: string
  allocation: number
}

interface RecentTransaction {
  id: string
  type: 'buy' | 'sell' | 'deposit' | 'withdrawal'
  symbol: string
  amount: string
  price: string
  timestamp: string
  status: 'completed' | 'pending' | 'failed'
}

export const DashboardOverview: React.FC = () => {
  const { user } = useAuth()
  const [stats, setStats] = useState<DashboardStats>({
    totalBalance: '0.00',
    todayChange: '0.00',
    todayChangePercent: '0.00',
    totalOrders: 0,
    activeOrders: 0,
    completedOrders: 0
  })
  const [assets, setAssets] = useState<Asset[]>([])
  const [transactions, setTransactions] = useState<RecentTransaction[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      // Load user portfolio stats
      const statsResponse = await fetch('/api/portfolio/stats')
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats(statsData)
      }

      // Load assets
      const assetsResponse = await fetch('/api/portfolio/assets')
      if (assetsResponse.ok) {
        const assetsData = await assetsResponse.json()
        setAssets(assetsData)
      }

      // Load recent transactions
      const transactionsResponse = await fetch('/api/transactions/recent')
      if (transactionsResponse.ok) {
        const transactionsData = await transactionsResponse.json()
        setTransactions(transactionsData)
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
          <div className="grid grid-cols-2 gap-4">
            <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Portfolio Overview */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Portfolio Overview
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Total Balance</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              ${stats.totalBalance}
            </p>
            <p className={`text-sm ${
              parseFloat(stats.todayChange) >= 0 
                ? 'text-green-600 dark:text-green-400' 
                : 'text-red-600 dark:text-red-400'
            }`}>
              {parseFloat(stats.todayChange) >= 0 ? '+' : ''}{stats.todayChange} ({stats.todayChangePercent}%)
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Total Orders</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {stats.totalOrders}
            </p>
            <div className="flex space-x-4 text-sm">
              <span className="text-blue-600 dark:text-blue-400">{stats.activeOrders} Active</span>
              <span className="text-green-600 dark:text-green-400">{stats.completedOrders} Completed</span>
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Account Level</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {user?.role === 'admin' ? 'Admin' : user?.role === 'institutional' ? 'Institutional' : 'Standard'}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {user?.kycVerified ? 'KYC Verified' : 'KYC Pending'}
            </p>
          </div>
        </div>
      </div>

      {/* Assets Distribution */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Assets Distribution
        </h2>
        <div className="space-y-4">
          {assets.map((asset, index) => (
            <div key={index} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                  <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">
                    {asset.symbol.substring(0, 2)}
                  </span>
                </div>
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {asset.symbol}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {asset.balance} {asset.name}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-medium text-gray-900 dark:text-white">
                  ${asset.value}
                </p>
                <p className={`text-sm ${
                  parseFloat(asset.change24h) >= 0 
                    ? 'text-green-600 dark:text-green-400' 
                    : 'text-red-600 dark:text-red-400'
                }`}>
                  {parseFloat(asset.change24h) >= 0 ? '+' : ''}{asset.change24h}
                </p>
              </div>
              <div className="w-20">
                <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-600 dark:bg-blue-400 h-2 rounded-full"
                    style={{ width: `${asset.allocation}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 text-center mt-1">
                  {asset.allocation}%
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Recent Transactions
        </h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-600">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Pair
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Time
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-600">
              {transactions.map((transaction, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      transaction.type === 'buy'
                        ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                        : transaction.type === 'sell'
                        ? 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                        : transaction.type === 'deposit'
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
                    }`}>
                      {transaction.type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {transaction.symbol}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {transaction.amount}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    ${transaction.price}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      transaction.status === 'completed'
                        ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                        : transaction.status === 'pending'
                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
                        : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                    }`}>
                      {transaction.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                    {new Date(transaction.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}