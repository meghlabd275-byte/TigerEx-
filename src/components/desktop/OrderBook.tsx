import React, { useState } from 'react';
import { Settings, MoreHorizontal } from 'lucide-react';

const OrderBook: React.FC = () => {
  const [precision, setPrecision] = useState('0.01');
  
  // Mock order book data
  const sellOrders = [
    { price: '122,897.76', amount: '0.01363', total: '73.72200' },
    { price: '122,895.84', amount: '0.00020', total: '73.72089' },
    { price: '122,893.94', amount: '0.00044', total: '103.21074' },
    { price: '122,891.61', amount: '0.00015', total: '18.43344' },
    { price: '122,889.91', amount: '0.00016', total: '19.66238' },
    { price: '122,889.00', amount: '0.00066', total: '11.09421' },
    { price: '122,887.76', amount: '0.00029', total: '12.39900' }
  ];

  const buyOrders = [
    { price: '122,886.99', amount: '6.56199', total: '1.084' },
    { price: '122,886.99', amount: '0.00010', total: '12.28869' },
    { price: '122,885.50', amount: '0.00020', total: '11.06420' },
    { price: '122,887.76', amount: '0.00017', total: '12.28977' },
    { price: '122,887.76', amount: '0.06207', total: '338.17M' },
    { price: '122,887.76', amount: '0.00010', total: '36.86023' }
  ];

  const currentPrice = '122,887.76';
  const priceChange = '+2,887.76';

  return (
    <div className="bg-gray-800 text-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <h3 className="text-sm font-medium">Order Book</h3>
        <div className="flex items-center space-x-2">
          <select 
            value={precision}
            onChange={(e) => setPrecision(e.target.value)}
            className="bg-gray-700 text-white text-xs px-2 py-1 rounded border border-gray-600"
          >
            <option value="0.01">0.01</option>
            <option value="0.1">0.1</option>
            <option value="1">1</option>
            <option value="10">10</option>
          </select>
          <button className="p-1 text-gray-400 hover:text-white">
            <Settings className="w-4 h-4" />
          </button>
          <button className="p-1 text-gray-400 hover:text-white">
            <MoreHorizontal className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Column Headers */}
      <div className="grid grid-cols-3 gap-2 px-4 py-2 text-xs text-gray-400 border-b border-gray-700">
        <div className="text-left">Price (USDT)</div>
        <div className="text-right">Amount (BTC)</div>
        <div className="text-right">Total</div>
      </div>

      {/* Sell Orders */}
      <div className="max-h-48 overflow-y-auto">
        {sellOrders.map((order, index) => (
          <div 
            key={index} 
            className="grid grid-cols-3 gap-2 px-4 py-1 text-xs hover:bg-gray-700 cursor-pointer relative"
          >
            {/* Background bar for volume visualization */}
            <div 
              className="absolute right-0 top-0 bottom-0 bg-red-900 opacity-20"
              style={{ width: `${Math.random() * 60 + 10}%` }}
            />
            <div className="text-red-500 relative z-10">{order.price}</div>
            <div className="text-white text-right relative z-10">{order.amount}</div>
            <div className="text-gray-400 text-right relative z-10">{order.total}</div>
          </div>
        ))}
      </div>

      {/* Current Price */}
      <div className="px-4 py-3 bg-gray-750 border-y border-gray-700">
        <div className="flex items-center justify-between">
          <div className="text-red-500 font-bold text-lg">{currentPrice}</div>
          <div className="text-red-500 text-sm">{priceChange}</div>
        </div>
        <div className="text-xs text-gray-400 mt-1">≈ $122,887.76</div>
      </div>

      {/* Buy Orders */}
      <div className="max-h-48 overflow-y-auto">
        {buyOrders.map((order, index) => (
          <div 
            key={index} 
            className="grid grid-cols-3 gap-2 px-4 py-1 text-xs hover:bg-gray-700 cursor-pointer relative"
          >
            {/* Background bar for volume visualization */}
            <div 
              className="absolute right-0 top-0 bottom-0 bg-green-900 opacity-20"
              style={{ width: `${Math.random() * 60 + 10}%` }}
            />
            <div className="text-green-500 relative z-10">{order.price}</div>
            <div className="text-white text-right relative z-10">{order.amount}</div>
            <div className="text-gray-400 text-right relative z-10">{order.total}</div>
          </div>
        ))}
      </div>

      {/* Order Book Summary */}
      <div className="p-4 border-t border-gray-700">
        <div className="grid grid-cols-2 gap-4 text-xs">
          <div>
            <div className="text-gray-400 mb-1">Sum (BTC)</div>
            <div className="text-green-500">847.438</div>
          </div>
          <div>
            <div className="text-gray-400 mb-1">Sum (BTC)</div>
            <div className="text-red-500">1,247.892</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderBook;