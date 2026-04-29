/**
 * TigerEx All Features - React (JavaScript)
 * Complete trading platform
 */

import React, { useState, useEffect } from 'react';

function TradingPlatform() {
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    setAuthenticated(!!localStorage.getItem('tigerex_auth'));
  }, []);

  const features = [
    { name: 'Spot Trading', desc: 'Buy & sell instantly', icon: '💰', page: '/spot.html' },
    { name: 'Futures USDT/COIN', desc: 'Up to 125x leverage', icon: '📈', page: '/futures.html' },
    { name: 'Options Trading', desc: 'Call/Put with Greeks', icon: '🎯', page: '/options.html' },
    { name: 'Margin Trading', desc: '10x borrowed leverage', icon: '📊', page: '/margin.html' },
    { name: 'Copy Trading', desc: 'Follow expert traders', icon: '📋', page: '/copy.html' },
    { name: 'P2P Trading', desc: 'Peer-to-peer marketplace', icon: '🤝', page: '/p2p.html' },
    { name: 'Pre-Market', desc: 'Trade before listing', icon: '🚀', page: '/pre-market.html' },
    { name: 'Prediction', desc: 'Binary outcome betting', icon: '🔮', page: '/prediction-market.html' },
    { name: 'Earn & Staking', desc: 'Up to 20% APY', icon: '💎', page: '/earn.html' },
    { name: 'Wallet', desc: 'Multi-chain wallet', icon: '💰', page: '/wallet.html' }
  ];

  return (
    <div className="platform">
      <header className="header">
        <div className="logo">🐯 TigerEx - React Platform</div>
        <nav>
          <a href="/index.html">Home</a>
          <a href="/dashboard.html">Dashboard</a>
          <a href="/wallet.html">Wallet</a>
        </nav>
      </header>
      <main>
        <h1>Complete Trading Features</h1>
        <p>All what you need in one platform</p>
        <div className="grid">
          {features.map(f => (
            <div key={f.name} className="card">
              <div className="icon">{f.icon}</div>
              <h3>{f.name}</h3>
              <p>{f.desc}</p>
              <a href={f.page} className="btn">Trade</a>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

export default TradingPlatform;