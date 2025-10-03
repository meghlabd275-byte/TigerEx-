import React, { useState } from 'react';
import { useWallet } from '../../contexts/WalletContext';

const Web3Onboarding: React.FC = () => {
  const { importWallet, connectWallet } = useWallet();
  const [currentSlide, setCurrentSlide] = useState(0);
  const [agreedToTerms, setAgreedToTerms] = useState(false);

  const slides = [
    {
      icon: '🪂',
      title: 'Join to earn Binance Web3 exclusive airdrops',
      description: 'Get exclusive access to Web3 airdrops and rewards'
    },
    {
      icon: '🔐',
      title: 'Your keys, your crypto',
      description: 'Full control over your assets with self-custody wallet'
    },
    {
      icon: '🌐',
      title: 'Access the decentralized web',
      description: 'Connect to DApps and explore the Web3 ecosystem'
    }
  ];

  const handleRestoreWallet = () => {
    // Navigate to restore wallet flow
    window.location.href = '/wallet-setup?mode=import';
  };

  const handleImportWallet = () => {
    // Navigate to import wallet flow
    window.location.href = '/wallet-setup?mode=import';
  };

  const nextSlide = () => {
    if (currentSlide < slides.length - 1) {
      setCurrentSlide(currentSlide + 1);
    }
  };

  const prevSlide = () => {
    if (currentSlide > 0) {
      setCurrentSlide(currentSlide - 1);
    }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-800">
        <button 
          onClick={() => window.history.back()}
          className="p-2"
        >
          <svg className="w-6 h-6 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
          Binance Wallet
        </h1>
        <div className="w-10"></div>
      </div>

      {/* Carousel */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-8">
        <div className="w-full max-w-md">
          {/* Icon */}
          <div className="flex justify-center mb-8">
            <div className="w-48 h-48 flex items-center justify-center">
              <div className="relative">
                {/* Parachute illustration */}
                <div className="text-9xl">
                  {slides[currentSlide].icon}
                </div>
              </div>
            </div>
          </div>

          {/* Title */}
          <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-white mb-4">
            {slides[currentSlide].title}
          </h2>

          {/* Description */}
          <p className="text-center text-gray-600 dark:text-gray-400 mb-8">
            {slides[currentSlide].description}
          </p>

          {/* Slide Indicators */}
          <div className="flex justify-center gap-2 mb-12">
            {slides.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentSlide(index)}
                className={`h-2 rounded-full transition-all ${
                  index === currentSlide
                    ? 'w-8 bg-yellow-400'
                    : 'w-2 bg-gray-300 dark:bg-gray-600'
                }`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="px-6 pb-8">
        {/* Terms Agreement */}
        <div className="mb-6">
          <p className="text-sm text-center text-gray-600 dark:text-gray-400">
            By using the Binance Wallet Services, you agree to the{' '}
            <a href="#" className="text-yellow-500 hover:text-yellow-600">
              Binance Wallet Terms of Use
            </a>
          </p>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={handleRestoreWallet}
            className="w-full bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-semibold py-4 rounded-lg transition-colors"
          >
            Restore Wallet
          </button>
          <button
            onClick={handleImportWallet}
            className="w-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-900 dark:text-white font-semibold py-4 rounded-lg transition-colors"
          >
            Import Wallet
          </button>
        </div>
      </div>
    </div>
  );
};

export default Web3Onboarding;