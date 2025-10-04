import React, { useState } from 'react';
import { ChevronDown, Settings, Info } from 'lucide-react';

interface TradingPanelProps {
  activeTab: string;
  pair: string;
}

const TradingPanel: React.FC<TradingPanelProps> = ({ activeTab, pair }) => {
  const [orderType, setOrderType] = useState('Limit');
  const [side, setSide] = useState<'Buy' | 'Sell'>('Buy');
  const [price, setPrice] = useState('122,866.48');
  const [amount, setAmount] = useState('');
  const [total, setTotal] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const orderTypes = ['Limit', 'Market', 'Stop Limit', 'OCO'];
  const percentages = [25, 50, 75, 100];

  const availableBalance = {
    buy: '0.00000000 USDT',
    sell: '0 BTC'
  };

  const handlePercentageClick = (percentage: number) => {
    // Calculate amount based on percentage of available balance
    const calculatedAmount = (percentage / 100).toString();
    setAmount(calculatedAmount);
  };

  const handlePlaceOrder = () => {
    console.log('Placing order:', {
      type: orderType,
      side,
      price,
      amount,
      total,
      pair
    });
    alert(`${side} order placed for ${amount} ${pair.split('/')[0]} at ${price}`);
  };

  return (
    <div className="bg-gray-800 text-white border-t border-gray-700">
      {/* Trading Tabs */}
      <div className="flex border-b border-gray-700">
        <button
          onClick={() => setSide('Buy')}
          className={`flex-1 py-3 text-sm font-medium ${
            side === 'Buy'
              ? 'text-green-500 border-b-2 border-green-500'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Buy
        </button>
        <button
          onClick={() => setSide('Sell')}
          className={`flex-1 py-3 text-sm font-medium ${
            side === 'Sell'
              ? 'text-red-500 border-b-2 border-red-500'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Sell
        </button>
      </div>

      <div className="p-4 space-y-4">
        {/* Order Type Selector */}
        <div className="flex space-x-1">
          {orderTypes.map((type) => (
            <button
              key={type}
              onClick={() => setOrderType(type)}
              className={`px-3 py-1 text-xs rounded ${
                orderType === type
                  ? 'bg-gray-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              {type}
            </button>
          ))}
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="px-2 py-1 text-xs text-gray-400 hover:text-white"
          >
            <ChevronDown className={`w-3 h-3 transform ${showAdvanced ? 'rotate-180' : ''}`} />
          </button>
        </div>

        {/* Available Balance */}
        <div className="text-xs text-gray-400">
          Available: {side === 'Buy' ? availableBalance.buy : availableBalance.sell}
        </div>

        {/* Price Input */}
        {orderType !== 'Market' && (
          <div className="space-y-2">
            <label className="text-xs text-gray-400">Price</label>
            <div className="relative">
              <input
                type="text"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-yellow-500"
              />
              <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-xs text-gray-400">
                USDT
              </span>
            </div>
          </div>
        )}

        {/* Amount Input */}
        <div className="space-y-2">
          <label className="text-xs text-gray-400">Amount</label>
          <div className="relative">
            <input
              type="text"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.00000000"
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-yellow-500"
            />
            <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-xs text-gray-400">
              BTC
            </span>
          </div>
        </div>

        {/* Percentage Buttons */}
        <div className="grid grid-cols-4 gap-2">
          {percentages.map((percentage) => (
            <button
              key={percentage}
              onClick={() => handlePercentageClick(percentage)}
              className="py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded text-gray-300"
            >
              {percentage}%
            </button>
          ))}
        </div>

        {/* Total */}
        <div className="space-y-2">
          <label className="text-xs text-gray-400">Total</label>
          <div className="relative">
            <input
              type="text"
              value={total}
              onChange={(e) => setTotal(e.target.value)}
              placeholder="0.00"
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-yellow-500"
            />
            <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-xs text-gray-400">
              USDT
            </span>
          </div>
        </div>

        {/* Advanced Options */}
        {showAdvanced && (
          <div className="space-y-3 pt-3 border-t border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">Post Only</span>
              <input type="checkbox" className="rounded" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">Reduce Only</span>
              <input type="checkbox" className="rounded" />
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1">
                <span className="text-xs text-gray-400">Time in Force</span>
                <Info className="w-3 h-3 text-gray-500" />
              </div>
              <select className="bg-gray-700 text-white text-xs px-2 py-1 rounded border border-gray-600">
                <option>GTC</option>
                <option>IOC</option>
                <option>FOK</option>
              </select>
            </div>
          </div>
        )}

        {/* Order Summary */}
        <div className="bg-gray-700 rounded p-3 space-y-2">
          <div className="text-xs text-gray-400">
            Now you can place Spot orders using assets in your Futures or Funding wallet by default. Click here to view all apps this setting.
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-gray-400">Max Buy:</span>
            <span className="text-white">0 BTC</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-gray-400">Est Fee:</span>
            <span className="text-white">0 USDT</span>
          </div>
        </div>

        {/* Place Order Button */}
        <button
          onClick={handlePlaceOrder}
          disabled={!amount}
          className={`w-full py-3 rounded font-medium transition-colors ${
            side === 'Buy'
              ? 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-red-600 hover:bg-red-700 text-white'
          } ${
            !amount ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {side} {pair.split('/')[0]}
        </button>

        {/* Fast Level */}
        <div className="text-center">
          <button className="text-xs text-gray-400 hover:text-white flex items-center justify-center space-x-1">
            <span>Fast Level</span>
            <Info className="w-3 h-3" />
          </button>
        </div>
      </div>

      {/* Open Orders */}
      <div className="border-t border-gray-700 p-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-medium">Open Orders(0)</h4>
          <button className="text-xs text-gray-400 hover:text-white">Hide Other Pairs</button>
        </div>
        <div className="text-center py-8 text-gray-500">
          <div className="text-xs">No open orders</div>
        </div>
      </div>

      {/* Order History Link */}
      <div className="border-t border-gray-700 p-4">
        <button className="text-xs text-gray-400 hover:text-white">
          Cancel All
        </button>
      </div>
    </div>
  );
};

export default TradingPanel;