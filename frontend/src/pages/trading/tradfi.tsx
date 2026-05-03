/**
 * TigerEx Frontend Component
 * @file tradfi.tsx
 * @description React component for TigerEx exchange
 * @author TigerEx Development Team
 */

/**
 * TigerEx TradFi Trading Interface
 * Complete CFD, Forex, ETF, Derivatives Trading
 */

import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area, BarChart, Bar 
} from 'recharts';
import { 
  TrendingUp, TrendingDown, Activity, DollarSign, Globe, 
  BarChart2, Clock, Settings, Info, ArrowUp, ArrowDown,
  Shield, Zap, Layers, CreditCard, RefreshCw
} from 'lucide-react';

// TradFi Instrument Types
const INSTRUMENT_TYPES: Record<string, { name: string; color: string; description: string }> = {
  CFD: { name: 'CFD', color: '#f59e0b', description: 'Contract for Difference' },
  FOREX: { name: 'Forex', color: '#8b5cf6', description: 'Currency Trading' },
  ETF: { name: 'ETF', color: '#10b981', description: 'Exchange Traded Funds' },
  STOCK_TOKEN: { name: 'Stock Token', color: '#3b82f6', description: 'Tokenized Stocks' },
  DERIVATIVE: { name: 'Derivative', color: '#ec4899', description: 'Derivative Contracts' },
  OPTION: { name: 'Option', color: '#06b6d4', description: 'Options Trading' },
  FUTURE: { name: 'Future', color: '#f97316', description: 'Futures Trading' },
};

// Sample TradFi Instruments
const TRADFI_INSTRUMENTS = [
  { symbol: 'BTC/USD', name: 'Bitcoin', type: 'CFD', price: 42500.00, change: 2.34, leverage: 100 },
  { symbol: 'ETH/USD', name: 'Ethereum', type: 'CFD', price: 2280.00, change: 1.56, leverage: 50 },
  { symbol: 'EUR/USD', name: 'Euro/US Dollar', type: 'FOREX', price: 1.0845, change: 0.12, leverage: 30 },
  { symbol: 'GBP/USD', name: 'British Pound', type: 'FOREX', price: 1.2650, change: -0.08, leverage: 30 },
  { symbol: 'AAPL', name: 'Apple Inc', type: 'STOCK_TOKEN', price: 178.50, change: 1.23, leverage: 20 },
  { symbol: 'TSLA', name: 'Tesla Inc', type: 'STOCK_TOKEN', price: 245.20, change: -2.45, leverage: 20 },
  { symbol: 'SPY', name: 'S&P 500 ETF', type: 'ETF', price: 478.50, change: 0.45, leverage: 10 },
  { symbol: 'QQQ', name: 'Nasdaq ETF', type: 'ETF', price: 405.20, change: 0.78, leverage: 10 },
  { symbol: 'GLD', name: 'Gold ETF', type: 'ETF', price: 185.30, change: 0.34, leverage: 10 },
  { symbol: 'GOOGL', name: 'Alphabet', type: 'STOCK_TOKEN', price: 142.80, change: 0.89, leverage: 20 },
  { symbol: 'MSFT', name: 'Microsoft', type: 'STOCK_TOKEN', price: 378.50, change: 1.12, leverage: 20 },
  { symbol: 'NVDA', name: 'NVIDIA', type: 'STOCK_TOKEN', price: 545.80, change: 3.45, leverage: 20 },
  { symbol: 'META', name: 'Meta', type: 'STOCK_TOKEN', price: 378.20, change: 2.10, leverage: 20 },
  { symbol: 'AMZN', name: 'Amazon', type: 'STOCK_TOKEN', price: 155.30, change: 1.45, leverage: 20 },
  { symbol: 'XAU/USD', name: 'Gold', type: 'DERIVATIVE', price: 2025.50, change: 0.56, leverage: 100 },
  { symbol: 'XAG/USD', name: 'Silver', type: 'DERIVATIVE', price: 22.85, change: 1.23, leverage: 50 },
];

// Sample price history
const generatePriceHistory = (basePrice: number, volatility = 0.02) => {
  const data = [];
  let price = basePrice * (1 - volatility);
  for (let i = 0; i < 50; i++) {
    price = price * (1 + (Math.random() - 0.5) * volatility);
    data.push({ time: i, price });
  }
  return data;
};

export default function TradFiTrading() {
  const [selectedInstrument, setSelectedInstrument] = useState(TRADFI_INSTRUMENTS[0]);
  const [orderType, setOrderType] = useState('market');
  const [orderSide, setOrderSide] = useState('buy');
  const [quantity, setQuantity] = useState(1);
  const [leverage, setLeverage] = useState(1);
  const [stopLoss, setStopLoss] = useState('');
  const [takeProfit, setTakeProfit] = useState('');
  const [positions, setPositions] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState('trade');
  const [filterType, setFilterType] = useState('ALL');

  // Filter instruments
  const filteredInstruments = filterType === 'ALL' 
    ? TRADFI_INSTRUMENTS 
    : TRADFI_INSTRUMENTS.filter(i => i.type === filterType);

  // Calculate order value
  const orderValue = selectedInstrument.price * quantity * leverage;
  const estimatedMargin = orderValue / leverage;
  const fee = orderValue * 0.001; // 0.1% fee

  // Handle position creation
  const handleOpenPosition = () => {
    const newPosition = {
      id: Date.now(),
      symbol: selectedInstrument.symbol,
      type: selectedInstrument.type,
      side: orderSide,
      quantity,
      entryPrice: selectedInstrument.price,
      leverage,
      stopLoss: stopLoss || null,
      takeProfit: takeProfit || null,
      pnl: 0,
      status: 'open'
    };
    setPositions([...positions, newPosition]);
    setQuantity(1);
    setStopLoss('');
    setTakeProfit('');
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <Globe className="w-8 h-8 text-yellow-500" />
          <div>
            <h1 className="text-2xl font-bold">TigerEx TradFi</h1>
            <p className="text-gray-400 text-sm">CFD, Forex, ETF, Derivatives</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button className="px-4 py-2 bg-gray-800 rounded-lg hover:bg-gray-700">
            <RefreshCw className="w-5 h-5" />
          </button>
          <button className="px-4 py-2 bg-gray-800 rounded-lg hover:bg-gray-700">
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b border-gray-700">
        {['trade', 'positions', 'history'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 capitalize ${activeTab === tab ? 'text-yellow-500 border-b-2 border-yellow-500' : 'text-gray-400'}`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-12 gap-4">
        {/* Instrument List */}
        <div className="col-span-3 bg-gray-800 rounded-lg p-4">
          <div className="mb-4">
            <input 
              type="text" 
              placeholder="Search instruments..." 
              className="w-full px-3 py-2 bg-gray-700 rounded-lg text-white placeholder-gray-400"
            />
          </div>
          
          {/* Filter tabs */}
          <div className="flex flex-wrap gap-2 mb-4">
            <button 
              onClick={() => setFilterType('ALL')}
              className={`px-2 py-1 text-xs rounded ${filterType === 'ALL' ? 'bg-yellow-500 text-black' : 'bg-gray-700'}`}
            >
              ALL
            </button>
            {Object.keys(INSTRUMENT_TYPES).map(type => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`px-2 py-1 text-xs rounded ${filterType === type ? 'bg-yellow-500 text-black' : 'bg-gray-700'}`}
              >
                {INSTRUMENT_TYPES[type].name}
              </button>
            ))}
          </div>

          {/* Instruments List */}
          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {filteredInstruments.map(inst => (
              <div
                key={inst.symbol}
                onClick={() => setSelectedInstrument(inst)}
                className={`p-3 rounded-lg cursor-pointer ${selectedInstrument.symbol === inst.symbol ? 'bg-yellow-500/20 border border-yellow-500' : 'bg-gray-700 hover:bg-gray-600'}`}
              >
                <div className="flex justify-between items-center">
                  <div>
                    <span className="font-bold">{inst.symbol}</span>
                    <span className="text-xs ml-2" style={{ color: INSTRUMENT_TYPES[inst.type]?.color }}>
                      {INSTRUMENT_TYPES[inst.type]?.name}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="font-mono">${inst.price.toLocaleString()}</div>
                    <div className={`text-xs ${inst.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {inst.change >= 0 ? '+' : ''}{inst.change}%
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Trading Area */}
        <div className="col-span-6 space-y-4">
          {/* Chart */}
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-xl font-bold">{selectedInstrument.symbol}</h2>
                <p className="text-gray-400">{INSTRUMENT_TYPES[selectedInstrument.type]?.description}</p>
              </div>
              <div className="flex gap-4">
                <div className="text-right">
                  <div className="text-2xl font-bold">${selectedInstrument.price.toLocaleString()}</div>
                  <div className={`text-sm ${selectedInstrument.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {selectedInstrument.change >= 0 ? '+' : ''}{selectedInstrument.change}%
                  </div>
                </div>
              </div>
            </div>
            
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={generatePriceHistory(selectedInstrument.price)}>
                  <defs>
                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="time" stroke="#6b7280" />
                  <YAxis domain={['auto', 'auto']} stroke="#6b7280" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1f2937', border: 'none' }}
                    labelStyle={{ color: '#9ca3af' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="price" 
                    stroke="#f59e0b" 
                    fillOpacity={1} 
                    fill="url(#colorPrice)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Quick Trade Buttons */}
            <div className="flex gap-2 mt-4">
              {['25%', '50%', '75%', '100%'].map(pct => (
                <button key={pct} className="px-3 py-1 bg-gray-700 rounded text-sm">
                  {pct}
                </button>
              ))}
            </div>
          </div>

          {/* Order Form */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-bold mb-4">Open Position</h3>
            
            {/* Buy/Sell Toggle */}
            <div className="flex gap-2 mb-4">
              <button
                onClick={() => setOrderSide('buy')}
                className={`flex-1 py-3 rounded-lg font-bold ${orderSide === 'buy' ? 'bg-green-500' : 'bg-gray-700 text-gray-400'}`}
              >
                BUY
              </button>
              <button
                onClick={() => setOrderSide('sell')}
                className={`flex-1 py-3 rounded-lg font-bold ${orderSide === 'sell' ? 'bg-red-500' : 'bg-gray-700 text-gray-400'}`}
              >
                SELL
              </button>
            </div>

            {/* Order Type */}
            <div className="grid grid-cols-4 gap-2 mb-4">
              {['market', 'limit', 'stop', 'oco'].map(type => (
                <button
                  key={type}
                  onClick={() => setOrderType(type)}
                  className={`py-2 rounded text-sm capitalize ${orderType === type ? 'bg-yellow-500 text-black' : 'bg-gray-700'}`}
                >
                  {type}
                </button>
              ))}
            </div>

            {/* Quantity & Leverage */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Quantity</label>
                <input 
                  type="number" 
                  value={quantity}
                  onChange={e => setQuantity(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Leverage</label>
                <select 
                  value={leverage}
                  onChange={e => setLeverage(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-700 rounded"
                >
                  {[1, 2, 5, 10, 20, 50, 100].map(l => (
                    <option key={l} value={l}>{l}x</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Stop Loss & Take Profit */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Stop Loss</label>
                <input 
                  type="number"
                  value={stopLoss}
                  onChange={e => setStopLoss(e.target.value)}
                  placeholder="0.00"
                  className="w-full px-3 py-2 bg-gray-700 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Take Profit</label>
                <input 
                  type="number"
                  value={takeProfit}
                  onChange={e => setTakeProfit(e.target.value)}
                  placeholder="0.00"
                  className="w-full px-3 py-2 bg-gray-700 rounded"
                />
              </div>
            </div>

            {/* Order Summary */}
            <div className="bg-gray-700 rounded-lg p-3 mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">Order Value</span>
                <span>${orderValue.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">Estimated Margin</span>
                <span>${estimatedMargin.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">Fee (0.1%)</span>
                <span>${fee.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Max PnL</span>
                <span className={orderSide === 'buy' ? 'text-green-500' : 'text-red-500'}>
                  ${(orderValue * 0.3).toLocaleString()}
                </span>
              </div>
            </div>

            {/* Submit Button */}
            <button
              onClick={handleOpenPosition}
              className={`w-full py-3 rounded-lg font-bold ${orderSide === 'buy' ? 'bg-green-500 hover:bg-green-600' : 'bg-red-500 hover:bg-red-600'}`}
            >
              {orderSide === 'buy' ? 'BUY' : 'SELL'} {selectedInstrument.symbol}
            </button>
          </div>
        </div>

        {/* Info Panel */}
        <div className="col-span-3 space-y-4">
          {/* Instrument Info */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="font-bold mb-3">Instrument Info</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Type</span>
                <span>{INSTRUMENT_TYPES[selectedInstrument.type]?.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Max Leverage</span>
                <span>{selectedInstrument.leverage}x</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Trading Hours</span>
                <span>24/7</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Maker Fee</span>
                <span>0.01%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Taker Fee</span>
                <span>0.02%</span>
              </div>
            </div>
          </div>

          {/* Account Summary */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="font-bold mb-3">Account</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Equity</span>
                <span>$10,000.00</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Available</span>
                <span>$8,500.00</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Margin Used</span>
                <span>$1,500.00</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Unrealized PnL</span>
                <span className="text-green-500">+$250.00</span>
              </div>
            </div>
          </div>

          {/* Leverage Warning */}
          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <Shield className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
              <div className="text-sm">
                <p className="font-bold text-yellow-500">Leverage Warning</p>
                <p className="text-gray-400">Higher leverage increases both profits and losses. Trade responsibly.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
