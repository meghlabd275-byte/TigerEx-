'use client';

import React, { useState } from 'react';
import { Search, Filter, Star, TrendingUp, TrendingDown } from 'lucide-react';

interface MarketItem {
  id: string;
  pair: string;
  price: string;
  change: string;
  changePercent: string;
  volume: string;
  leverage?: string;
  isPositive: boolean;
  isFavorite: boolean;
}

const mockMarkets: MarketItem[] = [
  {
    id: '1',
    pair: 'BTC/USDT',
    price: '43,250.00',
    change: '+1,250.00',
    changePercent: '+2.98%',
    volume: '1.2B',
    isPositive: true,
    isFavorite: false,
  },
  {
    id: '2',
    pair: 'ETH/USDT',
    price: '2,650.00',
    change: '+85.50',
    changePercent: '+3.33%',
    volume: '850M',
    leverage: '10x',
    isPositive: true,
    isFavorite: true,
  },
  {
    id: '3',
    pair: 'BNB/USDT',
    price: '315.20',
    change: '-5.80',
    changePercent: '-1.81%',
    volume: '420M',
    leverage: '5x',
    isPositive: false,
    isFavorite: false,
  },
  {
    id: '4',
    pair: 'SOL/USDT',
    price: '98.45',
    change: '+4.20',
    changePercent: '+4.46%',
    volume: '380M',
    leverage: 'Perp',
    isPositive: true,
    isFavorite: false,
  },
];

export default function MarketsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('Market');
  const [activeFilter, setActiveFilter] = useState('All');

  const categories = ['Favorites', 'Market', 'Alpha', 'Grow', 'Square', 'Data'];
  const filters = ['All', 'Holdings', 'Spot', 'Alpha', 'Futures', 'Options'];

  const filteredMarkets = mockMarkets.filter(market =>
    market.pair.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 lg:bg-bg-primary pb-20 lg:pb-0">
      {/* Mobile Header */}
      <div className="lg:hidden bg-white px-4 py-4 border-b border-gray-200">
        <div className="flex items-center gap-3 mb-4">
          <div className="relative flex-1">
            <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search Coin Pairs"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-gray-100 rounded-lg focus:outline-none focus:bg-white focus:ring-2 focus:ring-primary"
            />
          </div>
          <button className="p-3 bg-gray-100 rounded-lg">
            <Filter size={20} className="text-gray-600" />
          </button>
        </div>

        {/* Category Tabs */}
        <div className="flex gap-2 mb-4 overflow-x-auto scrollbar-hide">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setActiveCategory(category)}
              className={`whitespace-nowrap px-4 py-2 rounded-lg text-sm font-medium ${
                activeCategory === category
                  ? 'bg-primary text-black'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              {category}
            </button>
          ))}
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 overflow-x-auto scrollbar-hide">
          {filters.map((filter) => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              className={`whitespace-nowrap px-3 py-2 text-sm ${
                activeFilter === filter
                  ? 'text-primary border-b-2 border-primary'
                  : 'text-gray-600'
              }`}
            >
              {filter}
            </button>
          ))}
          <button className="whitespace-nowrap px-3 py-2 text-sm text-gray-600">
            Edit
          </button>
        </div>
      </div>

      {/* Desktop Header */}
      <div className="hidden lg:block bg-bg-secondary border-b border-border-primary px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-text-primary">Markets</h1>
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-secondary" />
              <input
                type="text"
                placeholder="Search markets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 bg-bg-tertiary border border-border-secondary rounded-lg focus:outline-none focus:border-primary text-sm w-80"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Market List */}
      <div className="lg:p-6">
        <div className="bg-white lg:bg-bg-secondary lg:rounded-lg lg:border lg:border-border-primary">
          {/* Desktop Header */}
          <div className="hidden lg:block px-6 py-4 border-b border-border-primary">
            <div className="flex gap-4">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setActiveCategory(category)}
                  className={`px-4 py-2 text-sm font-medium ${
                    activeCategory === category
                      ? 'text-primary border-b-2 border-primary'
                      : 'text-text-secondary hover:text-text-primary'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>

          {/* List Header */}
          <div className="px-4 lg:px-6 py-3 flex items-center justify-between text-sm text-gray-500 lg:text-text-secondary border-b border-gray-100 lg:border-border-primary">
            <span>Pair</span>
            <span>Last Price</span>
            <span>24h Change</span>
          </div>

          {/* Market Items */}
          <div className="divide-y divide-gray-100 lg:divide-border-primary">
            {filteredMarkets.map((market) => (
              <div
                key={market.id}
                className="px-4 lg:px-6 py-4 flex items-center justify-between hover:bg-gray-50 lg:hover:bg-bg-tertiary cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-3">
                  <button
                    className={`p-1 ${
                      market.isFavorite ? 'text-primary' : 'text-gray-400 lg:text-text-secondary'
                    }`}
                  >
                    <Star size={16} fill={market.isFavorite ? 'currentColor' : 'none'} />
                  </button>
                  <div>
                    <div className="font-medium text-gray-900 lg:text-text-primary flex items-center gap-2">
                      {market.pair}
                      {market.leverage && (
                        <span className="text-xs bg-gray-100 lg:bg-bg-tertiary text-gray-600 lg:text-text-secondary px-2 py-1 rounded">
                          {market.leverage}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-500 lg:text-text-secondary">
                      Vol: {market.volume}
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="font-medium text-gray-900 lg:text-text-primary">
                    ${market.price}
                  </div>
                </div>

                <div className="text-right">
                  <div className={`font-medium flex items-center gap-1 ${
                    market.isPositive ? 'text-success' : 'text-danger'
                  }`}>
                    {market.isPositive ? (
                      <TrendingUp size={14} />
                    ) : (
                      <TrendingDown size={14} />
                    )}
                    {market.changePercent}
                  </div>
                  <div className={`text-sm ${
                    market.isPositive ? 'text-success' : 'text-danger'
                  }`}>
                    {market.change}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}