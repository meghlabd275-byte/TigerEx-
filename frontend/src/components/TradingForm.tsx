import React, { useState } from 'react';

const TradingForm = () => {
  const [orderType, setOrderType] = useState('limit');
  const [side, setSide] = useState('buy');
  const [price, setPrice] = useState('');
  const [amount, setAmount] = useState('');
  const [total, setTotal] = useState('');

  const handlePriceChange = (e) => {
    setPrice(e.target.value);
    setTotal(parseFloat(e.target.value) * parseFloat(amount) || '');
  };

  const handleAmountChange = (e) => {
    setAmount(e.target.value);
    setTotal(parseFloat(price) * parseFloat(e.target.value) || '');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle order submission logic here
    console.log({
      orderType,
      side,
      price,
      amount,
      total,
    });
  };

  return (
    <div className="bg-gray-800 text-white p-4 rounded-lg">
      <h2 className="text-xl font-bold mb-4">Trade</h2>
      <div className="flex mb-4">
        <button
          className={`px-4 py-2 rounded-l-lg ${side === 'buy' ? 'bg-green-500' : 'bg-gray-700'}`}
          onClick={() => setSide('buy')}
        >
          Buy
        </button>
        <button
          className={`px-4 py-2 rounded-r-lg ${side === 'sell' ? 'bg-red-500' : 'bg-gray-700'}`}
          onClick={() => setSide('sell')}
        >
          Sell
        </button>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="orderType" className="block mb-2">Order Type</label>
          <select
            id="orderType"
            className="w-full p-2 bg-gray-700 rounded"
            value={orderType}
            onChange={(e) => setOrderType(e.target.value)}
          >
            <option value="limit">Limit</option>
            <option value="market">Market</option>
            <option value="stop-loss">Stop-Loss</option>
            <option value="take-profit">Take-Profit</option>
          </select>
        </div>
        <div className="mb-4">
          <label htmlFor="price" className="block mb-2">Price</label>
          <input
            type="text"
            id="price"
            className="w-full p-2 bg-gray-700 rounded"
            value={price}
            onChange={handlePriceChange}
            disabled={orderType === 'market'}
          />
        </div>
        <div className="mb-4">
          <label htmlFor="amount" className="block mb-2">Amount</label>
          <input
            type="text"
            id="amount"
            className="w-full p-2 bg-gray-700 rounded"
            value={amount}
            onChange={handleAmountChange}
          />
        </div>
        <div className="mb-4">
          <label htmlFor="total" className="block mb-2">Total</label>
          <input
            type="text"
            id="total"
            className="w-full p-2 bg-gray-700 rounded"
            value={total}
            readOnly
          />
        </div>
        <div className="flex justify-between mb-4">
          <button type="button" className="w-1/4 py-1 bg-gray-700 rounded">25%</button>
          <button type="button" className="w-1/4 py-1 bg-gray-700 rounded">50%</button>
          <button type="button" className="w-1/4 py-1 bg-gray-700 rounded">75%</button>
          <button type="button" className="w-1/4 py-1 bg-gray-700 rounded">100%</button>
        </div>
        <button
          type="submit"
          className={`w-full py-2 rounded ${side === 'buy' ? 'bg-green-500' : 'bg-red-500'}`}
        >
          {side === 'buy' ? 'Buy' : 'Sell'}
        </button>
      </form>
    </div>
  );
};

export default TradingForm;
