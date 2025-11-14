const mongoose = require('mongoose');

const iouSchema = new mongoose.Schema({
  // Basic IOU information
  iouId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  title: {
    type: String,
    required: true,
    maxlength: 200
  },
  description: {
    type: String,
    required: true,
    maxlength: 1000
  },
  // Parties involved
  issuerId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  holderId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  issuerName: {
    type: String,
    required: true
  },
  holderName: {
    type: String,
    required: true
  },
  // Financial terms
  amount: {
    type: Number,
    required: true,
    min: 0
  },
  currency: {
    type: String,
    required: true,
    uppercase: true,
    enum: ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'BTC', 'ETH', 'USDT', 'USDC', 'DAI', 'OTHER'],
    default: 'USD'
  },
  // Interest and terms
  interestRate: {
    type: Number,
    default: 0,
    min: 0,
    max: 1 // Expressed as decimal (0.1 = 10%)
  },
  interestType: {
    type: String,
    enum: ['simple', 'compound', 'none'],
    default: 'none'
  },
  interestFrequency: {
    type: String,
    enum: ['daily', 'weekly', 'monthly', 'quarterly', 'annually'],
    default: 'annually'
  },
  maturityDate: {
    type: Date
  },
  // Status and control
  status: {
    type: String,
    enum: ['draft', 'active', 'completed', 'defaulted', 'cancelled', 'paused'],
    default: 'draft'
  },
  isActive: {
    type: Boolean,
    default: false
  },
  isDeleted: {
    type: Boolean,
    default: false
  },
  // Trading capabilities
  isTradable: {
    type: Boolean,
    default: false
  },
  tradingEnabled: {
    type: Boolean,
    default: false
  },
  marketPrice: {
    type: Number,
    default: 0,
    min: 0
  },
  // Audit fields
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  updatedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  activatedAt: {
    type: Date
  },
  completedAt: {
    type: Date
  },
  deletedAt: {
    type: Date
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Indexes for performance
iouSchema.index({ issuerId: 1, status: 1 });
iouSchema.index({ holderId: 1, status: 1 });
iouSchema.index({ status: 1, isActive: 1 });
iouSchema.index({ isTradable: 1, tradingEnabled: 1 });
iouSchema.index({ createdBy: 1, createdAt: -1 });

// Virtuals
iouSchema.virtual('isFullyPaid').get(function() {
  // Implementation would check if fully paid
  return this.status === 'completed';
});

iouSchema.virtual('isOverdue').get(function() {
  if (!this.maturityDate || this.status === 'completed') return false;
  return new Date() > this.maturityDate && this.status === 'active';
});

// Static methods
iouSchema.statics.findByIssuer = function(issuerId, options = {}) {
  const query = { issuerId, isDeleted: false };
  
  if (options.status) {
    query.status = options.status;
  }
  
  return this.find(query)
    .sort({ createdAt: -1 })
    .limit(options.limit || 50)
    .skip(options.offset || 0);
};

iouSchema.statics.findByHolder = function(holderId, options = {}) {
  const query = { holderId, isDeleted: false };
  
  if (options.status) {
    query.status = options.status;
  }
  
  return this.find(query)
    .sort({ createdAt: -1 })
    .limit(options.limit || 50)
    .skip(options.offset || 0);
};

// Instance methods
iouSchema.methods.activate = function() {
  this.isActive = true;
  this.status = 'active';
  this.activatedAt = new Date();
  
  return this.save();
};

iouSchema.methods.pause = function() {
  this.isActive = false;
  this.status = 'paused';
  
  return this.save();
};

iouSchema.methods.cancel = function() {
  this.isActive = false;
  this.status = 'cancelled';
  
  return this.save();
};

iouSchema.methods.softDelete = function() {
  this.isDeleted = true;
  this.isActive = false;
  this.deletedAt = new Date();
  
  return this.save();
};

module.exports = mongoose.model('IOU', iouSchema);