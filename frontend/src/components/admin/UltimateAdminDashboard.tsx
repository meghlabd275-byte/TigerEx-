/**
 * TigerEx React Component
 * @file UltimateAdminDashboard.tsx
 * @description React component for TigerEx
 * @author TigerEx Development Team
 */
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users, Shield, Settings, TrendingUp, DollarSign, Activity,
  Bell, Search, Filter, RefreshCw, Plus, Edit, Trash2, Eye,
  CheckCircle, XCircle, Clock, AlertTriangle, ChevronDown,
  BarChart3, PieChart, Wallet, Coins, Building, Network,
  Bot, Lock, FileText, Download, Upload, Globe, Zap,
  Pause, Play, Square, AlertCircle, UserCheck, UserX,
  Key, Database, Server, Cpu, HardDrive, Wifi, WifiOff,
} from 'lucide-react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, Title, Tooltip, Legend, ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, Title, Tooltip, Legend, ArcElement
);

// Types
interface User {
  id: string;
  email: string;
  username: string;
  role: string;
  status: 'active' | 'suspended' | 'banned';
  kycLevel: number;
  createdAt: string;
  lastLogin?: string;
  balance?: number;
}

interface Token {
  id: string;
  symbol: string;
  name: string;
  status: 'active' | 'paused' | 'delisted';
  price: number;
  volume24h: number;
  marketCap?: number;
}

interface TradingPair {
  id: string;
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  status: 'active' | 'paused' | 'halted';
  makerFee: number;
  takerFee: number;
  volume24h: number;
}

interface SystemStats {
  totalUsers: number;
  activeUsers: number;
  totalVolume24h: number;
  totalTrades24h: number;
  openOrders: number;
  pendingWithdrawals: number;
  systemHealth: 'healthy' | 'degraded' | 'critical';
  activeConnections: number;
}

// Permission levels
type Permission = 
  | 'view_users' | 'create_users' | 'edit_users' | 'delete_users' | 'suspend_users'
  | 'view_trading' | 'control_trading' | 'pause_trading' | 'halt_trading'
  | 'view_financials' | 'process_withdrawals' | 'manage_funds'
  | 'list_tokens' | 'delist_tokens' | 'manage_pairs'
  | 'system_config' | 'view_logs' | 'manage_security' | 'admin_all';

interface AdminUser {
  id: string;
  email: string;
  username: string;
  role: 'super_admin' | 'admin' | 'moderator' | 'support';
  permissions: Permission[];
}

// Props
interface UltimateAdminDashboardProps {
  adminUser: AdminUser;
  apiBaseUrl?: string;
}

export function UltimateAdminDashboard({
  adminUser,
  apiBaseUrl = '/api/admin',
}: UltimateAdminDashboardProps) {
  // State
  const [activeTab, setActiveTab] = useState('overview');
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [tokens, setTokens] = useState<Token[]>([]);
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [modalContent, setModalContent] = useState<any>(null);
  const [notification, setNotification] = useState<{ type: string; message: string } | null>(null);
  const [tradingHalted, setTradingHalted] = useState(false);

  // Check permissions
  const hasPermission = useCallback((permission: Permission): boolean => {
    if (adminUser.role === 'super_admin') return true;
    return adminUser.permissions.includes(permission) || adminUser.permissions.includes('admin_all');
  }, [adminUser]);

  // Fetch data
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch all data in parallel
      const [statsRes, usersRes, tokensRes, pairsRes] = await Promise.all([
        fetch(`${apiBaseUrl}/system/status`, { headers }).catch(() => null),
        fetch(`${apiBaseUrl}/users?limit=100`, { headers }).catch(() => null),
        fetch(`${apiBaseUrl}/tokens`, { headers }).catch(() => null),
        fetch(`${apiBaseUrl}/trading-pairs`, { headers }).catch(() => null),
      ]);

      if (statsRes?.ok) {
        const data = await statsRes.json();
        setSystemStats(data);
      }

      if (usersRes?.ok) {
        const data = await usersRes.json();
        setUsers(data.users || []);
      }

      if (tokensRes?.ok) {
        const data = await tokensRes.json();
        setTokens(data.tokens || []);
      }

      if (pairsRes?.ok) {
        const data = await pairsRes.json();
        setTradingPairs(data);
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Use mock data for demo
      setMockData();
    }
  };

  const setMockData = () => {
    setSystemStats({
      totalUsers: 125000,
      activeUsers: 15420,
      totalVolume24h: 895000000,
      totalTrades24h: 458000,
      openOrders: 32000,
      pendingWithdrawals: 156,
      systemHealth: 'healthy',
      activeConnections: 8420,
    });

    setUsers([
      { id: '1', email: 'user1@example.com', username: 'trader1', role: 'user', status: 'active', kycLevel: 2, createdAt: '2024-01-01', balance: 5000 },
      { id: '2', email: 'user2@example.com', username: 'trader2', role: 'user', status: 'suspended', kycLevel: 1, createdAt: '2024-01-02', balance: 1200 },
      { id: '3', email: 'user3@example.com', username: 'whale1', role: 'vip', status: 'active', kycLevel: 3, createdAt: '2024-01-03', balance: 150000 },
    ]);

    setTokens([
      { id: '1', symbol: 'BTC', name: 'Bitcoin', status: 'active', price: 67250.00, volume24h: 28500000000 },
      { id: '2', symbol: 'ETH', name: 'Ethereum', status: 'active', price: 3450.00, volume24h: 15200000000 },
      { id: '3', symbol: 'TIGER', name: 'TigerEx Token', status: 'active', price: 0.85, volume24h: 45000000 },
    ]);

    setTradingPairs([
      { id: '1', symbol: 'BTCUSDT', baseAsset: 'BTC', quoteAsset: 'USDT', status: 'active', makerFee: 0.001, takerFee: 0.001, volume24h: 1250000000 },
      { id: '2', symbol: 'ETHUSDT', baseAsset: 'ETH', quoteAsset: 'USDT', status: 'active', makerFee: 0.001, takerFee: 0.001, volume24h: 850000000 },
    ]);

    setLoading(false);
  };

  // Show notification
  const showNotification = (type: string, message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  // User actions
  const handleUserAction = async (userId: string, action: 'suspend' | 'activate' | 'ban' | 'delete') => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(`${apiBaseUrl}/users/${userId}/${action === 'activate' ? 'status' : action}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: action === 'activate' ? 'active' : action }),
      });

      if (response.ok) {
        showNotification('success', `User ${action} successful`);
        fetchDashboardData();
      } else {
        showNotification('error', `Failed to ${action} user`);
      }
    } catch (error) {
      showNotification('error', `Error: ${error}`);
    }
  };

  // Trading control
  const handleTradingControl = async (action: 'pause' | 'resume' | 'halt', symbol?: string) => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(`${apiBaseUrl}/trading/${action}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symbol, reason: `Admin ${action}` }),
      });

      if (response.ok) {
        setTradingHalted(action === 'halt' || action === 'pause');
        showNotification('success', `Trading ${action}${symbol ? ` for ${symbol}` : ''}`);
        fetchDashboardData();
      }
    } catch (error) {
      showNotification('error', `Failed to ${action} trading`);
    }
  };

  // Token actions
  const handleTokenAction = async (symbol: string, action: 'pause' | 'activate' | 'delist') => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(`${apiBaseUrl}/tokens/${symbol}`, {
        method: action === 'delist' ? 'DELETE' : 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: action === 'activate' ? 'active' : action }),
      });

      if (response.ok) {
        showNotification('success', `Token ${action} successful`);
        fetchDashboardData();
      }
    } catch (error) {
      showNotification('error', `Failed to ${action} token`);
    }
  };

  // Tabs configuration
  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3, permission: null },
    { id: 'users', label: 'Users', icon: Users, permission: 'view_users' as Permission },
    { id: 'trading', label: 'Trading', icon: TrendingUp, permission: 'view_trading' as Permission },
    { id: 'tokens', label: 'Tokens', icon: Coins, permission: 'view_trading' as Permission },
    { id: 'financials', label: 'Financials', icon: DollarSign, permission: 'view_financials' as Permission },
    { id: 'security', label: 'Security', icon: Shield, permission: 'manage_security' as Permission },
    { id: 'system', label: 'System', icon: Server, permission: 'system_config' as Permission },
    { id: 'settings', label: 'Settings', icon: Settings, permission: 'system_config' as Permission },
  ];

  // Render stat card
  const StatCard = ({ title, value, change, icon: Icon, color }: any) => (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="bg-white rounded-xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {change && (
            <p className={`text-sm mt-1 ${change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {change >= 0 ? '↑' : '↓'} {Math.abs(change)}%
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg bg-${color}-100`}>
          <Icon className={`w-6 h-6 text-${color}-500`} />
        </div>
      </div>
    </motion.div>
  );

  // Render overview
  const renderOverview = () => (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Users"
          value={systemStats?.totalUsers.toLocaleString() || '0'}
          change={12.5}
          icon={Users}
          color="blue"
        />
        <StatCard
          title="Active Users (24h)"
          value={systemStats?.activeUsers.toLocaleString() || '0'}
          change={8.3}
          icon={Activity}
          color="green"
        />
        <StatCard
          title="24h Volume"
          value={`$${((systemStats?.totalVolume24h || 0) / 1e9).toFixed(2)}B`}
          change={15.2}
          icon={DollarSign}
          color="purple"
        />
        <StatCard
          title="24h Trades"
          value={systemStats?.totalTrades24h.toLocaleString() || '0'}
          change={22.1}
          icon={TrendingUp}
          color="orange"
        />
      </div>

      {/* System Status */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold mb-4">System Status</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${
              systemStats?.systemHealth === 'healthy' ? 'bg-green-500' :
              systemStats?.systemHealth === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
            }`} />
            <span className="text-sm capitalize">{systemStats?.systemHealth || 'Unknown'}</span>
          </div>
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-gray-400" />
            <span className="text-sm">{systemStats?.activeConnections?.toLocaleString() || 0} connections</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-gray-400" />
            <span className="text-sm">{systemStats?.openOrders?.toLocaleString() || 0} open orders</span>
          </div>
          <div className="flex items-center gap-2">
            <Wallet className="w-4 h-4 text-gray-400" />
            <span className="text-sm">{systemStats?.pendingWithdrawals || 0} pending withdrawals</span>
          </div>
        </div>
      </div>

      {/* Trading Control */}
      {hasPermission('control_trading') && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold mb-4">Trading Control</h3>
          <div className="flex flex-wrap gap-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleTradingControl('pause')}
              className="flex items-center gap-2 px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200"
            >
              <Pause className="w-4 h-4" />
              Pause All
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleTradingControl('halt')}
              className="flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
            >
              <Square className="w-4 h-4" />
              Emergency Halt
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleTradingControl('resume')}
              className="flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200"
            >
              <Play className="w-4 h-4" />
              Resume All
            </motion.button>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {[
            { action: 'User Registration', user: 'trader123@example.com', time: '2 min ago', type: 'user' },
            { action: 'Large Withdrawal', user: 'whale@example.com', time: '5 min ago', type: 'warning' },
            { action: 'KYC Approved', user: 'verified@example.com', time: '10 min ago', type: 'success' },
            { action: 'Support Ticket', user: 'issue@example.com', time: '15 min ago', type: 'support' },
          ].map((activity, i) => (
            <div key={i} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${
                  activity.type === 'warning' ? 'bg-yellow-100' :
                  activity.type === 'success' ? 'bg-green-100' :
                  activity.type === 'support' ? 'bg-blue-100' : 'bg-gray-100'
                }`}>
                  {activity.type === 'warning' ? <AlertTriangle className="w-4 h-4 text-yellow-500" /> :
                   activity.type === 'success' ? <CheckCircle className="w-4 h-4 text-green-500" /> :
                   activity.type === 'support' ? <Bell className="w-4 h-4 text-blue-500" /> :
                   <Users className="w-4 h-4 text-gray-500" />}
                </div>
                <div>
                  <p className="text-sm font-medium">{activity.action}</p>
                  <p className="text-xs text-gray-500">{activity.user}</p>
                </div>
              </div>
              <span className="text-xs text-gray-400">{activity.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Render users tab
  const renderUsers = () => (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="flex flex-wrap items-center gap-4">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search users..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500"
          />
        </div>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="suspended">Suspended</option>
          <option value="banned">Banned</option>
        </select>
        {hasPermission('create_users') && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
          >
            <Plus className="w-4 h-4" />
            Add User
          </motion.button>
        )}
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">KYC</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {users
              .filter(user => 
                (filterStatus === 'all' || user.status === filterStatus) &&
                (searchTerm === '' || user.email.includes(searchTerm) || user.username.includes(searchTerm))
              )
              .map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-400 to-amber-400 flex items-center justify-center text-white font-medium">
                        {user.username.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <p className="text-sm font-medium">{user.username}</p>
                        <p className="text-xs text-gray-500">{user.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      user.role === 'vip' ? 'bg-purple-100 text-purple-700' :
                      user.role === 'admin' ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      user.status === 'active' ? 'bg-green-100 text-green-700' :
                      user.status === 'suspended' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-1">
                      {Array.from({ length: 3 }).map((_, i) => (
                        <div
                          key={i}
                          className={`w-2 h-2 rounded-full ${
                            i < user.kycLevel ? 'bg-green-500' : 'bg-gray-200'
                          }`}
                        />
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      {hasPermission('edit_users') && (
                        <button
                          onClick={() => handleUserAction(user.id, user.status === 'active' ? 'suspend' : 'activate')}
                          className={`p-2 rounded-lg ${
                            user.status === 'active' ? 'text-yellow-500 hover:bg-yellow-50' : 'text-green-500 hover:bg-green-50'
                          }`}
                          title={user.status === 'active' ? 'Suspend' : 'Activate'}
                        >
                          {user.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        </button>
                      )}
                      {hasPermission('suspend_users') && (
                        <button
                          onClick={() => handleUserAction(user.id, 'ban')}
                          className="p-2 rounded-lg text-red-500 hover:bg-red-50"
                          title="Ban User"
                        >
                          <UserX className="w-4 h-4" />
                        </button>
                      )}
                      {hasPermission('delete_users') && (
                        <button
                          onClick={() => handleUserAction(user.id, 'delete')}
                          className="p-2 rounded-lg text-gray-500 hover:bg-gray-50"
                          title="Delete User"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  // Render tokens tab
  const renderTokens = () => (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-xl font-bold">Token Management</h2>
        {hasPermission('list_tokens') && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
          >
            <Plus className="w-4 h-4" />
            List New Token
          </motion.button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tokens.map((token) => (
          <motion.div
            key={token.id}
            whileHover={{ scale: 1.02 }}
            className="bg-white rounded-xl p-6 shadow-sm border border-gray-100"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-400 to-amber-400 flex items-center justify-center text-white font-bold">
                  {token.symbol.charAt(0)}
                </div>
                <div>
                  <p className="font-medium">{token.symbol}</p>
                  <p className="text-xs text-gray-500">{token.name}</p>
                </div>
              </div>
              <span className={`px-2 py-1 text-xs rounded-full ${
                token.status === 'active' ? 'bg-green-100 text-green-700' :
                token.status === 'paused' ? 'bg-yellow-100 text-yellow-700' :
                'bg-red-100 text-red-700'
              }`}>
                {token.status}
              </span>
            </div>
            
            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Price</span>
                <span className="font-medium">${token.price.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">24h Volume</span>
                <span className="font-medium">${(token.volume24h / 1e6).toFixed(2)}M</span>
              </div>
            </div>

            <div className="flex gap-2">
              {hasPermission('manage_pairs') && (
                <>
                  <button
                    onClick={() => handleTokenAction(token.symbol, token.status === 'active' ? 'pause' : 'activate')}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium ${
                      token.status === 'active' ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200' :
                      'bg-green-100 text-green-700 hover:bg-green-200'
                    }`}
                  >
                    {token.status === 'active' ? 'Pause' : 'Activate'}
                  </button>
                  {hasPermission('delist_tokens') && (
                    <button
                      onClick={() => handleTokenAction(token.symbol, 'delist')}
                      className="flex-1 py-2 rounded-lg text-sm font-medium bg-red-100 text-red-700 hover:bg-red-200"
                    >
                      Delist
                    </button>
                  )}
                </>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );

  // Render trading tab
  const renderTrading = () => (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-xl font-bold">Trading Pairs</h2>
        {hasPermission('manage_pairs') && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
          >
            <Plus className="w-4 h-4" />
            Add Trading Pair
          </motion.button>
        )}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pair</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">24h Volume</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Maker Fee</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Taker Fee</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {tradingPairs.map((pair) => (
              <tr key={pair.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    <div className="flex">
                      <div className="w-6 h-6 rounded-full bg-orange-400 border-2 border-white" />
                      <div className="w-6 h-6 rounded-full bg-gray-300 -ml-2" />
                    </div>
                    <span className="font-medium">{pair.symbol}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    pair.status === 'active' ? 'bg-green-100 text-green-700' :
                    pair.status === 'paused' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {pair.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">${(pair.volume24h / 1e6).toFixed(2)}M</td>
                <td className="px-6 py-4 whitespace-nowrap">{(pair.makerFee * 100).toFixed(2)}%</td>
                <td className="px-6 py-4 whitespace-nowrap">{(pair.takerFee * 100).toFixed(2)}%</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleTradingControl(pair.status === 'active' ? 'pause' : 'resume', pair.symbol)}
                      className={`p-2 rounded-lg ${
                        pair.status === 'active' ? 'text-yellow-500 hover:bg-yellow-50' : 'text-green-500 hover:bg-green-50'
                      }`}
                    >
                      {pair.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    </button>
                    <button className="p-2 rounded-lg text-gray-500 hover:bg-gray-50">
                      <Edit className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  // Render settings tab
  const renderSettings = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold mb-4">Admin Profile</h3>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={adminUser.email}
                readOnly
                className="w-full px-4 py-2 border border-gray-200 rounded-lg bg-gray-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
              <input
                type="text"
                value={adminUser.role}
                readOnly
                className="w-full px-4 py-2 border border-gray-200 rounded-lg bg-gray-50 capitalize"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Permissions</label>
            <div className="flex flex-wrap gap-2">
              {adminUser.permissions.map((perm) => (
                <span key={perm} className="px-2 py-1 text-xs bg-orange-100 text-orange-700 rounded-full">
                  {perm}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold mb-4">Security Settings</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Two-Factor Authentication</p>
              <p className="text-sm text-gray-500">Add an extra layer of security</p>
            </div>
            <button className="px-4 py-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200">
              Enable
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Session Management</p>
              <p className="text-sm text-gray-500">Manage active sessions</p>
            </div>
            <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
              View Sessions
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-orange-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-500 to-amber-500 flex items-center justify-center">
                  <Shield className="w-5 h-5 text-white" />
                </div>
                <span className="font-bold text-xl">TigerEx Admin</span>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <button className="p-2 text-gray-500 hover:text-gray-700 relative">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              </button>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-400 to-amber-400 flex items-center justify-center text-white text-sm font-medium">
                  {adminUser.username.charAt(0).toUpperCase()}
                </div>
                <span className="text-sm font-medium">{adminUser.username}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex overflow-x-auto gap-2 mb-6 pb-2">
          {tabs
            .filter(tab => !tab.permission || hasPermission(tab.permission))
            .map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-colors ${
                  activeTab === tab.id
                    ? 'bg-orange-500 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-100'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {activeTab === 'overview' && renderOverview()}
            {activeTab === 'users' && renderUsers()}
            {activeTab === 'tokens' && renderTokens()}
            {activeTab === 'trading' && renderTrading()}
            {activeTab === 'settings' && renderSettings()}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Notification */}
      <AnimatePresence>
        {notification && (
          <motion.div
            initial={{ opacity: 0, y: 50, x: '-50%' }}
            animate={{ opacity: 1, y: 0, x: '-50%' }}
            exit={{ opacity: 0 }}
            className={`fixed bottom-4 left-1/2 px-6 py-3 rounded-lg shadow-lg ${
              notification.type === 'success' ? 'bg-green-500' : 'bg-red-500'
            } text-white`}
          >
            {notification.message}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default UltimateAdminDashboard;