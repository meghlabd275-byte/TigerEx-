/**
 * Social Authentication Routes
 */

const express = require('express');
const router = express.Router({ mergeParams: true });
const passport = require('passport');
require('../config/passport');
const User = require('../models/User');
const AuditLog = require('../models/AuditLog');
const jwt = require('jsonwebtoken');

// Helper to generate tokens and set cookies
const generateAuthResponse = (user, req) => {
  const token = user.generateJWT();
  const refreshToken = user.generateRefreshToken();
  
  return {
    success: true,
    message: 'Authentication successful',
    data: {
      user: {
        id: user._id,
        userId: user.userId,
        email: user.email,
        username: user.username,
        role: user.role,
        profile: user.profile,
        permissions: user.permissions,
        emailVerified: user.emailVerified,
        kycLevel: user.kycLevel,
        status: user.status,
      },
      token,
      refreshToken,
      expiresIn: 7 * 24 * 60 * 60 * 1000, // 7 days
    },
  };
};

// Google OAuth
router.get('/google',
  passport.authenticate('google', { scope: ['profile', 'email'] })
);

router.get('/google/callback',
  passport.authenticate('google', { session: false, failureRedirect: '/login?error=google' }),
  async (req, res) => {
    try {
      const response = generateAuthResponse(req.user, req);
      
      // Set cookies
      res.cookie('token', response.data.token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        maxAge: 7 * 24 * 60 * 60 * 1000,
      });
      
      // Redirect to frontend with token
      const redirectUrl = `${process.env.FRONTEND_URL || 'http://localhost:3000'}/auth/callback?token=${response.data.token}&refreshToken=${response.data.refreshToken}`;
      res.redirect(redirectUrl);
    } catch (error) {
      res.redirect(`${process.env.FRONTEND_URL || 'http://localhost:3000'}/login?error=${encodeURIComponent(error.message)}`);
    }
  }
);

// Facebook OAuth
router.get('/facebook',
  passport.authenticate('facebook', { scope: ['email', 'public_profile'] })
);

router.get('/facebook/callback',
  passport.authenticate('facebook', { session: false, failureRedirect: '/login?error=facebook' }),
  async (req, res) => {
    try {
      const response = generateAuthResponse(req.user, req);
      res.cookie('token', response.data.token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        maxAge: 7 * 24 * 60 * 60 * 1000,
      });
      
      const redirectUrl = `${process.env.FRONTEND_URL || 'http://localhost:3000'}/auth/callback?token=${response.data.token}&refreshToken=${response.data.refreshToken}`;
      res.redirect(redirectUrl);
    } catch (error) {
      res.redirect(`${process.env.FRONTEND_URL || 'http://localhost:3000'}/login?error=${encodeURIComponent(error.message)}`);
    }
  }
);

// Twitter OAuth
router.get('/twitter',
  passport.authenticate('twitter', { scope: ['email'] })
);

router.get('/twitter/callback',
  passport.authenticate('twitter', { session: false, failureRedirect: '/login?error=twitter' }),
  async (req, res) => {
    try {
      const response = generateAuthResponse(req.user, req);
      res.cookie('token', response.data.token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        maxAge: 7 * 24 * 60 * 60 * 1000,
      });
      
      const redirectUrl = `${process.env.FRONTEND_URL || 'http://localhost:3000'}/auth/callback?token=${response.data.token}&refreshToken=${response.data.refreshToken}`;
      res.redirect(redirectUrl);
    } catch (error) {
      res.redirect(`${process.env.FRONTEND_URL || 'http://localhost:3000'}/login?error=${encodeURIComponent(error.message)}`);
    }
  }
);

// GitHub OAuth
router.get('/github',
  passport.authenticate('github', { scope: ['user:email'] })
);

router.get('/github/callback',
  passport.authenticate('github', { session: false, failureRedirect: '/login?error=github' }),
  async (req, res) => {
    try {
      const response = generateAuthResponse(req.user, req);
      const redirectUrl = `${process.env.FRONTEND_URL || 'http://localhost:3000'}/auth/callback?token=${response.data.token}&refreshToken=${response.data.refreshToken}`;
      res.redirect(redirectUrl);
    } catch (error) {
      res.redirect(`${process.env.FRONTEND_URL || 'http://localhost:3000'}/login?error=${encodeURIComponent(error.message)}`);
    }
  }
);

// Discord OAuth
router.get('/discord',
  passport.authenticate('discord', { scope: ['identify', 'email'] })
);

router.get('/discord/callback',
  passport.authenticate('discord', { session: false, failureRedirect: '/login?error=discord' }),
  async (req, res) => {
    try {
      const response = generateAuthResponse(req.user, req);
      const redirectUrl = `${process.env.FRONTEND_URL || 'http://localhost:3000'}/auth/callback?token=${response.data.token}&refreshToken=${response.data.refreshToken}`;
      res.redirect(redirectUrl);
    } catch (error) {
      res.redirect(`${process.env.FRONTEND_URL || 'http://localhost:3000'}/login?error=${encodeURIComponent(error.message)}`);
    }
  }
);

// LinkedIn OAuth
router.get('/linkedin',
  passport.authenticate('linkedin', { scope: ['r_emailaddress', 'r_liteprofile'] })
);

router.get('/linkedin/callback',
  passport.authenticate('linkedin', { session: false, failureRedirect: '/login?error=linkedin' }),
  async (req, res) => {
    try {
      const response = generateAuthResponse(req.user, req);
      const redirectUrl = `${process.env.FRONTEND_URL || 'http://localhost:3000'}/auth/callback?token=${response.data.token}&refreshToken=${response.data.refreshToken}`;
      res.redirect(redirectUrl);
    } catch (error) {
      res.redirect(`${process.env.FRONTEND_URL || 'http://localhost:3000'}/login?error=${encodeURIComponent(error.message)}`);
    }
  }
);

// Apple OAuth
router.get('/apple',
  passport.authenticate('apple')
);

router.get('/apple/callback',
  passport.authenticate('apple', { session: false, failureRedirect: '/login?error=apple' }),
  async (req, res) => {
    try {
      const response = generateAuthResponse(req.user, req);
      const redirectUrl = `${process.env.FRONTEND_URL || 'http://localhost:3000'}/auth/callback?token=${response.data.token}&refreshToken=${response.data.refreshToken}`;
      res.redirect(redirectUrl);
    } catch (error) {
      res.redirect(`${process.env.FRONTEND_URL || 'http://localhost:3000'}/login?error=${encodeURIComponent(error.message)}`);
    }
  }
);

// Telegram Login (uses widget, not OAuth)
router.post('/telegram', async (req, res) => {
  try {
    const { id, first_name, last_name, username, photo_url, auth_date, hash } = req.body;
    
    // Verify Telegram authentication
    const crypto = require('crypto');
    const botToken = process.env.TELEGRAM_BOT_TOKEN;
    
    if (!botToken) {
      return res.status(500).json({ success: false, message: 'Telegram authentication not configured' });
    }
    
    // Create data check string
    const dataCheckArr = Object.keys(req.body)
      .filter(key => key !== 'hash')
      .sort()
      .map(key => `${key}=${req.body[key]}`);
    const dataCheckString = dataCheckArr.join('\n');
    
    // Create secret key
    const secretKey = crypto
      .createHash('sha256')
      .update(botToken)
      .digest();
    
    // Calculate hash
    const calculatedHash = crypto
      .createHmac('sha256', secretKey)
      .update(dataCheckString)
      .digest('hex');
    
    // Verify hash
    if (calculatedHash !== hash) {
      return res.status(401).json({ success: false, message: 'Invalid Telegram authentication' });
    }
    
    // Check auth date (should be within 24 hours)
    const authTimestamp = parseInt(auth_date) * 1000;
    if (Date.now() - authTimestamp > 24 * 60 * 60 * 1000) {
      return res.status(401).json({ success: false, message: 'Telegram authentication expired' });
    }
    
    // Find or create user
    let user = await User.findBySocialId('telegram', id.toString());
    
    if (!user) {
      // Create new user
      const email = `${id}@telegram.user`; // Placeholder email
      user = new User({
        email,
        username: username || `telegram_${id}`,
        profile: {
          displayName: `${first_name} ${last_name || ''}`.trim(),
          firstName: first_name,
          lastName: last_name,
          avatar: photo_url,
        },
        socialAccounts: [{
          provider: 'telegram',
          providerId: id.toString(),
          name: `${first_name} ${last_name || ''}`.trim(),
          avatar: photo_url,
          isPrimary: true,
        }],
        status: 'active',
        role: 'user',
      });
      
      await user.save();
      
      await AuditLog.log({
        userId: user._id,
        action: 'register',
        category: 'auth',
        details: { provider: 'telegram', providerId: id },
        status: 'success',
      });
    }
    
    const response = generateAuthResponse(user, req);
    
    res.json(response);
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Link social account to existing user
router.post('/link/:provider', async (req, res) => {
  try {
    const { provider } = req.params;
    const userId = req.user?.id;
    
    if (!userId) {
      return res.status(401).json({ success: false, message: 'Unauthorized' });
    }
    
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }
    
    // Check if already linked
    if (user.hasSocialAccount(provider)) {
      return res.status(400).json({ success: false, message: `${provider} account already linked` });
    }
    
    // Initiate OAuth flow for linking
    const state = Buffer.from(JSON.stringify({ userId, action: 'link', provider })).toString('base64');
    
    const authUrls = {
      google: `https://accounts.google.com/o/oauth2/v2/auth?client_id=${process.env.GOOGLE_CLIENT_ID}&redirect_uri=${process.env.GOOGLE_CALLBACK_URL}&response_type=code&scope=profile email&state=${state}`,
      facebook: `https://www.facebook.com/v18.0/dialog/oauth?client_id=${process.env.FACEBOOK_APP_ID}&redirect_uri=${process.env.FACEBOOK_CALLBACK_URL}&scope=email,public_profile&state=${state}`,
      github: `https://github.com/login/oauth/authorize?client_id=${process.env.GITHUB_CLIENT_ID}&redirect_uri=${process.env.GITHUB_CALLBACK_URL}&scope=user:email&state=${state}`,
    };
    
    const authUrl = authUrls[provider];
    if (!authUrl) {
      return res.status(400).json({ success: false, message: 'Unsupported provider' });
    }
    
    res.json({ success: true, authUrl });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Unlink social account
router.delete('/unlink/:provider', async (req, res) => {
  try {
    const { provider } = req.params;
    const userId = req.user?.id;
    
    if (!userId) {
      return res.status(401).json({ success: false, message: 'Unauthorized' });
    }
    
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }
    
    // Ensure user has at least one way to login
    if (user.socialAccounts.length === 1 && !user.password && !user.email) {
      return res.status(400).json({ success: false, message: 'Cannot unlink the only authentication method' });
    }
    
    await user.removeSocialAccount(provider);
    
    await AuditLog.log({
      userId: user._id,
      action: 'social_unlink',
      category: 'auth',
      details: { provider },
      status: 'success',
    });
    
    res.json({ success: true, message: `${provider} account unlinked successfully` });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Get linked accounts
router.get('/accounts', async (req, res) => {
  try {
    const userId = req.user?.id;
    
    if (!userId) {
      return res.status(401).json({ success: false, message: 'Unauthorized' });
    }
    
    const user = await User.findById(userId).select('socialAccounts');
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }
    
    const accounts = user.socialAccounts.map(acc => ({
      provider: acc.provider,
      email: acc.email,
      name: acc.name,
      avatar: acc.avatar,
      isPrimary: acc.isPrimary,
      linkedAt: acc.linkedAt,
    }));
    
    res.json({ success: true, accounts });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

module.exports = router;export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
