import React, { useState } from 'react';
import { 
  Eye, 
  EyeOff, 
  Plus, 
  Send, 
  ArrowUpDown, 
  Search, 
  HelpCircle,
  TrendingUp,
  Coins
} from 'lucide-react';

interface AssetsOverviewProps {
  onNavigate: (section: string, data?: any) => void;
}

const AssetsOverview: React.FC<AssetsOverviewProps> = ({ onNavigate }) => {
  const [showBalance, setShowBalance] = useState(false);
  const [activeTab, setActiveTab] = useState<'Overview' | 'Futures' | 'Spot' | 'Funding' | 'Earn'>('Overview');
  const [activeSubTab, setActiveSubTab] = useState<'Spot' | 'Cross Margin' | 'Isolated Margin'>('Spot');

  const totalValue = "******";
  const todaysPnl = "******";

  const balances = [
    {
      symbol: 'FUN',
      name: 'FunToken',
      balance: showBalance ? '0.00000000' : '******',
      todaysPnl: showBalance ? '0.0000' : '******',
      averagePrice: showBalance ? '0.0000' : '******',
      icon: '🎮'
    }
  ];

  const tabs = ['Overview', 'Futures', 'Spot', 'Funding', 'Earn'];
  const subTabs = ['Spot', 'Cross Margin', 'Isolated Margin'];

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Header Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="flex overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`px-4 py-3 text-sm font-medium whitespace-nowrap ${
                activeTab === tab
                  ? 'text-gray-900 border-b-2 border-yellow-500'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Sub Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="flex px-4">
          {subTabs.map((subTab) => (
            <button
              key={subTab}
              onClick={() => setActiveSubTab(subTab as any)}
              className={`px-3 py-2 text-sm font-medium ${
                activeSubTab === subTab
                  ? 'text-gray-900 border-b-2 border-yellow-500'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {subTab}
            </button>
          ))}
        </div>
      </div>

      {/* Balance Overview */}
      <div className="bg-white p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Est. Total Value</span>
              <button
                onClick={() => setShowBalance(!showBalance)}
                className="p-1"
              >
                {showBalance ? (
                  <Eye className="w-4 h-4 text-gray-400" />
                ) : (
                  <EyeOff className="w-4 h-4 text-gray-400" />
                )}
              </button>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-2xl font-bold text-gray-900">
                {showBalance ? totalValue : "******"}
              </span>
              <span className="text-sm text-gray-600">USDT</span>
              <button className="p-1">
                <ArrowUpDown className="w-4 h-4 text-gray-400" />
              </button>
            </div>
          </div>
          <button className="p-2 bg-gray-100 rounded-full">
            <HelpCircle className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        <div className="flex items-center space-x-2 mb-4">
          <span className="text-sm text-gray-600">Today's PNL</span>
          <span className="text-sm font-medium text-gray-900">
            {showBalance ? todaysPnl : "******"}
          </span>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-3">
          <button
            onClick={() => onNavigate('add-funds')}
            className="flex-1 bg-yellow-500 text-white py-3 rounded-lg font-medium flex items-center justify-center space-x-2 hover:bg-yellow-600 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Funds</span>
          </button>
          <button
            onClick={() => onNavigate('send')}
            className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg font-medium flex items-center justify-center space-x-2 hover:bg-gray-300 transition-colors"
          >
            <Send className="w-4 h-4" />
            <span>Send</span>
          </button>
          <button
            onClick={() => onNavigate('transfer')}
            className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg font-medium flex items-center justify-center space-x-2 hover:bg-gray-300 transition-colors"
          >
            <ArrowUpDown className="w-4 h-4" />
            <span>Transfer</span>
          </button>
        </div>

        {/* Small Amount Exchange */}
        <button
          onClick={() => onNavigate('small-amount-exchange')}
          className="w-full mt-3 py-2 text-sm text-gray-600 flex items-center justify-center space-x-2 hover:bg-gray-50 rounded-lg transition-colors"
        >
          <Coins className="w-4 h-4" />
          <span>Small Amount Exchange</span>
        </button>
      </div>

      {/* Balances Section */}
      <div className="bg-white">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h3 className="font-medium text-gray-900">Balances</h3>
          <div className="flex items-center space-x-2">
            <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
              <Search className="w-4 h-4 text-gray-600" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
              <HelpCircle className="w-4 h-4 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Balance List */}
        <div className="divide-y divide-gray-100">
          {balances.map((balance, index) => (
            <div key={index} className="p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-pink-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-bold">FUN</span>
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{balance.symbol}</div>
                    <div className="text-sm text-gray-500">{balance.name}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium text-gray-900">{balance.balance}</div>
                  <div className="text-sm text-gray-500">
                    Today's PNL: {balance.todaysPnl}
                  </div>
                  <div className="text-sm text-gray-500">
                    Average Price: {balance.averagePrice}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State Message */}
        {balances.length === 0 && (
          <div className="p-8 text-center">
            <div className="text-gray-400 mb-2">No assets found</div>
            <button
              onClick={() => onNavigate('add-funds')}
              className="text-yellow-600 font-medium"
            >
              Add funds to get started
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AssetsOverview;