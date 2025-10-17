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
  Grid3X3, 
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
  Info
} from 'lucide-react';

const GridTrading: React.FC = () => {
  const [selectedPair, setSelectedPair] = useState('BTC/USDT');
  const [gridType, setGridType] = useState<'Arithmetic' | 'Geometric'>('Arithmetic');
  const [investment, setInvestment] = useState('1000');
  const [gridNumber, setGridNumber] = useState('10');
  const [priceRange, setPriceRange] = useState({ lower: '120000', upper: '130000' });
  const [activeTab, setActiveTab] = useState('Create');

  const tradingPairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT'];
  const tabs = ['Create', 'Running', 'History'];

  const currentPrice = 122887.76;
  const priceChange = '+2.29%';
  const isPositive = true;

  // Mock running grids data
  const runningGrids = [
    {
      id: 1,
      pair: 'BTC/USDT',
      type: 'Arithmetic',
      investment: 1000,
      currentValue: 1045.67,
      pnl: 45.67,
      pnlPercent: 4.57,
      grids: 10,
      filled: 6,
      priceRange: { lower: 120000, upper: 130000 },
      startTime: '2024-10-01 10:30:00',
      status: 'Running',
      totalTrades: 24,
      avgProfit: 1.89
    },
    {
      id: 2,
      pair: 'ETH/USDT',
      type: 'Geometric',
      investment: 500,
      currentValue: 478.23,
      pnl: -21.77,
      pnlPercent: -4.35,
      grids: 15,
      filled: 8,
      priceRange: { lower: 2400, upper: 2800 },
      startTime: '2024-09-28 14:15:00',
      status: 'Running',
      totalTrades: 18,
      avgProfit: -1.21
    }
  ];

  // Mock grid history
  const gridHistory = [
    {
      id: 3,
      pair: 'BNB/USDT',
      type: 'Arithmetic',
      investment: 750,
      finalValue: 823.45,
      pnl: 73.45,
      pnlPercent: 9.79,
      duration: '7 days',
      totalTrades: 45,
      avgProfit: 1.63,
      endTime: '2024-09-25 16:20:00',
      status: 'Completed'
    }
  ];

  const calculateGridSpacing = () => {
    const lower = parseFloat(priceRange.lower);
    const upper = parseFloat(priceRange.upper);
    const grids = parseInt(gridNumber);
    
    if (gridType === 'Arithmetic') {
      return (upper - lower) / grids;
    } else {
      return Math.pow(upper / lower, 1 / grids) - 1;
    }
  };

  const calculateInvestmentPerGrid = () => {
    const totalInvestment = parseFloat(investment);
    const grids = parseInt(gridNumber);
    return totalInvestment / grids;
  };

  const handleCreateGrid = () => {
    console.log('Creating grid:', {
      pair: selectedPair,
      type: gridType,
      investment,
      gridNumber,
      priceRange
    });
    alert(`Grid trading bot created for ${selectedPair} with ${gridNumber} grids`);
  };

  const handleStopGrid = (gridId: number) => {
    console.log('Stopping grid:', gridId);
    alert(`Grid ${gridId} stopped successfully`);
  };

  return (
    <div className="bg-gray-900 text-white min-h-screen">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Grid3X3 className="w-8 h-8 text-yellow-500" />
            <div>
              <h1 className="text-2xl font-bold text-white">Grid Trading</h1>
              <p className="text-gray-400">Automated profit from market volatility</p>
            </div>
          </div>
          <div className="flex items-center space-x-6">
            <div className="text-right">
              <div className="text-sm text-gray-400">{selectedPair}</div>
              <div className={`text-xl font-bold ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
                ${currentPrice.toLocaleString()}
              </div>
              <div className={`text-sm ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
                {priceChange}
              </div>
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
        {activeTab === 'Create' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Grid Configuration */}
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <h3 className="font-semibold text-white mb-4">Grid Configuration</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Trading Pair */}
                  <div className="space-y-2">
                    <label className="text-sm text-gray-400">Trading Pair</label>
                    <select
                      value={selectedPair}
                      onChange={(e) => setSelectedPair(e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                    >
                      {tradingPairs.map(pair => (
                        <option key={pair} value={pair}>{pair}</option>
                      ))}
                    </select>
                  </div>

                  {/* Grid Type */}
                  <div className="space-y-2">
                    <label className="text-sm text-gray-400">Grid Type</label>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setGridType('Arithmetic')}
                        className={`flex-1 py-2 px-3 rounded text-sm ${
                          gridType === 'Arithmetic'
                            ? 'bg-yellow-500 text-black'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                      >
                        Arithmetic
                      </button>
                      <button
                        onClick={() => setGridType('Geometric')}
                        className={`flex-1 py-2 px-3 rounded text-sm ${
                          gridType === 'Geometric'
                            ? 'bg-yellow-500 text-black'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                      >
                        Geometric
                      </button>
                    </div>
                  </div>

                  {/* Investment Amount */}
                  <div className="space-y-2">
                    <label className="text-sm text-gray-400">Investment Amount (USDT)</label>
                    <input
                      type="number"
                      value={investment}
                      onChange={(e) => setInvestment(e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                      placeholder="1000"
                    />
                  </div>

                  {/* Number of Grids */}
                  <div className="space-y-2">
                    <label className="text-sm text-gray-400">Number of Grids</label>
                    <input
                      type="number"
                      value={gridNumber}
                      onChange={(e) => setGridNumber(e.target.value)}
                      min="2"
                      max="200"
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                      placeholder="10"
                    />
                  </div>

                  {/* Price Range */}
                  <div className="space-y-2">
                    <label className="text-sm text-gray-400">Lower Price</label>
                    <input
                      type="number"
                      value={priceRange.lower}
                      onChange={(e) => setPriceRange({...priceRange, lower: e.target.value})}
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                      placeholder="120000"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm text-gray-400">Upper Price</label>
                    <input
                      type="number"
                      value={priceRange.upper}
                      onChange={(e) => setPriceRange({...priceRange, upper: e.target.value})}
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                      placeholder="130000"
                    />
                  </div>
                </div>

                {/* Grid Visualization */}
                <div className="mt-6">
                  <h4 className="text-sm text-gray-400 mb-3">Grid Preview</h4>
                  <div className="bg-gray-700 rounded p-4 h-64 relative overflow-hidden">
                    <div className="absolute inset-0 flex flex-col justify-between">
                      {Array.from({ length: parseInt(gridNumber) + 1 }, (_, i) => {
                        const lower = parseFloat(priceRange.lower);
                        const upper = parseFloat(priceRange.upper);
                        const price = gridType === 'Arithmetic' 
                          ? lower + (upper - lower) * (i / parseInt(gridNumber))
                          : lower * Math.pow(upper / lower, i / parseInt(gridNumber));
                        
                        return (
                          <div key={i} className="flex items-center justify-between border-b border-gray-600 py-1">
                            <div className="text-xs text-gray-400">Grid {parseInt(gridNumber) - i}</div>
                            <div className="text-xs text-white">${price.toFixed(2)}</div>
                            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                          </div>
                        );
                      })}
                    </div>
                    
                    {/* Current Price Indicator */}
                    <div 
                      className="absolute left-0 right-0 border-t-2 border-red-500 flex items-center"
                      style={{ 
                        top: `${((parseFloat(priceRange.upper) - currentPrice) / (parseFloat(priceRange.upper) - parseFloat(priceRange.lower))) * 100}%` 
                      }}
                    >
                      <div className="bg-red-500 text-white text-xs px-2 py-1 rounded ml-2">
                        Current: ${currentPrice.toLocaleString()}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Advanced Settings */}
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <h3 className="font-semibold text-white mb-4">Advanced Settings</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Stop Loss</span>
                    <input type="checkbox" className="rounded" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Take Profit</span>
                    <input type="checkbox" className="rounded" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Trailing Stop</span>
                    <input type="checkbox" className="rounded" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Auto Restart</span>
                    <input type="checkbox" className="rounded" />
                  </div>
                </div>
              </div>
            </div>

            {/* Grid Summary */}
            <div className="space-y-6">
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <h3 className="font-semibold text-white mb-4">Grid Summary</h3>
                
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Grid Spacing:</span>
                    <span className="text-white">
                      {gridType === 'Arithmetic' 
                        ? `$${calculateGridSpacing().toFixed(2)}`
                        : `${(calculateGridSpacing() * 100).toFixed(2)}%`
                      }
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-400">Investment per Grid:</span>
                    <span className="text-white">${calculateInvestmentPerGrid().toFixed(2)}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Investment:</span>
                    <span className="text-white">${investment}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-400">Estimated APR:</span>
                    <span className="text-green-500">15-30%</span>
                  </div>
                </div>

                <button
                  onClick={handleCreateGrid}
                  className="w-full mt-6 bg-yellow-500 hover:bg-yellow-600 text-black py-3 rounded font-medium transition-colors"
                >
                  Create Grid
                </button>
              </div>

              {/* Risk Warning */}
              <div className="bg-yellow-900 border border-yellow-700 rounded-lg p-4">
                <div className="flex items-start space-x-2">
                  <Info className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="text-yellow-200 font-medium mb-2">Risk Warning</h4>
                    <div className="text-xs text-yellow-200 space-y-1">
                      <p>• Grid trading works best in sideways markets</p>
                      <p>• Strong trends may cause losses</p>
                      <p>• Set appropriate price ranges</p>
                      <p>• Monitor your positions regularly</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Performance Stats */}
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <h3 className="font-semibold text-white mb-4">Platform Stats</h3>
                
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Active Grids:</span>
                    <span className="text-white">1,234</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Volume:</span>
                    <span className="text-white">$12.5M</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Avg. APR:</span>
                    <span className="text-green-500">22.5%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Success Rate:</span>
                    <span className="text-green-500">87.3%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'Running' && (
          <div className="space-y-6">
            {runningGrids.map((grid) => (
              <div key={grid.id} className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-yellow-500 rounded-lg flex items-center justify-center">
                      <Grid3X3 className="w-6 h-6 text-black" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white">{grid.pair}</h3>
                      <div className="text-sm text-gray-400">{grid.type} Grid • {grid.grids} Grids</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className={`text-lg font-bold ${grid.pnl > 0 ? 'text-green-500' : 'text-red-500'}`}>
                        ${grid.pnl.toFixed(2)}
                      </div>
                      <div className={`text-sm ${grid.pnlPercent > 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {grid.pnlPercent > 0 ? '+' : ''}{grid.pnlPercent.toFixed(2)}%
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button className="p-2 bg-gray-700 hover:bg-gray-600 rounded text-yellow-500">
                        <Settings className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => handleStopGrid(grid.id)}
                        className="p-2 bg-red-600 hover:bg-red-700 rounded text-white"
                      >
                        <Stop className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                  <div>
                    <div className="text-xs text-gray-400">Investment</div>
                    <div className="text-white font-medium">${grid.investment}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Current Value</div>
                    <div className="text-white font-medium">${grid.currentValue.toFixed(2)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Filled Grids</div>
                    <div className="text-white font-medium">{grid.filled}/{grid.grids}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Total Trades</div>
                    <div className="text-white font-medium">{grid.totalTrades}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Avg Profit</div>
                    <div className={`font-medium ${grid.avgProfit > 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {grid.avgProfit > 0 ? '+' : ''}{grid.avgProfit.toFixed(2)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Running Time</div>
                    <div className="text-white font-medium">3d 14h</div>
                  </div>
                </div>

                {/* Grid Progress Bar */}
                <div className="mt-4">
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>Price Range</span>
                    <span>${grid.priceRange.lower.toLocaleString()} - ${grid.priceRange.upper.toLocaleString()}</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-yellow-500 h-2 rounded-full" 
                      style={{ width: `${(grid.filled / grid.grids) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'History' && (
          <div className="bg-gray-800 rounded-lg border border-gray-700">
            <div className="p-4 border-b border-gray-700">
              <h3 className="font-semibold text-white">Grid History</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-750">
                  <tr className="text-xs text-gray-400">
                    <th className="px-4 py-3 text-left">Pair</th>
                    <th className="px-4 py-3 text-left">Type</th>
                    <th className="px-4 py-3 text-left">Investment</th>
                    <th className="px-4 py-3 text-left">Final Value</th>
                    <th className="px-4 py-3 text-left">PnL</th>
                    <th className="px-4 py-3 text-left">Duration</th>
                    <th className="px-4 py-3 text-left">Total Trades</th>
                    <th className="px-4 py-3 text-left">Avg Profit</th>
                    <th className="px-4 py-3 text-left">End Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {gridHistory.map((grid) => (
                    <tr key={grid.id} className="hover:bg-gray-750">
                      <td className="px-4 py-4 text-white font-medium">{grid.pair}</td>
                      <td className="px-4 py-4 text-gray-400">{grid.type}</td>
                      <td className="px-4 py-4 text-white">${grid.investment}</td>
                      <td className="px-4 py-4 text-white">${grid.finalValue.toFixed(2)}</td>
                      <td className="px-4 py-4">
                        <div className={grid.pnl > 0 ? 'text-green-500' : 'text-red-500'}>
                          ${grid.pnl.toFixed(2)}
                        </div>
                        <div className={`text-xs ${grid.pnlPercent > 0 ? 'text-green-500' : 'text-red-500'}`}>
                          ({grid.pnlPercent > 0 ? '+' : ''}{grid.pnlPercent.toFixed(2)}%)
                        </div>
                      </td>
                      <td className="px-4 py-4 text-gray-400">{grid.duration}</td>
                      <td className="px-4 py-4 text-white">{grid.totalTrades}</td>
                      <td className="px-4 py-4">
                        <span className={grid.avgProfit > 0 ? 'text-green-500' : 'text-red-500'}>
                          {grid.avgProfit > 0 ? '+' : ''}{grid.avgProfit.toFixed(2)}%
                        </span>
                      </td>
                      <td className="px-4 py-4 text-gray-400">{grid.endTime}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GridTrading;