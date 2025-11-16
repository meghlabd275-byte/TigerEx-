import React, { useState, useEffect } from 'react';
import { Search, Edit } from 'lucide-react';
import { getTradingPairs } from '../../lib/api';

interface TradingPair {
  symbol: string;
  volume_24h: string;
  last_price: string;
  price_change_24h: string;
}

const MarketsScreen: React.FC = () => {
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTradingPairs = async () => {
      try {
        const data = await getTradingPairs();
        setTradingPairs(data.trading_pairs);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch trading pairs');
        setLoading(false);
      }
    };

    fetchTradingPairs();
  }, []);

  return (
    <div className="bg-gray-900 text-white min-h-screen font-sans">
      <div className="p-4">
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search Coin Pairs"
            className="bg-gray-800 border border-gray-700 rounded-lg w-full pl-10 pr-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
          />
        </div>

        <div className="flex space-x-4 mb-4 overflow-x-auto whitespace-nowrap">
          {['Favorites', 'Market', 'Alpha', 'Grow', 'Square', 'Data'].map((item, index) => (
            <button key={item} className={`py-2 text-sm font-semibold ${index === 0 ? 'text-yellow-500 border-b-2 border-yellow-500' : 'text-gray-400'}`}>
              {item}
            </button>
          ))}
        </div>

        <div className="flex justify-between items-center mb-4">
          <div className="flex space-x-4 overflow-x-auto whitespace-nowrap">
            {['All', 'Holdings', 'Spot', 'Alpha', 'Futures', 'Options'].map((item, index) => (
              <button key={item} className={`text-xs ${index === 0 ? 'text-white' : 'text-gray-500'}`}>{item}</button>
            ))}
          </div>
          <Edit className="w-4 h-4 text-gray-400" />
        </div>

        <div className="flex justify-between items-center text-xs text-gray-500 mb-2">
          <button className="flex items-center">Name / Vol ▼</button>
          <div className="flex items-center space-x-4">
             <button className="flex items-center">Last Price ▼</button>
             <button className="flex items-center">24h Chg% ▼</button>
          </div>
        </div>

        <div>
          {loading && <p>Loading...</p>}
          {error && <p className="text-red-500">{error}</p>}
          {!loading && !error && tradingPairs.map((pair, index) => {
            const priceChange = parseFloat(pair.price_change_24h);
            const changeColor = priceChange >= 0 ? 'green' : 'red';

            return (
              <div key={index} className="grid grid-cols-3 items-center py-3 border-b border-gray-800">
                <div className="col-span-1">
                  <div className="flex items-center">
                    <span className="font-bold text-sm">{pair.symbol}</span>
                  </div>
                  <div className="text-xs text-gray-500">{pair.volume_24h}</div>
                </div>

                <div className="col-span-1 text-right">
                  <div className="font-semibold text-sm">{pair.last_price}</div>
                </div>

                <div className="col-span-1 flex justify-end">
                  <button className={`w-24 py-2 text-sm font-semibold rounded-lg ${changeColor === 'red' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                    {`${priceChange.toFixed(2)}%`}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default MarketsScreen;
