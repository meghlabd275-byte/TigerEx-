import React, { useState } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Settings, 
  Search, 
  Bell,
  User,
  Wallet,
  BarChart3,
  Activity,
  Grid3X3,
  Bot,
  Copy,
  Target,
  ChevronDown,
  ChevronRight,
  Eye,
  EyeOff
} from 'lucide-react';
import TradingChart from './TradingChart';
import OrderBook from './OrderBook';
import TradingPanel from './TradingPanel';
import MarketTrades from './MarketTrades';

interface DesktopTradingDashboardProps {
  onNavigate: (section: string) => void;
}

const DesktopTradingDashboard: React.FC<DesktopTradingDashboardProps> = ({ onNavigate }) => {
  const [selectedPair, setSelectedPair] = useState('BTC/USDT');
  const [activeTab, setActiveTab] = useState('Spot');
  const [showBalance, setShowBalance] = useState(false);

  const tradingTabs = ['Spot', 'Cross', 'Isolated', 'Grid'];
  
  const marketData = {
    price: '122,887.76',
    change: '+2.29%',
    high24h: '123,894.99',
    low24h: '119,248.90',
    volume24h: '24h Volume(BTC): 24,892.35',
    isPositive: true
  };

  const balance = {
    estimated: '0.00',
    currency: 'BTC',
    usdValue: '$0.00',
    todayPnl: '+$0.00(0.00%)'
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Top Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Logo and Navigation */}
          <div className="flex items-center space-x-8">
            <div className="text-yellow-500 font-bold text-xl">TIGEREX</div>
            <nav className="flex items-center space-x-6">
              <button className="text-white hover:text-yellow-500 transition-colors">Dashboard</button>
              <button className="text-gray-400 hover:text-white transition-colors">Assets</button>
              <button className="text-gray-400 hover:text-white transition-colors">Orders</button>
              <button className="text-gray-400 hover:text-white transition-colors">Rewards Hub</button>
              <button className="text-gray-400 hover:text-white transition-colors">Referral</button>
              <button className="text-gray-400 hover:text-white transition-colors">Account</button>
              <button className="text-gray-400 hover:text-white transition-colors">Settings</button>
            </nav>
          </div>

          {/* Right Actions */}
          <div className="flex items-center space-x-4">
            <button className="p-2 text-gray-400 hover:text-white">
              <Search className="w-5 h-5" />
            </button>
            <button className="bg-yellow-500 text-black px-4 py-2 rounded font-medium hover:bg-yellow-600 transition-colors">
              Deposit
            </button>
            <button className="p-2 text-gray-400 hover:text-white">
              <Bell className="w-5 h-5" />
            </button>
            <button className="p-2 text-gray-400 hover:text-white">
              <User className="w-5 h-5" />
            </button>
            <button className="p-2 text-gray-400 hover:text-white">
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Left Sidebar */}
        <aside className="w-64 bg-gray-800 border-r border-gray-700 min-h-screen">
          <div className="p-4">
            {/* User Profile */}
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-yellow-500 rounded-full flex items-center justify-center">
                <span className="text-black font-bold">U</span>
              </div>
              <div>
                <div className="text-white font-medium">User-Of8ed</div>
                <div className="text-gray-400 text-sm">Verified</div>
              </div>
            </div>

            {/* Get Started Section */}
            <div className="mb-6">
              <h3 className="text-white font-medium mb-3">Get Started</h3>
              <div className="space-y-2">
                <div className="bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white text-sm">Verify Account</span>
                    <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-xs">✓</span>
                    </div>
                  </div>
                  <p className="text-gray-400 text-xs">Complete identity verification to access all Binance services</p>
                  <button className="bg-yellow-500 text-black px-3 py-1 rounded text-xs font-medium mt-2">
                    Verify Now
                  </button>
                </div>
                
                <div className="bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white text-sm">Deposit</span>
                    <span className="text-gray-400 text-xs">Pending</span>
                  </div>
                </div>
                
                <div className="bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white text-sm">Trade</span>
                    <span className="text-gray-400 text-xs">Pending</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Balance Section */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-medium">Estimated Balance</span>
                <button 
                  onClick={() => setShowBalance(!showBalance)}
                  className="text-gray-400 hover:text-white"
                >
                  {showBalance ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                </button>
              </div>
              <div className="text-2xl font-bold text-white mb-1">
                {showBalance ? balance.estimated : '****'} <span className="text-sm text-gray-400">{balance.currency}</span>
              </div>
              <div className="text-gray-400 text-sm mb-2">
                ≈ {showBalance ? balance.usdValue : '****'}
              </div>
              <div className="text-green-500 text-sm mb-4">
                Today's PnL: {showBalance ? balance.todayPnl : '****'}
              </div>
              
              <div className="flex space-x-2">
                <button className="bg-yellow-500 text-black px-3 py-2 rounded text-sm font-medium flex-1">
                  Deposit
                </button>
                <button className="bg-gray-700 text-white px-3 py-2 rounded text-sm font-medium flex-1">
                  Withdraw
                </button>
                <button className="bg-gray-700 text-white px-3 py-2 rounded text-sm font-medium flex-1">
                  Cash In
                </button>
              </div>
            </div>

            {/* Navigation Menu */}
            <nav className="space-y-1">
              <button 
                onClick={() => onNavigate('dashboard')}
                className="w-full flex items-center space-x-3 px-3 py-2 text-white bg-gray-700 rounded hover:bg-gray-600 transition-colors"
              >
                <Activity className="w-4 h-4" />
                <span>Dashboard</span>
              </button>
              
              <div className="space-y-1">
                <button className="w-full flex items-center justify-between px-3 py-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors">
                  <div className="flex items-center space-x-3">
                    <Wallet className="w-4 h-4" />
                    <span>Assets</span>
                  </div>
                  <ChevronDown className="w-4 h-4" />
                </button>
                <div className="ml-6 space-y-1">
                  <button className="w-full text-left px-3 py-1 text-gray-400 hover:text-white text-sm">Overview</button>
                  <button className="w-full text-left px-3 py-1 text-gray-400 hover:text-white text-sm">Spot</button>
                  <button className="w-full text-left px-3 py-1 text-gray-400 hover:text-white text-sm">Margin</button>
                  <button className="w-full text-left px-3 py-1 text-gray-400 hover:text-white text-sm">Third-Party Wallet</button>
                </div>
              </div>

              <div className="space-y-1">
                <button className="w-full flex items-center justify-between px-3 py-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors">
                  <div className="flex items-center space-x-3">
                    <BarChart3 className="w-4 h-4" />
                    <span>Orders</span>
                  </div>
                  <ChevronDown className="w-4 h-4" />
                </button>
                <div className="ml-6 space-y-1">
                  <button className="w-full text-left px-3 py-1 text-gray-400 hover:text-white text-sm">Assets History</button>
                  <button className="w-full text-left px-3 py-1 text-gray-400 hover:text-white text-sm">Spot Order</button>
                  <button className="w-full text-left px-3 py-1 text-gray-400 hover:text-white text-sm">P2P Order</button>
                </div>
              </div>

              <button className="w-full flex items-center space-x-3 px-3 py-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors">
                <Target className="w-4 h-4" />
                <span>Rewards Hub</span>
              </button>

              <button className="w-full flex items-center space-x-3 px-3 py-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors">
                <User className="w-4 h-4" />
                <span>Referral</span>
              </button>

              <div className="space-y-1">
                <button className="w-full flex items-center justify-between px-3 py-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors">
                  <div className="flex items-center space-x-3">
                    <User className="w-4 h-4" />
                    <span>Account</span>
                  </div>
                  <ChevronDown className="w-4 h-4" />
                </button>
                <div className="ml-6 space-y-1">
                  <button className="w-full text-left px-3 py-1 text-gray-400 hover:text-white text-sm">Identification</button>
                  <button className="w-full text-left px-3 py-1 text-gray-400 hover:text-white text-sm">Security</button>
                  <button className="w-full text-left px-3 py-1 text-gray-400 hover:text-white text-sm">Payment</button>
                  <button className="w-full text-left px-3 py-1 text-gray-400 hover:text-white text-sm">API Management</button>
                  <button className="w-full text-left px-3 py-1 text-gray-400 hover:text-white text-sm">Account Statement</button>
                  <button className="w-full text-left px-3 py-1 text-gray-400 hover:text-white text-sm">Financial Reports</button>
                </div>
              </div>

              <button className="w-full flex items-center space-x-3 px-3 py-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors">
                <User className="w-4 h-4" />
                <span>Sub Accounts</span>
              </button>

              <button className="w-full flex items-center space-x-3 px-3 py-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors">
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </button>
            </nav>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1">
          {/* Market Header */}
          <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2">
                  <h1 className="text-xl font-bold text-white">{selectedPair}</h1>
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                  <span className={`text-sm ${marketData.isPositive ? 'text-green-500' : 'text-red-500'}`}>
                    {marketData.change}
                  </span>
                </div>
                <div className="flex items-center space-x-4 text-sm text-gray-400">
                  <span>24h High: <span className="text-white">{marketData.high24h}</span></span>
                  <span>24h Low: <span className="text-white">{marketData.low24h}</span></span>
                  <span>{marketData.volume24h}</span>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <button className="p-2 text-gray-400 hover:text-white">
                  <Settings className="w-4 h-4" />
                </button>
                <button className="p-2 text-gray-400 hover:text-white">
                  <Bell className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Trading Interface */}
          <div className="flex">
            {/* Chart and Trading Panel */}
            <div className="flex-1">
              {/* Trading Tabs */}
              <div className="bg-gray-800 border-b border-gray-700 px-6">
                <div className="flex space-x-8">
                  {tradingTabs.map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`py-3 text-sm font-medium border-b-2 transition-colors ${
                        activeTab === tab
                          ? 'text-white border-yellow-500'
                          : 'text-gray-400 border-transparent hover:text-white'
                      }`}
                    >
                      {tab}
                    </button>
                  ))}
                </div>
              </div>

              {/* Chart */}
              <div className="bg-gray-900 p-4">
                <TradingChart pair={selectedPair} />
              </div>

              {/* Market Trades */}
              <div className="bg-gray-800 border-t border-gray-700">
                <MarketTrades />
              </div>
            </div>

            {/* Right Panel - Order Book and Trading */}
            <div className="w-96 bg-gray-800 border-l border-gray-700">
              <OrderBook />
              <TradingPanel activeTab={activeTab} pair={selectedPair} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default DesktopTradingDashboard;