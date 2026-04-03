import React from 'react';

const LiquidityProviderDashboard = () => {
  // Mock data for liquidity pools
  const pools = [
    { id: 1, name: 'BTC/USDT', provider: 'Binance', volume: '1,000,000 USDT', status: 'Connected' },
    { id: 2, name: 'ETH/USDT', provider: 'KuCoin', volume: '500,000 USDT', status: 'Connected' },
    { id: 3, name: 'SOL/USDT', provider: 'Bybit', volume: '250,000 USDT', status: 'Disconnected' },
  ];

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Liquidity Provider Dashboard</h1>
      <div className="bg-gray-800 text-white p-4 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Liquidity Pools</h2>
        <table className="w-full">
          <thead>
            <tr>
              <th className="text-left">Pool</th>
              <th className="text-left">Provider</th>
              <th className="text-left">Volume (24h)</th>
              <th className="text-left">Status</th>
              <th className="text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {pools.map((pool) => (
              <tr key={pool.id}>
                <td>{pool.name}</td>
                <td>{pool.provider}</td>
                <td>{pool.volume}</td>
                <td>{pool.status}</td>
                <td>
                  <button className="bg-blue-500 px-2 py-1 rounded">View</button>
                  <button className="bg-green-500 px-2 py-1 rounded ml-2">Connect</button>
                  <button className="bg-red-500 px-2 py-1 rounded ml-2">Disconnect</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LiquidityProviderDashboard;
