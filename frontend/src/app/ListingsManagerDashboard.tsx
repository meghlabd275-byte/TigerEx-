import React from 'react';

const ListingsManagerDashboard = () => {
  // Mock data for token listings
  const listings = [
    { id: 1, name: 'Bitcoin', symbol: 'BTC', status: 'Active' },
    { id: 2, name: 'Ethereum', symbol: 'ETH', status: 'Active' },
    { id: 3, name: 'Solana', symbol: 'SOL', status: 'Pending' },
  ];

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Listings Manager Dashboard</h1>
      <div className="bg-gray-800 text-white p-4 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Token Listings</h2>
        <table className="w-full">
          <thead>
            <tr>
              <th className="text-left">Name</th>
              <th className="text-left">Symbol</th>
              <th className="text-left">Status</th>
              <th className="text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {listings.map((listing) => (
              <tr key={listing.id}>
                <td>{listing.name}</td>
                <td>{listing.symbol}</td>
                <td>{listing.status}</td>
                <td>
                  <button className="bg-blue-500 px-2 py-1 rounded">View</button>
                  <button className="bg-green-500 px-2 py-1 rounded ml-2">Approve</button>
                  <button className="bg-red-500 px-2 py-1 rounded ml-2">Reject</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ListingsManagerDashboard;
