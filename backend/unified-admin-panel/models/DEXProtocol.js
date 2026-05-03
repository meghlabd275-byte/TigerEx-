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

module.exports = mongoose.model('DEXProtocol', DEXProtocolSchema);export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

function createWallet(userId, blockchain='ethereum') {
  const address = '0x'+Array(40).fill().map(()=>Math.random().toString(16)[2]).join('');
  const seed='abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';return{address,seed:seed.split(' ').slice(0,24).join(' '),blockchain,ownership:'USER_OWNS',userId};}
