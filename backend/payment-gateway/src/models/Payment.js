const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

const paymentSchema = new mongoose.Schema(
  {
    // Payment Identification
    paymentId: {
      type: String,
      unique: true,
      required: true,
      default: () => `PAY_${Date.now()}_${uuidv4().substr(0, 8)}`,
    },

    // User Information
    userId: {
      type: String,
      required: true,
      index: true,
    },

    // Payment Details
    type: {
      type: String,
      enum: [
        'DEPOSIT',
        'WITHDRAWAL',
        'REFUND',
        'CHARGEBACK',
        'FEE_PAYMENT',
        'SUBSCRIPTION',
      ],
      required: true,
      index: true,
    },

    // Payment Method
    method: {
      type: String,
      enum: [
        'CREDIT_CARD',
        'DEBIT_CARD',
        'BANK_TRANSFER',
        'ACH',
        'WIRE_TRANSFER',
        'PAYPAL',
        'APPLE_PAY',
        'GOOGLE_PAY',
        'SEPA',
        'SWIFT',
      ],
      required: true,
      index: true,
    },

    // Currency and Amount
    currency: {
      type: String,
      required: true,
      uppercase: true,
      index: true,
    },
    amount: {
      type: mongoose.Schema.Types.Decimal128,
      required: true,
      min: 0,
    },
    fee: {
      type: mongoose.Schema.Types.Decimal128,
      default: 0,
      min: 0,
    },
    netAmount: {
      type: mongoose.Schema.Types.Decimal128,
      required: true,
      min: 0,
    },

    // Exchange Rate (for crypto conversions)
    exchangeRate: {
      type: mongoose.Schema.Types.Decimal128,
      default: 1,
    },
    cryptoCurrency: String,
    cryptoAmount: mongoose.Schema.Types.Decimal128,

    // Payment Status
    status: {
      type: String,
      enum: [
        'PENDING',
        'PROCESSING',
        'COMPLETED',
        'FAILED',
        'CANCELLED',
        'EXPIRED',
        'REFUNDED',
        'DISPUTED',
      ],
      default: 'PENDING',
      index: true,
    },

    // Provider Information
    provider: {
      name: {
        type: String,
        enum: ['STRIPE', 'PAYPAL', 'PLAID', 'BANK', 'INTERNAL'],
        required: true,
      },
      transactionId: String,
      paymentIntentId: String,
      chargeId: String,
      refundId: String,
      metadata: mongoose.Schema.Types.Mixed,
    },

    // Payment Instrument Details
    paymentInstrument: {
      type: {
        type: String,
        enum: ['CARD', 'BANK_ACCOUNT', 'WALLET', 'OTHER'],
      },
      last4: String,
      brand: String,
      country: String,
      fingerprint: String,
      bankName: String,
      accountType: String,
      routingNumber: String,
    },

    // Billing Information
    billingAddress: {
      name: String,
      line1: String,
      line2: String,
      city: String,
      state: String,
      postalCode: String,
      country: String,
    },

    // Risk and Fraud Detection
    riskAssessment: {
      score: {
        type: Number,
        default: 0,
        min: 0,
        max: 100,
      },
      level: {
        type: String,
        enum: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
        default: 'LOW',
      },
      factors: [String],
      ipAddress: String,
      deviceFingerprint: String,
      geoLocation: {
        country: String,
        region: String,
        city: String,
        latitude: Number,
        longitude: Number,
      },
    },

    // Compliance and AML
    compliance: {
      amlStatus: {
        type: String,
        enum: ['PENDING', 'APPROVED', 'REJECTED', 'REVIEW_REQUIRED'],
        default: 'PENDING',
      },
      sanctionsCheck: {
        type: String,
        enum: ['PENDING', 'CLEAR', 'HIT', 'ERROR'],
        default: 'PENDING',
      },
      kycLevel: {
        type: String,
        enum: ['NONE', 'BASIC', 'INTERMEDIATE', 'ADVANCED'],
        default: 'NONE',
      },
      reportedToAuthorities: {
        type: Boolean,
        default: false,
      },
      reportDate: Date,
      reportReference: String,
    },

    // Processing Information
    processing: {
      attempts: {
        type: Number,
        default: 0,
      },
      lastAttempt: Date,
      nextRetry: Date,
      errorCode: String,
      errorMessage: String,
      processingTime: Number, // in milliseconds
      webhookReceived: {
        type: Boolean,
        default: false,
      },
      webhookTimestamp: Date,
    },

    // Timestamps
    initiatedAt: {
      type: Date,
      default: Date.now,
    },
    processedAt: Date,
    completedAt: Date,
    expiresAt: Date,

    // Metadata
    metadata: {
      source: {
        type: String,
        enum: ['WEB', 'MOBILE', 'API', 'ADMIN'],
        default: 'WEB',
      },
      userAgent: String,
      referrer: String,
      sessionId: String,
      description: String,
      internalNotes: String,
      customerNotes: String,
      tags: [String],
    },

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
paymentSchema.index({ userId: 1, createdAt: -1 });
paymentSchema.index({ type: 1, status: 1 });
paymentSchema.index({ method: 1, currency: 1 });
paymentSchema.index({ 'provider.transactionId': 1 });
paymentSchema.index({ status: 1, 'processing.nextRetry': 1 });
paymentSchema.index({ 'compliance.amlStatus': 1 });
paymentSchema.index({ 'riskAssessment.level': 1 });

// Virtual fields
paymentSchema.virtual('isCompleted').get(function () {
  return this.status === 'COMPLETED';
});

paymentSchema.virtual('isPending').get(function () {
  return ['PENDING', 'PROCESSING'].includes(this.status);
});

paymentSchema.virtual('hasFailed').get(function () {
  return ['FAILED', 'CANCELLED', 'EXPIRED'].includes(this.status);
});

paymentSchema.virtual('totalAmount').get(function () {
  return parseFloat(this.amount) + parseFloat(this.fee || 0);
});

paymentSchema.virtual('isHighRisk').get(function () {
  return ['HIGH', 'CRITICAL'].includes(this.riskAssessment.level);
});

// Pre-save middleware
paymentSchema.pre('save', function (next) {
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

  // Set expiration time for pending payments (24 hours)
  if (this.isNew && this.status === 'PENDING' && !this.expiresAt) {
    this.expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000);
  }

  next();
});

// Methods
paymentSchema.methods.addAuditEntry = function (action, userId, details = {}) {
  this.auditTrail.push({
    action,
    userId,
    details,
    timestamp: new Date(),
  });
};

paymentSchema.methods.updateStatus = function (
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
    this.processing.errorCode = details.errorCode;
  }
};

paymentSchema.methods.updateRiskScore = function (score, factors = []) {
  this.riskAssessment.score = Math.max(0, Math.min(100, score));
  this.riskAssessment.factors = factors;

  // Update risk level based on score
  if (score >= 80) {
    this.riskAssessment.level = 'CRITICAL';
  } else if (score >= 60) {
    this.riskAssessment.level = 'HIGH';
  } else if (score >= 30) {
    this.riskAssessment.level = 'MEDIUM';
  } else {
    this.riskAssessment.level = 'LOW';
  }
};

paymentSchema.methods.scheduleRetry = function (delayMinutes = 5) {
  this.processing.nextRetry = new Date(Date.now() + delayMinutes * 60 * 1000);
  this.processing.attempts += 1;
};

paymentSchema.methods.toSafeObject = function () {
  const obj = this.toObject();

  // Remove sensitive information
  delete obj._id;
  delete obj.__v;
  delete obj.processing.errorMessage;
  delete obj.metadata.internalNotes;
  delete obj.paymentInstrument.fingerprint;

  return obj;
};

// Static methods
paymentSchema.statics.findByUserId = function (userId, filters = {}) {
  const query = { userId, ...filters };
  return this.find(query).sort({ createdAt: -1 });
};

paymentSchema.statics.findPendingPayments = function (type = null) {
  const query = {
    status: { $in: ['PENDING', 'PROCESSING'] },
    $or: [
      { 'processing.nextRetry': { $lte: new Date() } },
      { 'processing.nextRetry': { $exists: false } },
    ],
  };

  if (type) {
    query.type = type;
  }

  return this.find(query).sort({ createdAt: 1 });
};

paymentSchema.statics.getPaymentStats = function (userId, period = '30d') {
  const periodMap = {
    '24h': 24 * 60 * 60 * 1000,
    '7d': 7 * 24 * 60 * 60 * 1000,
    '30d': 30 * 24 * 60 * 60 * 1000,
    '90d': 90 * 24 * 60 * 60 * 1000,
  };

  const startTime = new Date(
    Date.now() - (periodMap[period] || periodMap['30d'])
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
          method: '$method',
          currency: '$currency',
        },
        count: { $sum: 1 },
        totalAmount: { $sum: { $toDouble: '$amount' } },
        totalFees: { $sum: { $toDouble: '$fee' } },
      },
    },
  ]);
};

module.exports = mongoose.model('Payment', paymentSchema);
