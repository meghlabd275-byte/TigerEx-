/**
 * TigerEx Frontend
 * @file index.tsx
 * @description TigerEx React component
 * @author TigerEx Development Team
 */

import React from 'react';
import { Crown, TrendingUp, Wallet, CreditCard, Users, Gift, Shield, Zap } from 'lucide-react';

export default function VIPPage() {
  const vipLevels = [
    { level: 0, name: 'Regular', color: 'gray', fee: 0.1 },
    { level: 1, name: 'VIP 1', color: 'green', fee: 0.09 },
    { level: 2, name: 'VIP 2', color: 'blue', fee: 0.08 },
    { level: 3, name: 'VIP 3', color: 'purple', fee: 0.07 },
    { level: 4, name: 'VIP 4', color: 'orange', fee: 0.06 },
    { level: 5, name: 'VIP 5', color: 'yellow', fee: 0.05 }
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="bg-gradient-to-r from-purple-900 via-purple-800 to-purple-900 py-16">
        <div className="max-w-7xl mx-auto px-6">
          <h1 className="text-4xl font-bold flex items-center gap-3">
            <Crown className="w-10 h-10 text-yellow-400" />
            VIP Program
          </h1>
          <p className="text-purple-200 text-xl mt-2">Exclusive benefits for premium traders</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-800 p-6 rounded-xl">
            <TrendingUp className="w-8 h-8 text-green-500 mb-2" />
            <p className="text-2xl font-bold">$750,000</p>
            <p className="text-gray-400">30-Day Volume</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <Wallet className="w-8 h-8 text-yellow-500 mb-2" />
            <p className="text-2xl font-bold">20%</p>
            <p className="text-gray-400">Fee Discount</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <CreditCard className="w-8 h-8 text-purple-500 mb-2" />
            <p className="text-2xl font-bold">40%</p>
            <p className="text-gray-400">Withdrawal Discount</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <Shield className="w-8 h-8 text-blue-500 mb-2" />
            <p className="text-2xl font-bold text-green-400">Active</p>
            <p className="text-gray-400">Status</p>
          </div>
        </div>

        <h2 className="text-2xl font-bold mb-4">VIP Levels</h2>
        <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-8">
          {vipLevels.map((vip) => (
            <div key={vip.level} className="bg-gray-800 p-4 rounded-xl text-center">
              <Crown className={`w-8 h-8 mx-auto mb-2 text-${vip.color}-500`} />
              <h3 className="font-bold">{vip.name}</h3>
              <p className="text-sm text-gray-400">{(vip.fee * 100).toFixed(0)}% fee</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-800 p-6 rounded-xl">
            <Zap className="w-8 h-8 text-yellow-500 mb-3" />
            <h3 className="text-lg font-semibold">Trading Fees</h3>
            <ul className="mt-2 space-y-2 text-gray-400">
              <li>• Reduced maker/taker fees</li>
              <li>• Futures discount</li>
              <li>• Options discount</li>
            </ul>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <CreditCard className="w-8 h-8 text-purple-500 mb-3" />
            <h3 className="text-lg font-semibold">Withdrawals</h3>
            <ul className="mt-2 space-y-2 text-gray-400">
              <li>• Reduced fees</li>
              <li>• Higher limits</li>
              <li>• Priority processing</li>
            </ul>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <Users className="w-8 h-8 text-blue-500 mb-3" />
            <h3 className="text-lg font-semibold">Premium Support</h3>
            <ul className="mt-2 space-y-2 text-gray-400">
              <li>• Dedicated manager</li>
              <li>• 24/7 VIP support</li>
              <li>• Exclusive events</li>
            </ul>
          </div>
        </div>

        <div className="mt-8 bg-gradient-to-r from-purple-900/50 to-blue-900/50 p-6 rounded-xl">
          <h3 className="text-xl font-bold flex items-center gap-2">
            <Gift className="w-6 h-6 text-yellow-500" />
            VIP Loan Service
          </h3>
          <p className="text-gray-400 mt-1">Get instant collateralized loans with preferential rates</p>
          <button className="mt-4 bg-yellow-500 hover:bg-yellow-400 text-black px-6 py-3 rounded-lg font-semibold">
            Apply Now
          </button>
        </div>
      </div>
    </div>
  );
}