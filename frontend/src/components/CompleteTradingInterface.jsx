/**
 * TigerEx Complete Trading Interface
 * Modern trading platform with all features from screenshot analysis
 * Includes Spot, Futures, Margin, Options, Alpha Trading, and ETF Trading
 */

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  CandlestickChart,
  Candle
} from 'recharts';
import { FiTrendingUp, FiTrendingDown, FiStar, FiSearch, FiSettings, FiBell, FiUser } from 'react-icons/fi';
import { BiChart, BiTime, BiRefresh } from 'react-icons/bi';
import { AiOutlineStar, AiFillStar } from 'react-icons/ai';
import { MdAttachMoney, MdShowChart, MdTimeline } from 'react-icons/md';

const CompleteTradingInterface = () => {
  const dispatch = useDispatch();
  const [activeTab, setActiveTab] = useState('markets');
  const [selectedPair, setSelectedPair] = useState('BTC/USDT');
  const [tradeMode, setTradeMode] = useState('spot'); // spot, futures, margin, options, alpha, etf
  const [orderType, setOrderType] = useState('market'); // market, limit, stop, stopLimit
  const [orderSide, setOrderSide] = useState('buy'); // buy, sell
  const [leverage, setLeverage] = useState(1);
  const [price, setPrice] = useState('');
  const [amount, setAmount] = useState('');
  const [chartType, setChartType] = useState('candlestick'); // candlestick, line, area, bar
  const [timeframe, setTimeframe] = useState('1h');
  const [showOrderBook, setShowOrderBook] = useState(true);
  const [showTrades, setShowTrades] = useState(true);
  const [favoritePairs, setFavoritePairs] = useState(['BTC/USDT', 'ETH/USDT']);
  const [searchQuery, setSearchQuery] = useState('');
  
  const chartRef = useRef(null);

  // Mock market data
  const marketData = useMemo(() => ({
    'BTC/USDT': { price: 43250.50, change: 2.34, volume: '1.2B', high: 44200, low: 42100 },
    'ETH/USDT': { price: 2280.30, change: -1.23, volume: '850M', high: 2350, low: 2200 },
    'BNB/USDT': { price: 315.80, change: 0.89, volume: '320M', high: 325, low: 310 },
    'SOL/USDT': { price: 98.45, change: 5.67, volume: '450M', high: 105, low: 92 },
    'ADA/USDT': { price: 0.58, change: -2.15, volume: '180M', high: 0.62, low: 0.55 },
  }), []);

  // Mock chart data
  const chartData = useMemo(() => {
    const data = [];
    let basePrice = 42000;
    for (let i = 0; i < 100; i++) {
      const change = (Math.random() - 0.5) * 500;
      basePrice += change;
      data.push({
        time: `${i}:00`,
        price: basePrice,
        high: basePrice + Math.random() * 200,
        low: basePrice - Math.random() * 200,
        open: basePrice - Math.random() * 100,
        close: basePrice,
        volume: Math.random() * 1000000
      });
    }
    return data;
  }, []);

  // Mock order book data
  const orderBookData = useMemo(() => ({
    bids: [
      [43250.00, 0.5421],
      [43249.50, 0.3214],
      [43249.00, 0.8932],
      [43248.50, 1.2341],
      [43248.00, 0.7856],
    ],
    asks: [
      [43250.50, 0.4231],
      [43251.00, 0.6123],
      [43251.50, 0.9234],
      [43252.00, 1.1234],
      [43252.50, 0.5678],
    ]
  }), []);

  // Mock recent trades
  const recentTrades = useMemo(() => [
    { time: '12:34:56', price: 43250.25, amount: 0.1234, type: 'buy' },
    { time: '12:34:55', price: 43249.75, amount: 0.5678, type: 'sell' },
    { time: '12:34:54', price: 43250.00, amount: 0.2345, type: 'buy' },
    { time: '12:34:53', price: 43248.50, amount: 0.8912, type: 'sell' },
    { time: '12:34:52', price: 43249.25, amount: 0.3456, type: 'buy' },
  ], []);

  // Calculate order book totals
  const orderBookTotals = useMemo(() => {
    let bidTotal = 0;
    let askTotal = 0;
    
    const bidsWithTotal = orderBookData.bids.map(([price, amount]) => {
      bidTotal += amount;
      return [price, amount, bidTotal];
    });
    
    const asksWithTotal = orderBookData.asks.map(([price, amount]) => {
      askTotal += amount;
      return [price, amount, askTotal];
    });
    
    return { bids: bidsWithTotal, asks: asksWithTotal };
  }, [orderBookData]);

  const toggleFavorite = (pair) => {
    setFavoritePairs(prev => 
      prev.includes(pair) 
        ? prev.filter(p => p !== pair)
        : [...prev, pair]
    );
  };

  const filteredPairs = useMemo(() => {
    if (!searchQuery) return Object.entries(marketData);
    return Object.entries(marketData).filter(([pair]) => 
      pair.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [marketData, searchQuery]);

  const calculateTotal = () => {
    if (!price || !amount) return 0;
    return parseFloat(price) * parseFloat(amount);
  };

  const calculateFee = () => {
    const total = calculateTotal();
    return total * 0.001; // 0.1% fee
  };

  const renderChart = () => {
    switch (chartType) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
              <XAxis dataKey="time" stroke="#666" />
              <YAxis stroke="#666" domain={['dataMin - 100', 'dataMax + 100']} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                labelStyle={{ color: '#fff' }}
              />
              <Line 
                type="monotone" 
                dataKey="price" 
                stroke="#00d4ff" 
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        );
      case 'area':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
              <XAxis dataKey="time" stroke="#666" />
              <YAxis stroke="#666" domain={['dataMin - 100', 'dataMax + 100']} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                labelStyle={{ color: '#fff' }}
              />
              <Area 
                type="monotone" 
                dataKey="price" 
                stroke="#00d4ff" 
                fill="#00d4ff" 
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        );
      default:
        return (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
              <XAxis dataKey="time" stroke="#666" />
              <YAxis stroke="#666" domain={['dataMin - 100', 'dataMax + 100']} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                labelStyle={{ color: '#fff' }}
              />
              <Line 
                type="monotone" 
                dataKey="price" 
                stroke="#00d4ff" 
                strokeWidth={1}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header Navigation */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center font-bold">
                  T
                </div>
                <span className="text-xl font-bold">TigerEx</span>
              </div>
              
              <nav className="hidden md:flex space-x-1">
                {[
                  { id: 'markets', label: 'Markets', icon: FiTrendingUp },
                  { id: 'trade', label: 'Trade', icon: BiChart },
                  { id: 'futures', label: 'Futures', icon: MdShowChart },
                  { id: 'portfolio', label: 'Portfolio', icon: FiUser },
                  { id: 'wallet', label: 'Wallet', icon: MdAttachMoney },
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors ${
                      activeTab === tab.id
                        ? 'bg-orange-500 text-white'
                        : 'text-gray-400 hover:text-white hover:bg-gray-700'
                    }`}
                  >
                    <tab.icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </button>
                ))}
              </nav>
            </div>
            
            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-400 hover:text-white">
                <FiBell className="w-5 h-5" />
              </button>
              <button className="p-2 text-gray-400 hover:text-white">
                <FiSettings className="w-5 h-5" />
              </button>
              <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                <FiUser className="w-4 h-4" />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-64px)]">
        {/* Left Sidebar - Trading Pairs */}
        <aside className="w-80 bg-gray-800 border-r border-gray-700 flex flex-col">
          {/* Search and Filter */}
          <div className="p-4 border-b border-gray-700">
            <div className="relative">
              <FiSearch className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search pairs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-orange-500"
              />
            </div>
            
            {/* Trading Mode Tabs */}
            <div className="flex mt-3 space-x-1">
              {[
                { id: 'spot', label: 'Spot' },
                { id: 'futures', label: 'Futures' },
                { id: 'margin', label: 'Margin' },
                { id: 'options', label: 'Options' },
                { id: 'alpha', label: 'Alpha' },
                { id: 'etf', label: 'ETF' },
              ].map(mode => (
                <button
                  key={mode.id}
                  onClick={() => setTradeMode(mode.id)}
                  className={`px-3 py-1 rounded text-sm transition-colors ${
                    tradeMode === mode.id
                      ? 'bg-orange-500 text-white'
                      : 'text-gray-400 hover:text-white hover:bg-gray-700'
                  }`}
                >
                  {mode.label}
                </button>
              ))}
            </div>
          </div>

          {/* Pairs List */}
          <div className="flex-1 overflow-y-auto">
            {/* Favorite Pairs */}
            {favoritePairs.length > 0 && (
              <div className="border-b border-gray-700">
                <div className="px-4 py-2 text-xs text-gray-500 font-semibold">FAVORITES</div>
                {favoritePairs.map(pair => {
                  const data = marketData[pair];
                  if (!data) return null;
                  return (
                    <div
                      key={pair}
                      onClick={() => setSelectedPair(pair)}
                      className={`px-4 py-3 border-b border-gray-700 hover:bg-gray-700 cursor-pointer transition-colors ${
                        selectedPair === pair ? 'bg-gray-700' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <AiFillStar className="w-4 h-4 text-yellow-500" />
                          <div>
                            <div className="font-medium">{pair.split('/')[0]}</div>
                            <div className="text-xs text-gray-400">{pair.split('/')[1]}</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-medium">{data.price.toLocaleString()}</div>
                          <div className={`text-xs ${data.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                            {data.change >= 0 ? '+' : ''}{data.change}%
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* All Pairs */}
            <div>
              <div className="px-4 py-2 text-xs text-gray-500 font-semibold">ALL PAIRS</div>
              {filteredPairs.map(([pair, data]) => (
                <div
                  key={pair}
                  onClick={() => setSelectedPair(pair)}
                  className={`px-4 py-3 border-b border-gray-700 hover:bg-gray-700 cursor-pointer transition-colors ${
                    selectedPair === pair ? 'bg-gray-700' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleFavorite(pair);
                        }}
                        className="text-gray-400 hover:text-yellow-500"
                      >
                        {favoritePairs.includes(pair) ? (
                          <AiFillStar className="w-4 h-4 text-yellow-500" />
                        ) : (
                          <AiOutlineStar className="w-4 h-4" />
                        )}
                      </button>
                      <div>
                        <div className="font-medium">{pair.split('/')[0]}</div>
                        <div className="text-xs text-gray-400">{pair.split('/')[1]}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">{data.price.toLocaleString()}</div>
                      <div className={`text-xs ${data.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {data.change >= 0 ? '+' : ''}{data.change}%
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* Main Trading Area */}
        <main className="flex-1 flex flex-col">
          {/* Trading Header */}
          <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold">{selectedPair}</h1>
                <div className="flex items-center space-x-4 mt-1">
                  <span className="text-2xl font-bold text-green-500">
                    {marketData[selectedPair]?.price.toLocaleString()}
                  </span>
                  <span className={`text-lg ${marketData[selectedPair]?.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {marketData[selectedPair]?.change >= 0 ? '+' : ''}{marketData[selectedPair]?.change}%
                  </span>
                </div>
              </div>
              
              {/* Chart Controls */}
              <div className="flex items-center space-x-4">
                {/* Timeframe Selection */}
                <div className="flex space-x-1">
                  {['1m', '5m', '15m', '1h', '4h', '1d', '1w'].map(tf => (
                    <button
                      key={tf}
                      onClick={() => setTimeframe(tf)}
                      className={`px-3 py-1 rounded text-sm transition-colors ${
                        timeframe === tf
                          ? 'bg-orange-500 text-white'
                          : 'text-gray-400 hover:text-white hover:bg-gray-700'
                      }`}
                    >
                      {tf}
                    </button>
                  ))}
                </div>
                
                {/* Chart Type Selection */}
                <div className="flex space-x-1">
                  {[
                    { id: 'candlestick', label: 'Candle', icon: MdShowChart },
                    { id: 'line', label: 'Line', icon: MdTimeline },
                    { id: 'area', label: 'Area', icon: BiChart },
                  ].map(type => (
                    <button
                      key={type.id}
                      onClick={() => setChartType(type.id)}
                      className={`px-3 py-1 rounded text-sm flex items-center space-x-1 transition-colors ${
                        chartType === type.id
                          ? 'bg-orange-500 text-white'
                          : 'text-gray-400 hover:text-white hover:bg-gray-700'
                      }`}
                    >
                      <type.icon className="w-4 h-4" />
                      <span>{type.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Chart and Trading Panels */}
          <div className="flex-1 flex">
            {/* Chart Area */}
            <div className="flex-1 flex flex-col">
              {/* Price Chart */}
              <div className="flex-1 bg-gray-800 p-4">
                {renderChart()}
              </div>
              
              {/* Trading Info */}
              <div className="bg-gray-800 border-t border-gray-700 px-6 py-4">
                <div className="grid grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="text-gray-400">24h High</div>
                    <div className="font-medium">{marketData[selectedPair]?.high.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-gray-400">24h Low</div>
                    <div className="font-medium">{marketData[selectedPair]?.low.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-gray-400">24h Volume</div>
                    <div className="font-medium">{marketData[selectedPair]?.volume}</div>
                  </div>
                  <div>
                    <div className="text-gray-400">Spread</div>
                    <div className="font-medium">0.50</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Sidebar - Order Book & Trading Panel */}
            <aside className="w-96 bg-gray-800 border-l border-gray-700 flex flex-col">
              {/* Order Book */}
              {showOrderBook && (
                <div className="flex-1 border-b border-gray-700">
                  <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
                    <h3 className="font-medium">Order Book</h3>
                    <button
                      onClick={() => setShowOrderBook(false)}
                      className="text-gray-400 hover:text-white"
                    >
                      ×
                    </button>
                  </div>
                  
                  <div className="h-64 overflow-hidden">
                    {/* Asks */}
                    <div className="h-1/2">
                      <div className="text-xs text-gray-500 px-2 py-1">Asks</div>
                      {orderBookTotals.asks.slice().reverse().map(([price, amount, total], index) => (
                        <div key={index} className="flex items-center justify-between px-2 py-1 text-xs hover:bg-gray-700">
                          <span className="text-red-500">{parseFloat(price).toLocaleString()}</span>
                          <span>{parseFloat(amount).toFixed(4)}</span>
                          <span className="text-gray-400">{parseFloat(total).toFixed(4)}</span>
                        </div>
                      ))}
                    </div>
                    
                    {/* Spread */}
                    <div className="border-t border-b border-gray-700 px-2 py-1 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-500">Spread</span>
                        <span className="text-yellow-500">
                          {(orderBookData.asks[0][0] - orderBookData.bids[0][0]).toFixed(2)}
                        </span>
                      </div>
                    </div>
                    
                    {/* Bids */}
                    <div className="h-1/2">
                      <div className="text-xs text-gray-500 px-2 py-1">Bids</div>
                      {orderBookTotals.bids.map(([price, amount, total], index) => (
                        <div key={index} className="flex items-center justify-between px-2 py-1 text-xs hover:bg-gray-700">
                          <span className="text-green-500">{parseFloat(price).toLocaleString()}</span>
                          <span>{parseFloat(amount).toFixed(4)}</span>
                          <span className="text-gray-400">{parseFloat(total).toFixed(4)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Trading Panel */}
              <div className="flex-1 flex flex-col">
                {/* Buy/Sell Tabs */}
                <div className="flex border-b border-gray-700">
                  {['buy', 'sell'].map(side => (
                    <button
                      key={side}
                      onClick={() => setOrderSide(side)}
                      className={`flex-1 py-2 font-medium transition-colors ${
                        orderSide === side
                          ? side === 'buy' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
                          : 'text-gray-400 hover:text-white'
                      }`}
                    >
                      {side.toUpperCase()}
                    </button>
                  ))}
                </div>

                {/* Order Type Selection */}
                <div className="px-4 py-3 border-b border-gray-700">
                  <label className="text-xs text-gray-400">Order Type</label>
                  <div className="grid grid-cols-2 gap-2 mt-1">
                    {[
                      { id: 'market', label: 'Market' },
                      { id: 'limit', label: 'Limit' },
                      { id: 'stop', label: 'Stop' },
                      { id: 'stopLimit', label: 'Stop Limit' },
                    ].map(type => (
                      <button
                        key={type.id}
                        onClick={() => setOrderType(type.id)}
                        className={`px-3 py-2 rounded text-sm transition-colors ${
                          orderType === type.id
                            ? 'bg-orange-500 text-white'
                            : 'bg-gray-700 text-gray-400 hover:text-white'
                        }`}
                      >
                        {type.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Price Input */}
                {orderType !== 'market' && (
                  <div className="px-4 py-3 border-b border-gray-700">
                    <label className="text-xs text-gray-400">Price (USDT)</label>
                    <input
                      type="number"
                      value={price}
                      onChange={(e) => setPrice(e.target.value)}
                      placeholder="0.00"
                      className="w-full mt-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:outline-none focus:border-orange-500"
                    />
                  </div>
                )}

                {/* Amount Input */}
                <div className="px-4 py-3 border-b border-gray-700">
                  <label className="text-xs text-gray-400">Amount (BTC)</label>
                  <input
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder="0.00"
                    className="w-full mt-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:outline-none focus:border-orange-500"
                  />
                  <div className="flex justify-between mt-2">
                    <span className="text-xs text-gray-400">Available: 0.12345678 BTC</span>
                    <div className="space-x-2">
                      <button className="text-xs text-orange-500 hover:text-orange-400">25%</button>
                      <button className="text-xs text-orange-500 hover:text-orange-400">50%</button>
                      <button className="text-xs text-orange-500 hover:text-orange-400">75%</button>
                      <button className="text-xs text-orange-500 hover:text-orange-400">100%</button>
                    </div>
                  </div>
                </div>

                {/* Leverage (for Futures/Margin) */}
                {(tradeMode === 'futures' || tradeMode === 'margin') && (
                  <div className="px-4 py-3 border-b border-gray-700">
                    <label className="text-xs text-gray-400">Leverage: {leverage}x</label>
                    <input
                      type="range"
                      min="1"
                      max="125"
                      value={leverage}
                      onChange={(e) => setLeverage(parseInt(e.target.value))}
                      className="w-full mt-1"
                    />
                    <div className="flex justify-between text-xs text-gray-400 mt-1">
                      <span>1x</span>
                      <span>25x</span>
                      <span>50x</span>
                      <span>100x</span>
                      <span>125x</span>
                    </div>
                  </div>
                )}

                {/* Order Summary */}
                <div className="px-4 py-3 border-b border-gray-700">
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Total</span>
                      <span>{calculateTotal().toFixed(2)} USDT</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Fee</span>
                      <span>{calculateFee().toFixed(4)} USDT</span>
                    </div>
                    <div className="flex justify-between font-medium">
                      <span>You will {orderSide}</span>
                      <span>{amount || '0.0000'} BTC</span>
                    </div>
                  </div>
                </div>

                {/* Place Order Button */}
                <div className="p-4">
                  <button
                    className={`w-full py-3 rounded-lg font-medium transition-colors ${
                      orderSide === 'buy'
                        ? 'bg-green-500 hover:bg-green-600 text-white'
                        : 'bg-red-500 hover:bg-red-600 text-white'
                    }`}
                  >
                    {orderType === 'market' ? `${orderSide.toUpperCase()} ${selectedPair.split('/')[0]}` : `Place ${orderSide.toUpperCase()} Order`}
                  </button>
                </div>
              </div>
            </aside>
          </div>
        </main>
      </div>
    </div>
  );
};

export default CompleteTradingInterface;