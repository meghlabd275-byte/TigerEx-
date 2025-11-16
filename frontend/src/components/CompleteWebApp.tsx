/**
 * TigerEx Complete Web Application
 * Comprehensive web trading platform with all features
 */

import React, { useState, useEffect, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { 
  FiHome, 
  FiTrendingUp, 
  FiPieChart, 
  FiSettings, 
  FiUsers,
  FiDollarSign,
  FiShield,
  FiActivity,
  FiSearch,
  FiBell,
  FiUser,
  FiLogOut,
  FiGrid,
  FiList,
  FiChevronDown
} from 'react-icons/fi';

const CompleteWebApp = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [userRole, setUserRole] = useState('admin'); // 'user' or 'admin'
  const [activeView, setActiveView] = useState('trading');
  const [selectedPair, setSelectedPair] = useState('BTC/USDT');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

  if (!isAuthenticated) {
    return <LoginPage onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-900">
        <WebAppLayout 
          activeView={activeView}
          setActiveView={setActiveView}
          userRole={userRole}
          setUserRole={setUserRole}
          selectedPair={selectedPair}
          setSelectedPair={setSelectedPair}
          viewMode={viewMode}
          setViewMode={setViewMode}
        />
      </div>
    </Router>
  );
};

const WebAppLayout = ({ 
  activeView, 
  setActiveView, 
  userRole, 
  setUserRole, 
  selectedPair, 
  setSelectedPair,
  viewMode,
  setViewMode 
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const menuItems = [
    { id: 'trading', label: 'Trading', icon: FiTrendingUp, roles: ['user', 'admin'] },
    { id: 'portfolio', label: 'Portfolio', icon: FiPieChart, roles: ['user', 'admin'] },
    { id: 'markets', label: 'Markets', icon: FiHome, roles: ['user', 'admin'] },
    { id: 'orders', label: 'Orders', icon: FiActivity, roles: ['user', 'admin'] },
    { id: 'admin', label: 'Admin Panel', icon: FiUsers, roles: ['admin'] },
    { id: 'settings', label: 'Settings', icon: FiSettings, roles: ['user', 'admin'] },
  ];

  const filteredMenuItems = menuItems.filter(item => item.roles.includes(userRole));

  const renderMainContent = () => {
    switch(activeView) {
      case 'trading':
        return <TradingInterface selectedPair={selectedPair} setSelectedPair={setSelectedPair} />;
      case 'portfolio':
        return <PortfolioManagement viewMode={viewMode} />;
      case 'markets':
        return <MarketsOverview viewMode={viewMode} />;
      case 'admin':
        return <AdminDashboard />;
      default:
        return <div className="text-gray-400">Content for {activeView}</div>;
    }
  };

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-gray-800 border-r border-gray-700 transition-all duration-300`}>
        <div className="p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center font-bold text-white flex-shrink-0">
              T
            </div>
            {sidebarOpen && (
              <div>
                <h1 className="text-xl font-bold text-white">TigerEx</h1>
                <p className="text-xs text-gray-400">Web Trading Platform</p>
              </div>
            )}
          </div>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="mt-4 text-gray-400 hover:text-white"
          >
            <FiGrid className="w-5 h-5" />
          </button>
        </div>

        <nav className="px-4">
          {filteredMenuItems.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors mb-2 ${
                activeView === item.id
                  ? 'bg-orange-500 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {sidebarOpen && <span>{item.label}</span>}
            </button>
          ))}
        </nav>

        {/* User Section */}
        {sidebarOpen && (
          <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-700">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                <FiUser className="w-4 h-4" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-white font-medium">Admin User</p>
                <p className="text-xs text-gray-400">{userRole}@tigerex.com</p>
              </div>
              <button className="text-gray-400 hover:text-white">
                <FiChevronDown className="w-4 h-4" />
              </button>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setUserRole(userRole === 'admin' ? 'user' : 'admin')}
                className="flex-1 py-2 px-3 bg-gray-700 text-gray-300 rounded text-sm hover:bg-gray-600"
              >
                Switch Role
              </button>
              <button className="flex-1 py-2 px-3 bg-red-500 text-white rounded text-sm hover:bg-red-600">
                <FiLogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        {/* Top Bar */}
        <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {activeView === 'markets' && (
                <div className="relative">
                  <FiSearch className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search markets..."
                    className="pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-orange-500"
                  />
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-4">
              {(activeView === 'portfolio' || activeView === 'markets') && (
                <div className="flex items-center space-x-2 bg-gray-700 rounded-lg p-1">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-2 rounded ${viewMode === 'grid' ? 'bg-orange-500 text-white' : 'text-gray-400 hover:text-white'}`}
                  >
                    <FiGrid className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-2 rounded ${viewMode === 'list' ? 'bg-orange-500 text-white' : 'text-gray-400 hover:text-white'}`}
                  >
                    <FiList className="w-4 h-4" />
                  </button>
                </div>
              )}
              
              <button className="p-2 text-gray-400 hover:text-white relative">
                <FiBell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              
              <div className="flex items-center space-x-3">
                <span className="text-sm text-gray-400">Balance:</span>
                <span className="text-sm font-medium text-white">$45,678.90</span>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-auto">
          {renderMainContent()}
        </div>
      </main>
    </div>
  );
};

const TradingInterface = ({ selectedPair, setSelectedPair }) => {
  const [chartType, setChartType] = useState('candlestick');
  const [timeframe, setTimeframe] = useState('1h');

  return (
    <div className="flex h-full">
      {/* Left Sidebar - Market Pairs */}
      <div className="w-80 bg-gray-800 border-r border-gray-700">
        <div className="p-4">
          <h3 className="text-lg font-bold mb-4">Market Pairs</h3>
          <div className="space-y-2">
            {['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT'].map(pair => (
              <div
                key={pair}
                onClick={() => setSelectedPair(pair)}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedPair === pair ? 'bg-orange-500 text-white' : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span className="font-medium">{pair}</span>
                  <span className="text-sm">{pair === 'BTC/USDT' ? '43,250.50' : pair === 'ETH/USDT' ? '2,280.30' : '315.80'}</span>
                </div>
                <div className="flex justify-between items-center mt-1">
                  <span className="text-xs text-gray-400">Volume</span>
                  <span className="text-xs text-green-500">+2.34%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Trading Area */}
      <div className="flex-1 flex flex-col">
        {/* Chart Area */}
        <div className="flex-1 p-6">
          <div className="bg-gray-800 rounded-lg h-full flex items-center justify-center">
            <div className="text-center">
              <FiTrendingUp className="w-16 h-16 text-orange-500 mx-auto mb-4" />
              <p className="text-gray-400">Advanced Trading Chart</p>
              <p className="text-sm text-gray-500 mt-2">Real-time {selectedPair} price data</p>
            </div>
          </div>
        </div>

        {/* Trading Controls */}
        <div className="bg-gray-800 border-t border-gray-700 p-6">
          <div className="grid grid-cols-4 gap-4">
            <button className="py-2 bg-gray-700 text-gray-300 rounded hover:bg-orange-500 hover:text-white">
              1m
            </button>
            <button className="py-2 bg-gray-700 text-gray-300 rounded hover:bg-orange-500 hover:text-white">
              5m
            </button>
            <button className="py-2 bg-orange-500 text-white rounded">
              1h
            </button>
            <button className="py-2 bg-gray-700 text-gray-300 rounded hover:bg-orange-500 hover:text-white">
              1d
            </button>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Trading Panel */}
      <div className="w-96 bg-gray-800 border-l border-gray-700">
        <div className="p-4">
          <h3 className="text-lg font-bold mb-4">Place Order</h3>
          <div className="space-y-4">
            <div className="flex space-x-2">
              <button className="flex-1 py-2 bg-green-500 text-white rounded font-medium">Buy</button>
              <button className="flex-1 py-2 bg-gray-700 text-gray-300 rounded font-medium">Sell</button>
            </div>
            
            <div className="grid grid-cols-2 gap-2">
              <button className="py-2 bg-gray-700 text-gray-300 rounded hover:bg-orange-500 hover:text-white">Market</button>
              <button className="py-2 bg-orange-500 text-white rounded">Limit</button>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Price</label>
              <input type="number" className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white" placeholder="0.00" />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Amount</label>
              <input type="number" className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white" placeholder="0.00" />
            </div>

            <button className="w-full py-3 bg-green-500 text-white rounded font-medium hover:bg-green-600">
              Place Buy Order
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const PortfolioManagement = ({ viewMode }) => {
  const portfolio = [
    { symbol: 'BTC', amount: '0.123456', value: '$5,432.10', change: '+2.34%' },
    { symbol: 'ETH', amount: '2.345678', value: '$5,349.80', change: '-1.23%' },
    { symbol: 'BNB', amount: '10.5', value: '$3,315.90', change: '+0.89%' },
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Portfolio</h1>
        <p className="text-gray-400 mt-2">Manage your assets</p>
      </div>

      {/* Balance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <p className="text-gray-400 text-sm mb-2">Total Balance</p>
          <p className="text-2xl font-bold">$45,678.90</p>
          <p className="text-green-500 text-sm mt-1">+2.34% (24h)</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <p className="text-gray-400 text-sm mb-2">Available Balance</p>
          <p className="text-2xl font-bold">$12,345.67</p>
          <p className="text-gray-500 text-sm mt-1">Ready to trade</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <p className="text-gray-400 text-sm mb-2">Total P&L</p>
          <p className="text-2xl font-bold text-green-500">+$3,456.78</p>
          <p className="text-green-500 text-sm mt-1">+8.19% all time</p>
        </div>
      </div>

      {/* Holdings */}
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-6 border-b border-gray-700">
          <h2 className="text-xl font-bold">Your Holdings</h2>
        </div>
        
        {viewMode === 'grid' ? (
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {portfolio.map((asset, index) => (
              <div key={index} className="bg-gray-700 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-orange-500 rounded-lg flex items-center justify-center font-bold">
                    {asset.symbol.charAt(0)}
                  </div>
                  <span className={`text-sm ${asset.change.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>
                    {asset.change}
                  </span>
                </div>
                <h3 className="font-bold text-lg mb-1">{asset.symbol}</h3>
                <p className="text-gray-400 text-sm mb-2">{asset.amount} {asset.symbol}</p>
                <p className="text-xl font-bold">{asset.value}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-700">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Asset</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Amount</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Value</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">24h Change</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {portfolio.map((asset, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center font-bold mr-3">
                          {asset.symbol.charAt(0)}
                        </div>
                        <span className="font-medium">{asset.symbol}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-300">
                      {asset.amount}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap font-medium">
                      {asset.value}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm ${asset.change.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>
                        {asset.change}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button className="text-orange-500 hover:text-orange-400 mr-3">Trade</button>
                      <button className="text-gray-400 hover:text-white">Details</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

const MarketsOverview = ({ viewMode }) => {
  const markets = [
    { pair: 'BTC/USDT', price: '43,250.50', change: '+2.34%', volume: '1.2B', category: 'Spot' },
    { pair: 'ETH/USDT', price: '2,280.30', change: '-1.23%', volume: '850M', category: 'Spot' },
    { pair: 'BNB/USDT', price: '315.80', change: '+0.89%', volume: '320M', category: 'Spot' },
    { pair: 'BTC-PERP', price: '43,251.00', change: '+2.35%', volume: '2.1B', category: 'Futures' },
    { pair: 'ETH-PERP', price: '2,280.85', change: '-1.22%', volume: '1.5B', category: 'Futures' },
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Markets</h1>
        <p className="text-gray-400 mt-2">Explore all trading pairs</p>
      </div>

      {/* Market Categories */}
      <div className="flex space-x-4 mb-8">
        {['All', 'Spot', 'Futures', 'Options', 'ETF'].map(category => (
          <button
            key={category}
            className="px-4 py-2 bg-gray-800 text-gray-300 rounded-lg hover:bg-orange-500 hover:text-white transition-colors"
          >
            {category}
          </button>
        ))}
      </div>

      {/* Market Grid/List */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {markets.map((market, index) => (
            <div key={index} className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-orange-500 transition-colors">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-lg">{market.pair}</h3>
                <span className="px-2 py-1 bg-gray-700 text-xs rounded">{market.category}</span>
              </div>
              <div className="mb-4">
                <p className="text-2xl font-bold">${market.price}</p>
                <p className={`text-sm ${market.change.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>
                  {market.change}
                </p>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400 text-sm">Vol: {market.volume}</span>
                <button className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600">
                  Trade
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-700">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Pair</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Price</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">24h Change</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Volume</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Category</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {markets.map((market, index) => (
                  <tr key={index} className="hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap font-medium">
                      {market.pair}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      ${market.price}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm ${market.change.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>
                        {market.change}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-300">
                      {market.volume}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 bg-gray-700 text-xs rounded">{market.category}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button className="text-orange-500 hover:text-orange-400 mr-3">Trade</button>
                      <button className="text-gray-400 hover:text-white">Chart</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

const AdminDashboard = () => {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-orange-500">Admin Dashboard</h1>
        <p className="text-gray-400 mt-2">Complete administrative control</p>
      </div>

      {/* Admin Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Users</p>
              <p className="text-2xl font-bold mt-1">45,678</p>
            </div>
            <FiUsers className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">24h Volume</p>
              <p className="text-2xl font-bold mt-1">$156M</p>
            </div>
            <FiDollarSign className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Orders</p>
              <p className="text-2xl font-bold mt-1">12,345</p>
            </div>
            <FiActivity className="w-8 h-8 text-orange-500" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">System Health</p>
              <p className="text-2xl font-bold mt-1">99.9%</p>
            </div>
            <FiShield className="w-8 h-8 text-green-500" />
          </div>
        </div>
      </div>

      {/* Admin Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <button className="w-full py-3 px-4 bg-gray-700 text-left rounded-lg hover:bg-gray-600 flex items-center justify-between">
              <span>User Management</span>
              <span>→</span>
            </button>
            <button className="w-full py-3 px-4 bg-gray-700 text-left rounded-lg hover:bg-gray-600 flex items-center justify-between">
              <span>Trading Controls</span>
              <span>→</span>
            </button>
            <button className="w-full py-3 px-4 bg-gray-700 text-left rounded-lg hover:bg-gray-600 flex items-center justify-between">
              <span>Security Settings</span>
              <span>→</span>
            </button>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-bold mb-4">System Status</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">API Status</span>
              <span className="px-2 py-1 bg-green-500 text-white text-xs rounded">Online</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Database</span>
              <span className="px-2 py-1 bg-green-500 text-white text-xs rounded">Healthy</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Trading Engine</span>
              <span className="px-2 py-1 bg-green-500 text-white text-xs rounded">Running</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const LoginPage = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 bg-orange-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">T</span>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
            Sign in to TigerEx
          </h2>
          <p className="mt-2 text-center text-sm text-gray-400">
            Complete trading platform
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={(e) => { e.preventDefault(); onLogin(); }}>
          <div className="rounded-md shadow-sm space-y-4">
            <div>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-700 placeholder-gray-500 text-white bg-gray-800 focus:outline-none focus:ring-orange-500 focus:border-orange-500"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-700 placeholder-gray-500 text-white bg-gray-800 focus:outline-none focus:ring-orange-500 focus:border-orange-500"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-orange-500 hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
            >
              Sign in
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div className="text-sm">
              <a href="#" className="font-medium text-orange-500 hover:text-orange-400">
                Forgot your password?
              </a>
            </div>
            <div className="text-sm">
              <a href="#" className="font-medium text-orange-500 hover:text-orange-400">
                Create account
              </a>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CompleteWebApp;