const axios = require('axios');
const crypto = require('crypto');
const WebSocket = require('ws');
const EventEmitter = require('events');
const LiquidityPool = require('../models/LiquidityPool');
const OrderBook = require('../models/OrderBook');
const TradeExecution = require('../models/TradeExecution');

class LiquidityAggregatorService extends EventEmitter {
  constructor() {
    super();
    this.exchanges = {
      binance: {
        name: 'Binance',
        apiKey: process.env.BINANCE_API_KEY,
        apiSecret: process.env.BINANCE_API_SECRET,
        baseUrl: 'https://api.binance.com',
        wsUrl: 'wss://stream.binance.com:9443/ws',
        connected: false,
        orderBooks: new Map(),
        balances: new Map()
      },
      kucoin: {
        name: 'KuCoin',
        apiKey: process.env.KUCOIN_API_KEY,
        apiSecret: process.env.KUCOIN_API_SECRET,
        passphrase: process.env.KUCOIN_PASSPHRASE,
        baseUrl: 'https://api.kucoin.com',
        wsUrl: 'wss://ws-api.kucoin.com/endpoint',
        connected: false,
        orderBooks: new Map(),
        balances: new Map()
      },
      okx: {
        name: 'OKX',
        apiKey: process.env.OKX_API_KEY,
        apiSecret: process.env.OKX_API_SECRET,
        passphrase: process.env.OKX_PASSPHRASE,
        baseUrl: 'https://www.okx.com',
        wsUrl: 'wss://ws.okx.com:8443/ws/v5/public',
        connected: false,
        orderBooks: new Map(),
        balances: new Map()
      },
      bybit: {
        name: 'Bybit',
        apiKey: process.env.BYBIT_API_KEY,
        apiSecret: process.env.BYBIT_API_SECRET,
        baseUrl: 'https://api.bybit.com',
        wsUrl: 'wss://stream.bybit.com/v5/public/linear',
        connected: false,
        orderBooks: new Map(),
        balances: new Map()
      },
      kraken: {
        name: 'Kraken',
        apiKey: process.env.KRAKEN_API_KEY,
        apiSecret: process.env.KRAKEN_API_SECRET,
        baseUrl: 'https://api.kraken.com',
        wsUrl: 'wss://ws.kraken.com',
        connected: false,
        orderBooks: new Map(),
        balances: new Map()
      }
    };
    
    this.aggregatedOrderBooks = new Map();
    this.liquidityPools = new Map();
    this.tradeExecutionQueue = [];
    this.isProcessing = false;
    
    this.initializeConnections();
  }

  // Initialize connections to all exchanges
  async initializeConnections() {
    console.log('🔄 Initializing multi-exchange liquidity connections...');
    
    for (const [exchangeId, exchange] of Object.entries(this.exchanges)) {
      try {
        await this.connectExchange(exchangeId);
        await this.subscribeToOrderBooks(exchangeId);
        await this.fetchInitialData(exchangeId);
      } catch (error) {
        console.error(`❌ Failed to connect to ${exchange.name}:`, error.message);
        this.emit('exchangeError', { exchangeId, error: error.message });
      }
    }
    
    console.log('✅ Multi-exchange liquidity system initialized');
    this.emit('initialized');
  }

  // Connect to individual exchange
  async connectExchange(exchangeId) {
    const exchange = this.exchanges[exchangeId];
    
    switch (exchangeId) {
      case 'binance':
        await this.connectBinance();
        break;
      case 'kucoin':
        await this.connectKuCoin();
        break;
      case 'okx':
        await this.connectOKX();
        break;
      case 'bybit':
        await this.connectBybit();
        break;
      case 'kraken':
        await this.connectKraken();
        break;
    }
    
    exchange.connected = true;
    console.log(`✅ Connected to ${exchange.name}`);
  }

  // Binance connection
  async connectBinance() {
    const exchange = this.exchanges.binance;
    exchange.ws = new WebSocket(`${exchange.wsUrl}/btcusdt@depth20@100ms`);
    
    exchange.ws.on('open', () => {
      console.log('📡 Binance WebSocket connected');
    });
    
    exchange.ws.on('message', (data) => {
      const orderBook = JSON.parse(data);
      this.processOrderBookUpdate('binance', orderBook);
    });
    
    exchange.ws.on('error', (error) => {
      console.error('❌ Binance WebSocket error:', error);
      exchange.connected = false;
    });
    
    exchange.ws.on('close', () => {
      console.log('🔌 Binance WebSocket disconnected');
      exchange.connected = false;
      // Reconnect after 5 seconds
      setTimeout(() => this.connectExchange('binance'), 5000);
    });
  }

  // KuCoin connection
  async connectKuCoin() {
    const exchange = this.exchanges.kucoin;
    
    try {
      // Get token for WebSocket connection
      const response = await axios.post(`${exchange.baseUrl}/api/v1/bullet-public`);
      const { token, instanceServers } = response.data.data;
      
      const wsUrl = `${instanceServers[0].endpoint}?token=${token}`;
      exchange.ws = new WebSocket(wsUrl);
      
      exchange.ws.on('open', () => {
        console.log('📡 KuCoin WebSocket connected');
        // Subscribe to depth updates
        this.subscribeKuCoinDepth();
      });
      
      exchange.ws.on('message', (data) => {
        const message = JSON.parse(data);
        if (message.type === 'message') {
          const orderBook = JSON.parse(message.data);
          this.processOrderBookUpdate('kucoin', orderBook);
        }
      });
      
      exchange.ws.on('error', (error) => {
        console.error('❌ KuCoin WebSocket error:', error);
        exchange.connected = false;
      });
      
      exchange.ws.on('close', () => {
        console.log('🔌 KuCoin WebSocket disconnected');
        exchange.connected = false;
        setTimeout(() => this.connectExchange('kucoin'), 5000);
      });
      
    } catch (error) {
      console.error('❌ KuCoin connection error:', error);
      throw error;
    }
  }

  // OKX connection
  async connectOKX() {
    const exchange = this.exchanges.okx;
    exchange.ws = new WebSocket(exchange.wsUrl);
    
    exchange.ws.on('open', () => {
      console.log('📡 OKX WebSocket connected');
      // Subscribe to BTC-USDT depth
      exchange.ws.send(JSON.stringify({
        op: 'subscribe',
        args: [{ channel: 'books', instId: 'BTC-USDT' }]
      }));
    });
    
    exchange.ws.on('message', (data) => {
      const message = JSON.parse(data);
      if (message.arg && message.arg.channel === 'books') {
        this.processOrderBookUpdate('okx', message);
      }
    });
    
    exchange.ws.on('error', (error) => {
      console.error('❌ OKX WebSocket error:', error);
      exchange.connected = false;
    });
    
    exchange.ws.on('close', () => {
      console.log('🔌 OKX WebSocket disconnected');
      exchange.connected = false;
      setTimeout(() => this.connectExchange('okx'), 5000);
    });
  }

  // Bybit connection
  async connectBybit() {
    const exchange = this.exchanges.bybit;
    exchange.ws = new WebSocket(exchange.wsUrl);
    
    exchange.ws.on('open', () => {
      console.log('📡 Bybit WebSocket connected');
      // Subscribe to orderbook
      exchange.ws.send(JSON.stringify({
        op: 'subscribe',
        args: ['orderbook.1.BTCUSDT']
      }));
    });
    
    exchange.ws.on('message', (data) => {
      const message = JSON.parse(data);
      if (message.topic === 'orderbook.1.BTCUSDT') {
        this.processOrderBookUpdate('bybit', message.data);
      }
    });
    
    exchange.ws.on('error', (error) => {
      console.error('❌ Bybit WebSocket error:', error);
      exchange.connected = false;
    });
    
    exchange.ws.on('close', () => {
      console.log('🔌 Bybit WebSocket disconnected');
      exchange.connected = false;
      setTimeout(() => this.connectExchange('bybit'), 5000);
    });
  }

  // Kraken connection
  async connectKraken() {
    const exchange = this.exchanges.kraken;
    exchange.ws = new WebSocket(exchange.wsUrl);
    
    exchange.ws.on('open', () => {
      console.log('📡 Kraken WebSocket connected');
      // Subscribe to XBT/USD order book
      exchange.ws.send(JSON.stringify({
        event: 'subscribe',
        pair: 'XBT/USD',
        subscription: { name: 'book' }
      }));
    });
    
    exchange.ws.on('message', (data) => {
      const message = JSON.parse(data);
      if (message[1] && Array.isArray(message[1].bids)) {
        this.processOrderBookUpdate('kraken', message);
      }
    });
    
    exchange.ws.on('error', (error) => {
      console.error('❌ Kraken WebSocket error:', error);
      exchange.connected = false;
    });
    
    exchange.ws.on('close', () => {
      console.log('🔌 Kraken WebSocket disconnected');
      exchange.connected = false;
      setTimeout(() => this.connectExchange('kraken'), 5000);
    });
  }

  // Process order book updates from exchanges
  processOrderBookUpdate(exchangeId, orderBook) {
    const exchange = this.exchanges[exchangeId];
    
    // Normalize order book data
    const normalizedOrderBook = this.normalizeOrderBook(exchangeId, orderBook);
    
    // Update exchange order book
    exchange.orderBooks.set('BTC/USDT', normalizedOrderBook);
    
    // Aggregate with other exchanges
    this.aggregateOrderBooks();
    
    // Emit update
    this.emit('orderBookUpdate', {
      exchangeId,
      symbol: 'BTC/USDT',
      orderBook: normalizedOrderBook
    });
  }

  // Normalize order book data from different exchanges
  normalizeOrderBook(exchangeId, rawOrderBook) {
    switch (exchangeId) {
      case 'binance':
        return {
          bids: rawOrderBook.bids.map(([price, quantity]) => ({
            price: parseFloat(price),
            quantity: parseFloat(quantity),
            exchange: 'binance'
          })),
          asks: rawOrderBook.asks.map(([price, quantity]) => ({
            price: parseFloat(price),
            quantity: parseFloat(quantity),
            exchange: 'binance'
          })),
          lastUpdate: rawOrderBook.lastUpdateId
        };
        
      case 'kucoin':
        return {
          bids: rawOrderBook.data.bids.map(([price, quantity]) => ({
            price: parseFloat(price),
            quantity: parseFloat(quantity),
            exchange: 'kucoin'
          })),
          asks: rawOrderBook.data.asks.map(([price, quantity]) => ({
            price: parseFloat(price),
            quantity: parseFloat(quantity),
            exchange: 'kucoin'
          })),
          lastUpdate: rawOrderBook.data.sequence
        };
        
      case 'okx':
        return {
          bids: rawOrderBook.data[0].bids.map(([price, quantity, , exchange]) => ({
            price: parseFloat(price),
            quantity: parseFloat(quantity),
            exchange: 'okx'
          })),
          asks: rawOrderBook.data[0].asks.map(([price, quantity, , exchange]) => ({
            price: parseFloat(price),
            quantity: parseFloat(quantity),
            exchange: 'okx'
          })),
          lastUpdate: rawOrderBook.data[0].ts
        };
        
      case 'bybit':
        return {
          bids: rawOrderBook.b.map(([price, quantity]) => ({
            price: parseFloat(price),
            quantity: parseFloat(quantity),
            exchange: 'bybit'
          })),
          asks: rawOrderBook.a.map(([price, quantity]) => ({
            price: parseFloat(price),
            quantity: parseFloat(quantity),
            exchange: 'bybit'
          })),
          lastUpdate: rawOrderBook.ts
        };
        
      case 'kraken':
        return {
          bids: rawOrderBook[1].bids.slice(0, 20).map(([price, quantity, timestamp]) => ({
            price: parseFloat(price),
            quantity: parseFloat(quantity),
            exchange: 'kraken'
          })),
          asks: rawOrderBook[1].asks.slice(0, 20).map(([price, quantity, timestamp]) => ({
            price: parseFloat(price),
            quantity: parseFloat(quantity),
            exchange: 'kraken'
          })),
          lastUpdate: rawOrderBook[1].ts || Date.now()
        };
        
      default:
        return { bids: [], asks: [] };
    }
  }

  // Aggregate order books from all connected exchanges
  aggregateOrderBooks() {
    const symbol = 'BTC/USDT';
    const aggregatedBids = [];
    const aggregatedAsks = [];
    
    // Collect all bids and asks from connected exchanges
    for (const [exchangeId, exchange] of Object.entries(this.exchanges)) {
      if (exchange.connected && exchange.orderBooks.has(symbol)) {
        const orderBook = exchange.orderBooks.get(symbol);
        aggregatedBids.push(...orderBook.bids);
        aggregatedAsks.push(...orderBook.asks);
      }
    }
    
    // Sort bids (descending price) and asks (ascending price)
    aggregatedBids.sort((a, b) => b.price - a.price);
    aggregatedAsks.sort((a, b) => a.price - b.price);
    
    // Calculate liquidity depth
    const bidDepth = this.calculateLiquidityDepth(aggregatedBids);
    const askDepth = this.calculateLiquidityDepth(aggregatedAsks);
    
    // Store aggregated order book
    this.aggregatedOrderBooks.set(symbol, {
      bids: aggregatedBids.slice(0, 100), // Top 100 bids
      asks: aggregatedAsks.slice(0, 100), // Top 100 asks
      bidDepth,
      askDepth,
      totalExchanges: this.getConnectedExchangeCount(),
      lastUpdate: Date.now()
    });
    
    // Update liquidity pool
    this.updateLiquidityPool(symbol, aggregatedBids, aggregatedAsks);
    
    this.emit('aggregatedOrderBook', {
      symbol,
      orderBook: this.aggregatedOrderBooks.get(symbol)
    });
  }

  // Calculate liquidity depth for order book
  calculateLiquidityDepth(orders) {
    let depth = 0;
    let cumulativeQuantity = 0;
    
    return orders.map(order => {
      cumulativeQuantity += order.quantity;
      depth += order.price * order.quantity;
      
      return {
        price: order.price,
        quantity: order.quantity,
        exchange: order.exchange,
        cumulativeQuantity,
        cumulativeDepth: depth
      };
    });
  }

  // Update liquidity pool for symbol
  updateLiquidityPool(symbol, bids, asks) {
    const totalBidLiquidity = bids.reduce((sum, bid) => sum + (bid.price * bid.quantity), 0);
    const totalAskLiquidity = asks.reduce((sum, ask) => sum + (ask.price * ask.quantity), 0);
    const spread = asks[0]?.price - bids[0]?.price || 0;
    const midPrice = (bids[0]?.price + asks[0]?.price) / 2 || 0;
    
    this.liquidityPools.set(symbol, {
      symbol,
      totalBidLiquidity,
      totalAskLiquidity,
      totalLiquidity: totalBidLiquidity + totalAskLiquidity,
      spread,
      spreadPercent: (spread / midPrice) * 100,
      midPrice,
      bestBid: bids[0]?.price || 0,
      bestAsk: asks[0]?.price || 0,
      exchangeCount: this.getConnectedExchangeCount(),
      lastUpdate: Date.now()
    });
  }

  // Get connected exchange count
  getConnectedExchangeCount() {
    return Object.values(this.exchanges).filter(exchange => exchange.connected).length;
  }

  // Execute trade across multiple exchanges for best price
  async executeTrade(tradeRequest) {
    const { symbol, side, quantity, type } = tradeRequest;
    const aggregatedBook = this.aggregatedOrderBooks.get(symbol);
    
    if (!aggregatedBook) {
      throw new Error('No liquidity available for symbol');
    }
    
    const execution = new TradeExecution({
      requestId: crypto.randomUUID(),
      symbol,
      side,
      quantity,
      type,
      status: 'processing',
      createdAt: new Date()
    });
    
    this.tradeExecutionQueue.push(execution);
    
    if (!this.isProcessing) {
      this.processTradeQueue();
    }
    
    return execution;
  }

  // Process trade execution queue
  async processTradeQueue() {
    this.isProcessing = true;
    
    while (this.tradeExecutionQueue.length > 0) {
      const execution = this.tradeExecutionQueue.shift();
      
      try {
        await this.executeTradeLogic(execution);
        execution.status = 'completed';
        execution.completedAt = new Date();
      } catch (error) {
        execution.status = 'failed';
        execution.error = error.message;
        execution.failedAt = new Date();
      }
      
      this.emit('tradeExecutionUpdate', execution);
    }
    
    this.isProcessing = false;
  }

  // Execute trade logic across exchanges
  async executeTradeLogic(execution) {
    const { symbol, side, quantity } = execution;
    const orders = side === 'buy' ? 
      this.aggregatedOrderBooks.get(symbol)?.asks : 
      this.aggregatedOrderBooks.get(symbol)?.bids;
    
    if (!orders || orders.length === 0) {
      throw new Error('No orders available for execution');
    }
    
    let remainingQuantity = quantity;
    const filledOrders = [];
    let totalCost = 0;
    let averagePrice = 0;
    
    for (const order of orders) {
      if (remainingQuantity <= 0) break;
      
      const fillQuantity = Math.min(remainingQuantity, order.quantity);
      const fillCost = fillQuantity * order.price;
      
      filledOrders.push({
        exchange: order.exchange,
        price: order.price,
        quantity: fillQuantity,
        cost: fillCost
      });
      
      totalCost += fillCost;
      remainingQuantity -= fillQuantity;
    }
    
    if (remainingQuantity > 0) {
      throw new Error('Insufficient liquidity to fill entire order');
    }
    
    averagePrice = totalCost / quantity;
    
    // Update execution details
    execution.filledOrders = filledOrders;
    execution.totalCost = totalCost;
    execution.averagePrice = averagePrice;
    execution.filledQuantity = quantity - remainingQuantity;
    
    // Save to database
    await execution.save();
    
    this.emit('tradeExecuted', {
      execution,
      filledOrders,
      totalCost,
      averagePrice
    });
  }

  // Get aggregated order book
  getAggregatedOrderBook(symbol) {
    return this.aggregatedOrderBooks.get(symbol) || null;
  }

  // Get liquidity pool information
  getLiquidityPool(symbol) {
    return this.liquidityPools.get(symbol) || null;
  }

  // Get all exchange statuses
  getExchangeStatuses() {
    const statuses = {};
    
    for (const [exchangeId, exchange] of Object.entries(this.exchanges)) {
      statuses[exchangeId] = {
        name: exchange.name,
        connected: exchange.connected,
        orderBooks: Array.from(exchange.orderBooks.keys()),
        lastUpdate: exchange.lastUpdate
      };
    }
    
    return statuses;
  }

  // Get best bid/ask across all exchanges
  getBestBidAsk(symbol) {
    const liquidityPool = this.getLiquidityPool(symbol);
    
    if (!liquidityPool) {
      return null;
    }
    
    return {
      bestBid: liquidityPool.bestBid,
      bestAsk: liquidityPool.bestAsk,
      spread: liquidityPool.spread,
      spreadPercent: liquidityPool.spreadPercent,
      midPrice: liquidityPool.midPrice
    };
  }

  // Get liquidity distribution by exchange
  getLiquidityDistribution(symbol) {
    const distribution = {};
    const aggregatedBook = this.aggregatedOrderBooks.get(symbol);
    
    if (!aggregatedBook) {
      return distribution;
    }
    
    // Calculate distribution for bids
    const bidsByExchange = {};
    aggregatedBook.bids.forEach(bid => {
      if (!bidsByExchange[bid.exchange]) {
        bidsByExchange[bid.exchange] = 0;
      }
      bidsByExchange[bid.exchange] += bid.price * bid.quantity;
    });
    
    // Calculate distribution for asks
    const asksByExchange = {};
    aggregatedBook.asks.forEach(ask => {
      if (!asksByExchange[ask.exchange]) {
        asksByExchange[ask.exchange] = 0;
      }
      asksByExchange[ask.exchange] += ask.price * ask.quantity;
    });
    
    // Combine and calculate percentages
    const totalBidLiquidity = Object.values(bidsByExchange).reduce((sum, value) => sum + value, 0);
    const totalAskLiquidity = Object.values(asksByExchange).reduce((sum, value) => sum + value, 0);
    const totalLiquidity = totalBidLiquidity + totalAskLiquidity;
    
    for (const exchange of Object.keys(bidsByExchange)) {
      distribution[exchange] = {
        bidLiquidity: bidsByExchange[exchange] || 0,
        askLiquidity: asksByExchange[exchange] || 0,
        totalLiquidity: (bidsByExchange[exchange] || 0) + (asksByExchange[exchange] || 0),
        percentage: ((bidsByExchange[exchange] || 0) + (asksByExchange[exchange] || 0)) / totalLiquidity * 100
      };
    }
    
    return distribution;
  }

  // Subscribe to KuCoin depth feed
  subscribeKuCoinDepth() {
    const exchange = this.exchanges.kucoin;
    exchange.ws.send(JSON.stringify({
      id: Date.now(),
      type: 'subscribe',
      topic: '/market/level2:BTC-USDT',
      response: true
    }));
  }

  // Fetch initial data from exchange
  async fetchInitialData(exchangeId) {
    const exchange = this.exchanges[exchangeId];
    
    try {
      // Fetch current balances
      const balances = await this.fetchExchangeBalances(exchangeId);
      exchange.balances = new Map(Object.entries(balances));
      
      // Fetch initial order books
      await this.fetchInitialOrderBooks(exchangeId);
      
    } catch (error) {
      console.error(`❌ Failed to fetch initial data from ${exchange.name}:`, error);
    }
  }

  // Fetch balances from exchange
  async fetchExchangeBalances(exchangeId) {
    // Implementation varies by exchange
    // This is a placeholder that would be implemented based on each exchange's API
    return {};
  }

  // Fetch initial order books
  async fetchInitialOrderBooks(exchangeId) {
    // Implementation varies by exchange
    // This would fetch the full order book via REST API
  }

  // Cleanup resources
  async disconnect() {
    for (const [exchangeId, exchange] of Object.entries(this.exchanges)) {
      if (exchange.ws) {
        exchange.ws.close();
        exchange.connected = false;
      }
    }
    
    console.log('🔌 Disconnected from all exchanges');
  }
}

module.exports = new LiquidityAggregatorService();