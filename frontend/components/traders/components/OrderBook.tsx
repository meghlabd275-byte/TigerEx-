import React from 'react';

interface OrderBookEntry {
  price: number;
  quantity: number;
  total: number;
}

interface OrderBookProps {
  symbol?: string;
  bids?: OrderBookEntry[];
  asks?: OrderBookEntry[];
}

export const OrderBook: React.FC<OrderBookProps> = ({
  symbol = 'BTCUSDT',
  bids = [],
  asks = [],
}) => {
  // Mock data if no data provided
  const mockBids: OrderBookEntry[] =
    bids.length > 0
      ? bids
      : [
          { price: 45000, quantity: 0.5, total: 22500 },
          { price: 44999, quantity: 1.2, total: 53998.8 },
          { price: 44998, quantity: 0.8, total: 35998.4 },
          { price: 44997, quantity: 2.1, total: 94493.7 },
          { price: 44996, quantity: 0.3, total: 13498.8 },
        ];

  const mockAsks: OrderBookEntry[] =
    asks.length > 0
      ? asks
      : [
          { price: 45001, quantity: 0.7, total: 31500.7 },
          { price: 45002, quantity: 1.1, total: 49502.2 },
          { price: 45003, quantity: 0.9, total: 40502.7 },
          { price: 45004, quantity: 1.5, total: 67506 },
          { price: 45005, quantity: 0.4, total: 18002 },
        ];

  return (
    <div className="bg-gray-900 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-semibold">Order Book</h3>
        <span className="text-gray-400 text-sm">{symbol}</span>
      </div>

      <div className="space-y-2">
        {/* Header */}
        <div className="grid grid-cols-3 gap-2 text-xs text-gray-400 font-medium">
          <div>Price (USDT)</div>
          <div className="text-right">Amount (BTC)</div>
          <div className="text-right">Total</div>
        </div>

        {/* Asks (Sell Orders) */}
        <div className="space-y-1">
          {mockAsks.reverse().map((ask, index) => (
            <div
              key={index}
              className="grid grid-cols-3 gap-2 text-xs hover:bg-gray-800 p-1 rounded"
            >
              <div className="text-red-400">{ask.price.toLocaleString()}</div>
              <div className="text-right text-white">
                {ask.quantity.toFixed(4)}
              </div>
              <div className="text-right text-gray-300">
                {ask.total.toLocaleString()}
              </div>
            </div>
          ))}
        </div>

        {/* Spread */}
        <div className="border-t border-gray-700 pt-2 pb-2">
          <div className="text-center text-xs text-gray-400">
            Spread:{' '}
            {((mockAsks[0]?.price || 0) - (mockBids[0]?.price || 0)).toFixed(2)}{' '}
            USDT
          </div>
        </div>

        {/* Bids (Buy Orders) */}
        <div className="space-y-1">
          {mockBids.map((bid, index) => (
            <div
              key={index}
              className="grid grid-cols-3 gap-2 text-xs hover:bg-gray-800 p-1 rounded"
            >
              <div className="text-green-400">{bid.price.toLocaleString()}</div>
              <div className="text-right text-white">
                {bid.quantity.toFixed(4)}
              </div>
              <div className="text-right text-gray-300">
                {bid.total.toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
