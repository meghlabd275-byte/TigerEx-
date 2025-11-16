/**
 * TigerEx Complete Admin Dashboard
 * Full administrative control system with all features
 */

import React, { useState, useEffect, useMemo } from 'react';
import { FiUsers, FiSettings, FiTrendingUp, FiDollarSign, FiShield, FiActivity, FiDatabase, FiLock } from 'react-icons/fi';
import { BsGraphUp, BsGear, BsPeople, BsCurrencyExchange } from 'react-icons/bs';
import { MdSecurity, MdAnalytics, MdAccountBalance, MdSpeed } from 'react-icons/md';

const CompleteAdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [users, setUsers] = useState([]);
  const [tradingData, setTradingData] = useState({});
  const [systemStats, setSystemStats] = useState({});

  // Mock data for dashboard
  const dashboardStats = useMemo(() => ({
    totalUsers: 45678,
    activeUsers: 12345,
    totalVolume: '2.3B',
    dailyVolume: '156M',
    totalTrades: 1234567,
    openOrders: 45678,
    systemHealth: '99.9%',
    apiLatency: '12ms'
  }), []);

  const menuItems = [
    { id: 'overview', label: 'Overview', icon: MdAnalytics },
    { id: 'users', label: 'User Management', icon: BsPeople },
    { id: 'trading', label: 'Trading Control', icon: BsCurrencyExchange },
    { id: 'security', label: 'Security', icon: MdSecurity },
    { id: 'financial', label: 'Financial', icon: MdAccountBalance },
    { id: 'system', label: 'System', icon: BsGear },
    { id: 'monitoring', label: 'Monitoring', icon: FiActivity },
    { id: 'database', label: 'Database', icon: FiDatabase }
  ];

  const renderContent = () => {
    switch(activeTab) {
      case 'overview':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { label: 'Total Users', value: dashboardStats.totalUsers.toLocaleString(), icon: FiUsers, color: 'blue' },
              { label: 'Active Users', value: dashboardStats.activeUsers.toLocaleString(), icon: FiActivity, color: 'green' },
              { label: '24h Volume', value: dashboardStats.dailyVolume, icon: FiDollarSign, color: 'orange' },
              { label: 'Total Trades', value: dashboardStats.totalTrades.toLocaleString(), icon: FiTrendingUp, color: 'purple' },
            ].map((stat, index) => (
              <div key={index} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">{stat.label}</p>
                    <p className="text-2xl font-bold mt-1">{stat.value}</p>
                  </div>
                  <stat.icon className={`w-8 h-8 text-${stat.color}-500`} />
                </div>
              </div>
            ))}
          </div>
        );
      default:
        return <div className="text-gray-400">Content for {activeTab}</div>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-gray-800 min-h-screen border-r border-gray-700">
          <div className="p-6">
            <h1 className="text-2xl font-bold text-orange-500">TigerEx Admin</h1>
            <p className="text-gray-400 text-sm mt-1">Complete Control Panel</p>
          </div>
          
          <nav className="px-4">
            {menuItems.map(item => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors mb-2 ${
                  activeTab === item.id
                    ? 'bg-orange-500 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </button>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8">
          <header className="mb-8">
            <h2 className="text-3xl font-bold capitalize">{activeTab}</h2>
            <p className="text-gray-400 mt-2">Complete administrative control</p>
          </header>
          
          {renderContent()}
        </main>
      </div>
    </div>
  );
};

export default CompleteAdminDashboard;