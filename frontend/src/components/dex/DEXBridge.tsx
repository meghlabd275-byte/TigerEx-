import React, { useState } from 'react';
import { ArrowDown, Info, AlertCircle } from 'lucide-react';

interface Network {
  id: string;
  name: string;
  icon: string;
  nativeCurrency: string;
}

const DEXBridge: React.FC = () => {
  const [fromNetwork, setFromNetwork] = useState<Network>({
    id: 'ethereum',
    name: 'Ethereum',
    icon: '◆',
    nativeCurrency: 'ETH'
  });
  const [toNetwork, setToNetwork] = useState<Network>({
    id: 'bsc',
    name: 'BNB Chain',
    icon: '🔶',
    nativeCurrency: 'BNB'
  });
  const [amount, setAmount] = useState('');
  const [selectedToken, setSelectedToken] = useState('USDT');

  const networks: Network[] = [
    { id: 'ethereum', name: 'Ethereum', icon: '◆', nativeCurrency: 'ETH' },
    { id: 'bsc', name: 'BNB Chain', icon: '🔶', nativeCurrency: 'BNB' },
    { id: 'polygon', name: 'Polygon', icon: '🟣', nativeCurrency: 'MATIC' },
    { id: 'arbitrum', name: 'Arbitrum', icon: '🔵', nativeCurrency: 'ETH' },
    { id: 'optimism', name: 'Optimism', icon: '🔴', nativeCurrency: 'ETH' },
  ];

  const switchNetworks = () => {
    const temp = fromNetwork;
    setFromNetwork(toNetwork);
    setToNetwork(temp);
  };

  const estimatedFee = amount ? (parseFloat(amount) * 0.001).toFixed(4) : '0';
  const estimatedTime = '2-5 minutes';

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-white">Bridge</h1>
          <button className="text-gray-400 hover:text-white">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
        </div>

        {/* Bridge Card */}
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-4 border border-gray-700">
          {/* From Network */}
          <div className="bg-gray-900/50 rounded-xl p-4 mb-2">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-400">From</span>
              <button className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded-lg transition-colors">
                <span className="text-xl">{fromNetwork.icon}</span>
                <span className="text-white font-semibold">{fromNetwork.name}</span>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="0.0"
                className="flex-1 bg-transparent text-3xl text-white outline-none"
              />
              <button className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 px-3 py-2 rounded-lg transition-colors">
                <span className="text-xl">₮</span>
                <span className="text-white font-semibold">{selectedToken}</span>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            <div className="mt-2 text-sm text-gray-500">
              Balance: 0 {selectedToken}
            </div>
          </div>

          {/* Switch Button */}
          <div className="flex justify-center -my-2 relative z-10">
            <button
              onClick={switchNetworks}
              className="bg-gray-800 hover:bg-gray-700 p-2 rounded-xl border-4 border-gray-800/50 transition-colors"
            >
              <ArrowDown className="w-5 h-5 text-white" />
            </button>
          </div>

          {/* To Network */}
          <div className="bg-gray-900/50 rounded-xl p-4 mt-2">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-400">To</span>
              <button className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded-lg transition-colors">
                <span className="text-xl">{toNetwork.icon}</span>
                <span className="text-white font-semibold">{toNetwork.name}</span>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            <div className="text-3xl text-white font-semibold">
              {amount || '0.0'}
            </div>
            <div className="mt-2 text-sm text-gray-500">
              You will receive ≈ {amount || '0'} {selectedToken}
            </div>
          </div>

          {/* Bridge Details */}
          {amount && (
            <div className="mt-4 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Bridge Fee</span>
                <span className="text-white">{estimatedFee} {selectedToken}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Estimated Time</span>
                <span className="text-white">{estimatedTime}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Route</span>
                <span className="text-white">Optimized</span>
              </div>
            </div>
          )}

          {/* Bridge Button */}
          <button
            disabled={!amount}
            className="w-full mt-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:from-gray-700 disabled:to-gray-700 disabled:text-gray-500 text-white font-bold py-4 rounded-xl transition-all"
          >
            {!amount ? 'Enter Amount' : 'Bridge Tokens'}
          </button>
        </div>

        {/* Info Cards */}
        <div className="mt-4 space-y-3">
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
            <div className="flex gap-3">
              <Info className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-blue-300">
                <p className="font-semibold mb-1">Cross-Chain Bridge</p>
                <p>
                  Transfer tokens between different blockchain networks securely. Always verify the destination address.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4">
            <div className="flex gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-yellow-300">
                <p className="font-semibold mb-1">Important</p>
                <p>
                  Bridge transactions are irreversible. Double-check all details before confirming.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Supported Networks */}
        <div className="mt-6">
          <h3 className="text-white font-semibold mb-3">Supported Networks</h3>
          <div className="grid grid-cols-5 gap-2">
            {networks.map((network) => (
              <button
                key={network.id}
                className="bg-gray-800/50 hover:bg-gray-700/50 rounded-lg p-3 flex flex-col items-center gap-2 transition-colors"
              >
                <span className="text-2xl">{network.icon}</span>
                <span className="text-xs text-gray-400">{network.name}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DEXBridge;