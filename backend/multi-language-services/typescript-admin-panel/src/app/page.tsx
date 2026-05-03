/**
 * TigerEx Admin Panel
 * Modern Next.js Admin Dashboard with TypeScript
 * Part of TigerEx Multi-Language Microservices Architecture
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// Types
interface ExchangeStatus {
  exchangeId: string;
  name: string;
  status: 'active' | 'paused' | 'halted' | 'maintenance';
  domain: string;
  whiteLabel: boolean;
  parentExchangeId?: string;
}

interface User {
  id: string;
  email: string;
  role: string;
  tier: string;
  kycStatus: string;
  createdAt: string;
  lastLogin: string;
  balance: Record<string, number>;
}

interface TradingPair {
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  status: string;
  volume24h: number;
  price: number;
  priceChange24h: number;
}

interface Order {
  id: string;
  userId: string;
  symbol: string;
  side: 'buy' | 'sell';
  type: string;
  price: number;
  quantity: number;
  filledQuantity: number;
  status: string;
  createdAt: string;
}

interface Trade {
  id: string;
  symbol: string;
  price: number;
  quantity: number;
  takerFee: number;
  makerFee: number;
  timestamp: string;
}

interface FeeTier {
  id: string;
  name: string;
  makerFee: number;
  takerFee: number;
  withdrawalFee: number;
  minVolume: number;
}

interface DashboardStats {
  totalUsers: number;
  activeUsers: number;
  totalVolume24h: number;
  totalTrades24h: number;
  totalFees24h: number;
  pendingWithdrawals: number;
  openOrders: number;
  systemHealth: 'healthy' | 'degraded' | 'down';
}

// API Configuration
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api/v1';

// Custom Hooks
const useApi = <T>(endpoint: string, options?: RequestInit) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            ...options?.headers,
          },
        });
        if (!response.ok) throw new Error('API request failed');
        const json = await response.json();
        setData(json);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [endpoint, JSON.stringify(options)]);

  return { data, loading, error, refetch: () => setLoading(true) };
};

// Components
const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const colors: Record<string, string> = {
    active: 'bg-green-100 text-green-800',
    paused: 'bg-yellow-100 text-yellow-800',
    halted: 'bg-red-100 text-red-800',
    maintenance: 'bg-blue-100 text-blue-800',
    filled: 'bg-green-100 text-green-800',
    partially_filled: 'bg-yellow-100 text-yellow-800',
    cancelled: 'bg-gray-100 text-gray-800',
    new: 'bg-blue-100 text-blue-800',
  };

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
      {status.toUpperCase()}
    </span>
  );
};

const Card: React.FC<{ title: string; children: React.ReactNode; className?: string }> = ({ 
  title, 
  children, 
  className = '' 
}) => (
  <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
    <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
    {children}
  </div>
);

const StatCard: React.FC<{ title: string; value: string | number; change?: number; icon: string }> = ({ 
  title, 
  value, 
  change, 
  icon 
}) => (
  <div className="bg-white rounded-lg shadow-md p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-500">{title}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        {change !== undefined && (
          <p className={`text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {change >= 0 ? '↑' : '↓'} {Math.abs(change).toFixed(2)}%
          </p>
        )}
      </div>
      <div className="text-4xl">{icon}</div>
    </div>
  </div>
);

// Exchange Status Control
const ExchangeControl: React.FC<{
  status: ExchangeStatus;
  onStatusChange: (status: ExchangeStatus['status']) => void;
}> = ({ status, onStatusChange }) => {
  const [loading, setLoading] = useState(false);

  const handleStatusChange = async (newStatus: ExchangeStatus['status']) => {
    setLoading(true);
    try {
      await fetch(`${API_BASE}/exchange/status`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });
      onStatusChange(newStatus);
    } catch (error) {
      console.error('Failed to update status:', error);
    }
    setLoading(false);
  };

  return (
    <Card title="Exchange Control">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Exchange ID</p>
            <p className="font-mono text-lg">{status.exchangeId}</p>
          </div>
          <StatusBadge status={status.status} />
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Domain</p>
            <p className="font-medium">{status.domain}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">White Label</p>
            <p className="font-medium">{status.whiteLabel ? 'Yes' : 'No'}</p>
          </div>
        </div>

        <div className="border-t pt-4">
          <p className="text-sm text-gray-600 mb-2">Change Exchange Status</p>
          <div className="flex gap-2">
            {(['active', 'paused', 'halted', 'maintenance'] as const).map((s) => (
              <button
                key={s}
                onClick={() => handleStatusChange(s)}
                disabled={loading || status.status === s}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors
                  ${status.status === s 
                    ? 'bg-gray-800 text-white' 
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                  } disabled:opacity-50`}
              >
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};

// User Management Table
const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await fetch(`${API_BASE}/admin/users`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });
        const data = await response.json();
        setUsers(data.users || []);
      } catch (error) {
        console.error('Failed to fetch users:', error);
      }
      setLoading(false);
    };
    fetchUsers();
  }, []);

  const filteredUsers = users.filter(user => 
    user.email.toLowerCase().includes(search.toLowerCase()) ||
    user.id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Card title="User Management">
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search users..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tier</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">KYC</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredUsers.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono">{user.id.slice(0, 8)}...</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{user.email}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <StatusBadge status={user.role} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{user.tier}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <StatusBadge status={user.kycStatus} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <button className="text-blue-600 hover:text-blue-900 mr-3">Edit</button>
                  <button className="text-red-600 hover:text-red-900">Suspend</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

// Fee Management
const FeeManagement: React.FC = () => {
  const [tiers, setTiers] = useState<FeeTier[]>([]);
  const [editingTier, setEditingTier] = useState<FeeTier | null>(null);

  useEffect(() => {
    const fetchTiers = async () => {
      try {
        const response = await fetch(`${API_BASE}/fees/tiers`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });
        const data = await response.json();
        setTiers(data.tiers || []);
      } catch (error) {
        console.error('Failed to fetch tiers:', error);
      }
    };
    fetchTiers();
  }, []);

  const handleUpdateTier = async (tier: FeeTier) => {
    try {
      await fetch(`${API_BASE}/fees/tiers/${tier.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(tier),
      });
      setEditingTier(null);
    } catch (error) {
      console.error('Failed to update tier:', error);
    }
  };

  return (
    <Card title="Fee Tier Management">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tier</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Maker Fee</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Taker Fee</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Withdrawal Fee</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Min Volume</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {tiers.map((tier) => (
              <tr key={tier.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{tier.name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {editingTier?.id === tier.id ? (
                    <input
                      type="number"
                      step="0.0001"
                      value={editingTier.makerFee}
                      onChange={(e) => setEditingTier({ ...editingTier, makerFee: parseFloat(e.target.value) })}
                      className="w-20 px-2 py-1 border rounded"
                    />
                  ) : (
                    `${(tier.makerFee * 100).toFixed(2)}%`
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {editingTier?.id === tier.id ? (
                    <input
                      type="number"
                      step="0.0001"
                      value={editingTier.takerFee}
                      onChange={(e) => setEditingTier({ ...editingTier, takerFee: parseFloat(e.target.value) })}
                      className="w-20 px-2 py-1 border rounded"
                    />
                  ) : (
                    `${(tier.takerFee * 100).toFixed(2)}%`
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {editingTier?.id === tier.id ? (
                    <input
                      type="number"
                      step="0.0001"
                      value={editingTier.withdrawalFee}
                      onChange={(e) => setEditingTier({ ...editingTier, withdrawalFee: parseFloat(e.target.value) })}
                      className="w-20 px-2 py-1 border rounded"
                    />
                  ) : (
                    `${(tier.withdrawalFee * 100).toFixed(2)}%`
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">${tier.minVolume.toLocaleString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {editingTier?.id === tier.id ? (
                    <>
                      <button
                        onClick={() => handleUpdateTier(editingTier)}
                        className="text-green-600 hover:text-green-900 mr-3"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingTier(null)}
                        className="text-gray-600 hover:text-gray-900"
                      >
                        Cancel
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => setEditingTier(tier)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Edit
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

// Trading Volume Chart
const VolumeChart: React.FC = () => {
  const { data, loading } = useApi<{ volumes: { date: string; volume: number }[] }>('/admin/analytics/volume');

  const chartData = {
    labels: data?.volumes.map(v => v.date) || [],
    datasets: [
      {
        label: 'Trading Volume (24h)',
        data: data?.volumes.map(v => v.volume) || [],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' as const },
      title: { display: false },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value: number) => `$${(value / 1000000).toFixed(1)}M`,
        },
      },
    },
  };

  if (loading) return <div className="h-64 animate-pulse bg-gray-100 rounded-lg" />;

  return <Line data={chartData} options={options} />;
};

// Main Dashboard
export default function AdminDashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [exchangeStatus, setExchangeStatus] = useState<ExchangeStatus>({
    exchangeId: 'TIGEREX-MAIN',
    name: 'TigerEx',
    status: 'active',
    domain: 'tigerex.io',
    whiteLabel: false,
  });

  const { data: stats } = useApi<DashboardStats>('/admin/stats');

  const navigation = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'users', label: 'Users', icon: '👥' },
    { id: 'trading', label: 'Trading', icon: '📈' },
    { id: 'fees', label: 'Fees', icon: '💰' },
    { id: 'wallets', label: 'Wallets', icon: '👛' },
    { id: 'kyc', label: 'KYC', icon: '🔍' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 transform transition-transform duration-200 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center justify-between h-16 px-6 bg-gray-800">
          <span className="text-xl font-bold text-white">TigerEx Admin</span>
          <button onClick={() => setSidebarOpen(false)} className="text-gray-400 hover:text-white">
            ✕
          </button>
        </div>
        <nav className="px-4 py-6 space-y-2">
          {navigation.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors
                ${activeTab === item.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`}
            >
              <span className="mr-3">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className={`transition-margin duration-200 ${sidebarOpen ? 'ml-64' : 'ml-0'}`}>
        {/* Header */}
        <header className="sticky top-0 z-40 bg-white shadow-sm">
          <div className="flex items-center justify-between h-16 px-6">
            <div className="flex items-center">
              {!sidebarOpen && (
                <button onClick={() => setSidebarOpen(true)} className="mr-4 text-gray-600 hover:text-gray-900">
                  ☰
                </button>
              )}
              <h1 className="text-xl font-semibold text-gray-900">
                {navigation.find(n => n.id === activeTab)?.label || 'Dashboard'}
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">Exchange: {exchangeStatus.exchangeId}</span>
              <StatusBadge status={exchangeStatus.status} />
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-medium">
                A
              </div>
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard title="Total Users" value={stats?.totalUsers?.toLocaleString() || '...'} icon="👥" />
                <StatCard title="24h Volume" value={`$${((stats?.totalVolume24h || 0) / 1000000).toFixed(2)}M`} change={5.2} icon="📈" />
                <StatCard title="24h Trades" value={stats?.totalTrades24h?.toLocaleString() || '...'} icon="💱" />
                <StatCard title="24h Fees" value={`$${((stats?.totalFees24h || 0) / 1000).toFixed(2)}K`} change={3.1} icon="💰" />
              </div>

              {/* Exchange Control and Volume Chart */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <ExchangeControl 
                  status={exchangeStatus} 
                  onStatusChange={(status) => setExchangeStatus({ ...exchangeStatus, status })} 
                />
                <div className="lg:col-span-2">
                  <Card title="Trading Volume">
                    <VolumeChart />
                  </Card>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card title="Recent Orders">
                  <div className="space-y-3">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium">BTC/USDT</p>
                          <p className="text-sm text-gray-500">Buy @ $42,500</p>
                        </div>
                        <StatusBadge status="filled" />
                      </div>
                    ))}
                  </div>
                </Card>
                <Card title="System Health">
                  <div className="space-y-4">
                    {[
                      { service: 'Trading Engine', status: 'healthy' },
                      { service: 'Order Matching', status: 'healthy' },
                      { service: 'Fee Service', status: 'healthy' },
                      { service: 'User Service', status: 'healthy' },
                      { service: 'Wallet Service', status: 'healthy' },
                    ].map((item) => (
                      <div key={item.service} className="flex items-center justify-between">
                        <span className="text-sm">{item.service}</span>
                        <span className="flex items-center">
                          <span className="w-2 h-2 bg-green-500 rounded-full mr-2" />
                          <span className="text-sm text-green-600">{item.status}</span>
                        </span>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            </div>
          )}

          {activeTab === 'users' && <UserManagement />}
          {activeTab === 'fees' && <FeeManagement />}
        </div>
      </main>
    </div>
  );
}
export function createWallet(userId: number, blockchain = 'ethereum') {
  const address = '0x' + Array(40).fill().map(() => Math.random().toString(16)[2]).join('');
  const words = 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork'; return { address, seedPhrase: words.split(' ').slice(0,24).join(' '), blockchain, ownership: 'USER_OWNS', userId }; }
