import React, { useState, useEffect } from 'react';
import { 
  Users, 
  TrendingUp, 
  DollarSign, 
  Activity, 
  AlertCircle, 
  Settings, 
  Shield, 
  Database, 
  Globe, 
  Zap, 
  BarChart3, 
  PieChart, 
  Lock, 
  Eye, 
  Download, 
  RefreshCw, 
  Filter, 
  Search,
  Bell,
  User,
  ChevronDown,
  ChevronRight,
  Plus,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  ArrowUp,
  ArrowDown,
  MoreVertical
} from 'lucide-react';

interface DashboardStats {
  totalUsers: number;
  activeTraders: number;
  totalVolume: string;
  revenue24h: string;
  pendingVerifications: number;
  systemStatus: 'operational' | 'degraded' | 'down';
  growth24h: number;
  activeOrders: number;
  totalBalance: string;
}

interface RecentActivity {
  id: string;
  type: string;
  user: string;
  action: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error';
  amount?: string;
}

interface UserTable {
  id: string;
  name: string;
  email: string;
  role: string;
  status: 'active' | 'suspended' | 'pending';
  balance: string;
  lastActive: string;
  kycStatus: 'verified' | 'pending' | 'rejected';
  joinDate: string;
}

const AdminPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [timeRange, setTimeRange] = useState('24h');

  const [stats, setStats] = useState<DashboardStats>({
    totalUsers: 15420,
    activeTraders: 3247,
    totalVolume: '$125.4M',
    revenue24h: '$42,350',
    pendingVerifications: 23,
    systemStatus: 'operational',
    growth24h: 12.5,
    activeOrders: 892,
    totalBalance: '$2.4B'
  });

  const recentActivity: RecentActivity[] = [
    { id: '1', type: 'user', user: 'john_trader', action: 'Completed KYC verification', timestamp: '2 minutes ago', status: 'success', amount: '$1,000' },
    { id: '2', type: 'trade', user: 'alice_crypto', action: 'Placed large BTC order', timestamp: '5 minutes ago', status: 'success', amount: '$50,000' },
    { id: '3', type: 'security', user: 'system', action: 'Detected unusual login pattern', timestamp: '12 minutes ago', status: 'warning' },
    { id: '4', type: 'ai', user: 'ai_engine', action: 'Generated trading signal', timestamp: '15 minutes ago', status: 'success' },
    { id: '5', type: 'withdrawal', user: 'bob_trader', action: 'Withdrawal processed', timestamp: '18 minutes ago', status: 'success', amount: '$5,000' },
    { id: '6', type: 'deposit', user: 'charlie_invest', action: 'Large deposit received', timestamp: '22 minutes ago', status: 'success', amount: '$100,000' },
    { id: '7', type: 'error', user: 'system', action: 'API rate limit exceeded', timestamp: '25 minutes ago', status: 'error' },
    { id: '8', type: 'user', user: 'diana_trader', action: 'Account suspended', timestamp: '30 minutes ago', status: 'warning' }
  ];

  const users: UserTable[] = [
    { id: '1', name: 'John Doe', email: 'john@example.com', role: 'Admin', status: 'active', balance: '$125,450', lastActive: '2 hours ago', kycStatus: 'verified', joinDate: '2023-01-15' },
    { id: '2', name: 'Jane Smith', email: 'jane@example.com', role: 'Trader', status: 'active', balance: '$45,230', lastActive: '5 minutes ago', kycStatus: 'verified', joinDate: '2023-03-22' },
    { id: '3', name: 'Bob Wilson', email: 'bob@example.com', role: 'User', status: 'suspended', balance: '$12,100', lastActive: '1 day ago', kycStatus: 'pending', joinDate: '2023-05-10' },
    { id: '4', name: 'Alice Johnson', email: 'alice@example.com', role: 'VIP Trader', status: 'active', balance: '$890,000', lastActive: '1 hour ago', kycStatus: 'verified', joinDate: '2022-11-30' },
    { id: '5', name: 'Charlie Brown', email: 'charlie@example.com', role: 'User', status: 'active', balance: '$8,450', lastActive: '3 hours ago', kycStatus: 'verified', joinDate: '2023-07-18' },
    { id: '6', name: 'Diana Prince', email: 'diana@example.com', role: 'Trader', status: 'active', balance: '$234,600', lastActive: '30 minutes ago', kycStatus: 'rejected', joinDate: '2023-02-14' },
    { id: '7', name: 'Edward Norton', email: 'edward@example.com', role: 'User', status: 'pending', balance: '$2,300', lastActive: '2 days ago', kycStatus: 'pending', joinDate: '2023-09-05' },
    { id: '8', name: 'Fiona Apple', email: 'fiona@example.com', role: 'VIP Trader', status: 'active', balance: '$1,245,000', lastActive: '45 minutes ago', kycStatus: 'verified', joinDate: '2022-08-22' }
  ];

  const tabs = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'users', name: 'Users', icon: Users },
    { id: 'trading', name: 'Trading', icon: TrendingUp },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'analytics', name: 'Analytics', icon: PieChart },
    { id: 'settings', name: 'Settings', icon: Settings }
  ];

  const timeRanges = ['1h', '24h', '7d', '30d', '90d'];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Shield size={16} className="text-white" />
                </div>
                <h1 className="text-xl font-bold text-gray-900">Admin Dashboard</h1>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                Super Admin
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="relative">
                <select 
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value)}
                  className="pl-8 pr-4 py-2 bg-white border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                >
                  {timeRanges.map(range => (
                    <option key={range} value={range}>{range}</option>
                  ))}
                </select>
                <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={14} />
              </div>
              
              <button className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <Bell size={20} className="text-gray-600" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              
              <div className="flex items-center space-x-2 px-3 py-2 bg-gray-100 rounded-lg">
                <div className="w-6 h-6 bg-blue-600 rounded-full"></div>
                <span className="text-sm font-medium text-gray-700">Admin User</span>
                <ChevronDown size={14} className="text-gray-500" />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon size={16} />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* System Status Banner */}
            <div className={`rounded-lg p-4 ${
              stats.systemStatus === 'operational' 
                ? 'bg-green-50 border border-green-200' 
                : stats.systemStatus === 'degraded'
                ? 'bg-yellow-50 border border-yellow-200'
                : 'bg-red-50 border border-red-200'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    stats.systemStatus === 'operational' ? 'bg-green-500' : 
                    stats.systemStatus === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
                  }`}></div>
                  <div>
                    <h3 className={`font-semibold ${
                      stats.systemStatus === 'operational' ? 'text-green-900' : 
                      stats.systemStatus === 'degraded' ? 'text-yellow-900' : 'text-red-900'
                    }`}>
                      System Status: {stats.systemStatus.toUpperCase()}
                    </h3>
                    <p className={`text-sm ${
                      stats.systemStatus === 'operational' ? 'text-green-700' : 
                      stats.systemStatus === 'degraded' ? 'text-yellow-700' : 'text-red-700'
                    }`}>
                      All systems are operating normally
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Uptime</p>
                    <p className="text-lg font-semibold text-gray-900">99.99%</p>
                  </div>
                  <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors">
                    View Details
                  </button>
                </div>
              </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Users size={24} className="text-blue-600" />
                  </div>
                  <div className="flex items-center text-green-600 text-sm">
                    <ArrowUp size={16} />
                    <span>{stats.growth24h}%</span>
                  </div>
                </div>
                <h3 className="text-2xl font-bold text-gray-900">{stats.totalUsers.toLocaleString()}</h3>
                <p className="text-sm text-gray-600">Total Users</p>
                <p className="text-xs text-gray-500 mt-2">+{Math.floor(stats.totalUsers * stats.growth24h / 100)} from last week</p>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <TrendingUp size={24} className="text-green-600" />
                  </div>
                  <div className="flex items-center text-green-600 text-sm">
                    <ArrowUp size={16} />
                    <span>8.3%</span>
                  </div>
                </div>
                <h3 className="text-2xl font-bold text-gray-900">{stats.activeTraders.toLocaleString()}</h3>
                <p className="text-sm text-gray-600">Active Traders</p>
                <p className="text-xs text-gray-500 mt-2">+{Math.floor(stats.activeTraders * 8.3 / 100)} from yesterday</p>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <DollarSign size={24} className="text-purple-600" />
                  </div>
                  <div className="flex items-center text-green-600 text-sm">
                    <ArrowUp size={16} />
                    <span>15.7%</span>
                  </div>
                </div>
                <h3 className="text-2xl font-bold text-gray-900">{stats.totalVolume}</h3>
                <p className="text-sm text-gray-600">24h Volume</p>
                <p className="text-xs text-gray-500 mt-2">+$18.5M from yesterday</p>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                    <Activity size={24} className="text-yellow-600" />
                  </div>
                  <div className="flex items-center text-green-600 text-sm">
                    <ArrowUp size={16} />
                    <span>22.1%</span>
                  </div>
                </div>
                <h3 className="text-2xl font-bold text-gray-900">{stats.revenue24h}</h3>
                <p className="text-sm text-gray-600">Revenue (24h)</p>
                <p className="text-xs text-gray-500 mt-2">+$7,650 from yesterday</p>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
                  <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                    View All
                  </button>
                </div>
              </div>
              <div className="divide-y divide-gray-200">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`w-2 h-2 rounded-full ${
                          activity.status === 'success' ? 'bg-green-500' :
                          activity.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                        }`}></div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                          <p className="text-xs text-gray-500">by {activity.user} • {activity.timestamp}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        {activity.amount && (
                          <span className="text-sm font-medium text-gray-900">{activity.amount}</span>
                        )}
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          activity.type === 'user' ? 'bg-blue-100 text-blue-800' :
                          activity.type === 'trade' ? 'bg-green-100 text-green-800' :
                          activity.type === 'security' ? 'bg-red-100 text-red-800' :
                          activity.type === 'ai' ? 'bg-purple-100 text-purple-800' :
                          activity.type === 'withdrawal' ? 'bg-orange-100 text-orange-800' :
                          activity.type === 'deposit' ? 'bg-teal-100 text-teal-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {activity.type}
                        </span>
                        <button className="p-1 hover:bg-gray-100 rounded">
                          <MoreVertical size={14} className="text-gray-400" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="space-y-6">
            {/* Users Header */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">User Management</h3>
                <div className="flex items-center space-x-3">
                  <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center space-x-2">
                    <Plus size={16} />
                    <span>Add User</span>
                  </button>
                  <button className="px-4 py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2">
                    <Download size={16} />
                    <span>Export</span>
                  </button>
                </div>
              </div>

              {/* Search and Filter */}
              <div className="flex items-center space-x-4 mb-6">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                  <input
                    type="text"
                    placeholder="Search users..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-white border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                  />
                </div>
                <button className="px-4 py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2">
                  <Filter size={16} />
                  <span>Filter</span>
                </button>
              </div>

              {/* Users Table */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        <input type="checkbox" className="rounded border-gray-300" />
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        User
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Role
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Balance
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        KYC Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Last Active
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {users.map((user) => (
                      <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <input type="checkbox" className="rounded border-gray-300" />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{user.name}</div>
                            <div className="text-sm text-gray-500">{user.email}</div>
                            <div className="text-xs text-gray-400">Joined {user.joinDate}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            user.role === 'Admin' ? 'bg-purple-100 text-purple-800' :
                            user.role === 'VIP Trader' ? 'bg-yellow-100 text-yellow-800' :
                            user.role === 'Trader' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {user.role}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            user.status === 'active' ? 'bg-green-100 text-green-800' :
                            user.status === 'suspended' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {user.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {user.balance}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            user.kycStatus === 'verified' ? 'bg-green-100 text-green-800' :
                            user.kycStatus === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {user.kycStatus}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {user.lastActive}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex items-center space-x-2">
                            <button className="text-blue-600 hover:text-blue-900">
                              <Eye size={16} />
                            </button>
                            <button className="text-gray-600 hover:text-gray-900">
                              <Edit size={16} />
                            </button>
                            <button className="text-red-600 hover:text-red-900">
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="flex items-center justify-between mt-6">
                <div className="text-sm text-gray-700">
                  Showing <span className="font-medium">1</span> to <span className="font-medium">{users.length}</span> of{' '}
                  <span className="font-medium">{users.length}</span> results
                </div>
                <div className="flex items-center space-x-2">
                  <button className="px-3 py-1 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">
                    Previous
                  </button>
                  <button className="px-3 py-1 bg-blue-600 text-white rounded-lg text-sm">
                    1
                  </button>
                  <button className="px-3 py-1 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">
                    2
                  </button>
                  <button className="px-3 py-1 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">
                    Next
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'trading' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Trading Overview</h3>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Active Orders</h4>
                  <p className="text-2xl font-bold text-gray-900">{stats.activeOrders}</p>
                  <p className="text-sm text-green-600">+12.5% from yesterday</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Total Balance</h4>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalBalance}</p>
                  <p className="text-sm text-green-600">+8.3% from yesterday</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Pending Verifications</h4>
                  <p className="text-2xl font-bold text-gray-900">{stats.pendingVerifications}</p>
                  <p className="text-sm text-yellow-600">Requires attention</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Security Overview</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="text-green-600" size={24} />
                    <div>
                      <h4 className="font-medium text-green-900">2FA Authentication</h4>
                      <p className="text-sm text-green-700">Enabled for all admin accounts</p>
                    </div>
                  </div>
                  <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">Active</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <AlertCircle className="text-yellow-600" size={24} />
                    <div>
                      <h4 className="font-medium text-yellow-900">Suspicious Login Attempts</h4>
                      <p className="text-sm text-yellow-700">3 unusual patterns detected today</p>
                    </div>
                  </div>
                  <button className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">Review</button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Analytics Dashboard</h3>
              <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                <p className="text-gray-500">Analytics charts will be displayed here</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">System Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Trading Fee (%)</label>
                  <input type="number" defaultValue="0.1" step="0.01" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Max Leverage</label>
                  <input type="number" defaultValue="10" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500" />
                </div>
                <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors">
                  Save Settings
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminPage;