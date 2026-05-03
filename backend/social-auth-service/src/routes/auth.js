/**
 * Authentication Routes (Email/Password + Token Management)
 */

const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const User = require('../models/User');
const AuditLog = require('../models/AuditLog');

// Auth middleware
const authMiddleware = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '') || req.cookies?.token;
    
    if (!token) {
      return res.status(401).json({ success: false, message: 'No token provided' });
    }
    
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'tigerex-jwt-secret');
    const user = await User.findById(decoded.id).select('-password -twoFactorSecret');
    
    if (!user) {
      return res.status(401).json({ success: false, message: 'User not found' });
    }
    
    if (user.status !== 'active') {
      return res.status(403).json({ success: false, message: `Account is ${user.status}` });
    }
    
    req.user = user;
    req.token = token;
    next();
  } catch (error) {
    res.status(401).json({ success: false, message: 'Invalid token' });
  }
};

// Admin middleware
const adminMiddleware = async (req, res, next) => {
  if (!['admin', 'super_admin'].includes(req.user.role)) {
    return res.status(403).json({ success: false, message: 'Admin access required' });
  }
  next();
};

// Register
router.post('/register', async (req, res) => {
  try {
    const { email, username, password, firstName, lastName, referralCode } = req.body;
    
    // Validate input
    if (!email || !username || !password) {
      return res.status(400).json({ success: false, message: 'Email, username, and password are required' });
    }
    
    // Check for existing user
    const existingUser = await User.findOne({
      $or: [{ email: email.toLowerCase() }, { username: username.toLowerCase() }],
    });
    
    if (existingUser) {
      return res.status(400).json({ success: false, message: 'User already exists' });
    }
    
    // Create user
    const user = new User({
      email: email.toLowerCase(),
      username: username.toLowerCase(),
      password,
      profile: { firstName, lastName },
      status: 'active',
      role: 'user',
      metadata: {
        registrationSource: 'email',
        registrationIP: req.ip,
        userAgent: req.get('User-Agent'),
      },
    });
    
    // Handle referral
    if (referralCode) {
      const referrer = await User.findByReferralCode(referralCode);
      if (referrer) {
        user.referral.referredBy = referrer._id;
      }
    }
    
    await user.save();
    
    // Generate tokens
    const token = user.generateJWT();
    const refreshToken = user.generateRefreshToken();
    
    await AuditLog.log({
      userId: user._id,
      action: 'register',
      category: 'auth',
      ipAddress: req.ip,
      userAgent: req.get('User-Agent'),
      status: 'success',
    });
    
    res.status(201).json({
      success: true,
      message: 'Registration successful',
      data: {
        user: {
          id: user._id,
          userId: user.userId,
          email: user.email,
          username: user.username,
          role: user.role,
          profile: user.profile,
        },
        token,
        refreshToken,
      },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Login
router.post('/login', async (req, res) => {
  try {
    const { emailOrUsername, password, twoFactorCode } = req.body;
    
    if (!emailOrUsername || !password) {
      return res.status(400).json({ success: false, message: 'Email/username and password are required' });
    }
    
    // Find user
    const user = await User.findOne({
      $or: [
        { email: emailOrUsername.toLowerCase() },
        { username: emailOrUsername.toLowerCase() },
      ],
    }).select('+password +twoFactorSecret');
    
    if (!user) {
      await AuditLog.log({
        action: 'failed_login',
        category: 'auth',
        ipAddress: req.ip,
        userAgent: req.get('User-Agent'),
        details: { reason: 'user_not_found', emailOrUsername },
        status: 'failed',
      });
      
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }
    
    // Check if account is locked
    if (user.isLocked()) {
      await AuditLog.log({
        userId: user._id,
        action: 'failed_login',
        category: 'auth',
        ipAddress: req.ip,
        details: { reason: 'account_locked' },
        status: 'failed',
      });
      
      return res.status(423).json({ success: false, message: 'Account is temporarily locked due to too many failed attempts' });
    }
    
    // Verify password
    const isMatch = await user.comparePassword(password);
    if (!isMatch) {
      await user.incLoginAttempts();
      
      await AuditLog.log({
        userId: user._id,
        action: 'failed_login',
        category: 'auth',
        ipAddress: req.ip,
        details: { reason: 'invalid_password' },
        status: 'failed',
      });
      
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
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
      
      // Verify 2FA code
      const speakeasy = require('speakeasy');
      const isValid = speakeasy.totp.verify({
        secret: user.twoFactorSecret,
        encoding: 'base32',
        token: twoFactorCode,
      });
      
      if (!isValid) {
        await AuditLog.log({
          userId: user._id,
          action: 'failed_login',
          category: 'auth',
          ipAddress: req.ip,
          details: { reason: 'invalid_2fa' },
          status: 'failed',
        });
        
        return res.status(401).json({ success: false, message: 'Invalid two-factor code' });
      }
    }
    
    // Check account status
    if (user.status !== 'active') {
      return res.status(403).json({ success: false, message: `Account is ${user.status}` });
    }
    
    // Reset login attempts
    await user.resetLoginAttempts();
    
    // Update last login
    user.lastLogin = new Date();
    user.lastLoginIP = req.ip;
    await user.save();
    
    // Generate tokens
    const token = user.generateJWT();
    const refreshToken = user.generateRefreshToken();
    
    await AuditLog.log({
      userId: user._id,
      action: 'login',
      category: 'auth',
      ipAddress: req.ip,
      userAgent: req.get('User-Agent'),
      status: 'success',
    });
    
    res.json({
      success: true,
      message: 'Login successful',
      data: {
        user: {
          id: user._id,
          userId: user.userId,
          email: user.email,
          username: user.username,
          role: user.role,
          profile: user.profile,
          permissions: user.permissions,
        },
        token,
        refreshToken,
      },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Refresh token
router.post('/refresh', async (req, res) => {
  try {
    const { refreshToken } = req.body;
    
    if (!refreshToken) {
      return res.status(400).json({ success: false, message: 'Refresh token required' });
    }
    
    const decoded = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET || 'tigerex-refresh-secret');
    
    if (decoded.type !== 'refresh') {
      return res.status(401).json({ success: false, message: 'Invalid refresh token' });
    }
    
    const user = await User.findById(decoded.id);
    if (!user || user.status !== 'active') {
      return res.status(401).json({ success: false, message: 'User not found or inactive' });
    }
    
    const newToken = user.generateJWT();
    const newRefreshToken = user.generateRefreshToken();
    
    res.json({
      success: true,
      data: {
        token: newToken,
        refreshToken: newRefreshToken,
      },
    });
  } catch (error) {
    res.status(401).json({ success: false, message: 'Invalid refresh token' });
  }
});

// Logout
router.post('/logout', authMiddleware, async (req, res) => {
  try {
    await AuditLog.log({
      userId: req.user._id,
      action: 'logout',
      category: 'auth',
      ipAddress: req.ip,
      status: 'success',
    });
    
    res.json({ success: true, message: 'Logged out successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Get current user
router.get('/me', authMiddleware, async (req, res) => {
  try {
    res.json({ success: true, user: req.user });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Update profile
router.put('/profile', authMiddleware, async (req, res) => {
  try {
    const updates = req.body;
    const allowedUpdates = ['firstName', 'lastName', 'displayName', 'bio', 'language', 'timezone'];
    
    const user = await User.findById(req.user._id);
    
    allowedUpdates.forEach(field => {
      if (updates[field] !== undefined) {
        user.profile[field] = updates[field];
      }
    });
    
    await user.save();
    
    await AuditLog.log({
      userId: user._id,
      action: 'profile_update',
      category: 'profile',
      ipAddress: req.ip,
      status: 'success',
    });
    
    res.json({ success: true, user });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Change password
router.put('/password', authMiddleware, async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body;
    
    const user = await User.findById(req.user._id).select('+password');
    
    const isMatch = await user.comparePassword(currentPassword);
    if (!isMatch) {
      return res.status(401).json({ success: false, message: 'Current password is incorrect' });
    }
    
    user.password = newPassword;
    await user.save();
    
    await AuditLog.log({
      userId: user._id,
      action: 'password_change',
      category: 'security',
      ipAddress: req.ip,
      status: 'success',
    });
    
    res.json({ success: true, message: 'Password changed successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Forgot password
router.post('/forgot-password', async (req, res) => {
  try {
    const { email } = req.body;
    
    const user = await User.findByEmail(email);
    if (!user) {
      return res.json({ success: true, message: 'If the email exists, a reset link has been sent' });
    }
    
    const resetToken = user.createPasswordResetToken();
    await user.save();
    
    // TODO: Send email with reset token
    // await EmailService.sendPasswordResetEmail(user.email, resetToken);
    
    await AuditLog.log({
      userId: user._id,
      action: 'password_reset',
      category: 'security',
      ipAddress: req.ip,
      status: 'success',
    });
    
    res.json({ success: true, message: 'If the email exists, a reset link has been sent' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Reset password
router.post('/reset-password', async (req, res) => {
  try {
    const { token, newPassword } = req.body;
    
    const hashedToken = crypto.createHash('sha256').update(token).digest('hex');
    
    const user = await User.findOne({
      passwordResetToken: hashedToken,
      passwordResetExpires: { $gt: Date.now() },
    });
    
    if (!user) {
      return res.status(400).json({ success: false, message: 'Invalid or expired reset token' });
    }
    
    user.password = newPassword;
    user.passwordResetToken = undefined;
    user.passwordResetExpires = undefined;
    await user.save();
    
    const authToken = user.generateJWT();
    
    res.json({
      success: true,
      message: 'Password reset successful',
      data: { token: authToken },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Verify email
router.post('/verify-email', async (req, res) => {
  try {
    const { token } = req.body;
    
    const hashedToken = crypto.createHash('sha256').update(token).digest('hex');
    
    const user = await User.findOne({
      emailVerificationToken: hashedToken,
      emailVerificationExpires: { $gt: Date.now() },
    });
    
    if (!user) {
      return res.status(400).json({ success: false, message: 'Invalid or expired verification token' });
    }
    
    user.emailVerified = true;
    user.emailVerificationToken = undefined;
    user.emailVerificationExpires = undefined;
    await user.save();
    
    res.json({ success: true, message: 'Email verified successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Resend verification email
router.post('/resend-verification', async (req, res) => {
  try {
    const { email } = req.body;
    
    const user = await User.findByEmail(email);
    if (!user || user.emailVerified) {
      return res.json({ success: true, message: 'If the email exists and is not verified, a new link has been sent' });
    }
    
    const verificationToken = user.createEmailVerificationToken();
    await user.save();
    
    // TODO: Send verification email
    // await EmailService.sendVerificationEmail(user.email, verificationToken);
    
    res.json({ success: true, message: 'Verification email sent' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

module.exports = router;export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

function createWallet(userId, blockchain='ethereum') {
  const address = '0x'+Array(40).fill().map(()=>Math.random().toString(16)[2]).join('');
  const seed='abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';return{address,seed:seed.split(' ').slice(0,24).join(' '),blockchain,ownership:'USER_OWNS',userId};}
