import React from 'react';
import { Building2, TrendingUp, Shield, Globe, DollarSign, Users, Lock, ArrowRight, Clock, Headphones } from 'lucide-react';

export default function InstitutionalPage() {
  const tiers = [
    { name: 'Basic', min: '1M' },
    { name: 'Premium', min: '10M' },
    { name: 'Elite', min: '50M' },
    { name: 'White Glove', min: '100M' }
  ];

  const services = [
    { icon: <TrendingUp />, title: 'OTC Trading', desc: 'Large orders with minimal market impact' },
    { icon: <Lock />, title: 'Custody Solutions', desc: 'Institutional-grade cold storage' },
    { icon: <Building2 />, title: 'Prime Brokerage', desc: 'Comprehensive prime services' },
    { icon: <Globe />, title: 'Global Markets', desc: '200+ markets across 50+ countries' },
    { icon: <Shield />, title: 'Compliance', desc: 'Full KYC/AML compliance' },
    { icon: <Headphones />, title: 'Dedicated Support', desc: '24/7 account management' }
  ];

  const institutionTypes = [
    'Hedge Fund', 'Family Office', 'Asset Manager', 'Pension Fund',
    'Insurance Company', 'Bank', 'Broker Dealer', 'Proprietary Trading',
    'Market Maker', 'Corporate Treasury'
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-purple-900 py-20">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold flex items-center justify-center gap-4">
            <Building2 className="w-12 h-12 text-blue-400" />
            Institutional Services
          </h1>
          <p className="text-xl text-blue-200 mt-4">Premium trading solutions for institutions</p>
          <button className="mt-8 bg-yellow-500 hover:bg-yellow-400 text-black px-8 py-4 rounded-xl font-bold flex items-center gap-2 mx-auto">
            Apply for Account <ArrowRight className="w-6 h-6" />
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-12">
          <div className="bg-gray-800 p-6 rounded-xl text-center">
            <Users className="w-10 h-10 text-blue-500 mx-auto mb-3" />
            <p className="text-3xl font-bold">245</p>
            <p className="text-gray-400">Institutional Clients</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl text-center">
            <DollarSign className="w-10 h-10 text-green-500 mx-auto mb-3" />
            <p className="text-3xl font-bold">$12.5B</p>
            <p className="text-gray-400">Trading Volume</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl text-center">
            <TrendingUp className="w-10 h-10 text-purple-500 mx-auto mb-3" />
            <p className="text-3xl font-bold">$2.5M</p>
            <p className="text-gray-400">Avg Trade Size</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl text-center">
            <Clock className="w-10 h-10 text-yellow-500 mx-auto mb-3" />
            <p className="text-3xl font-bold">99.99%</p>
            <p className="text-gray-400">Uptime</p>
          </div>
        </div>

        <h2 className="text-2xl font-bold mb-4">Service Tiers</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-12">
          {tiers.map((tier, idx) => (
            <div key={idx} className="bg-gray-800 p-6 rounded-xl text-center">
              <h3 className="text-xl font-bold text-blue-400">{tier.name}</h3>
              <p className="text-gray-400">Min AUM: ${tier.min}</p>
            </div>
          ))}
        </div>

        <h2 className="text-2xl font-bold mb-4">Our Services</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {services.map((service, idx) => (
            <div key={idx} className="bg-gray-800 p-6 rounded-xl">
              <div className="text-blue-400 mb-4">{service.icon}</div>
              <h3 className="text-xl font-bold mb-2">{service.title}</h3>
              <p className="text-gray-400">{service.desc}</p>
            </div>
          ))}
        </div>

        <h2 className="text-2xl font-bold mb-4">Eligible Institutions</h2>
        <div className="flex flex-wrap gap-3 mb-12">
          {institutionTypes.map((type) => (
            <span key={type} className="px-4 py-2 rounded-full bg-gray-800 border border-gray-700">
              {type}
            </span>
          ))}
        </div>

        <div className="bg-gray-800 rounded-xl p-8">
          <h2 className="text-2xl font-bold mb-6">Apply for Institutional Account</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-gray-400 mb-2">Institution Name</label>
              <input className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3" placeholder="Organization" />
            </div>
            <div>
              <label className="block text-gray-400 mb-2">Contact Email</label>
              <input className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3" placeholder="institution@email.com" />
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