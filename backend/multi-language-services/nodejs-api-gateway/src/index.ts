/**
 * TigerEx API Gateway
 * High-performance API Gateway written in Node.js/TypeScript
 * Part of TigerEx Multi-Language Microservices Architecture
 */

import express, { Request, Response, NextFunction } from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import rateLimit from 'express-rate-limit';
import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';
import morgan from 'morgan';
import { v4 as uuidv4 } from 'uuid';
import Redis from 'ioredis';
import jwt from 'jsonwebtoken';
import { WebSocketServer, WebSocket } from 'ws';
import http from 'http';
import https from 'https';

// Types
interface ServiceConfig {
  name: string;
  url: string;
  healthCheck: string;
  timeout: number;
  retries: number;
}

interface User {
  id: string;
  email: string;
  role: string;
  tier: string;
  permissions: string[];
}

interface RateLimitConfig {
  windowMs: number;
  max: number;
  message: string;
}

interface ExchangeConfig {
  id: string;
  name: string;
  status: 'active' | 'paused' | 'halted' | 'maintenance';
  domain: string;
  whiteLabel: boolean;
  parentExchangeId?: string;
}

// Configuration
const SERVICE_REGISTRY: Record<string, ServiceConfig> = {
  'trading-engine': {
    name: 'trading-engine',
    url: process.env.TRADING_ENGINE_URL || 'http://localhost:8080',
    healthCheck: '/health',
    timeout: 30000,
    retries: 3,
  },
  'order-matching': {
    name: 'order-matching',
    url: process.env.ORDER_MATCHING_URL || 'http://localhost:8081',
    healthCheck: '/health',
    timeout: 10000,
    retries: 3,
  },
  'fee-management': {
    name: 'fee-management',
    url: process.env.FEE_MANAGEMENT_URL || 'http://localhost:8180',
    healthCheck: '/health',
    timeout: 5000,
    retries: 2,
  },
  'user-service': {
    name: 'user-service',
    url: process.env.USER_SERVICE_URL || 'http://localhost:8001',
    healthCheck: '/health',
    timeout: 5000,
    retries: 2,
  },
  'wallet-service': {
    name: 'wallet-service',
    url: process.env.WALLET_SERVICE_URL || 'http://localhost:8002',
    healthCheck: '/health',
    timeout: 10000,
    retries: 3,
  },
  'auth-service': {
    name: 'auth-service',
    url: process.env.AUTH_SERVICE_URL || 'http://localhost:8003',
    healthCheck: '/health',
    timeout: 5000,
    retries: 2,
  },
  'admin-service': {
    name: 'admin-service',
    url: process.env.ADMIN_SERVICE_URL || 'http://localhost:8004',
    healthCheck: '/health',
    timeout: 5000,
    retries: 2,
  },
  'kyc-service': {
    name: 'kyc-service',
    url: process.env.KYC_SERVICE_URL || 'http://localhost:8005',
    healthCheck: '/health',
    timeout: 10000,
    retries: 2,
  },
  'notification-service': {
    name: 'notification-service',
    url: process.env.NOTIFICATION_SERVICE_URL || 'http://localhost:8006',
    healthCheck: '/health',
    timeout: 5000,
    retries: 2,
  },
  'market-data': {
    name: 'market-data',
    url: process.env.MARKET_DATA_URL || 'http://localhost:8007',
    healthCheck: '/health',
    timeout: 5000,
    retries: 2,
  },
};

// Rate limit configurations by tier
const RATE_LIMITS: Record<string, RateLimitConfig> = {
  regular: { windowMs: 60000, max: 100, message: 'Rate limit exceeded for regular tier' },
  vip1: { windowMs: 60000, max: 200, message: 'Rate limit exceeded for VIP1 tier' },
  vip2: { windowMs: 60000, max: 300, message: 'Rate limit exceeded for VIP2 tier' },
  vip3: { windowMs: 60000, max: 400, message: 'Rate limit exceeded for VIP3 tier' },
  vip4: { windowMs: 60000, max: 500, message: 'Rate limit exceeded for VIP4 tier' },
  vip5: { windowMs: 60000, max: 600, message: 'Rate limit exceeded for VIP5 tier' },
  vip_elite: { windowMs: 60000, max: 1000, message: 'Rate limit exceeded for VIP Elite tier' },
  institutional: { windowMs: 60000, max: 2000, message: 'Rate limit exceeded for Institutional tier' },
  market_maker: { windowMs: 60000, max: 5000, message: 'Rate limit exceeded for Market Maker tier' },
};

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Redis client for caching and session management
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

// Exchange configuration
let exchangeConfig: ExchangeConfig = {
  id: process.env.EXCHANGE_ID || 'TIGEREX-MAIN',
  name: process.env.EXCHANGE_NAME || 'TigerEx',
  status: 'active',
  domain: process.env.EXCHANGE_DOMAIN || 'tigerex.io',
  whiteLabel: process.env.WHITE_LABEL === 'true',
};

// Middleware setup
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGINS?.split(',') || '*',
  credentials: true,
}));
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging
app.use(morgan('combined'));

// Request ID middleware
app.use((req: Request, res: Response, next: NextFunction) => {
  req.headers['x-request-id'] = req.headers['x-request-id'] || uuidv4();
  res.setHeader('x-request-id', req.headers['x-request-id'] as string);
  next();
});

// Exchange status check middleware
const checkExchangeStatus = (req: Request, res: Response, next: NextFunction) => {
  const exemptPaths = ['/health', '/api/v1/exchange/status', '/api/v1/admin'];
  const isAdmin = req.user?.role === 'admin' || req.user?.role === 'super_admin';
  
  if (exemptPaths.some(path => req.path.startsWith(path)) || isAdmin) {
    return next();
  }

  if (exchangeConfig.status === 'halted') {
    return res.status(503).json({
      error: 'Exchange halted',
      message: 'Trading is temporarily suspended. Please try again later.',
      exchangeId: exchangeConfig.id,
    });
  }

  if (exchangeConfig.status === 'maintenance') {
    return res.status(503).json({
      error: 'Under maintenance',
      message: 'Exchange is under maintenance. Please check back soon.',
      exchangeId: exchangeConfig.id,
    });
  }

  if (exchangeConfig.status === 'paused') {
    return res.status(503).json({
      error: 'Exchange paused',
      message: 'Trading is paused. Please try again later.',
      exchangeId: exchangeConfig.id,
    });
  }

  next();
};

// JWT Authentication middleware
const authenticate = async (req: Request, res: Response, next: NextFunction) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key') as User;
    
    // Check if token is blacklisted
    const isBlacklisted = await redis.get(`blacklist:${token}`);
    if (isBlacklisted) {
      return res.status(401).json({ error: 'Token has been revoked' });
    }

    // Get user from cache or fetch from user service
    const cachedUser = await redis.get(`user:${decoded.id}`);
    if (cachedUser) {
      req.user = JSON.parse(cachedUser);
    } else {
      req.user = decoded;
      // Cache user for 5 minutes
      await redis.setex(`user:${decoded.id}`, 300, JSON.stringify(decoded));
    }

    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};

// Rate limiting middleware with tier-based limits
const createRateLimiter = (tier: string = 'regular') => {
  const config = RATE_LIMITS[tier] || RATE_LIMITS.regular;
  return rateLimit({
    windowMs: config.windowMs,
    max: config.max,
    message: { error: config.message },
    keyGenerator: (req: Request) => {
      return req.user?.id || req.ip;
    },
    handler: (req: Request, res: Response) => {
      res.status(429).json({
        error: 'Too many requests',
        message: config.message,
        retryAfter: Math.ceil(config.windowMs / 1000),
      });
    },
  });
};

// Dynamic rate limiting based on user tier
const dynamicRateLimit = async (req: Request, res: Response, next: NextFunction) => {
  const tier = req.user?.tier || 'regular';
  const limiter = createRateLimiter(tier);
  limiter(req, res, next);
};

// Permission check middleware
const checkPermission = (...requiredPermissions: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const userPermissions = req.user?.permissions || [];
    const hasPermission = requiredPermissions.some(perm => 
      userPermissions.includes(perm) || userPermissions.includes('*')
    );

    if (!hasPermission) {
      return res.status(403).json({
        error: 'Forbidden',
        message: 'You do not have permission to access this resource',
      });
    }

    next();
  };
};

// Role check middleware
const checkRole = (...requiredRoles: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const userRole = req.user?.role;
    
    if (!userRole || !requiredRoles.includes(userRole)) {
      return res.status(403).json({
        error: 'Forbidden',
        message: 'You do not have the required role to access this resource',
      });
    }

    next();
  };
};

// Proxy middleware factory
const createProxy = (serviceKey: string) => {
  const service = SERVICE_REGISTRY[serviceKey];
  if (!service) {
    throw new Error(`Service ${serviceKey} not found in registry`);
  }

  return createProxyMiddleware({
    target: service.url,
    changeOrigin: true,
    timeout: service.timeout,
    proxyTimeout: service.timeout,
    pathRewrite: (path: string) => {
      // Remove the service prefix from the path
      return path.replace(new RegExp(`^/api/v1/${serviceKey}`), '/api/v1');
    },
    on: {
      error: (err: Error, req: Request, res: Response) => {
        console.error(`Proxy error for ${serviceKey}:`, err.message);
        res.status(502).json({
          error: 'Bad Gateway',
          message: `Failed to connect to ${service.name} service`,
          serviceId: serviceKey,
        });
      },
      proxyReq: (proxyReq: http.ClientRequest, req: Request) => {
        // Add custom headers
        proxyReq.setHeader('X-Exchange-Id', exchangeConfig.id);
        proxyReq.setHeader('X-User-Id', req.user?.id || 'anonymous');
        proxyReq.setHeader('X-User-Tier', req.user?.tier || 'regular');
        proxyReq.setHeader('X-Request-Id', req.headers['x-request-id'] as string);
      },
    },
  });
};

// Health check endpoint
app.get('/health', async (req: Request, res: Response) => {
  const serviceHealth: Record<string, any> = {};
  
  for (const [key, service] of Object.entries(SERVICE_REGISTRY)) {
    try {
      const response = await fetch(`${service.url}${service.healthCheck}`, {
        method: 'GET',
        signal: AbortSignal.timeout(2000),
      });
      serviceHealth[key] = {
        status: response.ok ? 'healthy' : 'unhealthy',
        responseTime: Date.now(),
      };
    } catch (error) {
      serviceHealth[key] = {
        status: 'unreachable',
        error: (error as Error).message,
      };
    }
  }

  const allHealthy = Object.values(serviceHealth).every(
    (s: any) => s.status === 'healthy'
  );

  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'healthy' : 'degraded',
    service: 'api-gateway',
    exchangeId: exchangeConfig.id,
    exchangeStatus: exchangeConfig.status,
    timestamp: new Date().toISOString(),
    services: serviceHealth,
  });
});

// Exchange status endpoints
app.get('/api/v1/exchange/status', (req: Request, res: Response) => {
  res.json({
    exchangeId: exchangeConfig.id,
    name: exchangeConfig.name,
    status: exchangeConfig.status,
    domain: exchangeConfig.domain,
    whiteLabel: exchangeConfig.whiteLabel,
    parentExchangeId: exchangeConfig.parentExchangeId,
    timestamp: new Date().toISOString(),
  });
});

app.post('/api/v1/exchange/status', 
  authenticate, 
  checkRole('admin', 'super_admin'), 
  (req: Request, res: Response) => {
    const { status } = req.body;
    
    if (!['active', 'paused', 'halted', 'maintenance'].includes(status)) {
      return res.status(400).json({ error: 'Invalid status' });
    }

    exchangeConfig.status = status;
    
    res.json({
      message: 'Exchange status updated',
      exchangeId: exchangeConfig.id,
      status: exchangeConfig.status,
      updatedBy: req.user?.id,
      timestamp: new Date().toISOString(),
    });
  }
);

// White-label configuration endpoint
app.post('/api/v1/exchange/white-label',
  authenticate,
  checkRole('super_admin'),
  async (req: Request, res: Response) => {
    const { exchangeId, exchangeName, domain, parentExchangeId } = req.body;

    exchangeConfig = {
      id: exchangeId,
      name: exchangeName,
      status: 'active',
      domain,
      whiteLabel: true,
      parentExchangeId,
    };

    // Store in Redis for persistence
    await redis.set('exchange:config', JSON.stringify(exchangeConfig));

    res.json({
      message: 'White-label exchange configured successfully',
      config: exchangeConfig,
    });
  }
);

// Trading routes (with authentication and rate limiting)
app.use('/api/v1/trade', 
  authenticate, 
  checkExchangeStatus, 
  dynamicRateLimit, 
  createProxy('trading-engine')
);

app.use('/api/v1/order', 
  authenticate, 
  checkExchangeStatus, 
  dynamicRateLimit, 
  createProxy('order-matching')
);

app.use('/api/v1/orderbook', 
  authenticate, 
  dynamicRateLimit, 
  createProxy('order-matching')
);

// User and wallet routes
app.use('/api/v1/user', 
  authenticate, 
  dynamicRateLimit, 
  createProxy('user-service')
);

app.use('/api/v1/wallet', 
  authenticate, 
  dynamicRateLimit, 
  createProxy('wallet-service')
);

// Fee management routes
app.use('/api/v1/fees', 
  authenticate, 
  dynamicRateLimit, 
  createProxy('fee-management')
);

// Authentication routes (no authentication required for login/register)
app.use('/api/v1/auth', createProxy('auth-service'));

// Admin routes (admin only)
app.use('/api/v1/admin', 
  authenticate, 
  checkRole('admin', 'super_admin'), 
  createProxy('admin-service')
);

// KYC routes
app.use('/api/v1/kyc', 
  authenticate, 
  dynamicRateLimit, 
  createProxy('kyc-service')
);

// Notification routes
app.use('/api/v1/notifications', 
  authenticate, 
  dynamicRateLimit, 
  createProxy('notification-service')
);

// Market data routes (public with rate limiting)
app.use('/api/v1/market', 
  rateLimit({ windowMs: 60000, max: 1000 }), 
  createProxy('market-data')
);

// WebSocket server for real-time data
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

interface WSClient extends WebSocket {
  userId?: string;
  subscriptions?: Set<string>;
  isAlive?: boolean;
}

const clients = new Map<string, Set<WSClient>>();
const channelSubscriptions = new Map<string, Set<WSClient>>();

wss.on('connection', (ws: WSClient) => {
  ws.subscriptions = new Set();
  ws.isAlive = true;

  ws.on('pong', () => {
    ws.isAlive = true;
  });

  ws.on('message', async (data: Buffer) => {
    try {
      const message = JSON.parse(data.toString());
      
      switch (message.type) {
        case 'subscribe':
          handleSubscribe(ws, message);
          break;
        case 'unsubscribe':
          handleUnsubscribe(ws, message);
          break;
        case 'authenticate':
          await handleAuthenticate(ws, message);
          break;
        case 'ping':
          ws.send(JSON.stringify({ type: 'pong' }));
          break;
        default:
          ws.send(JSON.stringify({ error: 'Unknown message type' }));
      }
    } catch (error) {
      ws.send(JSON.stringify({ error: 'Invalid message format' }));
    }
  });

  ws.on('close', () => {
    if (ws.userId) {
      clients.get(ws.userId)?.delete(ws);
    }
    ws.subscriptions?.forEach(channel => {
      channelSubscriptions.get(channel)?.delete(ws);
    });
  });
});

function handleSubscribe(ws: WSClient, message: any) {
  const { channel } = message;
  
  if (!channel) {
    return ws.send(JSON.stringify({ error: 'Channel required' }));
  }

  ws.subscriptions?.add(channel);
  
  if (!channelSubscriptions.has(channel)) {
    channelSubscriptions.set(channel, new Set());
  }
  channelSubscriptions.get(channel)?.add(ws);

  ws.send(JSON.stringify({ 
    type: 'subscribed', 
    channel,
    message: `Subscribed to ${channel}`,
  }));
}

function handleUnsubscribe(ws: WSClient, message: any) {
  const { channel } = message;
  
  ws.subscriptions?.delete(channel);
  channelSubscriptions.get(channel)?.delete(ws);

  ws.send(JSON.stringify({ 
    type: 'unsubscribed', 
    channel,
    message: `Unsubscribed from ${channel}`,
  }));
}

async function handleAuthenticate(ws: WSClient, message: any) {
  const { token } = message;
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key') as User;
    ws.userId = decoded.id;
    
    if (!clients.has(decoded.id)) {
      clients.set(decoded.id, new Set());
    }
    clients.get(decoded.id)?.add(ws);

    ws.send(JSON.stringify({ 
      type: 'authenticated', 
      userId: decoded.id,
      message: 'WebSocket authenticated successfully',
    }));
  } catch (error) {
    ws.send(JSON.stringify({ error: 'Authentication failed' }));
  }
}

// Broadcast to channel
function broadcast(channel: string, data: any) {
  const subscribers = channelSubscriptions.get(channel);
  if (subscribers) {
    const message = JSON.stringify({ channel, data, timestamp: Date.now() });
    subscribers.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  }
}

// Heartbeat for connection health
setInterval(() => {
  wss.clients.forEach((ws: WSClient) => {
    if (!ws.isAlive) {
      return ws.terminate();
    }
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);

// Subscribe to Redis channels for cross-service messaging
const redisSubscriber = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

redisSubscriber.subscribe('order_updates', 'trade_updates', 'price_updates', 'system_alerts');

redisSubscriber.on('message', (channel: string, message: string) => {
  try {
    const data = JSON.parse(message);
    broadcast(channel, data);
  } catch (error) {
    console.error('Failed to parse Redis message:', error);
  }
});

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error('Error:', err);
  res.status(500).json({
    error: 'Internal Server Error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'An unexpected error occurred',
    requestId: req.headers['x-request-id'],
  });
});

// 404 handler
app.use((req: Request, res: Response) => {
  res.status(404).json({
    error: 'Not Found',
    message: `The requested resource ${req.path} was not found`,
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`TigerEx API Gateway running on port ${PORT}`);
  console.log(`Exchange ID: ${exchangeConfig.id}`);
  console.log(`Status: ${exchangeConfig.status}`);
  console.log(`WebSocket server ready for real-time data`);
});

export { app, server, broadcast };