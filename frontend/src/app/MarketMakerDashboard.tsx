import React from 'react';

const MarketMakerDashboard = () => {
  // Mock data for market maker bots
  const bots = [
    { id: 1, name: 'BTC/USDT Bot', strategy: 'Grid Trading', status: 'Running', pnl: '+1,250 USDT' },
    { id: 2, name: 'ETH/USDT Bot', strategy: 'Dollar Cost Averaging', status: 'Running', pnl: '+500 USDT' },
    { id: 3, name: 'SOL/USDT Bot', strategy: 'Grid Trading', status: 'Stopped', pnl: '-100 USDT' },
  ];

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Market Maker Dashboard</h1>
      <div className="bg-gray-800 text-white p-4 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Market Maker Bots</h2>
        <table className="w-full">
          <thead>
            <tr>
              <th className="text-left">Bot Name</th>
              <th className="text-left">Strategy</th>
              <th className="text-left">Status</th>
              <th className="text-left">PNL (24h)</th>
              <th className="text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {bots.map((bot) => (
              <tr key={bot.id}>
                <td>{bot.name}</td>
                <td>{bot.strategy}</td>
                <td>{bot.status}</td>
                <td>{bot.pnl}</td>
                <td>
                  <button className="bg-blue-500 px-2 py-1 rounded">View</button>
                  <button className="bg-green-500 px-2 py-1 rounded ml-2">Start</button>
                  <button className="bg-red-500 px-2 py-1 rounded ml-2">Stop</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default MarketMakerDashboard;
