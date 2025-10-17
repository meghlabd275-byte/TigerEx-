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
import { ChevronRight, Wallet, TrendingUp, BarChart3, Coins, Gift, FileText } from 'lucide-react';

interface WalletType {
  id: string;
  name: string;
  balance: string;
  currency: string;
  icon: React.ReactNode;
  description?: string;
  isActive?: boolean;
}

interface WalletSelectorProps {
  onSelectWallet: (wallet: WalletType) => void;
  selectedWallet?: WalletType;
  title?: string;
}

const WalletSelector: React.FC<WalletSelectorProps> = ({
  onSelectWallet,
  selectedWallet,
  title = "Select a wallet"
}) => {
  const wallets: WalletType[] = [
    {
      id: 'usd-futures',
      name: 'USD©-M Futures',
      balance: '0',
      currency: 'BTC',
      icon: <FileText className="w-5 h-5 text-gray-600" />,
      isActive: true
    },
    {
      id: 'coin-futures',
      name: 'COIN-M Futures',
      balance: '0',
      currency: 'BTC',
      icon: <Coins className="w-5 h-5 text-gray-600" />
    },
    {
      id: 'cross-margin',
      name: 'Cross Margin',
      balance: '0',
      currency: 'BTC',
      icon: <BarChart3 className="w-5 h-5 text-gray-600" />
    },
    {
      id: 'spot-wallet',
      name: 'Spot Wallet',
      balance: '0',
      currency: 'BTC',
      icon: <Wallet className="w-5 h-5 text-gray-600" />
    },
    {
      id: 'earn-flexible',
      name: 'Earn-Flexible Assets',
      balance: '0',
      currency: 'BTC',
      icon: <TrendingUp className="w-5 h-5 text-gray-600" />
    },
    {
      id: 'options',
      name: 'Options',
      balance: '0',
      currency: 'BTC',
      icon: <Gift className="w-5 h-5 text-gray-400" />,
      isActive: false
    }
  ];

  return (
    <div className="bg-white rounded-t-3xl p-4 max-h-[80vh] overflow-y-auto">
      {/* Handle */}
      <div className="w-12 h-1 bg-gray-300 rounded-full mx-auto mb-4"></div>
      
      {/* Title */}
      <h2 className="text-lg font-semibold text-gray-900 mb-4">{title}</h2>
      
      {/* Wallet List */}
      <div className="space-y-2">
        {wallets.map((wallet) => (
          <button
            key={wallet.id}
            onClick={() => onSelectWallet(wallet)}
            disabled={!wallet.isActive}
            className={`w-full p-4 rounded-xl border transition-all ${
              selectedWallet?.id === wallet.id
                ? 'border-yellow-500 bg-yellow-50'
                : wallet.isActive
                ? 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                : 'border-gray-100 bg-gray-50 opacity-60'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {wallet.icon}
                <div className="text-left">
                  <div className="font-medium text-gray-900">{wallet.name}</div>
                  <div className="text-sm text-gray-500">
                    {wallet.balance} {wallet.currency}
                  </div>
                </div>
              </div>
              {wallet.isActive && (
                <ChevronRight className="w-5 h-5 text-gray-400" />
              )}
              {!wallet.isActive && (
                <span className="text-xs text-gray-400 bg-gray-200 px-2 py-1 rounded">
                  Inactive
                </span>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default WalletSelector;