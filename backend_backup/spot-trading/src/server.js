const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const winston = require('winston');
const http = require('http');
const socketIo = require('socket.io');

// Import routes
const tradingRoutes = require('./routes/tradingRoutes');
const orderRoutes = require('./routes/orderRoutes');
const portfolioRoutes = require('./routes/portfolioRoutes');
const marketDataRoutes = require('./routes/marketDataRoutes');

// Import middleware
const authMiddleware = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');

// Import services
const TradingEngine = require('./services/TradingEngine');
const OrderBookService = require('./services/OrderBookService');
const MarketDataService = require('./services/MarketDataService');
const PortfolioService = require('./services/PortfolioService');
const WebSocketService = require('./services/WebSocketService');

const app = express();
// Admin routes
const adminRoutes = require('./admin/admin_routes');
app.use('/admin', adminRoutes);

const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: process.env.FRONTEND_URL || 'http://localhost:3000',
    methods: ['GET', 'POST'],
  },
});

const PORT = process.env.PORT || 3003;

// Logger configuration
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'spot-trading-service' },
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple(),
    }),
  ],
});

// Security middleware
app.use(helmet());
app.use(
  cors({
    origin: process.env.FRONTEND_URL || 'http://localhost:3000',
    credentials: true,
  })
);

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 1000, // limit each IP to 1000 requests per windowMs (higher for trading)
  message: 'Too many requests from this IP, please try again later.',
});
app.use('/api/', limiter);

// Stricter rate limiting for order placement
const orderLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 100, // limit each IP to 100 order requests per minute
  message: 'Too many order requests, please try again later.',
});
app.use('/api/orders', orderLimiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Database connection
mongoose
  .connect(
    process.env.MONGODB_URI || 'mongodb://localhost:27017/tigerex_spot_trading',
    {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    }
  )
  .then(() => {
    logger.info('Connected to MongoDB - Spot Trading Service');
  })
  .catch((error) => {
    logger.error('MongoDB connection error:', error);
    process.exit(1);
  });

// Routes
app.use('/api/trading', tradingRoutes);
app.use('/api/orders', orderRoutes);
app.use('/api/portfolio', portfolioRoutes);
app.use('/api/market-data', marketDataRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: 'spot-trading-service',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    orderBook: OrderBookService.getHealthStatus(),
    tradingEngine: TradingEngine.getHealthStatus(),
  });
});

// Error handling middleware
app.use(errorHandler);

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    message: 'Route not found',
  });
});

// Initialize services
const initializeServices = async () => {
  try {
    logger.info('Initializing Spot Trading Services...');

    // Initialize WebSocket service
    WebSocketService.initialize(io);

    // Initialize Trading Engine
    await TradingEngine.initialize();

    // Initialize Order Book Service
    await OrderBookService.initialize();

    // Initialize Market Data Service
    await MarketDataService.initialize();

    // Initialize Portfolio Service
    await PortfolioService.initialize();

    logger.info('All Spot Trading Services initialized successfully');
  } catch (error) {
    logger.error('Failed to initialize services:', error);
    process.exit(1);
  }
};

server.listen(PORT, async () => {
  logger.info(`Spot Trading Service running on port ${PORT}`);
  await initializeServices();
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    mongoose.connection.close();
    TradingEngine.shutdown();
    OrderBookService.shutdown();
    MarketDataService.shutdown();
    process.exit(0);
  });
});

module.exports = { app, server, io };
