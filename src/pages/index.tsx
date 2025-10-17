/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

import React from 'react';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-8">
          Welcome to TigerEx Exchange
        </h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold mb-4">Spot Trading</h2>
            <p className="text-gray-600 mb-4">
              Trade cryptocurrencies with the best prices and lowest fees.
            </p>
            <Link to="/trading" className="text-blue-600 hover:underline">
              Start Trading →
            </Link>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold mb-4">Futures Trading</h2>
            <p className="text-gray-600 mb-4">
              Advanced futures trading with up to 125x leverage.
            </p>
            <Link to="/trading" className="text-blue-600 hover:underline">
              Trade Futures →
            </Link>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold mb-4">Copy Trading</h2>
            <p className="text-gray-600 mb-4">
              Follow expert traders and copy their strategies automatically.
            </p>
            <Link to="/trading" className="text-blue-600 hover:underline">
              Copy Traders →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;