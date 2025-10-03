import React, { useState } from 'react';
import { ArrowDown, Settings, RefreshCw, Info } from 'lucide-react';
import { useWallet } from '../../contexts/WalletContext';

interface Token {
  symbol: string;
  name: string;
  balance: number;
  icon: string;
  address: string;
}

const DEXSwap: React.FC = () => {
  const { wallet, isConnected } = useWallet();
  const [fromToken, setFromToken] = useState<Token>({
    symbol: 'ETH',
    name: 'Ethereum',
    balance: 0.5,
    icon: '◆',
    address: '0x...',
  });
  const [toToken, setToToken] = useState<Token>({
    symbol: 'USDT',
    name: 'Tether USD',
    balance: 1000,
    icon: '₮',
    address: '0x...',
  });
  const [fromAmount, setFromAmount] = useState('');
  const [toAmount, setToAmount] = useState('');
  const [slippage, setSlippage] = useState(0.5);

  const tokens: Token[] = [
    { symbol: 'ETH', name: 'Ethereum', balance: 0.5, icon: '◆', address: '0x...' },
    { symbol: 'USDT', name: 'Tether USD', balance: 1000, icon: '₮', address: '0x...' },
    { symbol: 'BTC', name: 'Bitcoin', balance: 0.01, icon: '₿', address: '0x...' },
    { symbol: 'BNB', name: 'BNB', balance: 2.5, icon: '🔶', address: '0x...' },
    { symbol: 'USDC', name: 'USD Coin', balance: 500, icon: '💵', address: '0x...' },
  ];

  const handleSwap = () => {
    // Swap logic here
    console.log('Swapping', fromAmount, fromToken.symbol, 'to', toToken.symbol);
  };

  const switchTokens = () => {
    const temp = fromToken;
    setFromToken(toToken);
    setToToken(temp);
    
    const tempAmount = fromAmount;
    setFromAmount(toAmount);
    setToAmount(tempAmount);
  };

  const calculateToAmount = (amount: string) => {
    // Simple mock calculation (in production, use real DEX pricing)
    const rate = 2000; // 1 ETH = 2000 USDT
    const calculated = parseFloat(amount) * rate;
    return calculated.toFixed(2);
  };

  const handleFromAmountChange = (value: string) => {
    setFromAmount(value);
    if (value) {
      setToAmount(calculateToAmount(value));
    } else {
      setToAmount('');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-white">Swap</h1>
          <div className="flex items-center gap-2">
            <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
              <RefreshCw className="w-5 h-5 text-white" />
            </button>
            <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
              <Settings className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>

        {/* Swap Card */}
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-4 border border-gray-700">
          {/* From Token */}
          <div className="bg-gray-900/50 rounded-xl p-4 mb-2">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-400">From</span>
              <span className="text-sm text-gray-400">
                Balance: {fromToken.balance} {fromToken.symbol}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="number"
                value={fromAmount}
                onChange={(e) => handleFromAmountChange(e.target.value)}
                placeholder="0.0"
                className="flex-1 bg-transparent text-3xl text-white outline-none"
              />
              <button className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-xl transition-colors">
                <span className="text-2xl">{fromToken.icon}</span>
                <span className="text-white font-semibold">{fromToken.symbol}</span>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            <div className="mt-2 text-sm text-gray-500">
              ≈ ${fromAmount ? (parseFloat(fromAmount) * 2000).toFixed(2) : '0.00'}
            </div>
          </div>

          {/* Switch Button */}
          <div className="flex justify-center -my-2 relative z-10">
            <button
              onClick={switchTokens}
              className="bg-gray-800 hover:bg-gray-700 p-2 rounded-xl border-4 border-gray-800/50 transition-colors"
            >
              <ArrowDown className="w-5 h-5 text-white" />
            </button>
          </div>

          {/* To Token */}
          <div className="bg-gray-900/50 rounded-xl p-4 mt-2">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-400">To</span>
              <span className="text-sm text-gray-400">
                Balance: {toToken.balance} {toToken.symbol}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="number"
                value={toAmount}
                readOnly
                placeholder="0.0"
                className="flex-1 bg-transparent text-3xl text-white outline-none"
              />
              <button className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-xl transition-colors">
                <span className="text-2xl">{toToken.icon}</span>
                <span className="text-white font-semibold">{toToken.symbol}</span>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            <div className="mt-2 text-sm text-gray-500">
              ≈ ${toAmount || '0.00'}
            </div>
          </div>

          {/* Swap Details */}
          {fromAmount && toAmount && (
            <div className="mt-4 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Rate</span>
                <span className="text-white">
                  1 {fromToken.symbol} = {(parseFloat(toAmount) / parseFloat(fromAmount)).toFixed(2)} {toToken.symbol}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400 flex items-center gap-1">
                  Slippage Tolerance
                  <Info className="w-3 h-3" />
                </span>
                <span className="text-white">{slippage}%</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Network Fee</span>
                <span className="text-white">~$2.50</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Minimum Received</span>
                <span className="text-white">
                  {(parseFloat(toAmount) * (1 - slippage / 100)).toFixed(2)} {toToken.symbol}
                </span>
              </div>
            </div>
          )}

          {/* Swap Button */}
          <button
            onClick={handleSwap}
            disabled={!fromAmount || !isConnected}
            className="w-full mt-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:from-gray-700 disabled:to-gray-700 disabled:text-gray-500 text-white font-bold py-4 rounded-xl transition-all"
          >
            {!isConnected ? 'Connect Wallet' : !fromAmount ? 'Enter Amount' : 'Swap'}
          </button>
        </div>

        {/* Info Card */}
        <div className="mt-4 bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
          <div className="flex gap-3">
            <Info className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-300">
              <p className="font-semibold mb-1">DEX Trading</p>
              <p>You're trading on a decentralized exchange. Your wallet controls your funds at all times.</p>
            </div>
          </div>
        </div>

        {/* Wallet Info */}
        {isConnected && wallet && (
          <div className="mt-4 bg-gray-800/50 backdrop-blur-lg rounded-xl p-4 border border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Connected Wallet</span>
              <span className="text-sm text-white font-mono">
                {wallet.address.slice(0, 6)}...{wallet.address.slice(-4)}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DEXSwap;