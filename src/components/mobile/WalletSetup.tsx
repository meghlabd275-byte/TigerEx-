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

import React, { useState } from 'react';
import { CheckCircle } from 'lucide-react';

interface WalletSetupProps {
  onWalletAction: (action: 'restore' | 'import') => void;
}

const WalletSetup: React.FC<WalletSetupProps> = ({ onWalletAction }) => {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    {
      title: 'Join to earn TigerEx Web3 exclusive airdrops',
      description: 'Connect your wallet to participate in exclusive Web3 opportunities',
      image: '🏁', // Checkered flag emoji like in screenshot
      showButtons: true
    },
    {
      title: 'All wallets, one account',
      description: 'Manage all your crypto wallets from a single, secure account',
      image: '🔐', // Lock with key emoji
      showButtons: true
    }
  ];

  const currentStepData = steps[currentStep];

  return (
    <div className="bg-white min-h-screen flex flex-col">
      {/* Header */}
      <header className="text-center py-6 border-b border-gray-200">
        <h1 className="text-xl font-semibold text-gray-900">TigerEx Wallet</h1>
      </header>

      {/* Content */}
      <div className="flex-1 flex flex-col justify-center items-center px-6">
        {/* Illustration */}
        <div className="w-32 h-32 bg-gray-100 rounded-full flex items-center justify-center mb-8">
          <div className="text-6xl">{currentStepData.image}</div>
        </div>

        {/* Title */}
        <h2 className="text-xl font-semibold text-gray-900 text-center mb-4 max-w-sm">
          {currentStepData.title}
        </h2>

        {/* Description */}
        <p className="text-gray-600 text-center mb-8 max-w-sm">
          {currentStepData.description}
        </p>

        {/* Progress Dots */}
        <div className="flex space-x-2 mb-8">
          {steps.map((_, index) => (
            <div
              key={index}
              className={`w-2 h-2 rounded-full ${
                index === currentStep ? 'bg-yellow-500' : 'bg-gray-300'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Bottom Section */}
      <div className="p-6 space-y-4">
        {/* Terms */}
        <p className="text-xs text-gray-500 text-center">
          By using the TigerEx Wallet Services, you agree to the{' '}
          <button className="text-yellow-600 underline">
            TigerEx Wallet Terms of Use
          </button>
        </p>

        {/* Action Buttons */}
        {currentStepData.showButtons && (
          <div className="space-y-3">
            <button
              onClick={() => onWalletAction('restore')}
              className="w-full bg-yellow-500 text-white py-4 rounded-lg font-medium hover:bg-yellow-600 transition-colors"
            >
              Restore Wallet
            </button>
            <button
              onClick={() => onWalletAction('import')}
              className="w-full bg-gray-200 text-gray-700 py-4 rounded-lg font-medium hover:bg-gray-300 transition-colors"
            >
              Import Wallet
            </button>
          </div>
        )}

        {/* Navigation */}
        {currentStep < steps.length - 1 && (
          <button
            onClick={() => setCurrentStep(currentStep + 1)}
            className="w-full text-yellow-600 font-medium py-2"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
};

export default WalletSetup;