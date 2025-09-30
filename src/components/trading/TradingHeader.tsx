import React from 'react';
import Link from 'next/link';

const TradingHeader: React.FC = () => {
  return (
    <header className="bg-gray-800 border-b border-gray-700">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-yellow-500 rounded-lg flex items-center justify-center">
              <span className="text-black font-bold text-lg">T</span>
            </div>
            <span className="text-white font-bold text-xl">TigerEx</span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link
              href="/trading"
              className="text-gray-300 hover:text-white transition-colors"
            >
              Spot Trading
            </Link>
            <Link href="/futures" className="text-yellow-400 font-medium">
              Futures
            </Link>
            <Link
              href="/options"
              className="text-gray-300 hover:text-white transition-colors"
            >
              Options
            </Link>
            <Link
              href="/alpha-market"
              className="text-gray-300 hover:text-white transition-colors"
            >
              Alpha Market
            </Link>
            <Link
              href="/p2p"
              className="text-gray-300 hover:text-white transition-colors"
            >
              P2P
            </Link>
          </nav>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <div className="text-white text-sm">
              <div className="text-gray-400">Total Balance</div>
              <div className="font-medium">10,000.00 USDT</div>
            </div>
            <button className="bg-yellow-500 text-black px-4 py-2 rounded-lg font-medium hover:bg-yellow-400 transition-colors">
              Deposit
            </button>
            <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm">U</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default TradingHeader;
