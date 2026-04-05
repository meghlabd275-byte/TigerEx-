const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

const transactionSchema = new mongoose.Schema(
  {
    // Transaction Identification
    transactionId: {
      type: String,
      unique: true,
      required: true,
      default: () => `TXN_${Date.now()}_${uuidv4().substr(0, 8)}`,
    },

    // User and Wallet References
    userId: {
      type: String,
      required: true,
      index: true,
    },
    walletId: {
      type: String,
      required: true,
      index: true,
    },

    // Transaction Details
    type: {
      type: String,
      enum: [
        'DEPOSIT',
        'WITHDRAWAL',
        'TRADE_BUY',
        'TRADE_SELL',
        'TRANSFER_IN',
        'TRANSFER_OUT',
        'STAKING_REWARD',
        'REFERRAL_BONUS',
        'AIRDROP',
        'FEE_DEDUCTION',
        'ADJUSTMENT',
      ],
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

    // Amount Information
    amount: {
      type: mongoose.Schema.Types.Decimal128,
      required: true,
    },
    fee: {
      type: mongoose.Schema.Types.Decimal128,
      default: 0,
    },
    netAmount: {
      type: mongoose.Schema.Types.Decimal128,
      required: true,
    },

    // Balance Information (before and after)
    balanceBefore: {
      available: {
        type: mongoose.Schema.Types.Decimal128,
        required: true,
      },
      locked: {
        type: mongoose.Schema.Types.Decimal128,
        required: true,
      },
    },
    balanceAfter: {
      available: {
        type: mongoose.Schema.Types.Decimal128,
        required: true,
      },
      locked: {
        type: mongoose.Schema.Types.Decimal128,
        required: true,
      },
    },

    // Transaction Status
    status: {
      type: String,
      enum: [
        'PENDING',
        'PROCESSING',
        'COMPLETED',
        'FAILED',
        'CANCELLED',
        'EXPIRED',
      ],
      default: 'PENDING',
      index: true,
    },

    // Blockchain Information
    blockchain: {
      txHash: String,
      blockNumber: Number,
      blockHash: String,
      confirmations: {
        type: Number,
        default: 0,
      },
      requiredConfirmations: {
        type: Number,
        default: 1,
      },
      fromAddress: String,
      toAddress: String,
      gasUsed: Number,
      gasPrice: String,
      nonce: Number,
    },

    // External References
    externalId: String, // Reference to external system
    orderId: String, // Reference to trading order
    referenceId: String, // General reference field

    // Processing Information
    processing: {
      attempts: {
        type: Number,
        default: 0,
      },
      lastAttempt: Date,
      nextAttempt: Date,
      errorMessage: String,
      processingNode: String,
    },

    // Metadata
    metadata: {
      source: {
        type: String,
        enum: ['WEB', 'MOBILE', 'API', 'SYSTEM', 'ADMIN'],
        default: 'SYSTEM',
      },
      ipAddress: String,
      userAgent: String,
      description: String,
      tags: [String],
      notes: String,
    },

    // Timestamps
    initiatedAt: {
      type: Date,
      default: Date.now,
    },
    processedAt: Date,
    completedAt: Date,

    // Risk and Compliance
    riskScore: {
      type: Number,
      default: 0,
      min: 0,
      max: 100,
    },
    flagged: {
      type: Boolean,
      default: false,
    },
    flagReason: String,

    // Audit Trail
    auditTrail: [
      {
        action: String,
        timestamp: {
          type: Date,
          default: Date.now,
        },
        userId: String,
        details: mongoose.Schema.Types.Mixed,
      },
    ],
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
  }
);

// Indexes
transactionSchema.index({ userId: 1, createdAt: -1 });
transactionSchema.index({ walletId: 1, createdAt: -1 });
transactionSchema.index({ type: 1, status: 1 });
transactionSchema.index({ currency: 1, createdAt: -1 });
transactionSchema.index({ 'blockchain.txHash': 1 });
transactionSchema.index({ status: 1, 'processing.nextAttempt': 1 });
transactionSchema.index({ externalId: 1 });
transactionSchema.index({ orderId: 1 });

// Virtual fields
transactionSchema.virtual('isCompleted').get(function () {
  return this.status === 'COMPLETED';
});

transactionSchema.virtual('isPending').get(function () {
  return ['PENDING', 'PROCESSING'].includes(this.status);
});

transactionSchema.virtual('hasFailed').get(function () {
  return ['FAILED', 'CANCELLED', 'EXPIRED'].includes(this.status);
});

transactionSchema.virtual('confirmationProgress').get(function () {
  if (!this.blockchain.requiredConfirmations) return 100;
  return Math.min(
    100,
    (this.blockchain.confirmations / this.blockchain.requiredConfirmations) *
      100
  );
});

// Pre-save middleware
transactionSchema.pre('save', function (next) {
  // Calculate net amount if not set
  if (!this.netAmount) {
    this.netAmount = parseFloat(this.amount) - parseFloat(this.fee || 0);
  }

  // Set processed timestamp when status changes to processing
  if (
    this.isModified('status') &&
    this.status === 'PROCESSING' &&
    !this.processedAt
  ) {
    this.processedAt = new Date();
  }

  // Set completed timestamp when status changes to completed
  if (
    this.isModified('status') &&
    this.status === 'COMPLETED' &&
    !this.completedAt
  ) {
    this.completedAt = new Date();
  }

  next();
});

// Methods
transactionSchema.methods.addAuditEntry = function (
  action,
  userId,
  details = {}
) {
  this.auditTrail.push({
    action,
    userId,
    details,
    timestamp: new Date(),
  });
};

transactionSchema.methods.updateStatus = function (
  newStatus,
  userId,
  details = {}
) {
  const oldStatus = this.status;
  this.status = newStatus;

  this.addAuditEntry(
    `STATUS_CHANGE_${oldStatus}_TO_${newStatus}`,
    userId,
    details
  );

  // Update processing information
  if (newStatus === 'FAILED') {
    this.processing.attempts += 1;
    this.processing.lastAttempt = new Date();
    this.processing.errorMessage = details.error || 'Unknown error';
  }
};

transactionSchema.methods.updateConfirmations = function (confirmations) {
  this.blockchain.confirmations = confirmations;

  // Auto-complete if enough confirmations
  if (
    confirmations >= this.blockchain.requiredConfirmations &&
    this.status === 'PROCESSING'
  ) {
    this.status = 'COMPLETED';
    this.completedAt = new Date();
  }
};

transactionSchema.methods.scheduleRetry = function (delayMinutes = 5) {
  this.processing.nextAttempt = new Date(Date.now() + delayMinutes * 60 * 1000);
  this.processing.attempts += 1;
};

transactionSchema.methods.flag = function (reason, userId) {
  this.flagged = true;
  this.flagReason = reason;
  this.addAuditEntry('FLAGGED', userId, { reason });
};

transactionSchema.methods.toSafeObject = function () {
  const obj = this.toObject();

  // Remove sensitive information
  delete obj._id;
  delete obj.__v;
  delete obj.processing.errorMessage;

  return obj;
};

// Static methods
transactionSchema.statics.findByUserId = function (userId, filters = {}) {
  const query = { userId, ...filters };
  return this.find(query).sort({ createdAt: -1 });
};

transactionSchema.statics.findPendingTransactions = function (type = null) {
  const query = {
    status: { $in: ['PENDING', 'PROCESSING'] },
    $or: [
      { 'processing.nextAttempt': { $lte: new Date() } },
      { 'processing.nextAttempt': { $exists: false } },
    ],
  };

  if (type) {
    query.type = type;
  }

  return this.find(query).sort({ createdAt: 1 });
};

transactionSchema.statics.getTransactionHistory = function (
  userId,
  filters = {}
) {
  const {
    currency,
    type,
    status,
    startDate,
    endDate,
    limit = 50,
    skip = 0,
  } = filters;

  const query = { userId };

  if (currency) query.currency = currency.toUpperCase();
  if (type) query.type = type;
  if (status) query.status = status;

  if (startDate || endDate) {
    query.createdAt = {};
    if (startDate) query.createdAt.$gte = new Date(startDate);
    if (endDate) query.createdAt.$lte = new Date(endDate);
  }

  return this.find(query)
    .sort({ createdAt: -1 })
    .limit(parseInt(limit))
    .skip(parseInt(skip));
};

transactionSchema.statics.getTransactionStats = function (
  userId,
  period = '24h'
) {
  const periodMap = {
    '1h': 1 * 60 * 60 * 1000,
    '24h': 24 * 60 * 60 * 1000,
    '7d': 7 * 24 * 60 * 60 * 1000,
    '30d': 30 * 24 * 60 * 60 * 1000,
  };

  const startTime = new Date(
    Date.now() - (periodMap[period] || periodMap['24h'])
  );

  return this.aggregate([
    {
      $match: {
        userId: userId,
        createdAt: { $gte: startTime },
        status: 'COMPLETED',
      },
    },
    {
      $group: {
        _id: {
          type: '$type',
          currency: '$currency',
        },
        count: { $sum: 1 },
        totalAmount: { $sum: { $toDouble: '$amount' } },
        totalFees: { $sum: { $toDouble: '$fee' } },
      },
    },
  ]);
};

transactionSchema.statics.findByTxHash = function (txHash) {
  return this.findOne({ 'blockchain.txHash': txHash });
};

module.exports = mongoose.model('Transaction', transactionSchema);
