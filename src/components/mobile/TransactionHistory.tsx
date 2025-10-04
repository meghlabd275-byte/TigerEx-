import React, { useState } from 'react';
import { Filter, Download, ChevronDown } from 'lucide-react';

interface Transaction {
  id: string;
  type: 'Funding Fee' | 'Commission' | 'Transfer' | 'Trade';
  symbol: string;
  amount: string;
  timestamp: string;
  status: 'Completed' | 'Pending' | 'Failed';
}

interface TransactionHistoryProps {
  onNavigate: (section: string) => void;
}

const TransactionHistory: React.FC<TransactionHistoryProps> = ({ onNavigate }) => {
  const [activeTab, setActiveTab] = useState<'Order History' | 'Position History' | 'Trade History' | 'Transaction History' | 'Funding Fee'>('Transaction History');
  const [selectedAsset, setSelectedAsset] = useState('All');
  const [selectedType, setSelectedType] = useState('All');

  const tabs = ['Order History', 'Position History', 'Trade History', 'Transaction History', 'Funding Fee'];

  const transactions: Transaction[] = [
    {
      id: '1',
      type: 'Funding Fee',
      symbol: 'ETHUSDT Perpetual',
      amount: '-0.17010258',
      timestamp: '2025-10-04 06:00:00',
      status: 'Completed'
    },
    {
      id: '2',
      type: 'Funding Fee',
      symbol: 'ETHUSDT Perpetual',
      amount: '-0.17163573',
      timestamp: '2025-10-03 22:00:00',
      status: 'Completed'
    },
    {
      id: '3',
      type: 'Funding Fee',
      symbol: 'ETHUSDT Perpetual',
      amount: '-0.2395757',
      timestamp: '2025-10-03 14:00:00',
      status: 'Completed'
    },
    {
      id: '4',
      type: 'Funding Fee',
      symbol: 'ETHUSDT Perpetual',
      amount: '-0.03980753',
      timestamp: '2025-10-03 06:00:00',
      status: 'Completed'
    },
    {
      id: '5',
      type: 'Commission',
      symbol: 'ETHUSDT Perpetual',
      amount: '-1.51534264',
      timestamp: '2025-10-03 02:32:02',
      status: 'Completed'
    }
  ];

  const getAmountColor = (amount: string) => {
    if (amount.startsWith('-')) {
      return 'text-red-500';
    } else if (amount.startsWith('+')) {
      return 'text-green-500';
    }
    return 'text-gray-900';
  };

  return (
    <div className="bg-white min-h-screen">
      {/* Header */}
      <div className="border-b border-gray-200">
        <div className="flex items-center justify-between p-4">
          <h1 className="text-lg font-semibold text-gray-900">My Trades</h1>
          <div className="flex items-center space-x-2">
            <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
              <Download className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Tabs */}
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

      {/* Filters */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-2 px-3 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
            <span className="text-sm text-gray-700">Asset</span>
            <ChevronDown className="w-4 h-4 text-gray-500" />
          </button>
          <button className="flex items-center space-x-2 px-3 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
            <span className="text-sm text-gray-700">Type</span>
            <ChevronDown className="w-4 h-4 text-gray-500" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Filter className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>

      {/* Transaction List */}
      <div className="divide-y divide-gray-100">
        {transactions.map((transaction) => (
          <div key={transaction.id} className="p-4 hover:bg-gray-50 transition-colors">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-lg font-bold text-gray-900">USDT</span>
                <span className="text-sm text-gray-500">{transaction.timestamp}</span>
              </div>
            </div>
            
            <div className="space-y-1">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Type</span>
                <span className="text-sm font-medium text-gray-900">{transaction.type}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Symbol</span>
                <span className="text-sm font-medium text-gray-900">{transaction.symbol}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Amount</span>
                <span className={`text-sm font-medium ${getAmountColor(transaction.amount)}`}>
                  {transaction.amount}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {transactions.length === 0 && (
        <div className="p-8 text-center">
          <div className="text-gray-400 mb-2">No transactions found</div>
          <div className="text-sm text-gray-500">
            Your transaction history will appear here
          </div>
        </div>
      )}

      {/* Load More */}
      {transactions.length > 0 && (
        <div className="p-4 text-center">
          <button className="text-yellow-600 font-medium text-sm hover:text-yellow-700 transition-colors">
            Load More
          </button>
        </div>
      )}
    </div>
  );
};

export default TransactionHistory;