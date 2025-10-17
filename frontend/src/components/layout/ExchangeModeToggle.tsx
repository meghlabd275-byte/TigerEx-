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
import { useWallet } from '../../contexts/WalletContext';
import { Wallet, Building2, AlertCircle } from 'lucide-react';

const ExchangeModeToggle: React.FC = () => {
  const { wallet, isConnected, exchangeMode, switchExchangeMode, disconnectWallet } = useWallet();
  const [showModal, setShowModal] = React.useState(false);

  const handleModeSwitch = (mode: 'cex' | 'dex') => {
    try {
      switchExchangeMode(mode);
    } catch (error: any) {
      setShowModal(true);
    }
  };

  return (
    <>
      <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-4 py-3">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Trading Mode</h2>
          {isConnected && wallet && (
            <button
              onClick={disconnectWallet}
              className="text-sm text-red-500 hover:text-red-600"
            >
              Disconnect
            </button>
          )}
        </div>

        <div className="grid grid-cols-2 gap-3">
          {/* CEX Mode */}
          <button
            onClick={() => handleModeSwitch('cex')}
            className={`p-4 rounded-lg border-2 transition-all ${
              exchangeMode === 'cex'
                ? 'border-yellow-400 bg-yellow-50 dark:bg-yellow-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            }`}
          >
            <div className="flex flex-col items-center gap-2">
              <div
                className={`w-12 h-12 rounded-full flex items-center justify-center ${
                  exchangeMode === 'cex'
                    ? 'bg-yellow-400'
                    : 'bg-gray-200 dark:bg-gray-700'
                }`}
              >
                <Building2
                  className={`w-6 h-6 ${
                    exchangeMode === 'cex'
                      ? 'text-gray-900'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}
                />
              </div>
              <div className="text-center">
                <div
                  className={`font-semibold ${
                    exchangeMode === 'cex'
                      ? 'text-gray-900 dark:text-white'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}
                >
                  CEX Mode
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Centralized Exchange
                </div>
              </div>
            </div>
          </button>

          {/* DEX Mode */}
          <button
            onClick={() => handleModeSwitch('dex')}
            className={`p-4 rounded-lg border-2 transition-all ${
              exchangeMode === 'dex'
                ? 'border-purple-400 bg-purple-50 dark:bg-purple-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            }`}
          >
            <div className="flex flex-col items-center gap-2">
              <div
                className={`w-12 h-12 rounded-full flex items-center justify-center ${
                  exchangeMode === 'dex'
                    ? 'bg-purple-400'
                    : 'bg-gray-200 dark:bg-gray-700'
                }`}
              >
                <Wallet
                  className={`w-6 h-6 ${
                    exchangeMode === 'dex'
                      ? 'text-white'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}
                />
              </div>
              <div className="text-center">
                <div
                  className={`font-semibold ${
                    exchangeMode === 'dex'
                      ? 'text-gray-900 dark:text-white'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}
                >
                  DEX Mode
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Decentralized Exchange
                </div>
              </div>
            </div>
          </button>
        </div>

        {/* Wallet Status */}
        {isConnected && wallet && (
          <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-green-700 dark:text-green-400 font-medium">
                Wallet Connected
              </span>
            </div>
            <div className="text-xs text-green-600 dark:text-green-500 mt-1 font-mono">
              {wallet.address.slice(0, 10)}...{wallet.address.slice(-8)}
            </div>
          </div>
        )}

        {/* Mode Description */}
        <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
          {exchangeMode === 'cex' ? (
            <p>
              <strong>CEX Mode:</strong> Trade with TigerEx's centralized order book. Fast execution and deep liquidity.
            </p>
          ) : (
            <p>
              <strong>DEX Mode:</strong> Trade directly from your wallet. You maintain full control of your funds.
            </p>
          )}
        </div>
      </div>

      {/* Modal for DEX requirement */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6">
            <div className="flex items-start gap-3 mb-4">
              <div className="w-10 h-10 bg-yellow-100 dark:bg-yellow-900/30 rounded-full flex items-center justify-center flex-shrink-0">
                <AlertCircle className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Wallet Required for DEX
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  To use DEX mode, you need to connect a wallet first. Would you like to create or import a wallet now?
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  setShowModal(false);
                  // Navigate to wallet setup
                  window.location.href = '/wallet-setup';
                }}
                className="flex-1 px-4 py-2 bg-yellow-400 hover:bg-yellow-500 text-gray-900 rounded-lg font-semibold transition-colors"
              >
                Setup Wallet
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ExchangeModeToggle;