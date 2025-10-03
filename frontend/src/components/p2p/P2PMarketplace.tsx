import React, { useState } from 'react';
import { Search, Filter, Bell, ChevronDown, TrendingUp } from 'lucide-react';

interface P2POffer {
  id: string;
  merchant: string;
  merchantAvatar: string;
  trades: number;
  completionRate: number;
  price: number;
  currency: string;
  limit: {
    min: number;
    max: number;
  };
  available: number;
  paymentMethods: string[];
  responseTime: string;
  verified: boolean;
}

const P2PMarketplace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'express' | 'p2p'>('p2p');
  const [orderType, setOrderType] = useState<'buy' | 'sell'>('buy');
  const [selectedCrypto, setSelectedCrypto] = useState('USDT');
  const [selectedCurrency, setSelectedCurrency] = useState('BDT');

  const offers: P2POffer[] = [
    {
      id: '1',
      merchant: 'dealusdt',
      merchantAvatar: '👤',
      trades: 517,
      completionRate: 93.00,
      price: 124.61,
      currency: 'BDT',
      limit: { min: 10000, max: 24550 },
      available: 404.11,
      paymentMethods: ['bKash', 'Rocket'],
      responseTime: '15 min',
      verified: true,
    },
    {
      id: '2',
      merchant: '___Green--Support___',
      merchantAvatar: '👤',
      trades: 2690,
      completionRate: 100.00,
      price: 124.62,
      currency: 'BDT',
      limit: { min: 12000, max: 49100 },
      available: 986.46,
      paymentMethods: ['bKash', 'Rocket'],
      responseTime: '15 min',
      verified: true,
    },
    {
      id: '3',
      merchant: 'STOCK-TIME',
      merchantAvatar: '👤',
      trades: 1912,
      completionRate: 99.20,
      price: 124.75,
      currency: 'BDT',
      limit: { min: 15000, max: 28273 },
      available: 226.64,
      paymentMethods: ['bKash'],
      responseTime: '15 min',
      verified: true,
    },
    {
      id: '4',
      merchant: 'AN---NABA',
      merchantAvatar: '👤',
      trades: 4205,
      completionRate: 100.00,
      price: 124.79,
      currency: 'BDT',
      limit: { min: 10000, max: 50000 },
      available: 500.00,
      paymentMethods: ['bKash', 'Nagad', 'Rocket'],
      responseTime: '10 min',
      verified: true,
    },
  ];

  const sellOffers: P2POffer[] = [
    {
      id: '5',
      merchant: 'MR_Exchange_BD',
      merchantAvatar: '👤',
      trades: 339,
      completionRate: 98.30,
      price: 125.51,
      currency: 'BDT',
      limit: { min: 5000, max: 200000 },
      available: 45937.92,
      paymentMethods: ['Rocket'],
      responseTime: '30 min',
      verified: true,
    },
    {
      id: '6',
      merchant: 'FastP2PDeals',
      merchantAvatar: '👤',
      trades: 1183,
      completionRate: 100.00,
      price: 125.50,
      currency: 'BDT',
      limit: { min: 2000, max: 27636 },
      available: 220.21,
      paymentMethods: ['Rocket'],
      responseTime: '30 min',
      verified: true,
    },
    {
      id: '7',
      merchant: 'Wise_First_Trade',
      merchantAvatar: '👤',
      trades: 927,
      completionRate: 95.00,
      price: 125.47,
      currency: 'BDT',
      limit: { min: 5000, max: 26198 },
      available: 208.80,
      paymentMethods: ['Rocket'],
      responseTime: '15 min',
      verified: true,
    },
    {
      id: '8',
      merchant: 'TrustedAYAN---VAI',
      merchantAvatar: '👤',
      trades: 932,
      completionRate: 98.80,
      price: 125.45,
      currency: 'BDT',
      limit: { min: 10000, max: 50000 },
      available: 400.00,
      paymentMethods: ['bKash', 'Nagad'],
      responseTime: '20 min',
      verified: true,
    },
  ];

  const currentOffers = orderType === 'buy' ? offers : sellOffers;

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-10">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            <button className="text-gray-900 dark:text-white">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setActiveTab('express')}
                className={`text-lg font-semibold ${
                  activeTab === 'express'
                    ? 'text-gray-900 dark:text-white'
                    : 'text-gray-400'
                }`}
              >
                Express
              </button>
              <button
                onClick={() => setActiveTab('p2p')}
                className={`text-lg font-semibold ${
                  activeTab === 'p2p'
                    ? 'text-gray-900 dark:text-white'
                    : 'text-gray-400'
                }`}
              >
                P2P
              </button>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button className="px-3 py-1 border border-gray-300 dark:border-gray-700 rounded text-sm font-medium text-gray-900 dark:text-white flex items-center gap-1">
              {selectedCurrency}
              <ChevronDown className="w-4 h-4" />
            </button>
            <button className="p-2">
              <Bell className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>
          </div>
        </div>

        {/* Buy/Sell Toggle */}
        <div className="flex px-4 pb-3">
          <button
            onClick={() => setOrderType('buy')}
            className={`flex-1 py-2 rounded-l-lg font-semibold transition-colors ${
              orderType === 'buy'
                ? 'bg-gray-900 dark:bg-white text-white dark:text-gray-900'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
            }`}
          >
            Buy
          </button>
          <button
            onClick={() => setOrderType('sell')}
            className={`flex-1 py-2 rounded-r-lg font-semibold transition-colors ${
              orderType === 'sell'
                ? 'bg-gray-900 dark:bg-white text-white dark:text-gray-900'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
            }`}
          >
            Sell
          </button>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3 px-4 pb-3 overflow-x-auto">
          <button className="flex items-center gap-2 px-3 py-1.5 bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded-full whitespace-nowrap">
            <span className="w-4 h-4 rounded-full bg-green-500 flex items-center justify-center text-white text-xs">₮</span>
            {selectedCrypto}
            <ChevronDown className="w-4 h-4" />
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-full whitespace-nowrap">
            Amount
            <ChevronDown className="w-4 h-4" />
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-full whitespace-nowrap">
            Payment
            <ChevronDown className="w-4 h-4" />
          </button>
          <button className="p-1.5 bg-gray-100 dark:bg-gray-800 rounded-full">
            <Filter className="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>
        </div>
      </div>

      {/* Offers List */}
      <div className="divide-y divide-gray-100 dark:divide-gray-800">
        {currentOffers.map((offer) => (
          <div key={offer.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50">
            {/* Merchant Info */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                  {offer.merchantAvatar}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-900 dark:text-white">
                      {offer.merchant}
                    </span>
                    {offer.verified && (
                      <span className="text-yellow-500">✓</span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                    <span>Trade: {offer.trades} Trades ({offer.completionRate}%)</span>
                    <span className="flex items-center gap-1">
                      <TrendingUp className="w-3 h-3" />
                      {offer.completionRate}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Price and Details */}
            <div className="flex items-end justify-between mb-3">
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                  Tk. {offer.price.toFixed(2)}
                  <span className="text-sm font-normal text-gray-500 dark:text-gray-400 ml-1">
                    /{selectedCrypto}
                  </span>
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Limit {offer.limit.min.toLocaleString()} - {offer.limit.max.toLocaleString()} {offer.currency}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Available {offer.available.toFixed(2)} {selectedCrypto}
                </div>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mb-2">
                  {offer.paymentMethods.map((method, index) => (
                    <span key={index} className="px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded">
                      {method}
                    </span>
                  ))}
                </div>
                <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {offer.responseTime}
                </div>
              </div>
            </div>

            {/* Action Button */}
            <button
              className={`w-full py-2.5 rounded-lg font-semibold transition-colors ${
                orderType === 'buy'
                  ? 'bg-green-500 hover:bg-green-600 text-white'
                  : 'bg-red-500 hover:bg-red-600 text-white'
              }`}
            >
              {orderType === 'buy' ? 'Buy' : 'Sell'}
            </button>
          </div>
        ))}
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
        <div className="flex justify-around items-center h-16">
          <button className="flex flex-col items-center justify-center flex-1 text-gray-900 dark:text-white">
            <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span className="text-xs">Home</span>
          </button>
          <button className="flex flex-col items-center justify-center flex-1 text-gray-500 dark:text-gray-400">
            <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <span className="text-xs">Orders</span>
          </button>
          <button className="flex flex-col items-center justify-center flex-1 text-gray-500 dark:text-gray-400">
            <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
            </svg>
            <span className="text-xs">Ads</span>
          </button>
          <button className="flex flex-col items-center justify-center flex-1 text-gray-500 dark:text-gray-400 relative">
            <div className="relative">
              <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <span className="absolute -top-1 -right-1 w-2 h-2 bg-yellow-400 rounded-full"></span>
            </div>
            <span className="text-xs">Chat</span>
          </button>
          <button className="flex flex-col items-center justify-center flex-1 text-gray-500 dark:text-gray-400">
            <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span className="text-xs">Profile</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default P2PMarketplace;