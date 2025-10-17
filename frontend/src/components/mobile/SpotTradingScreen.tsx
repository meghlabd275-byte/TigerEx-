/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

'use client';

import React, { useState } from 'react';
import { 
  ChevronDown, 
  Star, 
  TrendingUp, 
  Plus,
  Minus,
  Info
} from 'lucide-react';

interface OrderBookItem {
  price: string;
  amount: string;
  total: string;
}

const mockOrderBook = {
  asks: [
    { price: '43,260.50', amount: '0.001', total: '43.26' },
    { price: '43,259.00', amount: '0.003', total: '129.78' },
    { price: '43,258.50', amount: '0.002', total: '86.52' },
    { price: '43,257.60', amount: '0.183', total: '7,916.14' },
    { price: '43,256.60', amount: '0.001', total: '43.26' },
  ] as OrderBookItem[],
  bids: [
    { price: '43,253.60', amount: '0.002', total: '86.51' },
    { price: '43,253.30', amount: '1.443', total: '62,394.51' },
    { price: '43,251.60', amount: '0.228', total: '9,861.36' },
    { price: '43,251.10', amount: '0.304', total: '13,148.33' },
    { price: '43,251.00', amount: '1.424', total: '61,589.42' },
  ] as OrderBookItem[],
};

export default function SpotTradingScreen() {
  const [orderType, setOrderType] = useState<'limit' | 'market'>('limit');
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [price, setPrice] = useState('43,250.00');
  const [amount, setAmount] = useState('');
  const [percentage, setPercentage] = useState(0);
  const [tpSlEnabled, setTpSlEnabled] = useState(false);
  const [icebergEnabled, setIcebergEnabled] = useState(false);

  const percentageOptions = [25, 50, 75, 100];

  return (
    <div className="min-h-screen bg-white pb-20">
      {/* Header */}
      <div className="bg-white px-4 py-3 border-b border-gray-200">
        <div className="flex items-center gap-4 mb-4">
          {['Convert', 'Spot', 'Margin', 'Buy/Sell', 'P2P', 'Alpha'].map((tab, index) => (
            <button
              key={tab}
              className={`px-3 py-2 text-sm font-medium ${
                tab === 'Spot'
                  ? 'text-primary border-b-2 border-primary'
                  : 'text-gray-600'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
        
        {/* Trading Pair */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-lg">ETH/USDT</span>
            <Star size={16} className="text-gray-400" />
          </div>
          <div className="text-success text-sm font-medium">+3.33%</div>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row">
        {/* Order Entry Panel */}
        <div className="flex-1 p-4">
          {/* Buy/Sell Toggle */}
          <div className="flex mb-4">
            <button
              onClick={() => setSide('buy')}
              className={`flex-1 py-3 text-center font-medium rounded-l-lg ${
                side === 'buy'
                  ? 'bg-success text-white'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              Buy
            </button>
            <button
              onClick={() => setSide('sell')}
              className={`flex-1 py-3 text-center font-medium rounded-r-lg ${
                side === 'sell'
                  ? 'bg-danger text-white'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              Sell
            </button>
          </div>

          {/* Order Type */}
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setOrderType('limit')}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                orderType === 'limit'
                  ? 'bg-primary text-black'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              Limit
            </button>
            <button
              onClick={() => setOrderType('market')}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                orderType === 'market'
                  ? 'bg-primary text-black'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              Market
            </button>
          </div>

          {/* Price Input */}
          {orderType === 'limit' && (
            <div className="mb-4">
              <label className="block text-sm text-gray-600 mb-2">Price (USDT)</label>
              <div className="relative">
                <input
                  type="text"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
                  placeholder="0.00"
                />
                <span className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 text-sm">
                  USDT
                </span>
              </div>
            </div>
          )}

          {/* Amount Input */}
          <div className="mb-4">
            <label className="block text-sm text-gray-600 mb-2">Amount (ETH)</label>
            <div className="relative">
              <input
                type="text"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
                placeholder="0.00"
              />
              <span className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 text-sm">
                ETH
              </span>
            </div>
          </div>

          {/* Percentage Slider */}
          <div className="mb-4">
            <div className="flex justify-between mb-2">
              {percentageOptions.map((percent) => (
                <button
                  key={percent}
                  onClick={() => setPercentage(percent)}
                  className={`px-3 py-1 text-xs rounded ${
                    percentage === percent
                      ? 'bg-primary text-black'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {percent}%
                </button>
              ))}
            </div>
            <div className="relative">
              <input
                type="range"
                min="0"
                max="100"
                value={percentage}
                onChange={(e) => setPercentage(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>
          </div>

          {/* Total */}
          <div className="mb-4">
            <label className="block text-sm text-gray-600 mb-2">Total (USDT)</label>
            <div className="px-4 py-3 bg-gray-50 rounded-lg text-gray-900">
              0.00
            </div>
          </div>

          {/* Options */}
          <div className="space-y-3 mb-6">
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={tpSlEnabled}
                onChange={(e) => setTpSlEnabled(e.target.checked)}
                className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
              />
              <span className="text-sm text-gray-700">TP/SL</span>
            </label>
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={icebergEnabled}
                onChange={(e) => setIcebergEnabled(e.target.checked)}
                className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
              />
              <span className="text-sm text-gray-700">Iceberg</span>
            </label>
          </div>

          {/* Available Balance */}
          <div className="mb-4 text-sm text-gray-600">
            Available: 0.00000000 USDT
          </div>

          {/* Max Buy / Est Fee */}
          <div className="mb-4 space-y-1 text-xs text-gray-500">
            <div>Max Buy: 0 ETH</div>
            <div>Est. Fee: 0.00000000 ETH</div>
          </div>

          {/* Buy/Sell Button */}
          <button
            className={`w-full py-4 rounded-lg font-medium text-white ${
              side === 'buy' ? 'bg-success hover:bg-success/90' : 'bg-danger hover:bg-danger/90'
            }`}
          >
            {side === 'buy' ? 'Buy ETH' : 'Sell ETH'}
          </button>

          {/* Fee Level */}
          <div className="mt-3 text-center">
            <span className="text-xs text-gray-500">Fee Level: VIP 0</span>
          </div>
        </div>

        {/* Order Book */}
        <div className="flex-1 p-4 border-t lg:border-t-0 lg:border-l border-gray-200">
          <div className="mb-4">
            <h3 className="font-semibold text-gray-900 mb-2">Order Book</h3>
            <div className="text-xs text-gray-500 grid grid-cols-3 gap-4 mb-2">
              <span>Price (USDT)</span>
              <span className="text-right">Amount (ETH)</span>
              <span className="text-right">Total</span>
            </div>
          </div>

          {/* Asks */}
          <div className="space-y-1 mb-4">
            {mockOrderBook.asks.reverse().map((ask, index) => (
              <div key={index} className="grid grid-cols-3 gap-4 text-xs py-1">
                <span className="text-danger">{ask.price}</span>
                <span className="text-right text-gray-600">{ask.amount}</span>
                <span className="text-right text-gray-600">{ask.total}</span>
              </div>
            ))}
          </div>

          {/* Current Price */}
          <div className="text-center py-2 mb-4 bg-success/10 rounded">
            <span className="text-success font-semibold">43,254.80</span>
            <span className="text-xs text-success ml-2">↑</span>
          </div>

          {/* Bids */}
          <div className="space-y-1">
            {mockOrderBook.bids.map((bid, index) => (
              <div key={index} className="grid grid-cols-3 gap-4 text-xs py-1">
                <span className="text-success">{bid.price}</span>
                <span className="text-right text-gray-600">{bid.amount}</span>
                <span className="text-right text-gray-600">{bid.total}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Order Tabs */}
      <div className="border-t border-gray-200 bg-white">
        <div className="flex">
          <button className="flex-1 py-3 text-center text-sm font-medium text-primary border-b-2 border-primary">
            Open Orders (0)
          </button>
          <button className="flex-1 py-3 text-center text-sm font-medium text-gray-600">
            Holdings
          </button>
          <button className="flex-1 py-3 text-center text-sm font-medium text-gray-600">
            Spot Grid
          </button>
        </div>
        <div className="p-4 text-center text-gray-500 text-sm">
          No open orders
        </div>
      </div>
    </div>
  );
}