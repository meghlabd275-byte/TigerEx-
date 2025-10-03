'use client';

import React, { useState } from 'react';
import { 
  Eye, 
  EyeOff, 
  Plus, 
  Send, 
  ArrowLeftRight, 
  ChevronDown,
  Search,
  MoreHorizontal
} from 'lucide-react';

interface AssetItem {
  id: string;
  symbol: string;
  name: string;
  balance: string;
  usdValue: string;
  todayPnl: string;
  avgPrice: string;
  isPositive: boolean;
}

const mockAssets: AssetItem[] = [
  {
    id: '1',
    symbol: 'BNB',
    name: 'Binance Coin',
    balance: '0.00',
    usdValue: '$0.00',
    todayPnl: '+0.00%',
    avgPrice: '$315.20',
    isPositive: true,
  },
  {
    id: '2',
    symbol: 'BTC',
    name: 'Bitcoin',
    balance: '0.00',
    usdValue: '$0.00',
    todayPnl: '+0.00%',
    avgPrice: '$43,250.00',
    isPositive: true,
  },
  {
    id: '3',
    symbol: 'ETH',
    name: 'Ethereum',
    balance: '0.00',
    usdValue: '$0.00',
    todayPnl: '+0.00%',
    avgPrice: '$2,650.00',
    isPositive: true,
  },
  {
    id: '4',
    symbol: 'USDT',
    name: 'TetherUS',
    balance: '0.00',
    usdValue: '$0.00',
    todayPnl: '+0.00%',
    avgPrice: '$1.00',
    isPositive: true,
  },
];

export default function AssetsPage() {
  const [balanceVisible, setBalanceVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('Overview');
  const [activeSubTab, setActiveSubTab] = useState('Spot');
  const [viewMode, setViewMode] = useState('Coin View');
  const [hideSmallAssets, setHideSmallAssets] = useState(false);

  const mainTabs = ['Overview', 'Futures', 'Spot', 'Funding', 'Earn'];
  const subTabs = ['Spot', 'Cross Margin', 'Isolated Margin'];
  const timePeriods = ['1W', '1M', '3M', '6M'];

  return (
    <div className="min-h-screen bg-gray-50 lg:bg-bg-primary pb-20 lg:pb-0">
      {/* Mobile Header */}
      <div className="lg:hidden bg-white px-4 py-4 border-b border-gray-200">
        <div className="flex gap-2 mb-4 overflow-x-auto scrollbar-hide">
          {mainTabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`whitespace-nowrap px-4 py-2 text-sm font-medium ${
                activeTab === tab
                  ? 'text-primary border-b-2 border-primary'
                  : 'text-gray-600'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {activeTab === 'Overview' && (
          <div className="flex gap-2 overflow-x-auto scrollbar-hide">
            {subTabs.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveSubTab(tab)}
                className={`whitespace-nowrap px-3 py-2 text-sm ${
                  activeSubTab === tab
                    ? 'text-primary border-b-2 border-primary'
                    : 'text-gray-600'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Desktop Header */}
      <div className="hidden lg:block bg-bg-secondary border-b border-border-primary px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-text-primary">Assets</h1>
          <div className="flex items-center gap-4">
            <button className="btn-primary">
              Deposit
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:p-6">
        {/* Balance Section */}
        <div className="bg-white lg:bg-bg-secondary lg:rounded-lg lg:border lg:border-border-primary p-4 lg:p-6 mb-4 lg:mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 lg:text-text-primary">
              Estimated Balance
            </h2>
            <button onClick={() => setBalanceVisible(!balanceVisible)}>
              {balanceVisible ? (
                <Eye size={20} className="text-gray-500 lg:text-text-secondary" />
              ) : (
                <EyeOff size={20} className="text-gray-500 lg:text-text-secondary" />
              )}
            </button>
          </div>

          <div className="mb-6">
            <div className="text-3xl font-bold text-gray-900 lg:text-text-primary mb-2">
              {balanceVisible ? '0.00' : '****'} <span className="text-lg text-gray-500 lg:text-text-secondary">BTC</span>
            </div>
            <div className="text-gray-500 lg:text-text-secondary mb-1">
              ≈ ${balanceVisible ? '0.00' : '****'}
            </div>
            <div className="text-sm text-gray-500 lg:text-text-secondary mb-4">
              Today's PnL: ≈ ${balanceVisible ? '0.00' : '****'} ({balanceVisible ? '0.00%' : '****'})
            </div>

            {/* Time Period Tabs */}
            <div className="flex gap-2 mb-4">
              {timePeriods.map((period) => (
                <button
                  key={period}
                  className="px-3 py-1 text-sm text-gray-600 lg:text-text-secondary hover:text-primary"
                >
                  {period}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <button className="btn-primary flex items-center gap-2">
              <Plus size={16} />
              Add Funds
            </button>
            <button className="btn-secondary flex items-center gap-2">
              <Send size={16} />
              Send
            </button>
            <button className="btn-secondary flex items-center gap-2">
              <ArrowLeftRight size={16} />
              Transfer
            </button>
          </div>
        </div>

        {/* Small Amount Exchange */}
        <div className="bg-white lg:bg-bg-secondary lg:rounded-lg lg:border lg:border-border-primary p-4 lg:p-6 mb-4 lg:mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900 lg:text-text-primary">Small Amount Exchange</h3>
              <p className="text-sm text-gray-500 lg:text-text-secondary">Convert dust to BNB</p>
            </div>
            <button className="text-primary text-sm font-medium">
              Convert →
            </button>
          </div>
        </div>

        {/* My Assets */}
        <div className="bg-white lg:bg-bg-secondary lg:rounded-lg lg:border lg:border-border-primary">
          <div className="p-4 lg:p-6 border-b border-gray-100 lg:border-border-primary">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 lg:text-text-primary">My Assets</h3>
              <button className="text-primary text-sm font-medium">
                View All 350+ Coins →
              </button>
            </div>

            <div className="flex items-center justify-between mb-4">
              <div className="flex gap-4">
                <button
                  onClick={() => setViewMode('Coin View')}
                  className={`px-3 py-2 text-sm font-medium ${
                    viewMode === 'Coin View'
                      ? 'text-primary border-b-2 border-primary'
                      : 'text-gray-600 lg:text-text-secondary'
                  }`}
                >
                  Coin View
                </button>
                <button
                  onClick={() => setViewMode('Account View')}
                  className={`px-3 py-2 text-sm font-medium ${
                    viewMode === 'Account View'
                      ? 'text-primary border-b-2 border-primary'
                      : 'text-gray-600 lg:text-text-secondary'
                  }`}
                >
                  Account View
                </button>
              </div>

              <label className="flex items-center gap-2 text-sm text-gray-600 lg:text-text-secondary">
                <input
                  type="checkbox"
                  checked={hideSmallAssets}
                  onChange={(e) => setHideSmallAssets(e.target.checked)}
                  className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                />
                Hide assets &lt;1 USD
              </label>
            </div>
          </div>

          {/* Assets List */}
          <div>
            {mockAssets.map((asset) => (
              <div
                key={asset.id}
                className="px-4 lg:px-6 py-4 flex items-center justify-between border-b border-gray-100 lg:border-border-primary last:border-b-0 hover:bg-gray-50 lg:hover:bg-bg-tertiary"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-black">
                      {asset.symbol.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <div className="font-medium text-gray-900 lg:text-text-primary">
                      {asset.symbol}
                    </div>
                    <div className="text-sm text-gray-500 lg:text-text-secondary">
                      {asset.name}
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="font-medium text-gray-900 lg:text-text-primary">
                    {balanceVisible ? asset.balance : '****'}
                  </div>
                  <div className="text-sm text-gray-500 lg:text-text-secondary">
                    {balanceVisible ? asset.usdValue : '****'}
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-sm text-gray-500 lg:text-text-secondary">
                    Today's PnL
                  </div>
                  <div className="text-sm text-success">
                    {balanceVisible ? asset.todayPnl : '****'}
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-sm text-gray-500 lg:text-text-secondary">
                    Avg. Price
                  </div>
                  <div className="text-sm text-gray-900 lg:text-text-primary">
                    {balanceVisible ? asset.avgPrice : '****'}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button className="px-3 py-1 text-xs bg-primary text-black rounded font-medium">
                    Earn
                  </button>
                  <button className="px-3 py-1 text-xs bg-gray-100 lg:bg-bg-tertiary text-gray-600 lg:text-text-secondary rounded font-medium">
                    Trade
                  </button>
                  <button className="p-1 text-gray-400 lg:text-text-secondary">
                    <MoreHorizontal size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="bg-white lg:bg-bg-secondary lg:rounded-lg lg:border lg:border-border-primary mt-4 lg:mt-6">
          <div className="p-4 lg:p-6 border-b border-gray-100 lg:border-border-primary">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 lg:text-text-primary">Recent Transactions</h3>
              <button className="text-primary text-sm font-medium">
                More →
              </button>
            </div>
          </div>
          <div className="p-4 lg:p-6 text-center">
            <Search size={48} className="text-gray-300 lg:text-text-quaternary mx-auto mb-4" />
            <p className="text-gray-500 lg:text-text-secondary">No records</p>
          </div>
        </div>
      </div>
    </div>
  );
}