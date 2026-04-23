'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import styles from '../styles/Home.module.css';

// Theme Context
const ThemeContext = createContext(null);

export default function Home() {
  const [theme, setTheme] = useState('dark');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const saved = localStorage.getItem('theme') || 'dark';
    setTheme(saved);
    document.body?.setAttribute('data-theme', saved);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.body?.setAttribute('data-theme', newTheme);
  };

  const coins = [
    { symbol: 'BTC', name: 'Bitcoin', price: '$67,432', change: '+2.3%', icon: '₿' },
    { symbol: 'ETH', name: 'Ethereum', price: '$3,456', change: '+1.8%', icon: 'Ξ' },
    { symbol: 'SOL', name: 'Solana', price: '$138', change: '-3.2%', icon: '◎' },
    { symbol: 'BNB', name: 'BNB', price: '$598', change: '+0.5%', icon: '🧱' },
    { symbol: 'XAU', name: 'Gold', price: '$2,345', change: '+0.8%', icon: '🥇' },
  ];

  const categories = [
    { name: 'Futures', icon: '📈', desc: '125x leverage', href: '/trade' },
    { name: 'Spot', icon: '💎', desc: '500+ tokens', href: '/trade?type=spot' },
    { name: 'P2P', icon: '🤝', desc: '0 fees', href: '/trade?type=p2p' },
    { name: 'TradFi', icon: '📊', desc: 'CFD Trading', href: '/tradfi' },
    { name: 'Staking', icon: '🔒', desc: 'Up to 20%', href: '/earn' },
    { name: 'Copy Trading', icon: '👥', desc: 'Follow experts', href: '/copy' },
    { name: 'Wallet', icon: '💰', desc: 'All assets', href: '/assets' },
    { name: 'Card', icon: '💳', desc: '3% cashback', href: '/card' },
  ];

  return (
    <div className={styles.container} data-theme={theme}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <Link href="/" className={styles.logo}>
            <span className={styles.logoIcon}>🐯</span>
            TigerEx
          </Link>
          
          {/* Search */}
          <div className={styles.searchContainer}>
            <input 
              type="text" 
              placeholder="Search coins..." 
              className={styles.searchInput}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
        
        <div className={styles.headerRight}>
          {/* QR Scanner */}
          <button className={styles.headerBtn} title="Scan QR">📷</button>
          
          {/* Notifications */}
          <button className={styles.headerBtn} title="Notifications">🔔</button>
          
          {/* Support */}
          <button className={styles.headerBtn} title="Support">💬</button>
          
          {/* Profile */}
          <Link href="/profile" className={styles.profileBtn}>
            <span className={styles.avatar}>JD</span>
          </Link>
          
          {/* Theme Toggle */}
          <button className={styles.themeToggle} onClick={toggleTheme}>
            {theme === 'dark' ? '🌙' : '☀️'}
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className={styles.main}>
        {/* Stats */}
        <div className={styles.statsGrid}>
          <div className={styles.statCard}>
            <div className={styles.statIcon}>💰</div>
            <div className={styles.statInfo}>
              <div className={styles.statValue}>$45,678</div>
              <div className={styles.statLabel}>Total Balance</div>
            </div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statIcon}>📈</div>
            <div className={styles.statInfo}>
              <div className={styles.statValue}>+$2,345</div>
              <div className={styles.statLabel}>Today's P&L</div>
            </div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statIcon}>🤝</div>
            <div className={styles.statInfo}>
              <div className={styles.statValue}>15</div>
              <div className={styles.statLabel}>Open Orders</div>
            </div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statIcon}>⭐</div>
            <div className={styles.statInfo}>
              <div className={styles.statValue}>VIP 3</div>
              <div className={styles.statLabel}>User Level</div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className={styles.quickActions}>
          <Link href="/trade" className={styles.actionBtn}>📈 Trade</Link>
          <Link href="/assets" className={styles.actionBtn}>💰 Deposit</Link>
          <Link href="/assets" className={styles.actionBtn}>📤 Withdraw</Link>
          <Link href="/tradfi" className={styles.actionBtn}>📊 TradFi</Link>
        </div>

        {/* Top Markets */}
        <h2 className={styles.sectionTitle}>Top Markets</h2>
        <div className={styles.marketsGrid}>
          {coins.map((coin) => (
            <Link key={coin.symbol} href={`/trade?symbol=${coin.symbol}`} className={styles.marketCard}>
              <div className={styles.marketHeader}>
                <span className={styles.marketIcon}>{coin.icon}</span>
                <div>
                  <div className={styles.marketName}>{coin.name}</div>
                  <div className={styles.marketSymbol}>{coin.symbol}/USDT</div>
                </div>
              </div>
              <div className={styles.marketPrice}>{coin.price}</div>
              <div className={`${styles.marketChange} ${coin.change.startsWith('+') ? styles.up : styles.down}`}>
                {coin.change}
              </div>
            </Link>
          ))}
        </div>

        {/* Categories */}
        <h2 className={styles.sectionTitle}>Services</h2>
        <div className={styles.categoriesGrid}>
          {categories.map((cat) => (
            <Link key={cat.name} href={cat.href} className={styles.categoryCard}>
              <div className={styles.categoryIcon}>{cat.icon}</div>
              <div className={styles.categoryName}>{cat.name}</div>
              <div className={styles.categoryDesc}>{cat.desc}</div>
            </Link>
          ))}
        </div>
      </main>

      {/* Mobile Nav */}
      <nav className={styles.mobileNav}>
        <Link href="/" className={styles.mobileNavItem + ' ' + styles.active}>🏠 Home</Link>
        <Link href="/trade" className={styles.mobileNavItem}>📈 Trade</Link>
        <Link href="/assets" className={styles.mobileNavItem}>💰 Assets</Link>
        <Link href="/more" className={styles.mobileNavItem}>📋 More</Link>
        <Link href="/profile" className={styles.mobileNavItem}>👤 Profile</Link>
      </nav>
    </div>
  );
}