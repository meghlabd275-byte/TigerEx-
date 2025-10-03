import React, { useState } from 'react';
import { Lock, Unlock, TrendingUp, Clock, Info } from 'lucide-react';

interface StakingPool {
  id: string;
  token: string;
  icon: string;
  apy: number;
  lockPeriod: string;
  minStake: number;
  totalStaked: string;
  myStake?: number;
  rewards?: number;
  status: 'active' | 'ended' | 'upcoming';
}

const DEXStaking: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'active' | 'my'>('active');
  const [selectedPool, setSelectedPool] = useState<StakingPool | null>(null);
  const [stakeAmount, setStakeAmount] = useState('');

  const stakingPools: StakingPool[] = [
    {
      id: '1',
      token: 'TIGER',
      icon: '🐯',
      apy: 45.5,
      lockPeriod: '30 days',
      minStake: 100,
      totalStaked: '$5.2M',
      myStake: 1000,
      rewards: 125.50,
      status: 'active'
    },
    {
      id: '2',
      token: 'ETH',
      icon: '◆',
      apy: 12.3,
      lockPeriod: '90 days',
      minStake: 0.1,
      totalStaked: '$12.8M',
      myStake: 2.5,
      rewards: 0.35,
      status: 'active'
    },
    {
      id: '3',
      token: 'BNB',
      icon: '🔶',
      apy: 28.7,
      lockPeriod: '60 days',
      minStake: 1,
      totalStaked: '$8.5M',
      status: 'active'
    },
    {
      id: '4',
      token: 'USDT',
      icon: '₮',
      apy: 8.5,
      lockPeriod: 'Flexible',
      minStake: 100,
      totalStaked: '$25.3M',
      status: 'active'
    }
  ];

  const myStakes = stakingPools.filter(pool => pool.myStake);
  const displayPools = activeTab === 'active' ? stakingPools : myStakes;

  const handleStake = () => {
    if (selectedPool && stakeAmount) {
      console.log('Staking', stakeAmount, selectedPool.token);
      setSelectedPool(null);
      setStakeAmount('');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
        <div className="flex items-center justify-between px-4 py-3">
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">
            Staking
          </h1>
          <button className="text-sm text-yellow-500 hover:text-yellow-600 font-medium">
            History
          </button>
        </div>

        {/* Tabs */}
        <div className="flex px-4">
          <button
            onClick={() => setActiveTab('active')}
            className={`px-4 py-3 font-medium border-b-2 transition-colors ${
              activeTab === 'active'
                ? 'border-yellow-400 text-gray-900 dark:text-white'
                : 'border-transparent text-gray-500 dark:text-gray-400'
            }`}
          >
            Active Pools
          </button>
          <button
            onClick={() => setActiveTab('my')}
            className={`px-4 py-3 font-medium border-b-2 transition-colors ${
              activeTab === 'my'
                ? 'border-yellow-400 text-gray-900 dark:text-white'
                : 'border-transparent text-gray-500 dark:text-gray-400'
            }`}
          >
            My Stakes ({myStakes.length})
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      {activeTab === 'my' && myStakes.length > 0 && (
        <div className="bg-gradient-to-r from-yellow-400 to-orange-500 mx-4 mt-4 rounded-lg p-6 text-white">
          <div className="text-sm opacity-90 mb-1">Total Staked Value</div>
          <div className="text-3xl font-bold mb-4">
            $
            {myStakes
              .reduce((acc, pool) => acc + (pool.myStake || 0) * 100, 0)
              .toFixed(2)}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm opacity-90 mb-1">Total Rewards</div>
              <div className="text-xl font-semibold">
                $
                {myStakes
                  .reduce((acc, pool) => acc + (pool.rewards || 0) * 100, 0)
                  .toFixed(2)}
              </div>
            </div>
            <div>
              <div className="text-sm opacity-90 mb-1">Avg APY</div>
              <div className="text-xl font-semibold">
                {(
                  myStakes.reduce((acc, pool) => acc + pool.apy, 0) /
                  myStakes.length
                ).toFixed(1)}
                %
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Pool List */}
      <div className="px-4 mt-4 space-y-3">
        {displayPools.map((pool) => (
          <div
            key={pool.id}
            className="bg-white dark:bg-gray-800 rounded-lg p-4 hover:shadow-lg transition-shadow"
          >
            {/* Pool Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-2xl">
                  {pool.icon}
                </div>
                <div>
                  <div className="font-semibold text-gray-900 dark:text-white text-lg">
                    {pool.token}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                    <Clock className="w-4 h-4" />
                    {pool.lockPeriod}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-green-500">
                  {pool.apy}%
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  APY
                </div>
              </div>
            </div>

            {/* Pool Info */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                  Min Stake
                </div>
                <div className="text-sm font-semibold text-gray-900 dark:text-white">
                  {pool.minStake} {pool.token}
                </div>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                  Total Staked
                </div>
                <div className="text-sm font-semibold text-gray-900 dark:text-white">
                  {pool.totalStaked}
                </div>
              </div>
            </div>

            {/* My Stake Info */}
            {pool.myStake && (
              <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3 mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    My Stake
                  </span>
                  <span className="text-sm font-semibold text-gray-900 dark:text-white">
                    {pool.myStake} {pool.token}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Pending Rewards
                  </span>
                  <span className="text-sm font-semibold text-green-500">
                    +{pool.rewards} {pool.token}
                  </span>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-2">
              {pool.myStake ? (
                <>
                  <button className="flex-1 bg-green-500 hover:bg-green-600 text-white font-semibold py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2">
                    <TrendingUp className="w-4 h-4" />
                    Claim Rewards
                  </button>
                  <button className="flex-1 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-semibold py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2">
                    <Unlock className="w-4 h-4" />
                    Unstake
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setSelectedPool(pool)}
                  className="w-full bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-semibold py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <Lock className="w-4 h-4" />
                  Stake Now
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Info Banner */}
      <div className="mx-4 mt-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex gap-3">
          <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-700 dark:text-blue-300">
            <p className="font-semibold mb-1">About Staking</p>
            <p>
              Lock your tokens to earn rewards. Longer lock periods typically offer higher APY. Rewards are automatically compounded.
            </p>
          </div>
        </div>
      </div>

      {/* Stake Modal */}
      {selectedPool && (
        <div className="fixed inset-0 bg-black/50 flex items-end justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-t-2xl w-full max-w-md p-6 animate-slide-up">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                Stake {selectedPool.token}
              </h3>
              <button
                onClick={() => setSelectedPool(null)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="mb-6">
              <label className="block text-sm text-gray-600 dark:text-gray-400 mb-2">
                Amount to Stake
              </label>
              <div className="relative">
                <input
                  type="number"
                  value={stakeAmount}
                  onChange={(e) => setStakeAmount(e.target.value)}
                  placeholder="0.0"
                  className="w-full bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg px-4 py-3 pr-20 text-lg font-semibold focus:outline-none focus:ring-2 focus:ring-yellow-400"
                />
                <button className="absolute right-3 top-1/2 transform -translate-y-1/2 text-yellow-500 font-semibold">
                  MAX
                </button>
              </div>
              <div className="flex items-center justify-between mt-2 text-sm text-gray-500 dark:text-gray-400">
                <span>Min: {selectedPool.minStake} {selectedPool.token}</span>
                <span>Balance: 0 {selectedPool.token}</span>
              </div>
            </div>

            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-6 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">APY</span>
                <span className="text-green-500 font-semibold">{selectedPool.apy}%</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Lock Period</span>
                <span className="text-gray-900 dark:text-white font-semibold">{selectedPool.lockPeriod}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Est. Rewards (30d)</span>
                <span className="text-gray-900 dark:text-white font-semibold">
                  {stakeAmount ? (parseFloat(stakeAmount) * selectedPool.apy / 100 / 12).toFixed(4) : '0'} {selectedPool.token}
                </span>
              </div>
            </div>

            <button
              onClick={handleStake}
              disabled={!stakeAmount || parseFloat(stakeAmount) < selectedPool.minStake}
              className="w-full bg-yellow-400 hover:bg-yellow-500 disabled:bg-gray-300 disabled:text-gray-500 text-gray-900 font-bold py-3 rounded-lg transition-colors"
            >
              Stake {selectedPool.token}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DEXStaking;