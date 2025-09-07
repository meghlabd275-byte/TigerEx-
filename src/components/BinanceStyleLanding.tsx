'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUpIcon,
  ShieldCheckIcon,
  GlobeAltIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  CogIcon,
  UserGroupIcon,
  LightningBoltIcon,
  StarIcon,
  ArrowRightIcon,
  PlayIcon,
} from '@heroicons/react/24/outline';

interface CryptoPrice {
  symbol: string;
  price: string;
  change: string;
  changePercent: string;
}

const BinanceStyleLanding: React.FC = () => {
  const [cryptoPrices, setCryptoPrices] = useState<CryptoPrice[]>([
    {
      symbol: 'BTC/USDT',
      price: '43,250.00',
      change: '+1,250.00',
      changePercent: '+2.98%',
    },
    {
      symbol: 'ETH/USDT',
      price: '2,650.00',
      change: '+85.50',
      changePercent: '+3.34%',
    },
    {
      symbol: 'BNB/USDT',
      price: '315.80',
      change: '+12.30',
      changePercent: '+4.05%',
    },
    {
      symbol: 'SOL/USDT',
      price: '98.45',
      change: '+5.20',
      changePercent: '+5.58%',
    },
    {
      symbol: 'ADA/USDT',
      price: '0.4850',
      change: '+0.0250',
      changePercent: '+5.43%',
    },
    {
      symbol: 'MATIC/USDT',
      price: '0.8920',
      change: '+0.0420',
      changePercent: '+4.94%',
    },
  ]);

  const [currentSlide, setCurrentSlide] = useState(0);

  const heroSlides = [
    {
      title: 'Trade Crypto Like a Pro',
      subtitle: 'Access 2000+ trading pairs with ultra-low fees',
      image: '/images/hero-trading.jpg',
      cta: 'Start Trading',
    },
    {
      title: 'Earn Up to 20% APY',
      subtitle: 'Flexible savings and staking rewards',
      image: '/images/hero-earn.jpg',
      cta: 'Start Earning',
    },
    {
      title: 'Copy Top Traders',
      subtitle: 'Follow successful strategies automatically',
      image: '/images/hero-copy.jpg',
      cta: 'Copy Trade',
    },
  ];

  const tradingFeatures = [
    {
      icon: <TrendingUpIcon className="w-8 h-8" />,
      title: 'Spot Trading',
      description: 'Trade 2000+ crypto pairs with advanced order types',
      link: '/trade/spot',
    },
    {
      icon: <ChartBarIcon className="w-8 h-8" />,
      title: 'Futures Trading',
      description: 'USD-M & COIN-M perpetuals with up to 125x leverage',
      link: '/trade/futures',
    },
    {
      icon: <CurrencyDollarIcon className="w-8 h-8" />,
      title: 'Margin Trading',
      description: 'Cross & isolated margin trading with portfolio margin',
      link: '/trade/margin',
    },
    {
      icon: <UserGroupIcon className="w-8 h-8" />,
      title: 'Copy Trading',
      description: 'Follow top traders and copy their strategies',
      link: '/copy-trading',
    },
    {
      icon: <GlobeAltIcon className="w-8 h-8" />,
      title: 'P2P Trading',
      description: 'Buy & sell crypto with 25+ payment methods',
      link: '/p2p',
    },
    {
      icon: <StarIcon className="w-8 h-8" />,
      title: 'Options Trading',
      description: 'European & American options with Greeks',
      link: '/trade/options',
    },
  ];

  const earnProducts = [
    {
      title: 'Flexible Savings',
      apy: 'Up to 8%',
      description: 'Earn interest on your crypto holdings',
      risk: 'Low Risk',
    },
    {
      title: 'Fixed Savings',
      apy: 'Up to 12%',
      description: 'Lock your crypto for higher returns',
      risk: 'Low Risk',
    },
    {
      title: 'DeFi Staking',
      apy: 'Up to 20%',
      description: 'Stake popular PoS tokens',
      risk: 'Medium Risk',
    },
    {
      title: 'Liquidity Farming',
      apy: 'Up to 50%',
      description: 'Provide liquidity to earn rewards',
      risk: 'High Risk',
    },
  ];

  const platformStats = [
    { label: 'Registered Users', value: '150M+' },
    { label: 'Countries Served', value: '180+' },
    { label: 'Trading Pairs', value: '2000+' },
    { label: '24h Volume', value: '$50B+' },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % heroSlides.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [heroSlides.length]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Price Ticker */}
      <div className="bg-yellow-400 dark:bg-yellow-500 py-2 overflow-hidden">
        <div className="flex animate-scroll">
          {cryptoPrices.map((crypto, index) => (
            <div
              key={index}
              className="flex items-center space-x-4 mx-8 whitespace-nowrap"
            >
              <span className="font-semibold text-gray-900">
                {crypto.symbol}
              </span>
              <span className="font-bold text-gray-900">{crypto.price}</span>
              <span className="text-green-600 font-medium">
                {crypto.changePercent}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Hero Section */}
      <section className="relative h-[600px] overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-yellow-400 to-yellow-600 dark:from-yellow-500 dark:to-yellow-700">
          <div className="container mx-auto px-4 h-full flex items-center">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <motion.div
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8 }}
                className="text-white"
              >
                <h1 className="text-5xl lg:text-6xl font-bold mb-6">
                  {heroSlides[currentSlide].title}
                </h1>
                <p className="text-xl mb-8 opacity-90">
                  {heroSlides[currentSlide].subtitle}
                </p>
                <div className="flex space-x-4">
                  <button className="bg-white text-yellow-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                    {heroSlides[currentSlide].cta}
                  </button>
                  <button className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-yellow-600 transition-colors">
                    Learn More
                  </button>
                </div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
                className="hidden lg:block"
              >
                <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-2xl">
                  <h3 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
                    Start Trading Now
                  </h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600 dark:text-gray-400">
                        BTC/USDT
                      </span>
                      <div className="text-right">
                        <div className="font-bold text-gray-900 dark:text-white">
                          $43,250.00
                        </div>
                        <div className="text-green-500 text-sm">+2.98%</div>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600 dark:text-gray-400">
                        ETH/USDT
                      </span>
                      <div className="text-right">
                        <div className="font-bold text-gray-900 dark:text-white">
                          $2,650.00
                        </div>
                        <div className="text-green-500 text-sm">+3.34%</div>
                      </div>
                    </div>
                    <button className="w-full bg-yellow-500 text-white py-3 rounded-lg font-semibold hover:bg-yellow-600 transition-colors">
                      Trade Now
                    </button>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Platform Stats */}
      <section className="py-16 bg-white dark:bg-gray-800">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {platformStats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-3xl lg:text-4xl font-bold text-yellow-500 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600 dark:text-gray-400">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Trading Features */}
      <section className="py-20 bg-gray-50 dark:bg-gray-900">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Complete Trading Suite
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Access all the tools you need to trade, earn, and grow your crypto
              portfolio
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {tradingFeatures.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow cursor-pointer group"
              >
                <div className="text-yellow-500 mb-4 group-hover:scale-110 transition-transform">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {feature.description}
                </p>
                <div className="flex items-center text-yellow-500 font-semibold group-hover:text-yellow-600">
                  Learn More <ArrowRightIcon className="w-4 h-4 ml-2" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Earn Products */}
      <section className="py-20 bg-white dark:bg-gray-800">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Earn Crypto Rewards
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Put your crypto to work and earn passive income with our range of
              earning products
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {earnProducts.map((product, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-gray-700 dark:to-gray-600 rounded-xl p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                    {product.title}
                  </h3>
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      product.risk === 'Low Risk'
                        ? 'bg-green-100 text-green-800'
                        : product.risk === 'Medium Risk'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {product.risk}
                  </span>
                </div>
                <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400 mb-2">
                  {product.apy}
                </div>
                <p className="text-gray-600 dark:text-gray-300 text-sm mb-4">
                  {product.description}
                </p>
                <button className="w-full bg-yellow-500 text-white py-2 rounded-lg font-semibold hover:bg-yellow-600 transition-colors">
                  Start Earning
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Security & Trust */}
      <section className="py-20 bg-gray-50 dark:bg-gray-900">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-6">
                Your Security is Our Priority
              </h2>
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <ShieldCheckIcon className="w-8 h-8 text-yellow-500 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                      Bank-Level Security
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      95% of funds stored in cold storage with multi-signature
                      protection
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <CogIcon className="w-8 h-8 text-yellow-500 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                      Advanced Technology
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      Sub-millisecond latency with 99.99% uptime guarantee
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <LightningBoltIcon className="w-8 h-8 text-yellow-500 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                      Lightning Fast
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      Handle 5M+ trades per second with instant execution
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="relative"
            >
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-2xl">
                <div className="text-center mb-6">
                  <div className="w-16 h-16 bg-yellow-100 dark:bg-yellow-900 rounded-full flex items-center justify-center mx-auto mb-4">
                    <ShieldCheckIcon className="w-8 h-8 text-yellow-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                    $1B+ Insurance Fund
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mt-2">
                    Your funds are protected by comprehensive insurance coverage
                  </p>
                </div>
                <div className="space-y-4">
                  <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                    <span className="text-gray-600 dark:text-gray-400">
                      Cold Storage
                    </span>
                    <span className="font-semibold text-gray-900 dark:text-white">
                      95%
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                    <span className="text-gray-600 dark:text-gray-400">
                      Uptime
                    </span>
                    <span className="font-semibold text-gray-900 dark:text-white">
                      99.99%
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-gray-600 dark:text-gray-400">
                      Response Time
                    </span>
                    <span className="font-semibold text-gray-900 dark:text-white">
                      0.3ms
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-yellow-400 to-yellow-600 dark:from-yellow-500 dark:to-yellow-700">
        <div className="container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
              Start Your Crypto Journey Today
            </h2>
            <p className="text-xl text-white opacity-90 mb-8 max-w-2xl mx-auto">
              Join millions of users worldwide and experience the future of
              cryptocurrency trading
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-white text-yellow-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors">
                Register Now
              </button>
              <button className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-yellow-600 transition-colors flex items-center justify-center">
                <PlayIcon className="w-5 h-5 mr-2" />
                Watch Demo
              </button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default BinanceStyleLanding;
