/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

const User = require('../models/User');
const crypto = require('crypto');

class AuthService {
  static async initialize() {
    console.log('AuthService initialized');
  }

  // User creation and management
  static async createUser(userData) {
    try {
      const user = new User(userData);
      await user.save();
      return user;
    } catch (error) {
      throw new Error(`Failed to create user: ${error.message}`);
    }
  }

  static async findUserByEmail(email) {
    try {
      return await User.findOne({ email: email.toLowerCase() });
    } catch (error) {
      throw new Error(`Failed to find user by email: ${error.message}`);
    }
  }

  static async findUserByUsername(username) {
    try {
      return await User.findOne({ username: username });
    } catch (error) {
      throw new Error(`Failed to find user by username: ${error.message}`);
    }
  }

  static async findUserByUserId(userId) {
    try {
      return await User.findOne({ userId: userId });
    } catch (error) {
      throw new Error(`Failed to find user by userId: ${error.message}`);
    }
  }

  static async findUserByEmailOrUsername(email, username) {
    try {
      return await User.findOne({
        $or: [{ email: email.toLowerCase() }, { username: username }],
      });
    } catch (error) {
      throw new Error(`Failed to find user: ${error.message}`);
    }
  }

  static async findUserByReferralCode(referralCode) {
    try {
      return await User.findOne({ referralCode: referralCode });
    } catch (error) {
      throw new Error(`Failed to find user by referral code: ${error.message}`);
    }
  }

  // Email verification
  static async verifyEmailToken(token) {
    try {
      const hashedToken = crypto
        .createHash('sha256')
        .update(token)
        .digest('hex');

      const user = await User.findOne({
        emailVerificationToken: hashedToken,
        emailVerificationExpires: { $gt: Date.now() },
      });

      return user;
    } catch (error) {
      throw new Error(`Failed to verify email token: ${error.message}`);
    }
  }

  // Password reset
  static async verifyPasswordResetToken(token) {
    try {
      const hashedToken = crypto
        .createHash('sha256')
        .update(token)
        .digest('hex');

      const user = await User.findOne({
        passwordResetToken: hashedToken,
        passwordResetExpires: { $gt: Date.now() },
      });

      return user;
    } catch (error) {
      throw new Error(
        `Failed to verify password reset token: ${error.message}`
      );
    }
  }

  // User statistics and analytics
  static async getUserStats() {
    try {
      const totalUsers = await User.countDocuments();
      const activeUsers = await User.countDocuments({
        accountStatus: 'active',
      });
      const pendingKyc = await User.countDocuments({ kycStatus: 'pending' });
      const suspendedUsers = await User.countDocuments({
        accountStatus: 'suspended',
      });

      const tierDistribution = await User.aggregate([
        {
          $group: {
            _id: '$tier',
            count: { $sum: 1 },
          },
        },
      ]);

      const kycDistribution = await User.aggregate([
        {
          $group: {
            _id: '$kycStatus',
            count: { $sum: 1 },
          },
        },
      ]);

      const totalStaked = await User.aggregate([
        {
          $group: {
            _id: null,
            total: { $sum: '$stakeAmount' },
          },
        },
      ]);

      return {
        totalUsers,
        activeUsers,
        pendingKyc,
        suspendedUsers,
        tierDistribution,
        kycDistribution,
        totalStaked: totalStaked[0]?.total || 0,
      };
    } catch (error) {
      throw new Error(`Failed to get user stats: ${error.message}`);
    }
  }

  // User management operations
  static async updateUserStatus(userId, status) {
    try {
      const user = await User.findOneAndUpdate(
        { userId: userId },
        { accountStatus: status },
        { new: true }
      );

      if (!user) {
        throw new Error('User not found');
      }

      return user;
    } catch (error) {
      throw new Error(`Failed to update user status: ${error.message}`);
    }
  }

  static async updateUserKycStatus(userId, status, reason = null) {
    try {
      const updateData = { kycStatus: status };

      if (status === 'rejected' && reason) {
        updateData.kycRejectionReason = reason;
      }

      const user = await User.findOneAndUpdate({ userId: userId }, updateData, {
        new: true,
      });

      if (!user) {
        throw new Error('User not found');
      }

      return user;
    } catch (error) {
      throw new Error(`Failed to update KYC status: ${error.message}`);
    }
  }

  static async updateUserTier(userId, stakeAmount) {
    try {
      const user = await User.findOne({ userId: userId });
      if (!user) {
        throw new Error('User not found');
      }

      user.stakeAmount = stakeAmount;
      user.updateTier();
      await user.save();

      return user;
    } catch (error) {
      throw new Error(`Failed to update user tier: ${error.message}`);
    }
  }

  // Bulk operations
  static async getUsers(filters = {}, pagination = {}) {
    try {
      const {
        page = 1,
        limit = 50,
        sortBy = 'createdAt',
        sortOrder = 'desc',
      } = pagination;
      const skip = (page - 1) * limit;

      const query = {};

      if (filters.accountStatus) {
        query.accountStatus = filters.accountStatus;
      }

      if (filters.kycStatus) {
        query.kycStatus = filters.kycStatus;
      }

      if (filters.tier) {
        query.tier = filters.tier;
      }

      if (filters.search) {
        query.$or = [
          { email: { $regex: filters.search, $options: 'i' } },
          { username: { $regex: filters.search, $options: 'i' } },
          { firstName: { $regex: filters.search, $options: 'i' } },
          { lastName: { $regex: filters.search, $options: 'i' } },
        ];
      }

      const users = await User.find(query)
        .sort({ [sortBy]: sortOrder === 'desc' ? -1 : 1 })
        .skip(skip)
        .limit(limit)
        .select(
          '-password -twoFactorSecret -passwordResetToken -emailVerificationToken'
        );

      const total = await User.countDocuments(query);

      return {
        users,
        pagination: {
          page,
          limit,
          total,
          pages: Math.ceil(total / limit),
        },
      };
    } catch (error) {
      throw new Error(`Failed to get users: ${error.message}`);
    }
  }

  static async exportUsers(filters = {}) {
    try {
      const query = {};

      if (filters.accountStatus) {
        query.accountStatus = filters.accountStatus;
      }

      if (filters.kycStatus) {
        query.kycStatus = filters.kycStatus;
      }

      if (filters.tier) {
        query.tier = filters.tier;
      }

      const users = await User.find(query)
        .select(
          'userId email username firstName lastName tier kycStatus accountStatus stakeAmount createdAt lastLogin'
        )
        .sort({ createdAt: -1 });

      return users;
    } catch (error) {
      throw new Error(`Failed to export users: ${error.message}`);
    }
  }

  // Security operations
  static async logSecurityEvent(userId, event, details = {}) {
    try {
      // This would typically log to a security audit system
      console.log(`Security Event - User: ${userId}, Event: ${event}`, details);

      // You could implement a SecurityLog model here
      // await SecurityLog.create({
      //   userId,
      //   event,
      //   details,
      //   timestamp: new Date()
      // });
    } catch (error) {
      console.error('Failed to log security event:', error);
    }
  }

  static async detectSuspiciousActivity(userId, activityData) {
    try {
      // Implement suspicious activity detection logic
      const user = await User.findOne({ userId });
      if (!user) return false;

      // Check for multiple failed login attempts
      if (user.loginAttempts >= 3) {
        await this.logSecurityEvent(userId, 'MULTIPLE_FAILED_LOGINS', {
          attempts: user.loginAttempts,
        });
        return true;
      }

      // Check for login from new location
      const lastKnownIPs = user.ipAddresses.map((ip) => ip.ip);
      if (activityData.ip && !lastKnownIPs.includes(activityData.ip)) {
        await this.logSecurityEvent(userId, 'LOGIN_FROM_NEW_IP', {
          newIP: activityData.ip,
          knownIPs: lastKnownIPs,
        });
      }

      return false;
    } catch (error) {
      console.error('Failed to detect suspicious activity:', error);
      return false;
    }
  }
}

module.exports = AuthService;
