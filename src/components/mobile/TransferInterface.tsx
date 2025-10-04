import React, { useState } from 'react';
import { ChevronRight, ChevronDown, RefreshCw } from 'lucide-react';
import WalletSelector from './WalletSelector';

interface TransferInterfaceProps {
  onTransfer: (data: any) => void;
}

const TransferInterface: React.FC<TransferInterfaceProps> = ({ onTransfer }) => {
  const [fromWallet, setFromWallet] = useState({
    id: 'funding',
    name: 'Funding',
    balance: '0.00000000',
    currency: 'BTC'
  });
  
  const [toWallet, setToWallet] = useState({
    id: 'usd-futures',
    name: 'USD©-M Futures',
    balance: '0',
    currency: 'BTC'
  });

  const [selectedCoin, setSelectedCoin] = useState({
    symbol: 'BTC',
    name: 'Bitcoin',
    icon: '₿'
  });

  const [amount, setAmount] = useState('');
  const [showWalletSelector, setShowWalletSelector] = useState(false);
  const [selectorType, setSelectorType] = useState<'from' | 'to'>('from');

  const handleWalletSelect = (wallet: any) => {
    if (selectorType === 'from') {
      setFromWallet(wallet);
    } else {
      setToWallet(wallet);
    }
    setShowWalletSelector(false);
  };

  const handleSwapWallets = () => {
    const temp = fromWallet;
    setFromWallet(toWallet);
    setToWallet(temp);
  };

  const handleConfirmTransfer = () => {
    if (!amount || parseFloat(amount) <= 0) {
      alert('Please enter a valid amount');
      return;
    }

    onTransfer({
      from: fromWallet,
      to: toWallet,
      coin: selectedCoin,
      amount: parseFloat(amount)
    });
  };

  return (
    <div className="bg-white min-h-screen">
      {/* Transfer Form */}
      <div className="p-4 space-y-4">
        {/* From Section */}
        <div className="space-y-2">
          <label className="text-sm text-gray-600">From</label>
          <button
            onClick={() => {
              setSelectorType('from');
              setShowWalletSelector(true);
            }}
            className="w-full p-4 bg-gray-50 rounded-lg flex items-center justify-between"
          >
            <span className="font-medium text-gray-900">{fromWallet.name}</span>
            <ChevronRight className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Swap Button */}
        <div className="flex justify-center">
          <button
            onClick={handleSwapWallets}
            className="p-2 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
          >
            <RefreshCw className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* To Section */}
        <div className="space-y-2">
          <label className="text-sm text-gray-600">To</label>
          <button
            onClick={() => {
              setSelectorType('to');
              setShowWalletSelector(true);
            }}
            className="w-full p-4 bg-gray-50 rounded-lg flex items-center justify-between"
          >
            <span className="font-medium text-gray-900">{toWallet.name}</span>
            <ChevronRight className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Coin Selection */}
        <div className="space-y-2">
          <label className="text-sm text-gray-600">Coin</label>
          <button className="w-full p-4 bg-gray-50 rounded-lg flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center text-white font-bold">
                {selectedCoin.icon}
              </div>
              <span className="font-medium text-gray-900">
                {selectedCoin.symbol} {selectedCoin.name}
              </span>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Amount Input */}
        <div className="space-y-2">
          <label className="text-sm text-gray-600">Amount</label>
          <div className="relative">
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.00000000"
              className="w-full p-4 bg-gray-50 rounded-lg text-right text-lg font-medium focus:outline-none focus:ring-2 focus:ring-yellow-500"
            />
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
              <span className="text-gray-600 font-medium">{selectedCoin.symbol}</span>
              <button className="text-yellow-600 font-medium text-sm">Max</button>
            </div>
          </div>
          <div className="text-sm text-gray-500">
            Available {fromWallet.balance} {selectedCoin.symbol}
          </div>
        </div>

        {/* Error Message */}
        {parseFloat(amount) > 0 && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">
              No amount available to transfer, please select another coin.
            </p>
          </div>
        )}
      </div>

      {/* Confirm Button */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-gray-200">
        <button
          onClick={handleConfirmTransfer}
          disabled={!amount || parseFloat(amount) <= 0}
          className={`w-full py-4 rounded-lg font-medium transition-colors ${
            amount && parseFloat(amount) > 0
              ? 'bg-yellow-500 text-white hover:bg-yellow-600'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }`}
        >
          Confirm Transfer
        </button>
      </div>

      {/* Wallet Selector Modal */}
      {showWalletSelector && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end">
          <div className="w-full">
            <WalletSelector
              onSelectWallet={handleWalletSelect}
              title={`Select ${selectorType} wallet`}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default TransferInterface;