'use client';

import React, { useState } from 'react';
import { 
  Search, 
  Bell, 
  Settings, 
  Eye, 
  EyeOff,
  Plus,
  Gift,
  Users,
  CreditCard,
  TrendingUp,
  MoreHorizontal,
  ChevronDown,
  Star
} from 'lucide-react';

interface ShortcutItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  color: string;
}

interface TokenItem {
  id: string;
  symbol: string;
  name: string;
  price: string;
  change: string;
  changePercent: string;
  volume: string;
  isPositive: boolean;
}

const shortcuts: ShortcutItem[] = [
  { id: 'loans', label: 'Loans', icon: CreditCard, color: 'bg-blue-500' },
  { id: 'rewards', label: 'Rewards Hub', icon: Gift, color: 'bg-purple-500' },
  { id: 'referral', label: 'Referral', icon: Users, color: 'bg-green-500' },
  { id: 'gift-card', label: 'Gift Card', icon: Gift, color: 'bg-red-500' },
  { id: 'red-packet', label: 'Red Packet', icon: Gift, color: 'bg-red-600' },
  { id: 'futures', label: 'Futures', icon: TrendingUp, color: 'bg-orange-500' },
  { id: 'spot', label: 'Spot', icon: TrendingUp, color: 'bg-blue-600' },
  { id: 'more', label: 'Edit', icon: MoreHorizontal, color: 'bg-gray-500' },
];

const mockTokens: TokenItem[] = [
  {
    id: '1',
    symbol: 'BTC',
    name: 'Bitcoin',
    price: '43,250.00',
    change: '+1,250.00',
    changePercent: '+2.98%',
    volume: '1.2B',
    isPositive: true,
  },
  {
    id: '2',
    symbol: 'ETH',
    name: 'Ethereum',
    price: '2,650.00',
    change: '+85.50',
    changePercent: '+3.33%',
    volume: '850M',
    isPositive: true,
  },
  {
    id: '3',
    symbol: 'BNB',
    name: 'BNB',
    price: '315.20',
    change: '-5.80',
    changePercent: '-1.81%',
    volume: '420M',
    isPositive: false,
  },
];

export default function HomeScreen() {
  const [balanceVisible, setBalanceVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('Exchange');

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-white px-4 py-3 flex items-center justify-between border-b border-gray-200">
        <div className="flex items-center gap-4">
          <button
            className={`px-4 py-2 rounded-lg font-medium ${
              activeTab === 'Exchange'
                ? 'bg-primary text-black'
                : 'text-gray-600'
            }`}
            onClick={() => setActiveTab('Exchange')}
          >
            Exchange
          </button>
          <button
            className={`px-4 py-2 rounded-lg font-medium ${
              activeTab === 'Wallet'
                ? 'bg-primary text-black'
                : 'text-gray-600'
            }`}
            onClick={() => setActiveTab('Wallet')}
          >
            Wallet
          </button>
        </div>
        <div className="flex items-center gap-3">
          <Search size={20} className="text-gray-600" />
          <Bell size={20} className="text-gray-600" />
          <Settings size={20} className="text-gray-600" />
        </div>
      </div>

      {/* User Profile Section */}
      <div className="bg-white px-4 py-6 border-b border-gray-200">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
            <span className="text-black font-bold text-lg">U</span>
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">User-0f8ed</h2>
            <div className="flex items-center gap-2">
              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                Regular
              </span>
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                Verified
              </span>
            </div>
          </div>
        </div>

        {/* Balance Display */}
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-gray-600 text-sm">Total Balance</span>
            <button onClick={() => setBalanceVisible(!balanceVisible)}>
              {balanceVisible ? (
                <Eye size={16} className="text-gray-500" />
              ) : (
                <EyeOff size={16} className="text-gray-500" />
              )}
            </button>
            <div className="flex items-center gap-1 ml-auto">
              <span className="text-sm text-gray-600">USDT</span>
              <ChevronDown size={16} className="text-gray-500" />
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">
            {balanceVisible ? '12,450.67' : '******'}
          </div>
          <div className="text-sm text-gray-600 mb-4">
            Today's PNL: {balanceVisible ? '+125.45 (+1.02%)' : '******'}
          </div>
          <button className="w-full bg-primary text-black font-medium py-3 rounded-lg">
            Add Funds
          </button>
        </div>
      </div>

      {/* Shortcuts Grid */}
      <div className="bg-white px-4 py-6 border-b border-gray-200">
        <div className="grid grid-cols-4 gap-4">
          {shortcuts.map((shortcut) => {
            const Icon = shortcut.icon;
            return (
              <button
                key={shortcut.id}
                className="flex flex-col items-center gap-2 p-3 rounded-lg hover:bg-gray-50"
              >
                <div className={`w-10 h-10 ${shortcut.color} rounded-lg flex items-center justify-center`}>
                  <Icon size={20} className="text-white" />
                </div>
                <span className="text-xs text-gray-700 text-center">
                  {shortcut.label}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Recommendations Section */}
      <div className="bg-white px-4 py-6 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900 mb-4">Recommendations</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gradient-to-r from-green-50 to-green-100 rounded-lg">
            <div>
              <h4 className="font-medium text-gray-900">New Listing Promos</h4>
              <p className="text-sm text-gray-600">Earn rewards on new tokens</p>
            </div>
            <button className="bg-success text-white px-4 py-2 rounded-lg text-sm font-medium">
              Join
            </button>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg">
            <div>
              <h4 className="font-medium text-gray-900">Simple Earn</h4>
              <p className="text-sm text-gray-600">15.2% APY USDT</p>
            </div>
            <button className="bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium">
              Earn
            </button>
          </div>
        </div>
      </div>

      {/* Market Tabs */}
      <div className="bg-white px-4 py-4 border-b border-gray-200">
        <div className="flex items-center gap-4 mb-4">
          <h3 className="font-semibold text-gray-900">Markets</h3>
          <button className="text-primary text-sm font-medium ml-auto">
            More →
          </button>
        </div>
        <div className="flex gap-2 mb-4 overflow-x-auto scrollbar-hide">
          {['Holding', 'Hot', 'New Listing', 'Favorite', 'Top Gainers', '24h Volume'].map((tab) => (
            <button
              key={tab}
              className="whitespace-nowrap px-3 py-2 text-sm text-gray-600 hover:text-primary"
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Token List */}
      <div className="bg-white">
        <div className="px-4 py-2 flex items-center justify-between text-sm text-gray-600 border-b border-gray-100">
          <span>Coin</span>
          <span>Coin Price</span>
          <span>24H Change</span>
        </div>
        {mockTokens.map((token) => (
          <div
            key={token.id}
            className="px-4 py-3 flex items-center justify-between border-b border-gray-100 hover:bg-gray-50"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <span className="text-xs font-bold text-black">
                  {token.symbol.charAt(0)}
                </span>
              </div>
              <div>
                <div className="font-medium text-gray-900">{token.symbol}</div>
                <div className="text-xs text-gray-500">{token.name}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="font-medium text-gray-900">${token.price}</div>
              <div className="text-xs text-gray-500">{token.volume}</div>
            </div>
            <div className="text-right">
              <div className={`font-medium ${token.isPositive ? 'text-success' : 'text-danger'}`}>
                {token.changePercent}
              </div>
              <div className={`text-xs ${token.isPositive ? 'text-success' : 'text-danger'}`}>
                {token.change}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}