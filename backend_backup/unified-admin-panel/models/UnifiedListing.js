const mongoose = require('mongoose');

const UnifiedListingSchema = new mongoose.Schema({
  // Token Information
  tokenName: { type: String, required: true },
  tokenSymbol: { type: String, required: true, uppercase: true },
  tokenAddress: { type: String, required: true },
  blockchain: { 
    type: String, 
    required: true,
    enum: ['ethereum', 'bsc', 'polygon', 'avalanche', 'fantom', 'arbitrum', 'optimism', 'solana', 'tron']
  },
  tokenType: { 
    type: String, 
    required: true,
    enum: ['ERC20', 'BEP20', 'SPL', 'TRC20', 'Native']
  },
  decimals: { type: Number, required: true },
  totalSupply: { type: String, required: true },
  
  // Listing Type
  listingType: {
    type: String,
    required: true,
    enum: ['CEX_ONLY', 'DEX_ONLY', 'HYBRID'] // HYBRID = both CEX and DEX
  },
  
  // CEX Configuration
  cexConfig: {
    enabled: { type: Boolean, default: false },
    tradingPairs: [{ type: String }], // ['USDT', 'BTC', 'ETH']
    minimumOrderSize: { type: Number },
    makerFee: { type: Number, default: 0.001 }, // 0.1%
    takerFee: { type: Number, default: 0.002 }, // 0.2%
    status: { 
      type: String, 
      enum: ['PENDING', 'APPROVED', 'REJECTED', 'ACTIVE', 'SUSPENDED'],
      default: 'PENDING'
    }
  },
  
  // DEX Configuration
  dexConfig: {
    enabled: { type: Boolean, default: false },
    protocols: [{
      name: { type: String }, // 'uniswap', 'pancakeswap', etc.
      version: { type: String }, // 'v2', 'v3'
      poolAddress: { type: String },
      routerAddress: { type: String },
      factoryAddress: { type: String }
    }],
    liquidityPools: [{
      protocol: { type: String },
      pairToken: { type: String },
      poolAddress: { type: String },
      initialLiquidity: { type: Number },
      status: { type: String, enum: ['PENDING', 'ACTIVE', 'PAUSED'], default: 'PENDING' }
    }],
    status: { 
      type: String, 
      enum: ['PENDING', 'APPROVED', 'REJECTED', 'ACTIVE', 'SUSPENDED'],
      default: 'PENDING'
    }
  },
  
  // Project Information
  projectInfo: {
    website: { type: String },
    whitepaper: { type: String },
    description: { type: String },
    socialMedia: {
      twitter: { type: String },
      telegram: { type: String },
      discord: { type: String },
      github: { type: String }
    },
    team: [{
      name: { type: String },
      role: { type: String },
      linkedin: { type: String }
    }]
  },
  
  // Compliance & Verification
  compliance: {
    kycCompleted: { type: Boolean, default: false },
    auditReport: { type: String },
    auditCompany: { type: String },
    legalOpinion: { type: String },
    regulatoryApproval: { type: Boolean, default: false }
  },
  
  // Listing Fees
  fees: {
    listingFee: { type: Number, required: true },
    paid: { type: Boolean, default: false },
    paymentTxHash: { type: String },
    paymentDate: { type: Date }
  },
  
  // Admin Actions
  adminActions: [{
    action: { type: String }, // 'APPROVED', 'REJECTED', 'SUSPENDED', etc.
    reason: { type: String },
    adminId: { type: mongoose.Schema.Types.ObjectId, ref: 'Admin' },
    timestamp: { type: Date, default: Date.now }
  }],
  
  // Status
  overallStatus: {
    type: String,
    enum: ['DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'ACTIVE', 'SUSPENDED'],
    default: 'DRAFT'
  },
  
  // Timestamps
  submittedAt: { type: Date },
  approvedAt: { type: Date },
  listedAt: { type: Date }
}, {
  timestamps: true
});

// Indexes
UnifiedListingSchema.index({ tokenSymbol: 1, blockchain: 1 }, { unique: true });
UnifiedListingSchema.index({ overallStatus: 1 });
UnifiedListingSchema.index({ 'cexConfig.status': 1 });
UnifiedListingSchema.index({ 'dexConfig.status': 1 });

module.exports = mongoose.model('UnifiedListing', UnifiedListingSchema);