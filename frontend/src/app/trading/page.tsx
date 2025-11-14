'use client'

import React, { useState, useEffect } from 'react'
import { Line, CandlestickChart, TrendingUp, TrendingDown, Activity, DollarSign, BarChart3, Settings, Bell, User, Search, Menu, X, ArrowUpRight, ArrowDownRight, Clock, Globe, Shield, Star, ChevronRight, Plus, Minus, Info, Wallet, History, BookOpen, HelpCircle, LogOut, Home, PieChart, FileText, Users, Lock, Eye, EyeOff, ChevronDown, Filter, Grid, List, Download, Upload, RefreshCw, Copy, ExternalLink, CheckCircle, AlertCircle, AlertTriangle } from 'lucide-react'

interface TradingPair {
  symbol: string
  name: string
  price: number
  change24h: number
  volume24h: number
  high24h: number
  low24h: number
}

interface OrderBookEntry {
  price: number
  amount: number
  total: number
}

interface Trade {
  time: string
  price: number
  amount: number
  type: 'buy' | 'sell'
}

export default function TradingPage() {
  const [selectedTab, setSelectedTab] = useState('spot')
  const [selectedPair, setSelectedPair] = useState('BTC/USDT')
  const [orderType, setOrderType] = useState('market')
  const [buyAmount, setBuyAmount] = useState('')
  const [sellAmount, setSellAmount] = useState('')
  const [leverage, setLeverage] = useState('1')
  const [showPassword, setShowPassword] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [chartType, setChartType] = useState('candlestick')
  const [timeframe, setTimeframe] = useState('1h')

  const tradingPairs: TradingPair[] = [
    { symbol: 'BTC/USDT', name: 'Bitcoin', price: 67850.25, change24h: 2.5, volume24h: 1250000000, high24h: 68900, low24h: 66500 },
    { symbol: 'ETH/USDT', name: 'Ethereum', price: 3542.18, change24h: -1.2, volume24h: 850000000, high24h: 3650, low24h: 3480 },
    { symbol: 'BNB/USDT', name: 'Binance Coin', price: 612.45, change24h: 0.8, volume24h: 320000000, high24h: 625, low24h: 605 },
    { symbol: 'SOL/USDT', name: 'Solana', price: 145.67, change24h: 3.2, volume24h: 450000000, high24h: 152, low24h: 140 },
    { symbol: 'ADA/USDT', name: 'Cardano', price: 0.385, change24h: -0.5, volume24h: 180000000, high24h: 0.395, low24h: 0.380 },
  ]

  const orderBookBuy: OrderBookEntry[] = [
    { price: 67845.50, amount: 0.1254, total: 8508.92 },
    { price: 67845.25, amount: 0.2341, total: 15879.16 },
    { price: 67845.00, amount: 0.5678, total: 38531.64 },
    { price: 67844.75, amount: 0.1234, total: 8373.63 },
    { price: 67844.50, amount: 0.4567, total: 30979.82 },
  ]

  const orderBookSell: OrderBookEntry[] = [
    { price: 67846.00, amount: 0.2345, total: 15908.37 },
    { price: 67846.25, amount: 0.1234, total: 8376.64 },
    { price: 67846.50, amount: 0.3456, total: 23444.42 },
    { price: 67846.75, amount: 0.5678, total: 38534.64 },
    { price: 67847.00, amount: 0.2341, total: 15879.16 },
  ]

  const recentTrades: Trade[] = [
    { time: '14:32:15', price: 67845.50, amount: 0.1254, type: 'buy' },
    { time: '14:32:12', price: 67845.25, amount: 0.2341, type: 'sell' },
    { time: '14:32:08', price: 67845.00, amount: 0.5678, type: 'buy' },
    { time: '14:32:05', price: 67844.75, amount: 0.1234, type: 'buy' },
    { time: '14:32:02', price: 67844.50, amount: 0.4567, type: 'sell' },
  ]

  const tabs = [
    { id: 'spot', name: 'Spot', icon: BarChart3 },
    { id: 'futures', name: 'Futures', icon: TrendingUp },
    { id: 'margin', name: 'Margin', icon: DollarSign },
    { id: 'options', name: 'Options', icon: Settings },
    { id: 'alpha', name: 'Alpha Market', icon: Star },
    { id: 'tradex', name: 'TradeX', icon: Activity },
    { id: 'etf', name: 'ETF Trading', icon: PieChart },
  ]

  const timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']

  const currentPair = tradingPairs.find(p => p.symbol === selectedPair) || tradingPairs[0]

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            >
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <TrendingUp size={16} />
              </div>
              <h1 className="text-xl font-bold">TigerEx</h1>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
              <input
                type="text"
                placeholder="Search pairs..."
                className="pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <button className="p-2 hover:bg-gray-800 rounded-lg transition-colors relative">
              <Bell size={20} />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
            <button className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
              <Settings size={20} />
            </button>
            <div className="flex items-center space-x-2 px-3 py-2 bg-gray-800 rounded-lg">
              <div className="w-6 h-6 bg-blue-600 rounded-full"></div>
              <span className="text-sm">Trader</span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        {sidebarOpen && (
          <aside className="w-64 bg-gray-900 border-r border-gray-800 min-h-screen">
            <nav className="p-4">
              <ul className="space-y-2">
                <li>
                  <a href="#" className="flex items-center space-x-3 px-3 py-2 hover:bg-gray-800 rounded-lg transition-colors">
                    <Home size={20} />
                    <span>Dashboard</span>
                  </a>
                </li>
                <li>
                  <a href="#" className="flex items-center space-x-3 px-3 py-2 bg-blue-600 rounded-lg">
                    <BarChart3 size={20} />
                    <span>Trading</span>
                  </a>
                </li>
                <li>
                  <a href="#" className="flex items-center space-x-3 px-3 py-2 hover:bg-gray-800 rounded-lg transition-colors">
                    <Wallet size={20} />
                    <span>Wallet</span>
                  </a>
                </li>
                <li>
                  <a href="#" className="flex items-center space-x-3 px-3 py-2 hover:bg-gray-800 rounded-lg transition-colors">
                    <History size={20} />
                    <span>Orders</span>
                  </a>
                </li>
                <li>
                  <a href="#" className="flex items-center space-x-3 px-3 py-2 hover:bg-gray-800 rounded-lg transition-colors">
                    <FileText size={20} />
                    <span>Reports</span>
                  </a>
                </li>
              </ul>
            </nav>
          </aside>
        )}

        {/* Main Content */}
        <main className="flex-1 p-4">
          {/* Trading Tabs */}
          <div className="flex space-x-1 mb-4 bg-gray-900 p-1 rounded-lg">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setSelectedTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  selectedTab === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              >
                <tab.icon size={16} />
                <span className="font-medium">{tab.name}</span>
              </button>
            ))}
          </div>

          <div className="grid grid-cols-12 gap-4">
            {/* Trading Pairs */}
            <div className="col-span-3">
              <div className="bg-gray-900 rounded-lg p-4">
                <h3 className="font-semibold mb-4">Markets</h3>
                <div className="space-y-2">
                  {tradingPairs.map(pair => (
                    <div
                      key={pair.symbol}
                      onClick={() => setSelectedPair(pair.symbol)}
                      className={`p-3 rounded-lg cursor-pointer transition-colors ${
                        selectedPair === pair.symbol
                          ? 'bg-blue-600 bg-opacity-20 border border-blue-600'
                          : 'hover:bg-gray-800'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium">{pair.symbol}</div>
                          <div className="text-xs text-gray-400">{pair.name}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-medium">${pair.price.toLocaleString()}</div>
                          <div className={`text-xs flex items-center ${
                            pair.change24h > 0 ? 'text-green-500' : 'text-red-500'
                          }`}>
                            {pair.change24h > 0 ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                            {Math.abs(pair.change24h)}%
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Chart */}
            <div className="col-span-6">
              <div className="bg-gray-900 rounded-lg p-4">
                <div className="mb-4">
                  <div className="text-2xl font-bold">{selectedPair}</div>
                  <div className="text-3xl font-bold">${currentPair.price.toLocaleString()}</div>
                </div>
                <div className="h-96 bg-gray-800 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <CandlestickChart size={48} className="mx-auto mb-2 text-gray-600" />
                    <p className="text-gray-400">Trading Chart</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Trading Form */}
            <div className="col-span-3">
              <div className="bg-gray-900 rounded-lg p-4">
                <div className="flex space-x-2 mb-4">
                  <button className="flex-1 py-2 bg-green-600 rounded-lg">Buy</button>
                  <button className="flex-1 py-2 bg-red-600 rounded-lg">Sell</button>
                </div>

                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium mb-2">Order Type</label>
                    <select className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg">
                      <option>Market</option>
                      <option>Limit</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Amount</label>
                    <input
                      type="number"
                      value={buyAmount}
                      onChange={(e) => setBuyAmount(e.target.value)}
                      placeholder="0.00"
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Total (USDT)</label>
                    <input
                      type="number"
                      value={sellAmount}
                      onChange={(e) => setSellAmount(e.target.value)}
                      placeholder="0.00"
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                    />
                  </div>

                  <button className="w-full py-3 bg-green-600 hover:bg-green-700 rounded-lg font-medium">
                    Buy {selectedPair.split('/')[0]}
                  </button>

                  <div className="p-3 bg-gray-800 rounded-lg">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Available Balance</span>
                      <span>10,000.00 USDT</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}