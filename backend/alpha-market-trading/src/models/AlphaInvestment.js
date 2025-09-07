const mongoose = require('mongoose');

const alphaInvestmentSchema = new mongoose.Schema({
  // Investment identification
  investmentId: {
    type: String,
    required: true,
    unique: true,
    index: true,
  },

  // References
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true,
  },
  tokenId: {
    type: String,
    ref: 'AlphaToken',
    required: true,
    index: true,
  },

  // Investment details
  investmentAmount: {
    type: Number,
    required: true,
    min: 0,
  },
  tokenAmount: {
    type: Number,
    required: true,
    min: 0,
  },
  pricePerToken: {
    type: Number,
    required: true,
    min: 0,
  },

  // User tier at time of investment
  userTier: {
    type: String,
    enum: ['bronze', 'silver', 'gold', 'platinum'],
    required: true,
  },
  userStakeAmount: {
    type: Number,
    required: true,
    min: 0,
  },

  // Transaction details
  transactionHash: {
    type: String,
    sparse: true,
  },
  blockchain: {
    type: String,
    required: true,
  },
  paymentMethod: {
    type: String,
    enum: ['USDT', 'USDC', 'ETH', 'BNB', 'MATIC', 'AVAX'],
    required: true,
  },

  // Status tracking
  status: {
    type: String,
    enum: ['pending', 'confirmed', 'failed', 'refunded', 'vested'],
    default: 'pending',
  },
  confirmationBlocks: {
    type: Number,
    default: 0,
  },
  requiredConfirmations: {
    type: Number,
    default: 12,
  },

  // Vesting information
  vestingSchedule: [
    {
      releaseDate: Date,
      percentage: Number,
      tokenAmount: Number,
      status: {
        type: String,
        enum: ['pending', 'released', 'claimed'],
        default: 'pending',
      },
      claimedAt: Date,
      transactionHash: String,
    },
  ],
  totalVested: {
    type: Number,
    default: 0,
  },
  totalClaimed: {
    type: Number,
    default: 0,
  },

  // Risk assessment at time of investment
  riskScore: {
    type: Number,
    min: 0,
    max: 100,
  },
  riskAcknowledged: {
    type: Boolean,
    default: false,
  },

  // KYC and compliance
  kycStatus: {
    type: String,
    enum: ['pending', 'approved', 'rejected'],
    default: 'pending',
  },
  kycDocuments: [
    {
      type: String,
      url: String,
      uploadedAt: Date,
    },
  ],

  // Referral information
  referralCode: String,
  referredBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
  },
  referralBonus: {
    type: Number,
    default: 0,
  },

  // Analytics and tracking
  investmentSource: {
    type: String,
    enum: ['web', 'mobile', 'api', 'telegram'],
    default: 'web',
  },
  ipAddress: String,
  userAgent: String,

  // Timestamps
  investedAt: {
    type: Date,
    default: Date.now,
  },
  confirmedAt: Date,
  firstVestingDate: Date,
  lastClaimDate: Date,

  createdAt: {
    type: Date,
    default: Date.now,
  },
  updatedAt: {
    type: Date,
    default: Date.now,
  },
});

// Compound indexes for performance
alphaInvestmentSchema.index({ userId: 1, tokenId: 1 });
alphaInvestmentSchema.index({ status: 1, investedAt: -1 });
alphaInvestmentSchema.index({ tokenId: 1, status: 1 });
alphaInvestmentSchema.index({ transactionHash: 1 }, { sparse: true });

// Pre-save middleware
alphaInvestmentSchema.pre('save', function (next) {
  this.updatedAt = new Date();
  next();
});

// Virtual for remaining vesting
alphaInvestmentSchema.virtual('remainingVesting').get(function () {
  return this.tokenAmount - this.totalClaimed;
});

// Virtual for vesting progress
alphaInvestmentSchema.virtual('vestingProgress').get(function () {
  return (this.totalClaimed / this.tokenAmount) * 100;
});

// Methods
alphaInvestmentSchema.methods.isConfirmed = function () {
  return (
    this.status === 'confirmed' &&
    this.confirmationBlocks >= this.requiredConfirmations
  );
};

alphaInvestmentSchema.methods.canClaim = function () {
  const now = new Date();
  return this.vestingSchedule.some(
    (vest) => vest.releaseDate <= now && vest.status === 'released'
  );
};

alphaInvestmentSchema.methods.getClaimableAmount = function () {
  const now = new Date();
  return this.vestingSchedule
    .filter((vest) => vest.releaseDate <= now && vest.status === 'released')
    .reduce((total, vest) => total + vest.tokenAmount, 0);
};

alphaInvestmentSchema.methods.processVesting = function () {
  const now = new Date();
  let updated = false;

  this.vestingSchedule.forEach((vest) => {
    if (vest.releaseDate <= now && vest.status === 'pending') {
      vest.status = 'released';
      this.totalVested += vest.tokenAmount;
      updated = true;
    }
  });

  if (updated) {
    return this.save();
  }
  return Promise.resolve(this);
};

alphaInvestmentSchema.methods.claimTokens = function (amount, transactionHash) {
  const claimableAmount = this.getClaimableAmount();
  if (amount > claimableAmount) {
    throw new Error('Insufficient claimable tokens');
  }

  let remainingAmount = amount;
  this.vestingSchedule.forEach((vest) => {
    if (vest.status === 'released' && remainingAmount > 0) {
      const claimAmount = Math.min(vest.tokenAmount, remainingAmount);
      vest.status = 'claimed';
      vest.claimedAt = new Date();
      vest.transactionHash = transactionHash;
      remainingAmount -= claimAmount;
    }
  });

  this.totalClaimed += amount;
  this.lastClaimDate = new Date();

  return this.save();
};

// Static methods
alphaInvestmentSchema.statics.getUserInvestments = function (
  userId,
  options = {}
) {
  const query = { userId };
  if (options.status) query.status = options.status;
  if (options.tokenId) query.tokenId = options.tokenId;

  return this.find(query)
    .populate('tokenId')
    .sort({ investedAt: -1 })
    .limit(options.limit || 50);
};

alphaInvestmentSchema.statics.getTokenInvestments = function (
  tokenId,
  options = {}
) {
  const query = { tokenId };
  if (options.status) query.status = options.status;

  return this.find(query)
    .populate('userId', 'email username')
    .sort({ investedAt: -1 })
    .limit(options.limit || 100);
};

alphaInvestmentSchema.statics.getInvestmentStats = function (tokenId) {
  return this.aggregate([
    { $match: { tokenId, status: 'confirmed' } },
    {
      $group: {
        _id: null,
        totalInvestments: { $sum: 1 },
        totalAmount: { $sum: '$investmentAmount' },
        totalTokens: { $sum: '$tokenAmount' },
        averageInvestment: { $avg: '$investmentAmount' },
        uniqueInvestors: { $addToSet: '$userId' },
      },
    },
    {
      $project: {
        totalInvestments: 1,
        totalAmount: 1,
        totalTokens: 1,
        averageInvestment: 1,
        uniqueInvestors: { $size: '$uniqueInvestors' },
      },
    },
  ]);
};

module.exports = mongoose.model('AlphaInvestment', alphaInvestmentSchema);
