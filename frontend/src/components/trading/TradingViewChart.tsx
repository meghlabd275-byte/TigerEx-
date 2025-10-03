import React, { useEffect, useRef, useState } from 'react';
import { Maximize2, Settings, TrendingUp } from 'lucide-react';

const TradingViewChart: React.FC = () => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const [timeframe, setTimeframe] = useState('1D');
  const [chartType, setChartType] = useState('candlestick');

  const timeframes = ['1s', '15m', '1H', '4H', '1D', '1W', '1M'];
  const chartTypes = ['Chart', 'Info', 'Trading Data', 'Square'];

  useEffect(() => {
    // In a real implementation, you would initialize TradingView widget here
    // For now, we'll create a placeholder
    if (chartContainerRef.current) {
      // TradingView widget initialization would go here
    }
  }, []);

  return (
    <div className="bg-gray-900 text-white h-full flex flex-col">
      {/* Chart Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800">
        <div className="flex items-center gap-4">
          {/* Timeframe Selector */}
          <div className="flex items-center gap-1">
            <span className="text-sm text-gray-400 mr-2">Time</span>
            {timeframes.map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  timeframe === tf
                    ? 'bg-gray-700 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>

          {/* Chart Type Tabs */}
          <div className="flex items-center gap-2 ml-4">
            {chartTypes.map((type) => (
              <button
                key={type}
                className="px-3 py-1 text-sm text-gray-400 hover:text-white hover:bg-gray-800 rounded"
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* Chart Controls */}
        <div className="flex items-center gap-2">
          <button className="p-2 hover:bg-gray-800 rounded">
            <span className="text-sm font-semibold">AI</span>
          </button>
          <button className="p-2 hover:bg-gray-800 rounded">
            <Settings className="w-4 h-4" />
          </button>
          <button className="p-2 hover:bg-gray-800 rounded">
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Chart Drawing Tools */}
      <div className="flex items-center gap-2 px-4 py-2 border-b border-gray-800 overflow-x-auto">
        <button className="p-2 hover:bg-gray-800 rounded" title="Cursor">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
          </svg>
        </button>
        <button className="p-2 hover:bg-gray-800 rounded" title="Trend Line">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        </button>
        <button className="p-2 hover:bg-gray-800 rounded" title="Horizontal Line">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
          </svg>
        </button>
        <button className="p-2 hover:bg-gray-800 rounded" title="Rectangle">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <rect x="3" y="3" width="18" height="18" strokeWidth={2} />
          </svg>
        </button>
        <button className="p-2 hover:bg-gray-800 rounded" title="Fibonacci">
          <span className="text-xs font-semibold">Fib</span>
        </button>
        <div className="w-px h-6 bg-gray-700 mx-2"></div>
        <button className="p-2 hover:bg-gray-800 rounded" title="Indicators">
          <TrendingUp className="w-4 h-4" />
        </button>
        <button className="p-2 hover:bg-gray-800 rounded" title="Compare">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </button>
      </div>

      {/* Chart Container */}
      <div ref={chartContainerRef} className="flex-1 relative bg-gray-950">
        {/* Placeholder Chart */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="w-64 h-48 mx-auto mb-4 opacity-10">
              <svg viewBox="0 0 300 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                {/* Candlestick Chart Placeholder */}
                <rect x="20" y="80" width="10" height="60" fill="#10b981" />
                <line x1="25" y1="60" x2="25" y2="140" stroke="#10b981" strokeWidth="2" />
                
                <rect x="50" y="100" width="10" height="40" fill="#ef4444" />
                <line x1="55" y1="80" x2="55" y2="140" stroke="#ef4444" strokeWidth="2" />
                
                <rect x="80" y="70" width="10" height="70" fill="#10b981" />
                <line x1="85" y1="50" x2="85" y2="140" stroke="#10b981" strokeWidth="2" />
                
                <rect x="110" y="90" width="10" height="50" fill="#10b981" />
                <line x1="115" y1="70" x2="115" y2="140" stroke="#10b981" strokeWidth="2" />
                
                <rect x="140" y="60" width="10" height="80" fill="#10b981" />
                <line x1="145" y1="40" x2="145" y2="140" stroke="#10b981" strokeWidth="2" />
                
                <rect x="170" y="80" width="10" height="60" fill="#ef4444" />
                <line x1="175" y1="60" x2="175" y2="140" stroke="#ef4444" strokeWidth="2" />
                
                <rect x="200" y="70" width="10" height="70" fill="#10b981" />
                <line x1="205" y1="50" x2="205" y2="140" stroke="#10b981" strokeWidth="2" />
                
                <rect x="230" y="50" width="10" height="90" fill="#10b981" />
                <line x1="235" y1="30" x2="235" y2="140" stroke="#10b981" strokeWidth="2" />
                
                <rect x="260" y="60" width="10" height="80" fill="#10b981" />
                <line x1="265" y1="40" x2="265" y2="140" stroke="#10b981" strokeWidth="2" />
              </svg>
            </div>
            <p className="text-gray-500 text-sm">TradingView Chart</p>
            <p className="text-gray-600 text-xs mt-1">Real-time price chart will be displayed here</p>
          </div>
        </div>

        {/* Price Scale (Right Side) */}
        <div className="absolute right-0 top-0 bottom-0 w-16 bg-gray-900 border-l border-gray-800 flex flex-col justify-between py-4 text-xs text-gray-400">
          <div className="px-2">121,000</div>
          <div className="px-2">120,800</div>
          <div className="px-2 text-green-400 font-semibold">120,442</div>
          <div className="px-2">120,200</div>
          <div className="px-2">120,000</div>
        </div>

        {/* Time Scale (Bottom) */}
        <div className="absolute bottom-0 left-0 right-16 h-8 bg-gray-900 border-t border-gray-800 flex justify-between items-center px-4 text-xs text-gray-400">
          <span>09:01</span>
          <span>12:00</span>
          <span>15:00</span>
          <span>18:00</span>
          <span>21:00</span>
        </div>
      </div>

      {/* Chart Footer with Volume */}
      <div className="px-4 py-2 border-t border-gray-800 flex items-center justify-between text-xs">
        <div className="flex items-center gap-4">
          <span className="text-gray-400">Vol(BTC)</span>
          <span className="text-white font-semibold">20.048K</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-gray-400">MA(7)</span>
          <span className="text-purple-400">108,922.27</span>
          <span className="text-gray-400">MA(25)</span>
          <span className="text-yellow-400">108,922.27</span>
          <span className="text-gray-400">MA(99)</span>
          <span className="text-blue-400">108,922.27</span>
        </div>
      </div>
    </div>
  );
};

export default TradingViewChart;