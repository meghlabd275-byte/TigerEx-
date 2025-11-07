'use client'

import React, { useState, useEffect } from 'react'

interface MarketData {
  symbol: string
  name: string
  price: string
  change24h: string
  change24hPercent: string
  volume24h: string
  marketCap: string
}

interface MarketStats {
  totalMarketCap: string
  totalVolume24h: string
  btcDominance: string
  activeCryptocurrencies: number
  activeMarkets: number
}

export const MarketOverview: React.FC = () => {
  const [marketData, setMarketData] = useState<MarketData[]>([])
  const [stats, setStats] = useState<MarketStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadMarketData()
    const interval = setInterval(loadMarketData, 30000) // Update every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const loadMarketData = async () => {
    try {
      const response = await fetch('/api/markets/overview')
      if (response.ok) {
        const data = await response.json()
        setMarketData(data.markets)
        setStats(data.stats)
      }
    } catch (error) {
      console.error('Failed to load market data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className='bg-white dark:bg-gray-800 rounded-lg shadow p-6'>
        <div className='animate-pulse'>
          <div className='h-8 bg-gray-200 dark:bg-gray-700 rounded mb-6'></div>
          <div className='grid grid-cols-2 gap-4 mb-6'>
            {[...Array(4)].map((_, i) => (
              <div key={i} className='h-16 bg-gray-200 dark:bg-gray-700 rounded'></div>
            ))}
          </div>
          <div className='space-y-3'>
            {[...Array(10)].map((_, i) => (
              <div key={i} className='h-12 bg-gray-200 dark:bg-gray-700 rounded'></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className='bg-white dark:bg-gray-800 rounded-lg shadow'>
      <div className='p-6'>
        <h2 className='text-lg font-semibold text-gray-900 dark:text-white mb-6'>
          Market Overview
        </h2>

        {/* Market Statistics */}
        {stats && (
          <div className='grid grid-cols-2 md:grid-cols-4 gap-4 mb-8'>
            <div className='bg-gray-50 dark:bg-gray-700 rounded-lg p-4'>
              <p className='text-sm text-gray-600 dark:text-gray-400'>Market Cap</p>
              <p className='text-xl font-bold text-gray-900 dark:text-white'>
                ${stats.totalMarketCap}
              </p>
            </div>
            <div className='bg-gray-50 dark:bg-gray-700 rounded-lg p-4'>
              <p className='text-sm text-gray-600 dark:text-gray-400'>24h Volume</p>
              <p className='text-xl font-bold text-gray-900 dark:text-white'>
                ${stats.totalVolume24h}
              </p>
            </div>
            <div className='bg-gray-50 dark:bg-gray-700 rounded-lg p-4'>
              <p className='text-sm text-gray-600 dark:text-gray-400'>BTC Dominance</p>
              <p className='text-xl font-bold text-gray-900 dark:text-white'>
                {stats.btcDominance}%
              </p>
            </div>
            <div className='bg-gray-50 dark:bg-gray-700 rounded-lg p-4'>
              <p className='text-sm text-gray-600 dark:text-gray-400'>Active Markets</p>
              <p className='text-xl font-bold text-gray-900 dark:text-white'>
                {stats.activeMarkets}
              </p>
            </div>
          </div>
        )}

        {/* Market Data Table */}
        <div className='overflow-x-auto'>
          <table className='min-w-full divide-y divide-gray-200 dark:divide-gray-600'>
            <thead className='bg-gray-50 dark:bg-gray-700'>
              <tr>
                <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider'>
                  Name
                </th>
                <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider'>
                  Price
                </th>
                <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider'>
                  24h Change
                </th>
                <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider'>
                  24h Volume
                </th>
                <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider'>
                  Market Cap
                </th>
                <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider'>
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className='bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-600'>
              {marketData.map((market, index) => (
                <tr key={index}>
                  <td className='px-6 py-4 whitespace-nowrap'>
                    <div className='flex items-center'>
                      <div className='flex-shrink-0 h-8 w-8'>
                        <div className='h-8 w-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center'>
                          <span className='text-xs font-medium text-blue-600 dark:text-blue-400'>
                            {market.symbol.substring(0, 2)}
                          </span>
                        </div>
                      </div>
                      <div className='ml-4'>
                        <div className='text-sm font-medium text-gray-900 dark:text-white'>
                          {market.symbol}
                        </div>
                        <div className='text-sm text-gray-500 dark:text-gray-300'>
                          {market.name}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className='px-6 py-4 whitespace-nowrap'>
                    <div className='text-sm text-gray-900 dark:text-white'>
                      ${market.price}
                    </div>
                  </td>
                  <td className='px-6 py-4 whitespace-nowrap'>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      parseFloat(market.change24hPercent) >= 0
                        ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                        : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                    }`}>
                      {parseFloat(market.change24hPercent) >= 0 ? '+' : ''}{market.change24hPercent}%
                    </span>
                  </td>
                  <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white'>
                    ${market.volume24h}
                  </td>
                  <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white'>
                    ${market.marketCap}
                  </td>
                  <td className='px-6 py-4 whitespace-nowrap text-sm font-medium'>
                    <button className='text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 mr-3'>
                      Trade
                    </button>
                    <button className='text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-100'>
                      Details
                    </button>
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
</create_file>