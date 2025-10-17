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

const mongoose = require('mongoose');

const DEXProtocolSchema = new mongoose.Schema({
  // Protocol Information
  name: { 
    type: String, 
    required: true,
    enum: [
      'uniswap-v2', 'uniswap-v3',
      'pancakeswap-v2', 'pancakeswap-v3',
      'sushiswap',
      'quickswap',
      'spookyswap',
      'traderjoe',
      'raydium',
      'tronswap',
      'apeswap',
      'biswap',
      'mdex'
    ]
  },
  displayName: { type: String, required: true },
  version: { type: String },
  
  // Blockchain
  blockchain: {
    type: String,
    required: true,
    enum: ['ethereum', 'bsc', 'polygon', 'avalanche', 'fantom', 'arbitrum', 'optimism', 'solana', 'tron']
  },
  chainId: { type: Number, required: true },
  
  // Smart Contract Addresses
  contracts: {
    router: { type: String, required: true },
    factory: { type: String, required: true },
    weth: { type: String }, // Wrapped native token
    multicall: { type: String }
  },
  
  // Protocol Configuration
  config: {
    feePercent: { type: Number, default: 0.003 }, // 0.3%
    feeTiers: [{ type: Number }], // For V3 protocols
    minLiquidity: { type: Number, default: 1000 }, // Minimum liquidity in USD
    maxSlippage: { type: Number, default: 0.05 }, // 5%
    gasLimit: { type: Number, default: 300000 }
  },
  
  // API Configuration
  api: {
    graphqlEndpoint: { type: String },
    restEndpoint: { type: String },
    websocketEndpoint: { type: String },
    apiKey: { type: String }
  },
  
  // Status
  status: {
    type: String,
    enum: ['ACTIVE', 'INACTIVE', 'MAINTENANCE'],
    default: 'ACTIVE'
  },
  
  // Statistics
  stats: {
    totalPools: { type: Number, default: 0 },
    totalVolume24h: { type: Number, default: 0 },
    totalLiquidity: { type: Number, default: 0 },
    lastUpdated: { type: Date }
  },
  
  // Features
  features: {
    supportsV3: { type: Boolean, default: false },
    supportsMultihop: { type: Boolean, default: true },
    supportsGasEstimation: { type: Boolean, default: true },
    supportsFlashSwap: { type: Boolean, default: false }
  }
}, {
  timestamps: true
});

// Indexes
DEXProtocolSchema.index({ name: 1, blockchain: 1 }, { unique: true });
DEXProtocolSchema.index({ status: 1 });
DEXProtocolSchema.index({ blockchain: 1 });

module.exports = mongoose.model('DEXProtocol', DEXProtocolSchema);