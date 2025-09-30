const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const winston = require('winston');
const { Server } = require('socket.io');
const http = require('http');

// Import routes
const alphaRoutes = require('./routes/alphaRoutes');
const investorRoutes = require('./routes/investorRoutes');
const tokenRoutes = require('./routes/tokenRoutes');
const riskRoutes = require('./routes/riskRoutes');

// Import middleware
const authMiddleware = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');

// Import services
const AlphaMarketService = require('./services/AlphaMarketService');
const RiskAssessmentService = require('./services/RiskAssessmentService');
const NotificationService = require('./services/NotificationService');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: process.env.FRONTEND_URL || 'http://localhost:3000',
    methods: ['GET', 'POST'],
  },
});

// Logger configuration
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'alpha-market-trading' },
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
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
});
app.use('/api/', limiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Database connection
mongoose
  .connect(
    process.env.MONGODB_URI || 'mongodb://localhost:27017/tigerex_alpha_market',
    {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    }
  )
  .then(() => {
    logger.info('Connected to MongoDB - Alpha Market Trading');
  })
  .catch((error) => {
    logger.error('MongoDB connection error:', error);
    process.exit(1);
  });

// Socket.IO connection handling
io.on('connection', (socket) => {
  logger.info(`Client connected: ${socket.id}`);

  socket.on('join_alpha_room', (data) => {
    socket.join(`alpha_${data.tokenId}`);
    logger.info(
      `Client ${socket.id} joined alpha room for token ${data.tokenId}`
    );
  });

  socket.on('disconnect', () => {
    logger.info(`Client disconnected: ${socket.id}`);
  });
});

// Make io available to routes
app.set('io', io);

// Routes
app.use('/api/alpha', alphaRoutes);
app.use('/api/investors', investorRoutes);
app.use('/api/tokens', tokenRoutes);
app.use('/api/risk', riskRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: 'alpha-market-trading',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
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

const PORT = process.env.PORT || 3001;

server.listen(PORT, () => {
  logger.info(`Alpha Market Trading Service running on port ${PORT}`);

  // Initialize services
  AlphaMarketService.initialize();
  RiskAssessmentService.initialize();
  NotificationService.initialize(io);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    mongoose.connection.close();
    process.exit(0);
  });
});

module.exports = app;
