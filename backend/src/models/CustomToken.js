const mongoose = require('mongoose');

const customTokenSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    index: true
  },
  symbol: {
    type: String,
    required: true,
    uppercase: true,
    unique: true,
    index: true
  },
  contractAddress: {
    type: String,
    required: true,
    lowercase: true,
    index: true
  },
  blockchainType: {
    type: String,
    required: true,
    enum: ['evm', 'solana', 'bitcoin', 'polkadot', 'cosmos', 'avalanche', 'polygon', 'arbitrum', 'optimism', 'binance_smart_chain', 'other'],
    index: true
  },
  networkName: {
    type: String,
    required: true,
    index: true
  },
  // Token specifications
  totalSupply: {
    type: Number,
    required: true,
    min: 0
  },
  circulatingSupply: {
    type: Number,
    default: 0,
    min: 0
  },
  decimals: {
    type: Number,
    required: true,
    min: 0,
    max: 18,
    default: 18
  },
  // Visual identity
  logoUrl: {
    type: String,
    validate: {
      validator: function(v) {
        return !v || /^https?:\/\/.+\.(jpg|jpeg|png|gif|svg)$/i.test(v);
      },
      message: 'Invalid logo URL format'
    }
  },
  primaryColor: {
    type: String,
    validate: {
      validator: function(v) {
        return !v || /^#[0-9A-Fa-f]{6}$/i.test(v);
      },
      message: 'Invalid color format (use #RRGGBB)'
    }
  },
  // Token information
  description: {
    type: String,
    maxlength: 1000
  },
  website: {
    type: String,
    validate: {
      validator: function(v) {
        return !v || /^https?:\/\/.+/.test(v);
      },
      message: 'Invalid website URL'
    }
  },
  whitepaper: {
    type: String,
    validate: {
      validator: function(v) {
        return !v || /^https?:\/\/.+/.test(v);
      },
      message: 'Invalid whitepaper URL'
    }
  },
  socialLinks: {
    twitter: {
      type: String,
      validate: {
        validator: function(v) {
          return !v || /^https?:\/\/(www\.)?twitter\.com\/.+/.test(v);
        },
        message: 'Invalid Twitter URL'
      }
    },
    telegram: {
      type: String,
      validate: {
        validator: function(v) {
          return !v || /^https?:\/\/(www\.)?t\.me\/.+/.test(v);
        },
        message: 'Invalid Telegram URL'
      }
    },
    discord: {
      type: String,
      validate: {
        validator: function(v) {
          return !v || /^https?:\/\/(www\.)?discord\.gg\/.+/.test(v);
        },
        message: 'Invalid Discord URL'
      }
    },
    medium: {
      type: String,
      validate: {
        validator: function(v) {
          return !v || /^https?:\/\/(www\.)?medium\.com\/.+/.test(v);
        },
        message: 'Invalid Medium URL'
      }
    }
  },
  // Token economics
  marketCap: {
    type: Number,
    default: 0,
    min: 0
  },
  price: {
    type: Number,
    default: 0,
    min: 0
  },
  priceChange24h: {
    type: Number,
    default: 0
  },
  volume24h: {
    type: Number,
    default: 0,
    min: 0
  },
  high24h: {
    type: Number,
    default: 0,
    min: 0
  },
  low24h: {
    type: Number,
    default: 0,
    min: 0
  },
  // Status and control
  status: {
    type: String,
    enum: ['active', 'paused', 'suspended', 'delisted'],
    default: 'active'
  },
  isActive: {
    type: Boolean,
    default: true,
    index: true
  },
  isVerified: {
    type: Boolean,
    default: false
  },
  isFeatured: {
    type: Boolean,
    default: false
  },
  isDeleted: {
    type: Boolean,
    default: false,
    index: true
  },
  // Features and capabilities
  features: {
    isStakable: {
      type: Boolean,
      default: false
    },
    isGovernance: {
      type: Boolean,
      default: false
    },
    isUtility: {
      type: Boolean,
      default: false
    },
    isSecurity: {
      type: Boolean,
      default: false
    },
    isDefi: {
      type: Boolean,
      default: false
    },
    isGaming: {
      type: Boolean,
      default: false
    },
    isNFT: {
      type: Boolean,
      default: false
    },
    isMetaverse: {
      type: Boolean,
      default: false
    },
    hasBurning: {
      type: Boolean,
      default: false
    },
    hasMinting: {
      type: Boolean,
      default: false
    },
    hasReflections: {
      type: Boolean,
      default: false
    }
  },
  // Trading configuration
  tradingEnabled: {
    type: Boolean,
    default: true
  },
  tradingRules: {
    minOrderSize: {
      type: Number,
      default: 0.001,
      min: 0
    },
    maxOrderSize: {
      type: Number,
      default: 1000000
    },
    maxSlippage: {
      type: Number,
      default: 0.05, // 5%
      min: 0,
      max: 1
    },
    coolingOffPeriod: {
      type: Number,
      default: 0 // 0 = no cooling off period
    }
  },
  // Blockchain specific data
  blockchainData: {
    abi: {
      type: mongoose.Schema.Types.Mixed
    },
    bytecode: {
      type: String
    },
    deploymentTxHash: {
      type: String
    },
    creator: {
      type: String
    },
    blockNumber: {
      type: Number,
      min: 0
    },
    gasLimit: {
      type: Number,
      min: 0
    },
    gasUsed: {
      type: Number,
      min: 0
    }
  },
  // Compliance and legal
  compliance: {
    kycRequired: {
      type: Boolean,
      default: false
    },
    amlCompliant: {
      type: Boolean,
      default: false
    },
    regulated: {
      type: Boolean,
      default: false
    },
    jurisdictions: [{
      type: String,
      enum: ['US', 'EU', 'UK', 'JP', 'KR', 'SG', 'HK', 'CA', 'AU', 'OTHER']
    }]
  },
  // Metadata
  tags: [{
    type: String,
    maxlength: 20
  }],
  category: {
    type: String,
    enum: ['defi', 'gaming', 'nft', 'metaverse', 'infrastructure', 'layer1', 'layer2', 'oracle', 'storage', 'privacy', 'exchange', 'lending', 'staking', 'insurance', 'prediction', 'social', 'content', 'identity', 'other'],
    default: 'other'
  },
  metadata: {
    type: mongoose.Schema.Types.Mixed
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
  deletedAt: {
    type: Date
  },
  verifiedAt: {
    type: Date
  },
  featuredAt: {
    type: Date
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Indexes for performance
customTokenSchema.index({ symbol: 1, isActive: 1 });
customTokenSchema.index({ blockchainType: 1, networkName: 1 });
customTokenSchema.index({ status: 1, isActive: 1 });
customTokenSchema.index({ createdBy: 1, createdAt: -1 });
customTokenSchema.index({ isFeatured: 1, marketCap: -1 });
customTokenSchema.index({ category: 1, isActive: 1 });
customTokenSchema.index({ tags: 1 });

// Virtuals
customTokenSchema.virtual('priceChangePercent24h').get(function() {
  if (this.price === 0 || this.priceChange24h === 0) return 0;
  return (this.priceChange24h / (this.price - this.priceChange24h)) * 100;
});

customTokenSchema.virtual('marketCapRank').get(function() {
  // This would typically be calculated by a separate aggregation
  return 0;
});

customTokenSchema.virtual('isPopular').get(function() {
  return this.volume24h > 1000000 || this.marketCap > 10000000;
});

customTokenSchema.virtual('fullyDilutedMarketCap').get(function() {
  return this.price * this.totalSupply;
});

// Static methods
customTokenSchema.statics.findBySymbol = function(symbol) {
  return this.findOne({ symbol: symbol.toUpperCase(), isDeleted: false })
    .populate('createdBy', 'username email')
    .populate('updatedBy', 'username email');
};

customTokenSchema.statics.findByBlockchain = function(blockchainType, networkName) {
  const query = { blockchainType, isDeleted: false };
  
  if (networkName) {
    query.networkName = networkName;
  }
  
  return this.find(query)
    .sort({ marketCap: -1 })
    .populate('createdBy', 'username email');
};

customTokenSchema.statics.findActiveTokens = function(options = {}) {
  const query = { isActive: true, status: 'active', isDeleted: false };
  
  if (options.category) {
    query.category = options.category;
  }
  
  if (options.featured) {
    query.isFeatured = true;
  }
  
  if (options.verified) {
    query.isVerified = true;
  }
  
  return this.find(query)
    .sort({ options.sortBy || 'marketCap', options.sortOrder || -1 })
    .limit(options.limit || 100)
    .skip(options.offset || 0)
    .populate('createdBy', 'username email');
};

customTokenSchema.statics.findFeaturedTokens = function(limit = 10) {
  return this.find({ 
    isActive: true, 
    isFeatured: true, 
    status: 'active', 
    isDeleted: false 
  })
  .sort({ marketCap: -1 })
  .limit(limit)
  .populate('createdBy', 'username email');
};

customTokenSchema.statics.findTokensByUser = function(userId, options = {}) {
  const query = { createdBy: userId, isDeleted: false };
  
  if (options.status) {
    query.status = options.status;
  }
  
  return this.find(query)
    .sort({ createdAt: -1 })
    .limit(options.limit || 50)
    .skip(options.offset || 0);
};

customTokenSchema.statics.searchTokens = function(searchTerm, options = {}) {
  const query = {
    isDeleted: false,
    $or: [
      { name: { $regex: searchTerm, $options: 'i' } },
      { symbol: { $regex: searchTerm, $options: 'i' } },
      { description: { $regex: searchTerm, $options: 'i' } },
      { tags: { $regex: searchTerm, $options: 'i' } }
    ]
  };
  
  if (options.category) {
    query.category = options.category;
  }
  
  if (options.blockchainType) {
    query.blockchainType = options.blockchainType;
  }
  
  return this.find(query)
    .sort({ options.sortBy || 'marketCap', options.sortOrder || -1 })
    .limit(options.limit || 50)
    .skip(options.offset || 0)
    .populate('createdBy', 'username email');
};

customTokenSchema.statics.getTokenStats = function() {
  return this.aggregate([
    {
      $match: { isDeleted: false }
    },
    {
      $group: {
        _id: null,
        total: { $sum: 1 },
        active: { $sum: { $cond: ['$isActive', 1, 0] } },
        verified: { $sum: { $cond: ['$isVerified', 1, 0] } },
        featured: { $sum: { $cond: ['$isFeatured', 1, 0] } },
        totalMarketCap: { $sum: '$marketCap' },
        totalVolume24h: { $sum: '$volume24h' },
        avgPrice: { $avg: '$price' },
        blockchainStats: {
          $push: {
            blockchainType: '$blockchainType',
            count: 1
          }
        }
      }
    }
  ]);
};

// Instance methods
customTokenSchema.methods.activate = function() {
  this.isActive = true;
  this.status = 'active';
  return this.save();
};

customTokenSchema.methods.pause = function() {
  this.isActive = false;
  this.status = 'paused';
  return this.save();
};

customTokenSchema.methods.suspend = function() {
  this.isActive = false;
  this.status = 'suspended';
  return this.save();
};

customTokenSchema.methods.delist = function() {
  this.isActive = false;
  this.status = 'delisted';
  return this.save();
};

customTokenSchema.methods.verify = function() {
  this.isVerified = true;
  this.verifiedAt = new Date();
  return this.save();
};

customTokenSchema.methods.feature = function() {
  this.isFeatured = true;
  this.featuredAt = new Date();
  return this.save();
};

customTokenSchema.methods.unfeature = function() {
  this.isFeatured = false;
  this.featuredAt = undefined;
  return this.save();
};

customTokenSchema.methods.softDelete = function() {
  this.isDeleted = true;
  this.isActive = false;
  this.status = 'delisted';
  this.deletedAt = new Date();
  return this.save();
};

customTokenSchema.methods.updateMarketData = function(marketData) {
  if (marketData.price !== undefined) this.price = marketData.price;
  if (marketData.priceChange24h !== undefined) this.priceChange24h = marketData.priceChange24h;
  if (marketData.volume24h !== undefined) this.volume24h = marketData.volume24h;
  if (marketData.marketCap !== undefined) this.marketCap = marketData.marketCap;
  if (marketData.high24h !== undefined) this.high24h = marketData.high24h;
  if (marketData.low24h !== undefined) this.low24h = marketData.low24h;
  if (marketData.circulatingSupply !== undefined) this.circulatingSupply = marketData.circulatingSupply;
  
  return this.save();
};

customTokenSchema.methods.addTag = function(tag) {
  if (!this.tags.includes(tag)) {
    this.tags.push(tag);
    return this.save();
  }
  return Promise.resolve(this);
};

customTokenSchema.methods.removeTag = function(tag) {
  const index = this.tags.indexOf(tag);
  if (index > -1) {
    this.tags.splice(index, 1);
    return this.save();
  }
  return Promise.resolve(this);
};

customTokenSchema.methods.enableTrading = function() {
  this.tradingEnabled = true;
  return this.save();
};

customTokenSchema.methods.disableTrading = function() {
  this.tradingEnabled = false;
  return this.save();
};

customTokenSchema.methods.updatePrice = function(newPrice) {
  const oldPrice = this.price;
  this.price = newPrice;
  this.priceChange24h = newPrice - oldPrice;
  
  // Update market cap
  this.marketCap = newPrice * this.circulatingSupply;
  
  return this.save();
};

customTokenSchema.methods.validateOrder = function(order) {
  const errors = [];
  
  if (!this.tradingEnabled) {
    errors.push('Trading is not enabled for this token');
  }
  
  if (!this.isActive || this.status !== 'active') {
    errors.push('Token is not active');
  }
  
  if (order.quantity < this.tradingRules.minOrderSize) {
    errors.push(`Order size must be at least ${this.tradingRules.minOrderSize}`);
  }
  
  if (order.quantity > this.tradingRules.maxOrderSize) {
    errors.push(`Order size cannot exceed ${this.tradingRules.maxOrderSize}`);
  }
  
  return errors;
};

// Pre-save middleware
customTokenSchema.pre('save', function(next) {
  // Ensure symbol is uppercase
  if (this.symbol) {
    this.symbol = this.symbol.toUpperCase();
  }
  
  // Ensure contract address is lowercase
  if (this.contractAddress) {
    this.contractAddress = this.contractAddress.toLowerCase();
  }
  
  // Update market cap if price or circulating supply changes
  if (this.isModified('price') || this.isModified('circulatingSupply')) {
    this.marketCap = this.price * this.circulatingSupply;
  }
  
  next();
});

// Pre-remove middleware
customTokenSchema.pre('remove', async function(next) {
  // Log token removal
  console.log(`Custom token ${this.symbol} removed`);
  next();
});

module.exports = mongoose.model('CustomToken', customTokenSchema);