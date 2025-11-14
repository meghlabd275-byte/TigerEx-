const mongoose = require('mongoose');

const orderBookSchema = new mongoose.Schema({
  exchangeId: {
    type: String,
    required: true,
    enum: ['binance', 'kucoin', 'okx', 'bybit', 'kraken'],
    index: true
  },
  exchangeName: {
    type: String,
    required: true
  },
  symbol: {
    type: String,
    required: true,
    uppercase: true,
    index: true
  },
  lastUpdateId: {
    type: String,
    default: ''
  },
  bids: [{
    price: {
      type: Number,
      required: true,
      min: 0
    },
    quantity: {
      type: Number,
      required: true,
      min: 0
    },
    total: {
      type: Number,
      default: 0,
      min: 0
    },
    depth: {
      type: Number,
      default: 0,
      min: 0
    },
    cumulativeQuantity: {
      type: Number,
      default: 0,
      min: 0
    },
    cumulativeDepth: {
      type: Number,
      default: 0,
      min: 0
    }
  }],
  asks: [{
    price: {
      type: Number,
      required: true,
      min: 0
    },
    quantity: {
      type: Number,
      required: true,
      min: 0
    },
    total: {
      type: Number,
      default: 0,
      min: 0
    },
    depth: {
      type: Number,
      default: 0,
      min: 0
    },
    cumulativeQuantity: {
      type: Number,
      default: 0,
      min: 0
    },
    cumulativeDepth: {
      type: Number,
      default: 0,
      min: 0
    }
  }],
  bestBid: {
    type: Number,
    default: 0,
    min: 0
  },
  bestAsk: {
    type: Number,
    default: 0,
    min: 0
  },
  spread: {
    type: Number,
    default: 0,
    min: 0
  },
  spreadPercent: {
    type: Number,
    default: 0,
    min: 0
  },
  midPrice: {
    type: Number,
    default: 0,
    min: 0
  },
  bidDepth: {
    type: Number,
    default: 0,
    min: 0
  },
  askDepth: {
    type: Number,
    default: 0,
    min: 0
  },
  totalDepth: {
    type: Number,
    default: 0,
    min: 0
  },
  bidCount: {
    type: Number,
    default: 0,
    min: 0
  },
  askCount: {
    type: Number,
    default: 0,
    min: 0
  },
  totalOrders: {
    type: Number,
    default: 0,
    min: 0
  },
  volume24h: {
    type: Number,
    default: 0,
    min: 0
  },
  change24h: {
    type: Number,
    default: 0
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
  isActive: {
    type: Boolean,
    default: true
  },
  quality: {
    type: String,
    enum: ['excellent', 'good', 'fair', 'poor'],
    default: 'fair'
  },
  latency: {
    type: Number,
    default: 0,
    min: 0
  },
  lastUpdate: {
    type: Date,
    default: Date.now,
    index: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Indexes for performance
orderBookSchema.index({ exchangeId: 1, symbol: 1, isActive: 1 });
orderBookSchema.index({ symbol: 1, lastUpdate: -1 });
orderBookSchema.index({ exchangeId: 1, lastUpdate: -1 });

// Virtuals
orderBookSchema.virtual('spreadValue').get(function() {
  return this.bestAsk - this.bestBid;
});

orderBookSchema.virtual('isLiquid').get(function() {
  return this.totalDepth > 1000000; // Consider liquid if > $1M
});

orderBookSchema.virtual('spreadQuality').get(function() {
  if (this.spreadPercent < 0.01) return 'tight';
  if (this.spreadPercent < 0.05) return 'narrow';
  if (this.spreadPercent < 0.1) return 'moderate';
  return 'wide';
});

// Static methods
orderBookSchema.statics.findByExchangeAndSymbol = function(exchangeId, symbol) {
  return this.findOne({ exchangeId, symbol, isActive: true })
    .sort({ lastUpdate: -1 });
};

orderBookSchema.statics.findBySymbol = function(symbol, options = {}) {
  const query = { symbol, isActive: true };
  
  if (options.exchangeId) {
    query.exchangeId = options.exchangeId;
  }
  
  return this.find(query)
    .sort({ lastUpdate: -1 })
    .limit(options.limit || 10);
};

orderBookSchema.statics.findActiveOrderBooks = function() {
  return this.find({ isActive: true })
    .sort({ lastUpdate: -1 })
    .limit(100);
};

orderBookSchema.statics.getAggregatedOrderBook = function(symbol) {
  return this.aggregate([
    {
      $match: { symbol, isActive: true }
    },
    {
      $group: {
        _id: '$symbol',
        exchanges: {
          $push: {
            exchangeId: '$exchangeId',
            exchangeName: '$exchangeName',
            bestBid: '$bestBid',
            bestAsk: '$bestAsk',
            bidDepth: '$bidDepth',
            askDepth: '$askDepth',
            totalDepth: '$totalDepth',
            latency: '$latency',
            lastUpdate: '$lastUpdate'
          }
        },
        avgBid: { $avg: '$bestBid' },
        avgAsk: { $avg: '$bestAsk' },
        totalBidDepth: { $sum: '$bidDepth' },
        totalAskDepth: { $sum: '$askDepth' },
        totalDepth: { $sum: '$totalDepth' },
        exchangeCount: { $sum: 1 },
        lastUpdate: { $max: '$lastUpdate' }
      }
    }
  ]);
};

orderBookSchema.statics.getOrderBookStats = function(timeframe = '24h') {
  const dateLimit = new Date();
  
  switch (timeframe) {
    case '1h':
      dateLimit.setHours(dateLimit.getHours() - 1);
      break;
    case '24h':
      dateLimit.setDate(dateLimit.getDate() - 1);
      break;
    case '7d':
      dateLimit.setDate(dateLimit.getDate() - 7);
      break;
    default:
      dateLimit.setDate(dateLimit.getDate() - 1);
  }
  
  return this.aggregate([
    {
      $match: {
        lastUpdate: { $gte: dateLimit },
        isActive: true
      }
    },
    {
      $group: {
        _id: null,
        totalOrderBooks: { $sum: 1 },
        avgSpread: { $avg: '$spreadPercent' },
        avgDepth: { $avg: '$totalDepth' },
        totalVolume: { $sum: '$volume24h' },
        exchangeStats: {
          $push: {
            exchangeId: '$exchangeId',
            exchangeName: '$exchangeName',
            depth: '$totalDepth',
            spread: '$spreadPercent'
          }
        }
      }
    }
  ]);
};

// Instance methods
orderBookSchema.methods.updateOrderBook = function(orderBookData) {
  // Update bids and asks
  if (orderBookData.bids) {
    this.bids = orderBookData.bids.map((bid, index) => ({
      ...bid,
      total: bid.price * bid.quantity,
      depth: bid.price * bid.quantity,
      cumulativeQuantity: bid.cumulativeQuantity || 0,
      cumulativeDepth: bid.cumulativeDepth || 0
    }));
  }
  
  if (orderBookData.asks) {
    this.asks = orderBookData.asks.map((ask, index) => ({
      ...ask,
      total: ask.price * ask.quantity,
      depth: ask.price * ask.quantity,
      cumulativeQuantity: ask.cumulativeQuantity || 0,
      cumulativeDepth: ask.cumulativeDepth || 0
    }));
  }
  
  // Update best bid/ask
  if (this.bids.length > 0) {
    this.bestBid = this.bids[0].price;
    this.bidCount = this.bids.length;
  }
  
  if (this.asks.length > 0) {
    this.bestAsk = this.asks[0].price;
    this.askCount = this.asks.length;
  }
  
  // Calculate spread and mid price
  if (this.bestBid && this.bestAsk) {
    this.spread = this.bestAsk - this.bestBid;
    this.midPrice = (this.bestBid + this.bestAsk) / 2;
    this.spreadPercent = (this.spread / this.midPrice) * 100;
  }
  
  // Calculate depth
  this.bidDepth = this.bids.reduce((sum, bid) => sum + bid.depth, 0);
  this.askDepth = this.asks.reduce((sum, ask) => sum + ask.depth, 0);
  this.totalDepth = this.bidDepth + this.askDepth;
  this.totalOrders = this.bidCount + this.askCount;
  
  // Update other fields
  if (orderBookData.lastUpdateId) {
    this.lastUpdateId = orderBookData.lastUpdateId;
  }
  
  if (orderBookData.volume24h) {
    this.volume24h = orderBookData.volume24h;
  }
  
  if (orderBookData.change24h) {
    this.change24h = orderBookData.change24h;
  }
  
  if (orderBookData.high24h) {
    this.high24h = orderBookData.high24h;
  }
  
  if (orderBookData.low24h) {
    this.low24h = orderBookData.low24h;
  }
  
  this.lastUpdate = new Date();
  
  // Calculate quality based on spread and depth
  this.calculateQuality();
  
  return this.save();
};

orderBookSchema.methods.calculateQuality = function() {
  if (this.spreadPercent < 0.01 && this.totalDepth > 1000000) {
    this.quality = 'excellent';
  } else if (this.spreadPercent < 0.05 && this.totalDepth > 500000) {
    this.quality = 'good';
  } else if (this.spreadPercent < 0.1 && this.totalDepth > 100000) {
    this.quality = 'fair';
  } else {
    this.quality = 'poor';
  }
};

orderBookSchema.methods.getTopBids = function(limit = 10) {
  return this.bids.slice(0, limit);
};

orderBookSchema.methods.getTopAsks = function(limit = 10) {
  return this.asks.slice(0, limit);
};

orderBookSchema.methods.getLiquidityAtPrice = function(price, side, depth = 0.01) {
  const orders = side === 'buy' ? this.bids : this.asks;
  let totalLiquidity = 0;
  
  if (side === 'buy') {
    // Sum up bids from best bid down to price - depth
    const priceLimit = this.bestBid - (this.bestBid * depth);
    for (const order of orders) {
      if (order.price < priceLimit) break;
      totalLiquidity += order.total;
    }
  } else {
    // Sum up asks from best ask up to price + depth
    const priceLimit = this.bestAsk + (this.bestAsk * depth);
    for (const order of orders) {
      if (order.price > priceLimit) break;
      totalLiquidity += order.total;
    }
  }
  
  return totalLiquidity;
};

orderBookSchema.methods.deactivate = function() {
  this.isActive = false;
  this.lastUpdate = new Date();
  return this.save();
};

orderBookSchema.methods.activate = function() {
  this.isActive = true;
  this.lastUpdate = new Date();
  return this.save();
};

orderBookSchema.methods.updateLatency = function(latency) {
  this.latency = latency;
  this.lastUpdate = new Date();
  return this.save();
};

// Pre-save middleware
orderBookSchema.pre('save', function(next) {
  // Ensure bids are sorted by price (descending)
  if (this.isModified('bids')) {
    this.bids.sort((a, b) => b.price - a.price);
  }
  
  // Ensure asks are sorted by price (ascending)
  if (this.isModified('asks')) {
    this.asks.sort((a, b) => a.price - b.price);
  }
  
  // Update timestamp
  this.lastUpdate = new Date();
  
  next();
});

module.exports = mongoose.model('OrderBook', orderBookSchema);