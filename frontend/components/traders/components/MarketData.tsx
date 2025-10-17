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

interface MarketStats {
  symbol: string;
  price: number;
  change24h: number;
  changePercent24h: number;
  high24h: number;
  low24h: number;
  volume24h: number;
  volumeQuote24h: number;
}

interface MarketDataProps {
  symbol?: string;
  data?: MarketStats;
}

export const MarketData: React.FC<MarketDataProps> = ({
  symbol = 'BTCUSDT',
  data,
}) => {
  // Mock data if no data provided
  const mockData: MarketStats = data || {
    symbol: 'BTCUSDT',
    price: 45001.25,
    change24h: 1250.75,
    changePercent24h: 2.86,
    high24h: 45850.0,
    low24h: 43200.5,
    volume24h: 12345.67,
    volumeQuote24h: 555789123.45,
  };

  const isPositive = mockData.changePercent24h >= 0;

  const formatNumber = (num: number, decimals: number = 2) => {
    return num.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  };

  const formatVolume = (num: number) => {
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toFixed(2);
  };

  return (
    <div className="bg-gray-900 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-semibold">Market Data</h3>
        <span className="text-gray-400 text-sm">{mockData.symbol}</span>
      </div>

      {/* Current Price */}
      <div className="mb-6">
        <div className="text-3xl font-bold text-white mb-2">
          ${formatNumber(mockData.price)}
        </div>
        <div className="flex items-center space-x-2">
          <span
            className={`text-sm font-medium ${isPositive ? 'text-green-400' : 'text-red-400'}`}
          >
            {isPositive ? '+' : ''}
            {formatNumber(mockData.change24h)}
          </span>
          <span
            className={`text-sm font-medium ${isPositive ? 'text-green-400' : 'text-red-400'}`}
          >
            ({isPositive ? '+' : ''}
            {mockData.changePercent24h.toFixed(2)}%)
          </span>
        </div>
      </div>

      {/* Market Statistics */}
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-gray-400 text-sm">24h High</span>
          <span className="text-white text-sm font-medium">
            ${formatNumber(mockData.high24h)}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-400 text-sm">24h Low</span>
          <span className="text-white text-sm font-medium">
            ${formatNumber(mockData.low24h)}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-400 text-sm">24h Volume (BTC)</span>
          <span className="text-white text-sm font-medium">
            {formatVolume(mockData.volume24h)}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-400 text-sm">24h Volume (USDT)</span>
          <span className="text-white text-sm font-medium">
            {formatVolume(mockData.volumeQuote24h)}
          </span>
        </div>
      </div>

      {/* Price Range Indicator */}
      <div className="mt-6">
        <div className="flex justify-between text-xs text-gray-400 mb-2">
          <span>24h Range</span>
          <span>
            {(
              ((mockData.price - mockData.low24h) /
                (mockData.high24h - mockData.low24h)) *
              100
            ).toFixed(1)}
            %
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div
            className="bg-gradient-to-r from-red-500 to-green-500 h-2 rounded-full relative"
            style={{ width: '100%' }}
          >
            <div
              className="absolute top-0 w-1 h-2 bg-white rounded-full"
              style={{
                left: `${((mockData.price - mockData.low24h) / (mockData.high24h - mockData.low24h)) * 100}%`,
                transform: 'translateX(-50%)',
              }}
            />
          </div>
        </div>
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>${formatNumber(mockData.low24h)}</span>
          <span>${formatNumber(mockData.high24h)}</span>
        </div>
      </div>
    </div>
  );
};
