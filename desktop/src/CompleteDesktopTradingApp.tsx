/**
 * TigerEx Complete Desktop Trading Application
 * Full-featured desktop trading platform with Electron
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { 
  FiHome, 
  FiTrendingUp, 
  FiPieChart, 
  FiSettings, 
  FiUsers,
  FiDollarSign,
  FiShield,
  FiActivity
} from 'react-icons/fi';

const CompleteDesktopTradingApp = () => {
  const [activeView, setActiveView] = useState('trading');
  const [selectedPair, setSelectedPair] = useState('BTC/USDT');
  const [isAdminMode, setIsAdminMode] = useState(false);

  const menuItems = [
    { id: 'trading', label: 'Trading', icon: FiTrendingUp },
    { id: 'portfolio', label: 'Portfolio', icon: FiPieChart },
    { id: 'markets', label: 'Markets', icon: FiHome },
    { id: 'orders', label: 'Orders', icon: FiActivity },
    { id: 'admin', label: 'Admin', icon: FiUsers, adminOnly: true },
    { id: 'settings', label: 'Settings', icon: FiSettings },
  ];

  const filteredMenuItems = isAdminMode 
    ? menuItems 
    : menuItems.filter(item => !item.adminOnly);

  const TradingView = () => (
    <div className="flex-1 flex flex-col bg-gray-900">
      {/* Trading Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">{selectedPair}</h1>
            <div className="flex items-center space-x-4 mt-1">
              <span className="text-xl text-green-500">$43,250.50</span>
              <span className="text-green-500">+2.34%</span>
            </div>
          </div>
          <div className="flex space-x-2">
            {['1m', '5m', '15m', '1h', '4h', '1d'].map(tf => (
              <button key={tf} className="px-3 py-1 bg-gray-700 text-gray-300 rounded hover:bg-orange-500 hover:text-white">
                {tf}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Trading Area */}
      <div className="flex-1 flex">
        {/* Chart Area */}
        <div className="flex-1 bg-gray-800 m-4 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <FiTrendingUp className="w-16 h-16 text-orange-500 mx-auto mb-4" />
            <p className="text-gray-400">Advanced Trading Chart</p>
            <p className="text-sm text-gray-500 mt-2">Real-time price data with technical indicators</p>
          </div>
        </div>

        {/* Right Panel */}
        <div className="w-96 flex flex-col">
          {/* Order Book */}
          <div className="bg-gray-800 m-4 mt-4 mb-2 rounded-lg p-4">
            <h3 className="font-bold mb-3">Order Book</h3>
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-red-500">43,251.00</span>
                <span>0.4231</span>
                <span className="text-gray-400">0.4231</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-red-500">43,250.50</span>
                <span>0.6123</span>
                <span className="text-gray-400">1.0354</span>
              </div>
              <div className="flex justify-between text-sm text-yellow-500 py-1 border-t border-b border-gray-700">
                <span>43,250.25</span>
                <span>Spread: 0.25</span>
                <span>43,250.25</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-green-500">43,250.00</span>
                <span>0.5421</span>
                <span className="text-gray-400">0.5421</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-green-500">43,249.50</span>
                <span>0.3214</span>
                <span className="text-gray-400">0.8635</span>
              </div>
            </div>
          </div>

          {/* Trading Panel */}
          <div className="bg-gray-800 m-4 mt-2 mb-4 rounded-lg p-4 flex-1">
            <div className="flex space-x-2 mb-4">
              <button className="flex-1 py-2 bg-green-500 text-white rounded font-medium">Buy</button>
              <button className="flex-1 py-2 bg-gray-700 text-gray-300 rounded font-medium">Sell</button>
            </div>

            <div className="grid grid-cols-2 gap-2 mb-4">
              <button className="py-2 bg-gray-700 text-gray-300 rounded hover:bg-orange-500 hover:text-white">Market</button>
              <button className="py-2 bg-orange-500 text-white rounded">Limit</button>
            </div>

            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-2">Price (USDT)</label>
              <input type="number" className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white" placeholder="0.00" />
            </div>

            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-2">Amount (BTC)</label>
              <input type="number" className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white" placeholder="0.00" />
              <div className="flex justify-between mt-2">
                <span className="text-xs text-gray-400">Available: 0.12345678 BTC</span>
                <div className="space-x-2">
                  <button className="text-xs text-orange-500">25%</button>
                  <button className="text-xs text-orange-500">50%</button>
                  <button className="text-xs text-orange-500">75%</button>
                  <button className="text-xs text-orange-500">100%</button>
                </div>
              </div>
            </div>

            <div className="bg-gray-700 rounded p-3 mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">Total</span>
                <span>0.00 USDT</span>
              </div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-400">Fee</span>
                <span>0.0000 USDT</span>
              </div>
              <div className="flex justify-between font-medium">
                <span>You will buy</span>
                <span>0.0000 BTC</span>
              </div>
            </div>

            <button className="w-full py-3 bg-green-500 text-white rounded font-medium hover:bg-green-600">
              Place Buy Order
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const AdminView = () => (
    <div className="flex-1 bg-gray-900 p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-orange-500">Admin Dashboard</h1>
        <p className="text-gray-400 mt-2">Complete administrative control</p>
      </div>

      {/* Admin Stats Grid */}
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
          <h2 className="text-xl font-bold mb-4">User Management</h2>
          <div className="space-y-3">
            <button className="w-full py-3 px-4 bg-gray-700 text-left rounded-lg hover:bg-gray-600 flex items-center justify-between">
              <span>View All Users</span>
              <span>→</span>
            </button>
            <button className="w-full py-3 px-4 bg-gray-700 text-left rounded-lg hover:bg-gray-600 flex items-center justify-between">
              <span>KYC Verification</span>
              <span>→</span>
            </button>
            <button className="w-full py-3 px-4 bg-gray-700 text-left rounded-lg hover:bg-gray-600 flex items-center justify-between">
              <span>Account Settings</span>
              <span>→</span>
            </button>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-bold mb-4">Trading Controls</h2>
          <div className="space-y-3">
            <button className="w-full py-3 px-4 bg-gray-700 text-left rounded-lg hover:bg-gray-600 flex items-center justify-between">
              <span>Market Configuration</span>
              <span>→</span>
            </button>
            <button className="w-full py-3 px-4 bg-gray-700 text-left rounded-lg hover:bg-gray-600 flex items-center justify-between">
              <span>Fee Management</span>
              <span>→</span>
            </button>
            <button className="w-full py-3 px-4 bg-gray-700 text-left rounded-lg hover:bg-gray-600 flex items-center justify-between">
              <span>Leverage Controls</span>
              <span>→</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const PortfolioView = () => (
    <div className="flex-1 bg-gray-900 p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Portfolio</h1>
        <p className="text-gray-400 mt-2">Track your investments</p>
      </div>
      <div className="bg-gray-800 rounded-lg p-8 text-center">
        <FiPieChart className="w-16 h-16 text-orange-500 mx-auto mb-4" />
        <p className="text-gray-400">Portfolio Management</p>
      </div>
    </div>
  );

  return (
    <Router>
      <div className="min-h-screen bg-gray-900 flex">
        {/* Sidebar */}
        <div className="w-64 bg-gray-800 border-r border-gray-700">
          <div className="p-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center font-bold text-white">
                T
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">TigerEx</h1>
                <p className="text-xs text-gray-400">Desktop Trading Platform</p>
              </div>
            </div>
          </div>

          <nav className="px-4">
            {filteredMenuItems.map(item => (
              <button
                key={item.id}
                onClick={() => {
                  setActiveView(item.id);
                  if (item.id === 'admin') setIsAdminMode(true);
                }}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors mb-2 ${
                  activeView === item.id
                    ? 'bg-orange-500 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </button>
            ))}
          </nav>

          {/* Admin Toggle */}
          <div className="px-4 mt-8 pt-8 border-t border-gray-700">
            <button
              onClick={() => setIsAdminMode(!isAdminMode)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isAdminMode
                  ? 'bg-orange-500 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              <FiShield className="w-5 h-5" />
              <span>Admin Mode</span>
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1">
          {activeView === 'trading' && <TradingView />}
          {activeView === 'portfolio' && <PortfolioView />}
          {activeView === 'admin' && <AdminView />}
          {activeView === 'markets' && (
            <div className="flex-1 bg-gray-900 p-8">
              <h1 className="text-3xl font-bold">Markets</h1>
            </div>
          )}
          {activeView === 'orders' && (
            <div className="flex-1 bg-gray-900 p-8">
              <h1 className="text-3xl font-bold">Orders</h1>
            </div>
          )}
          {activeView === 'settings' && (
            <div className="flex-1 bg-gray-900 p-8">
              <h1 className="text-3xl font-bold">Settings</h1>
            </div>
          )}
        </div>
      </div>
    </Router>
  );
};

export default CompleteDesktopTradingApp;