'use client';

import React, { useState } from 'react';
import { 
  Search, 
  Bell, 
  User, 
  Settings, 
  ChevronRight,
  CheckCircle,
  Clock,
  Eye,
  EyeOff,
  Plus,
  Minus,
  ArrowUpRight,
  ArrowDownLeft,
  TrendingUp
} from 'lucide-react';

interface MarketItem {
  id: string;
  symbol: string;
  name: string;
  price: string;
  change: string;
  changePercent: string;
  volume: string;
  isPositive: boolean;
}

const mockMarkets: MarketItem[] = [
  {
    id: '1',
    symbol: 'BTC',
    name: 'Bitcoin',
    price: '43,250.00',
    change: '+1,250.00',
    changePercent: '+2.98%',
    volume: '1.2B',
    isPositive: true,
  },
  {
    id: '2',
    symbol: 'ETH',
    name: 'Ethereum',
    price: '2,650.00',
    change: '+85.50',
    changePercent: '+3.33%',
    volume: '850M',
    isPositive: true,
  },
  {
    id: '3',
    symbol: 'BNB',
    name: 'BNB',
    price: '315.20',
    change: '-5.80',
    changePercent: '-1.81%',
    volume: '420M',
    isPositive: false,
  },
  {
    id: '4',
    symbol: 'SOL',
    name: 'Solana',
    price: '98.45',
    change: '+4.20',
    changePercent: '+4.46%',
    volume: '380M',
    isPositive: true,
  },
];

export default function DashboardScreen() {
  const [balanceVisible, setBalanceVisible] = useState(false);
  const [activeMarketTab, setActiveMarketTab] = useState('Holding');

  const marketTabs = ['Holding', 'Hot', 'New Listing', 'Favorite', 'Top Gainers', '24h Volume'];

  return (
    <div className="flex-1 bg-bg-primary text-text-primary overflow-y-auto">
      {/* Top Navigation */}
      <div className="bg-bg-secondary border-b border-border-primary px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-semibold">Dashboard</h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-secondary" />
              <input
                type="text"
                placeholder="Search..."
                className="pl-10 pr-4 py-2 bg-bg-tertiary border border-border-secondary rounded-lg focus:outline-none focus:border-primary text-sm w-80"
              />
            </div>
            <button className="btn-primary">
              Deposit
            </button>
            <Bell size={20} className="text-text-secondary hover:text-text-primary cursor-pointer" />
            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center cursor-pointer">
              <User size={16} className="text-black" />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6 space-y-6">
        {/* User Profile Section */}
        <div className="card-primary">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center">
              <span className="text-black font-bold text-xl">U</span>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-text-primary">User-0f8ed</h2>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs bg-success/20 text-success px-2 py-1 rounded">
                  Regular
                </span>
                <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                  Verified
                </span>
              </div>
            </div>
          </div>

          {/* Get Started Checklist */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-4">Get Started</h3>
            <div className="space-y-3">
              {/* Step 1: Verify Account */}
              <div className="flex items-center justify-between p-4 bg-bg-secondary rounded-lg border border-border-secondary">
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 bg-success rounded-full flex items-center justify-center">
                    <CheckCircle size={16} className="text-white" />
                  </div>
                  <div>
                    <h4 className="font-medium text-text-primary">Verify Account</h4>
                    <p className="text-sm text-text-secondary">Complete identity verification to access all Binance services</p>
                  </div>
                </div>
                <button className="btn-primary">
                  Verify Now
                </button>
              </div>

              {/* Step 2: Deposit */}
              <div className="flex items-center justify-between p-4 bg-bg-secondary rounded-lg border border-border-secondary">
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 bg-text-quaternary rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">2</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-text-primary">Deposit</h4>
                    <div className="flex items-center gap-2">
                      <Clock size={14} className="text-text-secondary" />
                      <span className="text-sm text-text-secondary">Pending</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Step 3: Trade */}
              <div className="flex items-center justify-between p-4 bg-bg-secondary rounded-lg border border-border-secondary">
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 bg-text-quaternary rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">3</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-text-primary">Trade</h4>
                    <div className="flex items-center gap-2">
                      <Clock size={14} className="text-text-secondary" />
                      <span className="text-sm text-text-secondary">Pending</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Estimated Balance Widget */}
        <div className="card-primary">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Estimated Balance</h3>
            <button onClick={() => setBalanceVisible(!balanceVisible)}>
              {balanceVisible ? (
                <Eye size={20} className="text-text-secondary hover:text-text-primary" />
              ) : (
                <EyeOff size={20} className="text-text-secondary hover:text-text-primary" />
              )}
            </button>
          </div>

          <div className="mb-6">
            <div className="text-3xl font-bold text-text-primary mb-2">
              {balanceVisible ? '0.00' : '****'} <span className="text-lg text-text-secondary">BTC</span>
            </div>
            <div className="text-text-secondary mb-1">
              ≈ ${balanceVisible ? '0.00' : '****'}
            </div>
            <div className="text-sm text-text-secondary">
              Today's PnL: ≈ ${balanceVisible ? '0.00' : '****'} ({balanceVisible ? '0.00%' : '****'})
            </div>
          </div>

          <div className="flex gap-3">
            <button className="btn-primary flex items-center gap-2">
              <Plus size={16} />
              Deposit
            </button>
            <button className="btn-secondary flex items-center gap-2">
              <Minus size={16} />
              Withdraw
            </button>
            <button className="btn-secondary">
              Cash In
            </button>
          </div>
        </div>

        {/* Markets Section */}
        <div className="card-primary">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Markets</h3>
            <button className="text-primary hover:text-primary-hover text-sm font-medium flex items-center gap-1">
              More
              <ChevronRight size={16} />
            </button>
          </div>

          {/* Market Tabs */}
          <div className="flex gap-4 mb-4 border-b border-border-secondary">
            {marketTabs.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveMarketTab(tab)}
                className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
                  activeMarketTab === tab
                    ? 'border-primary text-primary'
                    : 'border-transparent text-text-secondary hover:text-text-primary'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Market List Header */}
          <div className="grid grid-cols-4 gap-4 py-2 text-sm text-text-secondary border-b border-border-secondary mb-2">
            <span>Coin</span>
            <span className="text-right">Coin Price</span>
            <span className="text-right">24H Change</span>
            <span className="text-right">Actions</span>
          </div>

          {/* Market List */}
          <div className="space-y-2">
            {mockMarkets.map((market) => (
              <div
                key={market.id}
                className="grid grid-cols-4 gap-4 py-3 hover:bg-bg-secondary rounded-lg cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                    <span className="text-xs font-bold text-black">
                      {market.symbol.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <div className="font-medium text-text-primary">{market.symbol}</div>
                    <div className="text-xs text-text-secondary">{market.name}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium text-text-primary">${market.price}</div>
                  <div className="text-xs text-text-secondary">{market.volume}</div>
                </div>
                <div className="text-right">
                  <div className={`font-medium ${market.isPositive ? 'text-success' : 'text-danger'}`}>
                    {market.changePercent}
                  </div>
                  <div className={`text-xs ${market.isPositive ? 'text-success' : 'text-danger'}`}>
                    {market.change}
                  </div>
                </div>
                <div className="text-right">
                  <button className="btn-primary text-xs px-3 py-1">
                    Trade
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}