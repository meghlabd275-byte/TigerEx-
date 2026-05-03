/**
 * TigerEx Frontend Component
 * @file page.tsx
 * @description React component for TigerEx exchange
 * @author TigerEx Development Team
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign, 
  RefreshCw,
  Search,
  Filter,
  Star,
  ArrowUpRight,
  ArrowDownRight,
  ExternalLink,
  Wifi,
  WifiOff
} from 'lucide-react';

const PRICE_API = 'http://localhost:8095';
const EXCHANGES = ['binance', 'coinbase', 'kraken', 'bybit', 'kucoin', 'okx', 'huobi', 'bitget', 'gate', 'bitfinex'];

export default function PriceAggregationPage() {
  const [prices, setPrices] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedExchange, setSelectedExchange] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    fetchPrices();
    
    // Setup WebSocket
    const ws = new WebSocket(`ws://${PRICE_API}/ws/prices`);
    
    ws.onopen = () => {
      setWsConnected(true);
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'price_update') {
        setPrices(data.data);
        setLastUpdate(new Date());
      }
    };
    
    ws.onerror = () => {
      setWsConnected(false);
    };
    
    ws.onclose = () => {
      setWsConnected(false);
    };

    // Refresh every 30 seconds
    const interval = setInterval(fetchPrices, 30000);
    
    return () => {
      ws.close();
      clearInterval(interval);
    };
  }, []);

  const fetchPrices = async () => {
    try {
      const response = await fetch(`${PRICE_API}/api/v1/prices`);
      const data = await response.json();
      if (data.success) {
        setPrices(data.prices || {});
        setLastUpdate(new Date());
      }
    } catch (error) {
      console.error('Failed to fetch prices:', error);
    } finally {
      setLoading(false);
    }
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

  const formatVolume = (volume: number) => {
    if (volume >= 1e9) return `$${(volume / 1e9).toFixed(2)}B`;
    if (volume >= 1e6) return `$${(volume / 1e6).toFixed(2)}M`;
    if (volume >= 1e3) return `$${(volume / 1e3).toFixed(2)}K`;
    return `$${volume.toFixed(2)}`;
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
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
            <button 
              onClick={fetchPrices}
              className="p-2 bg-yellow-500 hover:bg-yellow-400 rounded-lg transition-colors"
            >
              <RefreshCw className="w-5 h-5 text-black" />
            </button>
          </div>
        </div>

        {/* Last Update */}
        {lastUpdate && (
          <p className="text-gray-500 text-sm mb-4">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </p>
        )}

        {/* Search and Filters */}
        <div className="flex gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search trading pairs..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-3 focus:outline-none focus:border-yellow-500"
            />
          </div>
          <select
            value={selectedExchange || ''}
            onChange={(e) => setSelectedExchange(e.target.value || null)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:border-yellow-500"
          >
            <option value="">All Exchanges</option>
            {EXCHANGES.map(ex => (
              <option key={ex} value={ex}>{ex.charAt(0).toUpperCase() + ex.slice(1)}</option>
            ))}
          </select>
        </div>

        {/* Loading State */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="w-8 h-8 text-yellow-500 animate-spin" />
          </div>
        ) : (
          /* Price Table */
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
                {filteredPrices.slice(0, 50).map(([symbol, data]: [string, any]) => (
                  <tr key={symbol} className="border-t border-gray-700 hover:bg-gray-700/30 transition-colors">
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">{symbol}</span>
                      </div>
                    </td>
                    <td className="p-4 text-right font-mono">
                      ${formatPrice(data.price)}
                    </td>
                    <td className={`p-4 text-right ${data.change_percent_24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      <div className="flex items-center justify-end gap-1">
                        {data.change_percent_24h >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                        {data.change_percent_24h?.toFixed(2)}%
                      </div>
                    </td>
                    <td className="p-4 text-right font-mono">${formatPrice(data.high_24h)}</td>
                    <td className="p-4 text-right font-mono">${formatPrice(data.low_24h)}</td>
                    <td className="p-4 text-right">
                      <div className="flex justify-end gap-1">
                        {data.exchanges?.slice(0, 3).map((ex: string) => (
                          <span key={ex} className="px-2 py-1 bg-gray-700 rounded text-xs">{ex}</span>
                        ))}
                        {data.exchanges?.length > 3 && (
                          <span className="px-2 py-1 bg-gray-700 rounded text-xs">+{data.exchanges.length - 3}</span>
                        )}
                      </div>
                    </td>
                    <td className="p-4 text-right font-mono text-gray-400">
                      ${formatPrice(data.spread)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Exchanges Section */}
        <div className="mt-8">
          <h2 className="text-xl font-bold mb-4">Supported Exchanges</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {EXCHANGES.map(exchange => (
              <div key={exchange} className="bg-gray-800 p-4 rounded-xl text-center">
                <div className="w-12 h-12 bg-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-xl">{exchange[0].toUpperCase()}</span>
                </div>
                <h3 className="font-semibold">{exchange.charAt(0).toUpperCase() + exchange.slice(1)}</h3>
                <span className="text-green-400 text-sm">Active</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}// TigerEx Wallet API
export const useWallet = () => ({ createWallet: () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' }) })
