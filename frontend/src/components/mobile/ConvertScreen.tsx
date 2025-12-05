'use client';

import React, { useState } from 'react';
import { Search, X } from 'lucide-react';

interface CryptoCurrency {
  name: string;
  ticker: string;
  icon: string;
  isAlpha?: boolean;
}

const mockCurrencies: CryptoCurrency[] = [
  { name: '4 (BSC)', ticker: '', icon: '/path/to/icon.png' },
  { name: 'Semantic Layer (BSC)', ticker: '42', icon: '/path/to/icon.png', isAlpha: true },
  { name: 'Vulta', ticker: 'A', icon: '/path/to/icon.png' },
  { name: 'Arena-Z', ticker: 'A2Z', icon: '/path/to/icon.png' },
  { name: 'ARAI (BSC)', ticker: 'AA', icon: '/path/to/icon.png', isAlpha: true },
  { name: 'Aave', ticker: 'AAVE', icon: '/path/to/icon.png' },
  { name: 'AB (BSC)', ticker: 'AB', icon: '/path/to/icon.png', isAlpha: true },
  { name: 'ACA', ticker: 'ACA', icon: '/path/to/icon.png' },
];

export default function ConvertScreen() {
  const [isModalOpen, setIsModalOpen] = useState(true);
  const [selectedCoinType, setSelectedCoinType] = useState<'single' | 'multi'>('single');

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Header */}
      <header className="bg-white px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          {['Convert', 'Spot', 'Margin', 'P2P', 'Alpha'].map((tab) => (
            <button
              key={tab}
              className={`py-2 text-sm font-semibold ${
                tab === 'Convert'
                  ? 'text-black border-b-2 border-yellow-500'
                  : 'text-gray-500'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
        <button className="text-gray-600">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
        </button>
      </header>

      {/* Promotion Banner */}
      <div className="bg-gray-100 p-3 mx-4 my-4 rounded-lg">
        <div className="flex items-center gap-2 text-sm text-gray-800">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 12V8H6V4H4v4H2v12h10v-4h8v-4h-2zm-6 0v4H4v-4h10z"/><path d="M18 4h-2v4h2V4z"/><path d="M6 12v4H4v-4H2v- металл/svg>
          <span>Earn Rebates with Convert Recurring from just $1!</span>
        </div>
      </div>


      {/* Main Content - Placeholder for when modal is closed */}
      <div className="p-4">
        <button onClick={openModal} className="px-4 py-2 bg-blue-500 text-white rounded">
          Select Coin
        </button>
      </div>


      {/* "From" Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-end">
          <div className="w-full bg-white rounded-t-2xl h-[90vh] flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">From</h2>
                <button onClick={closeModal}>
                  <X size={24} className="text-gray-500" />
                </button>
              </div>
            </div>

            <div className="p-4">
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setSelectedCoinType('single')}
                  className={`flex-1 py-2 text-center rounded-lg text-sm font-medium ${selectedCoinType === 'single' ? 'bg-white shadow' : 'text-gray-600'}`}>
                  Single Coin
                </button>
                <button
                  onClick={() => setSelectedCoinType('multi')}
                  className={`flex-1 py-2 text-center rounded-lg text-sm font-medium ${selectedCoinType === 'multi' ? 'bg-white shadow' : 'text-gray-600'}`}>
                  Multi Coins
                </button>
              </div>
            </div>

            <div className="px-4 pb-4">
              <div className="relative">
                <Search size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search"
                  className="w-full bg-gray-100 border-none rounded-lg pl-10 pr-4 py-3 focus:outline-none focus:ring-2 focus:ring-yellow-500"
                />
              </div>
            </div>

            <div className="px-4 flex items-center gap-4 text-sm">
              {['All', 'Alpha', 'New', 'Hot'].map(filter => (
                <button key={filter} className={`py-1 ${filter === 'All' ? 'text-black font-semibold' : 'text-gray-500'}`}>
                  {filter}
                </button>
              ))}
            </div>

            <div className="flex-1 overflow-y-auto px-4 pt-4">
              {mockCurrencies.map((coin, index) => (
                <div key={index} className="flex items-center gap-4 py-3">
                  <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{coin.ticker}</span>
                      {coin.isAlpha && (
                        <span className="bg-yellow-100 text-yellow-600 text-xs font-semibold px-2 py-0.5 rounded">
                          Alpha
                        </span>
                      )}
                    </div>
                    <p className="text-gray-500 text-sm">{coin.name}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}