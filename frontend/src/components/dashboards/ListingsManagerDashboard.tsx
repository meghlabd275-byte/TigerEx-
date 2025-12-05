import React, { useState, useEffect } from 'react';
import { getTokenListings } from '../../lib/api';

interface TokenListing {
  listing_id: string;
  token_name: string;
  token_symbol: string;
  blockchain_network: string;
  status: string;
}

const ListingsManagerDashboard: React.FC = () => {
  const [listings, setListings] = useState<TokenListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchListings = async () => {
      try {
        const data = await getTokenListings();
        setListings(data.listings);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch token listings');
        setLoading(false);
      }
    };

    fetchListings();
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Listings Manager Dashboard</h1>
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}
      {!loading && !error && (
        <table className="min-w-full bg-white border border-gray-200">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b">ID</th>
              <th className="py-2 px-4 border-b">Token Name</th>
              <th className="py-2 px-4 border-b">Symbol</th>
              <th className="py-2 px-4 border-b">Network</th>
              <th className="py-2 px-4 border-b">Status</th>
            </tr>
          </thead>
          <tbody>
            {listings.map((listing) => (
              <tr key={listing.listing_id}>
                <td className="py-2 px-4 border-b">{listing.listing_id}</td>
                <td className="py-2 px-4 border-b">{listing.token_name}</td>
                <td className="py-2 px-4 border-b">{listing.token_symbol}</td>
                <td className="py-2 px-4 border-b">{listing.blockchain_network}</td>
                <td className="py-2 px-4 border-b">{listing.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ListingsManagerDashboard;
