'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { 
  Users, 
  Settings, 
  Shield, 
  TrendingUp, 
  DollarSign, 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Eye,
  EyeOff,
  Edit,
  Trash2,
  Plus,
  Search,
  Filter,
  Download,
  Upload,
  RefreshCw,
  Lock,
  Unlock,
  Ban,
  UserCheck,
  Calendar,
  BarChart3,
  PieChart,
  FileText,
  Bell,
  Mail,
  Phone,
  MapPin,
  CreditCard,
  Wallet,
  Zap,
  Database,
  Server,
  Globe,
  Cpu,
  HardDrive,
  Wifi,
  WifiOff,
  ChevronDown,
  ChevronUp,
  ChevronRight,
  ChevronLeft,
  ArrowUp,
  ArrowDown,
  MoreVertical,
  LogOut,
  Menu,
  X,
  Home,
  Building,
  Package,
  Truck,
  Archive,
  Tag,
  ShoppingCart,
  MessageSquare,
  HelpCircle,
  BookOpen,
  Code,
  Layers,
  Grid,
  List,
  Save,
  Copy,
  ExternalLink,
  AlertCircle,
  Info,
  Check,
  X,
  ChevronDownSquare,
  ChevronUpSquare
} from 'lucide-react'

interface User {
  id: string
  user_id: string
  username: string
  email: string
  phone?: string
  role: string
  status: 'active' | 'inactive' | 'locked' | 'suspended'
  verified: boolean
  kyc_completed: boolean
  premium: boolean
  balance: number
  trading_volume: number
  last_login: string
  created_at: string
  ip_address?: string
  country?: string
}

interface TradingPair {
  symbol: string
  price: number
  change_24h: number
  volume_24h: number
  high_24h: number
  low_24h: number
  active: boolean
}

interface SystemMetrics {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_in: number
  network_out: number
  active_connections: number
  uptime: string
}

interface Order {
  id: string
  user_id: string
  symbol: string
  type: string
  side: string
  quantity: number
  price: number
  status: string
  created_at: string
}

const EnhancedAdminPage: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [activeTab, setActiveTab] = useState('dashboard')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedRole, setSelectedRole] = useState('all')
  const [selectedStatus, setSelectedStatus] = useState('all')
  const [showUserModal, setShowUserModal] = useState(false)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [showNotifications, setShowNotifications] = useState(false)
  const [theme, setTheme] = useState<'dark' | 'light'>('dark')

  // Sample data
  const [users, setUsers] = useState<User[]>([
    {
      id: '1',
      user_id: 'USR001',
      username: 'john_trader',
      email: 'john@example.com',
      phone: '+1234567890',
      role: 'verified_trader',
      status: 'active',
      verified: true,
      kyc_completed: true,
      premium: true,
      balance: 125000.50,
      trading_volume: 2500000.00,
      last_login: '2024-11-14T10:30:00Z',
      created_at: '2024-01-15T08:00:00Z',
      ip_address: '192.168.1.100',
      country: 'United States'
    },
    {
      id: '2',
      user_id: 'USR002',
      username: 'alice_crypto',
      email: 'alice@example.com',
      role: 'trader',
      status: 'active',
      verified: true,
      kyc_completed: false,
      premium: false,
      balance: 45000.25,
      trading_volume: 850000.00,
      last_login: '2024-11-14T09:15:00Z',
      created_at: '2024-03-20T14:30:00Z',
      ip_address: '192.168.1.101',
      country: 'Canada'
    },
    {
      id: '3',
      user_id: 'USR003',
      username: 'bob_investor',
      email: 'bob@example.com',
      role: 'premium_user',
      status: 'suspended',
      verified: false,
      kyc_completed: false,
      premium: true,
      balance: 250000.00,
      trading_volume: 5000000.00,
      last_login: '2024-11-13T16:45:00Z',
      created_at: '2024-02-10T11:20:00Z',
      ip_address: '192.168.1.102',
      country: 'United Kingdom'
    }
  ])

  const [tradingPairs] = useState<TradingPair[]>([
    { symbol: 'BTC/USDT', price: 67850.25, change_24h: 2.5, volume_24h: 1250000000, high_24h: 68900, low_24h: 66500, active: true },
    { symbol: 'ETH/USDT', price: 3542.18, change_24h: -1.2, volume_24h: 850000000, high_24h: 3650, low_24h: 3480, active: true },
    { symbol: 'SOL/USDT', price: 145.67, change_24h: 3.2, volume_24h: 450000000, high_24h: 152, low_24h: 140, active: true },
    { symbol: 'BNB/USDT', price: 612.45, change_24h: 0.8, volume_24h: 320000000, high_24h: 625, low_24h: 605, active: true },
  ])

  const [systemMetrics] = useState<SystemMetrics>({
    cpu_usage: 65.2,
    memory_usage: 78.5,
    disk_usage: 45.8,
    network_in: 125.6,
    network_out: 98.3,
    active_connections: 15234,
    uptime: '45 days, 12 hours'
  })

  const [orders] = useState<Order[]>([
    { id: 'ORD001', user_id: 'USR001', symbol: 'BTC/USDT', type: 'limit', side: 'buy', quantity: 0.5, price: 67500, status: 'filled', created_at: '2024-11-14T10:25:00Z' },
    { id: 'ORD002', user_id: 'USR002', symbol: 'ETH/USDT', type: 'market', side: 'sell', quantity: 2.0, price: 3540, status: 'pending', created_at: '2024-11-14T10:20:00Z' },
    { id: 'ORD003', user_id: 'USR003', symbol: 'SOL/USDT', type: 'limit', side: 'buy', quantity: 100, price: 144.50, status: 'cancelled', created_at: '2024-11-14T10:15:00Z' },
  ])

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'users', label: 'User Management', icon: Users },
    { id: 'trading', label: 'Trading Control', icon: TrendingUp },
    { id: 'finance', label: 'Financial', icon: DollarSign },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'system', label: 'System', icon: Server },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'logs', label: 'Audit Logs', icon: FileText },
    { id: 'help', label: 'Help & Support', icon: HelpCircle },
  ]

  const roles = [
    'all', 'super_admin', 'exchange_admin', 'trading_admin', 'compliance_admin',
    'support_admin', 'risk_manager', 'market_maker', 'institutional_trader',
    'verified_trader', 'trader', 'premium_user', 'verified_user', 'user'
  ]

  const statusOptions = [
    { value: 'all', label: 'All Status' },
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' },
    { value: 'locked', label: 'Locked' },
    { value: 'suspended', label: 'Suspended' }
  ]

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         user.user_id.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesRole = selectedRole === 'all' || user.role === selectedRole
    const matchesStatus = selectedStatus === 'all' || user.status === selectedStatus
    return matchesSearch && matchesRole && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400 bg-green-400/20'
      case 'inactive': return 'text-gray-400 bg-gray-400/20'
      case 'locked': return 'text-red-400 bg-red-400/20'
      case 'suspended': return 'text-orange-400 bg-orange-400/20'
      default: return 'text-gray-400 bg-gray-400/20'
    }
  }

  const getRoleColor = (role: string) => {
    if (role.includes('admin')) return 'text-purple-400 bg-purple-400/20'
    if (role.includes('trader')) return 'text-blue-400 bg-blue-400/20'
    if (role.includes('premium')) return 'text-yellow-400 bg-yellow-400/20'
    return 'text-gray-400 bg-gray-400/20'
  }

  const handleUserAction = (action: string, user: User) => {
    setSelectedUser(user)
    switch (action) {
      case 'edit':
        setShowUserModal(true)
        break
      case 'suspend':
        // Handle suspend
        break
      case 'activate':
        // Handle activate
        break
      case 'delete':
        // Handle delete
        break
    }
  }

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Users</p>
              <p className="text-2xl font-bold text-white">15,234</p>
              <p className="text-green-400 text-sm mt-1">↑ 12.5%</p>
            </div>
            <Users className="text-blue-400" size={32} />
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Traders</p>
              <p className="text-2xl font-bold text-white">3,567</p>
              <p className="text-green-400 text-sm mt-1">↑ 8.3%</p>
            </div>
            <TrendingUp className="text-green-400" size={32} />
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">24h Volume</p>
              <p className="text-2xl font-bold text-white">$2.8B</p>
              <p className="text-red-400 text-sm mt-1">↓ 3.2%</p>
            </div>
            <DollarSign className="text-yellow-400" size={32} />
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">System Health</p>
              <p className="text-2xl font-bold text-white">98.5%</p>
              <p className="text-green-400 text-sm mt-1">Optimal</p>
            </div>
            <Activity className="text-green-400" size={32} />
          </div>
        </div>
      </div>

      {/* Charts and Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {orders.slice(0, 5).map(order => (
              <div key={order.id} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    order.status === 'filled' ? 'bg-green-400' :
                    order.status === 'pending' ? 'bg-yellow-400' : 'bg-red-400'
                  }`} />
                  <div>
                    <p className="text-white font-medium">{order.symbol}</p>
                    <p className="text-gray-400 text-sm">{order.user_id}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-white font-medium">{order.side.toUpperCase()} {order.quantity}</p>
                  <p className="text-gray-400 text-sm">${order.price}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Metrics */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">System Metrics</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">CPU Usage</span>
                <span className="text-white">{systemMetrics.cpu_usage}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-blue-400 h-2 rounded-full" 
                  style={{ width: `${systemMetrics.cpu_usage}%` }}
                />
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">Memory Usage</span>
                <span className="text-white">{systemMetrics.memory_usage}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-green-400 h-2 rounded-full" 
                  style={{ width: `${systemMetrics.memory_usage}%` }}
                />
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">Disk Usage</span>
                <span className="text-white">{systemMetrics.disk_usage}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-yellow-400 h-2 rounded-full" 
                  style={{ width: `${systemMetrics.disk_usage}%` }}
                />
              </div>
            </div>
            
            <div className="pt-2 border-t border-gray-700">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Uptime</span>
                <span className="text-white">{systemMetrics.uptime}</span>
              </div>
              <div className="flex justify-between text-sm mt-1">
                <span className="text-gray-400">Active Connections</span>
                <span className="text-white">{systemMetrics.active_connections.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Trading Pairs */}
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Trading Pairs</h3>
          <button className="text-blue-400 hover:text-blue-300 text-sm">
            View All
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 text-gray-400">Pair</th>
                <th className="text-right py-3 text-gray-400">Price</th>
                <th className="text-right py-3 text-gray-400">24h Change</th>
                <th className="text-right py-3 text-gray-400">24h Volume</th>
                <th className="text-right py-3 text-gray-400">24h High</th>
                <th className="text-right py-3 text-gray-400">24h Low</th>
                <th className="text-center py-3 text-gray-400">Status</th>
              </tr>
            </thead>
            <tbody>
              {tradingPairs.map(pair => (
                <tr key={pair.symbol} className="border-b border-gray-700">
                  <td className="py-3 font-medium text-white">{pair.symbol}</td>
                  <td className="text-right text-white">${pair.price.toLocaleString()}</td>
                  <td className={`text-right ${pair.change_24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {pair.change_24h >= 0 ? '↑' : '↓'} {Math.abs(pair.change_24h)}%
                  </td>
                  <td className="text-right text-gray-300">
                    ${(pair.volume_24h / 1000000000).toFixed(2)}B
                  </td>
                  <td className="text-right text-gray-300">${pair.high_24h.toLocaleString()}</td>
                  <td className="text-right text-gray-300">${pair.low_24h.toLocaleString()}</td>
                  <td className="text-center">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      pair.active ? 'bg-green-400/20 text-green-400' : 'bg-red-400/20 text-red-400'
                    }`}>
                      {pair.active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )

  const renderUsers = () => (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search users..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-400"
              />
            </div>
          </div>
          
          <div className="flex gap-2">
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-400"
            >
              {roles.map(role => (
                <option key={role} value={role}>
                  {role === 'all' ? 'All Roles' : role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </option>
              ))}
            </select>
            
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-400"
            >
              {statusOptions.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
            
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2">
              <Filter size={16} />
              Filter
            </button>
            
            <button className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center gap-2">
              <Plus size={16} />
              Add User
            </button>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-400'}`}
            >
              <Grid size={16} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-400'}`}
            >
              <List size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Users Grid/List */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredUsers.map(user => (
            <div key={user.id} className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">
                      {user.username.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-white font-medium">{user.username}</h3>
                    <p className="text-gray-400 text-sm">{user.user_id}</p>
                  </div>
                </div>
                <button className="text-gray-400 hover:text-white">
                  <MoreVertical size={16} />
                </button>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Email</span>
                  <span className="text-white">{user.email}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Role</span>
                  <span className={`px-2 py-1 rounded text-xs ${getRoleColor(user.role)}`}>
                    {user.role.replace('_', ' ')}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Status</span>
                  <span className={`px-2 py-1 rounded text-xs ${getStatusColor(user.status)}`}>
                    {user.status}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Balance</span>
                  <span className="text-white">${user.balance.toLocaleString()}</span>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleUserAction('edit', user)}
                  className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleUserAction('suspend', user)}
                  className="flex-1 px-3 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded text-sm"
                >
                  Suspend
                </button>
                <button className="p-2 bg-gray-700 hover:bg-gray-600 text-white rounded">
                  <MoreVertical size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-6 text-gray-400">User</th>
                <th className="text-left py-3 px-6 text-gray-400">Contact</th>
                <th className="text-left py-3 px-6 text-gray-400">Role</th>
                <th className="text-left py-3 px-6 text-gray-400">Status</th>
                <th className="text-right py-3 px-6 text-gray-400">Balance</th>
                <th className="text-right py-3 px-6 text-gray-400">Volume</th>
                <th className="text-left py-3 px-6 text-gray-400">Last Login</th>
                <th className="text-center py-3 px-6 text-gray-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map(user => (
                <tr key={user.id} className="border-b border-gray-700 hover:bg-gray-700/50">
                  <td className="py-3 px-6">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                        <span className="text-white text-sm font-bold">
                          {user.username.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <p className="text-white font-medium">{user.username}</p>
                        <p className="text-gray-400 text-sm">{user.user_id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-6">
                    <div>
                      <p className="text-white text-sm">{user.email}</p>
                      <p className="text-gray-400 text-sm">{user.phone}</p>
                    </div>
                  </td>
                  <td className="py-3 px-6">
                    <span className={`px-2 py-1 rounded text-xs ${getRoleColor(user.role)}`}>
                      {user.role.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-3 px-6">
                    <span className={`px-2 py-1 rounded text-xs ${getStatusColor(user.status)}`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="text-right py-3 px-6 text-white">
                    ${user.balance.toLocaleString()}
                  </td>
                  <td className="text-right py-3 px-6 text-white">
                    ${(user.trading_volume / 1000000).toFixed(2)}M
                  </td>
                  <td className="py-3 px-6 text-gray-300 text-sm">
                    {new Date(user.last_login).toLocaleDateString()}
                  </td>
                  <td className="py-3 px-6">
                    <div className="flex items-center justify-center space-x-2">
                      <button
                        onClick={() => handleUserAction('edit', user)}
                        className="p-1 text-blue-400 hover:text-blue-300"
                      >
                        <Edit size={16} />
                      </button>
                      <button
                        onClick={() => handleUserAction('suspend', user)}
                        className="p-1 text-orange-400 hover:text-orange-300"
                      >
                        <Ban size={16} />
                      </button>
                      <button
                        onClick={() => handleUserAction('delete', user)}
                        className="p-1 text-red-400 hover:text-red-300"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="text-gray-400 text-sm">
          Showing {filteredUsers.length} of {users.length} users
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            className="p-2 bg-gray-700 hover:bg-gray-600 text-white rounded"
          >
            <ChevronLeft size={16} />
          </button>
          <span className="text-white px-3 py-1">
            {currentPage} / 10
          </span>
          <button
            onClick={() => setCurrentPage(Math.min(10, currentPage + 1))}
            className="p-2 bg-gray-700 hover:bg-gray-600 text-white rounded"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </div>
  )

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return renderDashboard()
      case 'users':
        return renderUsers()
      case 'trading':
        return (
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Trading Control Panel</h3>
            <p className="text-gray-400">Trading control features coming soon...</p>
          </div>
        )
      case 'finance':
        return (
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Financial Management</h3>
            <p className="text-gray-400">Financial management features coming soon...</p>
          </div>
        )
      case 'security':
        return (
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Security Settings</h3>
            <p className="text-gray-400">Security management features coming soon...</p>
          </div>
        )
      case 'system':
        return (
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">System Configuration</h3>
            <p className="text-gray-400">System configuration features coming soon...</p>
          </div>
        )
      default:
        return (
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Under Development</h3>
            <p className="text-gray-400">This section is under development...</p>
          </div>
        )
    }
  }

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {/* Header */}
      <header className={`${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-b`}>
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className={`${theme === 'dark' ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'}`}
              >
                {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
              <h1 className={`ml-4 text-xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                Enhanced Admin Dashboard
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className={`relative p-2 rounded-lg ${theme === 'dark' ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
              >
                <Bell size={20} />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              
              <button
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                className={`p-2 rounded-lg ${theme === 'dark' ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
              >
                {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
              </button>
              
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-bold">A</span>
                </div>
                <span className={`text-sm font-medium ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                  Admin User
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        {sidebarOpen && (
          <aside className={`w-64 ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-r min-h-screen`}>
            <nav className="p-4">
              <div className="space-y-1">
                {menuItems.map(item => (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                      activeTab === item.id
                        ? theme === 'dark' ? 'bg-blue-600 text-white' : 'bg-blue-50 text-blue-600'
                        : theme === 'dark' ? 'text-gray-300 hover:bg-gray-700 hover:text-white' : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`}
                  >
                    <item.icon size={18} />
                    <span className="text-sm font-medium">{item.label}</span>
                  </button>
                ))}
              </div>
            </nav>
          </aside>
        )}

        {/* Main Content */}
        <main className="flex-1 p-6">
          {renderContent()}
        </main>
      </div>
    </div>
  )
}

export default EnhancedAdminPage