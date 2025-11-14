import React, { useState, useEffect } from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  status: 'active' | 'suspended' | 'pending';
  lastLogin: string;
  balance: number;
}

interface Transaction {
  id: string;
  userId: string;
  type: 'buy' | 'sell' | 'deposit' | 'withdrawal';
  amount: number;
  currency: string;
  status: 'completed' | 'pending' | 'failed';
  timestamp: string;
}

interface SystemMetrics {
  timestamp: string;
  activeUsers: number;
  totalTrades: number;
  volume: number;
  serverLoad: number;
}

const EnhancedAdminDashboard: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [metrics, setMetrics] = useState<SystemMetrics[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState('24h');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  // Mock data generation
  useEffect(() => {
    const generateMockData = () => {
      // Generate users
      const mockUsers: User[] = Array.from({ length: 50 }, (_, i) => ({
        id: `user_${i + 1}`,
        name: `User ${i + 1}`,
        email: `user${i + 1}@example.com`,
        role: ['admin', 'trader', 'user'][Math.floor(Math.random() * 3)],
        status: ['active', 'suspended', 'pending'][Math.floor(Math.random() * 3)] as User['status'],
        lastLogin: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
        balance: Math.random() * 100000
      }));

      // Generate transactions
      const mockTransactions: Transaction[] = Array.from({ length: 100 }, (_, i) => ({
        id: `tx_${i + 1}`,
        userId: `user_${Math.floor(Math.random() * 50) + 1}`,
        type: ['buy', 'sell', 'deposit', 'withdrawal'][Math.floor(Math.random() * 4)] as Transaction['type'],
        amount: Math.random() * 10000,
        currency: ['BTC', 'ETH', 'USDT', 'BNB'][Math.floor(Math.random() * 4)],
        status: ['completed', 'pending', 'failed'][Math.floor(Math.random() * 3)] as Transaction['status'],
        timestamp: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString()
      }));

      // Generate metrics
      const mockMetrics: SystemMetrics[] = Array.from({ length: 24 }, (_, i) => ({
        timestamp: new Date(Date.now() - (23 - i) * 60 * 60 * 1000).toISOString(),
        activeUsers: Math.floor(Math.random() * 1000) + 500,
        totalTrades: Math.floor(Math.random() * 500) + 200,
        volume: Math.random() * 1000000 + 500000,
        serverLoad: Math.random() * 100
      }));

      setUsers(mockUsers);
      setTransactions(mockTransactions);
      setMetrics(mockMetrics);
      setLoading(false);
    };

    generateMockData();
  }, []);

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const pieData = [
    { name: 'Active Users', value: users.filter(u => u.status === 'active').length, color: '#10B981' },
    { name: 'Suspended', value: users.filter(u => u.status === 'suspended').length, color: '#EF4444' },
    { name: 'Pending', value: users.filter(u => u.status === 'pending').length, color: '#F59E0B' }
  ];

  const roleData = [
    { name: 'Admin', value: users.filter(u => u.role === 'admin').length, color: '#8B5CF6' },
    { name: 'Trader', value: users.filter(u => u.role === 'trader').length, color: '#3B82F6' },
    { name: 'User', value: users.filter(u => u.role === 'user').length, color: '#6B7280' }
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
                        <button className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm">
                          Edit
                        </button>
                        <button className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm">
                          Suspend
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