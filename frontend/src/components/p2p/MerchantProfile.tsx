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
import { Share2, ChevronRight, ThumbsUp } from 'lucide-react';

interface MerchantStats {
  trades30d: number;
  completionRate: number;
  avgReleaseTime: string;
  avgPayTime: string;
}

const MerchantProfile: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'trade' | 'notifications' | 'others'>('trade');

  const merchantStats: MerchantStats = {
    trades30d: 2,
    completionRate: 100.00,
    avgReleaseTime: '7.22 m',
    avgPayTime: '5.15 m',
  };

  const menuItems = [
    { icon: ThumbsUp, label: 'Received Feedback', count: 35, color: 'text-blue-500' },
    { icon: '💳', label: 'Payment Method(s)', count: 11, color: '' },
    { icon: '🔒', label: 'Restrictions Removal Center', count: null, color: '' },
    { icon: '👥', label: 'Follows', count: null, color: '' },
    { icon: '🚫', label: 'Blocked Users', count: null, color: '' },
    { icon: '🔗', label: 'Ad Sharing Code', count: null, color: '' },
    { icon: '👁️', label: 'Recently Viewed', count: null, color: '' },
  ];

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 pb-20">
      {/* Header */}
      <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-10">
        <div className="flex items-center justify-between px-4 py-3">
          <button className="text-gray-900 dark:text-white">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="text-lg font-semibold text-gray-900 dark:text-white">shahrukh</h1>
          <button className="text-gray-900 dark:text-white">
            <Share2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Stats Card */}
      <div className="mx-4 my-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="grid grid-cols-2 gap-6 mb-4">
          <div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {merchantStats.trades30d}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">30d Trades</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {merchantStats.completionRate}%
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">30d Completion Rate</div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {merchantStats.avgReleaseTime}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Avg. Release Time</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {merchantStats.avgPayTime}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Avg. Pay Time</div>
          </div>
        </div>

        <button className="w-full mt-4 text-center text-gray-500 dark:text-gray-400 text-sm flex items-center justify-center gap-1">
          More
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-800 px-4">
        <button
          onClick={() => setActiveTab('trade')}
          className={`px-4 py-3 font-medium border-b-2 transition-colors ${
            activeTab === 'trade'
              ? 'border-yellow-400 text-gray-900 dark:text-white'
              : 'border-transparent text-gray-500 dark:text-gray-400'
          }`}
        >
          Trade
        </button>
        <button
          onClick={() => setActiveTab('notifications')}
          className={`px-4 py-3 font-medium border-b-2 transition-colors ${
            activeTab === 'notifications'
              ? 'border-yellow-400 text-gray-900 dark:text-white'
              : 'border-transparent text-gray-500 dark:text-gray-400'
          }`}
        >
          Notifications
        </button>
        <button
          onClick={() => setActiveTab('others')}
          className={`px-4 py-3 font-medium border-b-2 transition-colors ${
            activeTab === 'others'
              ? 'border-yellow-400 text-gray-900 dark:text-white'
              : 'border-transparent text-gray-500 dark:text-gray-400'
          }`}
        >
          Others
        </button>
      </div>

      {/* Menu Items */}
      <div className="divide-y divide-gray-100 dark:divide-gray-800">
        {menuItems.map((item, index) => (
          <button
            key={index}
            className="w-full px-4 py-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              {typeof item.icon === 'string' ? (
                <span className="text-2xl">{item.icon}</span>
              ) : (
                <item.icon className={`w-5 h-5 ${item.color || 'text-gray-600 dark:text-gray-400'}`} />
              )}
              <span className="text-gray-900 dark:text-white font-medium">
                {item.label}
              </span>
            </div>
            <div className="flex items-center gap-2">
              {item.count !== null && (
                <span className="text-gray-500 dark:text-gray-400">{item.count}</span>
              )}
              <ChevronRight className="w-5 h-5 text-gray-400" />
            </div>
          </button>
        ))}
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
        <div className="flex justify-around items-center h-16">
          <button className="flex flex-col items-center justify-center flex-1 text-gray-500 dark:text-gray-400">
            <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span className="text-xs">Home</span>
          </button>
          <button className="flex flex-col items-center justify-center flex-1 text-gray-500 dark:text-gray-400">
            <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <span className="text-xs">Orders</span>
          </button>
          <button className="flex flex-col items-center justify-center flex-1 text-gray-500 dark:text-gray-400">
            <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
            </svg>
            <span className="text-xs">Ads</span>
          </button>
          <button className="flex flex-col items-center justify-center flex-1 text-gray-500 dark:text-gray-400 relative">
            <div className="relative">
              <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <span className="absolute -top-1 -right-1 w-2 h-2 bg-yellow-400 rounded-full"></span>
            </div>
            <span className="text-xs">Chat</span>
          </button>
          <button className="flex flex-col items-center justify-center flex-1 text-gray-900 dark:text-white">
            <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span className="text-xs">Profile</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default MerchantProfile;