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
  MoreHorizontal,
  TrendingUp,
  TrendingDown,
  Download,
  Filter,
  RefreshCw,
  Wallet,
  CreditCard,
  Zap,
  Star,
  Gift,
  ArrowUpRight,
  ArrowDownRight,
  DollarSign,
  Activity,
  Settings,
  Bell,
  HelpCircle,
  ChevronRight
} from 'lucide-react';

interface AssetItem {
  id: string;
  symbol: string;
  name: string;
  balance: string;
  usdValue: string;
  todayPnl: string;
  pnlPercentage: string;
  avgPrice: string;
  isPositive: boolean;
  change24h: number;
  icon?: string;
}

interface TransactionItem {
  id: string;
  type: 'deposit' | 'withdrawal' | 'trade' | 'earn';
  asset: string;
  amount: string;
  value: string;
  status: 'completed' | 'pending' | 'failed';
  timestamp: string;
  from?: string;
  to?: string;
}

const mockAssets: AssetItem[] = [
  {
    id: '1',
    symbol: 'BTC',
    name: 'Bitcoin',
    balance: '0.0523',
    usdValue: '$3,548.12',
    todayPnl: '+$125.50',
    pnlPercentage: '+3.67%',
    avgPrice: '$65,450.00',
    isPositive: true,
    change24h: 3.67,
    icon: '₿'
  },
  {
    id: '2',
    symbol: 'ETH',
    name: 'Ethereum',
    balance: '2.456',
    usdValue: '$8,694.23',
    todayPnl: '+$234.18',
    pnlPercentage: '+2.77%',
    avgPrice: '$3,420.00',
    isPositive: true,
    change24h: 2.77,
    icon: 'Ξ'
  },
  {
    id: '3',
    symbol: 'BNB',
    name: 'Binance Coin',
    balance: '15.234',
    usdValue: '$9,334.56',
    todayPnl: '-$45.12',
    pnlPercentage: '-0.48%',
    avgPrice: '$618.50',
    isPositive: false,
    change24h: -0.48,
    icon: 'B'
  },
  {
    id: '4',
    symbol: 'USDT',
    name: 'TetherUS',
    balance: '5,000.00',
    usdValue: '$5,000.00',
    todayPnl: '+$0.00',
    pnlPercentage: '+0.00%',
    avgPrice: '$1.00',
    isPositive: true,
    change24h: 0.00,
    icon: '₮'
  },
  {
    id: '5',
    symbol: 'SOL',
    name: 'Solana',
    balance: '45.678',
    usdValue: '$6,656.34',
    todayPnl: '+$456.78',
    pnlPercentage: '+7.37%',
    avgPrice: '$135.60',
    isPositive: true,
    change24h: 7.37,
    icon: 'S'
  },
  {
    id: '6',
    symbol: 'ADA',
    name: 'Cardano',
    balance: '2,500.00',
    usdValue: '$962.50',
    todayPnl: '-$12.50',
    pnlPercentage: '-1.28%',
    avgPrice: '$0.390',
    isPositive: false,
    change24h: -1.28,
    icon: 'A'
  }
];

const mockTransactions: TransactionItem[] = [
  {
    id: '1',
    type: 'deposit',
    asset: 'USDT',
    amount: '1,000.00',
    value: '$1,000.00',
    status: 'completed',
    timestamp: '2 hours ago',
    from: '0x1234...5678'
  },
  {
    id: '2',
    type: 'trade',
    asset: 'BTC/USDT',
    amount: '0.01',
    value: '$678.50',
    status: 'completed',
    timestamp: '5 hours ago'
  },
  {
    id: '3',
    type: 'earn',
    asset: 'BNB',
    amount: '0.025',
    value: '$15.31',
    status: 'completed',
    timestamp: '1 day ago'
  },
  {
    id: '4',
    type: 'withdrawal',
    asset: 'ETH',
    amount: '0.5',
    value: '$1,771.09',
    status: 'pending',
    timestamp: '2 days ago',
    to: '0xabcd...efgh'
  }
];

export default function AssetsPage() {
  const [balanceVisible, setBalanceVisible] = useState(true);
  const [activeTab, setActiveTab] = useState('Overview');
  const [activeSubTab, setActiveSubTab] = useState('Spot');
  const [viewMode, setViewMode] = useState('Coin View');
  const [hideSmallAssets, setHideSmallAssets] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTimeRange, setSelectedTimeRange] = useState('1M');

  const mainTabs = ['Overview', 'Futures', 'Spot', 'Funding', 'Earn'];
  const subTabs = ['Spot', 'Cross Margin', 'Isolated Margin'];
  const timePeriods = ['1W', '1M', '3M', '6M', '1Y'];

  const totalPortfolioValue = mockAssets.reduce((sum, asset) => {
    const value = parseFloat(asset.usdValue.replace('$', '').replace(',', ''));
    return sum + value;
  }, 0);

  const totalPnL = mockAssets.reduce((sum, asset) => {
    const pnl = parseFloat(asset.todayPnl.replace('$', '').replace('+', '').replace('-', ''));
    return sum + (asset.isPositive ? pnl : -pnl);
  }, 0);

  const totalPnLPercentage = (totalPnL / totalPortfolioValue) * 100;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Wallet size={16} className="text-white" />
                </div>
                <h1 className="text-xl font-bold text-gray-900">Assets</h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
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

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {mainTabs.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Portfolio Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Balance Card */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">Portfolio Value</h2>
              <button 
                onClick={() => setBalanceVisible(!balanceVisible)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                {balanceVisible ? (
                  <Eye size={20} className="text-gray-600" />
                ) : (
                  <EyeOff size={20} className="text-gray-600" />
                )}
              </button>
            </div>

            <div className="mb-6">
              <div className="text-3xl font-bold text-gray-900 mb-2">
                ${balanceVisible ? totalPortfolioValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '****'}
              </div>
              <div className="flex items-center space-x-2 mb-4">
                <div className={`flex items-center ${totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {totalPnL >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                  <span className="text-lg font-semibold">
                    {totalPnL >= 0 ? '+' : ''}${balanceVisible ? Math.abs(totalPnL).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '****'}
                  </span>
                  <span className="text-sm">
                    ({totalPnL >= 0 ? '+' : ''}{balanceVisible ? totalPnLPercentage.toFixed(2) : '****'}%)
                  </span>
                </div>
                <span className="text-sm text-gray-500">24h</span>
              </div>

              {/* Time Period Tabs */}
              <div className="flex space-x-2">
                {timePeriods.map((period) => (
                  <button
                    key={period}
                    onClick={() => setSelectedTimeRange(period)}
                    className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                      selectedTimeRange === period
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    {period}
                  </button>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-3">
              <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors">
                <Plus size={16} />
                <span>Buy</span>
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg font-medium transition-colors">
                <Send size={16} />
                <span>Send</span>
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg font-medium transition-colors">
                <ArrowLeftRight size={16} />
                <span>Receive</span>
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg font-medium transition-colors">
                <Zap size={16} />
                <span>Swap</span>
              </button>
            </div>

            {/* Mini Chart */}
            <div className="mt-6 h-20 bg-gray-50 rounded-lg flex items-center justify-center">
              <Activity size={32} className="text-gray-400" />
            </div>
          </div>

          {/* Quick Actions */}
          <div className="space-y-4">
            {/* Small Amount Exchange */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                    <Star size={20} className="text-yellow-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">Small Amount Exchange</h3>
                    <p className="text-sm text-gray-500">Convert dust to BNB</p>
                  </div>
                </div>
                <button className="text-blue-600 text-sm font-medium flex items-center space-x-1">
                  <span>Convert</span>
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>

            {/* Earn */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <TrendingUp size={20} className="text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">Earn</h3>
                    <p className="text-sm text-gray-500">Up to 15% APY</p>
                  </div>
                </div>
                <button className="text-blue-600 text-sm font-medium flex items-center space-x-1">
                  <span>Start Earning</span>
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>

            {/* Rewards */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Gift size={20} className="text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">Rewards</h3>
                    <p className="text-sm text-gray-500">3 rewards available</p>
                  </div>
                </div>
                <button className="text-blue-600 text-sm font-medium flex items-center space-x-1">
                  <span>Claim</span>
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Assets Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {/* Assets Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">My Assets</h3>
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                  <input
                    type="text"
                    placeholder="Search assets..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 pr-4 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                  />
                </div>
                <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <Filter size={16} className="text-gray-600" />
                </button>
                <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <RefreshCw size={16} className="text-gray-600" />
                </button>
                <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <Download size={16} className="text-gray-600" />
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex space-x-4">
                <button
                  onClick={() => setViewMode('Coin View')}
                  className={`px-3 py-2 text-sm font-medium ${
                    viewMode === 'Coin View'
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Coin View
                </button>
                <button
                  onClick={() => setViewMode('Account View')}
                  className={`px-3 py-2 text-sm font-medium ${
                    viewMode === 'Account View'
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Account View
                </button>
              </div>

              <label className="flex items-center space-x-2 text-sm text-gray-600">
                <input
                  type="checkbox"
                  checked={hideSmallAssets}
                  onChange={(e) => setHideSmallAssets(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span>Hide assets &lt;1 USD</span>
              </label>
            </div>
          </div>

          {/* Assets List */}
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Asset
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Balance
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    24h Change
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Avg Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    PnL
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {mockAssets.map((asset) => (
                  <tr key={asset.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mr-3">
                          <span className="text-sm font-bold text-gray-700">
                            {asset.icon || asset.symbol.charAt(0)}
                          </span>
                        </div>
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {asset.symbol}
                          </div>
                          <div className="text-sm text-gray-500">
                            {asset.name}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {balanceVisible ? asset.balance : '****'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {balanceVisible ? asset.usdValue : '****'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`flex items-center text-sm ${
                        asset.change24h > 0 ? 'text-green-600' : 
                        asset.change24h < 0 ? 'text-red-600' : 'text-gray-600'
                      }`}>
                        {asset.change24h > 0 ? <TrendingUp size={14} /> : 
                         asset.change24h < 0 ? <TrendingDown size={14} /> : null}
                        <span>{asset.change24h > 0 ? '+' : ''}{asset.change24h}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {balanceVisible ? asset.avgPrice : '****'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`text-sm font-medium ${
                        asset.isPositive ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {balanceVisible ? asset.todayPnl : '****'}
                        <span className="text-xs font-normal ml-1">
                          ({balanceVisible ? asset.pnlPercentage : '****'})
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        <button className="px-3 py-1 bg-green-100 text-green-700 rounded text-xs font-medium hover:bg-green-200">
                          Earn
                        </button>
                        <button className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium hover:bg-blue-200">
                          Trade
                        </button>
                        <button className="p-1 text-gray-400 hover:text-gray-600">
                          <MoreHorizontal size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Recent Transactions</h3>
              <button className="text-blue-600 text-sm font-medium">
                View All →
              </button>
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {mockTransactions.map((transaction) => (
              <div key={transaction.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      transaction.type === 'deposit' ? 'bg-green-100' :
                      transaction.type === 'withdrawal' ? 'bg-red-100' :
                      transaction.type === 'trade' ? 'bg-blue-100' :
                      'bg-purple-100'
                    }`}>
                      {transaction.type === 'deposit' ? <ArrowDownRight size={20} className="text-green-600" /> :
                       transaction.type === 'withdrawal' ? <ArrowUpRight size={20} className="text-red-600" /> :
                       transaction.type === 'trade' ? <ArrowLeftRight size={20} className="text-blue-600" /> :
                       <TrendingUp size={20} className="text-purple-600" />}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900 capitalize">
                        {transaction.type} {transaction.asset}
                      </div>
                      <div className="text-sm text-gray-500">
                        {transaction.from && `From: ${transaction.from}`}
                        {transaction.to && `To: ${transaction.to}`}
                        {transaction.timestamp}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">
                      {transaction.amount} {transaction.asset}
                    </div>
                    <div className="text-sm text-gray-500">
                      {transaction.value}
                    </div>
                    <div className={`text-xs px-2 py-1 rounded-full inline-block mt-1 ${
                      transaction.status === 'completed' ? 'bg-green-100 text-green-800' :
                      transaction.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {transaction.status}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}