import React, { useState } from 'react';
import { 
  Search, 
  Menu, 
  Headphones, 
  QrCode, 
  TrendingUp, 
  TrendingDown,
  Calendar,
  Signal,
  Lock,
  User,
  MoreHorizontal,
  Star
} from 'lucide-react';

interface ExchangeHomeProps {
  onNavigate: (section: string, data?: any) => void;
}

const ExchangeHome: React.FC<ExchangeHomeProps> = ({ onNavigate }) => {
  const [activeTab, setActiveTab] = useState<'Exchange' | 'Wallet'>('Exchange');
  const [selectedTimeframe, setSelectedTimeframe] = useState('1h');

  const balance = "₹0";

  const quickActions = [
    { icon: Calendar, label: 'Alpha', action: 'alpha' },
    { icon: Signal, label: 'Signals', action: 'signals' },
    { icon: Lock, label: 'Earn', action: 'earn' },
    { icon: User, label: 'Referral', action: 'referral' },
    { icon: MoreHorizontal, label: 'More', action: 'more' }
  ];

  const featuredPrograms = [
    {
      title: 'Turtle Booster Program Phase 1',
      action: 'Join',
      color: 'bg-green-100 text-green-800'
    }
  ];

  const marketSections = [
    {
      title: 'Meme Rush',
      subtitle: '1.7K new tokens in 1h',
      value: '1.7K',
      change: 'new tokens in 1h'
    },
    {
      title: 'Earn',
      subtitle: '15.2% APY',
      value: '15.2%',
      change: 'APY',
      currency: 'USDT'
    }
  ];

  const trendingCoins = [
    {
      symbol: 'P',
      name: 'Polygon',
      price: '₹10.12',
      change: '-1.61%',
      isPositive: false,
      marketCap: '₹125.53M',
      volume: '₹10.13B'
    },
    {
      symbol: 'EVAA',
      name: 'EVAA',
      price: '₹620.21',
      change: '+4.15%',
      isPositive: true,
      marketCap: '₹874.92M',
      volume: '₹18.61B'
    },
    {
      symbol: 'KOGE',
      name: 'KOGE',
      price: '₹5,016.06',
      change: '+2.89%',
      isPositive: true,
      marketCap: '₹2.45B',
      volume: '₹892.34M'
    }
  ];

  const marketTabs = ['Watchlist', 'Trending', 'Alpha', 'Newest'];
  const timeframes = ['1h', '24h', '7d', '30d'];

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Top Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <button className="p-2 -ml-2">
            <Menu className="w-6 h-6 text-gray-700" />
          </button>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setActiveTab('Exchange')}
              className={`text-lg font-medium ${
                activeTab === 'Exchange' ? 'text-gray-900' : 'text-gray-500'
              }`}
            >
              Exchange
            </button>
            <button
              onClick={() => setActiveTab('Wallet')}
              className={`text-lg font-medium ${
                activeTab === 'Wallet' ? 'text-gray-900' : 'text-gray-500'
              }`}
            >
              Wallet
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <button className="p-2">
              <Headphones className="w-5 h-5 text-gray-700" />
            </button>
            <button className="p-2">
              <QrCode className="w-5 h-5 text-gray-700" />
            </button>
          </div>
        </div>
      </header>

      {/* Search Bar */}
      <div className="bg-white px-4 py-3 border-b border-gray-200">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search"
            className="w-full pl-10 pr-4 py-2 bg-gray-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500"
          />
        </div>
      </div>

      {/* Balance Display */}
      <div className="bg-white px-4 py-6 border-b border-gray-200">
        <div className="flex items-center space-x-2 mb-2">
          <button className="p-1">
            <Menu className="w-4 h-4 text-gray-400" />
          </button>
          <button className="p-1">
            <QrCode className="w-4 h-4 text-gray-400" />
          </button>
        </div>
        <div className="text-3xl font-bold text-gray-900 mb-4">{balance}</div>

        {/* Quick Actions */}
        <div className="flex justify-between">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => onNavigate(action.action)}
              className="flex flex-col items-center space-y-2 p-2 hover:bg-gray-50 rounded-lg transition-colors"
            >
              <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                <action.icon className="w-6 h-6 text-gray-600" />
              </div>
              <span className="text-xs font-medium text-gray-700">{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Featured Programs */}
      {featuredPrograms.map((program, index) => (
        <div key={index} className="bg-white mx-4 my-4 p-4 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm">🐢</span>
              </div>
              <span className="font-medium text-gray-900">{program.title}</span>
            </div>
            <button className={`px-4 py-2 rounded-lg font-medium ${program.color}`}>
              {program.action}
            </button>
          </div>
        </div>
      ))}

      {/* Market Sections */}
      <div className="flex space-x-4 px-4 mb-4">
        {marketSections.map((section, index) => (
          <button
            key={index}
            onClick={() => onNavigate(section.title.toLowerCase())}
            className="flex-1 bg-white p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
          >
            <div className="text-left">
              <div className="text-sm text-gray-600 mb-1">{section.title}</div>
              <div className="text-lg font-bold text-gray-900 mb-1">{section.value}</div>
              <div className="text-xs text-gray-500">{section.change}</div>
              {section.currency && (
                <div className="flex items-center mt-2">
                  <div className="w-4 h-4 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-xs text-gray-600">{section.currency}</span>
                </div>
              )}
            </div>
            {index === 1 && (
              <div className="mt-2">
                <div className="w-8 h-6 bg-yellow-100 rounded flex items-center justify-center">
                  <TrendingUp className="w-4 h-4 text-yellow-600" />
                </div>
              </div>
            )}
          </button>
        ))}
      </div>

      {/* Market Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="flex overflow-x-auto px-4">
          {marketTabs.map((tab) => (
            <button
              key={tab}
              className="px-4 py-3 text-sm font-medium whitespace-nowrap text-gray-500 hover:text-gray-700"
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Timeframe Selector */}
      <div className="bg-white px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1">
            <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
            <span className="text-sm font-medium text-gray-900">All</span>
          </div>
          <div className="flex items-center space-x-2">
            {timeframes.map((timeframe) => (
              <button
                key={timeframe}
                onClick={() => setSelectedTimeframe(timeframe)}
                className={`px-2 py-1 text-xs rounded ${
                  selectedTimeframe === timeframe
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {timeframe}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Trending Coins */}
      <div className="bg-white divide-y divide-gray-100">
        {trendingCoins.map((coin, index) => (
          <button
            key={index}
            onClick={() => onNavigate('coin-detail', coin)}
            className="w-full p-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-bold">{coin.symbol}</span>
                </div>
                <div className="text-left">
                  <div className="font-medium text-gray-900">{coin.symbol}</div>
                  <div className="text-sm text-gray-500">
                    ₹{coin.marketCap} • ₹{coin.volume}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="font-medium text-gray-900">{coin.price}</div>
                <div className={`text-sm ${coin.isPositive ? 'text-green-500' : 'text-red-500'}`}>
                  {coin.change}
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ExchangeHome;