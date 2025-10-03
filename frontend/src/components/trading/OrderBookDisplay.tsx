import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';

interface OrderBookEntry {
  price: number;
  amount: number;
  total: number;
}

const OrderBookDisplay: React.FC = () => {
  const [viewMode, setViewMode] = useState<'all' | 'bids' | 'asks'>('all');
  const [precision, setPrecision] = useState('0.1');

  // Sample order book data
  const asks: OrderBookEntry[] = [
    { price: 120444.2, amount: 0.0249, total: 0 },
    { price: 120443.9, amount: 0.0431, total: 0 },
    { price: 120443.3, amount: 0.0249, total: 0 },
    { price: 120443.2, amount: 0.0249, total: 0 },
    { price: 120443.1, amount: 0.4990, total: 0 },
    { price: 120443.0, amount: 0.4990, total: 0 },
    { price: 120442.9, amount: 2.5933, total: 0 },
  ];

  const bids: OrderBookEntry[] = [
    { price: 120442.8, amount: 0.9360, total: 0 },
    { price: 120442.7, amount: 0.0100, total: 0 },
    { price: 120442.5, amount: 0.4500, total: 0 },
    { price: 120442.0, amount: 0.0431, total: 0 },
    { price: 120441.6, amount: 0.0031, total: 0 },
    { price: 120440.9, amount: 0.1195, total: 0 },
    { price: 120440.4, amount: 0.0105, total: 0 },
  ];

  const currentPrice = 120442.8;
  const priceChange = 120442.8;
  const priceChangePercent = 0.57;

  const getDepthPercentage = (amount: number, maxAmount: number = 3) => {
    return (amount / maxAmount) * 100;
  };

  return (
    <div className="bg-gray-900 text-white h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-800">
        <h3 className="font-semibold">Order Book</h3>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPrecision('0.1')}
            className="text-xs text-gray-400 hover:text-white px-2 py-1 rounded bg-gray-800"
          >
            {precision}
          </button>
          <div className="flex gap-1">
            <button
              onClick={() => setViewMode('all')}
              className={`p-1 rounded ${viewMode === 'all' ? 'bg-gray-700' : 'hover:bg-gray-800'}`}
            >
              <div className="flex flex-col gap-0.5">
                <div className="w-3 h-0.5 bg-red-500"></div>
                <div className="w-3 h-0.5 bg-green-500"></div>
              </div>
            </button>
            <button
              onClick={() => setViewMode('asks')}
              className={`p-1 rounded ${viewMode === 'asks' ? 'bg-gray-700' : 'hover:bg-gray-800'}`}
            >
              <div className="flex flex-col gap-0.5">
                <div className="w-3 h-0.5 bg-red-500"></div>
                <div className="w-3 h-0.5 bg-red-500"></div>
              </div>
            </button>
            <button
              onClick={() => setViewMode('bids')}
              className={`p-1 rounded ${viewMode === 'bids' ? 'bg-gray-700' : 'hover:bg-gray-800'}`}
            >
              <div className="flex flex-col gap-0.5">
                <div className="w-3 h-0.5 bg-green-500"></div>
                <div className="w-3 h-0.5 bg-green-500"></div>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Column Headers */}
      <div className="flex justify-between px-3 py-2 text-xs text-gray-400 border-b border-gray-800">
        <span>Price (USDT)</span>
        <span>Amount (BTC)</span>
        <span className="text-right">Total</span>
      </div>

      {/* Order Book Content */}
      <div className="flex-1 overflow-y-auto">
        {/* Asks (Sell Orders) */}
        {(viewMode === 'all' || viewMode === 'asks') && (
          <div className="flex flex-col-reverse">
            {asks.map((ask, index) => (
              <div
                key={`ask-${index}`}
                className="relative px-3 py-1 hover:bg-gray-800/50 cursor-pointer"
              >
                <div
                  className="absolute right-0 top-0 h-full bg-red-500/10"
                  style={{ width: `${getDepthPercentage(ask.amount)}%` }}
                ></div>
                <div className="relative flex justify-between text-xs">
                  <span className="text-red-500 font-mono">{ask.price.toFixed(1)}</span>
                  <span className="text-gray-300 font-mono">{ask.amount.toFixed(4)}</span>
                  <span className="text-gray-400 font-mono text-right">{ask.total.toFixed(0)}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Current Price */}
        <div className="px-3 py-3 bg-gray-800/50 border-y border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-green-400 text-lg font-bold font-mono">
                {currentPrice.toFixed(1)}
              </span>
              <span className="text-xs text-gray-400">≈${priceChange.toFixed(2)} USD</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="text-green-400 text-sm">↑</span>
              <span className="text-green-400 text-sm font-semibold">+{priceChangePercent}%</span>
            </div>
          </div>
        </div>

        {/* Bids (Buy Orders) */}
        {(viewMode === 'all' || viewMode === 'bids') && (
          <div>
            {bids.map((bid, index) => (
              <div
                key={`bid-${index}`}
                className="relative px-3 py-1 hover:bg-gray-800/50 cursor-pointer"
              >
                <div
                  className="absolute right-0 top-0 h-full bg-green-500/10"
                  style={{ width: `${getDepthPercentage(bid.amount)}%` }}
                ></div>
                <div className="relative flex justify-between text-xs">
                  <span className="text-green-500 font-mono">{bid.price.toFixed(1)}</span>
                  <span className="text-gray-300 font-mono">{bid.amount.toFixed(4)}</span>
                  <span className="text-gray-400 font-mono text-right">{bid.total.toFixed(0)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Spread Indicator */}
      <div className="px-3 py-2 border-t border-gray-800 flex items-center justify-between text-xs">
        <span className="text-gray-400">Spread</span>
        <div className="flex items-center gap-2">
          <span className="text-white font-mono">1.4</span>
          <div className="flex items-center gap-1 bg-green-500/20 text-green-400 px-2 py-0.5 rounded">
            <span className="font-bold">B</span>
            <span>20%</span>
          </div>
          <div className="flex items-center gap-1 bg-red-500/20 text-red-400 px-2 py-0.5 rounded">
            <span>80%</span>
            <span className="font-bold">S</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderBookDisplay;