import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useRouter } from 'next/navigation';

interface MarketData {
  symbol: string;
  price: string;
  change: string;
  changePercent: string;
  volume: string;
}

interface TradeHistory {
  id: string;
  symbol: string;
  type: string;
  amount: string;
  price: string;
  time: string;
}

const HomePage: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [recentTrades, setRecentTrades] = useState<TradeHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate market data fetching
    const mockMarketData: MarketData[] = [
      { symbol: 'BTC/USDT', price: '43,521.50', change: '+1,234.56', changePercent: '+2.92%', volume: '1.2B' },
      { symbol: 'ETH/USDT', price: '2,234.78', change: '+45.23', changePercent: '+2.07%', volume: '890M' },
      { symbol: 'BNB/USDT', price: '312.45', change: '+5.67', changePercent: '+1.85%', volume: '234M' },
      { symbol: 'SOL/USDT', price: '98.76', change: '-2.34', changePercent: '-2.31%', volume: '567M' },
      { symbol: 'ADA/USDT', price: '0.5823', change: '+0.0123', changePercent: '+2.16%', volume: '123M' },
    ];

    const mockTrades: TradeHistory[] = [
      { id: '1', symbol: 'BTC/USDT', type: 'Buy', amount: '0.025', price: '43,521.50', time: '10:45:23' },
      { id: '2', symbol: 'ETH/USDT', type: 'Sell', amount: '1.5', price: '2,234.78', time: '10:44:15' },
      { id: '3', symbol: 'BNB/USDT', type: 'Buy', amount: '10', price: '312.45', time: '10:43:02' },
      { id: '4', symbol: 'SOL/USDT', type: 'Buy', amount: '50', price: '98.76', time: '10:42:45' },
    ];

    setTimeout(() => {
      setMarketData(mockMarketData);
      setRecentTrades(mockTrades);
      setLoading(false);
    }, 1000);
  }, []);

  const handleTrade = (symbol: string) => {
    router.push(`/trade?symbol=${symbol}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-400">TigerEx</h1>
              <nav className="ml-10 flex items-baseline space-x-4">
                <a href="#" className="bg-gray-900 text-white px-3 py-2 rounded-md text-sm font-medium">Markets</a>
                <a href="#" className="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Trade</a>
                <a href="#" className="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Futures</a>
                <a href="#" className="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Wallet</a>
                {isAuthenticated && user?.isAdmin && (
                  <a href="/admin" className="text-purple-400 hover:bg-purple-900 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Admin</a>
                )}
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <>
                  <span className="text-sm">Welcome, {user?.username}</span>
                  <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-md text-sm font-medium">
                    Profile
                  </button>
                </>
              ) : (
                <>
                  <button 
                    onClick={() => router.push('/login')}
                    className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-md text-sm font-medium"
                  >
                    Login
                  </button>
                  <button 
                    onClick={() => router.push('/register')}
                    className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium"
                  >
                    Register
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-purple-600 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-extrabold text-white sm:text-5xl md:text-6xl">
            Trade Crypto with Confidence
          </h2>
          <p className="mt-3 max-w-md mx-auto text-base text-gray-200 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            Advanced trading platform with spot, futures, and options trading. 
            Low fees, high liquidity, and enterprise-grade security.
          </p>
          <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
            <div className="rounded-md shadow">
              <button 
                onClick={() => router.push('/register')}
                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg md:px-10"
              >
                Get Started
              </button>
            </div>
            <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
              <button 
                onClick={() => router.push('/trade')}
                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10"
              >
                Trade Now
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Market Overview */}
      <section className="py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h3 className="text-2xl font-bold text-white mb-6">Market Overview</h3>
          <div className="bg-gray-800 rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-700">
                <thead className="bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Pair</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">24h Change</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">24h Volume</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-gray-800 divide-y divide-gray-700">
                  {marketData.map((market) => (
                    <tr key={market.symbol} className="hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-white">{market.symbol}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-300">${market.price}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          market.change.startsWith('+') 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {market.change} ({market.changePercent})
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                        ${market.volume}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button 
                          onClick={() => handleTrade(market.symbol)}
                          className="text-blue-400 hover:text-blue-600 mr-3"
                        >
                          Trade
                        </button>
                        <button className="text-gray-400 hover:text-gray-600">
                          Chart
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* Recent Trades */}
      <section className="py-12 bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h3 className="text-2xl font-bold text-white mb-6">Recent Trades</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {recentTrades.map((trade) => (
              <div key={trade.id} className="bg-gray-900 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-white">{trade.symbol}</p>
                    <p className="text-xs text-gray-400">{trade.time}</p>
                  </div>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                    trade.type === 'Buy' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {trade.type}
                  </span>
                </div>
                <div className="mt-2">
                  <p className="text-lg font-semibold text-white">${trade.price}</p>
                  <p className="text-sm text-gray-400">{trade.amount} {trade.symbol.split('/')[0]}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-white mb-6">Why Choose TigerEx</h3>
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
              <div className="text-center">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white mb-4 mx-auto">
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                </div>
                <h4 className="text-lg font-medium text-white mb-2">Low Fees</h4>
                <p className="text-sm text-gray-400">Competitive trading fees with volume-based discounts</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-green-500 text-white mb-4 mx-auto">
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <h4 className="text-lg font-medium text-white mb-2">Secure</h4>
                <p className="text-sm text-gray-400">Enterprise-grade security with multi-sig wallets</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-purple-500 text-white mb-4 mx-auto">
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h4 className="text-lg font-medium text-white mb-2">Fast</h4>
                <p className="text-sm text-gray-400">High-performance matching engine with microsecond latency</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-yellow-500 text-white mb-4 mx-auto">
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h4 className="text-lg font-medium text-white mb-2">24/7 Support</h4>
                <p className="text-sm text-gray-400">Round-the-clock customer support in multiple languages</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-sm text-gray-400">
              © 2024 TigerEx. All rights reserved. 
              <a href="#" className="ml-4 text-blue-400 hover:text-blue-600">Terms</a> 
              <a href="#" className="ml-4 text-blue-400 hover:text-blue-600">Privacy</a>
              <a href="#" className="ml-4 text-blue-400 hover:text-blue-600">Support</a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;