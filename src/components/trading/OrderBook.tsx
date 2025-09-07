import React from 'react';

interface OrderBookProps {
  pair: string;
}

const OrderBook: React.FC<OrderBookProps> = ({ pair }) => {
  // Mock order book data
  const asks = [
    { price: 43260.5, amount: 0.125, total: 5407.56 },
    { price: 43255.25, amount: 0.25, total: 10813.81 },
    { price: 43252.0, amount: 0.5, total: 21626.0 },
    { price: 43250.75, amount: 0.75, total: 32438.06 },
    { price: 43248.5, amount: 1.0, total: 43248.5 },
  ];

  const bids = [
    { price: 43245.25, amount: 0.875, total: 37839.59 },
    { price: 43242.0, amount: 0.625, total: 27026.25 },
    { price: 43240.5, amount: 0.375, total: 16215.19 },
    { price: 43238.75, amount: 0.25, total: 10809.69 },
    { price: 43235.0, amount: 0.125, total: 5404.38 },
  ];

  return (
    <div className="h-full p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-medium">Order Book</h3>
        <div className="text-xs text-gray-400">{pair}</div>
      </div>

      <div className="space-y-2">
        {/* Header */}
        <div className="grid grid-cols-3 text-xs text-gray-400 pb-2 border-b border-gray-700">
          <div>Price (USDT)</div>
          <div className="text-right">Amount (BTC)</div>
          <div className="text-right">Total</div>
        </div>

        {/* Asks (Sell Orders) */}
        <div className="space-y-1">
          {asks.reverse().map((ask, index) => (
            <div
              key={index}
              className="grid grid-cols-3 text-xs hover:bg-gray-700/50 p-1 rounded"
            >
              <div className="text-red-400">{ask.price.toFixed(2)}</div>
              <div className="text-right text-white">
                {ask.amount.toFixed(3)}
              </div>
              <div className="text-right text-gray-300">
                {ask.total.toFixed(2)}
              </div>
            </div>
          ))}
        </div>

        {/* Spread */}
        <div className="py-2 text-center">
          <div className="text-xs text-gray-400">Spread</div>
          <div className="text-sm text-white">5.25 (0.01%)</div>
        </div>

        {/* Bids (Buy Orders) */}
        <div className="space-y-1">
          {bids.map((bid, index) => (
            <div
              key={index}
              className="grid grid-cols-3 text-xs hover:bg-gray-700/50 p-1 rounded"
            >
              <div className="text-green-400">{bid.price.toFixed(2)}</div>
              <div className="text-right text-white">
                {bid.amount.toFixed(3)}
              </div>
              <div className="text-right text-gray-300">
                {bid.total.toFixed(2)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default OrderBook;
