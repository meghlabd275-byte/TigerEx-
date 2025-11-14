'use client'

import React, { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Activity, DollarSign, BarChart3, Settings, Bell, User, Search, Menu, X, ArrowUpRight, ArrowDownRight, Clock, Globe, Shield, Star, ChevronRight, Plus, Minus, Info, Wallet, History, BookOpen, HelpCircle, LogOut, Home, PieChart, FileText, Users, Lock, Eye, EyeOff, ChevronDown, Filter, Grid, List, Download, Upload, RefreshCw, Copy, ExternalLink, CheckCircle, AlertCircle, AlertTriangle, Calendar, Target, Zap, Award, Calculator } from 'lucide-react'

interface OptionContract {
  symbol: string
  type: 'call' | 'put'
  strike: number
  expiration: string
  bid: number
  ask: number
  volume: number
  openInterest: number
  impliedVolatility: number
  delta: number
  gamma: number
  theta: number
  vega: number
  inTheMoney: boolean
}

interface OptionChain {
  expiration: string
  calls: OptionContract[]
  puts: OptionContract[]
}

interface Position {
  id: string
  symbol: string
  type: 'call' | 'put'
  strike: number
  expiration: string
  quantity: number
  avgCost: number
  currentPrice: number
  pnl: number
  pnlPercent: number
  status: 'open' | 'closed'
}

export default function OptionsPage() {
  const [selectedTab, setSelectedTab] = useState('trade')
  const [selectedSymbol, setSelectedSymbol] = useState('BTC')
  const [selectedExpiration, setSelectedExpiration] = useState('2024-12-27')
  const [quantity, setQuantity] = useState('1')
  const [orderType, setOrderType] = useState('limit')
  const [limitPrice, setLimitPrice] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [showGreeks, setShowGreeks] = useState(true)
  const [chartView, setChartView] = useState('chain')

  const symbols = [
    { symbol: 'BTC', name: 'Bitcoin', price: 67850.25, change: 2.5 },
    { symbol: 'ETH', name: 'Ethereum', price: 3542.18, change: -1.2 },
    { symbol: 'SOL', name: 'Solana', price: 145.67, change: 3.2 },
    { symbol: 'BNB', name: 'Binance Coin', price: 612.45, change: 0.8 }
  ]

  const expirations = [
    { date: '2024-11-22', label: 'Weekly', dte: 8 },
    { date: '2024-11-29', label: 'Weekly', dte: 15 },
    { date: '2024-12-27', label: 'Monthly', dte: 43 },
    { date: '2025-01-31', label: 'Monthly', dte: 78 },
    { date: '2025-03-28', label: 'Quarterly', dte: 135 }
  ]

  const generateOptionChain = (): OptionChain => {
    const basePrice = 67850.25
    const strikes = []
    
    // Generate strikes around the current price
    for (let i = -10; i <= 10; i++) {
      strikes.push(basePrice + (i * 1000))
    }

    const calls = strikes.map(strike => ({
      symbol: `${selectedSymbol}-${selectedExpiration}-${strike}-C`,
      type: 'call' as const,
      strike,
      expiration: selectedExpiration,
      bid: Math.max(0.01, basePrice - strike + Math.random() * 500),
      ask: Math.max(0.01, basePrice - strike + Math.random() * 500 + 10),
      volume: Math.floor(Math.random() * 1000),
      openInterest: Math.floor(Math.random() * 5000),
      impliedVolatility: 0.65 + Math.random() * 0.35,
      delta: Math.max(0.01, Math.min(0.99, 0.5 + (basePrice - strike) / (basePrice * 2) + Math.random() * 0.1)),
      gamma: 0.0001 + Math.random() * 0.0005,
      theta: -(0.01 + Math.random() * 0.05),
      vega: 0.1 + Math.random() * 0.3,
      inTheMoney: strike < basePrice
    }))

    const puts = strikes.map(strike => ({
      symbol: `${selectedSymbol}-${selectedExpiration}-${strike}-P`,
      type: 'put' as const,
      strike,
      expiration: selectedExpiration,
      bid: Math.max(0.01, strike - basePrice + Math.random() * 500),
      ask: Math.max(0.01, strike - basePrice + Math.random() * 500 + 10),
      volume: Math.floor(Math.random() * 1000),
      openInterest: Math.floor(Math.random() * 5000),
      impliedVolatility: 0.65 + Math.random() * 0.35,
      delta: Math.max(-0.99, Math.min(-0.01, -0.5 + (basePrice - strike) / (basePrice * 2) + Math.random() * 0.1)),
      gamma: 0.0001 + Math.random() * 0.0005,
      theta: -(0.01 + Math.random() * 0.05),
      vega: 0.1 + Math.random() * 0.3,
      inTheMoney: strike > basePrice
    }))

    return {
      expiration: selectedExpiration,
      calls: calls.sort((a, b) => b.strike - a.strike),
      puts: puts.sort((a, b) => b.strike - a.strike)
    }
  }

  const [optionChain, setOptionChain] = useState<OptionChain>(generateOptionChain())

  const positions: Position[] = [
    {
      id: '1',
      symbol: 'BTC',
      type: 'call',
      strike: 65000,
      expiration: '2024-12-27',
      quantity: 5,
      avgCost: 2850.50,
      currentPrice: 3250.75,
      pnl: 2001.25,
      pnlPercent: 14.03,
      status: 'open'
    },
    {
      id: '2',
      symbol: 'ETH',
      type: 'put',
      strike: 3200,
      expiration: '2024-11-29',
      quantity: 10,
      avgCost: 45.25,
      currentPrice: 32.15,
      pnl: -130.95,
      pnlPercent: -28.93,
      status: 'open'
    }
  ]

  useEffect(() => {
    setOptionChain(generateOptionChain())
  }, [selectedSymbol, selectedExpiration])

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-gray-400 hover:text-white"
            >
              {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            <div className="flex items-center space-x-2">
              <Target className="text-purple-400" size={28} />
              <h1 className="text-2xl font-bold">Options Trading</h1>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-gray-700 rounded-lg px-3 py-2">
              <Search size={16} className="text-gray-400" />
              <select
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value)}
                className="bg-transparent outline-none text-sm"
              >
                {symbols.map(sym => (
                  <option key={sym.symbol} value={sym.symbol}>
                    {sym.symbol} - {sym.name}
                  </option>
                ))}
              </select>
            </div>
            
            <button className="flex items-center space-x-2 bg-gray-700 hover:bg-gray-600 px-3 py-2 rounded-lg">
              <Bell size={16} />
              <span className="text-sm">Alerts</span>
            </button>
            
            <button className="flex items-center space-x-2 bg-gray-700 hover:bg-gray-600 px-3 py-2 rounded-lg">
              <Settings size={16} />
              <span className="text-sm">Settings</span>
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        {sidebarOpen && (
          <aside className="w-64 bg-gray-800 border-r border-gray-700 min-h-screen">
            <nav className="p-4">
              <div className="space-y-1">
                {[
                  { id: 'trade', label: 'Trade Options', icon: Target },
                  { id: 'chain', label: 'Option Chain', icon: BarChart3 },
                  { id: 'positions', label: 'Positions', icon: PieChart },
                  { id: 'watchlist', label: 'Watchlist', icon: Star },
                  { id: 'volatility', label: 'Volatility Analysis', icon: Activity },
                  { id: 'strategies', label: 'Strategies', icon: Zap },
                  { id: 'history', label: 'Trade History', icon: History },
                  { id: 'tools', label: 'Tools & Calculators', icon: Calculator },
                ].map(item => (
                  <button
                    key={item.id}
                    onClick={() => setSelectedTab(item.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                      selectedTab === item.id
                        ? 'bg-purple-600 text-white'
                        : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                    }`}
                  >
                    <item.icon size={18} />
                    <span className="text-sm font-medium">{item.label}</span>
                  </button>
                ))}
              </div>
            </nav>
          </aside>
        )}

        {/* Main Content */}
        <main className="flex-1 p-6">
          {/* Symbol Info Bar */}
          <div className="bg-gray-800 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div>
                  <h2 className="text-xl font-bold">{selectedSymbol}/USD</h2>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-2xl font-bold">
                      ${symbols.find(s => s.symbol === selectedSymbol)?.price.toLocaleString()}
                    </span>
                    <span className={`flex items-center text-sm ${
                      symbols.find(s => s.symbol === selectedSymbol)?.change! > 0
                        ? 'text-green-400'
                        : 'text-red-400'
                    }`}>
                      {symbols.find(s => s.symbol === selectedSymbol)?.change! > 0 ? (
                        <TrendingUp size={16} />
                      ) : (
                        <TrendingDown size={16} />
                      )}
                      {Math.abs(symbols.find(s => s.symbol === selectedSymbol)?.change || 0)}%
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4 text-sm text-gray-400">
                  <span>Volume: ${(Math.random() * 1000000000).toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ",")}</span>
                  <span>IV: {(65 + Math.random() * 15).toFixed(1)}%</span>
                  <span>PCR: {(0.8 + Math.random() * 0.4).toFixed(2)}</span>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {expirations.map(exp => (
                  <button
                    key={exp.date}
                    onClick={() => setSelectedExpiration(exp.date)}
                    className={`px-3 py-1 rounded text-sm ${
                      selectedExpiration === exp.date
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {exp.label} ({exp.dte}D)
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Trade Tab */}
          {selectedTab === 'trade' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Order Form */}
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Place Order</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">Order Type</label>
                    <div className="grid grid-cols-2 gap-2">
                      {['call', 'put'].map(type => (
                        <button
                          key={type}
                          onClick={() => setOrderType(type)}
                          className={`px-3 py-2 rounded capitalize ${
                            orderType === type
                              ? type === 'call' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                          }`}
                        >
                          {type}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">Strike Price</label>
                    <select className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2">
                      {optionChain.calls.map(option => (
                        <option key={option.strike} value={option.strike}>
                          ${option.strike.toLocaleString()}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">Quantity</label>
                    <input
                      type="number"
                      value={quantity}
                      onChange={(e) => setQuantity(e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2"
                      min="1"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">Order Price</label>
                    <div className="space-y-2">
                      <button
                        onClick={() => setOrderType('market')}
                        className={`w-full px-3 py-2 rounded ${
                          orderType === 'market'
                            ? 'bg-purple-600 text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                      >
                        Market
                      </button>
                      <input
                        type="number"
                        value={limitPrice}
                        onChange={(e) => setLimitPrice(e.target.value)}
                        placeholder="Limit Price"
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2"
                        step="0.01"
                      />
                    </div>
                  </div>

                  <button className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 rounded-lg">
                    Place Order
                  </button>
                </div>
              </div>

              {/* Option Chain */}
              <div className="lg:col-span-2 bg-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Option Chain</h3>
                  <div className="flex items-center space-x-2">
                    <label className="flex items-center space-x-2 text-sm">
                      <input
                        type="checkbox"
                        checked={showGreeks}
                        onChange={(e) => setShowGreeks(e.target.checked)}
                        className="rounded"
                      />
                      <span>Show Greeks</span>
                    </label>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-700">
                        <th className="text-left py-2">Calls</th>
                        <th className="text-center py-2">Bid</th>
                        <th className="text-center py-2">Ask</th>
                        <th className="text-center py-2">Volume</th>
                        <th className="text-center py-2">OI</th>
                        <th className="text-center py-2">IV</th>
                        {showGreeks && (
                          <>
                            <th className="text-center py-2">Delta</th>
                            <th className="text-center py-2">Gamma</th>
                            <th className="text-center py-2">Theta</th>
                            <th className="text-center py-2">Vega</th>
                          </>
                        )}
                        <th className="text-center py-2">Strike</th>
                        <th className="text-center py-2">IV</th>
                        <th className="text-center py-2">OI</th>
                        <th className="text-center py-2">Volume</th>
                        <th className="text-center py-2">Bid</th>
                        <th className="text-center py-2">Ask</th>
                        <th className="text-right py-2">Puts</th>
                      </tr>
                    </thead>
                    <tbody>
                      {optionChain.calls.map((call, index) => {
                        const put = optionChain.puts[index]
                        return (
                          <tr key={call.strike} className="border-b border-gray-700">
                            {/* Calls */}
                            <td className={`py-2 ${call.inTheMoney ? 'text-blue-400' : 'text-gray-400'}`}>
                              {call.symbol}
                            </td>
                            <td className="text-center py-2 text-green-400">{call.bid.toFixed(2)}</td>
                            <td className="text-center py-2 text-red-400">{call.ask.toFixed(2)}</td>
                            <td className="text-center py-2">{call.volume}</td>
                            <td className="text-center py-2">{call.openInterest}</td>
                            <td className="text-center py-2">{(call.impliedVolatility * 100).toFixed(1)}%</td>
                            {showGreeks && (
                              <>
                                <td className="text-center py-2">{call.delta.toFixed(3)}</td>
                                <td className="text-center py-2">{call.gamma.toFixed(4)}</td>
                                <td className="text-center py-2 text-red-400">{call.theta.toFixed(3)}</td>
                                <td className="text-center py-2">{call.vega.toFixed(3)}</td>
                              </>
                            )}
                            
                            {/* Strike */}
                            <td className="text-center py-2 font-bold">{call.strike.toLocaleString()}</td>
                            
                            {/* Puts */}
                            <td className="text-center py-2">{(put.impliedVolatility * 100).toFixed(1)}%</td>
                            <td className="text-center py-2">{put.openInterest}</td>
                            <td className="text-center py-2">{put.volume}</td>
                            <td className="text-center py-2 text-green-400">{put.bid.toFixed(2)}</td>
                            <td className="text-center py-2 text-red-400">{put.ask.toFixed(2)}</td>
                            <td className={`py-2 text-right ${put.inTheMoney ? 'text-blue-400' : 'text-gray-400'}`}>
                              {put.symbol}
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Positions Tab */}
          {selectedTab === 'positions' && (
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Open Positions</h3>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="text-left py-3">Symbol</th>
                      <th className="text-left py-3">Type</th>
                      <th className="text-center py-3">Strike</th>
                      <th className="text-center py-3">Expiration</th>
                      <th className="text-center py-3">Quantity</th>
                      <th className="text-center py-3">Avg Cost</th>
                      <th className="text-center py-3">Current Price</th>
                      <th className="text-right py-3">P&L</th>
                      <th className="text-right py-3">P&L %</th>
                      <th className="text-center py-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {positions.map(position => (
                      <tr key={position.id} className="border-b border-gray-700">
                        <td className="py-3 font-medium">{position.symbol}</td>
                        <td className="py-3">
                          <span className={`px-2 py-1 rounded text-xs ${
                            position.type === 'call' ? 'bg-green-600/20 text-green-400' : 'bg-red-600/20 text-red-400'
                          }`}>
                            {position.type.toUpperCase()}
                          </span>
                        </td>
                        <td className="text-center py-3">${position.strike.toLocaleString()}</td>
                        <td className="text-center py-3">{position.expiration}</td>
                        <td className="text-center py-3">{position.quantity}</td>
                        <td className="text-center py-3">${position.avgCost.toFixed(2)}</td>
                        <td className="text-center py-3">${position.currentPrice.toFixed(2)}</td>
                        <td className={`text-right py-3 font-medium ${
                          position.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          ${position.pnl >= 0 ? '+' : ''}{position.pnl.toFixed(2)}
                        </td>
                        <td className={`text-right py-3 font-medium ${
                          position.pnlPercent >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {position.pnlPercent >= 0 ? '+' : ''}{position.pnlPercent.toFixed(2)}%
                        </td>
                        <td className="text-center py-3">
                          <button className="text-blue-400 hover:text-blue-300 text-sm">
                            Close
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Other tabs placeholder */}
          {selectedTab !== 'trade' && selectedTab !== 'positions' && (
            <div className="bg-gray-800 rounded-lg p-12 text-center">
              <div className="text-gray-400">
                {selectedTab === 'chain' && <BarChart3 size={48} className="mx-auto mb-4" />}
                {selectedTab === 'watchlist' && <Star size={48} className="mx-auto mb-4" />}
                {selectedTab === 'volatility' && <Activity size={48} className="mx-auto mb-4" />}
                {selectedTab === 'strategies' && <Zap size={48} className="mx-auto mb-4" />}
                {selectedTab === 'history' && <History size={48} className="mx-auto mb-4" />}
                {selectedTab === 'tools' && <Settings size={48} className="mx-auto mb-4" />}
                
                <h3 className="text-xl font-semibold mb-2">
                  {selectedTab.charAt(0).toUpperCase() + selectedTab.slice(1)} Features
                </h3>
                <p className="text-gray-500">
                  Advanced {selectedTab} functionality coming soon
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}