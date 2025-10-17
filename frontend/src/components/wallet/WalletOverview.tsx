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
import { TrendingUp, Eye, EyeOff, BarChart2, QrCode } from 'lucide-react';

interface Asset {
  symbol: string;
  name: string;
  balance: string;
  usdValue: string;
  todayPnl: string;
  avgPrice: string;
  icon: string;
}

const WalletOverview: React.FC = () => {
  const [showBalance, setShowBalance] = useState(false);
  const [activeTab, setActiveTab] = useState<'crypto' | 'account'>('crypto');

  const assets: Asset[] = [
    {
      symbol: 'USDT',
      name: 'TetherUS',
      balance: '******',
      usdValue: '******',
      todayPnl: '******',
      avgPrice: '******',
      icon: '₮',
    },
    {
      symbol: 'SHIB',
      name: 'SHIBA INU',
      balance: '******',
      usdValue: '******',
      todayPnl: '***********',
      avgPrice: '******',
      icon: '🐕',
    },
    {
      symbol: 'LUNC',
      name: 'Terra Classic',
      balance: '******',
      usdValue: '******',
      todayPnl: '***********',
      avgPrice: '******',
      icon: '🌙',
    },
    {
      symbol: 'FUN',
      name: 'FunToken',
      balance: '******',
      usdValue: '******',
      todayPnl: '***********',
      avgPrice: '******',
      icon: '🎮',
    },
  ];

  return (
    <div className="bg-white dark:bg-gray-900 min-h-screen">
      {/* Header Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-800">
        <div className="flex px-4">
          <button className="px-4 py-4 text-gray-900 dark:text-white font-semibold border-b-2 border-yellow-400">
            Overview
          </button>
          <button className="px-4 py-4 text-gray-500 dark:text-gray-400">
            Futures
          </button>
          <button className="px-4 py-4 text-gray-500 dark:text-gray-400">
            Spot
          </button>
          <button className="px-4 py-4 text-gray-500 dark:text-gray-400">
            Funding
          </button>
          <button className="px-4 py-4 text-gray-500 dark:text-gray-400">
            Earn
          </button>
        </div>
      </div>

      {/* Total Value Section */}
      <div className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Est. Total Value</span>
            <button onClick={() => setShowBalance(!showBalance)}>
              {showBalance ? (
                <Eye className="w-4 h-4 text-gray-400" />
              ) : (
                <EyeOff className="w-4 h-4 text-gray-400" />
              )}
            </button>
          </div>
          <div className="flex items-center gap-3">
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
              <BarChart2 className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
              <QrCode className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>
          </div>
        </div>

        <div className="mb-4">
          <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
            {showBalance ? '0.00' : '******'}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">USDT</span>
            <button className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        </div>

        <div className="mb-4">
          <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Today's PNL</div>
          <div className="text-lg font-semibold text-gray-900 dark:text-white">
            {showBalance ? '0.00' : '******'}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          <button className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-3 rounded-lg">
            Add Funds
          </button>
          <button className="bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-900 dark:text-white font-semibold py-3 rounded-lg">
            Send
          </button>
          <button className="bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-900 dark:text-white font-semibold py-3 rounded-lg">
            Transfer
          </button>
        </div>

        {/* Crypto/Account Tabs */}
        <div className="flex gap-4 mb-4">
          <button
            onClick={() => setActiveTab('crypto')}
            className={`pb-2 font-semibold ${
              activeTab === 'crypto'
                ? 'text-gray-900 dark:text-white border-b-2 border-yellow-400'
                : 'text-gray-500 dark:text-gray-400'
            }`}
          >
            Crypto
          </button>
          <button
            onClick={() => setActiveTab('account')}
            className={`pb-2 font-semibold ${
              activeTab === 'account'
                ? 'text-gray-900 dark:text-white border-b-2 border-yellow-400'
                : 'text-gray-500 dark:text-gray-400'
            }`}
          >
            Account
          </button>
          <div className="ml-auto flex items-center gap-2">
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
              <svg className="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
              <svg className="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
            </button>
          </div>
        </div>

        {/* Assets List */}
        <div className="space-y-1">
          {assets.map((asset) => (
            <div
              key={asset.symbol}
              className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 hover:bg-gray-100 dark:hover:bg-gray-750 cursor-pointer"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-yellow-400 flex items-center justify-center text-xl">
                    {asset.icon}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900 dark:text-white">{asset.symbol}</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">{asset.name}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-gray-900 dark:text-white">{asset.balance}</div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">{asset.usdValue}</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                <div>
                  <div className="text-gray-500 dark:text-gray-400 mb-1">Today's PNL</div>
                  <div className="text-gray-900 dark:text-white font-medium">{asset.todayPnl}</div>
                </div>
                <div>
                  <div className="text-gray-500 dark:text-gray-400 mb-1">Average Price</div>
                  <div className="text-gray-900 dark:text-white font-medium">{asset.avgPrice}</div>
                </div>
              </div>

              <div className="flex gap-2">
                <button className="flex-1 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-medium py-2 rounded-lg">
                  Earn
                </button>
                <button className="flex-1 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-medium py-2 rounded-lg">
                  Trade
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WalletOverview;