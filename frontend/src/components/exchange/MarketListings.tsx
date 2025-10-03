import React, { useState } from 'react';
import { Search, TrendingUp, TrendingDown, Star } from 'lucide-react';

interface Token {
  symbol: string;
  name: string;
  price: number;
  change24h: number;
  volume24h: number;
  icon: string;
}

const MarketListings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('hot');
  const [marketType, setMarketType] = useState<'crypto' | 'futures'>('crypto');
  const [searchQuery, setSearchQuery] = useState('');

  const tokens: Token[] = [
    { symbol: 'BNB', name: 'BNB', price: 1130.83, change24h: 6.97, volume24h: 137655.94, icon: '🔶' },
    { symbol: 'BTC', name: 'Bitcoin', price: 120486.52, change24h: 0.76, volume24h: 14666824.08, icon: '₿' },
    { symbol: 'ETH', name: 'Ethereum', price: 4483.35, change24h: 1.84, volume24h: 545758.20, icon: '◆' },
    { symbol: 'SOL', name: 'Solana', price: 230.28, change24h: 1.94, volume24h: 28031.98, icon: '◎' },
    { symbol: 'XRP', name: 'Ripple', price: 3.0296, change24h: 1.68, volume24h: 368.79, icon: '✕' },
  ];

  const tabs = [
    { id: 'favorites', label: 'Favorites', icon: <Star className="w-4 h-4" /> },
    { id: 'hot', label: 'Hot' },
    { id: 'alpha', label: 'Alpha' },
    { id: 'new', label: 'New' },
    { id: 'gainers', label: 'Gainers' },
    { id: 'losers', label: 'Losers' },
    { id: '24h-vol', label: '24h Vol' },
    { id: 'market', label: 'Market' },
  ];

  return (
    <div className="bg-white dark:bg-gray-900">
      {/* Search Bar */}
      <div className="px-4 py-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="🔥 MORPHO"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-yellow-400"
          />
        </div>
      </div>

      {/* Total Value Display */}
      <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Est. Total Value(USDT)</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mt-1">******</div>
          </div>
          <button className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold px-6 py-2 rounded-lg">
            Add Funds
          </button>
        </div>
      </div>

      {/* Trading Countdown Banner */}
      <div className="mx-4 my-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
            <span className="text-2xl">🔥</span>
          </div>
          <div>
            <div className="text-white font-semibold">MORPHO</div>
            <div className="text-white text-sm opacity-90">Starts in 1H : 9M</div>
          </div>
        </div>
        <button className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold px-6 py-2 rounded-lg">
          Trade
        </button>
      </div>

      {/* Tabs Navigation */}
      <div className="px-4 overflow-x-auto">
        <div className="flex gap-4 border-b border-gray-200 dark:border-gray-800">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1 px-3 py-3 whitespace-nowrap ${
                activeTab === tab.id
                  ? 'text-gray-900 dark:text-white border-b-2 border-yellow-400 font-semibold'
                  : 'text-gray-500 dark:text-gray-400'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Market Type Toggle */}
      <div className="px-4 py-3 flex gap-4">
        <button
          onClick={() => setMarketType('crypto')}
          className={`px-4 py-1 rounded-full ${
            marketType === 'crypto'
              ? 'bg-yellow-400 text-black font-semibold'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
          }`}
        >
          Crypto
        </button>
        <button
          onClick={() => setMarketType('futures')}
          className={`px-4 py-1 rounded-full ${
            marketType === 'futures'
              ? 'bg-yellow-400 text-black font-semibold'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
          }`}
        >
          Futures
        </button>
      </div>

      {/* Token List Header */}
      <div className="px-4 py-2 flex justify-between text-sm text-gray-500 dark:text-gray-400">
        <div className="flex-1">Name</div>
        <div className="w-32 text-right">Last Price</div>
        <div className="w-24 text-right">24h chg%</div>
      </div>

      {/* Token List */}
      <div className="divide-y divide-gray-100 dark:divide-gray-800">
        {tokens.map((token) => (
          <div key={token.symbol} className="px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer">
            <div className="flex items-center gap-3 flex-1">
              <div className="w-8 h-8 rounded-full bg-yellow-400 flex items-center justify-center text-xl">
                {token.icon}
              </div>
              <div>
                <div className="font-semibold text-gray-900 dark:text-white">{token.symbol}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">{token.name}</div>
              </div>
            </div>
            <div className="w-32 text-right">
              <div className="font-semibold text-gray-900 dark:text-white">
                {token.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                ₿{token.volume24h.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </div>
            </div>
            <div className="w-24 text-right">
              <div
                className={`inline-flex items-center gap-1 px-2 py-1 rounded ${
                  token.change24h > 0
                    ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
                    : 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                }`}
              >
                {token.change24h > 0 ? (
                  <TrendingUp className="w-3 h-3" />
                ) : (
                  <TrendingDown className="w-3 h-3" />
                )}
                {token.change24h > 0 ? '+' : ''}
                {token.change24h.toFixed(2)}%
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* View More Button */}
      <div className="px-4 py-4 text-center">
        <button className="text-yellow-400 hover:text-yellow-500 font-semibold">
          View More
        </button>
      </div>
    </div>
  );
};

export default MarketListings;