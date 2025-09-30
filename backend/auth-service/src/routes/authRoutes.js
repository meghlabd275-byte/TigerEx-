const express = require('express');
const router = express.Router();
const AuthService = require('../services/AuthService');
const TokenService = require('../services/TokenService');
const TwoFactorService = require('../services/TwoFactorService');
const EmailService = require('../services/EmailService');
const authMiddleware = require('../middleware/auth');
const {
  validateRegistration,
  validateLogin,
  validatePasswordReset,
} = require('../middleware/validation');

// Register new user
router.post('/register', validateRegistration, async (req, res) => {
  try {
    const {
      email,
      username,
      password,
      firstName,
      lastName,
      phoneNumber,
      country,
      referralCode,
    } = req.body;

    // Check if user already exists
    const existingUser = await AuthService.findUserByEmailOrUsername(
      email,
      username
    );
    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: 'User with this email or username already exists',
      });
    }

    // Create new user
    const userData = {
      email,
      username,
      password,
      firstName,
      lastName,
      phoneNumber,
      country,
      metadata: {
        registrationSource: 'web',
        userAgent: req.get('User-Agent'),
        registrationIP: req.ip,
      },
    };

    // Handle referral
    if (referralCode) {
      const referrer = await AuthService.findUserByReferralCode(referralCode);
      if (referrer) {
        userData.referredBy = referrer._id;
      }
    }

    const user = await AuthService.createUser(userData);

    // Send verification email
    const verificationToken = user.createEmailVerificationToken();
    await user.save();
    await EmailService.sendVerificationEmail(user.email, verificationToken);

    res.status(201).json({
      success: true,
      message:
        'User registered successfully. Please check your email for verification.',
      data: {
        userId: user.userId,
        email: user.email,
        username: user.username,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Registration failed',
      error: error.message,
    });
  }
});

// Login user
router.post('/login', validateLogin, async (req, res) => {
  try {
    const { emailOrUsername, password, twoFactorCode } = req.body;

    // Find user
    const user = await AuthService.findUserByEmailOrUsername(
      emailOrUsername,
      emailOrUsername
    );
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Invalid credentials',
      });
    }

    // Check if account is locked
    if (user.isLocked) {
      return res.status(423).json({
        success: false,
        message:
          'Account is temporarily locked due to too many failed login attempts',
      });
    }

    // Check if account is active
    if (user.accountStatus !== 'active') {
      return res.status(403).json({
        success: false,
        message: 'Account is not active. Please contact support.',
      });
    }

    // Verify password
    const isPasswordValid = await user.comparePassword(password);
    if (!isPasswordValid) {
      await user.incrementLoginAttempts();
      return res.status(401).json({
        success: false,
        message: 'Invalid credentials',
      });
    }

    // Check 2FA if enabled
    if (user.twoFactorEnabled) {
      if (!twoFactorCode) {
        return res.status(200).json({
          success: true,
          requiresTwoFactor: true,
          message: 'Two-factor authentication required',
        });
      }

      const isTwoFactorValid = TwoFactorService.verifyToken(
        user.twoFactorSecret,
        twoFactorCode
      );
      if (!isTwoFactorValid) {
        return res.status(401).json({
          success: false,
          message: 'Invalid two-factor authentication code',
        });
      }
    }

    // Reset login attempts on successful login
    await user.resetLoginAttempts();

    // Update last login and IP
    user.lastLogin = new Date();
    user.ipAddresses.push({
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      location: req.get('CF-IPCountry') || 'Unknown',
    });

    // Keep only last 10 IP addresses
    if (user.ipAddresses.length > 10) {
      user.ipAddresses = user.ipAddresses.slice(-10);
    }

    await user.save();

    // Generate tokens
    const accessToken = TokenService.generateAccessToken(user);
    const refreshToken = TokenService.generateRefreshToken(user);

    // Store refresh token
    await TokenService.storeRefreshToken(user.userId, refreshToken);

    res.json({
      success: true,
      message: 'Login successful',
      data: {
        user: user.toSafeObject(),
        accessToken,
        refreshToken,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Login failed',
      error: error.message,
    });
  }
});

// Refresh access token
router.post('/refresh', async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(401).json({
        success: false,
        message: 'Refresh token is required',
      });
    }

    // Verify refresh token
    const decoded = TokenService.verifyRefreshToken(refreshToken);
    if (!decoded) {
      return res.status(401).json({
        success: false,
        message: 'Invalid refresh token',
      });
    }

    // Check if refresh token exists in store
    const storedToken = await TokenService.getRefreshToken(decoded.userId);
    if (!storedToken || storedToken !== refreshToken) {
      return res.status(401).json({
        success: false,
        message: 'Refresh token not found or expired',
      });
    }

    // Get user
    const user = await AuthService.findUserByUserId(decoded.userId);
    if (!user || user.accountStatus !== 'active') {
      return res.status(401).json({
        success: false,
        message: 'User not found or account not active',
      });
    }

    // Generate new tokens
    const newAccessToken = TokenService.generateAccessToken(user);
    const newRefreshToken = TokenService.generateRefreshToken(user);

    // Update stored refresh token
    await TokenService.storeRefreshToken(user.userId, newRefreshToken);

    res.json({
      success: true,
      message: 'Token refreshed successfully',
      data: {
        accessToken: newAccessToken,
        refreshToken: newRefreshToken,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Token refresh failed',
      error: error.message,
    });
  }
});

// Logout user
router.post('/logout', authMiddleware, async (req, res) => {
  try {
    // Remove refresh token from store
    await TokenService.removeRefreshToken(req.user.userId);

    res.json({
      success: true,
      message: 'Logout successful',
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Logout failed',
      error: error.message,
    });
  }
});

// Verify email
router.get('/verify-email/:token', async (req, res) => {
  try {
    const { token } = req.params;

    const user = await AuthService.verifyEmailToken(token);
    if (!user) {
      return res.status(400).json({
        success: false,
        message: 'Invalid or expired verification token',
      });
    }

    user.isEmailVerified = true;
    user.emailVerificationToken = undefined;
    user.emailVerificationExpires = undefined;

    // Activate account if it was pending
    if (user.accountStatus === 'pending') {
      user.accountStatus = 'active';
    }

    await user.save();

    res.json({
      success: true,
      message: 'Email verified successfully',
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Email verification failed',
      error: error.message,
    });
  }
});

// Resend verification email
router.post('/resend-verification', async (req, res) => {
  try {
    const { email } = req.body;

    const user = await AuthService.findUserByEmail(email);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found',
      });
    }

    if (user.isEmailVerified) {
      return res.status(400).json({
        success: false,
        message: 'Email is already verified',
      });
    }

    // Generate new verification token
    const verificationToken = user.createEmailVerificationToken();
    await user.save();

    // Send verification email
    await EmailService.sendVerificationEmail(user.email, verificationToken);

    res.json({
      success: true,
      message: 'Verification email sent successfully',
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to send verification email',
      error: error.message,
    });
  }
});

// Forgot password
router.post('/forgot-password', async (req, res) => {
  try {
    const { email } = req.body;

    const user = await AuthService.findUserByEmail(email);
    if (!user) {
      // Don't reveal if user exists or not
      return res.json({
        success: true,
        message: 'If the email exists, a password reset link has been sent',
      });
    }

    // Generate password reset token
    const resetToken = user.createPasswordResetToken();
    await user.save();

    // Send password reset email
    await EmailService.sendPasswordResetEmail(user.email, resetToken);

    res.json({
      success: true,
      message: 'If the email exists, a password reset link has been sent',
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to process password reset request',
      error: error.message,
    });
  }
});

// Reset password
router.post(
  '/reset-password/:token',
  validatePasswordReset,
  async (req, res) => {
    try {
      const { token } = req.params;
      const { password } = req.body;

      const user = await AuthService.verifyPasswordResetToken(token);
      if (!user) {
        return res.status(400).json({
          success: false,
          message: 'Invalid or expired password reset token',
        });
      }

      // Update password
      user.password = password;
      user.passwordResetToken = undefined;
      user.passwordResetExpires = undefined;

      // Reset login attempts
      user.loginAttempts = 0;
      user.lockUntil = undefined;

      await user.save();

      res.json({
        success: true,
        message: 'Password reset successfully',
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Password reset failed',
        error: error.message,
      });
    }
  }
);

// Change password (authenticated)
router.post('/change-password', authMiddleware, async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body;

    const user = await AuthService.findUserByUserId(req.user.userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found',
      });
    }

    // Verify current password
    const isCurrentPasswordValid = await user.comparePassword(currentPassword);
    if (!isCurrentPasswordValid) {
      return res.status(400).json({
        success: false,
        message: 'Current password is incorrect',
      });
    }

    // Update password
    user.password = newPassword;
    await user.save();

    res.json({
      success: true,
      message: 'Password changed successfully',
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Password change failed',
      error: error.message,
    });
  }
});

// Get current user
router.get('/me', authMiddleware, async (req, res) => {
  try {
    const user = await AuthService.findUserByUserId(req.user.userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found',
      });
    }

    res.json({
      success: true,
      data: user.toSafeObject(),
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to get user information',
      error: error.message,
    });
  }
});

module.exports = router;
