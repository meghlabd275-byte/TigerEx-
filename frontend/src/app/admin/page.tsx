import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface DashboardStats {
  totalUsers: number;
  activeTraders: number;
  totalVolume: string;
  revenue24h: string;
  pendingVerifications: number;
  systemStatus: 'operational' | 'degraded' | 'down';
}

interface RecentActivity {
  id: string;
  type: string;
  user: string;
  action: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error';
}

const AdminPage: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-purple-400">Admin Dashboard</h1>
              <span className="ml-4 px-3 py-1 rounded-full text-xs font-medium bg-purple-900/30 text-purple-300">
                {user?.role}
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium">
                Export Report
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { id: 'overview', name: 'Overview' },
              { id: 'ai-insights', name: 'AI Insights' },
              { id: 'portfolio-analytics', name: 'Portfolio Analytics' },
              { id: 'multi-tenant', name: 'Multi-Tenant' },
              { id: 'derivatives', name: 'Derivatives' },
              { id: 'institutional', name: 'Institutional' },
              { id: 'blockchain', name: 'Blockchain' },
              { id: 'compliance', name: 'Compliance' },
              { id: 'users', name: 'Users' },
              { id: 'settings', name: 'Settings' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-purple-500 text-purple-400'
                    : 'border-transparent text-gray-500 hover:text-gray-300 hover:border-gray-300'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'ai-insights' && <AIInsightsTab />}
        {activeTab === 'portfolio-analytics' && <PortfolioAnalyticsTab />}
        {activeTab === 'multi-tenant' && <MultiTenantTab />}
        {activeTab === 'derivatives' && <DerivativesTab />}
        {activeTab === 'institutional' && <InstitutionalTab />}
        {activeTab === 'blockchain' && <BlockchainTab />}
        {activeTab === 'compliance' && <ComplianceTab />}
        {activeTab === 'users' && <UsersTab />}
        {activeTab === 'settings' && <SettingsTab />}
      </main>
    </div>
  );
};

const OverviewTab: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalUsers: 15420,
    activeTraders: 3247,
    totalVolume: '$125.4M',
    revenue24h: '$42,350',
    pendingVerifications: 23,
    systemStatus: 'operational'
  });

  return (
    <div className="space-y-6">
      {/* System Status */}
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white mb-2">System Status</h2>
            <div className="flex items-center space-x-2">
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-900/20 text-green-400">
                OPERATIONAL
              </span>
              <span className="text-sm text-gray-400">All systems operational</span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-400">Uptime</p>
            <p className="text-lg font-semibold text-white">15:23:45</p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-400">Total Users</p>
              <p className="text-2xl font-bold text-white">{stats.totalUsers.toLocaleString()}</p>
              <p className="text-sm text-green-400 mt-2">+12.5% from last week</p>
            </div>
            <div className="h-12 w-12 bg-blue-900/20 rounded-lg flex items-center justify-center">
              <svg className="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-400">Active Traders</p>
              <p className="text-2xl font-bold text-white">{stats.activeTraders.toLocaleString()}</p>
              <p className="text-sm text-green-400 mt-2">+8.3% from yesterday</p>
            </div>
            <div className="h-12 w-12 bg-green-900/20 rounded-lg flex items-center justify-center">
              <svg className="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-400">24h Volume</p>
              <p className="text-2xl font-bold text-white">{stats.totalVolume}</p>
              <p className="text-sm text-green-400 mt-2">+15.7% from yesterday</p>
            </div>
            <div className="h-12 w-12 bg-purple-900/20 rounded-lg flex items-center justify-center">
              <svg className="h-6 w-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-400">Revenue (24h)</p>
              <p className="text-2xl font-bold text-white">{stats.revenue24h}</p>
              <p className="text-sm text-green-400 mt-2">+22.1% from yesterday</p>
            </div>
            <div className="h-12 w-12 bg-yellow-900/20 rounded-lg flex items-center justify-center">
              <svg className="h-6 w-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-6">Recent Activity</h3>
        <div className="space-y-4">
          {[
            { id: '1', type: 'user', user: 'john_trader', action: 'Completed KYC verification', timestamp: '2 minutes ago', status: 'success' },
            { id: '2', type: 'trade', user: 'alice_crypto', action: 'Placed large BTC order', timestamp: '5 minutes ago', status: 'success' },
            { id: '3', type: 'security', user: 'system', action: 'Detected unusual login pattern', timestamp: '12 minutes ago', status: 'warning' },
            { id: '4', type: 'ai', user: 'ai_engine', action: 'Generated trading signal', timestamp: '15 minutes ago', status: 'success' }
          ].map((activity) => (
            <div key={activity.id} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="h-2 w-2 rounded-full bg-green-400"></div>
                <div>
                  <p className="text-sm font-medium text-white">{activity.action}</p>
                  <p className="text-xs text-gray-400">by {activity.user} • {activity.timestamp}</p>
                </div>
              </div>
              <span className="px-2 py-1 rounded text-xs font-medium bg-blue-900/20 text-blue-400">
                {activity.type}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const AIInsightsTab: React.FC = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">AI-Powered Trading Insights</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">AI Model Performance</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-400">Price Prediction Model</span>
                <span className="text-sm text-green-400">87.3% Accuracy</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '87.3%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-400">Sentiment Analysis Model</span>
                <span className="text-sm text-blue-400">82.1% Accuracy</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: '82.1%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-400">Risk Assessment Model</span>
                <span className="text-sm text-yellow-400">91.7% Accuracy</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '91.7%' }}></div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Active Trading Signals</h3>
          <div className="space-y-3">
            {[
              { symbol: 'BTC/USDT', signal: 'BUY', confidence: 92, target: '$45,500' },
              { symbol: 'ETH/USDT', signal: 'HOLD', confidence: 65, target: '$2,350' },
              { symbol: 'SOL/USDT', signal: 'SELL', confidence: 78, target: '$85.20' },
              { symbol: 'ADA/USDT', signal: 'BUY', confidence: 71, target: '$0.65' }
            ].map((signal) => (
              <div key={signal.symbol} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-white">{signal.symbol}</p>
                  <p className="text-xs text-gray-400">Target: {signal.target}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    signal.signal === 'BUY' ? 'bg-green-900/20 text-green-400' :
                    signal.signal === 'SELL' ? 'bg-red-900/20 text-red-400' :
                    'bg-yellow-900/20 text-yellow-400'
                  }`}>
                    {signal.signal}
                  </span>
                  <span className="text-sm text-gray-400">{signal.confidence}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">AI Training Queue</h3>
        <div className="space-y-3">
          {[
            { model: 'Market Sentiment Analysis', status: 'Training', progress: 67 },
            { model: 'Volatility Prediction', status: 'Completed', progress: 100 },
            { model: 'Portfolio Optimization', status: 'Queued', progress: 0 },
            { model: 'Fraud Detection', status: 'Training', progress: 34 }
          ].map((item) => (
            <div key={item.model} className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-white">{item.model}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    item.status === 'Training' ? 'bg-blue-900/20 text-blue-400' :
                    item.status === 'Completed' ? 'bg-green-900/20 text-green-400' :
                    'bg-gray-900/20 text-gray-400'
                  }`}>
                    {item.status}
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300" 
                    style={{ width: `${item.progress}%` }}
                  ></div>
                </div>
              </div>
              <div className="ml-4 text-sm text-gray-400">{item.progress}%</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const PortfolioAnalyticsTab: React.FC = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Advanced Portfolio Analytics</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Portfolio Performance Overview</h3>
          <div className="h-64 bg-gray-700 rounded-lg flex items-center justify-center">
            <p className="text-gray-400">Performance Chart</p>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Risk Metrics</h3>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Portfolio Beta</span>
              <span className="text-sm font-medium text-white">1.23</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Sharpe Ratio</span>
              <span className="text-sm font-medium text-green-400">1.87</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Max Drawdown</span>
              <span className="text-sm font-medium text-red-400">-12.3%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Value at Risk (95%)</span>
              <span className="text-sm font-medium text-white">$2.34M</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Alpha</span>
              <span className="text-sm font-medium text-green-400">+3.2%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Asset Allocation</h3>
          <div className="space-y-3">
            {[
              { asset: 'Cryptocurrency', allocation: 45, color: 'bg-blue-500' },
              { asset: 'Stocks', allocation: 25, color: 'bg-green-500' },
              { asset: 'Bonds', allocation: 15, color: 'bg-yellow-500' },
              { asset: 'Real Estate', allocation: 10, color: 'bg-purple-500' },
              { asset: 'Cash', allocation: 5, color: 'bg-gray-500' }
            ].map((item) => (
              <div key={item.asset} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${item.color}`}></div>
                  <span className="text-sm text-gray-300">{item.asset}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-700 rounded-full h-2">
                    <div className={`${item.color} h-2 rounded-full`} style={{ width: `${item.allocation}%` }}></div>
                  </div>
                  <span className="text-sm font-medium text-white w-12 text-right">{item.allocation}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Portfolio Recommendations</h3>
          <div className="space-y-3">
            {[
              { type: 'RISK', priority: 'HIGH', title: 'High Concentration Risk', desc: 'Consider diversifying crypto holdings' },
              { type: 'PERFORMANCE', priority: 'MEDIUM', title: 'Underperforming Sector', desc: 'Energy sector showing weakness' },
              { type: 'OPPORTUNITY', priority: 'LOW', title: 'Rebalancing Opportunity', desc: 'Target allocation deviation detected' }
            ].map((rec) => (
              <div key={rec.title} className="p-3 bg-gray-700/50 rounded-lg">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-white">{rec.title}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    rec.priority === 'HIGH' ? 'bg-red-900/20 text-red-400' :
                    rec.priority === 'MEDIUM' ? 'bg-yellow-900/20 text-yellow-400' :
                    'bg-green-900/20 text-green-400'
                  }`}>
                    {rec.priority}
                  </span>
                </div>
                <p className="text-xs text-gray-400">{rec.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const MultiTenantTab: React.FC = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Multi-Tenant Management</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-blue-400">124</p>
          <p className="text-sm text-gray-400">Active Tenants</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-green-400">8,456</p>
          <p className="text-sm text-gray-400">Total Users</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-yellow-400">92%</p>
          <p className="text-sm text-gray-400">Utilization</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-purple-400">$2.4M</p>
          <p className="text-sm text-gray-400">MRR</p>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Recent Tenant Activity</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Tenant</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Plan</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Users</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {[
                { name: 'Acme Corp', plan: 'Enterprise', users: 156, status: 'Active' },
                { name: 'Tech Solutions Inc', plan: 'Pro', users: 45, status: 'Active' },
                { name: 'Global Trading Co', plan: 'Enterprise', users: 234, status: 'Active' },
                { name: 'StartupXYZ', plan: 'Basic', users: 12, status: 'Trial' }
              ].map((tenant) => (
                <tr key={tenant.name}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-white">{tenant.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{tenant.plan}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{tenant.users}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      tenant.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {tenant.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button className="text-blue-400 hover:text-blue-600 mr-3">Manage</button>
                    <button className="text-gray-400 hover:text-gray-600">View</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const DerivativesTab: React.FC = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Derivatives Trading Management</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Contract Overview</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Active Futures</span>
              <span className="text-sm font-medium text-white">47</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Perpetual Contracts</span>
              <span className="text-sm font-medium text-white">23</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Options Contracts</span>
              <span className="text-sm font-medium text-white">156</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Total Open Interest</span>
              <span className="text-sm font-medium text-white">$1.2B</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Risk Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">System Leverage</span>
              <span className="text-sm font-medium text-yellow-400">8.5x</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Margin Utilization</span>
              <span className="text-sm font-medium text-blue-400">67%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Liquidation Risk</span>
              <span className="text-sm font-medium text-green-400">Low</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Funding Rate (8h)</span>
              <span className="text-sm font-medium text-white">0.012%</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Volume Statistics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">24h Volume</span>
              <span className="text-sm font-medium text-white">$456M</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Open Positions</span>
              <span className="text-sm font-medium text-white">12,345</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Daily Trades</span>
              <span className="text-sm font-medium text-white">89,234</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Avg Trade Size</span>
              <span className="text-sm font-medium text-white">$5.1K</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Top Performing Contracts</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Contract</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Volume 24h</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Open Interest</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Funding Rate</th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {[
                { contract: 'BTC-USDT-PERP', type: 'Perpetual', volume: '$234M', oi: '$456M', funding: '0.012%' },
                { contract: 'ETH-USDT-PERP', type: 'Perpetual', volume: '$123M', oi: '$234M', funding: '0.008%' },
                { contract: 'BTC-USDT-0329', type: 'Future', volume: '$89M', oi: '$123M', funding: 'N/A' },
                { contract: 'SOL-USDT-PERP', type: 'Perpetual', volume: '$45M', oi: '$67M', funding: '0.025%' }
              ].map((item) => (
                <tr key={item.contract}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-white">{item.contract}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{item.type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{item.volume}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{item.oi}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{item.funding}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const InstitutionalTab: React.FC = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Institutional Client Management</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-blue-400">89</p>
          <p className="text-sm text-gray-400">Institutions</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-green-400">$45.6B</p>
          <p className="text-sm text-gray-400">AUM</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-yellow-400">234</p>
          <p className="text-sm text-gray-400">Active Strategies</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-purple-400">$12.3M</p>
          <p className="text-sm text-gray-400">Daily Volume</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">OTC Requests</h3>
          <div className="space-y-3">
            {[
              { institution: 'Acme Capital', asset: 'BTC', size: '$10M', status: 'Negotiating' },
              { institution: 'Global Hedge Fund', asset: 'ETH', size: '$5M', status: 'Executed' },
              { institution: 'Tech Trading Co', asset: 'Custom Derivative', size: '$2.5M', status: 'Pending' },
              { institution: 'Investment Partners', asset: 'Structured Product', size: '$15M', status: 'Negotiating' }
            ].map((request) => (
              <div key={request.institution} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-white">{request.institution}</p>
                  <p className="text-xs text-gray-400">{request.asset} • {request.size}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  request.status === 'Executed' ? 'bg-green-900/20 text-green-400' :
                  request.status === 'Negotiating' ? 'bg-yellow-900/20 text-yellow-400' :
                  'bg-blue-900/20 text-blue-400'
                }`}>
                  {request.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Algorithmic Strategies</h3>
          <div className="space-y-3">
            {[
              { name: 'Market Making Bot', status: 'Active', return: '+2.3%', trades: 1234 },
              { name: 'Arbitrage Strategy', status: 'Active', return: '+1.8%', trades: 892 },
              { name: 'Statistical Arbitrage', status: 'Paused', return: '+0.9%', trades: 456 },
              { name: 'Trend Following', status: 'Active', return: '+3.1%', trades: 2341 }
            ].map((strategy) => (
              <div key={strategy.name} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-white">{strategy.name}</p>
                  <p className="text-xs text-gray-400">{strategy.trades} trades</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-green-400">{strategy.return}</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    strategy.status === 'Active' ? 'bg-green-900/20 text-green-400' : 'bg-gray-900/20 text-gray-400'
                  }`}>
                    {strategy.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const BlockchainTab: React.FC = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Blockchain & Smart Contracts</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Network Status</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Ethereum Gas</span>
              <span className="text-sm font-medium text-white">45 Gwei</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">BNB Gas</span>
              <span className="text-sm font-medium text-white">12 Gwei</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Polygon Gas</span>
              <span className="text-sm font-medium text-white">8 Gwei</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Contracts Deployed</span>
              <span className="text-sm font-medium text-white">234</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">DeFi Integration</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Total TVL</span>
              <span className="text-sm font-medium text-green-400">$45.6M</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Active Positions</span>
              <span className="text-sm font-medium text-white">1,234</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Yield APY</span>
              <span className="text-sm font-medium text-yellow-400">8.5%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Bridge Volume</span>
              <span className="text-sm font-medium text-blue-400">$12.3M</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Smart Contracts</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Trading Contract</span>
              <span className="text-sm font-medium text-green-400">Verified</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Lending Contract</span>
              <span className="text-sm font-medium text-green-400">Verified</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Staking Contract</span>
              <span className="text-sm font-medium text-yellow-400">Pending</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-400">Governance Contract</span>
              <span className="text-sm font-medium text-green-400">Verified</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const ComplianceTab: React.FC = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Compliance & AML</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">KYC Status</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Pending Verification</span>
              <span className="px-3 py-1 bg-yellow-900/20 text-yellow-400 rounded-full text-xs">23</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Verified Users</span>
              <span className="px-3 py-1 bg-green-900/20 text-green-400 rounded-full text-xs">15,420</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Rejected Applications</span>
              <span className="px-3 py-1 bg-red-900/20 text-red-400 rounded-full text-xs">156</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">AML Monitoring</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">High Risk Transactions</span>
              <span className="px-3 py-1 bg-red-900/20 text-red-400 rounded-full text-xs">12</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Under Review</span>
              <span className="px-3 py-1 bg-yellow-900/20 text-yellow-400 rounded-full text-xs">45</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Cleared</span>
              <span className="px-3 py-1 bg-green-900/20 text-green-400 rounded-full text-xs">1,234</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const UsersTab: React.FC = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">User Management</h2>
      
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">All Users</h3>
          <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium">
            Add User
          </button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">User</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Role</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Last Active</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {[
                { user: 'John Doe', email: 'john@example.com', role: 'Admin', status: 'Active', lastActive: '2 hours ago' },
                { user: 'Jane Smith', email: 'jane@example.com', role: 'User', status: 'Active', lastActive: '5 minutes ago' },
                { user: 'Bob Wilson', email: 'bob@example.com', role: 'Trader', status: 'Suspended', lastActive: '1 day ago' }
              ].map((user) => (
                <tr key={user.email}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-white">{user.user}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{user.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{user.role}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      user.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{user.lastActive}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button className="text-blue-400 hover:text-blue-600 mr-3">Edit</button>
                    <button className="text-gray-400 hover:text-gray-600">Suspend</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const SettingsTab: React.FC = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">System Settings</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Trading Configuration</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Max Leverage</label>
              <input type="number" defaultValue="10" className="w-full bg-gray-700 border border-gray-600 rounded-md text-white px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Trading Fee (%)</label>
              <input type="number" defaultValue="0.1" step="0.01" className="w-full bg-gray-700 border border-gray-600 rounded-md text-white px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Maintenance Margin (%)</label>
              <input type="number" defaultValue="5" step="0.1" className="w-full bg-gray-700 border border-gray-600 rounded-md text-white px-3 py-2" />
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Security Settings</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">2FA Required</span>
              <button className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm">Enabled</button>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">IP Whitelist</span>
              <button className="bg-gray-600 hover:bg-gray-700 px-3 py-1 rounded text-sm">Disabled</button>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">Session Timeout</span>
              <input type="number" defaultValue="24" className="w-20 bg-gray-700 border border-gray-600 rounded text-white px-2 py-1" />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">System Configuration</h3>
          <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-md text-sm font-medium">
            Save Changes
          </button>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">API Rate Limit (req/min)</label>
            <input type="number" defaultValue="1000" className="w-full bg-gray-700 border border-gray-600 rounded-md text-white px-3 py-2" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Max Concurrent Users</label>
            <input type="number" defaultValue="10000" className="w-full bg-gray-700 border border-gray-600 rounded-md text-white px-3 py-2" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Cache TTL (seconds)</label>
            <input type="number" defaultValue="300" className="w-full bg-gray-700 border border-gray-600 rounded-md text-white px-3 py-2" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPage;