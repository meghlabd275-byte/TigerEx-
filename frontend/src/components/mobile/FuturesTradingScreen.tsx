'use client';

import React, { useState } from 'react';
import { 
  ChevronDown, 
  TrendingUp, 
  Settings,
  BarChart3,
  Clock
} from 'lucide-react';

interface OrderBookItem {
  price: string;
  amount: string;
  percentage: string;
}

const mockOrderBook = {
  asks: [
    { price: '123,660.50', amount: '0.001', percentage: '3%' },
    { price: '123,660.00', amount: '0.003', percentage: '97%' },
    { price: '123,659.50', amount: '0.002', percentage: '3%' },
    { price: '123,658.50', amount: '0.002', percentage: '3%' },
    { price: '123,657.60', amount: '0.183', percentage: '3%' },
  ] as OrderBookItem[],
  bids: [
    { price: '123,653.60', amount: '0.002', percentage: '97%' },
    { price: '123,653.30', amount: '1.443', percentage: '3%' },
    { price: '123,651.60', amount: '0.228', percentage: '3%' },
    { price: '123,651.10', amount: '0.304', percentage: '3%' },
    { price: '123,651.00', amount: '1.424', percentage: '3%' },
  ] as OrderBookItem[],
};

export default function FuturesTradingScreen() {
  const [orderType, setOrderType] = useState<'limit' | 'market'>('limit');
  const [marginMode, setMarginMode] = useState<'cross' | 'isolated'>('cross');
  const [leverage, setLeverage] = useState('10x');
  const [price, setPrice] = useState('123,650.00');
  const [quantity, setQuantity] = useState('');
  const [percentage, setPercentage] = useState(0);
  const [tpSlEnabled, setTpSlEnabled] = useState(false);
  const [postOnlyEnabled, setPostOnlyEnabled] = useState(false);
  const [reduceOnlyEnabled, setReduceOnlyEnabled] = useState(false);
  const [timeInForce, setTimeInForce] = useState('GTC');

  const leverageOptions = ['5x', '10x', '20x', '50x', '100x'];
  const percentageOptions = [25, 50, 75, 100];

  return (
    <div className="min-h-screen bg-dark-primary text-text-primary pb-20">
      {/* Header */}
      <div className="bg-dark-secondary px-4 py-3 border-b border-border-primary">
        <div className="flex items-center gap-4 mb-4">
          {['Convert', 'Spot', 'Futures', 'Options', 'TradFi'].map((tab) => (
            <button
              key={tab}
              className={`px-3 py-2 text-sm font-medium ${
                tab === 'Futures'
                  ? 'text-primary border-b-2 border-primary'
                  : 'text-text-secondary'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
        
        {/* Trading Pair */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-lg">BTCUSDT</span>
              <ChevronDown size={16} className="text-text-secondary" />
            </div>
            <div className="text-success text-sm font-medium">+3.22%</div>
          </div>
          <div className="flex items-center gap-2">
            <div className="bg-success/20 text-success px-2 py-1 rounded text-xs">
              MM 0.00%
            </div>
            <Settings size={16} className="text-text-secondary" />
            <BarChart3 size={16} className="text-text-secondary" />
          </div>
        </div>

        {/* Funding Rate */}
        <div className="flex items-center justify-between mt-2 text-xs text-text-secondary">
          <span>Funding Rate / Countdown</span>
          <div className="flex items-center gap-2">
            <span>0.0100%</span>
            <Clock size={12} />
            <span>07:21:24</span>
          </div>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row">
        {/* Order Entry Panel */}
        <div className="flex-1 p-4 bg-dark-secondary">
          {/* Margin Mode & Leverage */}
          <div className="flex gap-2 mb-4">
            <div className="flex-1">
              <button className="w-full flex items-center justify-between px-3 py-2 bg-dark-tertiary rounded-lg text-sm">
                <span>{marginMode === 'cross' ? 'Cross' : 'Isolated'}</span>
                <ChevronDown size={16} />
              </button>
            </div>
            <div className="flex-1">
              <button className="w-full flex items-center justify-between px-3 py-2 bg-dark-tertiary rounded-lg text-sm">
                <span>{leverage}</span>
                <ChevronDown size={16} />
              </button>
            </div>
          </div>

          {/* Available Balance */}
          <div className="mb-4">
            <div className="text-sm text-text-secondary mb-1">Available</div>
            <div className="text-lg font-semibold">0.0000 USDT</div>
          </div>

          {/* Order Type */}
          <div className="mb-4">
            <button className="w-full flex items-center justify-between px-3 py-2 bg-dark-tertiary rounded-lg text-sm">
              <span>{orderType === 'limit' ? 'Limit' : 'Market'}</span>
              <ChevronDown size={16} />
            </button>
          </div>

          {/* Price & Quantity */}
          <div className="space-y-4 mb-4">
            {orderType === 'limit' && (
              <div>
                <label className="block text-sm text-text-secondary mb-2">Price</label>
                <div className="relative">
                  <input
                    type="text"
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    className="w-full px-4 py-3 bg-dark-tertiary border border-border-secondary rounded-lg focus:outline-none focus:border-primary text-text-primary"
                    placeholder="0.00"
                  />
                  <span className="absolute right-4 top-1/2 transform -translate-y-1/2 text-text-secondary text-sm">
                    USDT
                  </span>
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm text-text-secondary mb-2">Quantity</label>
              <div className="relative">
                <input
                  type="text"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  className="w-full px-4 py-3 bg-dark-tertiary border border-border-secondary rounded-lg focus:outline-none focus:border-primary text-text-primary"
                  placeholder="0.00"
                />
                <span className="absolute right-4 top-1/2 transform -translate-y-1/2 text-text-secondary text-sm">
                  BTC
                </span>
              </div>
            </div>
          </div>

          {/* Percentage Slider */}
          <div className="mb-4">
            <div className="relative mb-2">
              <input
                type="range"
                min="0"
                max="100"
                value={percentage}
                onChange={(e) => setPercentage(Number(e.target.value))}
                className="w-full h-2 bg-dark-tertiary rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-text-secondary mt-1">
                <span>0</span>
                <span>25</span>
                <span>50</span>
                <span>75</span>
                <span>100</span>
              </div>
            </div>
          </div>

          {/* Value, Cost, Liq. Price */}
          <div className="space-y-2 mb-4 text-sm">
            <div className="flex justify-between">
              <span className="text-text-secondary">Value</span>
              <span>0/0 USDT</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Cost</span>
              <span>0/0 USDT</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Liq. Price</span>
              <span>--</span>
            </div>
          </div>

          {/* Options */}
          <div className="space-y-3 mb-6">
            <label className="flex items-center justify-between">
              <span className="text-sm text-text-primary">TP/SL</span>
              <input
                type="checkbox"
                checked={tpSlEnabled}
                onChange={(e) => setTpSlEnabled(e.target.checked)}
                className="w-4 h-4 text-primary bg-dark-tertiary border-border-secondary rounded focus:ring-primary"
              />
            </label>
            <label className="flex items-center justify-between">
              <span className="text-sm text-text-primary">Post-Only</span>
              <input
                type="checkbox"
                checked={postOnlyEnabled}
                onChange={(e) => setPostOnlyEnabled(e.target.checked)}
                className="w-4 h-4 text-primary bg-dark-tertiary border-border-secondary rounded focus:ring-primary"
              />
            </label>
            <label className="flex items-center justify-between">
              <span className="text-sm text-text-primary">Reduce-Only</span>
              <input
                type="checkbox"
                checked={reduceOnlyEnabled}
                onChange={(e) => setReduceOnlyEnabled(e.target.checked)}
                className="w-4 h-4 text-primary bg-dark-tertiary border-border-secondary rounded focus:ring-primary"
              />
            </label>
            <div className="flex items-center justify-between">
              <span className="text-sm text-text-primary">Time in Force</span>
              <button className="flex items-center gap-1 text-sm text-text-secondary">
                <span>{timeInForce}</span>
                <ChevronDown size={14} />
              </button>
            </div>
          </div>

          {/* Long/Short Buttons */}
          <div className="flex gap-2 mb-4">
            <button className="flex-1 py-4 bg-success hover:bg-success/90 text-white rounded-lg font-medium">
              Long
            </button>
            <button className="flex-1 py-4 bg-danger hover:bg-danger/90 text-white rounded-lg font-medium">
              Short
            </button>
          </div>
        </div>

        {/* Order Book */}
        <div className="flex-1 p-4 bg-dark-primary border-t lg:border-t-0 lg:border-l border-border-primary">
          <div className="mb-4">
            <div className="text-xs text-text-secondary grid grid-cols-3 gap-4 mb-2">
              <span>Price (USDT)</span>
              <span className="text-right">Quantity (BTC)</span>
              <span className="text-right">%</span>
            </div>
          </div>

          {/* Asks */}
          <div className="space-y-1 mb-4">
            {mockOrderBook.asks.reverse().map((ask, index) => (
              <div key={index} className="grid grid-cols-3 gap-4 text-xs py-1 relative">
                <div 
                  className="absolute left-0 top-0 bottom-0 bg-danger/10 rounded"
                  style={{ width: `${Math.random() * 60 + 20}%` }}
                />
                <span className="text-danger relative z-10">{ask.price}</span>
                <span className="text-right text-text-secondary relative z-10">{ask.amount}</span>
                <span className="text-right text-text-secondary relative z-10">{ask.percentage}</span>
              </div>
            ))}
          </div>

          {/* Current Price */}
          <div className="text-center py-2 mb-4 bg-success/10 rounded">
            <span className="text-success font-semibold text-lg">123,650.00</span>
            <div className="text-xs text-text-secondary">123,657.23</div>
          </div>

          {/* Bids */}
          <div className="space-y-1">
            {mockOrderBook.bids.map((bid, index) => (
              <div key={index} className="grid grid-cols-3 gap-4 text-xs py-1 relative">
                <div 
                  className="absolute left-0 top-0 bottom-0 bg-success/10 rounded"
                  style={{ width: `${Math.random() * 60 + 20}%` }}
                />
                <span className="text-success relative z-10">{bid.price}</span>
                <span className="text-right text-text-secondary relative z-10">{bid.amount}</span>
                <span className="text-right text-text-secondary relative z-10">{bid.percentage}</span>
              </div>
            ))}
          </div>

          {/* Order Book Footer */}
          <div className="flex items-center justify-between mt-4 text-xs">
            <button className="flex items-center gap-1 text-text-secondary">
              <span>0.1</span>
              <ChevronDown size={12} />
            </button>
            <div className="flex gap-2">
              <div className="w-4 h-4 bg-success/20 rounded"></div>
              <div className="w-4 h-4 bg-danger/20 rounded"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Tabs */}
      <div className="border-t border-border-primary bg-dark-secondary">
        <div className="flex">
          {['Orders(0)', 'Positions(0)', 'Assets', 'Borrowings(0)', 'Tools(0)'].map((tab, index) => (
            <button 
              key={tab}
              className={`flex-1 py-3 text-center text-xs font-medium ${
                index === 0 ? 'text-primary border-b-2 border-primary' : 'text-text-secondary'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
        
        {/* All Markets Filter */}
        <div className="p-4 border-t border-border-primary">
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2">
              <input type="checkbox" className="w-4 h-4 text-primary bg-dark-tertiary border-border-secondary rounded" />
              <span className="text-sm text-text-primary">All Markets</span>
            </label>
            <button className="flex items-center gap-1 text-sm text-text-secondary">
              <span>All Types</span>
              <ChevronDown size={14} />
            </button>
            <button className="ml-auto">
              <BarChart3 size={16} className="text-text-secondary" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}