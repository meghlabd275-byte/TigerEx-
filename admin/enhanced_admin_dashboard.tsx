import React, { useState, useEffect, useCallback } from 'react';
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar, 
  PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

// Types
interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  status: 'active' | 'suspended' | 'pending' | 'banned';
  lastLogin: string;
  balance: number;
  kycStatus: 'verified' | 'pending' | 'rejected' | 'not_submitted';
  createdAt: string;
}

interface ExchangeService {
  id: string;
  name: string;
  status: 'active' | 'paused' | 'halted' | 'stopped';
  load: number;
  uptime: string;
  responseTime: number;
  errorRate: number;
}

interface Transaction {
  id: string;
  userId: string;
  type: 'buy' | 'sell' | 'deposit' | 'withdrawal' | 'transfer';
  amount: number;
  currency: string;
  status: 'completed' | 'pending' | 'failed' | 'cancelled';
  timestamp: string;
  fee: number;
}

interface SystemMetrics {
  timestamp: string;
  activeUsers: number;
  totalTrades: number;
  volume: number;
  serverLoad: number;
  apiLatency: number;
}

// Constants
const STATUS_COLORS = {
  active: '#22c55e',
  suspended: '#eab308',
  pending: '#f59e0b',
  banned: '#ef4444',
  completed: '#22c55e',
  failed: '#ef4444',
  cancelled: '#6b7280'
};

const CURRENCY_ICONS: Record<string, string> = {
  BTC: '₿',
  ETH: 'Ξ',
  USDT: '$',
  BNB: '◈'
};

const EnhancedAdminDashboard: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [metrics, setMetrics] = useState<SystemMetrics[]>([]);
  const [services, setServices] = useState<ExchangeService[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState('24h');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  // Mock data generation
  useEffect(() => {
    const generateMockData = () => {
      // Generate users with enhanced data
      const mockUsers: User[] = Array.from({ length: 50 }, (_, i) => ({
        id: `user_${i + 1}`,
        name: `User ${i + 1}`,
        email: `user${i + 1}@example.com`,
        role: ['admin', 'trader', 'user', 'vip'][Math.floor(Math.random() * 4)],
        status: ['active', 'suspended', 'pending', 'banned'][Math.floor(Math.random() * 4)] as User['status'],
        lastLogin: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
        balance: Math.random() * 100000,
        kycStatus: ['verified', 'pending', 'rejected', 'not_submitted'][Math.floor(Math.random() * 4)] as User['kycStatus'],
        createdAt: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString()
      }));

      // Generate exchange services with enhanced metrics
      const exchangeNames = ['Binance', 'Bybit', 'OKX', 'Bitget', 'Bitfinex', 'MEXC', 'Kraken', 'Robinhood', 'Gate.io', 'Coinbase', 'HTX'];
      const mockServices: ExchangeService[] = exchangeNames.map(name => ({
        id: name.toLowerCase().replace('.', ''),
        name: name,
        status: ['active', 'paused', 'halted', 'stopped'][Math.floor(Math.random() * 4)] as ExchangeService['status'],
        load: Math.random() * 100,
        uptime: '99.9%',
        responseTime: Math.random() * 500 + 50,
        errorRate: Math.random() * 2
      }));

      // Generate transactions with enhanced data
      const mockTransactions: Transaction[] = Array.from({ length: 100 }, (_, i) => ({
        id: `tx_${i + 1}`,
        userId: `user_${Math.floor(Math.random() * 50) + 1}`,
        type: ['buy', 'sell', 'deposit', 'withdrawal', 'transfer'][Math.floor(Math.random() * 5)] as Transaction['type'],
        amount: Math.random() * 10000,
        currency: ['BTC', 'ETH', 'USDT', 'BNB', 'SOL'][Math.floor(Math.random() * 5)],
        status: ['completed', 'pending', 'failed', 'cancelled'][Math.floor(Math.random() * 4)] as Transaction['status'],
        timestamp: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(),
        fee: Math.random() * 10
      }));

      // Generate system metrics
      const mockMetrics: SystemMetrics[] = Array.from({ length: 24 }, (_, i) => ({
        timestamp: new Date(Date.now() - (23 - i) * 60 * 60 * 1000).toISOString(),
        activeUsers: Math.floor(Math.random() * 1000) + 500,
        totalTrades: Math.floor(Math.random() * 500) + 200,
        volume: Math.random() * 1000000 + 500000,
        serverLoad: Math.random() * 100,
        apiLatency: Math.random() * 200 + 20
      }));

      setUsers(mockUsers);
      setTransactions(mockTransactions);
      setMetrics(mockMetrics);
      setServices(mockServices);
      setLoading(false);
    };

    generateMockData();
  }, []);

  // Filter functions
  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Helper functions
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
  };

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string): string => {
    return STATUS_COLORS[status] || '#6b7280';
  };

  const getTotalVolume = (): number => {
    return transactions
      .filter(t => t.status === 'completed')
      .reduce((sum, t) => sum + t.amount, 0);
  };

  const getActiveServices = (): number => {
    return services.filter(s => s.status === 'active').length;
  };

  // Chart data
  const pieData = [
    { name: 'Active Users', value: users.filter(u => u.status === 'active').length, color: '#10B981' },
    { name: 'Suspended', value: users.filter(u => u.status === 'suspended').length, color: '#EF4444' },
    { name: 'Pending', value: users.filter(u => u.status === 'pending').length, color: '#F59E0B' },
    { name: 'Banned', value: users.filter(u => u.status === 'banned').length, color: '#6B7280' }
  ];

  const roleData = [
    { name: 'Admin', value: users.filter(u => u.role === 'admin').length, color: '#8B5CF6' },
    { name: 'Trader', value: users.filter(u => u.role === 'trader').length, color: '#3B82F6' },
    { name: 'VIP', value: users.filter(u => u.role === 'vip').length, color: '#F59E0B' },
    { name: 'User', value: users.filter(u => u.role === 'user').length, color: '#6B7280' }
  ];

  const transactionTypeData = [
    { name: 'Buy', value: transactions.filter(t => t.type === 'buy').length, color: '#22c55e' },
    { name: 'Sell', value: transactions.filter(t => t.type === 'sell').length, color: '#ef4444' },
    { name: 'Deposit', value: transactions.filter(t => t.type === 'deposit').length, color: '#3b82f6' },
    { name: 'Withdrawal', value: transactions.filter(t => t.type === 'withdrawal').length, color: '#f59e0b' }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-2xl">Loading Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Enhanced Admin Dashboard</h1>
          <p className="text-gray-400">Complete platform control and monitoring</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="text-sm text-gray-400 mb-2">Total Users</div>
            <div className="text-3xl font-bold text-blue-400">{users.length}</div>
            <div className="text-sm text-green-400 mt-2">+12% from last period</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="text-sm text-gray-400 mb-2">Active Users</div>
            <div className="text-3xl font-bold text-green-400">{users.filter(u => u.status === 'active').length}</div>
            <div className="text-sm text-green-400 mt-2">+8% from last period</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="text-sm text-gray-400 mb-2">Total Transactions</div>
            <div className="text-3xl font-bold text-yellow-400">{transactions.length}</div>
            <div className="text-sm text-green-400 mt-2">+15% from last period</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="text-sm text-gray-400 mb-2">System Load</div>
            <div className="text-3xl font-bold text-purple-400">{(metrics[metrics.length - 1]?.serverLoad || 0).toFixed(1)}%</div>
            <div className="text-sm text-red-400 mt-2">+2% from last period</div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* System Metrics Chart */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-4">System Metrics (24h)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={metrics}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="timestamp" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
                <Legend />
                <Line type="monotone" dataKey="activeUsers" stroke="#3B82F6" strokeWidth={2} />
                <Line type="monotone" dataKey="totalTrades" stroke="#10B981" strokeWidth={2} />
                <Line type="monotone" dataKey="serverLoad" stroke="#F59E0B" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* User Status Pie Chart */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-4">User Status Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Service Management */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <h3 className="text-xl font-semibold mb-6">Service Control Panel</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {services.map(service => (
              <div key={service.id} className="bg-gray-700 p-4 rounded-lg flex justify-between items-center">
                <div>
                  <div className="font-bold">{service.name}</div>
                  <div className="text-xs text-gray-400">Load: {service.load.toFixed(1)}% | Uptime: {service.uptime}</div>
                  <span className={`text-[10px] uppercase px-1.5 py-0.5 rounded ${
                    service.status === 'active' ? 'bg-green-900 text-green-200' :
                    service.status === 'paused' ? 'bg-yellow-900 text-yellow-200' :
                    'bg-red-900 text-red-200'
                  }`}>
                    {service.status}
                  </span>
                </div>
                <div className="flex gap-1">
                  <button className="bg-yellow-600 hover:bg-yellow-700 p-1 rounded text-xs" title="Pause">⏸</button>
                  <button className="bg-green-600 hover:bg-green-700 p-1 rounded text-xs" title="Resume">▶</button>
                  <button className="bg-red-600 hover:bg-red-700 p-1 rounded text-xs" title="Stop">⏹</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* User Management Table */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-semibold">User Management</h3>
            <div className="flex gap-4">
              <input
                type="text"
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-gray-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="bg-gray-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="1h">Last Hour</option>
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="pb-3 text-gray-400">User</th>
                  <th className="pb-3 text-gray-400">Role</th>
                  <th className="pb-3 text-gray-400">Status</th>
                  <th className="pb-3 text-gray-400">Balance</th>
                  <th className="pb-3 text-gray-400">Last Login</th>
                  <th className="pb-3 text-gray-400">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.slice(0, 10).map((user) => (
                  <tr key={user.id} className="border-b border-gray-700">
                    <td className="py-3">
                      <div>
                        <div className="font-medium">{user.name}</div>
                        <div className="text-sm text-gray-400">{user.email}</div>
                      </div>
                    </td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-xs ${
                        user.role === 'admin' ? 'bg-purple-900 text-purple-200' :
                        user.role === 'trader' ? 'bg-blue-900 text-blue-200' :
                        'bg-gray-700 text-gray-300'
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-xs ${
                        user.status === 'active' ? 'bg-green-900 text-green-200' :
                        user.status === 'suspended' ? 'bg-red-900 text-red-200' :
                        'bg-yellow-900 text-yellow-200'
                      }`}>
                        {user.status}
                      </span>
                    </td>
                    <td className="py-3">${user.balance.toFixed(2)}</td>
                    <td className="py-3 text-gray-400">
                      {new Date(user.lastLogin).toLocaleDateString()}
                    </td>
                    <td className="py-3">
                      <div className="flex gap-2">
                        <button className="bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded text-xs">
                          Edit
                        </button>
                        <button className="bg-yellow-600 hover:bg-yellow-700 px-2 py-1 rounded text-xs">
                          Suspend
                        </button>
                        <button className="bg-red-600 hover:bg-red-700 px-2 py-1 rounded text-xs">
                          Ban
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-6">Recent Transactions</h3>
          <div className="space-y-4">
            {transactions.slice(0, 10).map((transaction) => (
              <div key={transaction.id} className="flex justify-between items-center p-4 bg-gray-700 rounded-lg">
                <div className="flex items-center gap-4">
                  <div className={`w-2 h-2 rounded-full ${
                    transaction.status === 'completed' ? 'bg-green-400' :
                    transaction.status === 'pending' ? 'bg-yellow-400' :
                    'bg-red-400'
                  }`} />
                  <div>
                    <div className="font-medium">{transaction.type.toUpperCase()}</div>
                    <div className="text-sm text-gray-400">{transaction.currency} • {transaction.id}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium">${transaction.amount.toFixed(2)}</div>
                  <div className="text-sm text-gray-400">
                    {new Date(transaction.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedAdminDashboard;