const mongoose = require('mongoose');

const alphaTokenSchema = new mongoose.Schema({
  // Basic token information
  tokenId: {
    type: String,
    required: true,
    unique: true,
    index: true,
  },
  name: {
    type: String,
    required: true,
    trim: true,
  },
  symbol: {
    type: String,
    required: true,
    uppercase: true,
    trim: true,
  },
  description: {
    type: String,
    required: true,
  },

  // Contract information
  contractAddress: {
    type: String,
    sparse: true, // Allow null but unique when present
  },
  blockchain: {
    type: String,
    required: true,
    enum: [
      'ethereum',
      'bsc',
      'polygon',
      'arbitrum',
      'optimism',
      'avalanche',
      'fantom',
      'solana',
    ],
  },
  decimals: {
    type: Number,
    default: 18,
  },

  // Alpha market specific data
  launchPhase: {
    type: String,
    enum: ['pre_alpha', 'alpha', 'beta', 'public', 'launched'],
    default: 'pre_alpha',
  },
  alphaStartDate: {
    type: Date,
    required: true,
  },
  alphaEndDate: {
    type: Date,
    required: true,
  },
  publicLaunchDate: {
    type: Date,
  },

  // Pricing and allocation
  alphaPrice: {
    type: Number,
    required: true,
    min: 0,
  },
  totalSupply: {
    type: Number,
    required: true,
    min: 0,
  },
  alphaAllocation: {
    type: Number,
    required: true,
    min: 0,
  },
  soldAmount: {
    type: Number,
    default: 0,
    min: 0,
  },
  minInvestment: {
    type: Number,
    default: 100,
    min: 0,
  },
  maxInvestment: {
    type: Number,
    default: 10000,
    min: 0,
  },

  // Investor requirements
  tierRequirements: {
    bronze: {
      minStake: { type: Number, default: 1000 },
      allocation: { type: Number, default: 0.1 },
    },
    silver: {
      minStake: { type: Number, default: 5000 },
      allocation: { type: Number, default: 0.3 },
    },
    gold: {
      minStake: { type: Number, default: 25000 },
      allocation: { type: Number, default: 0.6 },
    },
    platinum: {
      minStake: { type: Number, default: 100000 },
      allocation: { type: Number, default: 1.0 },
    },
  },

  // Risk assessment
  riskScore: {
    type: Number,
    min: 0,
    max: 100,
    default: 50,
  },
  riskFactors: [
    {
      factor: String,
      score: Number,
      description: String,
    },
  ],

  // Project information
  projectTeam: [
    {
      name: String,
      role: String,
      linkedin: String,
      experience: String,
    },
  ],
  whitepaper: {
    url: String,
    hash: String,
  },
  website: String,
  socialLinks: {
    twitter: String,
    telegram: String,
    discord: String,
    medium: String,
  },

  // Vesting schedule
  vestingSchedule: [
    {
      releaseDate: Date,
      percentage: Number,
      description: String,
    },
  ],

  // Status and flags
  status: {
    type: String,
    enum: [
      'pending',
      'approved',
      'rejected',
      'active',
      'completed',
      'cancelled',
    ],
    default: 'pending',
  },
  isKYCRequired: {
    type: Boolean,
    default: true,
  },
  isWhitelisted: {
    type: Boolean,
    default: false,
  },

  // Analytics
  totalInvestors: {
    type: Number,
    default: 0,
  },
  averageInvestment: {
    type: Number,
    default: 0,
  },

  // Metadata
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
  },
  approvedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Admin',
  },
  approvedAt: Date,

  // Timestamps
  createdAt: {
    type: Date,
    default: Date.now,
  },
  updatedAt: {
    type: Date,
    default: Date.now,
  },
});

// Indexes for performance
alphaTokenSchema.index({ launchPhase: 1, status: 1 });
alphaTokenSchema.index({ alphaStartDate: 1, alphaEndDate: 1 });
alphaTokenSchema.index({ blockchain: 1 });
alphaTokenSchema.index({ riskScore: 1 });

// Pre-save middleware
alphaTokenSchema.pre('save', function (next) {
  this.updatedAt = new Date();
  next();
});

// Virtual for remaining allocation
alphaTokenSchema.virtual('remainingAllocation').get(function () {
  return this.alphaAllocation - this.soldAmount;
});

// Virtual for progress percentage
alphaTokenSchema.virtual('progressPercentage').get(function () {
  return (this.soldAmount / this.alphaAllocation) * 100;
});

// Methods
alphaTokenSchema.methods.isAlphaActive = function () {
  const now = new Date();
  return (
    now >= this.alphaStartDate &&
    now <= this.alphaEndDate &&
    this.status === 'active'
  );
};

alphaTokenSchema.methods.canInvest = function (amount, userTier) {
  if (!this.isAlphaActive()) return false;
  if (amount < this.minInvestment || amount > this.maxInvestment) return false;
  if (this.remainingAllocation < amount) return false;

  const tierAllocation = this.tierRequirements[userTier]?.allocation || 0;
  return tierAllocation > 0;
};

alphaTokenSchema.methods.updateSoldAmount = function (amount) {
  this.soldAmount += amount;
  this.totalInvestors += 1;
  this.averageInvestment = this.soldAmount / this.totalInvestors;
  return this.save();
};

module.exports = mongoose.model('AlphaToken', alphaTokenSchema);
