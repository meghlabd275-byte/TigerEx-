import React, { useState } from 'react';
import { 
  Star, 
  TrendingUp, 
  TrendingDown, 
  Users, 
  DollarSign, 
  Calendar,
  Filter,
  Search,
  Copy,
  Eye,
  BarChart3
} from 'lucide-react';

const CopyTradingInterface: React.FC = () => {
  const [activeTab, setActiveTab] = useState('Top Traders');
  const [filterBy, setFilterBy] = useState('All');

  const tabs = ['Top Traders', 'My Copies', 'Portfolio'];
  const filters = ['All', 'Spot', 'Futures', 'Options'];

  const topTraders = [
    {
      id: 1,
      name: 'CryptoMaster2024',
      avatar: '👑',
      roi: '+245.67%',
      followers: 12450,
      winRate: '87.5%',
      totalReturn: '$2,456,789',
      maxDrawdown: '-12.3%',
      tradingDays: 365,
      copiers: 1250,
      minCopyAmount: '$100',
      isVerified: true,
      tags: ['Spot', 'Futures'],
      performance: [
        { month: 'Jan', return: 15.2 },
        { month: 'Feb', return: 22.8 },
        { month: 'Mar', return: -5.1 },
        { month: 'Apr', return: 31.4 },
        { month: 'May', return: 18.7 },
        { month: 'Jun', return: 42.1 }
      ]
    },
    {
      id: 2,
      name: 'FuturesKing',
      avatar: '⚡',
      roi: '+189.34%',
      followers: 8920,
      winRate: '82.1%',
      totalReturn: '$1,893,456',
      maxDrawdown: '-18.7%',
      tradingDays: 298,
      copiers: 890,
      minCopyAmount: '$250',
      isVerified: true,
      tags: ['Futures', 'Options'],
      performance: [
        { month: 'Jan', return: 12.5 },
        { month: 'Feb', return: 28.3 },
        { month: 'Mar', return: -8.2 },
        { month: 'Apr', return: 35.7 },
        { month: 'May', return: 15.9 },
        { month: 'Jun', return: 38.4 }
      ]
    },
    {
      id: 3,
      name: 'SpotTrader Pro',
      avatar: '🎯',
      roi: '+156.78%',
      followers: 6750,
      winRate: '79.3%',
      totalReturn: '$1,567,890',
      maxDrawdown: '-9.8%',
      tradingDays: 412,
      copiers: 675,
      minCopyAmount: '$50',
      isVerified: false,
      tags: ['Spot'],
      performance: [
        { month: 'Jan', return: 8.9 },
        { month: 'Feb', return: 19.2 },
        { month: 'Mar', return: -3.1 },
        { month: 'Apr', return: 24.6 },
        { month: 'May', return: 12.3 },
        { month: 'Jun', return: 29.8 }
      ]
    }
  ];

  const myCopies = [
    {
      trader: 'CryptoMaster2024',
      copyAmount: '$1,000',
      currentValue: '$1,245.67',
      pnl: '+$245.67',
      pnlPercent: '+24.57%',
      startDate: '2024-01-15',
      status: 'Active'
    },
    {
      trader: 'FuturesKing',
      copyAmount: '$500',
      currentValue: '$478.23',
      pnl: '-$21.77',
      pnlPercent: '-4.35%',
      startDate: '2024-02-20',
      status: 'Active'
    }
  ];

  return (
    <div className="bg-gray-900 text-white min-h-screen">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">Copy Trading</h1>
            <p className="text-gray-400">Follow and copy successful traders automatically</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search traders..."
                className="bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-white text-sm focus:outline-none focus:border-yellow-500"
              />
            </div>
            <button className="flex items-center space-x-2 bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg transition-colors">
              <Filter className="w-4 h-4" />
              <span>Filter</span>
            </button>
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
        {activeTab === 'Top Traders' && (
          <div>
            {/* Filters */}
            <div className="flex items-center space-x-4 mb-6">
              <span className="text-gray-400">Filter by:</span>
              {filters.map((filter) => (
                <button
                  key={filter}
                  onClick={() => setFilterBy(filter)}
                  className={`px-3 py-1 rounded text-sm ${
                    filterBy === filter
                      ? 'bg-yellow-500 text-black'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>

            {/* Traders Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {topTraders.map((trader) => (
                <div key={trader.id} className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                  {/* Trader Header */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center text-2xl">
                        {trader.avatar}
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="font-semibold text-white">{trader.name}</h3>
                          {trader.isVerified && (
                            <div className="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                              <span className="text-white text-xs">✓</span>
                            </div>
                          )}
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-400">
                          <Users className="w-3 h-3" />
                          <span>{trader.followers.toLocaleString()} followers</span>
                        </div>
                      </div>
                    </div>
                    <button className="p-2 text-gray-400 hover:text-yellow-500">
                      <Star className="w-5 h-5" />
                    </button>
                  </div>

                  {/* Performance Stats */}
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="bg-gray-700 rounded p-3">
                      <div className="text-xs text-gray-400 mb-1">Total ROI</div>
                      <div className="text-lg font-bold text-green-500">{trader.roi}</div>
                    </div>
                    <div className="bg-gray-700 rounded p-3">
                      <div className="text-xs text-gray-400 mb-1">Win Rate</div>
                      <div className="text-lg font-bold text-white">{trader.winRate}</div>
                    </div>
                    <div className="bg-gray-700 rounded p-3">
                      <div className="text-xs text-gray-400 mb-1">Max Drawdown</div>
                      <div className="text-lg font-bold text-red-500">{trader.maxDrawdown}</div>
                    </div>
                    <div className="bg-gray-700 rounded p-3">
                      <div className="text-xs text-gray-400 mb-1">Copiers</div>
                      <div className="text-lg font-bold text-white">{trader.copiers}</div>
                    </div>
                  </div>

                  {/* Trading Tags */}
                  <div className="flex items-center space-x-2 mb-4">
                    {trader.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-gray-600 text-xs rounded text-gray-300"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  {/* Performance Chart */}
                  <div className="mb-4">
                    <div className="text-xs text-gray-400 mb-2">6M Performance</div>
                    <div className="flex items-end space-x-1 h-16">
                      {trader.performance.map((month, index) => (
                        <div
                          key={index}
                          className="flex-1 bg-gray-700 rounded-t"
                          style={{
                            height: `${Math.abs(month.return) * 2}px`,
                            backgroundColor: month.return > 0 ? '#10B981' : '#EF4444'
                          }}
                        />
                      ))}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-2">
                    <button className="flex-1 bg-yellow-500 hover:bg-yellow-600 text-black py-2 rounded font-medium transition-colors">
                      Copy Trade
                    </button>
                    <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors">
                      <Eye className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Min Copy Amount */}
                  <div className="text-xs text-gray-400 text-center mt-2">
                    Min. copy amount: {trader.minCopyAmount}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'My Copies' && (
          <div>
            <div className="bg-gray-800 rounded-lg border border-gray-700">
              <div className="p-4 border-b border-gray-700">
                <h3 className="font-semibold text-white">Active Copy Trades</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-750">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Trader</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Copy Amount</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Current Value</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">PnL</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Start Date</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Status</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {myCopies.map((copy, index) => (
                      <tr key={index} className="hover:bg-gray-750">
                        <td className="px-4 py-4 text-white font-medium">{copy.trader}</td>
                        <td className="px-4 py-4 text-white">{copy.copyAmount}</td>
                        <td className="px-4 py-4 text-white">{copy.currentValue}</td>
                        <td className="px-4 py-4">
                          <div className={copy.pnl.startsWith('+') ? 'text-green-500' : 'text-red-500'}>
                            {copy.pnl}
                          </div>
                          <div className={`text-xs ${copy.pnlPercent.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>
                            {copy.pnlPercent}
                          </div>
                        </td>
                        <td className="px-4 py-4 text-gray-400">{copy.startDate}</td>
                        <td className="px-4 py-4">
                          <span className="px-2 py-1 bg-green-900 text-green-300 text-xs rounded">
                            {copy.status}
                          </span>
                        </td>
                        <td className="px-4 py-4">
                          <div className="flex space-x-2">
                            <button className="text-yellow-500 hover:text-yellow-400 text-xs">
                              Modify
                            </button>
                            <button className="text-red-500 hover:text-red-400 text-xs">
                              Stop
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'Portfolio' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Portfolio Summary */}
            <div className="lg:col-span-2 bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h3 className="font-semibold text-white mb-4">Portfolio Performance</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-500">+$224.90</div>
                  <div className="text-xs text-gray-400">Total PnL</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">+14.99%</div>
                  <div className="text-xs text-gray-400">Total ROI</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">2</div>
                  <div className="text-xs text-gray-400">Active Copies</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">$1,500</div>
                  <div className="text-xs text-gray-400">Total Invested</div>
                </div>
              </div>
              
              {/* Performance Chart Placeholder */}
              <div className="h-64 bg-gray-700 rounded flex items-center justify-center">
                <div className="text-center">
                  <BarChart3 className="w-12 h-12 text-gray-500 mx-auto mb-2" />
                  <div className="text-gray-400">Portfolio Performance Chart</div>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="space-y-4">
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                <h4 className="font-medium text-white mb-3">Best Performer</h4>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center">
                    👑
                  </div>
                  <div>
                    <div className="text-white font-medium">CryptoMaster2024</div>
                    <div className="text-green-500 text-sm">+24.57%</div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                <h4 className="font-medium text-white mb-3">Risk Level</h4>
                <div className="flex items-center space-x-2">
                  <div className="flex-1 bg-gray-700 rounded-full h-2">
                    <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '60%' }} />
                  </div>
                  <span className="text-sm text-gray-400">Medium</span>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                <h4 className="font-medium text-white mb-3">Available Balance</h4>
                <div className="text-xl font-bold text-white">$2,450.00</div>
                <div className="text-xs text-gray-400">USDT</div>
                <button className="w-full mt-3 bg-yellow-500 hover:bg-yellow-600 text-black py-2 rounded font-medium transition-colors">
                  Add Funds
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CopyTradingInterface;