import React, { useState } from 'react';
import { Clock, TrendingUp, TrendingDown } from 'lucide-react';

const MarketTrades: React.FC = () => {
  const [activeTab, setActiveTab] = useState('Market Trades');

  // Mock market trades data
  const marketTrades = [
    { price: '122,887.76', amount: '0.01363', time: '22:55:14', side: 'sell' },
    { price: '122,887.77', amount: '0.00020', time: '22:55:14', side: 'buy' },
    { price: '122,887.76', amount: '0.00044', time: '22:55:14', side: 'sell' },
    { price: '122,887.77', amount: '0.00015', time: '22:55:14', side: 'buy' },
    { price: '122,887.00', amount: '0.00066', time: '22:55:14', side: 'sell' },
    { price: '122,886.07', amount: '0.00102', time: '22:55:14', side: 'buy' },
    { price: '122,885.01', amount: '0.00028', time: '22:55:14', side: 'sell' },
    { price: '122,884.40', amount: '0.00006', time: '22:55:14', side: 'buy' },
    { price: '122,884.17', amount: '0.00020', time: '22:55:14', side: 'sell' },
    { price: '122,883.61', amount: '0.00013', time: '22:55:14', side: 'buy' },
    { price: '122,882.08', amount: '0.00009', time: '22:55:14', side: 'sell' }
  ];

  const tabs = ['Market Trades', 'My Trades'];

  return (
    <div className="bg-gray-800 text-white">
      {/* Tabs */}
      <div className="flex border-b border-gray-700">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-3 text-sm font-medium ${
              activeTab === tab
                ? 'text-white border-b-2 border-yellow-500'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Column Headers */}
      <div className="grid grid-cols-3 gap-2 px-4 py-2 text-xs text-gray-400 border-b border-gray-700">
        <div className="text-left">Price (USDT)</div>
        <div className="text-right">Amount (BTC)</div>
        <div className="text-right">Time</div>
      </div>

      {/* Trades List */}
      <div className="max-h-64 overflow-y-auto">
        {marketTrades.map((trade, index) => (
          <div 
            key={index}
            className="grid grid-cols-3 gap-2 px-4 py-1 text-xs hover:bg-gray-700 cursor-pointer"
          >
            <div className={`${trade.side === 'buy' ? 'text-green-500' : 'text-red-500'}`}>
              {trade.price}
            </div>
            <div className="text-white text-right">{trade.amount}</div>
            <div className="text-gray-400 text-right">{trade.time}</div>
          </div>
        ))}
      </div>

      {/* Market Summary */}
      <div className="p-4 border-t border-gray-700">
        <div className="grid grid-cols-2 gap-4 text-xs">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-400">24h Volume:</span>
              <span className="text-white">24,892.35 BTC</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">24h High:</span>
              <span className="text-green-500">123,894.99</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-400">24h Low:</span>
              <span className="text-red-500">119,248.90</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">24h Change:</span>
              <span className="text-green-500">+2.29%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Trading Stats */}
      <div className="p-4 border-t border-gray-700 bg-gray-750">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <TrendingUp className="w-3 h-3 text-green-500" />
              <span className="text-gray-400">Buy Pressure:</span>
              <span className="text-green-500">67%</span>
            </div>
            <div className="flex items-center space-x-1">
              <TrendingDown className="w-3 h-3 text-red-500" />
              <span className="text-gray-400">Sell Pressure:</span>
              <span className="text-red-500">33%</span>
            </div>
          </div>
          <div className="flex items-center space-x-1">
            <Clock className="w-3 h-3 text-gray-400" />
            <span className="text-gray-400">Last Update: 22:55:14</span>
          </div>
        </div>
        
        {/* Pressure Bar */}
        <div className="mt-2 h-1 bg-gray-600 rounded overflow-hidden">
          <div className="h-full bg-gradient-to-r from-green-500 to-red-500" style={{ width: '67%' }} />
        </div>
      </div>
    </div>
  );
};

export default MarketTrades;