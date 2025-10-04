import React, { useState } from 'react';
import { 
  Calendar, 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Clock, 
  DollarSign,
  BarChart3,
  Settings,
  Info,
  ChevronDown
} from 'lucide-react';

const OptionsTrading: React.FC = () => {
  const [selectedUnderlying, setSelectedUnderlying] = useState('BTC');
  const [selectedExpiry, setSelectedExpiry] = useState('2024-12-27');
  const [optionType, setOptionType] = useState<'Call' | 'Put'>('Call');
  const [selectedStrike, setSelectedStrike] = useState('130000');
  const [quantity, setQuantity] = useState('1');
  const [orderType, setOrderType] = useState('Market');

  const underlyingAssets = ['BTC', 'ETH', 'BNB', 'SOL'];
  const expiryDates = [
    '2024-12-27', '2025-01-03', '2025-01-10', '2025-01-17', 
    '2025-01-24', '2025-01-31', '2025-02-07', '2025-02-14'
  ];

  const currentPrice = 122887.76;
  const impliedVolatility = 65.2;

  // Mock options chain data
  const optionsChain = [
    {
      strike: 120000,
      call: { bid: 4250.5, ask: 4280.2, last: 4265.8, volume: 125, oi: 1250, iv: 62.5, delta: 0.75, gamma: 0.0001, theta: -12.5, vega: 45.2 },
      put: { bid: 1320.1, ask: 1350.8, last: 1335.4, volume: 89, oi: 890, iv: 64.1, delta: -0.25, gamma: 0.0001, theta: -8.9, vega: 42.1 }
    },
    {
      strike: 122500,
      call: { bid: 3180.3, ask: 3210.7, last: 3195.5, volume: 234, oi: 2340, iv: 63.8, delta: 0.65, gamma: 0.0002, theta: -15.2, vega: 48.7 },
      put: { bid: 1810.2, ask: 1840.9, last: 1825.6, volume: 156, oi: 1560, iv: 65.4, delta: -0.35, gamma: 0.0002, theta: -11.3, vega: 46.8 }
    },
    {
      strike: 125000,
      call: { bid: 2250.8, ask: 2280.4, last: 2265.6, volume: 345, oi: 3450, iv: 65.1, delta: 0.52, gamma: 0.0003, theta: -18.7, vega: 52.3 },
      put: { bid: 2380.5, ask: 2410.2, last: 2395.8, volume: 278, oi: 2780, iv: 66.8, delta: -0.48, gamma: 0.0003, theta: -14.6, vega: 50.1 }
    },
    {
      strike: 127500,
      call: { bid: 1450.2, ask: 1480.9, last: 1465.5, volume: 189, oi: 1890, iv: 66.7, delta: 0.38, gamma: 0.0003, theta: -22.1, vega: 55.8 },
      put: { bid: 3080.7, ask: 3110.4, last: 3095.6, volume: 167, oi: 1670, iv: 68.2, delta: -0.62, gamma: 0.0003, theta: -17.9, vega: 53.4 }
    },
    {
      strike: 130000,
      call: { bid: 850.3, ask: 880.7, last: 865.5, volume: 456, oi: 4560, iv: 68.4, delta: 0.25, gamma: 0.0002, theta: -25.8, vega: 59.2 },
      put: { bid: 3950.1, ask: 3980.8, last: 3965.4, volume: 234, oi: 2340, iv: 69.9, delta: -0.75, gamma: 0.0002, theta: -21.3, vega: 56.7 }
    }
  ];

  const myPositions = [
    {
      option: 'BTC-241227-125000-C',
      type: 'Call',
      strike: 125000,
      expiry: '2024-12-27',
      quantity: 2,
      avgPrice: 2280.5,
      currentPrice: 2265.6,
      pnl: -29.8,
      pnlPercent: -0.65,
      delta: 1.04,
      gamma: 0.0006,
      theta: -37.4,
      vega: 104.6
    },
    {
      option: 'BTC-241227-130000-P',
      type: 'Put',
      strike: 130000,
      expiry: '2024-12-27',
      quantity: 1,
      avgPrice: 3890.2,
      currentPrice: 3965.4,
      pnl: 75.2,
      pnlPercent: 1.93,
      delta: -0.75,
      gamma: 0.0002,
      theta: -21.3,
      vega: 56.7
    }
  ];

  const handlePlaceOrder = () => {
    const selectedOption = optionsChain.find(o => o.strike.toString() === selectedStrike);
    if (!selectedOption) return;

    const option = optionType === 'Call' ? selectedOption.call : selectedOption.put;
    console.log('Placing options order:', {
      underlying: selectedUnderlying,
      expiry: selectedExpiry,
      strike: selectedStrike,
      type: optionType,
      quantity,
      orderType,
      price: option.ask
    });
    
    alert(`${optionType} option order placed: ${quantity} contracts at strike ${selectedStrike}`);
  };

  return (
    <div className="bg-gray-900 text-white min-h-screen">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">Options Trading</h1>
            <p className="text-gray-400">Trade Bitcoin and Ethereum options with advanced strategies</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-sm text-gray-400">BTC Price</div>
              <div className="text-xl font-bold text-green-500">${currentPrice.toLocaleString()}</div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-400">Implied Volatility</div>
              <div className="text-xl font-bold text-white">{impliedVolatility}%</div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Main Content */}
        <div className="flex-1">
          {/* Controls */}
          <div className="bg-gray-800 border-b border-gray-700 p-4">
            <div className="flex items-center space-x-6">
              {/* Underlying Asset */}
              <div className="flex items-center space-x-2">
                <span className="text-gray-400 text-sm">Underlying:</span>
                <select
                  value={selectedUnderlying}
                  onChange={(e) => setSelectedUnderlying(e.target.value)}
                  className="bg-gray-700 text-white px-3 py-1 rounded border border-gray-600"
                >
                  {underlyingAssets.map(asset => (
                    <option key={asset} value={asset}>{asset}</option>
                  ))}
                </select>
              </div>

              {/* Expiry Date */}
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-gray-400" />
                <span className="text-gray-400 text-sm">Expiry:</span>
                <select
                  value={selectedExpiry}
                  onChange={(e) => setSelectedExpiry(e.target.value)}
                  className="bg-gray-700 text-white px-3 py-1 rounded border border-gray-600"
                >
                  {expiryDates.map(date => (
                    <option key={date} value={date}>{date}</option>
                  ))}
                </select>
              </div>

              {/* Option Type */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setOptionType('Call')}
                  className={`px-3 py-1 rounded text-sm ${
                    optionType === 'Call'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  Calls
                </button>
                <button
                  onClick={() => setOptionType('Put')}
                  className={`px-3 py-1 rounded text-sm ${
                    optionType === 'Put'
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  Puts
                </button>
              </div>

              <button className="flex items-center space-x-1 text-gray-400 hover:text-white">
                <Settings className="w-4 h-4" />
                <span className="text-sm">Settings</span>
              </button>
            </div>
          </div>

          {/* Options Chain */}
          <div className="p-4">
            <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
              <div className="p-4 border-b border-gray-700">
                <h3 className="font-semibold text-white">Options Chain - {selectedExpiry}</h3>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-750">
                    <tr>
                      <th colSpan={6} className="px-4 py-2 text-center text-green-500 border-r border-gray-600">
                        CALLS
                      </th>
                      <th className="px-4 py-2 text-center text-white border-r border-gray-600">
                        STRIKE
                      </th>
                      <th colSpan={6} className="px-4 py-2 text-center text-red-500">
                        PUTS
                      </th>
                    </tr>
                    <tr className="text-xs text-gray-400">
                      <th className="px-2 py-2 text-left">Bid</th>
                      <th className="px-2 py-2 text-left">Ask</th>
                      <th className="px-2 py-2 text-left">Last</th>
                      <th className="px-2 py-2 text-left">Vol</th>
                      <th className="px-2 py-2 text-left">OI</th>
                      <th className="px-2 py-2 text-left border-r border-gray-600">IV</th>
                      <th className="px-2 py-2 text-center border-r border-gray-600">Price</th>
                      <th className="px-2 py-2 text-left">IV</th>
                      <th className="px-2 py-2 text-left">OI</th>
                      <th className="px-2 py-2 text-left">Vol</th>
                      <th className="px-2 py-2 text-left">Last</th>
                      <th className="px-2 py-2 text-left">Ask</th>
                      <th className="px-2 py-2 text-left">Bid</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {optionsChain.map((row, index) => (
                      <tr 
                        key={index} 
                        className={`hover:bg-gray-750 cursor-pointer ${
                          row.strike.toString() === selectedStrike ? 'bg-gray-700' : ''
                        }`}
                        onClick={() => setSelectedStrike(row.strike.toString())}
                      >
                        {/* Call Options */}
                        <td className="px-2 py-2 text-green-500 text-sm">{row.call.bid}</td>
                        <td className="px-2 py-2 text-green-500 text-sm">{row.call.ask}</td>
                        <td className="px-2 py-2 text-white text-sm">{row.call.last}</td>
                        <td className="px-2 py-2 text-gray-400 text-sm">{row.call.volume}</td>
                        <td className="px-2 py-2 text-gray-400 text-sm">{row.call.oi}</td>
                        <td className="px-2 py-2 text-gray-400 text-sm border-r border-gray-600">{row.call.iv}%</td>
                        
                        {/* Strike Price */}
                        <td className="px-2 py-2 text-center font-bold text-white border-r border-gray-600">
                          {row.strike.toLocaleString()}
                        </td>
                        
                        {/* Put Options */}
                        <td className="px-2 py-2 text-gray-400 text-sm">{row.put.iv}%</td>
                        <td className="px-2 py-2 text-gray-400 text-sm">{row.put.oi}</td>
                        <td className="px-2 py-2 text-gray-400 text-sm">{row.put.volume}</td>
                        <td className="px-2 py-2 text-white text-sm">{row.put.last}</td>
                        <td className="px-2 py-2 text-red-500 text-sm">{row.put.ask}</td>
                        <td className="px-2 py-2 text-red-500 text-sm">{row.put.bid}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* My Positions */}
          <div className="p-4">
            <div className="bg-gray-800 rounded-lg border border-gray-700">
              <div className="p-4 border-b border-gray-700">
                <h3 className="font-semibold text-white">My Positions</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-750">
                    <tr className="text-xs text-gray-400">
                      <th className="px-4 py-3 text-left">Option</th>
                      <th className="px-4 py-3 text-left">Type</th>
                      <th className="px-4 py-3 text-left">Quantity</th>
                      <th className="px-4 py-3 text-left">Avg Price</th>
                      <th className="px-4 py-3 text-left">Current Price</th>
                      <th className="px-4 py-3 text-left">PnL</th>
                      <th className="px-4 py-3 text-left">Delta</th>
                      <th className="px-4 py-3 text-left">Gamma</th>
                      <th className="px-4 py-3 text-left">Theta</th>
                      <th className="px-4 py-3 text-left">Vega</th>
                      <th className="px-4 py-3 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {myPositions.map((position, index) => (
                      <tr key={index} className="hover:bg-gray-750">
                        <td className="px-4 py-3 text-white font-mono text-sm">{position.option}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded text-xs ${
                            position.type === 'Call' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
                          }`}>
                            {position.type}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-white">{position.quantity}</td>
                        <td className="px-4 py-3 text-white">${position.avgPrice}</td>
                        <td className="px-4 py-3 text-white">${position.currentPrice}</td>
                        <td className="px-4 py-3">
                          <div className={position.pnl > 0 ? 'text-green-500' : 'text-red-500'}>
                            ${position.pnl}
                          </div>
                          <div className={`text-xs ${position.pnlPercent > 0 ? 'text-green-500' : 'text-red-500'}`}>
                            ({position.pnlPercent > 0 ? '+' : ''}{position.pnlPercent}%)
                          </div>
                        </td>
                        <td className="px-4 py-3 text-gray-400">{position.delta}</td>
                        <td className="px-4 py-3 text-gray-400">{position.gamma}</td>
                        <td className="px-4 py-3 text-gray-400">{position.theta}</td>
                        <td className="px-4 py-3 text-gray-400">{position.vega}</td>
                        <td className="px-4 py-3">
                          <div className="flex space-x-2">
                            <button className="text-yellow-500 hover:text-yellow-400 text-xs">Close</button>
                            <button className="text-blue-500 hover:text-blue-400 text-xs">Roll</button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel - Order Entry */}
        <div className="w-80 bg-gray-800 border-l border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="font-semibold text-white">Place Order</h3>
          </div>
          
          <div className="p-4 space-y-4">
            {/* Selected Option Info */}
            {selectedStrike && (
              <div className="bg-gray-700 rounded p-3">
                <div className="text-sm text-gray-400 mb-2">Selected Option</div>
                <div className="text-white font-mono text-sm">
                  {selectedUnderlying}-{selectedExpiry.replace(/-/g, '')}-{selectedStrike}-{optionType.charAt(0)}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  Strike: ${parseInt(selectedStrike).toLocaleString()}
                </div>
              </div>
            )}

            {/* Order Type */}
            <div className="space-y-2">
              <label className="text-sm text-gray-400">Order Type</label>
              <select
                value={orderType}
                onChange={(e) => setOrderType(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
              >
                <option value="Market">Market</option>
                <option value="Limit">Limit</option>
                <option value="Stop">Stop</option>
              </select>
            </div>

            {/* Quantity */}
            <div className="space-y-2">
              <label className="text-sm text-gray-400">Quantity (Contracts)</label>
              <input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                min="1"
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
              />
            </div>

            {/* Price (for limit orders) */}
            {orderType === 'Limit' && (
              <div className="space-y-2">
                <label className="text-sm text-gray-400">Limit Price</label>
                <input
                  type="number"
                  step="0.1"
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                  placeholder="Enter price"
                />
              </div>
            )}

            {/* Greeks Display */}
            {selectedStrike && (
              <div className="bg-gray-700 rounded p-3">
                <div className="text-sm text-gray-400 mb-2">Greeks</div>
                {(() => {
                  const option = optionsChain.find(o => o.strike.toString() === selectedStrike);
                  const greeks = option ? (optionType === 'Call' ? option.call : option.put) : null;
                  return greeks ? (
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>Delta: <span className="text-white">{greeks.delta}</span></div>
                      <div>Gamma: <span className="text-white">{greeks.gamma}</span></div>
                      <div>Theta: <span className="text-white">{greeks.theta}</span></div>
                      <div>Vega: <span className="text-white">{greeks.vega}</span></div>
                    </div>
                  ) : null;
                })()}
              </div>
            )}

            {/* Order Summary */}
            <div className="bg-gray-700 rounded p-3">
              <div className="text-sm text-gray-400 mb-2">Order Summary</div>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-400">Premium:</span>
                  <span className="text-white">$0.00</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Fees:</span>
                  <span className="text-white">$0.00</span>
                </div>
                <div className="flex justify-between border-t border-gray-600 pt-1">
                  <span className="text-gray-400">Total:</span>
                  <span className="text-white font-medium">$0.00</span>
                </div>
              </div>
            </div>

            {/* Place Order Buttons */}
            <div className="space-y-2">
              <button
                onClick={handlePlaceOrder}
                className={`w-full py-3 rounded font-medium transition-colors ${
                  optionType === 'Call'
                    ? 'bg-green-600 hover:bg-green-700 text-white'
                    : 'bg-red-600 hover:bg-red-700 text-white'
                }`}
              >
                Buy {optionType}
              </button>
              <button className="w-full py-2 bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors">
                Sell {optionType}
              </button>
            </div>

            {/* Risk Warning */}
            <div className="bg-yellow-900 border border-yellow-700 rounded p-3">
              <div className="flex items-start space-x-2">
                <Info className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                <div className="text-xs text-yellow-200">
                  Options trading involves substantial risk and is not suitable for all investors. 
                  Please ensure you understand the risks before trading.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OptionsTrading;