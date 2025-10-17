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

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';
import { 
  ChartBarIcon, 
  CurrencyDollarIcon, 
  ShieldCheckIcon, 
  GlobeAltIcon,
  ArrowTrendingUpIcon,
  UserGroupIcon,
  BoltIcon,
  CogIcon
} from '@heroicons/react/24/outline';

const HomePage = () => {
  const features = [
    {
      icon: ChartBarIcon,
      title: 'Advanced Trading',
      description: 'Professional trading tools with real-time charts and technical indicators',
    },
    {
      icon: ShieldCheckIcon,
      title: 'Bank-Level Security',
      description: '95% cold storage, multi-signature wallets, and advanced encryption',
    },
    {
      icon: BoltIcon,
      title: 'Lightning Fast',
      description: 'Sub-10ms order execution with high-frequency trading support',
    },
    {
      icon: GlobeAltIcon,
      title: 'Global Access',
      description: 'Trade 500+ cryptocurrencies with 50+ fiat currencies',
    },
    {
      icon: UserGroupIcon,
      title: 'Copy Trading',
      description: 'Follow and copy successful traders automatically',
    },
    {
      icon: CogIcon,
      title: 'White Label',
      description: 'Launch your own exchange with our white-label solution',
    },
  ];

  const stats = [
    { label: '24h Volume', value: '$2.5B+' },
    { label: 'Users', value: '10M+' },
    { label: 'Countries', value: '180+' },
    { label: 'Trading Pairs', value: '500+' },
  ];

  const tradingProducts = [
    {
      title: 'Spot Trading',
      description: 'Trade cryptocurrencies with zero fees on selected pairs',
      icon: '📊',
    },
    {
      title: 'Futures Trading',
      description: 'Up to 125x leverage on perpetual and quarterly contracts',
      icon: '📈',
    },
    {
      title: 'Options Trading',
      description: 'European and American style options with advanced strategies',
      icon: '🎯',
    },
    {
      title: 'P2P Trading',
      description: 'Buy and sell crypto directly with other users',
      icon: '🤝',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-black/20 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="text-2xl font-bold text-white">
                🐅 <span className="text-orange-400">Tiger</span>Ex
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <Link href="/markets" className="text-white hover:text-orange-400 transition-colors">
                Markets
              </Link>
              <Link href="/trading" className="text-white hover:text-orange-400 transition-colors">
                Trade
              </Link>
              <Link href="/futures" className="text-white hover:text-orange-400 transition-colors">
                Futures
              </Link>
              <Link href="/p2p" className="text-white hover:text-orange-400 transition-colors">
                P2P
              </Link>
              <Link href="/earn" className="text-white hover:text-orange-400 transition-colors">
                Earn
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/login"
                className="text-white hover:text-orange-400 transition-colors"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg transition-colors"
              >
                Register
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
              Trade Crypto
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-pink-600">
                Like a Pro
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
              Advanced trading platform with institutional-grade security, 
              lightning-fast execution, and comprehensive trading tools.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/register"
                className="bg-gradient-to-r from-orange-500 to-pink-600 hover:from-orange-600 hover:to-pink-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-all transform hover:scale-105"
              >
                Start Trading
              </Link>
              <Link
                href="/markets"
                className="border border-white/20 hover:border-white/40 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-all hover:bg-white/5"
              >
                View Markets
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-3xl md:text-4xl font-bold text-white mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-400">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Trading Products */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Trading Products
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Comprehensive suite of trading products for every type of trader
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {tradingProducts.map((product, index) => (
              <motion.div
                key={product.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-all cursor-pointer"
              >
                <div className="text-4xl mb-4">{product.icon}</div>
                <h3 className="text-xl font-semibold text-white mb-3">
                  {product.title}
                </h3>
                <p className="text-gray-400">{product.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Why Choose TigerEx?
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Built for traders, by traders. Experience the next generation of cryptocurrency trading.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8 hover:bg-white/10 transition-all"
              >
                <feature.icon className="h-12 w-12 text-orange-400 mb-6" />
                <h3 className="text-xl font-semibold text-white mb-4">
                  {feature.title}
                </h3>
                <p className="text-gray-400">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="bg-gradient-to-r from-orange-500/20 to-pink-600/20 backdrop-blur-sm border border-white/10 rounded-2xl p-12"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Ready to Start Trading?
            </h2>
            <p className="text-xl text-gray-300 mb-8">
              Join millions of traders worldwide and experience the future of cryptocurrency trading.
            </p>
            <Link
              href="/register"
              className="bg-gradient-to-r from-orange-500 to-pink-600 hover:from-orange-600 hover:to-pink-700 text-white px-12 py-4 rounded-lg text-xl font-semibold transition-all transform hover:scale-105 inline-block"
            >
              Get Started Now
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black/20 backdrop-blur-sm border-t border-white/10 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="text-2xl font-bold text-white mb-4">
                🐅 <span className="text-orange-400">Tiger</span>Ex
              </div>
              <p className="text-gray-400">
                The world's leading cryptocurrency exchange platform.
              </p>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Products</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/spot" className="hover:text-white transition-colors">Spot Trading</Link></li>
                <li><Link href="/futures" className="hover:text-white transition-colors">Futures</Link></li>
                <li><Link href="/options" className="hover:text-white transition-colors">Options</Link></li>
                <li><Link href="/p2p" className="hover:text-white transition-colors">P2P</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/help" className="hover:text-white transition-colors">Help Center</Link></li>
                <li><Link href="/api" className="hover:text-white transition-colors">API Docs</Link></li>
                <li><Link href="/fees" className="hover:text-white transition-colors">Fees</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/about" className="hover:text-white transition-colors">About</Link></li>
                <li><Link href="/careers" className="hover:text-white transition-colors">Careers</Link></li>
                <li><Link href="/news" className="hover:text-white transition-colors">News</Link></li>
                <li><Link href="/legal" className="hover:text-white transition-colors">Legal</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/10 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 TigerEx. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;