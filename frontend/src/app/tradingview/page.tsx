'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Search, 
  Activity, 
  Settings,
  Maximize2,
  RefreshCw,
  LineChart,
  BarChart3,
  CandlestickChart
} from 'lucide-react';

const TRADINGVIEW_API = 'http://localhost:8092';
const INDICATORS = [
  { id: 'sma', name: 'SMA', params: { period: 20 } },
  { id: 'ema', name: 'EMA', params: { period: 20 } },
  { id: 'rsi', name: 'RSI', params: { period: 14 } },
  { id: 'macd', name: 'MACD', params: { fast: 12, slow: 26 } },
  { id: 'bollinger', name: 'Bollinger', params: { period: 20, std: 2 } },
  { id: 'atr', name: 'ATR', params: { period: 14 } },
  { id: 'adx', name: 'ADX', params: { period: 14 } },
  { id: 'stoch', name: 'Stochastic', params: { k: 14, d: 3 } }
];

const TIMEFRAMES = [
  { id: '1m', label: '1m' },
  { id: '5m', label: '5m' },
  { id: '15m', label: '15m' },
  { id: '1h', label: '1H' },
  { id: '4h', label: '4H' },
  { id: '1d', label: '1D' },
  { id: '1w', label: '1W' }
];

interface Token {
  id: string;
  name: string;
  symbol: string;
  price: number;
  price_change_24h: number;
  volume_24h: number;
  market_cap: number;
  blockchain: string;
}

export default function TradingViewPage() {
  const [tokens, setTokens] = useState<Token[]>([]);
  const [selectedToken, setSelectedToken] = useState<Token | null>(null);
  const [search, setSearch] = useState('');
  const [timeframe, setTimeframe] = useState('1h');
  const [indicators, setIndicators] = useState<string[]>(['sma', 'rsi']);
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchTokens();
  }, []);

  useEffect(() => {
    if (selectedToken) {
      fetchChartData();
    }
  }, [selectedToken, timeframe]);

  const fetchTokens = async () => {
    try {
      const response = await fetch(`${TRADINGVIEW_API}/api/v1/tokens?limit=50`);
      const data = await response.json();
      if (data.success) {
        setTokens(data.tokens || []);
        if (data.tokens?.length > 0) {
          setSelectedToken(data.tokens[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch tokens:', error);
      // Use sample data for demo
      setTokens([
        { id: 'tiger-coin', name: 'TigerCoin', symbol: 'TIGER', price: 0.05, price_change_24h: 5.2, volume_24h: 2500000, market_cap: 50000000, blockchain: 'ethereum' },
        { id: 'pepe-coin', name: 'PepeCoin', symbol: 'PEPE', price: 0.00000429, price_change_24h: 15.2, volume_24h: 500000000, market_cap: 1800000000, blockchain: 'ethereum' },
        { id: 'arbitrum', name: 'Arbitrum', symbol: 'ARB', price: 1.85, price_change_24h: 3.2, volume_24h: 1200000000, market_cap: 5000000000, blockchain: 'ethereum' },
        { id: 'base', name: 'Base', symbol: 'BASE', price: 2.45, price_change_24h: 1.8, volume_24h: 800000000, market_cap: 3500000000, blockchain: 'ethereum' },
        { id: 'sui', name: 'Sui', symbol: 'SUI', price: 3.20, price_change_24h: 12.5, volume_24h: 1500000000, market_cap: 6000000000, blockchain: 'sui' }
      ]);
      setSelectedToken({
        id: 'tiger-coin',
        name: 'TigerCoin',
        symbol: 'TIGER',
        price: 0.05,
        price_change_24h: 5.2,
        volume_24h: 2500000,
        market_cap: 50000000,
        blockchain: 'ethereum'
      });
    }
  };

  const fetchChartData = async () => {
    if (!selectedToken) return;
    setLoading(true);
    try {
      const response = await fetch(
        `${TRADINGVIEW_API}/api/v1/tokens/${selectedToken.id}/ohlc?timeframe=${timeframe}&limit=500`
      );
      const data = await response.json();
      if (data.success) {
        setChartData(data.data || []);
      }
    } catch (error) {
      console.error('Failed to fetch chart data:', error);
      // Generate sample data for demo
      const sampleData = generateSampleData(selectedToken.price);
      setChartData(sampleData);
    } finally {
      setLoading(false);
    }
  };

  const generateSampleData = (currentPrice: number) => {
    const data = [];
    const now = Date.now();
    let price = currentPrice * 0.9;
    for (let i = 500; i >= 0; i--) {
      const change = (Math.random() - 0.48) * price * 0.02;
      const open = price;
      const close = price + change;
      const high = Math.max(open, close) * (1 + Math.random() * 0.01);
      const low = Math.min(open, close) * (1 - Math.random() * 0.01);
      data.push([
        now - i * 3600000,
        open,
        high,
        low,
        close,
        Math.random() * 1000000
      ]);
      price = close;
    }
    return data;
  };

  const toggleIndicator = (indicatorId: string) => {
    setIndicators(prev => 
      prev.includes(indicatorId)
        ? prev.filter(i => i !== indicatorId)
        : [...prev, indicatorId]
    );
  };

  const filteredTokens = tokens.filter(t => 
    t.name.toLowerCase().includes(search.toLowerCase()) ||
    t.symbol.toLowerCase().includes(search.toLowerCase())
  );

  const formatPrice = (price: number) => {
    if (price >= 1000) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (price >= 1) return price.toFixed(4);
    if (price >= 0.0001) return price.toFixed(6);
    return price.toFixed(8);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex">
      {/* Sidebar - Token List */}
      <div className="w-72 bg-gray-800 border-r border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search tokens..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-yellow-500"
            />
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {filteredTokens.map(token => (
            <div
              key={token.id}
              onClick={() => setSelectedToken(token)}
              className={`p-4 border-b border-gray-700 cursor-pointer hover:bg-gray-700/50 ${
                selectedToken?.id === token.id ? 'bg-gray-700' : ''
              }`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold">{token.symbol}</h3>
                  <p className="text-gray-400 text-sm">{token.name}</p>
                </div>
                <div className="text-right">
                  <p className="font-mono">${formatPrice(token.price)}</p>
                  <p className={`text-sm ${token.price_change_24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {token.price_change_24h >= 0 ? '+' : ''}{token.price_change_24h.toFixed(2)}%
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chart Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-gray-800 border-b border-gray-700 p-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            {selectedToken && (
              <>
                <div>
                  <h2 className="text-2xl font-bold flex items-center gap-2">
                    {selectedToken.symbol}/USDT
                    <span className="text-gray-400 text-lg">{selectedToken.name}</span>
                  </h2>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-mono">${formatPrice(selectedToken.price)}</p>
                  <p className={`text-sm ${selectedToken.price_change_24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {selectedToken.price_change_24h >= 0 ? '+' : ''}{selectedToken.price_change_24h.toFixed(2)}% (24h)
                  </p>
                </div>
              </>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            {/* Timeframes */}
            {TIMEFRAMES.map(tf => (
              <button
                key={tf.id}
                onClick={() => setTimeframe(tf.id)}
                className={`px-3 py-1 rounded text-sm ${
                  timeframe === tf.id 
                    ? 'bg-yellow-500 text-black' 
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {tf.label}
              </button>
            ))}
            
            <button className="p-2 bg-gray-700 hover:bg-gray-600 rounded">
              <Maximize2 className="w-4 h-4" />
            </button>
            <button 
              onClick={fetchChartData}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Chart Container */}
        <div className="flex-1 relative" ref={chartRef}>
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <RefreshCw className="w-8 h-8 text-yellow-500 animate-spin" />
            </div>
          ) : (
            <div className="w-full h-full p-4">
              {/* Simple candle chart visualization */}
              <div className="flex items-end justify-between h-full gap-1">
                {chartData.slice(-100).map((candle, idx) => {
                  const [timestamp, open, high, low, close, volume] = candle;
                  const isGreen = close >= open;
                  const height = Math.max(10, Math.abs(close - open) / ((selectedToken?.price || 1) * 0.1) * 100);
                  const wickHigh = (high - Math.max(open, close)) / ((selectedToken?.price || 1) * 0.1) * 50;
                  const wickLow = (Math.min(open, close) - low) / ((selectedToken?.price || 1) * 0.1) * 50;
                  
                  return (
                    <div
                      key={idx}
                      className="flex-1 flex flex-col items-center group relative"
                    >
                      {/* Tooltip */}
                      <div className="absolute bottom-full mb-2 bg-gray-900 p-2 rounded text-xs hidden group-hover:block z-10 whitespace-nowrap">
                        <div>O: {open.toFixed(6)}</div>
                        <div>H: {high.toFixed(6)}</div>
                        <div>L: {low.toFixed(6)}</div>
                        <div>C: {close.toFixed(6)}</div>
                      </div>
                      
                      {/* Wick */}
                      <div 
                        className={`w-0.5 ${isGreen ? 'bg-green-500' : 'bg-red-500'}`}
                        style={{ height: `${20 + height}px` }}
                      />
                      {/* Body */}
                      <div 
                        className={`w-full ${isGreen ? 'bg-green-500' : 'bg-red-500'}`}
                        style={{ height: `${Math.max(4, height)}px` }}
                      />
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Indicators Panel */}
        <div className="bg-gray-800 border-t border-gray-700 p-4">
          <div className="flex items-center gap-4">
            <span className="text-gray-400 text-sm flex items-center gap-2">
              <LineChart className="w-4 h-4" /> Indicators:
            </span>
            <div className="flex gap-2">
              {INDICATORS.map(ind => (
                <button
                  key={ind.id}
                  onClick={() => toggleIndicator(ind.id)}
                  className={`px-3 py-1 rounded text-sm ${
                    indicators.includes(ind.id)
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {ind.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Token Info */}
      <div className="w-72 bg-gray-800 border-l border-gray-700 p-4">
        <h3 className="font-bold mb-4">Token Info</h3>
        
        {selectedToken && (
          <div className="space-y-4">
            <div className="bg-gray-700/50 p-3 rounded">
              <p className="text-gray-400 text-sm">Market Cap</p>
              <p className="font-semibold">${(selectedToken.market_cap / 1e9).toFixed(2)}B</p>
            </div>
            <div className="bg-gray-700/50 p-3 rounded">
              <p className="text-gray-400 text-sm">24h Volume</p>
              <p className="font-semibold">${(selectedToken.volume_24h / 1e6).toFixed(2)}M</p>
            </div>
            <div className="bg-gray-700/50 p-3 rounded">
              <p className="text-gray-400 text-sm">Blockchain</p>
              <p className="font-semibold capitalize">{selectedToken.blockchain}</p>
            </div>
            
            <button className="w-full bg-yellow-500 hover:bg-yellow-400 text-black py-3 rounded-lg font-semibold mt-4">
              Trade {selectedToken.symbol}
            </button>
          </div>
        )}

        {/* Available Indicators */}
        <div className="mt-6">
          <h4 className="font-semibold mb-3">Chart Indicators</h4>
          <div className="space-y-2">
            {INDICATORS.map(ind => (
              <div
                key={ind.id}
                onClick={() => toggleIndicator(ind.id)}
                className={`p-2 rounded cursor-pointer flex items-center justify-between ${
                  indicators.includes(ind.id) ? 'bg-blue-500/20 text-blue-400' : 'bg-gray-700/50 text-gray-300'
                }`}
              >
                <span>{ind.name}</span>
                <div className={`w-4 h-4 rounded border ${
                  indicators.includes(ind.id) ? 'bg-blue-500 border-blue-500' : 'border-gray-500'
                }`}>
                  {indicators.includes(ind.id) && (
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                    </svg>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}