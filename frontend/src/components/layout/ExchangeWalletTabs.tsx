import React, { useState } from 'react';
import { Search, Bell, Headphones, QrCode } from 'lucide-react';

interface ExchangeWalletTabsProps {
  activeTab: 'exchange' | 'wallet';
  onTabChange: (tab: 'exchange' | 'wallet') => void;
}

const ExchangeWalletTabs: React.FC<ExchangeWalletTabsProps> = ({ activeTab, onTabChange }) => {
  return (
    <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
      <div className="flex items-center justify-between px-4 py-3">
        {/* Left side - Menu and notifications */}
        <div className="flex items-center gap-4">
          <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
            <div className="w-6 h-6 flex flex-col justify-center gap-1">
              <div className="h-0.5 bg-gray-700 dark:bg-gray-300"></div>
              <div className="h-0.5 bg-gray-700 dark:bg-gray-300"></div>
              <div className="h-0.5 bg-gray-700 dark:bg-gray-300"></div>
            </div>
          </button>
          <div className="relative">
            <Bell className="w-6 h-6 text-gray-700 dark:text-gray-300" />
            <span className="absolute -top-1 -right-1 bg-yellow-400 text-black text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
              99+
            </span>
          </div>
        </div>

        {/* Center - Exchange/Wallet Tabs */}
        <div className="flex items-center gap-8">
          <button
            onClick={() => onTabChange('exchange')}
            className={`text-lg font-semibold pb-1 ${
              activeTab === 'exchange'
                ? 'text-gray-900 dark:text-white border-b-2 border-yellow-400'
                : 'text-gray-500 dark:text-gray-400'
            }`}
          >
            Exchange
          </button>
          <button
            onClick={() => onTabChange('wallet')}
            className={`text-lg font-semibold pb-1 ${
              activeTab === 'wallet'
                ? 'text-gray-900 dark:text-white border-b-2 border-yellow-400'
                : 'text-gray-500 dark:text-gray-400'
            }`}
          >
            Wallet
          </button>
        </div>

        {/* Right side - Support and QR */}
        <div className="flex items-center gap-4">
          <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
            <Headphones className="w-6 h-6 text-gray-700 dark:text-gray-300" />
          </button>
          <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
            <QrCode className="w-6 h-6 text-gray-700 dark:text-gray-300" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExchangeWalletTabs;