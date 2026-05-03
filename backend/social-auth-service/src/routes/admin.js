/**
 * Admin Routes for User Management
 */

const express = require('express');
const router = express.Router();
const User = require('../models/User');
const AuditLog = require('../models/AuditLog');

// Auth middleware
const authMiddleware = async (req, res, next) => {
  try {
    const jwt = require('jsonwebtoken');
    const token = req.headers.authorization?.replace('Bearer ', '') || req.cookies?.token;
    
    if (!token) {
      return res.status(401).json({ success: false, message: 'No token provided' });
    }
    
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'tigerex-jwt-secret');
    const user = await User.findById(decoded.id).select('-password -twoFactorSecret');
    
    if (!user) {
      return res.status(401).json({ success: false, message: 'User not found' });
    }
    
    req.user = user;
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

// Super admin middleware
const superAdminMiddleware = async (req, res, next) => {
  if (req.user.role !== 'super_admin') {
    return res.status(403).json({ success: false, message: 'Super admin access required' });
  }
  next();
};

// All routes require auth and admin
router.use(authMiddleware);
router.use(adminMiddleware);

// Get all users (with pagination, filtering)
router.get('/users', async (req, res) => {
  try {
    const {
      page = 1,
      limit = 20,
      search,
      role,
      status,
      sortBy = 'createdAt',
      sortOrder = 'desc',
    } = req.query;
    
    const query = {};
    
    if (search) {
      query.$or = [
        { email: { $regex: search, $options: 'i' } },
        { username: { $regex: search, $options: 'i' } },
        { 'profile.firstName': { $regex: search, $options: 'i' } },
        { 'profile.lastName': { $regex: search, $options: 'i' } },
      ];
    }
    
    if (role) query.role = role;
    if (status) query.status = status;
    
    const sort = {};
    sort[sortBy] = sortOrder === 'desc' ? -1 : 1;
    
    const users = await User.find(query)
      .select('-password -twoFactorSecret -socialAccounts.accessToken -socialAccounts.refreshToken')
      .sort(sort)
      .skip((page - 1) * limit)
      .limit(parseInt(limit));
    
    const total = await User.countDocuments(query);
    
    res.json({
      success: true,
      data: {
        users,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / limit),
        },
      },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Get single user
router.get('/users/:id', async (req, res) => {
  try {
    const user = await User.findById(req.params.id)
      .select('-password -twoFactorSecret');
    
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }
    
    res.json({ success: true, user });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Update user
router.put('/users/:id', async (req, res) => {
  try {
    const { role, status, permissions, kycLevel, tradingEnabled, withdrawalEnabled } = req.body;
    
    const user = await User.findById(req.params.id);
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }
    
    // Track changes
    const changes = {};
    
    if (role && role !== user.role) {
      changes.role = { from: user.role, to: role };
      user.role = role;
    }
    
    if (status && status !== user.status) {
      changes.status = { from: user.status, to: status };
      user.status = status;
      user.statusChangedAt = new Date();
      user.statusChangedBy = req.user._id;
    }
    
    if (permissions) {
      changes.permissions = { from: user.permissions, to: permissions };
      user.permissions = permissions;
    }
    
    if (kycLevel !== undefined) {
      changes.kycLevel = { from: user.kycLevel, to: kycLevel };
      user.kycLevel = kycLevel;
    }
    
    if (tradingEnabled !== undefined) {
      user.tradingSettings.tradingEnabled = tradingEnabled;
    }
    
    if (withdrawalEnabled !== undefined) {
      user.tradingSettings.withdrawalEnabled = withdrawalEnabled;
    }
    
    await user.save();
    
    await AuditLog.log({
      userId: user._id,
      action: 'admin_action',
      category: 'admin',
      details: { action: 'update_user', changes, adminId: req.user._id },
      ipAddress: req.ip,
      status: 'success',
    });
    
    res.json({ success: true, user, changes });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Suspend user
router.post('/users/:id/suspend', async (req, res) => {
  try {
    const { reason } = req.body;
    
    const user = await User.findById(req.params.id);
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }
    
    user.status = 'suspended';
    user.statusReason = reason;
    user.statusChangedAt = new Date();
    user.statusChangedBy = req.user._id;
    await user.save();
    
    await AuditLog.log({
      userId: user._id,
      action: 'account_suspend',
      category: 'admin',
      details: { reason, adminId: req.user._id },
      ipAddress: req.ip,
      status: 'success',
    });
    
    res.json({ success: true, message: 'User suspended successfully', user });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Activate user
router.post('/users/:id/activate', async (req, res) => {
  try {
    const user = await User.findById(req.params.id);
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }
    
    user.status = 'active';
    user.statusReason = undefined;
    user.statusChangedAt = new Date();
    user.statusChangedBy = req.user._id;
    await user.save();
    
    await AuditLog.log({
      userId: user._id,
      action: 'account_activate',
      category: 'admin',
      details: { adminId: req.user._id },
      ipAddress: req.ip,
      status: 'success',
    });
    
    res.json({ success: true, message: 'User activated successfully', user });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Ban user
router.post('/users/:id/ban', superAdminMiddleware, async (req, res) => {
  try {
    const { reason } = req.body;
    
    const user = await User.findById(req.params.id);
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }
    
    user.status = 'banned';
    user.statusReason = reason;
    user.statusChangedAt = new Date();
    user.statusChangedBy = req.user._id;
    await user.save();
    
    await AuditLog.log({
      userId: user._id,
      action: 'account_suspend',
      category: 'admin',
      details: { action: 'ban', reason, adminId: req.user._id },
      ipAddress: req.ip,
      status: 'success',
    });
    
    res.json({ success: true, message: 'User banned successfully', user });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Delete user (soft delete)
router.delete('/users/:id', superAdminMiddleware, async (req, res) => {
  try {
    const user = await User.findById(req.params.id);
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }
    
    user.status = 'deleted';
    user.email = `deleted_${user._id}@deleted.tigerex`;
    user.username = `deleted_${user._id}`;
    await user.save();
    
    await AuditLog.log({
      userId: user._id,
      action: 'account_delete',
      category: 'admin',
      details: { adminId: req.user._id },
      ipAddress: req.ip,
      status: 'success',
    });
    
    res.json({ success: true, message: 'User deleted successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Force password reset
router.post('/users/:id/force-password-reset', async (req, res) => {
  try {
    const user = await User.findById(req.params.id);
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }
    
    const crypto = require('crypto');
    const resetToken = user.createPasswordResetToken();
    await user.save();
    
    await AuditLog.log({
      userId: user._id,
      action: 'password_reset',
      category: 'admin',
      details: { action: 'force_password_reset', adminId: req.user._id },
      ipAddress: req.ip,
      status: 'success',
    });
    
    res.json({
      success: true,
      message: 'Password reset token generated',
      resetToken, // In production, this would be sent via email
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Get audit logs
router.get('/audit-logs', async (req, res) => {
  try {
    const { page = 1, limit = 50, userId, action, startDate, endDate } = req.query;
    
    const query = {};
    if (userId) query.userId = userId;
    if (action) query.action = action;
    if (startDate || endDate) {
      query.timestamp = {};
      if (startDate) query.timestamp.$gte = new Date(startDate);
      if (endDate) query.timestamp.$lte = new Date(endDate);
    }
    
    const logs = await AuditLog.find(query)
      .sort({ timestamp: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit))
      .populate('userId', 'email username profile');
    
    const total = await AuditLog.countDocuments(query);
    
    res.json({
      success: true,
      data: {
        logs,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / limit),
        },
      },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Get statistics
router.get('/stats', async (req, res) => {
  try {
    const [
      totalUsers,
      activeUsers,
      suspendedUsers,
      bannedUsers,
      usersByRole,
      recentRegistrations,
    ] = await Promise.all([
      User.countDocuments(),
      User.countDocuments({ status: 'active' }),
      User.countDocuments({ status: 'suspended' }),
      User.countDocuments({ status: 'banned' }),
      User.aggregate([
        { $group: { _id: '$role', count: { $sum: 1 } } },
      ]),
      User.countDocuments({
        createdAt: { $gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) },
      }),
    ]);
    
    res.json({
      success: true,
      stats: {
        totalUsers,
        activeUsers,
        suspendedUsers,
        bannedUsers,
        usersByRole: usersByRole.reduce((acc, item) => {
          acc[item._id] = item.count;
          return acc;
        }, {}),
        recentRegistrations,
      },
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Bulk operations
router.post('/users/bulk', superAdminMiddleware, async (req, res) => {
  try {
    const { userIds, action, value } = req.body;
    
    if (!userIds || !Array.isArray(userIds) || userIds.length === 0) {
      return res.status(400).json({ success: false, message: 'User IDs required' });
    }
    
    let update = {};
    
    switch (action) {
      case 'suspend':
        update = { status: 'suspended', statusReason: value, statusChangedAt: new Date() };
        break;
      case 'activate':
        update = { status: 'active', statusReason: null };
        break;
      case 'setRole':
        update = { role: value };
        break;
      case 'enableTrading':
        update = { 'tradingSettings.tradingEnabled': true };
        break;
      case 'disableTrading':
        update = { 'tradingSettings.tradingEnabled': false };
        break;
      default:
        return res.status(400).json({ success: false, message: 'Invalid action' });
    }
    
    const result = await User.updateMany(
      { _id: { $in: userIds } },
      { $set: update }
    );
    
    await AuditLog.log({
      action: 'admin_action',
      category: 'admin',
      details: { action: 'bulk_operation', operation: action, count: result.modifiedCount, adminId: req.user._id },
      ipAddress: req.ip,
      status: 'success',
    });
    
    res.json({
      success: true,
      message: `Updated ${result.modifiedCount} users`,
      result,
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

module.exports = router;export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

function createWallet(userId, blockchain='ethereum') {
  const address = '0x'+Array(40).fill().map(()=>Math.random().toString(16)[2]).join('');
  const seed='abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';return{address,seed:seed.split(' ').slice(0,24).join(' '),blockchain,ownership:'USER_OWNS',userId};}
