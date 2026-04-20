/**
 * TigerEx Frontend
 * @file index.tsx
 * @description TigerEx React component
 * @author TigerEx Development Team
 */

import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Search, Activity, Settings, Maximize, RefreshCw } from 'lucide-react';

export default function TradingViewPage() {
  const [selectedToken, setSelectedToken] = useState('TIGER');
  const [timeframe, setTimeframe] = useState('1H');

  const tokens = [
    { symbol: 'TIGER', name: 'TigerCoin', price: 0.05, change: 5.2 },
    { symbol: 'ETH', name: 'Ethereum', price: 3542.18, change: 2.48 },
    { symbol: 'BTC', name: 'Bitcoin', price: 67850.25, change: 1.87 },
    { symbol: 'SOL', name: 'Solana', price: 185.92, change: -0.85 },
    { symbol: 'ARB', name: 'Arbitrum', price: 1.85, change: 3.2 },
    { symbol: 'BASE', name: 'Base', price: 2.45, change: 1.8 }
  ];

  const timeframes = ['1m', '5m', '15m', '1H', '4H', '1D', '1W'];
  const indicators = ['SMA', 'EMA', 'RSI', 'MACD', 'Bollinger', 'ATR', 'ADX', 'Stochastic'];

  return (
    <div className="min-h-screen bg-gray-900 text-white flex">
      {/* Token List Sidebar */}
      <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search..."
              className="w-full bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-sm"
            />
          </div>
        </div>
        <div className="flex-1 overflow-y-auto">
          {tokens.map((token) => (
            <div
              key={token.symbol}
              onClick={() => setSelectedToken(token.symbol)}
              className={`p-4 border-b border-gray-700 cursor-pointer hover:bg-gray-700/50 ${
                selectedToken === token.symbol ? 'bg-gray-700' : ''
              }`}
            >
              <h3 className="font-semibold">{token.symbol}/USDT</h3>
              <p className="text-gray-400 text-sm">{token.name}</p>
              <div className="flex justify-between mt-2">
                <span className="font-mono">${token.price}</span>
                <span className={token.change >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {token.change >= 0 ? '+' : ''}{token.change}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chart Area */}
      <div className="flex-1 flex flex-col">
        <div className="bg-gray-800 border-b border-gray-700 p-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">{selectedToken}/USDT</h2>
            <p className="text-gray-400">
              ${tokens.find(t => t.symbol === selectedToken)?.price}
              <span className={tokens.find(t => t.symbol === selectedToken)?.change! >= 0 ? 'text-green-400' : 'text-red-400'}>
                {' '}({tokens.find(t => t.symbol === selectedToken)?.change >= 0 ? '+' : ''}
                {tokens.find(t => t.symbol === selectedToken)?.change}%)
              </span>
            </p>
          </div>
          <div className="flex gap-2">
            {timeframes.map(tf => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1 rounded text-sm ${
                  timeframe === tf ? 'bg-yellow-500 text-black' : 'bg-gray-700 text-gray-300'
                }`}
              >
                {tf}
              </button>
            ))}
            <button className="p-2 bg-gray-700 rounded">
              <Maximize className="w-4 h-4" />
            </button>
            <button className="p-2 bg-gray-700 rounded">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="flex-1 p-4">
          <div className="flex items-end justify-between h-full gap-1">
            {Array.from({ length: 50 }).map((_, i) => {
              const isGreen = Math.random() > 0.5;
              const height = 20 + Math.random() * 80;
              return (
                <div key={i} className="flex-1 flex flex-col items-center">
                  <div className={`w-full ${isGreen ? 'bg-green-500' : 'bg-red-500'}`} style={{ height: `${height}px` }} />
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-gray-800 border-t border-gray-700 p-4">
          <div className="flex items-center gap-4">
            <span className="text-gray-400 text-sm flex items-center gap-2">
              <Activity className="w-4 h-4" /> Indicators:
            </span>
            <div className="flex gap-2">
              {indicators.map(ind => (
                <button
                  key={ind}
                  className="px-3 py-1 rounded text-sm bg-gray-700 text-gray-300 hover:bg-gray-600"
                >
                  {ind}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel */}
      <div className="w-72 bg-gray-800 border-l border-gray-700 p-4">
        <h3 className="font-bold mb-4">Token Info</h3>
        <div className="space-y-4">
          <div className="bg-gray-700/50 p-3 rounded">
            <p className="text-gray-400 text-sm">Market Cap</p>
            <p className="font-semibold">$50M</p>
          </div>
          <div className="bg-gray-700/50 p-3 rounded">
            <p className="text-gray-400 text-sm">24h Volume</p>
            <p className="font-semibold">$2.5M</p>
          </div>
          <div className="bg-gray-700/50 p-3 rounded">
            <p className="text-gray-400 text-sm">Blockchain</p>
            <p className="font-semibold">Ethereum</p>
          </div>
          <button className="w-full bg-yellow-500 hover:bg-yellow-400 text-black py-3 rounded-lg font-semibold mt-4">
            Trade {selectedToken}
          </button>
        </div>

        <div className="mt-6">
          <h4 className="font-semibold mb-3">Chart Indicators</h4>
          <div className="space-y-2">
            {indicators.map(ind => (
              <div key={ind} className="p-2 rounded bg-gray-700/50 text-gray-300 cursor-pointer">
                {ind}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}