import React from 'react';
import TradingForm from '../components/TradingForm';

const FuturesTrading: React.FC = () => {
  const currentSymbol = "BTCUSDT"; // This would typically come from state or props

  return (
    <div className="futures-trading-page">
      <h1 className="text-2xl font-bold mb-4">Futures Trading: {currentSymbol}</h1>
      <div className="trading-layout">
        <div className="trading-main">
          {/* Chart would go here */}
          <TradingForm symbol={currentSymbol} />
        </div>
        <div className="trading-sidebar">
          {/* Order book would go here */}
          <h3>Order Book</h3>
          <p>Order book will be implemented later.</p>

          {/* Order history would go here */}
          <h3>Order History</h3>
          <p>Order history will be implemented later.</p>
        </div>
      </div>
    </div>
  );
};

export default FuturesTrading;
