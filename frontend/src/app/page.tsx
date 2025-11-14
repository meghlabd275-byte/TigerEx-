'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  DollarSign, 
  Shield, 
  Zap, 
  Users, 
  Clock, 
  ChevronRight, 
  Star, 
  ArrowUpRight, 
  ArrowDownRight,
  Search,
  Menu,
  X,
  Globe,
  Activity,
  Package,
  CreditCard,
  Eye,
  Bell,
  Settings,
  HelpCircle,
  Play,
  Download,
  ExternalLink
} from 'lucide-react';

interface MarketItem {
  symbol: string;
  name: string;
  price: string;
  change: string;
  changePercent: string;
  volume: string;
  marketCap: string;
  isPositive: boolean;
  sparkline: number[];
}

interface FeatureItem {
  icon: any;
  title: string;
  description: string;
  color: string;
}

interface StatItem {
  label: string;
  value: string;
  change?: string;
  isPositive?: boolean;
}

const mockMarkets: MarketItem[] = [
  {
    symbol: 'BTC/USDT',
    name: 'Bitcoin',
    price: '67,850.25',
    change: '+1,250.00',
    changePercent: '+1.87%',
    volume: '1.2B',
    marketCap: '1.32T',
    isPositive: true,
    sparkline: [66500, 66800, 67200, 66900, 67400, 67100, 67850]
  },
  {
    symbol: 'ETH/USDT',
    name: 'Ethereum',
    price: '3,542.18',
    change: '+85.50',
    changePercent: '+2.48%',
    volume: '850M',
    marketCap: '425B',
    isPositive: true,
    sparkline: [3450, 3480, 3520, 3490, 3540, 3510, 3542]
  },
  {
    symbol: 'BNB/USDT',
    name: 'Binance Coin',
    price: '612.45',
    change: '-5.80',
    changePercent: '-0.94%',
    volume: '420M',
    marketCap: '94B',
    isPositive: false,
    sparkline: [618, 616, 614, 617, 613, 615, 612]
  },
  {
    symbol: 'SOL/USDT',
    name: 'Solana',
    price: '145.67',
    change: '+4.20',
    changePercent: '+2.97%',
    volume: '380M',
    marketCap: '65B',
    isPositive: true,
    sparkline: [141, 143, 145, 142, 144, 146, 145]
  },
  {
    symbol: 'ADA/USDT',
    name: 'Cardano',
    price: '0.385',
    change: '-0.002',
    changePercent: '-0.52%',
    volume: '180M',
    marketCap: '13.5B',
    isPositive: false,
    sparkline: [0.387, 0.386, 0.385, 0.388, 0.384, 0.386, 0.385]
  },
  {
    symbol: 'XRP/USDT',
    name: 'Ripple',
    price: '0.625',
    change: '+0.015',
    changePercent: '+2.46%',
    volume: '1.2B',
    marketCap: '34B',
    isPositive: true,
    sparkline: [0.61, 0.613, 0.618, 0.615, 0.622, 0.62, 0.625]
  }
];

const features: FeatureItem[] = [
  {
    icon: DollarSign,
    title: 'Low Trading Fees',
    description: 'Competitive fees starting from 0.1% with volume-based VIP discounts',
    color: 'blue'
  },
  {
    icon: Shield,
    title: 'Enterprise Security',
    description: 'Multi-signature wallets, 2FA, and cold storage for maximum protection',
    color: 'green'
  },
  {
    icon: Zap,
    title: 'Lightning Fast',
    description: 'High-performance matching engine with microsecond latency',
    color: 'yellow'
  },
  {
    icon: Users,
    title: '24/7 Support',
    description: 'Round-the-clock customer support in multiple languages',
    color: 'purple'
  }
];

const stats: StatItem[] = [
  { label: 'Total Volume (24h)', value: '$45.6B', change: '+12.5%', isPositive: true },
  { label: 'Active Users', value: '1.2M+', change: '+8.3%', isPositive: true },
  { label: 'Trading Pairs', value: '350+', change: '+25', isPositive: true },
  { label: 'Countries', value: '180+', change: '+15', isPositive: true }
];

export default function HomePage() {
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTimeframe, setSelectedTimeframe] = useState('1D');

  const handleTrade = (symbol: string) => {
    router.push(`/trading?symbol=${symbol}`);
  };

  const handleMarkets = () => {
    router.push('/markets');
  };

  const handleLogin = () => {
    router.push('/login');
  };

  const handleRegister = () => {
    router.push('/register');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <TrendingUp size={16} className="text-white" />
                </div>
                <h1 className="text-xl font-bold text-gray-900">TigerEx</h1>
              </div>
              
              {/* Desktop Navigation */}
              <nav className="hidden md:flex items-center space-x-6">
                <button 
                  onClick={handleMarkets}
                  className="text-gray-900 hover:text-blue-600 font-medium transition-colors"
                >
                  Markets
                </button>
                <button 
                  onClick={() => router.push('/trading')}
                  className="text-gray-600 hover:text-blue-600 font-medium transition-colors"
                >
                  Trade
                </button>
                <button className="text-gray-600 hover:text-blue-600 font-medium transition-colors">
                  Futures
                </button>
                <button className="text-gray-600 hover:text-blue-600 font-medium transition-colors">
                  Assets
                </button>
                <button 
                  onClick={() => router.push('/admin')}
                  className="text-gray-600 hover:text-blue-600 font-medium transition-colors"
                >
                  Admin
                </button>
              </nav>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Search Bar */}
              <div className="hidden md:block relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                <input
                  type="text"
                  placeholder="Search markets..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-blue-500 w-64"
                />
              </div>
              
              {/* Action Buttons */}
              <button className="hidden md:block p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <Bell size={20} className="text-gray-600" />
              </button>
              <button className="hidden md:block p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <Settings size={20} className="text-gray-600" />
              </button>
              <button 
                onClick={handleLogin}
                className="hidden md:block px-4 py-2 text-gray-700 hover:text-gray-900 font-medium transition-colors"
              >
                Log In
              </button>
              <button 
                onClick={handleRegister}
                className="hidden md:block px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
              >
                Sign Up
              </button>
              
              {/* Mobile Menu Button */}
              <button 
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                {mobileMenuOpen ? <X size={20} className="text-gray-600" /> : <Menu size={20} className="text-gray-600" />}
              </button>
            </div>
          </div>
        </div>
        
        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-200">
            <div className="px-4 py-4 space-y-3">
              <button 
                onClick={handleMarkets}
                className="block w-full text-left text-gray-900 hover:text-blue-600 font-medium py-2"
              >
                Markets
              </button>
              <button className="block w-full text-left text-gray-600 hover:text-blue-600 font-medium py-2">
                Trade
              </button>
              <button className="block w-full text-left text-gray-600 hover:text-blue-600 font-medium py-2">
                Futures
              </button>
              <button className="block w-full text-left text-gray-600 hover:text-blue-600 font-medium py-2">
                Assets
              </button>
              <button 
                onClick={handleLogin}
                className="block w-full text-left text-gray-600 hover:text-blue-600 font-medium py-2"
              >
                Log In
              </button>
              <button 
                onClick={handleRegister}
                className="block w-full text-left px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
              >
                Sign Up
              </button>
            </div>
          </div>
        )}
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
              Trade Crypto with Confidence
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-blue-100 max-w-3xl mx-auto">
              Advanced trading platform with spot, futures, and options. 
              Low fees, high liquidity, and enterprise-grade security.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={handleRegister}
                className="px-8 py-4 bg-white text-blue-600 rounded-lg font-semibold hover:bg-gray-100 transition-colors flex items-center justify-center space-x-2"
              >
                <span>Get Started</span>
                <ChevronRight size={20} />
              </button>
              <button 
                onClick={handleTrade}
                className="px-8 py-4 bg-blue-500 hover:bg-blue-400 text-white rounded-lg font-semibold transition-colors flex items-center justify-center space-x-2"
              >
                <span>Trade Now</span>
                <Play size={20} />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-600 mb-2">
                  {stat.label}
                </div>
                {stat.change && (
                  <div className={`flex items-center justify-center text-sm ${
                    stat.isPositive ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stat.isPositive ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                    <span>{stat.change}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Market Overview */}
      <section className="bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Market Overview</h2>
              <p className="text-gray-600">Real-time prices and market data</p>
            </div>
            <button 
              onClick={handleMarkets}
              className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium"
            >
              <span>View All Markets</span>
              <ChevronRight size={20} />
            </button>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Pair
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      24h Change
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      24h Volume
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Market Cap
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Chart (7D)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {mockMarkets.map((market) => (
                    <tr key={market.symbol} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mr-3">
                            <span className="text-sm font-bold text-gray-700">
                              {market.symbol.charAt(0)}
                            </span>
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {market.symbol}
                            </div>
                            <div className="text-sm text-gray-500">{market.name}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          ${market.price}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`flex items-center text-sm font-medium ${
                          market.isPositive ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {market.isPositive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                          <span>{market.changePercent}</span>
                        </div>
                        <div className={`text-sm ${
                          market.isPositive ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {market.change}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">${market.volume}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">${market.marketCap}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="w-24 h-12 bg-gray-50 rounded flex items-center justify-center">
                          <svg viewBox="0 0 100 40" className="w-full h-full">
                            <polyline
                              points={market.sparkline.map((price, index) => {
                                const normalizedPrice = ((price - Math.min(...market.sparkline)) / 
                                  (Math.max(...market.sparkline) - Math.min(...market.sparkline))) * 35 + 2;
                                return `${index * 14},${40 - normalizedPrice}`;
                              }).join(' ')}
                              fill="none"
                              stroke={market.isPositive ? '#10b981' : '#ef4444'}
                              strokeWidth="2"
                            />
                          </svg>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button 
                          onClick={() => handleTrade(market.symbol)}
                          className="text-blue-600 hover:text-blue-900 mr-3"
                        >
                          Trade
                        </button>
                        <button className="text-gray-400 hover:text-gray-600">
                          <Eye size={16} />
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

      {/* Features Section */}
      <section className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Why Choose TigerEx</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Experience the next generation of cryptocurrency trading with our comprehensive platform
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center">
                <div className={`w-16 h-16 bg-${feature.color}-100 rounded-lg flex items-center justify-center mx-auto mb-4`}>
                  <feature.icon size={32} className={`text-${feature.color}-600`} />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Start Trading?</h2>
          <p className="text-xl mb-8 text-blue-100">
            Join thousands of traders who trust TigerEx for their cryptocurrency trading needs
          </p>
          <button 
            onClick={handleRegister}
            className="px-8 py-4 bg-white text-blue-600 rounded-lg font-semibold hover:bg-gray-100 transition-colors flex items-center space-x-2 mx-auto"
          >
            <span>Get Started Now</span>
            <ChevronRight size={20} />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <TrendingUp size={16} className="text-white" />
                </div>
                <h3 className="text-xl font-bold">TigerEx</h3>
              </div>
              <p className="text-gray-400">
                Your trusted partner for cryptocurrency trading
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Trading</h4>
              <ul className="space-y-2 text-gray-400">
                <li><button className="hover:text-white">Spot Trading</button></li>
                <li><button className="hover:text-white">Futures Trading</button></li>
                <li><button className="hover:text-white">Options Trading</button></li>
                <li><button className="hover:text-white">Margin Trading</button></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><button className="hover:text-white">About Us</button></li>
                <li><button className="hover:text-white">Careers</button></li>
                <li><button className="hover:text-white">Blog</button></li>
                <li><button className="hover:text-white">Contact</button></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400">
                <li><button className="hover:text-white">Help Center</button></li>
                <li><button className="hover:text-white">API Documentation</button></li>
                <li><button className="hover:text-white">Fees</button></li>
                <li><button className="hover:text-white">Terms of Service</button></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 TigerEx. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}