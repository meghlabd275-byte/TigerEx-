/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

import React, { useState } from 'react';
import { 
  Bot, 
  Play, 
  Pause, 
  Square as Stop, 
  Settings, 
  TrendingUp, 
  TrendingDown,
  BarChart3,
  DollarSign,
  Clock,
  Target,
  Zap,
  Info,
  Brain,
  Activity,
  Repeat
} from 'lucide-react';

const BotTrading: React.FC = () => {
  const [activeTab, setActiveTab] = useState('Marketplace');
  const [selectedBot, setSelectedBot] = useState<any>(null);

  const tabs = ['Marketplace', 'My Bots', 'Create Bot', 'Performance'];

  // Mock bot marketplace data
  const botMarketplace = [
    {
      id: 1,
      name: 'DCA Master Pro',
      type: 'DCA',
      description: 'Advanced Dollar Cost Averaging with smart entry points',
      creator: 'TradingBot Labs',
      rating: 4.8,
      users: 12450,
      performance: {
        roi: '+156.7%',
        winRate: '87.3%',
        maxDrawdown: '-8.2%',
        avgTrade: '2.4%'
      },
      price: 'Free',
      tags: ['DCA', 'Long-term', 'Low Risk'],
      supported: ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'],
      isVerified: true
    },
    {
      id: 2,
      name: 'Scalping Beast',
      type: 'Scalping',
      description: 'High-frequency scalping bot for quick profits',
      creator: 'AlgoTrader Pro',
      rating: 4.6,
      users: 8920,
      performance: {
        roi: '+234.5%',
        winRate: '72.1%',
        maxDrawdown: '-15.3%',
        avgTrade: '0.8%'
      },
      price: '$29.99/month',
      tags: ['Scalping', 'High Frequency', 'High Risk'],
      supported: ['BTC/USDT', 'ETH/USDT'],
      isVerified: true
    },
    {
      id: 3,
      name: 'Trend Follower AI',
      type: 'Trend Following',
      description: 'AI-powered trend following with machine learning',
      creator: 'AI Trading Systems',
      rating: 4.9,
      users: 6750,
      performance: {
        roi: '+189.2%',
        winRate: '79.8%',
        maxDrawdown: '-12.1%',
        avgTrade: '3.2%'
      },
      price: '$49.99/month',
      tags: ['AI', 'Trend Following', 'Medium Risk'],
      supported: ['All Major Pairs'],
      isVerified: true
    },
    {
      id: 4,
      name: 'Arbitrage Hunter',
      type: 'Arbitrage',
      description: 'Cross-exchange arbitrage opportunities detector',
      creator: 'ArbiBot Inc',
      rating: 4.7,
      users: 3420,
      performance: {
        roi: '+98.4%',
        winRate: '94.2%',
        maxDrawdown: '-3.1%',
        avgTrade: '0.3%'
      },
      price: '$99.99/month',
      tags: ['Arbitrage', 'Low Risk', 'Cross Exchange'],
      supported: ['Multiple Exchanges'],
      isVerified: false
    }
  ];

  // Mock user's active bots
  const myBots = [
    {
      id: 1,
      name: 'DCA Master Pro',
      type: 'DCA',
      pair: 'BTC/USDT',
      status: 'Running',
      investment: 1000,
      currentValue: 1156.7,
      pnl: 156.7,
      pnlPercent: 15.67,
      trades: 24,
      startDate: '2024-09-01',
      lastTrade: '2024-10-04 08:30:00'
    },
    {
      id: 2,
      name: 'Scalping Beast',
      type: 'Scalping',
      pair: 'ETH/USDT',
      status: 'Paused',
      investment: 500,
      currentValue: 478.5,
      pnl: -21.5,
      pnlPercent: -4.3,
      trades: 156,
      startDate: '2024-09-15',
      lastTrade: '2024-10-03 22:15:00'
    }
  ];

  const handleSubscribeBot = (botId: number) => {
    console.log('Subscribing to bot:', botId);
    alert('Bot subscription successful! Configure your settings to start trading.');
  };

  const handleStartBot = (botId: number) => {
    console.log('Starting bot:', botId);
    alert(`Bot ${botId} started successfully!`);
  };

  const handleStopBot = (botId: number) => {
    console.log('Stopping bot:', botId);
    alert(`Bot ${botId} stopped successfully!`);
  };

  return (
    <div className="bg-gray-900 text-white min-h-screen">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Bot className="w-8 h-8 text-yellow-500" />
            <div>
              <h1 className="text-2xl font-bold text-white">Trading Bots</h1>
              <p className="text-gray-400">Automated trading strategies for consistent profits</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-sm text-gray-400">Active Bots</div>
              <div className="text-2xl font-bold text-green-500">2</div>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-sm text-gray-400">Total Profit</div>
              <div className="text-2xl font-bold text-green-500">+$135.20</div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="flex space-x-8 px-6">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-4 text-sm font-medium border-b-2 transition-colors ${
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

      {/* Content */}
      <div className="p-6">
        {activeTab === 'Marketplace' && (
          <div>
            {/* Filters */}
            <div className="flex items-center space-x-4 mb-6">
              <span className="text-gray-400">Filter by:</span>
              <button className="px-3 py-1 bg-yellow-500 text-black rounded text-sm">All</button>
              <button className="px-3 py-1 bg-gray-700 text-gray-300 hover:bg-gray-600 rounded text-sm">DCA</button>
              <button className="px-3 py-1 bg-gray-700 text-gray-300 hover:bg-gray-600 rounded text-sm">Scalping</button>
              <button className="px-3 py-1 bg-gray-700 text-gray-300 hover:bg-gray-600 rounded text-sm">Grid</button>
              <button className="px-3 py-1 bg-gray-700 text-gray-300 hover:bg-gray-600 rounded text-sm">AI</button>
              <button className="px-3 py-1 bg-gray-700 text-gray-300 hover:bg-gray-600 rounded text-sm">Arbitrage</button>
            </div>

            {/* Bot Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {botMarketplace.map((bot) => (
                <div key={bot.id} className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                  {/* Bot Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-lg flex items-center justify-center">
                        <Bot className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="font-semibold text-white">{bot.name}</h3>
                          {bot.isVerified && (
                            <div className="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                              <span className="text-white text-xs">✓</span>
                            </div>
                          )}
                        </div>
                        <div className="text-sm text-gray-400">{bot.creator}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-yellow-500 font-bold">{bot.price}</div>
                      <div className="flex items-center space-x-1 text-sm text-gray-400">
                        <span>★</span>
                        <span>{bot.rating}</span>
                      </div>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-gray-400 text-sm mb-4">{bot.description}</p>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {bot.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-700 text-xs rounded text-gray-300"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  {/* Performance Stats */}
                  <div className="grid grid-cols-2 gap-3 mb-4">
                    <div className="bg-gray-700 rounded p-2">
                      <div className="text-xs text-gray-400">ROI</div>
                      <div className="text-sm font-bold text-green-500">{bot.performance.roi}</div>
                    </div>
                    <div className="bg-gray-700 rounded p-2">
                      <div className="text-xs text-gray-400">Win Rate</div>
                      <div className="text-sm font-bold text-white">{bot.performance.winRate}</div>
                    </div>
                    <div className="bg-gray-700 rounded p-2">
                      <div className="text-xs text-gray-400">Max DD</div>
                      <div className="text-sm font-bold text-red-500">{bot.performance.maxDrawdown}</div>
                    </div>
                    <div className="bg-gray-700 rounded p-2">
                      <div className="text-xs text-gray-400">Avg Trade</div>
                      <div className="text-sm font-bold text-white">{bot.performance.avgTrade}</div>
                    </div>
                  </div>

                  {/* Users Count */}
                  <div className="text-xs text-gray-400 mb-4">
                    {bot.users.toLocaleString()} users • Supports: {bot.supported.join(', ')}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleSubscribeBot(bot.id)}
                      className="flex-1 bg-yellow-500 hover:bg-yellow-600 text-black py-2 rounded font-medium transition-colors"
                    >
                      Subscribe
                    </button>
                    <button
                      onClick={() => setSelectedBot(bot)}
                      className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors"
                    >
                      Details
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'My Bots' && (
          <div className="space-y-6">
            {myBots.map((bot) => (
              <div key={bot.id} className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-lg flex items-center justify-center">
                      <Bot className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white">{bot.name}</h3>
                      <div className="text-sm text-gray-400">{bot.type} • {bot.pair}</div>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-xs ${
                      bot.status === 'Running' 
                        ? 'bg-green-900 text-green-300' 
                        : 'bg-yellow-900 text-yellow-300'
                    }`}>
                      {bot.status}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className={`text-lg font-bold ${bot.pnl > 0 ? 'text-green-500' : 'text-red-500'}`}>
                        ${bot.pnl.toFixed(2)}
                      </div>
                      <div className={`text-sm ${bot.pnlPercent > 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {bot.pnlPercent > 0 ? '+' : ''}{bot.pnlPercent.toFixed(2)}%
                      </div>
                    </div>
                    
                    <div className="flex space-x-2">
                      {bot.status === 'Running' ? (
                        <button 
                          onClick={() => handleStopBot(bot.id)}
                          className="p-2 bg-red-600 hover:bg-red-700 rounded text-white"
                        >
                          <Pause className="w-4 h-4" />
                        </button>
                      ) : (
                        <button 
                          onClick={() => handleStartBot(bot.id)}
                          className="p-2 bg-green-600 hover:bg-green-700 rounded text-white"
                        >
                          <Play className="w-4 h-4" />
                        </button>
                      )}
                      <button className="p-2 bg-gray-700 hover:bg-gray-600 rounded text-white">
                        <Settings className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div>
                    <div className="text-xs text-gray-400">Investment</div>
                    <div className="text-white font-medium">${bot.investment}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Current Value</div>
                    <div className="text-white font-medium">${bot.currentValue.toFixed(2)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Total Trades</div>
                    <div className="text-white font-medium">{bot.trades}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Start Date</div>
                    <div className="text-white font-medium">{bot.startDate}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Last Trade</div>
                    <div className="text-white font-medium">{bot.lastTrade}</div>
                  </div>
                </div>
              </div>
            ))}

            {myBots.length === 0 && (
              <div className="text-center py-12">
                <Bot className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">No Active Bots</h3>
                <p className="text-gray-400 mb-4">Subscribe to trading bots from the marketplace to get started</p>
                <button 
                  onClick={() => setActiveTab('Marketplace')}
                  className="bg-yellow-500 hover:bg-yellow-600 text-black px-6 py-2 rounded font-medium transition-colors"
                >
                  Browse Marketplace
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'Create Bot' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h3 className="font-semibold text-white mb-6">Create Custom Trading Bot</h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Bot Configuration */}
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">Bot Name</label>
                    <input
                      type="text"
                      placeholder="My Custom Bot"
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                    />
                  </div>
                  
                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">Strategy Type</label>
                    <select className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white">
                      <option>DCA (Dollar Cost Averaging)</option>
                      <option>Grid Trading</option>
                      <option>Momentum Trading</option>
                      <option>Mean Reversion</option>
                      <option>Custom Strategy</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">Trading Pair</label>
                    <select className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white">
                      <option>BTC/USDT</option>
                      <option>ETH/USDT</option>
                      <option>BNB/USDT</option>
                      <option>SOL/USDT</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">Investment Amount (USDT)</label>
                    <input
                      type="number"
                      placeholder="1000"
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                    />
                  </div>
                </div>

                {/* Strategy Parameters */}
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">Risk Level</label>
                    <select className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white">
                      <option>Conservative</option>
                      <option>Moderate</option>
                      <option>Aggressive</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">Take Profit (%)</label>
                    <input
                      type="number"
                      placeholder="5"
                      step="0.1"
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                    />
                  </div>
                  
                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">Stop Loss (%)</label>
                    <input
                      type="number"
                      placeholder="3"
                      step="0.1"
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                    />
                  </div>
                  
                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">Max Trades per Day</label>
                    <input
                      type="number"
                      placeholder="10"
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                    />
                  </div>
                </div>
              </div>

              {/* Advanced Settings */}
              <div className="mt-6 pt-6 border-t border-gray-700">
                <h4 className="font-medium text-white mb-4">Advanced Settings</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Enable Trailing Stop</span>
                    <input type="checkbox" className="rounded" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Auto Compound Profits</span>
                    <input type="checkbox" className="rounded" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Market Hours Only</span>
                    <input type="checkbox" className="rounded" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Send Notifications</span>
                    <input type="checkbox" className="rounded" />
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-4 mt-6">
                <button className="flex-1 bg-yellow-500 hover:bg-yellow-600 text-black py-3 rounded font-medium transition-colors">
                  Create Bot
                </button>
                <button className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-3 rounded font-medium transition-colors">
                  Save as Template
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'Performance' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Performance Overview */}
            <div className="lg:col-span-2 bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h3 className="font-semibold text-white mb-4">Performance Overview</h3>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-500">+$135.20</div>
                  <div className="text-xs text-gray-400">Total Profit</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">+9.01%</div>
                  <div className="text-xs text-gray-400">Total ROI</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">180</div>
                  <div className="text-xs text-gray-400">Total Trades</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-500">78.3%</div>
                  <div className="text-xs text-gray-400">Win Rate</div>
                </div>
              </div>
              
              {/* Performance Chart Placeholder */}
              <div className="h-64 bg-gray-700 rounded flex items-center justify-center">
                <div className="text-center">
                  <BarChart3 className="w-12 h-12 text-gray-500 mx-auto mb-2" />
                  <div className="text-gray-400">Performance Chart</div>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="space-y-4">
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                <h4 className="font-medium text-white mb-3">Best Performing Bot</h4>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-lg flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <div className="text-white font-medium">DCA Master Pro</div>
                    <div className="text-green-500 text-sm">+15.67%</div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                <h4 className="font-medium text-white mb-3">Risk Level</h4>
                <div className="flex items-center space-x-2">
                  <div className="flex-1 bg-gray-700 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '40%' }} />
                  </div>
                  <span className="text-sm text-gray-400">Low</span>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                <h4 className="font-medium text-white mb-3">Monthly Stats</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Profitable Days:</span>
                    <span className="text-green-500">23/30</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Avg Daily Return:</span>
                    <span className="text-white">+0.3%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Max Drawdown:</span>
                    <span className="text-red-500">-5.2%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BotTrading;