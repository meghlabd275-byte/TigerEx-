import React, { useState } from 'react';
import { Users, DollarSign, Gift, TrendingUp, Link, Copy, Check, Award, ChevronRight, Wallet } from 'lucide-react';

export default function AffiliatePage() {
  const [copied, setCopied] = useState(false);
  const referralLink = 'https://tigerex.com/ref/ABC123XYZ';

  const stats = {
    totalReferrals: 156,
    activeReferrals: 89,
    totalCommission: 24500,
    pendingCommission: 3200,
    tier: 2
  };

  const tiers = [
    { tier: 1, rate: 20, req: '0-50' },
    { tier: 2, rate: 25, req: '51-200' },
    { tier: 3, rate: 30, req: '201-500' },
    { tier: 4, rate: 35, req: '501-1000' },
    { tier: 5, rate: 40, req: '1000+' }
  ];

  const copyLink = () => {
    navigator.clipboard.writeText(referralLink);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="bg-gradient-to-r from-green-900 to-teal-900 py-16">
        <div className="max-w-7xl mx-auto px-6">
          <h1 className="text-4xl font-bold flex items-center gap-3">
            <Users className="w-10 h-10 text-green-400" />
            Affiliate Program
          </h1>
          <p className="text-green-200 text-xl mt-2">Earn up to 40% commission on referrals' trading fees</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-gray-800 p-6 rounded-xl">
            <Users className="w-8 h-8 text-green-500 mb-2" />
            <p className="text-2xl font-bold">{stats.totalReferrals}</p>
            <p className="text-gray-400">Total Referrals</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <TrendingUp className="w-8 h-8 text-blue-500 mb-2" />
            <p className="text-2xl font-bold">{stats.activeReferrals}</p>
            <p className="text-gray-400">Active</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <DollarSign className="w-8 h-8 text-yellow-500 mb-2" />
            <p className="text-2xl font-bold">${stats.totalCommission.toLocaleString()}</p>
            <p className="text-gray-400">Total Earned</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <Wallet className="w-8 h-8 text-purple-500 mb-2" />
            <p className="text-2xl font-bold">${stats.pendingCommission.toLocaleString()}</p>
            <p className="text-gray-400">Pending</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <Award className="w-8 h-8 text-teal-500 mb-2" />
            <p className="text-2xl font-bold">{tiers[stats.tier - 1].rate}%</p>
            <p className="text-gray-400">Commission</p>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-xl mb-8">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Link className="w-6 h-6 text-green-500" />
            Your Referral Link
          </h2>
          <div className="flex gap-4">
            <input
              type="text"
              value={referralLink}
              readOnly
              className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-3"
            />
            <button
              onClick={copyLink}
              className="bg-green-500 hover:bg-green-400 text-black px-6 py-3 rounded-lg font-semibold flex items-center gap-2"
            >
              {copied ? <Check className="w-5 h-5" /> : <Copy className="w-5 h-5" />}
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
        </div>

        <h2 className="text-xl font-bold mb-4">Commission Tiers</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          {tiers.map((t) => (
            <div key={t.tier} className={`bg-gray-800 p-4 rounded-xl text-center ${stats.tier === t.tier ? 'ring-2 ring-green-500' : ''}`}>
              <Award className={`w-8 h-8 mx-auto mb-2 ${stats.tier === t.tier ? 'text-yellow-500' : 'text-gray-500'}`} />
              <h3 className="font-bold">Tier {t.tier}</h3>
              <p className="text-2xl font-bold text-green-400">{t.rate}%</p>
              <p className="text-gray-400 text-sm">{t.req} refs</p>
            </div>
          ))}
        </div>

        <button className="w-full bg-green-500 hover:bg-green-400 text-black py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2">
          <Wallet className="w-6 h-6" />
          Request Payout
        </button>
      </div>
    </div>
  );
}