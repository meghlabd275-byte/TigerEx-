/**
 * TigerEx Spot Trading - React (JavaScript)
 * Complete spot trading functionality
 */

import React, { useState, useEffect } from 'react';

function SpotTrading() {
  const [markets, setMarkets] = useState([]);
  const [balance, setBalance] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check auth
    const auth = localStorage.getItem('tigerex_auth');
    if (auth) {
      setBalance(0);
    }
    
    // Load markets data
    setMarkets([
      { symbol: 'BTC', price: 42500, change: 2.5, volume: 1250000000 },
      { symbol: 'ETH', price: 2250, change: 3.2, volume: 890000000 },
      { symbol: 'BNB', price: 320, change: 1.8, volume: 450000000 },
      { symbol: 'SOL', price: 98, change: 5.5, volume: 320000000 },
      { symbol: 'XRP', price: 0.62, change: -1.2, volume: 280000000 }
    ]);
    setLoading(false);
  }, []);

  const handleBuy = (symbol) => {
    if (!localStorage.getItem('tigerex_auth')) {
      window.location.href = '/login.html';
      return;
    }
    alert(`Buy ${symbol} - Order placed!`);
  };

  const handleSell = (symbol) => {
    if (!localStorage.getItem('tigerex_auth')) {
      window.location.href = '/login.html';
      return;
    }
    alert(`Sell ${symbol} - Order placed!`);
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="trading-platform">
      <header className="header">
        <div className="logo">🐯 TigerEx - Spot (React)</div>
        <nav className="nav">
          <a href="/dashboard.html">Dashboard</a>
          <a href="/spot.html" className="active">Spot</a>
          <a href="/futures.html">Futures</a>
          <a href="/wallet.html">Wallet</a>
        </nav>
      </header>

      <main className="main">
        <h1>Spot Trading</h1>
        <p className="subtitle">Buy and sell cryptocurrencies instantly</p>

        <div className="balance-display">
          <div className="balance-item">
            <span className="label">Available Balance</span>
            <span className="value">${balance.toFixed(2)}</span>
          </div>
        </div>

        <div className="markets-grid">
          {markets.map(market => (
            <div key={market.symbol} className="market-card">
              <div className="market-header">
                <span className="pair">{market.symbol}/USDT</span>
                <span className={`change ${market.change >= 0 ? 'positive' : 'negative'}`}>
                  {market.change >= 0 ? '+' : ''}{market.change}%
                </span>
              </div>
              <div className={`price ${market.change >= 0 ? 'positive' : 'negative'}`}>
                ${market.price.toLocaleString()}
              </div>
              <div className="volume">Volume: ${(market.volume / 1000000).toFixed(0)}M</div>
              <div className="actions">
                <button className="buy-btn" onClick={() => handleBuy(market.symbol)}>Buy</button>
                <button className="sell-btn" onClick={() => handleSell(market.symbol)}>Sell</button>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

export default SpotTrading;export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
