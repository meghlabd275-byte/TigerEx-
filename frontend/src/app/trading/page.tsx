'use client'

import React, { useState, useEffect } from 'react'
import { Line, CandlestickChart, TrendingUp, TrendingDown, Activity, DollarSign, BarChart3, Settings, Bell, User, Search, Menu, X, ArrowUpRight, ArrowDownRight, Clock, Globe, Shield, Star, ChevronRight, Plus, Minus, Info, Wallet, History, BookOpen, HelpCircle, LogOut, Home, PieChart, FileText, Users, Lock, Eye, EyeOff, ChevronDown, Filter, Grid, List, Download, Upload, RefreshCw, Copy, ExternalLink, CheckCircle, AlertCircle, AlertTriangle, Zap, Package, CreditCard, ArrowLeft, ArrowRight, MoreVertical } from 'lucide-react'

interface TradingPair {
  symbol: string
  name: string
  price: number
  change24h: number
  volume24h: number
  high24h: number
  low24h: number
  marketCap: number
  circulatingSupply: number
}

interface OrderBookEntry {
  price: number
  amount: number
  total: number
  cumulative?: number
}

interface Trade {
  time: string
  price: number
  amount: number
  type: 'buy' | 'sell'
}

interface OrderForm {
  type: 'market' | 'limit'
  side: 'buy' | 'sell'
  amount: string
  price: string
  total: string
}

export default function TradingPage() {
  const [selectedTab, setSelectedTab] = useState('spot')
  const [selectedPair, setSelectedPair] = useState('BTC/USDT')
  const [orderType, setOrderType] = useState<'market' | 'limit'>('market')
  const [orderSide, setOrderSide] = useState<'buy' | 'sell'>('buy')
  const [orderForm, setOrderForm] = useState<OrderForm>({
    type: 'market',
    side: 'buy',
    amount: '',
    price: '',
    total: ''
  })
  const [leverage, setLeverage] = useState('1')
  const [showPassword, setShowPassword] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [chartType, setChartType] = useState('candlestick')
  const [timeframe, setTimeframe] = useState('1h')
  const [orderBookTab, setOrderBookTab] = useState('book')

  const tradingPairs: TradingPair[] = [
    { symbol: 'BTC/USDT', name: 'Bitcoin', price: 67850.25, change24h: 2.5, volume24h: 1250000000, high24h: 68900, low24h: 66500, marketCap: 1320000000000, circulatingSupply: 19450000 },
    { symbol: 'ETH/USDT', name: 'Ethereum', price: 3542.18, change24h: -1.2, volume24h: 850000000, high24h: 3650, low24h: 3480, marketCap: 425000000000, circulatingSupply: 120000000 },
    { symbol: 'BNB/USDT', name: 'Binance Coin', price: 612.45, change24h: 0.8, volume24h: 320000000, high24h: 625, low24h: 605, marketCap: 94000000000, circulatingSupply: 153500000 },
    { symbol: 'SOL/USDT', name: 'Solana', price: 145.67, change24h: 3.2, volume24h: 450000000, high24h: 152, low24h: 140, marketCap: 65000000000, circulatingSupply: 446000000 },
    { symbol: 'ADA/USDT', name: 'Cardano', price: 0.385, change24h: -0.5, volume24h: 180000000, high24h: 0.395, low24h: 0.380, marketCap: 13500000000, circulatingSupply: 35000000000 },
    { symbol: 'XRP/USDT', name: 'Ripple', price: 0.625, change24h: 1.8, volume24h: 1200000000, high24h: 0.640, low24h: 0.610, marketCap: 34000000000, circulatingSupply: 54400000000 },
    { symbol: 'DOGE/USDT', name: 'Dogecoin', price: 0.0856, change24h: 4.2, volume24h: 450000000, high24h: 0.0895, low24h: 0.0820, marketCap: 12200000000, circulatingSupply: 142500000000 },
    { symbol: 'AVAX/USDT', name: 'Avalanche', price: 28.45, change24h: -2.1, volume24h: 280000000, high24h: 29.80, low24h: 27.90, marketCap: 10500000000, circulatingSupply: 369000000 }
  ]

  const orderBookBuy: OrderBookEntry[] = [
    { price: 67845.50, amount: 0.1254, total: 8508.92 },
    { price: 67845.25, amount: 0.2341, total: 15879.16 },
    { price: 67845.00, amount: 0.5678, total: 38531.64 },
    { price: 67844.75, amount: 0.1234, total: 8373.63 },
    { price: 67844.50, amount: 0.4567, total: 30979.82 },
    { price: 67844.25, amount: 0.7890, total: 53547.30 },
    { price: 67844.00, amount: 0.3456, total: 23442.62 },
    { price: 67843.75, amount: 0.6789, total: 46078.21 }
  ]

  const orderBookSell: OrderBookEntry[] = [
    { price: 67846.00, amount: 0.2345, total: 15908.37 },
    { price: 67846.25, amount: 0.1234, total: 8376.64 },
    { price: 67846.50, amount: 0.3456, total: 23444.42 },
    { price: 67846.75, amount: 0.5678, total: 38534.64 },
    { price: 67847.00, amount: 0.2341, total: 15879.16 },
    { price: 67847.25, amount: 0.4567, total: 30987.15 },
    { price: 67847.50, amount: 0.1234, total: 8380.83 },
    { price: 67847.75, amount: 0.6789, total: 46095.26 }
  ]

  const recentTrades: Trade[] = [
    { time: '14:32:15', price: 67845.50, amount: 0.1254, type: 'buy' },
    { time: '14:32:12', price: 67845.25, amount: 0.2341, type: 'sell' },
    { time: '14:32:08', price: 67845.00, amount: 0.5678, type: 'buy' },
    { time: '14:32:05', price: 67844.75, amount: 0.1234, type: 'buy' },
    { time: '14:32:02', price: 67844.50, amount: 0.4567, type: 'sell' },
    { time: '14:31:58', price: 67844.25, amount: 0.7890, type: 'sell' },
    { time: '14:31:55', price: 67844.00, amount: 0.3456, type: 'buy' },
    { time: '14:31:52', price: 67843.75, amount: 0.6789, type: 'buy' }
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
  const chartTypes = ['candlestick', 'line', 'area', 'volume']

  const currentPair = tradingPairs.find(p => p.symbol === selectedPair) || tradingPairs[0]

  const calculateTotal = () => {
    if (orderForm.amount && orderForm.price) {
      return (parseFloat(orderForm.amount) * parseFloat(orderForm.price)).toFixed(2)
    }
    return ''
  }

  useEffect(() => {
    const total = calculateTotal()
    setOrderForm(prev => ({ ...prev, total }))
  }, [orderForm.amount, orderForm.price])

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
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold">Markets</h3>
                  <div className="flex space-x-2">
                    <button className="p-1 hover:bg-gray-800 rounded">
                      <Search size={16} />
                    </button>
                    <button className="p-1 hover:bg-gray-800 rounded">
                      <Filter size={16} />
                    </button>
                  </div>
                </div>
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
                          <div className={`text-xs flex items-center justify-end ${
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

            {/* Chart and Trading Info */}
            <div className="col-span-6">
              <div className="bg-gray-900 rounded-lg p-4">
                {/* Chart Header */}
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <div className="text-2xl font-bold">{selectedPair}</div>
                    <div className="text-3xl font-bold">${currentPair.price.toLocaleString()}</div>
                    <div className={`text-sm ${currentPair.change24h > 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {currentPair.change24h > 0 ? '+' : ''}{currentPair.change24h}% 
                      ({currentPair.change24h > 0 ? '+' : ''}${(currentPair.price * currentPair.change24h / 100).toFixed(2)})
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <select 
                      value={chartType}
                      onChange={(e) => setChartType(e.target.value)}
                      className="px-3 py-1 bg-gray-800 border border-gray-700 rounded text-sm"
                    >
                      {chartTypes.map(type => (
                        <option key={type} value={type}>{type.charAt(0).toUpperCase() + type.slice(1)}</option>
                      ))}
                    </select>
                    <div className="flex space-x-1 bg-gray-800 rounded-lg p-1">
                      {timeframes.map(tf => (
                        <button
                          key={tf}
                          onClick={() => setTimeframe(tf)}
                          className={`px-2 py-1 rounded text-xs transition-colors ${
                            timeframe === tf ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
                          }`}
                        >
                          {tf}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Chart */}
                <div className="h-80 bg-gray-800 rounded-lg flex items-center justify-center mb-4">
                  <div className="text-center">
                    <CandlestickChart size={48} className="mx-auto mb-2 text-gray-600" />
                    <p className="text-gray-400">Trading Chart</p>
                  </div>
                </div>

                {/* Market Stats */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">24h High</span>
                      <span className="text-green-500">${currentPair.high24h.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">24h Low</span>
                      <span className="text-red-500">${currentPair.low24h.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">24h Volume</span>
                      <span>${(currentPair.volume24h / 1000000).toFixed(1)}M</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Market Cap</span>
                      <span>${(currentPair.marketCap / 1000000000).toFixed(1)}B</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Circulating Supply</span>
                      <span>{(currentPair.circulatingSupply / 1000000).toFixed(1)}M</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Market Cap Rank</span>
                      <span>#1</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Order Book */}
              <div className="bg-gray-900 rounded-lg p-4 mt-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold">Order Book</h3>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setOrderBookTab('book')}
                      className={`px-3 py-1 rounded text-sm transition-colors ${
                        orderBookTab === 'book' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
                      }`}
                    >
                      Book
                    </button>
                    <button
                      onClick={() => setOrderBookTab('trades')}
                      className={`px-3 py-1 rounded text-sm transition-colors ${
                        orderBookTab === 'trades' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
                      }`}
                    >
                      Trades
                    </button>
                  </div>
                </div>

                {orderBookTab === 'book' ? (
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <div className="text-xs text-gray-400 mb-2">Price(USDT)</div>
                      <div className="space-y-1">
                        {orderBookSell.reverse().map((order, idx) => (
                          <div key={idx} className="text-sm text-red-500 text-right">
                            {order.price.toFixed(2)}
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-400 mb-2">Amount</div>
                      <div className="space-y-1">
                        {orderBookSell.reverse().map((order, idx) => (
                          <div key={idx} className="text-sm text-gray-300 text-center">
                            {order.amount.toFixed(4)}
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-400 mb-2">Total</div>
                      <div className="space-y-1">
                        {orderBookSell.reverse().map((order, idx) => (
                          <div key={idx} className="text-sm text-gray-300">
                            {order.total.toFixed(2)}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <div className="grid grid-cols-3 text-xs text-gray-400 mb-2">
                      <div>Time</div>
                      <div>Price(USDT)</div>
                      <div>Amount</div>
                    </div>
                    {recentTrades.map((trade, idx) => (
                      <div key={idx} className="grid grid-cols-3 text-sm">
                        <div className="text-gray-400">{trade.time}</div>
                        <div className={trade.type === 'buy' ? 'text-green-500' : 'text-red-500'}>
                          {trade.price.toFixed(2)}
                        </div>
                        <div className="text-gray-300">{trade.amount.toFixed(4)}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Trading Form */}
            <div className="col-span-3">
              <div className="bg-gray-900 rounded-lg p-4">
                {/* Order Side Selector */}
                <div className="flex space-x-2 mb-4">
                  <button
                    onClick={() => setOrderSide('buy')}
                    className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
                      orderSide === 'buy' ? 'bg-green-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-white'
                    }`}
                  >
                    Buy
                  </button>
                  <button
                    onClick={() => setOrderSide('sell')}
                    className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
                      orderSide === 'sell' ? 'bg-red-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-white'
                    }`}
                  >
                    Sell
                  </button>
                </div>

                {/* Order Type */}
                <div className="flex space-x-2 mb-4">
                  <button
                    onClick={() => setOrderType('market')}
                    className={`flex-1 py-2 rounded-lg text-sm transition-colors ${
                      orderType === 'market' ? 'bg-gray-800 text-white border border-blue-600' : 'bg-gray-800 text-gray-400 hover:text-white'
                    }`}
                  >
                    Market
                  </button>
                  <button
                    onClick={() => setOrderType('limit')}
                    className={`flex-1 py-2 rounded-lg text-sm transition-colors ${
                      orderType === 'limit' ? 'bg-gray-800 text-white border border-blue-600' : 'bg-gray-800 text-gray-400 hover:text-white'
                    }`}
                  >
                    Limit
                  </button>
                </div>

                {/* Form Fields */}
                <div className="space-y-3">
                  {orderType === 'limit' && (
                    <div>
                      <label className="block text-sm font-medium mb-2">Price</label>
                      <input
                        type="number"
                        value={orderForm.price}
                        onChange={(e) => setOrderForm(prev => ({ ...prev, price: e.target.value }))}
                        placeholder="0.00"
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
                      />
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium mb-2">Amount</label>
                    <input
                      type="number"
                      value={orderForm.amount}
                      onChange={(e) => setOrderForm(prev => ({ ...prev, amount: e.target.value }))}
                      placeholder="0.00"
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Total (USDT)</label>
                    <input
                      type="number"
                      value={orderForm.total}
                      onChange={(e) => setOrderForm(prev => ({ ...prev, total: e.target.value }))}
                      placeholder="0.00"
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
                    />
                  </div>

                  {/* Quick Amount Buttons */}
                  <div className="grid grid-cols-4 gap-2">
                    {[25, 50, 75, 100].map(percent => (
                      <button
                        key={percent}
                        className="py-1 px-2 bg-gray-800 hover:bg-gray-700 rounded text-xs transition-colors"
                      >
                        {percent}%
                      </button>
                    ))}
                  </div>

                  <button className={`w-full py-3 rounded-lg font-medium transition-colors ${
                    orderSide === 'buy' 
                      ? 'bg-green-600 hover:bg-green-700 text-white' 
                      : 'bg-red-600 hover:bg-red-700 text-white'
                  }`}>
                    {orderSide === 'buy' ? 'Buy' : 'Sell'} {selectedPair.split('/')[0]}
                  </button>

                  <div className="p-3 bg-gray-800 rounded-lg">
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-400">Available Balance</span>
                      <span>10,000.00 USDT</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Estimated Fee</span>
                      <span>0.10 USDT</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Advanced Settings */}
              <div className="bg-gray-900 rounded-lg p-4 mt-4">
                <h3 className="font-semibold mb-3">Advanced Settings</h3>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium mb-2">Leverage</label>
                    <input
                      type="range"
                      min="1"
                      max="125"
                      value={leverage}
                      onChange={(e) => setLeverage(e.target.value)}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-400">
                      <span>1x</span>
                      <span>{leverage}x</span>
                      <span>125x</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Post-Only</span>
                    <button className="w-12 h-6 bg-gray-700 rounded-full relative">
                      <div className="w-5 h-5 bg-gray-400 rounded-full absolute top-0.5 left-0.5"></div>
                    </button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Reduce Only</span>
                    <button className="w-12 h-6 bg-gray-700 rounded-full relative">
                      <div className="w-5 h-5 bg-gray-400 rounded-full absolute top-0.5 left-0.5"></div>
                    </button>
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