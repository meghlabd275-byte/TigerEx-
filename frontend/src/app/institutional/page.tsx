'use client';

import React, { useState } from 'react';
import { 
  Building2, 
  TrendingUp, 
  Shield, 
  Globe, 
  DollarSign, 
  Users,
  Lock,
  ArrowRight,
  Check,
  Clock,
  FileText,
  HeadphonesIcon
} from 'lucide-react';

const SERVICE_TIERS = [
  { id: 'basic', name: 'Basic', minAUM: 1000000, color: 'blue' },
  { id: 'premium', name: 'Premium', minAUM: 10000000, color: 'purple' },
  { id: 'elite', name: 'Elite', minAUM: 50000000, color: 'orange' },
  { id: 'white_glove', name: 'White Glove', minAUM: 100000000, color: 'yellow' }
];

const INSTITUTION_TYPES = [
  'Hedge Fund',
  'Family Office', 
  'Asset Manager',
  'Pension Fund',
  'Insurance Company',
  'Bank',
  'Broker Dealer',
  'Proprietary Trading',
  'Market Maker',
  'Corporate Treasury'
];

export default function InstitutionalPage() {
  const [selectedTier, setSelectedTier] = useState('premium');
  const [institutionType, setInstitutionType] = useState('');
  
  const institutionalStats = {
    totalClients: 245,
    totalVolume: 12500000000,
    avgTradeSize: 2500000,
    uptime: 99.99
  };

  const services = [
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: 'OTC Trading',
      description: 'Over-the-counter trading for large orders with minimal market impact',
      features: ['$100K minimum', 'Competitive spreads', 'Instant settlement']
    },
    {
      icon: <Lock className="w-8 h-8" />,
      title: 'Custody Solutions',
      description: 'Institutional-grade cold storage with multi-signature security',
      features: ['Hot/Warm/Cold storage', 'Multi-sig support', '$500M insurance']
    },
    {
      icon: <Building2 className="w-8 h-8" />,
      title: 'Prime Brokerage',
      description: 'Comprehensive prime brokerage services for institutional clients',
      features: ['Margin lending', 'Securities lending', 'Reporting']
    },
    {
      icon: <Globe className="w-8 h-8" />,
      title: 'Global Market Access',
      description: 'Access to 200+ markets across 50+ countries',
      features: ['Spot, Futures, Options', '30+ exchanges', 'API connectivity']
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: 'Regulatory Compliance',
      description: 'Full compliance with global financial regulations',
      features: ['KYC/AML', 'SAR reporting', 'Audit trails']
    },
    {
      icon: <HeadphonesIcon className="w-8 h-8" />,
      title: 'Dedicated Support',
      description: '24/7 dedicated account management',
      features: ['Relationship manager', 'Priority support', 'Custom solutions']
    }
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Hero */}
      <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-purple-900 py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center">
            <h1 className="text-5xl font-bold mb-4 flex items-center justify-center gap-4">
              <Building2 className="w-12 h-12 text-blue-400" />
              Institutional Services
            </h1>
            <p className="text-xl text-blue-200 mb-8 max-w-2xl mx-auto">
              Premium trading solutions for hedge funds, family offices, and institutional investors
            </p>
            <button className="bg-yellow-500 hover:bg-yellow-400 text-black px-8 py-4 rounded-xl font-bold text-lg flex items-center gap-2 mx-auto">
              Apply for Account <ArrowRight className="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-12">
          <div className="bg-gray-800 p-6 rounded-xl text-center">
            <Users className="w-10 h-10 text-blue-500 mx-auto mb-3" />
            <p className="text-3xl font-bold">{institutionalStats.totalClients}</p>
            <p className="text-gray-400">Institutional Clients</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl text-center">
            <DollarSign className="w-10 h-10 text-green-500 mx-auto mb-3" />
            <p className="text-3xl font-bold">${(institutionalStats.totalVolume / 1e9).toFixed(0)}B</p>
            <p className="text-gray-400">Trading Volume</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl text-center">
            <TrendingUp className="w-10 h-10 text-purple-500 mx-auto mb-3" />
            <p className="text-3xl font-bold">${(institutionalStats.avgTradeSize / 1e6).toFixed(1)}M</p>
            <p className="text-gray-400">Avg Trade Size</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl text-center">
            <Clock className="w-10 h-10 text-yellow-500 mx-auto mb-3" />
            <p className="text-3xl font-bold">{institutionalStats.uptime}%</p>
            <p className="text-gray-400">System Uptime</p>
          </div>
        </div>

        {/* Service Tiers */}
        <h2 className="text-2xl font-bold mb-4">Service Tiers</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-12">
          {SERVICE_TIERS.map((tier) => (
            <div 
              key={tier.id}
              onClick={() => setSelectedTier(tier.id)}
              className={`bg-gray-800 p-6 rounded-xl cursor-pointer transition-all ${
                selectedTier === tier.id 
                  ? 'ring-2 ring-blue-500 transform scale-105' 
                  : 'hover:ring-1 hover:ring-gray-600'
              }`}
            >
              <h3 className={`text-xl font-bold mb-2 ${
                tier.color === 'blue' ? 'text-blue-400' :
                tier.color === 'purple' ? 'text-purple-400' :
                tier.color === 'orange' ? 'text-orange-400' : 'text-yellow-400'
              }`}>
                {tier.name}
              </h3>
              <p className="text-gray-400 mb-4">Min AUM: ${(tier.minAUM / 1e6).toFixed(0)}M</p>
              {selectedTier === tier.id && (
                <div className="flex items-center gap-2 text-green-400">
                  <Check className="w-5 h-5" /> Selected
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Services Grid */}
        <h2 className="text-2xl font-bold mb-4">Our Services</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {services.map((service, idx) => (
            <div key={idx} className="bg-gray-800 p-6 rounded-xl">
              <div className="text-blue-400 mb-4">{service.icon}</div>
              <h3 className="text-xl font-bold mb-2">{service.title}</h3>
              <p className="text-gray-400 mb-4">{service.description}</p>
              <ul className="space-y-2">
                {service.features.map((feature, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-gray-300">
                    <Check className="w-4 h-4 text-green-500" /> {feature}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Institution Types */}
        <h2 className="text-2xl font-bold mb-4">Eligible Institutions</h2>
        <div className="flex flex-wrap gap-3 mb-12">
          {INSTITUTION_TYPES.map((type) => (
            <span 
              key={type}
              className={`px-4 py-2 rounded-full bg-gray-800 border ${
                institutionType === type 
                  ? 'border-blue-500 text-blue-400' 
                  : 'border-gray-700 text-gray-400'
              } cursor-pointer transition-all`}
              onClick={() => setInstitutionType(institutionType === type ? '' : type)}
            >
              {type}
            </span>
          ))}
        </div>

        {/* Application Form */}
        <div className="bg-gray-800 rounded-xl p-8">
          <h2 className="text-2xl font-bold mb-6">Apply for Institutional Account</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-gray-400 mb-2">Institution Name</label>
              <input 
                type="text" 
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500"
                placeholder="Your organization"
              />
            </div>
            <div>
              <label className="block text-gray-400 mb-2">Institution Type</label>
              <select className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500">
                <option value="">Select type</option>
                {INSTITUTION_TYPES.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-gray-400 mb-2">Contact Email</label>
              <input 
                type="email" 
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500"
                placeholder="institution@email.com"
              />
            </div>
            <div>
              <label className="block text-gray-400 mb-2">Expected Monthly Volume</label>
              <select className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500">
                <option value="">Select volume</option>
                <option value="1m">$1M - $10M</option>
                <option value="10m">$10M - $50M</option>
                <option value="50m">$50M - $100M</option>
                <option value="100m">$100M+</option>
              </select>
            </div>
          </div>
          <button className="mt-6 bg-blue-500 hover:bg-blue-400 text-white px-8 py-4 rounded-xl font-bold">
            Submit Application
          </button>
        </div>
      </div>
    </div>
  );
}