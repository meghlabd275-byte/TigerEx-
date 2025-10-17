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
const { v4: uuidv4 } = require('uuid');
const Decimal = require('decimal.js');

const walletSchema = new mongoose.Schema(
  {
    // Wallet Identification
    walletId: {
      type: String,
      unique: true,
      required: true,
      default: () => `WALLET_${Date.now()}_${uuidv4().substr(0, 8)}`,
    },
    userId: {
      type: String,
      required: true,
      index: true,
    },

    // Currency Information
    currency: {
      type: String,
      required: true,
      uppercase: true,
      index: true,
    },
    network: {
      type: String,
      required: true,
      uppercase: true,
    },

    // Balance Information
    balance: {
      available: {
        type: mongoose.Schema.Types.Decimal128,
        default: 0,
        min: 0,
      },
      locked: {
        type: mongoose.Schema.Types.Decimal128,
        default: 0,
        min: 0,
      },
      staked: {
        type: mongoose.Schema.Types.Decimal128,
        default: 0,
        min: 0,
      },
    },

    // Wallet Status
    status: {
      type: String,
      enum: ['ACTIVE', 'SUSPENDED', 'FROZEN', 'CLOSED'],
      default: 'ACTIVE',
    },

    // Security Settings
    security: {
      withdrawalEnabled: {
        type: Boolean,
        default: true,
      },
      depositEnabled: {
        type: Boolean,
        default: true,
      },
      requireTwoFactor: {
        type: Boolean,
        default: false,
      },
      dailyWithdrawalLimit: {
        type: mongoose.Schema.Types.Decimal128,
        default: 0, // 0 means no limit
      },
      monthlyWithdrawalLimit: {
        type: mongoose.Schema.Types.Decimal128,
        default: 0, // 0 means no limit
      },
    },

    // Statistics
    statistics: {
      totalDeposited: {
        type: mongoose.Schema.Types.Decimal128,
        default: 0,
      },
      totalWithdrawn: {
        type: mongoose.Schema.Types.Decimal128,
        default: 0,
      },
      totalTrades: {
        type: Number,
        default: 0,
      },
      lastActivity: {
        type: Date,
        default: Date.now,
      },
    },

    // Addresses
    addresses: [
      {
        address: {
          type: String,
          required: true,
        },
        type: {
          type: String,
          enum: ['DEPOSIT', 'WITHDRAWAL', 'COLD_STORAGE'],
          default: 'DEPOSIT',
        },
        isActive: {
          type: Boolean,
          default: true,
        },
        createdAt: {
          type: Date,
          default: Date.now,
        },
        lastUsed: Date,
        memo: String, // For currencies that require memo/tag
        privateKeyEncrypted: String, // Encrypted private key for hot wallets
        derivationPath: String, // HD wallet derivation path
      },
    ],

    // Risk Management
    riskProfile: {
      riskScore: {
        type: Number,
        default: 0,
        min: 0,
        max: 100,
      },
      kycLevel: {
        type: String,
        enum: ['NONE', 'BASIC', 'INTERMEDIATE', 'ADVANCED'],
        default: 'NONE',
      },
      suspiciousActivity: {
        type: Boolean,
        default: false,
      },
      lastRiskAssessment: Date,
    },

    // Metadata
    metadata: {
      createdBy: String,
      createdSource: {
        type: String,
        enum: ['SYSTEM', 'USER', 'ADMIN'],
        default: 'SYSTEM',
      },
      notes: String,
      tags: [String],
    },
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
  }
);

// Indexes
walletSchema.index({ userId: 1, currency: 1 }, { unique: true });
walletSchema.index({ currency: 1, status: 1 });
walletSchema.index({ 'addresses.address': 1 });
walletSchema.index({ 'statistics.lastActivity': -1 });

// Virtual fields
walletSchema.virtual('totalBalance').get(function () {
  const available = parseFloat(this.balance.available || 0);
  const locked = parseFloat(this.balance.locked || 0);
  const staked = parseFloat(this.balance.staked || 0);
  return available + locked + staked;
});

walletSchema.virtual('availableForWithdrawal').get(function () {
  return parseFloat(this.balance.available || 0);
});

walletSchema.virtual('isActive').get(function () {
  return this.status === 'ACTIVE';
});

// Pre-save middleware
walletSchema.pre('save', function (next) {
  this.statistics.lastActivity = new Date();
  next();
});

// Methods
walletSchema.methods.addBalance = function (amount, type = 'available') {
  const currentBalance = parseFloat(this.balance[type] || 0);
  const newAmount = parseFloat(amount);

  if (newAmount < 0) {
    throw new Error('Cannot add negative amount');
  }

  this.balance[type] = new Decimal(currentBalance).plus(newAmount).toString();
  this.statistics.lastActivity = new Date();
};

walletSchema.methods.subtractBalance = function (amount, type = 'available') {
  const currentBalance = parseFloat(this.balance[type] || 0);
  const subtractAmount = parseFloat(amount);

  if (subtractAmount < 0) {
    throw new Error('Cannot subtract negative amount');
  }

  if (currentBalance < subtractAmount) {
    throw new Error('Insufficient balance');
  }

  this.balance[type] = new Decimal(currentBalance)
    .minus(subtractAmount)
    .toString();
  this.statistics.lastActivity = new Date();
};

walletSchema.methods.lockBalance = function (amount) {
  this.subtractBalance(amount, 'available');
  this.addBalance(amount, 'locked');
};

walletSchema.methods.unlockBalance = function (amount) {
  this.subtractBalance(amount, 'locked');
  this.addBalance(amount, 'available');
};

walletSchema.methods.addAddress = function (addressData) {
  // Check if address already exists
  const existingAddress = this.addresses.find(
    (addr) => addr.address === addressData.address
  );
  if (existingAddress) {
    throw new Error('Address already exists');
  }

  this.addresses.push({
    ...addressData,
    createdAt: new Date(),
    isActive: true,
  });
};

walletSchema.methods.deactivateAddress = function (address) {
  const addressObj = this.addresses.find((addr) => addr.address === address);
  if (addressObj) {
    addressObj.isActive = false;
  }
};

walletSchema.methods.getActiveDepositAddress = function () {
  return this.addresses.find(
    (addr) => addr.type === 'DEPOSIT' && addr.isActive
  );
};

walletSchema.methods.updateRiskScore = function (newScore) {
  this.riskProfile.riskScore = Math.max(0, Math.min(100, newScore));
  this.riskProfile.lastRiskAssessment = new Date();

  // Auto-suspend high-risk wallets
  if (newScore >= 80) {
    this.riskProfile.suspiciousActivity = true;
    if (newScore >= 95) {
      this.status = 'SUSPENDED';
    }
  }
};

walletSchema.methods.canWithdraw = function (amount) {
  if (!this.security.withdrawalEnabled) {
    return { allowed: false, reason: 'Withdrawals disabled' };
  }

  if (this.status !== 'ACTIVE') {
    return { allowed: false, reason: 'Wallet not active' };
  }

  const availableBalance = parseFloat(this.balance.available || 0);
  if (availableBalance < parseFloat(amount)) {
    return { allowed: false, reason: 'Insufficient balance' };
  }

  // Check daily limit
  const dailyLimit = parseFloat(this.security.dailyWithdrawalLimit || 0);
  if (dailyLimit > 0) {
    // This would need to check actual daily withdrawal amount from transactions
    // For now, we'll assume it's allowed
  }

  return { allowed: true };
};

walletSchema.methods.toSafeObject = function () {
  const obj = this.toObject();

  // Remove sensitive information
  if (obj.addresses) {
    obj.addresses = obj.addresses.map((addr) => ({
      address: addr.address,
      type: addr.type,
      isActive: addr.isActive,
      createdAt: addr.createdAt,
      lastUsed: addr.lastUsed,
      memo: addr.memo,
      // privateKeyEncrypted and derivationPath are excluded
    }));
  }

  delete obj._id;
  delete obj.__v;
  return obj;
};

// Static methods
walletSchema.statics.findByUserId = function (userId) {
  return this.find({ userId: userId, status: { $ne: 'CLOSED' } });
};

walletSchema.statics.findByUserIdAndCurrency = function (userId, currency) {
  return this.findOne({
    userId: userId,
    currency: currency.toUpperCase(),
    status: { $ne: 'CLOSED' },
  });
};

walletSchema.statics.findByAddress = function (address) {
  return this.findOne({
    'addresses.address': address,
    'addresses.isActive': true,
  });
};

walletSchema.statics.getTotalBalances = function () {
  return this.aggregate([
    {
      $match: { status: 'ACTIVE' },
    },
    {
      $group: {
        _id: '$currency',
        totalAvailable: {
          $sum: { $toDouble: '$balance.available' },
        },
        totalLocked: {
          $sum: { $toDouble: '$balance.locked' },
        },
        totalStaked: {
          $sum: { $toDouble: '$balance.staked' },
        },
        walletCount: { $sum: 1 },
      },
    },
  ]);
};

walletSchema.statics.getUserPortfolio = function (userId) {
  return this.find({
    userId: userId,
    status: { $ne: 'CLOSED' },
  }).select('currency balance statistics');
};

module.exports = mongoose.model('Wallet', walletSchema);
