'use client';

import React, { useState } from 'react';
import { 
  Settings, 
  DollarSign, 
  Zap, 
  Shield, 
  Globe, 
  Clock, 
  AlertCircle, 
  CheckCircle, 
  Info, 
  TrendingUp, 
  TrendingDown, 
  RefreshCw, 
  Save, 
  Eye, 
  EyeOff, 
  Calculator, 
  Activity, 
  Users, 
  BarChart3,
  ChevronRight,
  ChevronDown,
  Edit,
  Trash2,
  Plus,
  Copy,
  ExternalLink
} from 'lucide-react';

interface FeeTier {
  level: string;
  tradingVolume30d: string;
  makerFee: string;
  takerFee: string;
  futuresMakerFee: string;
  futuresTakerFee: string;
}

interface TradingPair {
  symbol: string;
  name: string;
  makerFee: string;
  takerFee: string;
  status: 'active' | 'inactive' | 'maintenance';
}

interface NetworkFee {
  network: string;
  asset: string;
  depositFee: string;
  withdrawFee: string;
  minWithdrawal: string;
  estimatedTime: string;
}

const feeTiers: FeeTier[] = [
  {
    level: 'VIP 0',
    tradingVolume30d: '< 50 BTC',
    makerFee: '0.10%',
    takerFee: '0.10%',
    futuresMakerFee: '0.02%',
    futuresTakerFee: '0.04%'
  },
  {
    level: 'VIP 1',
    tradingVolume30d: '≥ 50 BTC',
    makerFee: '0.08%',
    takerFee: '0.10%',
    futuresMakerFee: '0.015%',
    futuresTakerFee: '0.03%'
  },
  {
    level: 'VIP 2',
    tradingVolume30d: '≥ 250 BTC',
    makerFee: '0.06%',
    takerFee: '0.08%',
    futuresMakerFee: '0.01%',
    futuresTakerFee: '0.025%'
  },
  {
    level: 'VIP 3',
    tradingVolume30d: '≥ 1000 BTC',
    makerFee: '0.04%',
    takerFee: '0.06%',
    futuresMakerFee: '0.005%',
    futuresTakerFee: '0.02%'
  },
  {
    level: 'VIP 4',
    tradingVolume30d: '≥ 5000 BTC',
    makerFee: '0.02%',
    takerFee: '0.04%',
    futuresMakerFee: '0%',
    futuresTakerFee: '0.015%'
  },
  {
    level: 'VIP 5',
    tradingVolume30d: '≥ 10000 BTC',
    makerFee: '0%',
    takerFee: '0.02%',
    futuresMakerFee: '0%',
    futuresTakerFee: '0.01%'
  }
];

const tradingPairs: TradingPair[] = [
  { symbol: 'BTC/USDT', name: 'Bitcoin', makerFee: '0.10%', takerFee: '0.10%', status: 'active' },
  { symbol: 'ETH/USDT', name: 'Ethereum', makerFee: '0.10%', takerFee: '0.10%', status: 'active' },
  { symbol: 'BNB/USDT', name: 'Binance Coin', makerFee: '0.10%', takerFee: '0.10%', status: 'active' },
  { symbol: 'SOL/USDT', name: 'Solana', makerFee: '0.10%', takerFee: '0.10%', status: 'active' },
  { symbol: 'ADA/USDT', name: 'Cardano', makerFee: '0.10%', takerFee: '0.10%', status: 'maintenance' },
  { symbol: 'XRP/USDT', name: 'Ripple', makerFee: '0.10%', takerFee: '0.10%', status: 'inactive' }
];

const networkFees: NetworkFee[] = [
  { network: 'Bitcoin', asset: 'BTC', depositFee: '0 BTC', withdrawFee: '0.0005 BTC', minWithdrawal: '0.001 BTC', estimatedTime: '~30 minutes' },
  { network: 'Ethereum', asset: 'ETH', depositFee: '0 ETH', withdrawFee: '0.005 ETH', minWithdrawal: '0.01 ETH', estimatedTime: '~5 minutes' },
  { network: 'BNB Smart Chain', asset: 'BNB', depositFee: '0 BNB', withdrawFee: '0.001 BNB', minWithdrawal: '0.002 BNB', estimatedTime: '~2 minutes' },
  { network: 'Solana', asset: 'SOL', depositFee: '0 SOL', withdrawFee: '0.005 SOL', minWithdrawal: '0.01 SOL', estimatedTime: '~1 minute' },
  { network: 'Tron', asset: 'TRX', depositFee: '1 TRX', withdrawFee: '1 TRX', minWithdrawal: '1 TRX', estimatedTime: '~1 minute' },
  { network: 'Polygon', asset: 'MATIC', depositFee: '0 MATIC', withdrawFee: '10 MATIC', minWithdrawal: '20 MATIC', estimatedTime: '~2 minutes' }
];

export default function ExchangeSettingsPage() {
  const [activeTab, setActiveTab] = useState('fees');
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [selectedFeeType, setSelectedFeeType] = useState('spot');
  const [customFeeSettings, setCustomFeeSettings] = useState({
    defaultMakerFee: '0.10',
    defaultTakerFee: '0.10',
    futuresMakerFee: '0.02',
    futuresTakerFee: '0.04'
  });

  const tabs = [
    { id: 'fees', name: 'Trading Fees', icon: DollarSign },
    { id: 'network', name: 'Network Fees', icon: Globe },
    { id: 'limits', name: 'Limits', icon: Shield },
    { id: 'advanced', name: 'Advanced', icon: Settings }
  ];

  const feeTypes = ['spot', 'futures', 'margin', 'options'];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Settings size={16} className="text-white" />
                </div>
                <h1 className="text-xl font-bold text-gray-900">Exchange Settings</h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <RefreshCw size={20} className="text-gray-600" />
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors">
                <Save size={16} />
                <span>Save Changes</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon size={16} />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'fees' && (
          <div className="space-y-6">
            {/* Fee Type Selector */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Fee Configuration</h2>
              <div className="flex space-x-2 mb-6">
                {feeTypes.map((type) => (
                  <button
                    key={type}
                    onClick={() => setSelectedFeeType(type)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      selectedFeeType === type
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </button>
                ))}
              </div>

              {/* Custom Fee Settings */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Default Maker Fee (%)
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      value={customFeeSettings.defaultMakerFee}
                      onChange={(e) => setCustomFeeSettings(prev => ({ ...prev, defaultMakerFee: e.target.value }))}
                      step="0.01"
                      min="0"
                      max="1"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                    />
                    <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">%</span>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Default Taker Fee (%)
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      value={customFeeSettings.defaultTakerFee}
                      onChange={(e) => setCustomFeeSettings(prev => ({ ...prev, defaultTakerFee: e.target.value }))}
                      step="0.01"
                      min="0"
                      max="1"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                    />
                    <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* VIP Fee Tiers */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">VIP Fee Tiers</h3>
                  <button className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 text-sm font-medium">
                    <Plus size={16} />
                    <span>Add Tier</span>
                  </button>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        VIP Level
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        30-Day Trading Volume
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Maker Fee
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Taker Fee
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Futures Maker
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Futures Taker
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {feeTiers.map((tier, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${
                              index === 0 ? 'bg-gray-100' : 'bg-yellow-100'
                            }`}>
                              <span className={`text-sm font-bold ${
                                index === 0 ? 'text-gray-600' : 'text-yellow-600'
                              }`}>
                                {index === 0 ? '0' : index}
                              </span>
                            </div>
                            <span className="text-sm font-medium text-gray-900">{tier.level}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {tier.tradingVolume30d}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`text-sm font-medium ${
                            tier.makerFee === '0%' ? 'text-green-600' : 'text-gray-900'
                          }`}>
                            {tier.makerFee}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm font-medium text-gray-900">{tier.takerFee}</span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`text-sm font-medium ${
                            tier.futuresMakerFee === '0%' ? 'text-green-600' : 'text-gray-900'
                          }`}>
                            {tier.futuresMakerFee}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm font-medium text-gray-900">{tier.futuresTakerFee}</span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex items-center space-x-2">
                            <button className="text-blue-600 hover:text-blue-900">
                              <Edit size={16} />
                            </button>
                            {index > 0 && (
                              <button className="text-red-600 hover:text-red-900">
                                <Trash2 size={16} />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Trading Pair Fees */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Trading Pair Fees</h3>
                  <div className="flex items-center space-x-3">
                    <button className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 text-sm font-medium">
                      <Copy size={16} />
                      <span>Apply to All</span>
                    </button>
                    <button className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 text-sm font-medium">
                      <Plus size={16} />
                      <span>Add Pair</span>
                    </button>
                  </div>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Trading Pair
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Maker Fee
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Taker Fee
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {tradingPairs.map((pair) => (
                      <tr key={pair.symbol} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{pair.symbol}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {pair.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <input
                            type="text"
                            defaultValue={pair.makerFee}
                            className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                          />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <input
                            type="text"
                            defaultValue={pair.takerFee}
                            className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                          />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            pair.status === 'active' ? 'bg-green-100 text-green-800' :
                            pair.status === 'maintenance' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {pair.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex items-center space-x-2">
                            <button className="text-blue-600 hover:text-blue-900">
                              <Edit size={16} />
                            </button>
                            <button className="text-red-600 hover:text-red-900">
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'network' && (
          <div className="space-y-6">
            {/* Network Fees */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Network Fee Configuration</h3>
                  <button className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 text-sm font-medium">
                    <Plus size={16} />
                    <span>Add Network</span>
                  </button>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Network
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Asset
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Deposit Fee
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Withdrawal Fee
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Min Withdrawal
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Est. Time
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {networkFees.map((fee) => (
                      <tr key={fee.network} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{fee.network}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {fee.asset}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <input
                            type="text"
                            defaultValue={fee.depositFee}
                            className="w-24 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                          />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <input
                            type="text"
                            defaultValue={fee.withdrawFee}
                            className="w-24 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                          />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <input
                            type="text"
                            defaultValue={fee.minWithdrawal}
                            className="w-24 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                          />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {fee.estimatedTime}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex items-center space-x-2">
                            <button className="text-blue-600 hover:text-blue-900">
                              <Edit size={16} />
                            </button>
                            <button className="text-red-600 hover:text-red-900">
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Fee Calculator */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Fee Calculator</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Trade Amount (USDT)
                  </label>
                  <input
                    type="number"
                    placeholder="1000"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Trading Pair
                  </label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500">
                    <option>BTC/USDT</option>
                    <option>ETH/USDT</option>
                    <option>BNB/USDT</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Order Type
                  </label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500">
                    <option>Market</option>
                    <option>Limit</option>
                  </select>
                </div>
              </div>
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-gray-600">Maker Fee</div>
                    <div className="text-lg font-semibold text-gray-900">1.00 USDT</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Taker Fee</div>
                    <div className="text-lg font-semibold text-gray-900">1.00 USDT</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'limits' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Trading Limits</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Maximum Leverage
                    </label>
                    <input
                      type="number"
                      defaultValue="125"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Minimum Order Size (USDT)
                    </label>
                    <input
                      type="number"
                      defaultValue="10"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Maximum Order Size (USDT)
                    </label>
                    <input
                      type="number"
                      defaultValue="1000000"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Daily Withdrawal Limit (USDT)
                    </label>
                    <input
                      type="number"
                      defaultValue="100000"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'advanced' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Advanced Settings</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h4 className="font-medium text-gray-900">Enable API Trading</h4>
                    <p className="text-sm text-gray-600">Allow users to trade via API</p>
                  </div>
                  <button className="w-12 h-6 bg-blue-600 rounded-full relative">
                    <div className="w-5 h-5 bg-white rounded-full absolute top-0.5 right-0.5"></div>
                  </button>
                </div>
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h4 className="font-medium text-gray-900">Require KYC for Trading</h4>
                    <p className="text-sm text-gray-600">Only verified users can trade</p>
                  </div>
                  <button className="w-12 h-6 bg-blue-600 rounded-full relative">
                    <div className="w-5 h-5 bg-white rounded-full absolute top-0.5 right-0.5"></div>
                  </button>
                </div>
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h4 className="font-medium text-gray-900">Enable Margin Trading</h4>
                    <p className="text-sm text-gray-600">Allow users to trade with leverage</p>
                  </div>
                  <button className="w-12 h-6 bg-gray-300 rounded-full relative">
                    <div className="w-5 h-5 bg-white rounded-full absolute top-0.5 left-0.5"></div>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}