'use client';

import React, { useState } from 'react';
import { 
  Search, 
  Bell, 
  User, 
  Settings, 
  Star,
  ChevronDown,
  TrendingUp,
  TrendingDown,
  MoreHorizontal,
  Maximize2,
  BarChart3,
  Activity
} from 'lucide-react';

interface OrderBookItem {
  price: string;
  amount: string;
  total: string;
}

interface TradeItem {
  price: string;
  amount: string;
  time: string;
  side: 'buy' | 'sell';
}

const mockOrderBook = {
  asks: [
    { price: '122,887.76', amount: '0.00047', total: '57.74' },
    { price: '122,886.48', amount: '0.00010', total: '12.29' },
    { price: '122,885.20', amount: '0.00025', total: '30.72' },
    { price: '122,884.92', amount: '0.00018', total: '22.12' },
    { price: '122,883.64', amount: '0.00032', total: '39.32' },
  ] as OrderBookItem[],
  bids: [
    { price: '122,873.35', amount: '0.00025', total: '30.72' },
    { price: '122,872.07', amount: '0.00040', total: '49.15' },
    { price: '122,870.79', amount: '0.00015', total: '18.43' },
    { price: '122,869.51', amount: '0.00028', total: '34.40' },
    { price: '122,868.23', amount: '0.00035', total: '43.00' },
  ] as OrderBookItem[],
};

const mockTrades: TradeItem[] = [
  { price: '122,887.76', amount: '0.00183', time: '22:55:14', side: 'buy' },
  { price: '122,887.77', amount: '0.02190', time: '22:55:14', side: 'sell' },
  { price: '122,887.76', amount: '0.00148', time: '22:55:14', side: 'buy' },
  { price: '122,887.74', amount: '0.00094', time: '22:55:14', side: 'sell' },
  { price: '122,887.76', amount: '0.00020', time: '22:55:14', side: 'buy' },
];

export default function TradingScreen() {
  const [orderType, setOrderType] = useState<'limit' | 'market' | 'stop-limit'>('limit');
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [price, setPrice] = useState('122,866.48');
  const [amount, setAmount] = useState('');
  const [total, setTotal] = useState('');
  const [activeTab, setActiveTab] = useState('Chart');

  return (
    <div className="flex-1 bg-bg-primary text-text-primary overflow-hidden">
      {/* Top Navigation */}
      <div className="bg-bg-secondary border-b border-border-primary px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Trading Pair Info */}
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold">BTC/USDT</span>
              <Star size={16} className="text-text-secondary hover:text-primary cursor-pointer" />
            </div>
            <div className="flex items-center gap-4 text-sm">
              <div>
                <span className="text-2xl font-bold text-success">122,887.76</span>
                <span className="text-success ml-2">+3,152.87 (+2.63%)</span>
              </div>
            </div>
            <div className="flex items-center gap-6 text-xs text-text-secondary">
              <div>
                <span className="block">24h High</span>
                <span className="text-text-primary">123,994.99</span>
              </div>
              <div>
                <span className="block">24h Low</span>
                <span className="text-text-primary">119,248.30</span>
              </div>
              <div>
                <span className="block">24h Volume(BTC)</span>
                <span className="text-text-primary">9,507.93</span>
              </div>
              <div>
                <span className="block">24h Volume(USDT)</span>
                <span className="text-text-primary">1.16B</span>
              </div>
            </div>
          </div>

          {/* Right Side Controls */}
          <div className="flex items-center gap-4">
            <Search size={20} className="text-text-secondary hover:text-text-primary cursor-pointer" />
            <button className="btn-primary">
              Deposit
            </button>
            <Bell size={20} className="text-text-secondary hover:text-text-primary cursor-pointer" />
            <Settings size={20} className="text-text-secondary hover:text-text-primary cursor-pointer" />
            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center cursor-pointer">
              <User size={16} className="text-black" />
            </div>
          </div>
        </div>
      </div>

      {/* Main Trading Interface */}
      <div className="flex h-[calc(100vh-120px)]">
        {/* Left Panel - Chart Area */}
        <div className="flex-1 flex flex-col">
          {/* Chart Tabs */}
          <div className="bg-bg-secondary border-b border-border-primary px-4 py-2">
            <div className="flex items-center gap-6">
              {['Chart', 'Info', 'Trading Data', 'Trading Analysis', 'Square'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-3 py-2 text-sm font-medium ${
                    activeTab === tab
                      ? 'text-primary border-b-2 border-primary'
                      : 'text-text-secondary hover:text-text-primary'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>

          {/* Chart Controls */}
          <div className="bg-bg-secondary border-b border-border-primary px-4 py-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {/* Timeframes */}
                <div className="flex items-center gap-2">
                  {['1s', '15m', '1h', '4h', '1D', '1W'].map((timeframe) => (
                    <button
                      key={timeframe}
                      className="px-2 py-1 text-xs text-text-secondary hover:text-text-primary hover:bg-bg-tertiary rounded"
                    >
                      {timeframe}
                    </button>
                  ))}
                </div>
                
                {/* Chart Type */}
                <div className="flex items-center gap-2">
                  <BarChart3 size={16} className="text-text-secondary" />
                  <Activity size={16} className="text-text-secondary" />
                  <TrendingUp size={16} className="text-text-secondary" />
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button className="text-xs text-text-secondary hover:text-text-primary">
                  Original
                </button>
                <button className="text-xs text-primary">
                  TradingView
                </button>
                <Maximize2 size={16} className="text-text-secondary hover:text-text-primary cursor-pointer" />
              </div>
            </div>
          </div>

          {/* Chart Area */}
          <div className="flex-1 bg-bg-primary p-4">
            <div className="w-full h-full bg-bg-secondary rounded-lg flex items-center justify-center">
              <div className="text-center">
                <BarChart3 size={48} className="text-text-secondary mx-auto mb-4" />
                <p className="text-text-secondary">Trading Chart</p>
                <p className="text-xs text-text-tertiary mt-1">
                  Price: 122,887.76 | Open: 120,529.35 | High: 123,994.99 | Low: 119,248.30
                </p>
              </div>
            </div>
          </div>

          {/* Market Trades */}
          <div className="h-64 bg-bg-secondary border-t border-border-primary">
            <div className="p-4">
              <h3 className="text-sm font-semibold mb-3">Market Trades</h3>
              <div className="grid grid-cols-3 gap-4 text-xs text-text-secondary mb-2">
                <span>Price (USDT)</span>
                <span className="text-right">Amount (BTC)</span>
                <span className="text-right">Time</span>
              </div>
              <div className="space-y-1 max-h-40 overflow-y-auto">
                {mockTrades.map((trade, index) => (
                  <div key={index} className="grid grid-cols-3 gap-4 text-xs py-1">
                    <span className={trade.side === 'buy' ? 'text-success' : 'text-danger'}>
                      {trade.price}
                    </span>
                    <span className="text-right text-text-primary">{trade.amount}</span>
                    <span className="text-right text-text-secondary">{trade.time}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Center Panel - Order Book */}
        <div className="w-80 bg-bg-secondary border-l border-r border-border-primary">
          <div className="p-4">
            <h3 className="text-sm font-semibold mb-3">Order Book</h3>
            <div className="grid grid-cols-3 gap-4 text-xs text-text-secondary mb-2">
              <span>Price (USDT)</span>
              <span className="text-right">Amount (BTC)</span>
              <span className="text-right">Total</span>
            </div>

            {/* Asks */}
            <div className="space-y-1 mb-4">
              {mockOrderBook.asks.reverse().map((ask, index) => (
                <div key={index} className="grid grid-cols-3 gap-4 text-xs py-1 hover:bg-bg-tertiary cursor-pointer">
                  <span className="text-danger">{ask.price}</span>
                  <span className="text-right text-text-primary">{ask.amount}</span>
                  <span className="text-right text-text-secondary">{ask.total}</span>
                </div>
              ))}
            </div>

            {/* Current Price */}
            <div className="text-center py-2 mb-4 bg-success/10 rounded">
              <span className="text-success font-semibold">122,887.76</span>
              <TrendingUp size={12} className="inline ml-1 text-success" />
            </div>

            {/* Bids */}
            <div className="space-y-1">
              {mockOrderBook.bids.map((bid, index) => (
                <div key={index} className="grid grid-cols-3 gap-4 text-xs py-1 hover:bg-bg-tertiary cursor-pointer">
                  <span className="text-success">{bid.price}</span>
                  <span className="text-right text-text-primary">{bid.amount}</span>
                  <span className="text-right text-text-secondary">{bid.total}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Panel - Order Entry */}
        <div className="w-80 bg-bg-secondary">
          <div className="p-4">
            {/* Trading Mode Tabs */}
            <div className="flex mb-4">
              {['Spot', 'Cross', 'Isolated', 'Grid'].map((mode) => (
                <button
                  key={mode}
                  className={`flex-1 py-2 text-xs font-medium ${
                    mode === 'Spot'
                      ? 'text-primary border-b-2 border-primary'
                      : 'text-text-secondary hover:text-text-primary'
                  }`}
                >
                  {mode}
                </button>
              ))}
            </div>

            {/* Buy/Sell Toggle */}
            <div className="flex mb-4">
              <button
                onClick={() => setSide('buy')}
                className={`flex-1 py-3 text-center font-medium rounded-l-lg ${
                  side === 'buy'
                    ? 'bg-success text-white'
                    : 'bg-bg-tertiary text-text-secondary'
                }`}
              >
                Buy
              </button>
              <button
                onClick={() => setSide('sell')}
                className={`flex-1 py-3 text-center font-medium rounded-r-lg ${
                  side === 'sell'
                    ? 'bg-danger text-white'
                    : 'bg-bg-tertiary text-text-secondary'
                }`}
              >
                Sell
              </button>
            </div>

            {/* Order Type */}
            <div className="mb-4">
              <div className="flex items-center gap-2 mb-2">
                <button
                  onClick={() => setOrderType('limit')}
                  className={`px-3 py-1 text-xs rounded ${
                    orderType === 'limit'
                      ? 'bg-primary text-black'
                      : 'bg-bg-tertiary text-text-secondary'
                  }`}
                >
                  Limit
                </button>
                <button
                  onClick={() => setOrderType('market')}
                  className={`px-3 py-1 text-xs rounded ${
                    orderType === 'market'
                      ? 'bg-primary text-black'
                      : 'bg-bg-tertiary text-text-secondary'
                  }`}
                >
                  Market
                </button>
                <button className="flex items-center gap-1 px-3 py-1 text-xs bg-bg-tertiary text-text-secondary rounded">
                  Stop Limit
                  <ChevronDown size={12} />
                </button>
              </div>
            </div>

            {/* Price Input */}
            <div className="mb-4">
              <label className="block text-xs text-text-secondary mb-2">Price</label>
              <div className="relative">
                <input
                  type="text"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  className="input-primary w-full"
                  placeholder="0.00"
                />
                <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary text-xs">
                  USDT
                </span>
              </div>
            </div>

            {/* Amount Input */}
            <div className="mb-4">
              <label className="block text-xs text-text-secondary mb-2">Amount</label>
              <div className="relative">
                <input
                  type="text"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="input-primary w-full"
                  placeholder="0.00"
                />
                <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary text-xs">
                  BTC
                </span>
              </div>
            </div>

            {/* Percentage Slider */}
            <div className="mb-4">
              <div className="flex justify-between mb-2">
                {[25, 50, 75, 100].map((percent) => (
                  <button
                    key={percent}
                    className="px-2 py-1 text-xs bg-bg-tertiary text-text-secondary rounded hover:bg-bg-quaternary"
                  >
                    {percent}%
                  </button>
                ))}
              </div>
              <input
                type="range"
                min="0"
                max="100"
                className="w-full h-1 bg-bg-tertiary rounded-lg appearance-none cursor-pointer"
              />
            </div>

            {/* Total */}
            <div className="mb-4">
              <label className="block text-xs text-text-secondary mb-2">Total</label>
              <div className="relative">
                <input
                  type="text"
                  value={total}
                  onChange={(e) => setTotal(e.target.value)}
                  className="input-primary w-full"
                  placeholder="0.00"
                />
                <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary text-xs">
                  USDT
                </span>
              </div>
              <p className="text-xs text-text-tertiary mt-1">Minimum 5</p>
            </div>

            {/* Available Balance */}
            <div className="mb-4 text-xs text-text-secondary">
              Available: 0.00000000 USDT
            </div>

            {/* Additional Info */}
            <div className="mb-4 p-3 bg-bg-tertiary rounded-lg text-xs text-text-secondary">
              Now you can place Spot orders using assets in your Flexible or Locked Products. 
              Click here to view or adjust this setting.
            </div>

            {/* Max Buy / Est Fee */}
            <div className="mb-4 space-y-1 text-xs text-text-secondary">
              <div className="flex justify-between">
                <span>Max Buy</span>
                <span>0 BTC</span>
              </div>
              <div className="flex justify-between">
                <span>Est. Fee</span>
                <span>0.00000000 BTC</span>
              </div>
            </div>

            {/* Buy/Sell Button */}
            <button
              className={`w-full py-3 rounded-lg font-medium text-white mb-3 ${
                side === 'buy' ? 'bg-success hover:bg-success/90' : 'bg-danger hover:bg-danger/90'
              }`}
            >
              {side === 'buy' ? 'Buy BTC' : 'Sell BTC'}
            </button>

            {/* Fee Level */}
            <div className="text-center text-xs text-text-secondary">
              Fee Level: VIP 0
            </div>
          </div>

          {/* Open Orders */}
          <div className="border-t border-border-primary">
            <div className="flex">
              <button className="flex-1 py-3 text-center text-xs font-medium text-primary border-b-2 border-primary">
                Open Orders(0)
              </button>
              <button className="flex-1 py-3 text-center text-xs font-medium text-text-secondary">
                Funds
              </button>
            </div>
            <div className="p-4">
              <div className="flex items-center justify-between mb-2">
                <label className="flex items-center gap-2 text-xs text-text-secondary">
                  <input type="checkbox" className="w-3 h-3" />
                  Hide Other Pairs
                </label>
                <button className="text-xs text-danger hover:text-danger/80">
                  Cancel All
                </button>
              </div>
              <div className="text-center text-text-secondary text-xs py-8">
                No open orders
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}