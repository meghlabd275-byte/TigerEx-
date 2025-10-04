import React, { useState } from 'react';
import { 
  Users, 
  TrendingUp, 
  DollarSign, 
  Activity, 
  Settings, 
  Shield, 
  Database,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Eye,
  Edit,
  Trash2
} from 'lucide-react';

interface AdminDashboardProps {
  onNavigate: (section: string) => void;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ onNavigate }) => {
  const [activeTab, setActiveTab] = useState('overview');

  const stats = {
    totalUsers: 125430,
    activeTraders: 8945,
    totalVolume: '$2.5B',
    totalRevenue: '$12.5M',
    pendingKYC: 234,
    suspendedAccounts: 12,
    systemHealth: 99.9
  };

  const recentUsers = [
    { id: '39333599', username: 'User-2ede9', status: 'verified', joinDate: '2025-10-04', volume: '$1,250' },
    { id: '39333598', username: 'TraderPro', status: 'pending', joinDate: '2025-10-04', volume: '$850' },
    { id: '39333597', username: 'CryptoKing', status: 'verified', joinDate: '2025-10-03', volume: '$5,420' },
    { id: '39333596', username: 'BlockMaster', status: 'suspended', joinDate: '2025-10-03', volume: '$0' }
  ];

  const systemServices = [
    { name: 'Authentication Service', status: 'healthy', uptime: '99.9%' },
    { name: 'Trading Engine', status: 'healthy', uptime: '99.8%' },
    { name: 'Wallet Service', status: 'healthy', uptime: '100%' },
    { name: 'Market Data', status: 'warning', uptime: '98.5%' },
    { name: 'Notification Service', status: 'healthy', uptime: '99.7%' }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'verified':
      case 'healthy':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'pending':
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'suspended':
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'verified':
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'pending':
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'suspended':
      case 'error':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">TigerEx Admin Dashboard</h1>
          <div className="flex items-center space-x-4">
            <button className="p-2 text-gray-600 hover:text-gray-900">
              <Settings className="w-5 h-5" />
            </button>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-bold">A</span>
              </div>
              <span className="text-sm font-medium text-gray-900">Admin</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-gray-200 px-6">
        <div className="flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: Activity },
            { id: 'users', label: 'Users', icon: Users },
            { id: 'trading', label: 'Trading', icon: TrendingUp },
            { id: 'finance', label: 'Finance', icon: DollarSign },
            { id: 'system', label: 'System', icon: Database },
            { id: 'security', label: 'Security', icon: Shield }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`flex items-center space-x-2 py-4 border-b-2 transition-colors ${
                activeTab === id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="font-medium">{label}</span>
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className="p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Users</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.totalUsers.toLocaleString()}</p>
                  </div>
                  <Users className="w-8 h-8 text-blue-500" />
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Active Traders</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.activeTraders.toLocaleString()}</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-green-500" />
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Volume</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.totalVolume}</p>
                  </div>
                  <DollarSign className="w-8 h-8 text-yellow-500" />
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">System Health</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.systemHealth}%</p>
                  </div>
                  <Activity className="w-8 h-8 text-purple-500" />
                </div>
              </div>
            </div>

            {/* Recent Users */}
            <div className="bg-white rounded-lg border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Recent Users</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Join Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Volume</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {recentUsers.map((user) => (
                      <tr key={user.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div>
                            <div className="font-medium text-gray-900">{user.username}</div>
                            <div className="text-sm text-gray-500">ID: {user.id}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(user.status)}`}>
                            {getStatusIcon(user.status)}
                            <span className="capitalize">{user.status}</span>
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">{user.joinDate}</td>
                        <td className="px-6 py-4 text-sm text-gray-900">{user.volume}</td>
                        <td className="px-6 py-4">
                          <div className="flex items-center space-x-2">
                            <button className="p-1 text-gray-400 hover:text-blue-600">
                              <Eye className="w-4 h-4" />
                            </button>
                            <button className="p-1 text-gray-400 hover:text-green-600">
                              <Edit className="w-4 h-4" />
                            </button>
                            <button className="p-1 text-gray-400 hover:text-red-600">
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* System Services */}
            <div className="bg-white rounded-lg border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">System Services</h2>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {systemServices.map((service, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(service.status)}
                        <div>
                          <div className="font-medium text-gray-900">{service.name}</div>
                          <div className="text-sm text-gray-500">Uptime: {service.uptime}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">User Management</h2>
            </div>
            <div className="p-6">
              <p className="text-gray-600">Complete user management interface with KYC, verification, and account controls.</p>
            </div>
          </div>
        )}

        {activeTab === 'trading' && (
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Trading Management</h2>
            </div>
            <div className="p-6">
              <p className="text-gray-600">Trading engine controls, order management, and market oversight.</p>
            </div>
          </div>
        )}

        {activeTab === 'finance' && (
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Financial Management</h2>
            </div>
            <div className="p-6">
              <p className="text-gray-600">Revenue tracking, fee management, and financial reporting.</p>
            </div>
          </div>
        )}

        {activeTab === 'system' && (
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">System Management</h2>
            </div>
            <div className="p-6">
              <p className="text-gray-600">System monitoring, service management, and infrastructure controls.</p>
            </div>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Security Management</h2>
            </div>
            <div className="p-6">
              <p className="text-gray-600">Security monitoring, threat detection, and access controls.</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminDashboard;