import React from 'react';
import TradingForm from '@/components/TradingForm';

const TraderDashboard = () => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Trader Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-1">
          <TradingForm />
        </div>
        <div className="md:col-span-2">
          {/* Chart and order book will go here */}
          <div className="bg-gray-800 text-white p-4 rounded-lg h-full">
            <h2 className="text-xl font-bold mb-4">Chart</h2>
            <p>Chart component will be rendered here.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TraderDashboard;
