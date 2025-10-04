import React, { useState } from 'react';
import { ChevronDown, BarChart3, Settings, TrendingUp, TrendingDown } from 'lucide-react';

interface FuturesTradingProps {
  onPlaceOrder: (order: any) => void;
}

const FuturesTrading: React.FC<FuturesTradingProps> = ({ onPlaceOrder }) => {
  const [selectedPair, setSelectedPair] = useState('BTCUSDT');
  const [orderType, setOrderType] = useState<'Long' | 'Short'>('Long');
  const [marginType, setMarginType] = useState('Cross');
  const [leverage, setLeverage] = useState('10x');
  const [price, setPrice] = useState('123,650.00');
  const [quantity, setQuantity] = useState('0.001');
  const [orderMode, setOrderMode] = useState('Limit');

  const marketData = {
    price: '123,650.00',
    change: '+3.22%',
    isPositive: true,
    fundingRate: '0.010%',
    countdown: '07:21:24'
  };

  const orderBook = [
    { price: '123,660.50', quantity: '0.001' },
    { price: '123,660.00', quantity: '0.003' },
    { price: '123,658.50', quantity: '0.002' },
    { price: '123,657.60', quantity: '0.183' },
    { price: '123,656.60', quantity: '0.001' },
    { price: '123,656.50', quantity: '0.001' },
    { price: '123,654.80', quantity: '0.002' }
  ];

  const handlePlaceOrder = () => {
    const order = {
      pair: selectedPair,
      type: orderType,
      marginType,
      leverage,
      price: parseFloat(price.replace(',', '')),
      quantity: parseFloat(quantity),
      orderMode
    };
    onPlaceOrder(order);
  };

  return (
    <div className="bg-black text-white min-h-screen">
      {/* Top Navigation */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800">
        <div className="flex items-center space-x-4">
          <span className="text-orange-500 font-medium">Convert</span>
          <span className="text-gray-400">Spot</span>
          <span className="text-white font-medium border-b-2 border-yellow-500 pb-1">Futures</span>
          <span className="text-gray-400">Options</span>
          <span className="text-gray-400">TradFi</span>
        </div>
      </div>

      {/* Market Header */}
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-bold">{selectedPair}</h1>
            <ChevronDown className="w-4 h-4 text-gray-400" />
            <span className={`text-sm ${marketData.isPositive ? 'text-green-500' : 'text-red-500'}`}>
              {marketData.change}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xs bg-gray-800 px-2 py-1 rounded">MM</span>
            <span className="text-xs text-gray-400">{marketData.fundingRate}</span>
            <BarChart3 className="w-4 h-4 text-gray-400" />
            <Settings className="w-4 h-4 text-gray-400" />
          </div>
        </div>
        
        <div className="flex items-center justify-between text-xs text-gray-400">
          <div>
            <span>Funding Rate / Countdown</span>
            <div>{marketData.fundingRate} / {marketData.countdown}</div>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Left Side - Trading Form */}
        <div className="flex-1 p-4">
          {/* Margin and Leverage */}
          <div className="flex items-center space-x-4 mb-4">
            <button className="flex items-center space-x-1 bg-gray-800 px-3 py-1 rounded">
              <span className="text-sm">{marginType}</span>
              <ChevronDown className="w-3 h-3" />
            </button>
            <button className="flex items-center space-x-1 bg-gray-800 px-3 py-1 rounded">
              <span className="text-sm">{leverage}</span>
              <ChevronDown className="w-3 h-3" />
            </button>
          </div>

          {/* Available Balance */}
          <div className="mb-4">
            <div className="text-xs text-gray-400 mb-1">Available</div>
            <div className="text-sm">0.0000 USDT</div>
          </div>

          {/* Order Type Selector */}
          <div className="flex items-center space-x-2 mb-4">
            <button className="flex items-center space-x-1 bg-gray-800 px-3 py-1 rounded">
              <span className="text-sm">{orderMode}</span>
              <ChevronDown className="w-3 h-3" />
            </button>
          </div>

          {/* Price Input */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Price</span>
              <span className="text-sm text-white">USDT</span>
            </div>
            <input
              type="text"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
            />
          </div>

          {/* Quantity Input */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Quantity</span>
              <span className="text-sm text-white">BTC</span>
            </div>
            <input
              type="text"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
            />
          </div>

          {/* Quantity Slider */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-gray-400">Value</span>
              <span className="text-xs text-white">0/0 USDT</span>
            </div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-gray-400">Cost</span>
              <span className="text-xs text-white">0/0 USDT</span>
            </div>
            <div className="text-xs text-gray-400 mb-2">Liq. Price</div>
            <div className="relative">
              <input
                type="range"
                min="0"
                max="100"
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0</span>
                <span>25</span>
                <span>50</span>
                <span>75</span>
                <span>100</span>
              </div>
            </div>
          </div>

          {/* Order Options */}
          <div className="space-y-2 mb-6">
            <label className="flex items-center space-x-2">
              <input type="checkbox" className="rounded" />
              <span className="text-sm text-gray-300">TP/SL</span>
            </label>
            <label className="flex items-center space-x-2">
              <input type="checkbox" className="rounded" />
              <span className="text-sm text-gray-300">Post-Only</span>
            </label>
            <label className="flex items-center space-x-2">
              <input type="checkbox" className="rounded" />
              <span className="text-sm text-gray-300">Reduce-Only</span>
            </label>
          </div>

          {/* Order Buttons */}
          <div className="space-y-3">
            <button
              onClick={() => {
                setOrderType('Long');
                handlePlaceOrder();
              }}
              className="w-full bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg font-medium transition-colors"
            >
              Long
            </button>
            <button
              onClick={() => {
                setOrderType('Short');
                handlePlaceOrder();
              }}
              className="w-full bg-red-600 hover:bg-red-700 text-white py-3 rounded-lg font-medium transition-colors"
            >
              Short
            </button>
          </div>
        </div>

        {/* Right Side - Order Book */}
        <div className="w-48 border-l border-gray-800 p-2">
          <div className="text-xs text-gray-400 mb-2 flex justify-between">
            <span>Price (USDT)</span>
            <span>Quantity (BTC)</span>
          </div>
          
          {/* Sell Orders */}
          <div className="space-y-1 mb-2">
            {orderBook.slice(0, 4).map((order, index) => (
              <div key={index} className="flex justify-between text-xs">
                <span className="text-red-500">{order.price}</span>
                <span className="text-gray-300">{order.quantity}</span>
              </div>
            ))}
          </div>

          {/* Current Price */}
          <div className="text-center py-2 border-y border-gray-700 mb-2">
            <div className="text-red-500 font-bold text-sm">{marketData.price}</div>
            <div className="text-xs text-gray-400">123,657.23</div>
          </div>

          {/* Buy Orders */}
          <div className="space-y-1">
            {orderBook.slice(4).map((order, index) => (
              <div key={index} className="flex justify-between text-xs">
                <span className="text-green-500">{order.price}</span>
                <span className="text-gray-300">{order.quantity}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Tabs */}
      <div className="border-t border-gray-800 p-4">
        <div className="flex justify-between text-xs">
          <button className="text-white border-b border-white pb-1">Orders(0)</button>
          <button className="text-gray-400">Positions(0)</button>
          <button className="text-gray-400">Assets</button>
          <button className="text-gray-400">Borrowings(0)</button>
          <button className="text-gray-400">Tools(0)</button>
        </div>
      </div>
    </div>
  );
};

export default FuturesTrading;