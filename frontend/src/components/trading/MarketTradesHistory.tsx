import React, { useState } from 'react';
import { Clock } from 'lucide-react';

interface Trade {
  price: number;
  amount: number;
  time: string;
  side: 'buy' | 'sell';
}

const MarketTradesHistory: React.FC = () => {
  const [trades] = useState<Trade[]>([
    { price: 120406.79, amount: 0.0007, time: '19:47:27', side: 'buy' },
    { price: 120406.80, amount: 0.0050, time: '19:47:27', side: 'sell' },
    { price: 120406.80, amount: 0.0290, time: '19:47:27', side: 'sell' },
    { price: 120406.80, amount: 0.0023, time: '19:47:27', side: 'sell' },
    { price: 120406.79, amount: 0.0401, time: '19:47:26', side: 'buy' },
    { price: 120406.79, amount: 0.0320, time: '19:47:26', side: 'buy' },
    { price: 120404.19, amount: 0.0005, time: '19:47:25', side: 'sell' },
    { price: 120404.53, amount: 0.0005, time: '19:47:24', side: 'buy' },
    { price: 120404.53, amount: 0.0023, time: '19:47:24', side: 'buy' },
    { price: 120404.64, amount: 0.0010, time: '19:47:23', side: 'buy' },
  ]);

  return (
    <div className="bg-gray-900 text-white h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <h3 className="font-semibold">Market Trades</h3>
        <Clock className="w-4 h-4 text-gray-400" />
      </div>

      {/* Column Headers */}
      <div className="flex justify-between px-4 py-2 text-xs text-gray-400 border-b border-gray-800">
        <span>Price (USDT)</span>
        <span>Amount (BTC)</span>
        <span className="text-right">Time</span>
      </div>

      {/* Trades List */}
      <div className="flex-1 overflow-y-auto">
        {trades.map((trade, index) => (
          <div
            key={index}
            className="flex justify-between px-4 py-1.5 hover:bg-gray-800/50 cursor-pointer"
          >
            <span
              className={`font-mono text-sm ${
                trade.side === 'buy' ? 'text-green-500' : 'text-red-500'
              }`}
            >
              {trade.price.toFixed(2)}
            </span>
            <span className="font-mono text-sm text-gray-300">
              {trade.amount.toFixed(4)}
            </span>
            <span className="font-mono text-xs text-gray-400 text-right">
              {trade.time}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MarketTradesHistory;