'use client';

import React, { useState } from 'react';
import { 
  Search, 
  Filter, 
  Star, 
  TrendingUp, 
  TrendingDown, 
  ArrowUpRight,
  ArrowDownRight,
  ChevronDown,
  Grid,
  List,
  MoreVertical,
  Bell,
  Settings,
  HelpCircle,
  Eye,
  EyeOff,
  RefreshCw,
  CandlestickChart,
  BarChart3,
  Activity,
  DollarSign,
  Globe,
  Zap,
  Package,
  Clock,
  Hash
} from 'lucide-react';

interface MarketItem {
  id: string;
  pair: string;
  name: string;
  price: string;
  change: string;
  changePercent: string;
  volume: string;
  marketCap?: string;
  leverage?: string;
  isPositive: boolean;
  isFavorite: boolean;
  category: string;
  icon?: string;
  sparkline?: number[];
}

interface CategoryFilter {
  id: string;
  name: string;
  count?: number;
  icon?: any;
}

const mockMarkets: MarketItem[] = [
  {
    id: '1',
    pair: 'BTC/USDT',
    name: 'Bitcoin',
    price: '67,850.25',
    change: '+1,250.00',
    changePercent: '+1.87%',
    volume: '1.2B',
    marketCap: '1.32T',
    isPositive: true,
    isFavorite: true,
    category: 'cryptocurrency',
    icon: '₿',
    sparkline: [66500, 66800, 67200, 66900, 67400, 67100, 67850]
  },
  {
    id: '2',
    pair: 'ETH/USDT',
    name: 'Ethereum',
    price: '3,542.18',
    change: '+85.50',
    changePercent: '+2.48%',
    volume: '850M',
    marketCap: '425B',
    isPositive: true,
    isFavorite: false,
    category: 'cryptocurrency',
    icon: 'Ξ',
    sparkline: [3450, 3480, 3520, 3490, 3540, 3510, 3542]
  },
  {
    id: '3',
    pair: 'BNB/USDT',
    name: 'Binance Coin',
    price: '612.45',
    change: '-5.80',
    changePercent: '-0.94%',
    volume: '420M',
    marketCap: '94B',
    isPositive: false,
    isFavorite: false,
    category: 'cryptocurrency',
    icon: 'B',
    leverage: 'Perp',
    sparkline: [618, 616, 614, 617, 613, 615, 612]
  },
  {
    id: '4',
    pair: 'SOL/USDT',
    name: 'Solana',
    price: '145.67',
    change: '+4.20',
    changePercent: '+2.97%',
    volume: '380M',
    marketCap: '65B',
    isPositive: true,
    isFavorite: false,
    category: 'cryptocurrency',
    icon: 'S',
    leverage: '10x',
    sparkline: [141, 143, 145, 142, 144, 146, 145]
  },
  {
    id: '5',
    pair: 'ADA/USDT',
    name: 'Cardano',
    price: '0.385',
    change: '-0.002',
    changePercent: '-0.52%',
    volume: '180M',
    marketCap: '13.5B',
    isPositive: false,
    isFavorite: false,
    category: 'cryptocurrency',
    icon: 'A',
    leverage: '5x',
    sparkline: [0.387, 0.386, 0.385, 0.388, 0.384, 0.386, 0.385]
  },
  {
    id: '6',
    pair: 'XRP/USDT',
    name: 'Ripple',
    price: '0.625',
    change: '+0.015',
    changePercent: '+2.46%',
    volume: '1.2B',
    marketCap: '34B',
    isPositive: true,
    isFavorite: true,
    category: 'cryptocurrency',
    icon: 'X',
    leverage: 'Perp',
    sparkline: [0.61, 0.613, 0.618, 0.615, 0.622, 0.62, 0.625]
  },
  {
    id: '7',
    pair: 'DOGE/USDT',
    name: 'Dogecoin',
    price: '0.0856',
    change: '+0.0035',
    changePercent: '+4.26%',
    volume: '450M',
    marketCap: '12.2B',
    isPositive: true,
    isFavorite: false,
    category: 'cryptocurrency',
    icon: 'D',
    leverage: '3x',
    sparkline: [0.082, 0.083, 0.084, 0.083, 0.085, 0.085, 0.0856]
  },
  {
    id: '8',
    pair: 'AVAX/USDT',
    name: 'Avalanche',
    price: '28.45',
    change: '-0.65',
    changePercent: '-2.23%',
    volume: '280M',
    marketCap: '10.5B',
    isPositive: false,
    isFavorite: false,
    category: 'cryptocurrency',
    icon: 'A',
    leverage: '5x',
    sparkline: [29.1, 28.9, 28.7, 28.8, 28.5, 28.6, 28.45]
  }
];

const categories: CategoryFilter[] = [
  { id: 'all', name: 'All Markets', count: 8, icon: Globe },
  { id: 'favorites', name: 'Favorites', count: 2, icon: Star },
  { id: 'spot', name: 'Spot', count: 5, icon: DollarSign },
  { id: 'futures', name: 'Futures', count: 3, icon: TrendingUp },
  { id: 'perpetual', name: 'Perpetual', count: 2, icon: Activity },
  { id: 'options', name: 'Options', count: 0, icon: Settings }
];

export default function MarketsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');
  const [sortBy, setSortBy] = useState('volume');
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
  const [hideSmallBalances, setHideSmallBalances] = useState(false);

  const filteredMarkets = mockMarkets.filter(market => {
    const matchesSearch = market.pair.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          market.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = activeCategory === 'all' || 
                           (activeCategory === 'favorites' && market.isFavorite) ||
                           (activeCategory === 'spot' && !market.leverage) ||
                           (activeCategory === 'futures' && market.leverage && market.leverage !== 'Perp') ||
                           (activeCategory === 'perpetual' && market.leverage === 'Perp');
    const matchesFavorites = !showFavoritesOnly || market.isPositive;
    
    return matchesSearch && matchesCategory && matchesFavorites;
  });

  const sortedMarkets = [...filteredMarkets].sort((a, b) => {
    switch (sortBy) {
      case 'volume':
        return parseFloat(b.volume.replace('B', '').replace('M', '')) - 
               parseFloat(a.volume.replace('B', '').replace('M', ''));
      case 'price':
        return parseFloat(b.price.replace(',', '')) - parseFloat(a.price.replace(',', ''));
      case 'change':
        return parseFloat(b.changePercent.replace('%', '').replace('+', '')) - 
               parseFloat(a.changePercent.replace('%', '').replace('+', ''));
      default:
        return 0;
    }
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <BarChart3 size={16} className="text-white" />
                </div>
                <h1 className="text-xl font-bold text-gray-900">Markets</h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                <input
                  type="text"
                  placeholder="Search markets..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-blue-500 w-80"
                />
              </div>
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <Bell size={20} className="text-gray-600" />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <Settings size={20} className="text-gray-600" />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <HelpCircle size={20} className="text-gray-600" />
              </button>
              <div className="flex items-center space-x-2 px-3 py-2 bg-gray-100 rounded-lg">
                <div className="w-6 h-6 bg-blue-600 rounded-full"></div>
                <span className="text-sm font-medium text-gray-700">User</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Category Navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Categories">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setActiveCategory(category.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeCategory === category.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <category.icon size={16} />
                <span>{category.name}</span>
                {category.count && (
                  <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                    {category.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-lg transition-colors ${
                    viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <List size={16} />
                </button>
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-lg transition-colors ${
                    viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Grid size={16} />
                </button>
              </div>

              <div className="flex items-center space-x-2">
                <label className="flex items-center space-x-2 text-sm text-gray-600">
                  <input
                    type="checkbox"
                    checked={showFavoritesOnly}
                    onChange={(e) => setShowFavoritesOnly(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span>Favorites only</span>
                </label>
                <label className="flex items-center space-x-2 text-sm text-gray-600">
                  <input
                    type="checkbox"
                    checked={hideSmallBalances}
                    onChange={(e) => setHideSmallBalances(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span>Hide small balances</span>
                </label>
              </div>

              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Sort by:</span>
                <select 
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="px-3 py-1 bg-gray-50 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                >
                  <option value="volume">Volume</option>
                  <option value="price">Price</option>
                  <option value="change">Change</option>
                </select>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <RefreshCw size={16} className="text-gray-600" />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <Eye size={16} className="text-gray-600" />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <Filter size={16} className="text-gray-600" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Markets List */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {viewMode === 'list' ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      <div className="flex items-center space-x-2">
                        <Star size={14} />
                        <span>Pair</span>
                      </div>
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      24h Change
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      24h Volume
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Market Cap
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Chart (7D)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {sortedMarkets.map((market) => (
                    <tr key={market.id} className="hover:bg-gray-50 transition-colors cursor-pointer">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <button
                            className="mr-3"
                            onClick={(e) => {
                              e.stopPropagation();
                              // Toggle favorite logic
                            }}
                          >
                            <Star 
                              size={16} 
                              className={market.isFavorite ? 'text-yellow-500 fill-current' : 'text-gray-400'} 
                            />
                          </button>
                          <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mr-3">
                            <span className="text-sm font-bold text-gray-700">
                              {market.icon || market.pair.charAt(0)}
                            </span>
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900 flex items-center">
                              {market.pair}
                              {market.leverage && (
                                <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                                  {market.leverage}
                                </span>
                              )}
                            </div>
                            <div className="text-sm text-gray-500">{market.name}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          ${market.price}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`flex items-center text-sm font-medium ${
                          market.isPositive ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {market.isPositive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                          <span>{market.changePercent}</span>
                        </div>
                        <div className={`text-sm ${
                          market.isPositive ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {market.change}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">${market.volume}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">${market.marketCap}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="w-24 h-12 bg-gray-50 rounded flex items-center justify-center">
                          {market.sparkline && (
                            <svg viewBox="0 0 100 40" className="w-full h-full">
                              <polyline
                                points={market.sparkline.map((price, index) => {
                                  const normalizedPrice = ((price - Math.min(...market.sparkline!)) / 
                                    (Math.max(...market.sparkline!) - Math.min(...market.sparkline!))) * 35 + 2;
                                  return `${index * 14},${40 - normalizedPrice}`;
                                }).join(' ')}
                                fill="none"
                                stroke={market.isPositive ? '#10b981' : '#ef4444'}
                                strokeWidth="2"
                              />
                            </svg>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium hover:bg-blue-200">
                            Trade
                          </button>
                          <button className="p-1 text-gray-400 hover:text-gray-600">
                            <MoreVertical size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
              {sortedMarkets.map((market) => (
                <div key={market.id} className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors cursor-pointer">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <button
                        className="mr-2"
                        onClick={(e) => {
                          e.stopPropagation();
                          // Toggle favorite logic
                        }}
                      >
                        <Star 
                          size={14} 
                          className={market.isFavorite ? 'text-yellow-500 fill-current' : 'text-gray-400'} 
                        />
                      </button>
                      <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center mr-2">
                        <span className="text-xs font-bold text-gray-700">
                          {market.icon || market.pair.charAt(0)}
                        </span>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {market.pair}
                        </div>
                        <div className="text-xs text-gray-500">{market.name}</div>
                      </div>
                    </div>
                    <div className={`text-sm font-medium ${
                      market.isPositive ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {market.changePercent}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Price</span>
                      <span className="text-sm font-medium text-gray-900">${market.price}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">24h Volume</span>
                      <span className="text-sm text-gray-900">${market.volume}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Market Cap</span>
                      <span className="text-sm text-gray-900">${market.marketCap}</span>
                    </div>
                  </div>
                  
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <button className="w-full px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium transition-colors">
                      Trade {market.pair}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}