import React, { useState, useEffect } from 'react';
import { LineChart, Line, AreaChart, Area, CandlestickChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface MarketData {
  timestamp: string;
  price: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  close: number;
}

interface OrderBookItem {
  price: number;
  amount: number;
  total: number;
}

interface Trade {
  id: string;
  price: number;
  amount: number;
  time: string;
  type: 'buy' | 'sell';
}

interface Order {
  type: 'market' | 'limit' | 'stop-loss';
  side: 'buy' | 'sell';
  amount: string;
  price?: string;
  total?: string;
}

const AdvancedTradingPlatform: React.FC = () => {
  const [selectedPair, setSelectedPair] = useState('BTC/USDT');
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [orderBook, setOrderBook] = useState<{ bids: OrderBookItem[], asks: OrderBookItem[] }>({ bids: [], asks: [] });
  const [recentTrades, setRecentTrades] = useState<Trade[]>([]);
  const [order, setOrder] = useState<Order>({ type: 'market', side: 'buy', amount: '' });
  const [currentPrice, setCurrentPrice] = useState(45000);
  const [priceChange, setPriceChange] = useState(2.5);
  const [loading, setLoading] = useState(true);

  // Generate mock data
  useEffect(() => {
    const generateMockData = () => {
      // Generate market data
      const mockMarketData: MarketData[] = Array.from({ length: 50 }, (_, i) => {
        const basePrice = 45000;
        const variation = (Math.random() - 0.5) * 2000;
        const price = basePrice + variation;
        return {
          timestamp: new Date(Date.now() - (49 - i) * 5 * 60 * 1000).toISOString(),
          price: price,
          volume: Math.random() * 100 + 50,
          high: price + Math.random() * 100,
          low: price - Math.random() * 100,
          open: i === 0 ? price : mockMarketData[i - 1]?.close || price,
          close: price + (Math.random() - 0.5) * 50
        };
      });

      // Generate order book
      const mockBids: OrderBookItem[] = Array.from({ length: 15 }, (_, i) => ({
        price: currentPrice - (i + 1) * 10,
        amount: Math.random() * 2 + 0.1,
        total: 0
      })).map(item => ({ ...item, total: item.price * item.amount }));

      const mockAsks: OrderBookItem[] = Array.from({ length: 15 }, (_, i) => ({
        price: currentPrice + (i + 1) * 10,
        amount: Math.random() * 2 + 0.1,
        total: 0
      })).map(item => ({ ...item, total: item.price * item.amount }));

      // Generate recent trades
      const mockTrades: Trade[] = Array.from({ length: 20 }, (_, i) => ({
        id: `trade_${i + 1}`,
        price: currentPrice + (Math.random() - 0.5) * 100,
        amount: Math.random() * 1 + 0.1,
        time: new Date(Date.now() - i * 30 * 1000).toLocaleTimeString(),
        type: Math.random() > 0.5 ? 'buy' : 'sell'
      }));

      setMarketData(mockMarketData);
      setOrderBook({ bids: mockBids, asks: mockAsks });
      setRecentTrades(mockTrades);
      setLoading(false);
    };

    generateMockData();
    
    // Simulate real-time updates
    const interval = setInterval(() => {
      setCurrentPrice(prev => prev + (Math.random() - 0.5) * 100);
      setPriceChange(prev => prev + (Math.random() - 0.5) * 0.5);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const handleOrderSubmit = () => {
    console.log('Order submitted:', order);
    // Handle order submission logic
  };

  const calculateTotal = () => {
    if (order.type === 'market') return 'Market Price';
    if (order.price && order.amount) {
      return (parseFloat(order.price) * parseFloat(order.amount)).toFixed(2);
    }
    return '0.00';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-2xl">Loading Trading Platform...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-6">
            <h1 className="text-2xl font-bold text-blue-400">TigerEx</h1>
            <div className="flex gap-2">
              {['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT'].map(pair => (
                <button
                  key={pair}
                  onClick={() => setSelectedPair(pair)}
                  className={`px-4 py-2 rounded ${
                    selectedPair === pair ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
                  }`}
                >
                  {pair}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-2xl font-bold">${currentPrice.toFixed(2)}</div>
              <div className={`text-sm ${priceChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)}%
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-screen">
        {/* Main Trading Area */}
        <div className="flex-1 flex">
          {/* Chart Section */}
          <div className="flex-1 p-6">
            <div className="bg-gray-800 rounded-lg p-4 h-full">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-semibold">{selectedPair} Chart</h3>
                <div className="flex gap-2">
                  {['1m', '5m', '15m', '1h', '4h', '1d'].map(timeframe => (
                    <button
                      key={timeframe}
                      className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
                    >
                      {timeframe}
                    </button>
                  ))}
                </div>
              </div>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={marketData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="timestamp" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
                  <Area type="monotone" dataKey="price" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
              
              {/* Additional Chart Indicators */}
              <div className="mt-4 grid grid-cols-4 gap-4">
                <div className="bg-gray-700 rounded p-3">
                  <div className="text-sm text-gray-400">24h High</div>
                  <div className="text-lg font-semibold text-green-400">
                    ${(currentPrice + 500).toFixed(2)}
                  </div>
                </div>
                <div className="bg-gray-700 rounded p-3">
                  <div className="text-sm text-gray-400">24h Low</div>
                  <div className="text-lg font-semibold text-red-400">
                    ${(currentPrice - 500).toFixed(2)}
                  </div>
                </div>
                <div className="bg-gray-700 rounded p-3">
                  <div className="text-sm text-gray-400">24h Volume</div>
                  <div className="text-lg font-semibold text-blue-400">
                    ${(Math.random() * 100000000).toFixed(0)}
                  </div>
                </div>
                <div className="bg-gray-700 rounded p-3">
                  <div className="text-sm text-gray-400">24h Change</div>
                  <div className={`text-lg font-semibold ${priceChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {priceChange >= 0 ? '+' : ''}{(priceChange * 100).toFixed(2)}%
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Order Book */}
          <div className="w-80 p-6">
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">Order Book</h3>
              
              {/* Asks (Sell Orders) */}
              <div className="mb-4">
                <div className="text-sm text-gray-400 mb-2">Sell Orders</div>
                <div className="space-y-1">
                  {orderBook.asks.slice(0, 8).reverse().map((ask, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span className="text-red-400">{ask.price.toFixed(2)}</span>
                      <span className="text-gray-300">{ask.amount.toFixed(4)}</span>
                      <span className="text-gray-400">{ask.total.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Spread */}
              <div className="bg-gray-700 rounded p-2 mb-4 text-center">
                <div className="text-sm text-gray-400">Spread</div>
                <div className="text-lg font-semibold">
                  {(orderBook.asks[0]?.price - orderBook.bids[0]?.price).toFixed(2)}
                </div>
              </div>

              {/* Bids (Buy Orders) */}
              <div>
                <div className="text-sm text-gray-400 mb-2">Buy Orders</div>
                <div className="space-y-1">
                  {orderBook.bids.slice(0, 8).map((bid, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span className="text-green-400">{bid.price.toFixed(2)}</span>
                      <span className="text-gray-300">{bid.amount.toFixed(4)}</span>
                      <span className="text-gray-400">{bid.total.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Sidebar - Order Form & Recent Trades */}
        <div className="w-96 border-l border-gray-700">
          {/* Order Form */}
          <div className="p-6 border-b border-gray-700">
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">Place Order</h3>
              
              {/* Order Type Tabs */}
              <div className="flex mb-4">
                {['market', 'limit', 'stop-loss'].map(type => (
                  <button
                    key={type}
                    onClick={() => setOrder({ ...order, type: type as Order['type'] })}
                    className={`flex-1 py-2 text-sm capitalize ${
                      order.type === type ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
                    }`}
                  >
                    {type.replace('-', ' ')}
                  </button>
                ))}
              </div>

              {/* Buy/Sell Tabs */}
              <div className="flex mb-4">
                <button
                  onClick={() => setOrder({ ...order, side: 'buy' })}
                  className={`flex-1 py-2 ${
                    order.side === 'buy' ? 'bg-green-600' : 'bg-gray-700 hover:bg-gray-600'
                  }`}
                >
                  Buy
                </button>
                <button
                  onClick={() => setOrder({ ...order, side: 'sell' })}
                  className={`flex-1 py-2 ${
                    order.side === 'sell' ? 'bg-red-600' : 'bg-gray-700 hover:bg-gray-600'
                  }`}
                >
                  Sell
                </button>
              </div>

              {/* Price Input (for non-market orders) */}
              {order.type !== 'market' && (
                <div className="mb-4">
                  <label className="block text-sm text-gray-400 mb-2">Price</label>
                  <input
                    type="number"
                    value={order.price}
                    onChange={(e) => setOrder({ ...order, price: e.target.value })}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0.00"
                  />
                </div>
              )}

              {/* Amount Input */}
              <div className="mb-4">
                <label className="block text-sm text-gray-400 mb-2">Amount</label>
                <input
                  type="number"
                  value={order.amount}
                  onChange={(e) => setOrder({ ...order, amount: e.target.value })}
                  className="w-full bg-gray-700 text-white px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>

              {/* Total */}
              <div className="mb-4">
                <label className="block text-sm text-gray-400 mb-2">Total</label>
                <div className="w-full bg-gray-700 text-white px-4 py-2 rounded">
                  ${calculateTotal()}
                </div>
              </div>

              {/* Submit Button */}
              <button
                onClick={handleOrderSubmit}
                className={`w-full py-3 rounded font-semibold ${
                  order.side === 'buy' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'
                }`}
              >
                {order.side === 'buy' ? 'Buy' : 'Sell'} {selectedPair.split('/')[0]}
              </button>
            </div>
          </div>

          {/* Recent Trades */}
          <div className="p-6">
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">Recent Trades</h3>
              <div className="space-y-2">
                {recentTrades.map((trade) => (
                  <div key={trade.id} className="flex justify-between items-center py-2 border-b border-gray-700">
                    <div>
                      <div className={`text-sm font-medium ${
                        trade.type === 'buy' ? 'text-green-400' : 'text-red-400'
                      }`}>
                        ${trade.price.toFixed(2)}
                      </div>
                      <div className="text-xs text-gray-400">{trade.time}</div>
                    </div>
                    <div className="text-sm text-gray-300">
                      {trade.amount.toFixed(4)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedTradingPlatform;