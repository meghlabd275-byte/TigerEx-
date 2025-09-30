const jwt = require('jsonwebtoken');

const authMiddleware = async (req, res, next) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');

    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'Access token is required',
      });
    }

    // Verify token
    const decoded = jwt.verify(
      token,
      process.env.JWT_SECRET || 'your-secret-key'
    );

    // In a real application, you would fetch user from database
    // For now, we'll use the decoded token data
    req.user = {
      userId: decoded.userId,
      email: decoded.email,
      roles: decoded.roles || ['user'],
    };

    next();
  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        success: false,
        message: 'Invalid token',
      });
    } else if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        message: 'Token expired',
      });
    }

    res.status(500).json({
      success: false,
      message: 'Authentication failed',
      error: error.message,
    });
  }
};

// Optional authentication middleware (doesn't fail if no token)
const optionalAuth = async (req, res, next) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');

    if (token) {
      const decoded = jwt.verify(
        token,
        process.env.JWT_SECRET || 'your-secret-key'
      );
      req.user = {
        userId: decoded.userId,
        email: decoded.email,
        roles: decoded.roles || ['user'],
      };
    }

    next();
  } catch (error) {
    // Continue without authentication
    next();
  }
};

// Role-based authorization middleware
const authorize = (...roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Authentication required',
      });
    }

    const hasRole = roles.some((role) => req.user.roles.includes(role));
    if (!hasRole) {
      return res.status(403).json({
        success: false,
        message: 'Insufficient permissions',
      });
    }

    next();
  };
};

module.exports = {
  authMiddleware,
  optionalAuth,
  authorize,
};
