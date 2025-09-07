const jwt = require('jsonwebtoken');
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { service: 'auth-middleware' },
  transports: [
    new winston.transports.File({ filename: 'logs/auth.log' }),
    new winston.transports.Console(),
  ],
});

const authMiddleware = async (req, res, next) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');

    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'Access denied. No token provided.',
      });
    }

    const decoded = jwt.verify(
      token,
      process.env.JWT_SECRET || 'fallback_secret_key'
    );

    // In a real implementation, you would fetch user details from database
    // For now, we'll use the decoded token data
    req.user = {
      id: decoded.userId,
      email: decoded.email,
      username: decoded.username,
      tier: decoded.tier || 'bronze',
      stakeAmount: decoded.stakeAmount || 0,
      isAdmin: decoded.isAdmin || false,
      isSuperAdmin: decoded.isSuperAdmin || false,
      kycStatus: decoded.kycStatus || 'pending',
    };

    logger.info(`User authenticated: ${req.user.email}`);
    next();
  } catch (error) {
    logger.error('Authentication error:', error);

    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        message: 'Token expired. Please login again.',
      });
    }

    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        success: false,
        message: 'Invalid token.',
      });
    }

    res.status(401).json({
      success: false,
      message: 'Authentication failed.',
    });
  }
};

// Optional middleware for admin-only routes
const adminMiddleware = (req, res, next) => {
  if (!req.user.isAdmin && !req.user.isSuperAdmin) {
    return res.status(403).json({
      success: false,
      message: 'Access denied. Admin privileges required.',
    });
  }
  next();
};

// Optional middleware for super admin-only routes
const superAdminMiddleware = (req, res, next) => {
  if (!req.user.isSuperAdmin) {
    return res.status(403).json({
      success: false,
      message: 'Access denied. Super admin privileges required.',
    });
  }
  next();
};

// Middleware to check KYC status
const kycMiddleware = (req, res, next) => {
  if (req.user.kycStatus !== 'approved') {
    return res.status(403).json({
      success: false,
      message: 'KYC verification required to access this resource.',
    });
  }
  next();
};

// Middleware to check user tier
const tierMiddleware = (requiredTier) => {
  const tierLevels = { bronze: 1, silver: 2, gold: 3, platinum: 4 };

  return (req, res, next) => {
    const userTierLevel = tierLevels[req.user.tier] || 0;
    const requiredTierLevel = tierLevels[requiredTier] || 0;

    if (userTierLevel < requiredTierLevel) {
      return res.status(403).json({
        success: false,
        message: `${requiredTier} tier or higher required to access this resource.`,
      });
    }
    next();
  };
};

module.exports = {
  authMiddleware,
  adminMiddleware,
  superAdminMiddleware,
  kycMiddleware,
  tierMiddleware,
};

// Export default as authMiddleware for backward compatibility
module.exports = authMiddleware;
module.exports.adminMiddleware = adminMiddleware;
module.exports.superAdminMiddleware = superAdminMiddleware;
module.exports.kycMiddleware = kycMiddleware;
module.exports.tierMiddleware = tierMiddleware;
