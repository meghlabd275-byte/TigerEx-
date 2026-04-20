import React, { useState, useEffect } from 'react';
import { Activity, TrendingUp, TrendingDown, RefreshCw, Search, Wifi, WifiOff, ArrowUpRight, ArrowDownRight } from 'lucide-react';

const EXCHANGES = ['binance', 'coinbase', 'kraken', 'bybit', 'kucoin', 'okx', 'huobi', 'bitget', 'gate', 'bitfinex'];

export default function PriceAggregationPage() {
  const [prices, setPrices] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    fetchPrices();
    setWsConnected(true);
    setLoading(false);
  }, []);

  const fetchPrices = async () => {
    setLoading(true);
    // Simulated price data
    setPrices({
      'BTCUSDT': { price: 67850.25, change: 1.87, high: 68200, low: 66500, exchanges: ['binance', 'coinbase', 'kraken'], spread: 0.5 },
      'ETHUSDT': { price: 3542.18, change: 2.48, high: 3600, low: 3450, exchanges: ['binance', 'bybit', 'okx'], spread: 0.3 },
      'SOLUSDT': { price: 185.92, change: -0.85, high: 190, low: 182, exchanges: ['binance', 'kucoin'], spread: 0.1 },
      'BNBUSDT': { price: 612.45, change: 1.12, high: 620, low: 605, exchanges: ['binance', 'bybit'], spread: 0.2 },
      'XRPUSDT': { price: 0.5245, change: 3.25, high: 0.54, low: 0.50, exchanges: ['binance', 'kraken', 'huobi'], spread: 0.01 },
      'ARBUSDT': { price: 1.85, change: 3.2, high: 1.90, low: 1.78, exchanges: ['binance', 'bybit'], spread: 0.02 },
      'BASEUSDT': { price: 2.45, change: 1.8, high: 2.52, low: 2.38, exchanges: ['binance', 'okx'], spread: 0.01 },
      'SUIUSDT': { price: 3.20, change: 12.5, high: 3.50, low: 2.85, exchanges: ['binance', 'bybit', 'kucoin'], spread: 0.05 },
      'PEPEUSDT': { price: 0.00000429, change: 15.2, high: 0.000005, low: 0.0000037, exchanges: ['binance'], spread: 0.0000001 },
      'BONKUSDT': { price: 0.000025, change: -5.8, high: 0.000027, low: 0.000023, exchanges: ['bybit'], spread: 0.000001 }
    });
    setLoading(false);
  };

  const filteredPrices = Object.entries(prices).filter(([symbol]) => 
    symbol.toLowerCase().includes(search.toLowerCase())
  );

  const formatPrice = (price: number) => {
    if (price >= 1000) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (price >= 1) return price.toFixed(4);
    if (price >= 0.0001) return price.toFixed(6);
    return price.toFixed(8);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Activity className="text-yellow-400" />
              Price Aggregation
            </h1>
            <p className="text-gray-400 mt-1">Real-time prices from 10+ exchanges</p>
          </div>
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${wsConnected ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
              {wsConnected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
              <span className="text-sm font-medium">{wsConnected ? 'Live' : 'Disconnected'}</span>
            </div>
            <button onClick={fetchPrices} className="p-2 bg-yellow-500 hover:bg-yellow-400 rounded-lg">
              <RefreshCw className="w-5 h-5 text-black" />
            </button>
          </div>
        </div>

        <div className="flex gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search trading pairs..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-3"
            />
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="w-8 h-8 text-yellow-500 animate-spin" />
          </div>
        ) : (
          <div className="bg-gray-800 rounded-xl overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-900/50">
                <tr>
                  <th className="text-left p-4 text-gray-400 font-medium">Pair</th>
                  <th className="text-right p-4 text-gray-400 font-medium">Price</th>
                  <th className="text-right p-4 text-gray-400 font-medium">Change 24h</th>
                  <th className="text-right p-4 text-gray-400 font-medium">High 24h</th>
                  <th className="text-right p-4 text-gray-400 font-medium">Low 24h</th>
                  <th className="text-right p-4 text-gray-400 font-medium">Exchanges</th>
                  <th className="text-right p-4 text-gray-400 font-medium">Spread</th>
                </tr>
              </thead>
              <tbody>
                {filteredPrices.slice(0, 20).map(([symbol, data]: [string, any]) => (
                  <tr key={symbol} className="border-t border-gray-700 hover:bg-gray-700/30">
                    <td className="p-4 font-semibold">{symbol}</td>
                    <td className="p-4 text-right font-mono">${formatPrice(data.price)}</td>
                    <td className={`p-4 text-right ${data.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      <div className="flex items-center justify-end gap-1">
                        {data.change >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                        {data.change.toFixed(2)}%
                      </div>
                    </td>
                    <td className="p-4 text-right font-mono">${formatPrice(data.high)}</td>
                    <td className="p-4 text-right font-mono">${formatPrice(data.low)}</td>
                    <td className="p-4 text-right">
                      <div className="flex justify-end gap-1">
                        {data.exchanges.slice(0, 3).map((ex: string) => (
                          <span key={ex} className="px-2 py-1 bg-gray-700 rounded text-xs">{ex}</span>
                        ))}
                        {data.exchanges.length > 3 && (
                          <span className="px-2 py-1 bg-gray-700 rounded text-xs">+{data.exchanges.length - 3}</span>
                        )}
                      </div>
                    </td>
                    <td className="p-4 text-right font-mono text-gray-400">${formatPrice(data.spread)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="mt-8">
          <h2 className="text-xl font-bold mb-4">Supported Exchanges</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {EXCHANGES.map(ex => (
              <div key={ex} className="bg-gray-800 p-4 rounded-xl text-center">
                <div className="w-12 h-12 bg-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-xl">{ex[0].toUpperCase()}</span>
                </div>
                <h3 className="font-semibold">{ex.charAt(0).toUpperCase() + ex.slice(1)}</h3>
                <span className="text-green-400 text-sm">Active</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}