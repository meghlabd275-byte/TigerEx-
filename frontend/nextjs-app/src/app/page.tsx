'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  Shield, 
  Zap, 
  Globe, 
  BarChart3, 
  Wallet,
  ArrowRight,
  CheckCircle2
} from 'lucide-react'

export default function Home() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  return (
    <main className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary-500/10 to-primary-600/10" />
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/20 rounded-full blur-3xl animate-pulse-slow" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-primary-600/20 rounded-full blur-3xl animate-pulse-slow delay-1000" />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h1 className="text-6xl md:text-8xl font-bold text-white mb-6">
              <span className="bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
                TigerEx
              </span>
            </h1>
            <p className="text-2xl md:text-3xl text-gray-300 mb-8">
              The World's Most Advanced Cryptocurrency Exchange
            </p>
            <p className="text-xl text-gray-400 mb-12 max-w-3xl mx-auto">
              Ultra-low latency trading engine • 1M+ TPS • Sub-microsecond execution
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-lg font-semibold text-lg shadow-glow hover:shadow-glow-lg transition-all"
              >
                Start Trading Now
                <ArrowRight className="inline-block ml-2" size={20} />
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 bg-dark-800 text-white rounded-lg font-semibold text-lg border border-dark-700 hover:border-primary-500 transition-all"
              >
                View Documentation
              </motion.button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-dark-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Why Choose TigerEx?
            </h2>
            <p className="text-xl text-gray-400">
              Industry-leading features and performance
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-dark-800 rounded-xl p-6 border border-dark-700 hover:border-primary-500 transition-all"
              >
                <div className="w-12 h-12 bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg flex items-center justify-center mb-4">
                  <feature.icon className="text-white" size={24} />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-400">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-4xl md:text-5xl font-bold text-primary-500 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-400">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="py-24 bg-dark-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Built with Modern Technology
            </h2>
            <p className="text-xl text-gray-400">
              Cutting-edge tech stack for maximum performance
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
            {technologies.map((tech, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.05 }}
                className="bg-dark-800 rounded-lg p-4 border border-dark-700 hover:border-primary-500 transition-all text-center"
              >
                <div className="text-2xl mb-2">{tech.icon}</div>
                <div className="text-sm text-gray-300 font-medium">{tech.name}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Ready to Start Trading?
            </h2>
            <p className="text-xl text-gray-400 mb-8">
              Join millions of traders on the world's most advanced exchange
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-12 py-5 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-lg font-semibold text-xl shadow-glow hover:shadow-glow-lg transition-all"
            >
              Create Free Account
            </motion.button>
          </motion.div>
        </div>
      </section>
    </main>
  )
}

const features = [
  {
    icon: Zap,
    title: 'Ultra-Low Latency',
    description: 'Sub-microsecond order execution with our C++ matching engine'
  },
  {
    icon: Shield,
    title: 'Bank-Grade Security',
    description: 'Multi-layer security with cold storage and insurance fund'
  },
  {
    icon: TrendingUp,
    title: '260+ Features',
    description: 'Most comprehensive feature set in the industry'
  },
  {
    icon: Globe,
    title: 'Global Liquidity',
    description: 'Deep liquidity across 1000+ trading pairs'
  },
  {
    icon: BarChart3,
    title: 'Advanced Trading',
    description: 'Spot, margin, futures, options, and more'
  },
  {
    icon: Wallet,
    title: 'Multi-Asset Support',
    description: 'Trade crypto, NFTs, and tokenized assets'
  }
]

const stats = [
  { value: '260+', label: 'Features' },
  { value: '1M+', label: 'TPS' },
  { value: '<1μs', label: 'Latency' },
  { value: '99.99%', label: 'Uptime' }
]

const technologies = [
  { name: 'C++', icon: '⚡' },
  { name: 'Rust', icon: '🦀' },
  { name: 'Go', icon: '🚀' },
  { name: 'Python', icon: '🐍' },
  { name: 'TypeScript', icon: '📘' },
  { name: 'Next.js', icon: '▲' },
  { name: 'React', icon: '⚛️' },
  { name: 'Vue.js', icon: '💚' },
  { name: 'Node.js', icon: '🟢' },
  { name: 'Solidity', icon: '💎' },
  { name: 'Java', icon: '☕' },
  { name: 'Kotlin', icon: '🎯' }
]