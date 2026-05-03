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
export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

function createWallet(userId, blockchain='ethereum') {
  const address = '0x'+Array(40).fill().map(()=>Math.random().toString(16)[2]).join('');
  const seed='abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';return{address,seed:seed.split(' ').slice(0,24).join(' '),blockchain,ownership:'USER_OWNS',userId};}
