import Head from 'next/head';
import { useState, useEffect } from 'react';

// Platform Links Data
const platformLinks = {
  home: [{ name: 'Bitget', url: 'https://www.bitget.com/', icon: '🐯', desc: 'Main exchange' }],
  markets: [{ name: 'Binance Markets', url: 'https://www.binance.com/en/markets/overview', icon: '📊', desc: 'Markets overview' }],
  trade: [
    { name: 'Futures', url: 'https://www.bitget.com/futures/usdt/BTCUSDT', icon: '📈', desc: 'USDT-M' },
    { name: 'Spot', url: 'https://www.bitget.com/spot/BTCUSDT', icon: '💎', desc: 'Spot' },
    { name: 'Margin', url: 'https://www.bitget.com/spot/BTCUSDT?type=cross', icon: '⚡', desc: 'Cross' },
    { name: 'P2P', url: 'https://p2p.binance.com/en', icon: '🤝', desc: 'P2P' },
    { name: 'On-Chain', url: 'https://www.bitget.com/on-chain/sol/2pFFgMtw7GkE6Kr6Xpg81mqDvEihhoafg64HdheKpump', icon: '⛓️', desc: 'On-chain' },
    { name: 'Alpha', url: 'https://www.binance.com/en/alpha/bsc/0xd20fb09a49a8e75fef536a2dbc68222900287bac', icon: '🚀', desc: 'Alpha' }
  ],
  tradfi: [
    { name: 'CFD', url: 'https://www.bitgettradfi.com/tradfi/XAUUSD', icon: '📊', desc: 'CFD' },
    { name: 'Stocks', url: 'https://www.bitget.com/on-chain/bnb/0xa9ee28c80f960b889dfbd1902055218cba016f75', icon: '🏢', desc: 'Stocks' },
    { name: 'Stock Preps', url: 'https://www.bitget.com/futures/usdt/NVDAUSDT', icon: '🧪', desc: 'NVDA' }
  ],
  assets: [
    { name: 'Assets', url: 'https://www.bitget.com/asset', icon: '💰', desc: 'All wallets' },
    { name: 'Deposit', url: 'https://www.bitget.com/asset', icon: '📥', desc: 'Deposit' },
    { name: 'Withdrawal', url: 'https://www.bitget.com/asset', icon: '📤', desc: 'Withdraw' },
    { name: 'Spot Wallet', url: 'https://www.bitget.com/asset', icon: '💵', desc: 'Spot' },
    { name: 'Futures', url: 'https://www.bitget.com/asset', icon: '📈', desc: 'Futures' },
    { name: 'P2P', url: 'https://www.bitget.com/asset', icon: '🤝', desc: 'P2P' },
    { name: 'TigerPay', url: 'https://www.bitget.com/asset', icon: '🐯', desc: 'Payment' },
    { name: 'TradFi', url: 'https://www.bitget.com/asset', icon: '📊', desc: 'CFD' },
    { name: 'Crypto Card', url: 'https://www.bitget.com/asset', icon: '💳', desc: 'Card' }
  ]
};

// Theme colors
const themes = {
  dark: { bg: '#050A12', surface: '#0D1B2A', card: '#0D1B2A', text: '#E8EEF4', textSec: 'rgba(255,255,255,0.7)' },
  light: { bg: '#F5F7FA', surface: '#FFFFFF', card: '#FFFFFF', text: '#1A1A2E', textSec: '#666666' }
};

export default function Home() {
  const [darkMode, setDarkMode] = useState(true);
  const [section, setSection] = useState('home');
  const t = themes[darkMode ? 'dark' : 'light'];

  // Auto-detect system theme
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setDarkMode(prefersDark);
    }
  }, []);

  const navItems = [
    { id: 'home', icon: '🏠', label: 'Home' },
    { id: 'markets', icon: '📊', label: 'Markets' },
    { id: 'trade', icon: '📈', label: 'Trade' },
    { id: 'tradfi', icon: '📊', label: 'TradFi' },
    { id: 'assets', icon: '💰', label: 'Assets' }
  ];

  const links = platformLinks[section] || [];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: t.bg, color: t.text }}>
      <Head><title>TigerEx Trading Dashboard</title></Head>
      
      {/* Sidebar */}
      <nav style={{ width: 260, background: t.surface, borderRight: '1px solid rgba(255,255,255,0.06)', padding: 20, position: 'fixed', height: '100vh' }}>
        <h1 style={{ fontSize: '1.8rem', color: '#F6821F', marginBottom: 24 }}>🐯 TigerEx</h1>
        {navItems.map(item => (
          <button key={item.id} onClick={() => setSection(item.id)}
            style={{ display: 'flex', alignItems: 'center', width: '100%', padding: '12px 16px', border: 'none', borderRadius: 8, cursor: 'pointer', background: section === item.id ? 'rgba(246,130,31,0.15)' : 'transparent', color: section === item.id ? '#F6821F' : t.textSec, marginBottom: 4, fontSize: '1rem', textAlign: 'left' }}>
            <span style={{ marginRight: 12 }}>{item.icon}</span>{item.label}
          </button>
        ))}
        <button onClick={() => setDarkMode(!darkMode)} style={{ position: 'absolute', bottom: 20, left: 20, padding: '12px 16px', border: 'none', borderRadius: 8, cursor: 'pointer', background: t.card, color: '#F6821F' }}>
          {darkMode ? '☀️ Light' : '🌙 Dark'}
        </button>
      </nav>

      {/* Main Content */}
      <main style={{ marginLeft: 260, padding: 24, flex: 1 }}>
        <h2 style={{ fontSize: '1.5rem', marginBottom: 24 }}>{navItems.find(n => n.id === section)?.label}</h2>
        
        {/* Stats */}
        {section === 'home' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 32 }}>
            {['8+', '50+', '24/7'].map((v, i) => (
              <div key={i} style={{ padding: 20, background: t.card, borderRadius: 12, textAlign: 'center' }}>
                <div style={{ fontSize: '1.8rem', color: '#F6821F', fontWeight: 'bold' }}>{v}</div>
                <div style={{ fontSize: '0.8rem', color: t.textSec }}>{['Platforms', 'Markets', 'Support'][i]}</div>
              </div>
            ))}
          </div>
        )}

        {/* Links Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>
          {links.map((link, i) => (
            <a key={i} href={link.url} target="_blank" rel="noopener noreferrer"
              style={{ display: 'block', padding: 20, background: t.card, borderRadius: 12, textDecoration: 'none', color: t.text, transition: 'transform 0.2s' }}>
              <div style={{ fontSize: '1.5rem', marginBottom: 12 }}>{link.icon}</div>
              <div style={{ fontWeight: 600, fontSize: '1.1rem', marginBottom: 4 }}>{link.name}</div>
              <div style={{ fontSize: '0.85rem', color: t.textSec }}>{link.desc}</div>
            </a>
          ))}
        </div>
      </main>
    </div>
  );
}