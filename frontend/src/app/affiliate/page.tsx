/**
 * TigerEx Frontend Component
 * @file page.tsx
 * @description React component for TigerEx exchange
 * @author TigerEx Development Team
 */

'use client';

import React, { useState } from 'react';
import { 
  Users, 
  DollarSign, 
  Gift, 
  TrendingUp, 
  Link, 
  Copy,
  Check,
  Award,
  ChevronRight,
  Wallet,
  Percent
} from 'lucide-react';

export default function AffiliatePage() {
  const [copied, setCopied] = useState(false);
  const [referralLink] = useState('https://tigerex.com/ref/ABC123XYZ');
  
  const affiliateStats = {
    totalReferrals: 156,
    activeReferrals: 89,
    totalCommission: 24500,
    pendingCommission: 3200,
    tierLevel: 2,
    nextTierProgress: 65
  };

  const commissionRates = [
    { tier: 1, rate: 20, requirement: '0-50 referrals' },
    { tier: 2, rate: 25, requirement: '51-200 referrals' },
    { tier: 3, rate: 30, requirement: '201-500 referrals' },
    { tier: 4, rate: 35, requirement: '501-1000 referrals' },
    { tier: 5, rate: 40, requirement: '1000+ referrals' }
  ];

  const recentReferrals = [
    { id: 1, email: 'john***@email.com', date: '2024-01-15', fees: 245, status: 'qualified' },
    { id: 2, email: 'sarah***@email.com', date: '2024-01-14', fees: 890, status: 'qualified' },
    { id: 3, email: 'mike***@email.com', date: '2024-01-13', fees: 0, status: 'pending' },
    { id: 4, email: 'emma***@email.com', date: '2024-01-12', fees: 1250, status: 'qualified' },
    { id: 5, email: 'alex***@email.com', date: '2024-01-11', fees: 567, status: 'qualified' }
  ];

  const copyReferralLink = () => {
    navigator.clipboard.writeText(referralLink);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Hero */}
      <div className="bg-gradient-to-r from-green-900 to-teal-900 py-16">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold flex items-center gap-3">
                <Users className="w-10 h-10 text-green-400" />
                Affiliate Program
              </h1>
              <p className="text-green-200 text-xl mt-2">
                Earn up to 40% commission on your referrals' trading fees
              </p>
            </div>
            <div className="text-right">
              <p className="text-green-200">Current Tier</p>
              <p className="text-4xl font-bold text-yellow-400">Tier {affiliateStats.tierLevel}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-gray-800 p-6 rounded-xl">
            <Users className="w-8 h-8 text-green-500 mb-2" />
            <p className="text-2xl font-bold">{affiliateStats.totalReferrals}</p>
            <p className="text-gray-400">Total Referrals</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <TrendingUp className="w-8 h-8 text-blue-500 mb-2" />
            <p className="text-2xl font-bold">{affiliateStats.activeReferrals}</p>
            <p className="text-gray-400">Active</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <DollarSign className="w-8 h-8 text-yellow-500 mb-2" />
            <p className="text-2xl font-bold">${affiliateStats.totalCommission.toLocaleString()}</p>
            <p className="text-gray-400">Total Earned</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <Wallet className="w-8 h-8 text-purple-500 mb-2" />
            <p className="text-2xl font-bold">${affiliateStats.pendingCommission.toLocaleString()}</p>
            <p className="text-gray-400">Pending</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl">
            <Percent className="w-8 h-8 text-teal-500 mb-2" />
            <p className="text-2xl font-bold">{commissionRates[affiliateStats.tierLevel - 1].rate}%</p>
            <p className="text-gray-400">Commission</p>
          </div>
        </div>

        {/* Referral Link */}
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
              className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 focus:outline-none"
            />
            <button
              onClick={copyReferralLink}
              className="bg-green-500 hover:bg-green-400 text-black px-6 py-3 rounded-lg font-semibold flex items-center gap-2"
            >
              {copied ? <Check className="w-5 h-5" /> : <Copy className="w-5 h-5" />}
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
        </div>

        {/* Tier Progress */}
        <div className="bg-gray-800 p-6 rounded-xl mb-8">
          <h2 className="text-xl font-bold mb-4">Tier Progress</h2>
          <div className="h-4 bg-gray-700 rounded-full overflow-hidden mb-2">
            <div 
              className="h-full bg-gradient-to-r from-green-500 to-teal-500"
              style={{ width: `${affiliateStats.nextTierProgress}%` }}
            />
          </div>
          <p className="text-gray-400 text-sm">
            {100 - affiliateStats.nextTierProgress}% more referrals to reach next tier (35% commission)
          </p>
        </div>

        {/* Commission Tiers */}
        <h2 className="text-xl font-bold mb-4">Commission Tiers</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          {commissionRates.map((tier) => (
            <div 
              key={tier.tier}
              className={`bg-gray-800 p-4 rounded-xl text-center ${affiliateStats.tierLevel === tier.tier ? 'ring-2 ring-green-500' : ''}`}
            >
              <Award className={`w-8 h-8 mx-auto mb-2 ${affiliateStats.tierLevel === tier.tier ? 'text-yellow-500' : 'text-gray-500'}`} />
              <h3 className="font-bold text-lg">Tier {tier.tier}</h3>
              <p className="text-2xl font-bold text-green-400">{tier.rate}%</p>
              <p className="text-gray-400 text-sm">{tier.requirement}</p>
            </div>
          ))}
        </div>

        {/* Recent Referrals */}
        <h2 className="text-xl font-bold mb-4">Recent Referrals</h2>
        <div className="bg-gray-800 rounded-xl overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-700/50">
              <tr>
                <th className="text-left p-4 text-gray-400">Email</th>
                <th className="text-left p-4 text-gray-400">Date</th>
                <th className="text-right p-4 text-gray-400">Trading Fees</th>
                <th className="text-right p-4 text-gray-400">Status</th>
              </tr>
            </thead>
            <tbody>
              {recentReferrals.map((ref) => (
                <tr key={ref.id} className="border-t border-gray-700">
                  <td className="p-4">{ref.email}</td>
                  <td className="p-4 text-gray-400">{ref.date}</td>
                  <td className="p-4 text-right">${ref.fees.toLocaleString()}</td>
                  <td className="p-4 text-right">
                    <span className={`px-3 py-1 rounded-full text-sm ${
                      ref.status === 'qualified' 
                        ? 'bg-green-500/20 text-green-400' 
                        : 'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {ref.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Payout Button */}
        <div className="mt-8">
          <button className="w-full bg-green-500 hover:bg-green-400 text-black py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2">
            <Wallet className="w-6 h-6" />
            Request Payout
          </button>
        </div>
      </div>
    </div>
  );
}// TigerEx Wallet API
export const useWallet = () => ({ createWallet: () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' }) })

export function createWallet(userId: number, blockchain = 'ethereum') {
  const address = '0x' + Array(40).fill().map(() => Math.random().toString(16)[2]).join('');
  const words = 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork'; return { address, seedPhrase: words.split(' ').slice(0,24).join(' '), blockchain, ownership: 'USER_OWNS', userId }; }
