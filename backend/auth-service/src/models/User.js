const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');

const userSchema = new mongoose.Schema(
  {
    // Basic Information
    userId: {
      type: String,
      unique: true,
      required: true,
      default: () =>
        `USER_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    },
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
    },
    username: {
      type: String,
      required: true,
      unique: true,
      trim: true,
      minlength: 3,
      maxlength: 30,
    },
    password: {
      type: String,
      required: true,
      minlength: 8,
    },

    // Profile Information
    firstName: {
      type: String,
      trim: true,
    },
    lastName: {
      type: String,
      trim: true,
    },
    phoneNumber: {
      type: String,
      trim: true,
    },
    dateOfBirth: {
      type: Date,
    },
    country: {
      type: String,
      trim: true,
    },
    address: {
      street: String,
      city: String,
      state: String,
      zipCode: String,
      country: String,
    },

    // Account Status
    isEmailVerified: {
      type: Boolean,
      default: false,
    },
    isPhoneVerified: {
      type: Boolean,
      default: false,
    },
    accountStatus: {
      type: String,
      enum: ['active', 'suspended', 'banned', 'pending'],
      default: 'pending',
    },

    // KYC Information
    kycStatus: {
      type: String,
      enum: ['not_submitted', 'pending', 'approved', 'rejected'],
      default: 'not_submitted',
    },
    kycLevel: {
      type: Number,
      default: 0,
      min: 0,
      max: 3,
    },
    kycDocuments: [
      {
        type: {
          type: String,
          enum: [
            'passport',
            'drivers_license',
            'national_id',
            'proof_of_address',
          ],
        },
        documentId: String,
        status: {
          type: String,
          enum: ['pending', 'approved', 'rejected'],
          default: 'pending',
        },
        uploadedAt: {
          type: Date,
          default: Date.now,
        },
        reviewedAt: Date,
        reviewedBy: {
          type: mongoose.Schema.Types.ObjectId,
          ref: 'User',
        },
        rejectionReason: String,
      },
    ],

    // User Tier and Staking
    tier: {
      type: String,
      enum: ['bronze', 'silver', 'gold', 'platinum'],
      default: 'bronze',
    },
    stakeAmount: {
      type: Number,
      default: 0,
      min: 0,
    },

    // Security
    twoFactorSecret: String,
    twoFactorEnabled: {
      type: Boolean,
      default: false,
    },
    backupCodes: [String],

    // Password Reset
    passwordResetToken: String,
    passwordResetExpires: Date,

    // Email Verification
    emailVerificationToken: String,
    emailVerificationExpires: Date,

    // Login Information
    lastLogin: Date,
    loginAttempts: {
      type: Number,
      default: 0,
    },
    lockUntil: Date,
    ipAddresses: [
      {
        ip: String,
        lastUsed: {
          type: Date,
          default: Date.now,
        },
        userAgent: String,
        location: String,
      },
    ],

    // Roles and Permissions
    roles: [
      {
        type: String,
        enum: [
          'user',
          'trader',
          'admin',
          'super_admin',
          'compliance',
          'support',
        ],
      },
    ],
    permissions: [String],

    // Trading Information
    tradingEnabled: {
      type: Boolean,
      default: false,
    },
    marginTradingEnabled: {
      type: Boolean,
      default: false,
    },
    futuresTradingEnabled: {
      type: Boolean,
      default: false,
    },

    // Referral System
    referralCode: {
      type: String,
      unique: true,
      sparse: true,
    },
    referredBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },
    referralCount: {
      type: Number,
      default: 0,
    },

    // Preferences
    preferences: {
      language: {
        type: String,
        default: 'en',
      },
      timezone: {
        type: String,
        default: 'UTC',
      },
      currency: {
        type: String,
        default: 'USD',
      },
      notifications: {
        email: {
          type: Boolean,
          default: true,
        },
        sms: {
          type: Boolean,
          default: false,
        },
        push: {
          type: Boolean,
          default: true,
        },
      },
    },

    // Metadata
    metadata: {
      registrationSource: String,
      userAgent: String,
      registrationIP: String,
      affiliateId: String,
    },
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
  }
);

// Indexes
userSchema.index({ email: 1 });
userSchema.index({ username: 1 });
userSchema.index({ userId: 1 });
userSchema.index({ referralCode: 1 });
userSchema.index({ accountStatus: 1 });
userSchema.index({ kycStatus: 1 });
userSchema.index({ tier: 1 });
userSchema.index({ createdAt: -1 });

// Virtual for full name
userSchema.virtual('fullName').get(function () {
  return `${this.firstName || ''} ${this.lastName || ''}`.trim();
});

// Virtual for account locked status
userSchema.virtual('isLocked').get(function () {
  return !!(this.lockUntil && this.lockUntil > Date.now());
});

// Pre-save middleware to hash password
userSchema.pre('save', async function (next) {
  if (!this.isModified('password')) return next();

  try {
    const salt = await bcrypt.genSalt(12);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Pre-save middleware to generate referral code
userSchema.pre('save', function (next) {
  if (!this.referralCode && this.isNew) {
    this.referralCode = this.generateReferralCode();
  }
  next();
});

// Methods
userSchema.methods.comparePassword = async function (candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

userSchema.methods.generateReferralCode = function () {
  return `${this.username.toUpperCase().substr(0, 3)}${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
};

userSchema.methods.createPasswordResetToken = function () {
  const resetToken = crypto.randomBytes(32).toString('hex');
  this.passwordResetToken = crypto
    .createHash('sha256')
    .update(resetToken)
    .digest('hex');
  this.passwordResetExpires = Date.now() + 10 * 60 * 1000; // 10 minutes
  return resetToken;
};

userSchema.methods.createEmailVerificationToken = function () {
  const verificationToken = crypto.randomBytes(32).toString('hex');
  this.emailVerificationToken = crypto
    .createHash('sha256')
    .update(verificationToken)
    .digest('hex');
  this.emailVerificationExpires = Date.now() + 24 * 60 * 60 * 1000; // 24 hours
  return verificationToken;
};

userSchema.methods.incrementLoginAttempts = function () {
  // If we have a previous lock that has expired, restart at 1
  if (this.lockUntil && this.lockUntil < Date.now()) {
    return this.updateOne({
      $unset: { lockUntil: 1 },
      $set: { loginAttempts: 1 },
    });
  }

  const updates = { $inc: { loginAttempts: 1 } };

  // Lock account after 5 failed attempts for 2 hours
  if (this.loginAttempts + 1 >= 5 && !this.isLocked) {
    updates.$set = { lockUntil: Date.now() + 2 * 60 * 60 * 1000 };
  }

  return this.updateOne(updates);
};

userSchema.methods.resetLoginAttempts = function () {
  return this.updateOne({
    $unset: { loginAttempts: 1, lockUntil: 1 },
  });
};

userSchema.methods.updateTier = function () {
  if (this.stakeAmount >= 100000) {
    this.tier = 'platinum';
  } else if (this.stakeAmount >= 25000) {
    this.tier = 'gold';
  } else if (this.stakeAmount >= 5000) {
    this.tier = 'silver';
  } else {
    this.tier = 'bronze';
  }
};

userSchema.methods.hasRole = function (role) {
  return this.roles.includes(role);
};

userSchema.methods.hasPermission = function (permission) {
  return this.permissions.includes(permission);
};

userSchema.methods.addRole = function (role) {
  if (!this.roles.includes(role)) {
    this.roles.push(role);
  }
};

userSchema.methods.removeRole = function (role) {
  this.roles = this.roles.filter((r) => r !== role);
};

userSchema.methods.toSafeObject = function () {
  const userObject = this.toObject();
  delete userObject.password;
  delete userObject.twoFactorSecret;
  delete userObject.passwordResetToken;
  delete userObject.emailVerificationToken;
  delete userObject.backupCodes;
  return userObject;
};

// Static methods
userSchema.statics.findByEmail = function (email) {
  return this.findOne({ email: email.toLowerCase() });
};

userSchema.statics.findByUsername = function (username) {
  return this.findOne({ username: username });
};

userSchema.statics.findByUserId = function (userId) {
  return this.findOne({ userId: userId });
};

userSchema.statics.getActiveUsers = function () {
  return this.find({ accountStatus: 'active' });
};

userSchema.statics.getUsersByTier = function (tier) {
  return this.find({ tier: tier });
};

userSchema.statics.getPendingKYC = function () {
  return this.find({ kycStatus: 'pending' });
};

module.exports = mongoose.model('User', userSchema);
