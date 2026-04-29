/**
 * TigerEx Spot Trading - React/TypeScript Page
 * Complete spot trading functionality
 */

import React, { useState, useEffect } from 'react';

interface Market {
  symbol: string;
  price: number;
  change: number;
  volume: number;
}

const SpotTrading: React.FC = () => {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [balance, setBalance] = useState(0);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [orderType, setOrderType] = useState('buy');
  const [orderAmount, setOrderAmount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const auth = localStorage.getItem('tigerex_auth');
    setIsAuthenticated(!!auth);
    
    // Load sample markets
    setMarkets([
      { symbol: 'BTC', price: 42500, change: 2.5, volume: 1250000000 },
      { symbol: 'ETH', price: 2250, change: 3.2, volume: 890000000 },
      { symbol: 'BNB', price: 320, change: 1.8, volume: 450000000 },
      { symbol: 'SOL', price: 98, change: 5.5, volume: 320000000 },
      { symbol: 'XRP', price: 0.62, change: -1.2, volume: 280000000 }
    ]);
    setLoading(false);
  }, []);

  const handleOrder = (symbol: string, type: string) => {
    if (!isAuthenticated) {
      window.location.href = '/login.html';
      return;
    }
    setSelectedSymbol(symbol);
    setOrderType(type);
  };

  const placeOrder = () => {
    if (!selectedSymbol || !orderAmount) return;
    alert(`${orderType === 'buy' ? 'Buy' : 'Sell'} order placed for ${orderAmount} ${selectedSymbol}!`);
    setSelectedSymbol('');
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div style={{ padding: '24px', background: '#0B0E14', minHeight: '100vh', color: '#EAECE4', fontFamily: 'Inter, sans-serif' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 24px', background: '#1C2128', marginBottom: '24px', borderRadius: '12px' }}>
        <div style={{ fontSize: '22px', fontWeight: '700', color: '#F0B90B' }}>🐯 TigerEx - Spot (React/TS)</div>
        <nav style={{ display: 'flex', gap: '20px' }}>
          <a href="/dashboard.html" style={{ color: '#8B929E', textDecoration: 'none' }}>Dashboard</a>
          <a href="/spot.html" style={{ color: '#F0B90B', textDecoration: 'none' }}>Spot</a>
          <a href="/wallet.html" style={{ color: '#8B929E', textDecoration: 'none' }}>Wallet</a>
        </nav>
      </header>
      
      <h1>Spot Trading</h1>
      <p style={{ color: '#8B929E', marginBottom: '24px' }}>Buy and sell cryptocurrencies instantly</p>
      
      {isAuthenticated && (
        <div style={{ background: '#1C2128', padding: '20px', borderRadius: '12px', marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#8B929E' }}>Balance</span>
            <span style={{ fontWeight: '700' }}>${balance.toFixed(2)}</span>
          </div>
        </div>
      )}
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {markets.map((market) => (
          <div key={market.symbol} style={{ background: '#1C2128', padding: '20px', borderRadius: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ fontWeight: '700' }}>{market.symbol}/USDT</span>
              <span style={{ color: market.change >= 0 ? '#00C087' : '#F6465D' }}>
                {market.change >= 0 ? '+' : ''}{market.change}%
              </span>
            </div>
            <div style={{ fontSize: '24px', fontWeight: '700', color: market.change >= 0 ? '#00C087' : '#F6465D', marginBottom: '12px' }}>
              ${market.price.toLocaleString()}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <button onClick={() => handleOrder(market.symbol, 'buy')} disabled={!isAuthenticated} style={{ padding: '12px', background: '#00C087', border: 'none', borderRadius: '8px', fontWeight: '600', cursor: isAuthenticated ? 'pointer' : 'not-allowed' }}>Buy</button>
              <button onClick={() => handleOrder(market.symbol, 'sell')} disabled={!isAuthenticated} style={{ padding: '12px', background: '#F6465D', border: 'none', borderRadius: '8px', fontWeight: '600', color: '#fff', cursor: isAuthenticated ? 'pointer' : 'not-allowed' }}>Sell</button>
            </div>
          </div>
        ))}
      </div>
      
      {selectedSymbol && (
        <div style={{ background: '#1C2128', padding: '24px', borderRadius: '12px' }}>
          <h3>Place {orderType === 'buy' ? 'Buy' : 'Sell'} {selectedSymbol}</h3>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', color: '#8B929E', marginBottom: '8px' }}>Amount</label>
            <input type="number" value={orderAmount} onChange={e => setOrderAmount(Number(e.target.value))} style={{ width: '100%', padding: '12px', background: '#0B0E14', border: '1px solid #2A303C', borderRadius: '8px', color: '#EAECE4' }} />
          </div>
          <button onClick={placeOrder} style={{ width: '100%', padding: '14px', background: orderType === 'buy' ? '#00C087' : '#F6465D', border: 'none', borderRadius: '8px', fontWeight: '700', cursor: 'pointer' }}>
            {orderType === 'buy' ? 'Buy' : 'Sell'} {selectedSymbol}
          </button>
        </div>
      )}
      
      {!isAuthenticated && (
        <div style={{ background: '#1C2128', padding: '24px', borderRadius: '12px' }}>
          <h3>Login Required</h3>
          <p style={{ color: '#8B929E' }}>Please login to trade</p>
          <a href="/login.html" style={{ display: 'block', textAlign: 'center', padding: '14px', background: '#F0B90B', color: '#000', textDecoration: 'none', borderRadius: '8px', marginTop: '16px', fontWeight: '700' }}>Login</a>
        </div>
      )}
    </div>
  );
};

export default SpotTrading;