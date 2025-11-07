'use client'

import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'

interface Portfolio {
  totalValue: string
  todayChange: string
  todayChangePercent: string
  assets: Asset[]
}

interface Asset {
  symbol: string
  name: string
  balance: string
  value: string
  price: string
  change24h: string
  allocation: number
}

export const PortfolioOverview: React.FC = () => {
  const { user } = useAuth()
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadPortfolioData()
  }, [])

  const loadPortfolioData = async () => {
    try {
      const response = await fetch('/api/portfolio/overview')
      if (response.ok) {
        const data = await response.json()
        setPortfolio(data)
      }
    } catch (error) {
      console.error('Failed to load portfolio data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (!portfolio) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <p className="text-center text-gray-600 dark:text-gray-300">
          Failed to load portfolio data
        </p>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Portfolio Overview
          </h2>
          <div className="text-right">
            <p className="text-sm text-gray-600 dark:text-gray-400">Total Value</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              ${portfolio.totalValue}
            </p>
            <p className={`text-sm ${
              parseFloat(portfolio.todayChange) >= 0 
                ? 'text-green-600 dark:text-green-400' 
                : 'text-red-600 dark:text-red-400'
            }`}>
              {parseFloat(portfolio.todayChange) >= 0 ? '+' : ''}{portfolio.todayChange} ({portfolio.todayChangePercent}%)
            </p>
          </div>
        </div>

        <div className="space-y-4">
          {portfolio.assets.map((asset, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                  <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                    {asset.symbol.substring(0, 2)}
                  </span>
                </div>
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {asset.symbol}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {asset.name}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-8">
                <div className="text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Balance</p>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {asset.balance}
                  </p>
                </div>
                
                <div className="text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Price</p>
                  <p className="font-medium text-gray-900 dark:text-white">
                    ${asset.price}
                  </p>
                </div>
                
                <div className="text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Value</p>
                  <p className="font-medium text-gray-900 dark:text-white">
                    ${asset.value}
                  </p>
                </div>
                
                <div className="text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400">24h Change</p>
                  <p className={`font-medium ${
                    parseFloat(asset.change24h) >= 0 
                      ? 'text-green-600 dark:text-green-400' 
                      : 'text-red-600 dark:text-red-400'
                  }`}>
                    {parseFloat(asset.change24h) >= 0 ? '+' : ''}{asset.change24h}
                  </p>
                </div>
                
                <div className="w-24">
                  <div className="bg-gray-200 dark:bg-gray-600 rounded-full h-2">
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
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}