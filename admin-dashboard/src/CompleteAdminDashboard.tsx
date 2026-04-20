/**
 * TigerEx Admin Component
 * @file CompleteAdminDashboard.tsx
 * @description Admin dashboard component
 * @author TigerEx Development Team
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
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

// ============================================================================
// TYPES AND INTERFACES
// ============================================================================

interface User {
  id: string;
  email: string;
  username: string;
  role: string;
  status: 'active' | 'suspended' | 'banned' | 'frozen';
  kyc_status: string;
  created_at: string;
  last_login: string;
  total_volume: string;
  total_trades: number;
  balances?: Record<string, string>;
}

interface TradingPair {
  symbol: string;
  base: string;
  quote: string;
  status: string;
  maker_fee: string;
  taker_fee: string;
  min_order: string;
  max_order: string;
  price_precision: number;
  qty_precision: number;
}

interface Token {
  symbol: string;
  name: string;
  status: string;
  blockchain: string;
  decimals: number;
  withdrawal_enabled: boolean;
  deposit_enabled: boolean;
  withdrawal_fee: string;
  min_withdrawal: string;
  max_withdrawal: string;
}

interface SystemStatus {
  status: string;
  uptime: string;
  version: string;
  maintenance_mode: boolean;
  services: Record<string, string>;
}

interface Announcement {
  id: string;
  title: string;
  content: string;
  type: 'info' | 'warning' | 'critical';
  active: boolean;
  created_at: string;
}

interface Withdrawal {
  id: string;
  user_id: string;
  asset: string;
  amount: string;
  fee: string;
  address: string;
  network: string;
  status: 'pending' | 'approved' | 'rejected' | 'completed';
  created_at: string;
}

// ============================================================================
// MAIN ADMIN DASHBOARD COMPONENT
// ============================================================================

const CompleteAdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  const [tokens, setTokens] = useState<Token[]>([]);
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [withdrawals, setWithdrawals] = useState<Withdrawal[]>([]);
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [notifications, setNotifications] = useState<any[]>([]);

  // Stats
  const [stats, setStats] = useState({
    totalUsers: 125000,
    activeUsers: 45000,
    totalVolume24h: 15000000,
    totalFees24h: 75000,
    openTickets: 125,
    pendingWithdrawals: 45,
    pendingKYC: 230,
    totalTradingPairs: 150,
    activeOrders: 5600
  });

  // Fetch data on mount
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    // In production, fetch from API
    // Mock data for now
  };

  // ============================================================================
  // SIDEBAR NAVIGATION
  // ============================================================================

  const Sidebar = () => (
    <div className={`bg-gray-900 text-white h-screen fixed left-0 top-0 ${sidebarCollapsed ? 'w-16' : 'w-64'} transition-all duration-300 z-50`}>
      <div className="p-4 border-b border-gray-700 flex items-center justify-between">
        {!sidebarCollapsed && <h1 className="text-xl font-bold text-orange-500">🐅 TigerEx Admin</h1>}
        <button onClick={() => setSidebarCollapsed(!sidebarCollapsed)} className="p-2 hover:bg-gray-700 rounded">
          {sidebarCollapsed ? '→' : '←'}
        </button>
      </div>
      
      <nav className="mt-4">
        {[
          { id: 'overview', icon: '📊', label: 'Overview' },
          { id: 'users', icon: '👥', label: 'Users' },
          { id: 'trading', icon: '📈', label: 'Trading' },
          { id: 'financials', icon: '💰', label: 'Financials' },
          { id: 'tokens', icon: '🪙', label: 'Tokens' },
          { id: 'withdrawals', icon: '💸', label: 'Withdrawals' },
          { id: 'kyc', icon: '📋', label: 'KYC/AML' },
          { id: 'announcements', icon: '📢', label: 'Announcements' },
          { id: 'reports', icon: '📑', label: 'Reports' },
          { id: 'settings', icon: '⚙️', label: 'Settings' },
          { id: 'security', icon: '🔒', label: 'Security' },
          { id: 'logs', icon: '📝', label: 'Audit Logs' }
        ].map(item => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-800 transition-colors ${activeTab === item.id ? 'bg-orange-600 text-white' : ''}`}
          >
            <span className="text-lg">{item.icon}</span>
            {!sidebarCollapsed && <span>{item.label}</span>}
          </button>
        ))}
      </nav>
      
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-700">
        {!sidebarCollapsed && (
          <div className="text-xs text-gray-400">
            <div>Version: 3.0.0</div>
            <div>Role: Super Admin</div>
          </div>
        )}
      </div>
    </div>
  );

  // ============================================================================
  // TOP HEADER
  // ============================================================================

  const TopHeader = () => (
    <header className="bg-white shadow-sm h-16 fixed top-0 right-0 left-0 z-40 flex items-center justify-between px-6" style={{ marginLeft: sidebarCollapsed ? '4rem' : '16rem' }}>
      <div className="flex items-center gap-4">
        <div className="relative">
          <input
            type="text"
            placeholder="Search users, orders, transactions..."
            className="w-96 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        {/* Quick Actions */}
        <button className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors">
          🛑 Emergency Stop
        </button>
        
        {/* Notifications */}
        <div className="relative">
          <button className="p-2 hover:bg-gray-100 rounded-full relative">
            🔔
            <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {notifications.length}
            </span>
          </button>
        </div>
        
        {/* Admin Profile */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center text-white font-bold">
            A
          </div>
          <span className="font-medium">Admin</span>
        </div>
      </div>
    </header>
  );

  // ============================================================================
  // OVERVIEW TAB
  // ============================================================================

  const OverviewTab = () => {
    const volumeChartData = {
      labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
      datasets: [{
        label: 'Trading Volume (USDT)',
        data: [500000, 800000, 1200000, 2500000, 3200000, 2800000, 1500000],
        fill: true,
        borderColor: '#f97316',
        backgroundColor: 'rgba(249, 115, 22, 0.1)',
        tension: 0.4
      }]
    };

    const userDistributionData = {
      labels: ['Active', 'Suspended', 'Banned', 'Pending'],
      datasets: [{
        data: [stats.activeUsers, 2500, 500, 15000],
        backgroundColor: ['#22c55e', '#eab308', '#ef4444', '#6b7280']
      }]
    };

    return (
      <div className="space-y-6">
        {/* Quick Stats */}
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: 'Total Users', value: stats.totalUsers.toLocaleString(), icon: '👥', color: 'blue' },
            { label: '24h Volume', value: `$${(stats.totalVolume24h / 1000000).toFixed(1)}M`, icon: '📈', color: 'green' },
            { label: '24h Fees', value: `$${stats.totalFees24h.toLocaleString()}`, icon: '💰', color: 'orange' },
            { label: 'Active Orders', value: stats.activeOrders.toLocaleString(), icon: '📋', color: 'purple' }
          ].map((stat, i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm">{stat.label}</p>
                  <p className="text-2xl font-bold mt-1">{stat.value}</p>
                </div>
                <div className="text-3xl">{stat.icon}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Alerts Row */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 flex items-center gap-4">
            <div className="text-3xl">⚠️</div>
            <div>
              <p className="font-medium text-yellow-800">Pending Withdrawals</p>
              <p className="text-2xl font-bold text-yellow-900">{stats.pendingWithdrawals}</p>
            </div>
            <button className="ml-auto px-4 py-2 bg-yellow-500 text-white rounded-lg">Review</button>
          </div>
          
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-center gap-4">
            <div className="text-3xl">📋</div>
            <div>
              <p className="font-medium text-blue-800">Pending KYC</p>
              <p className="text-2xl font-bold text-blue-900">{stats.pendingKYC}</p>
            </div>
            <button className="ml-auto px-4 py-2 bg-blue-500 text-white rounded-lg">Review</button>
          </div>
          
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-4">
            <div className="text-3xl">🎫</div>
            <div>
              <p className="font-medium text-red-800">Open Tickets</p>
              <p className="text-2xl font-bold text-red-900">{stats.openTickets}</p>
            </div>
            <button className="ml-auto px-4 py-2 bg-red-500 text-white rounded-lg">View</button>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="font-semibold mb-4">24h Trading Volume</h3>
            <Line data={volumeChartData} options={{ responsive: true, plugins: { legend: { display: false } } }} />
          </div>
          
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="font-semibold mb-4">User Distribution</h3>
            <div className="w-64 mx-auto">
              <Doughnut data={userDistributionData} options={{ responsive: true }} />
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold mb-4">System Status</h3>
          <div className="grid grid-cols-6 gap-4">
            {Object.entries({
              'Trading Engine': 'running',
              'Matching Engine': 'running',
              'Wallet Service': 'running',
              'Auth Service': 'running',
              'KYC Service': 'running',
              'Notifications': 'degraded'
            }).map(([service, status]) => (
              <div key={service} className="text-center p-3 rounded-lg bg-gray-50">
                <div className={`w-4 h-4 rounded-full mx-auto mb-2 ${status === 'running' ? 'bg-green-500' : status === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'}`}></div>
                <p className="text-xs text-gray-600">{service}</p>
                <p className={`text-xs font-medium ${status === 'running' ? 'text-green-600' : 'text-yellow-600'}`}>{status}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  // ============================================================================
  // USERS TAB
  // ============================================================================

  const UsersTab = () => {
    const [selectedUser, setSelectedUser] = useState<User | null>(null);
    const [userFilter, setUserFilter] = useState('all');

    const mockUsers: User[] = [
      { id: '1', email: 'john@example.com', username: 'johndoe', role: 'trader', status: 'active', kyc_status: 'approved', created_at: '2024-01-15', last_login: '2024-04-10', total_volume: '125000', total_trades: 450 },
      { id: '2', email: 'jane@example.com', username: 'janetrader', role: 'vip_trader', status: 'active', kyc_status: 'approved', created_at: '2024-02-01', last_login: '2024-04-10', total_volume: '500000', total_trades: 1200 },
      { id: '3', email: 'mike@example.com', username: 'mikepro', role: 'trader', status: 'suspended', kyc_status: 'pending', created_at: '2024-02-15', last_login: '2024-04-08', total_volume: '50000', total_trades: 120 },
    ];

    return (
      <div className="space-y-4">
        {/* User Management Header */}
        <div className="flex justify-between items-center">
          <div className="flex gap-2">
            {['all', 'active', 'suspended', 'banned', 'pending'].map(filter => (
              <button
                key={filter}
                onClick={() => setUserFilter(filter)}
                className={`px-4 py-2 rounded-lg capitalize ${userFilter === filter ? 'bg-orange-500 text-white' : 'bg-gray-100'}`}
              >
                {filter}
              </button>
            ))}
          </div>
          <button className="px-4 py-2 bg-orange-500 text-white rounded-lg">+ Add User</button>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">User</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Role</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">KYC</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Volume</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Trades</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody>
              {mockUsers.map(user => (
                <tr key={user.id} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium">{user.username}</p>
                      <p className="text-sm text-gray-500">{user.email}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm capitalize">{user.role}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-sm ${
                      user.status === 'active' ? 'bg-green-100 text-green-800' :
                      user.status === 'suspended' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-sm ${
                      user.kyc_status === 'approved' ? 'bg-green-100 text-green-800' :
                      user.kyc_status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {user.kyc_status}
                    </span>
                  </td>
                  <td className="px-4 py-3">${parseInt(user.total_volume).toLocaleString()}</td>
                  <td className="px-4 py-3">{user.total_trades}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button onClick={() => setSelectedUser(user)} className="px-3 py-1 bg-blue-500 text-white rounded text-sm">View</button>
                      <button className="px-3 py-1 bg-yellow-500 text-white rounded text-sm">Edit</button>
                      <button className="px-3 py-1 bg-red-500 text-white rounded text-sm">Suspend</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* User Detail Modal */}
        {selectedUser && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-6 w-full max-w-2xl">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">User Details: {selectedUser.username}</h2>
                <button onClick={() => setSelectedUser(null)} className="text-gray-500">✕</button>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <p><span className="font-medium">Email:</span> {selectedUser.email}</p>
                  <p><span className="font-medium">Role:</span> {selectedUser.role}</p>
                  <p><span className="font-medium">Status:</span> {selectedUser.status}</p>
                  <p><span className="font-medium">KYC:</span> {selectedUser.kyc_status}</p>
                </div>
                <div className="space-y-2">
                  <p><span className="font-medium">Total Volume:</span> ${parseInt(selectedUser.total_volume).toLocaleString()}</p>
                  <p><span className="font-medium">Total Trades:</span> {selectedUser.total_trades}</p>
                  <p><span className="font-medium">Created:</span> {selectedUser.created_at}</p>
                  <p><span className="font-medium">Last Login:</span> {selectedUser.last_login}</p>
                </div>
              </div>
              
              <div className="mt-6 flex gap-2">
                <button className="px-4 py-2 bg-green-500 text-white rounded-lg">Activate</button>
                <button className="px-4 py-2 bg-yellow-500 text-white rounded-lg">Suspend</button>
                <button className="px-4 py-2 bg-red-500 text-white rounded-lg">Ban</button>
                <button className="px-4 py-2 bg-purple-500 text-white rounded-lg">Freeze Balances</button>
                <button className="px-4 py-2 bg-gray-500 text-white rounded-lg">Impersonate</button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  // ============================================================================
  // TRADING TAB
  // ============================================================================

  const TradingTab = () => {
    const [tradingEnabled, setTradingEnabled] = useState(true);
    const [spotEnabled, setSpotEnabled] = useState(true);
    const [futuresEnabled, setFuturesEnabled] = useState(true);

    return (
      <div className="space-y-6">
        {/* Trading Controls */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold mb-4">Trading Controls</h3>
          <div className="grid grid-cols-4 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium">Master Switch</span>
                <button
                  onClick={() => setTradingEnabled(!tradingEnabled)}
                  className={`w-12 h-6 rounded-full ${tradingEnabled ? 'bg-green-500' : 'bg-gray-300'} relative`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-all ${tradingEnabled ? 'right-0.5' : 'left-0.5'}`}></div>
                </button>
              </div>
              <p className="text-sm text-gray-500">Enable/Disable all trading</p>
            </div>
            
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium">Spot Trading</span>
                <button
                  onClick={() => setSpotEnabled(!spotEnabled)}
                  className={`w-12 h-6 rounded-full ${spotEnabled ? 'bg-green-500' : 'bg-gray-300'} relative`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-all ${spotEnabled ? 'right-0.5' : 'left-0.5'}`}></div>
                </button>
              </div>
              <p className="text-sm text-gray-500">Spot market trading</p>
            </div>
            
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium">Futures Trading</span>
                <button
                  onClick={() => setFuturesEnabled(!futuresEnabled)}
                  className={`w-12 h-6 rounded-full ${futuresEnabled ? 'bg-green-500' : 'bg-gray-300'} relative`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-all ${futuresEnabled ? 'right-0.5' : 'left-0.5'}`}></div>
                </button>
              </div>
              <p className="text-sm text-gray-500">Futures & derivatives</p>
            </div>
            
            <div className="p-4 bg-red-50 rounded-lg">
              <button className="w-full px-4 py-2 bg-red-500 text-white rounded-lg font-medium">
                🛑 HALT ALL TRADING
              </button>
              <p className="text-sm text-red-600 mt-2">Emergency stop all operations</p>
            </div>
          </div>
        </div>

        {/* Trading Pairs Management */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold">Trading Pairs</h3>
            <button className="px-4 py-2 bg-orange-500 text-white rounded-lg">+ Add Pair</button>
          </div>
          
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Pair</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Maker Fee</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Taker Fee</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Min Order</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody>
              {['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT'].map(pair => (
                <tr key={pair} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{pair}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">Active</span>
                  </td>
                  <td className="px-4 py-3">0.1%</td>
                  <td className="px-4 py-3">0.1%</td>
                  <td className="px-4 py-3">0.0001</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button className="px-3 py-1 bg-blue-500 text-white rounded text-sm">Edit</button>
                      <button className="px-3 py-1 bg-yellow-500 text-white rounded text-sm">Pause</button>
                      <button className="px-3 py-1 bg-red-500 text-white rounded text-sm">Delist</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  // ============================================================================
  // FINANCIALS TAB
  // ============================================================================

  const FinancialsTab = () => {
    return (
      <div className="space-y-6">
        {/* Financial Overview */}
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: 'Total Assets', value: '$50,000,000', icon: '🏦' },
            { label: 'User Balances', value: '$35,000,000', icon: '👥' },
            { label: 'Pending Withdrawals', value: '$500,000', icon: '💸' },
            { label: 'Reserve Fund', value: '$10,000,000', icon: '🛡️' }
          ].map((item, i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm p-6">
              <div className="text-3xl mb-2">{item.icon}</div>
              <p className="text-gray-500 text-sm">{item.label}</p>
              <p className="text-2xl font-bold">{item.value}</p>
            </div>
          ))}
        </div>

        {/* Withdrawal Queue */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold">Withdrawal Queue</h3>
            <div className="flex gap-2">
              <button className="px-4 py-2 bg-green-500 text-white rounded-lg">Approve All (Safe)</button>
              <button className="px-4 py-2 bg-blue-500 text-white rounded-lg">Export CSV</button>
            </div>
          </div>
          
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">User</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Asset</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Amount</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Address</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Risk Score</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody>
              {[
                { user: 'user_001', asset: 'USDT', amount: '10,000', address: '0x1234...abcd', risk: 'low' },
                { user: 'user_002', asset: 'BTC', amount: '2.5', address: 'bc1q...xyz', risk: 'medium' },
                { user: 'user_003', asset: 'ETH', amount: '50', address: '0x5678...efgh', risk: 'high' }
              ].map((wd, i) => (
                <tr key={i} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-3">{wd.user}</td>
                  <td className="px-4 py-3 font-medium">{wd.asset}</td>
                  <td className="px-4 py-3">{wd.amount}</td>
                  <td className="px-4 py-3 font-mono text-sm">{wd.address}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-sm ${
                      wd.risk === 'low' ? 'bg-green-100 text-green-800' :
                      wd.risk === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {wd.risk}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button className="px-3 py-1 bg-green-500 text-white rounded text-sm">Approve</button>
                      <button className="px-3 py-1 bg-red-500 text-white rounded text-sm">Reject</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Balance Adjustment */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold mb-4">Balance Adjustment</h3>
          <div className="grid grid-cols-4 gap-4">
            <input type="text" placeholder="User ID" className="px-4 py-2 border rounded-lg" />
            <input type="text" placeholder="Asset" className="px-4 py-2 border rounded-lg" />
            <input type="number" placeholder="Amount" className="px-4 py-2 border rounded-lg" />
            <select className="px-4 py-2 border rounded-lg">
              <option>Add</option>
              <option>Subtract</option>
              <option>Set</option>
            </select>
          </div>
          <textarea placeholder="Reason for adjustment..." className="w-full mt-4 px-4 py-2 border rounded-lg" rows={2}></textarea>
          <button className="mt-4 px-4 py-2 bg-orange-500 text-white rounded-lg">Apply Adjustment</button>
        </div>
      </div>
    );
  };

  // ============================================================================
  // SETTINGS TAB
  // ============================================================================

  const SettingsTab = () => {
    return (
      <div className="space-y-6">
        {/* System Configuration */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold mb-4">System Configuration</h3>
          <div className="space-y-4">
            {[
              { label: 'Maintenance Mode', desc: 'Put the exchange in maintenance mode', enabled: false },
              { label: 'New Registrations', desc: 'Allow new user registrations', enabled: true },
              { label: 'KYC Required', desc: 'Require KYC for trading', enabled: true },
              { label: '2FA Required', desc: 'Require 2FA for withdrawals', enabled: true }
            ].map((setting, i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">{setting.label}</p>
                  <p className="text-sm text-gray-500">{setting.desc}</p>
                </div>
                <button className={`w-12 h-6 rounded-full ${setting.enabled ? 'bg-green-500' : 'bg-gray-300'} relative`}>
                  <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-all ${setting.enabled ? 'right-0.5' : 'left-0.5'}`}></div>
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Fee Management */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold mb-4">Fee Management</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <label className="block text-sm font-medium mb-2">Default Maker Fee (%)</label>
              <input type="number" defaultValue="0.1" step="0.01" className="w-full px-4 py-2 border rounded-lg" />
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <label className="block text-sm font-medium mb-2">Default Taker Fee (%)</label>
              <input type="number" defaultValue="0.1" step="0.01" className="w-full px-4 py-2 border rounded-lg" />
            </div>
          </div>
          <button className="mt-4 px-4 py-2 bg-orange-500 text-white rounded-lg">Save Fee Settings</button>
        </div>

        {/* Service Management */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold mb-4">Service Management</h3>
          <div className="grid grid-cols-3 gap-4">
            {[
              { name: 'Trading Engine', status: 'running' },
              { name: 'Matching Engine', status: 'running' },
              { name: 'Wallet Service', status: 'running' },
              { name: 'Auth Service', status: 'running' },
              { name: 'KYC Service', status: 'running' },
              { name: 'Notification Service', status: 'running' }
            ].map((service, i) => (
              <div key={i} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{service.name}</span>
                  <span className={`px-2 py-1 rounded text-xs ${service.status === 'running' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {service.status}
                  </span>
                </div>
                <div className="flex gap-2">
                  <button className="flex-1 px-2 py-1 bg-yellow-500 text-white rounded text-xs">Restart</button>
                  <button className="flex-1 px-2 py-1 bg-red-500 text-white rounded text-xs">Stop</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  return (
    <div className="min-h-screen bg-gray-100">
      <Sidebar />
      <TopHeader />
      
      <main className="pt-20 pb-8 px-6" style={{ marginLeft: sidebarCollapsed ? '4rem' : '16rem' }}>
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'users' && <UsersTab />}
        {activeTab === 'trading' && <TradingTab />}
        {activeTab === 'financials' && <FinancialsTab />}
        {activeTab === 'settings' && <SettingsTab />}
        
        {/* Placeholder for other tabs */}
        {!['overview', 'users', 'trading', 'financials', 'settings'].includes(activeTab) && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-bold capitalize">{activeTab}</h2>
            <p className="text-gray-500 mt-2">This section is under development...</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default CompleteAdminDashboard;