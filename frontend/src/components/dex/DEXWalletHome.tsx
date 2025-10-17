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

import React, { useState } from 'react';
import { useWallet } from '../../contexts/WalletContext';
import { 
  Search, 
  ChevronDown, 
  Copy, 
  Calendar, 
  Radio, 
  Lock, 
  Users, 
  MoreHorizontal,
  TrendingUp,
  TrendingDown,
  ChevronRight
} from 'lucide-react';

interface Token {
  symbol: string;
  name: string;
  icon: string;
  price: number;
  change24h: number;
  marketCap: string;
  volume: string;
  badges?: string[];
}

const DEXWalletHome: React.FC = () => {
  const { wallet } = useWallet();
  const [activeTab, setActiveTab] = useState<'watchlist' | 'trending' | 'alpha' | 'newest'>('trending');
  const [timeFilter, setTimeFilter] = useState('1h');
  const [searchQuery, setSearchQuery] = useState('');

  const quickActions = [
    { icon: Calendar, label: 'Alpha', color: 'bg-purple-500' },
    { icon: Radio, label: 'Signals', color: 'bg-blue-500' },
    { icon: Lock, label: 'Earn', color: 'bg-green-500' },
    { icon: Users, label: 'Referral', color: 'bg-orange-500' },
    { icon: MoreHorizontal, label: 'More', color: 'bg-gray-500' },
  ];

  const trendingTokens: Token[] = [
    {
      symbol: 'P',
      name: 'Peanut',
      icon: '🥜',
      price: 10.12,
      change24h: -1.61,
      marketCap: '฿125.53M',
      volume: '฿10.13B',
      badges: ['🔥', '⚡', '🌟']
    },
    {
      symbol: 'EVAA',
      name: 'EVAA',
      icon: '💜',
      price: 620.21,
      change24h: 4.15,
      marketCap: '฿874.92M',
      volume: '฿18.61B',
      badges: ['🔥']
    },
    {
      symbol: 'KOGE',
      name: 'KOGE',
      icon: '🐶',
      price: 15916.06,
      change24h: 12.45,
      marketCap: '฿2.5B',
      volume: '฿45.2B',
      badges: ['⚡']
    },
    {
      symbol: 'MEME',
      name: 'Meme Coin',
      icon: '😂',
      price: 0.0045,
      change24h: -5.23,
      marketCap: '฿89.3M',
      volume: '฿5.8B',
      badges: ['🔥', '🌟']
    },
  ];

  const copyAddress = () => {
    if (wallet?.address) {
      navigator.clipboard.writeText(wallet.address);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between px-4 py-3">
          <button className="p-2">
            <svg className="w-6 h-6 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div className="flex items-center gap-4">
            <button className="text-gray-500 dark:text-gray-400">Exchange</button>
            <button className="text-gray-900 dark:text-white font-semibold">Wallet</button>
          </div>
          <div className="flex items-center gap-3">
            <button className="p-2">
              <svg className="w-6 h-6 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </button>
            <button className="p-2">
              <svg className="w-6 h-6 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="px-4 pb-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-yellow-400"
            />
          </div>
        </div>
      </div>

      {/* Balance Section */}
      <div className="bg-white dark:bg-gray-800 px-4 py-6">
        <div className="flex items-center justify-between mb-2">
          <button className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
            <ChevronDown className="w-5 h-5" />
            <Copy className="w-5 h-5" />
          </button>
        </div>
        <div className="text-5xl font-bold text-gray-900 dark:text-white mb-1">
          ฿0
        </div>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          ≈ $0.00
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white dark:bg-gray-800 px-4 py-4 mb-2">
        <div className="flex justify-between items-center">
          {quickActions.map((action, index) => (
            <button
              key={index}
              className="flex flex-col items-center gap-2"
            >
              <div className={`w-12 h-12 ${action.color} rounded-full flex items-center justify-center`}>
                <action.icon className="w-6 h-6 text-white" />
              </div>
              <span className="text-xs text-gray-700 dark:text-gray-300">{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Turtle Booster Program */}
      <div className="bg-white dark:bg-gray-800 mx-4 mb-2 rounded-lg p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
            <span className="text-2xl">🐢</span>
          </div>
          <span className="font-semibold text-gray-900 dark:text-white">
            Turtle Booster Program Phase 1
          </span>
        </div>
        <button className="px-4 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg font-medium">
          Join
        </button>
      </div>

      {/* Meme Rush & Earn Cards */}
      <div className="grid grid-cols-2 gap-2 px-4 mb-2">
        {/* Meme Rush */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600 dark:text-gray-400">Meme Rush</span>
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
            1.7K
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            new tokens in 1h
          </div>
          <div className="flex gap-1 mt-2">
            {['🔥', '💎', '🚀', '⚡', '🌟'].map((emoji, i) => (
              <span key={i} className="text-lg">{emoji}</span>
            ))}
          </div>
        </div>

        {/* Earn */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600 dark:text-gray-400">Earn</span>
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </div>
          <div className="text-2xl font-bold text-green-500 mb-1">
            15.2%
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">
            APY
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
              <span className="text-white text-xs font-bold">₮</span>
            </div>
            <span className="text-sm font-medium text-gray-900 dark:text-white">USDT</span>
          </div>
          <div className="mt-2">
            <svg className="w-full h-8" viewBox="0 0 100 30" preserveAspectRatio="none">
              <path
                d="M0,15 Q25,5 50,15 T100,15"
                fill="none"
                stroke="#10b981"
                strokeWidth="2"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex px-4">
          {['watchlist', 'trending', 'alpha', 'newest'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`px-4 py-3 font-medium capitalize border-b-2 transition-colors ${
                activeTab === tab
                  ? 'border-yellow-400 text-gray-900 dark:text-white'
                  : 'border-transparent text-gray-500 dark:text-gray-400'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white dark:bg-gray-800 px-4 py-3 flex items-center justify-between border-b border-gray-200 dark:border-gray-700">
        <button className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          All
        </button>
        <div className="flex items-center gap-2">
          {['1h', '24h', '7d'].map((filter) => (
            <button
              key={filter}
              onClick={() => setTimeFilter(filter)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                timeFilter === filter
                  ? 'bg-yellow-400 text-gray-900'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
              }`}
            >
              {filter}
            </button>
          ))}
          <ChevronDown className="w-5 h-5 text-gray-500" />
        </div>
      </div>

      {/* Token List */}
      <div className="bg-white dark:bg-gray-800 divide-y divide-gray-100 dark:divide-gray-700">
        {trendingTokens.map((token, index) => (
          <div key={index} className="px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-750">
            <div className="flex items-center gap-3 flex-1">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-2xl">
                {token.icon}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {token.symbol}
                  </span>
                  {token.badges?.map((badge, i) => (
                    <span key={i} className="text-sm">{badge}</span>
                  ))}
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                  <span>{token.marketCap}</span>
                  <span>{token.volume}</span>
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="font-semibold text-gray-900 dark:text-white mb-1">
                ฿{token.price.toFixed(2)}
              </div>
              <div
                className={`flex items-center justify-end gap-1 text-sm font-medium ${
                  token.change24h > 0 ? 'text-green-500' : 'text-red-500'
                }`}
              >
                {token.change24h > 0 ? (
                  <TrendingUp className="w-4 h-4" />
                ) : (
                  <TrendingDown className="w-4 h-4" />
                )}
                {token.change24h > 0 ? '+' : ''}
                {token.change24h.toFixed(2)}%
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="flex justify-around items-center h-16">
          <button className="flex flex-col items-center justify-center flex-1 text-gray-900 dark:text-white">
            <svg className="w-6 h-6 mb-1" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
            </svg>
            <span className="text-xs">Home</span>
          </button>
          <button className="flex flex-col items-center justify-center flex-1 text-gray-500 dark:text-gray-400">
            <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
            <span className="text-xs">Markets</span>
          </button>
          <button className="flex flex-col items-center justify-center flex-1 text-gray-500 dark:text-gray-400">
            <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
            <span className="text-xs">Trade</span>
          </button>
          <button className="flex flex-col items-center justify-center flex-1 text-gray-500 dark:text-gray-400">
            <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span className="text-xs">Discover</span>
          </button>
          <button className="flex flex-col items-center justify-center flex-1 text-gray-500 dark:text-gray-400">
            <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
            <span className="text-xs">Assets</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default DEXWalletHome;