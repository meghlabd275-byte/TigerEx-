/**
 * User Model with Social Authentication Support
 */

const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');

const SocialAccountSchema = new mongoose.Schema({
  provider: {
    type: String,
    enum: ['google', 'facebook', 'twitter', 'telegram', 'apple', 'github', 'discord', 'linkedin', 'email'],
    required: true,
  },
  providerId: {
    type: String,
    required: true,
  },
  email: String,
  name: String,
  avatar: String,
  accessToken: String,
  refreshToken: String,
  tokenExpiresAt: Date,
  profileData: mongoose.Schema.Types.Mixed,
  linkedAt: {
    type: Date,
    default: Date.now,
  },
  lastUsed: {
    type: Date,
    default: Date.now,
  },
  isVerified: {
    type: Boolean,
    default: false,
  },
  isPrimary: {
    type: Boolean,
    default: false,
  },
});

SocialAccountSchema.index({ provider: 1, providerId: 1 }, { unique: true });

const UserSchema = new mongoose.Schema({
  // Primary identification
  userId: {
    type: String,
    unique: true,
    sparse: true,
  },
  email: {
    type: String,
    lowercase: true,
    trim: true,
    sparse: true,
  },
  username: {
    type: String,
    unique: true,
    sparse: true,
    trim: true,
    minlength: 3,
    maxlength: 30,
  },
  
  // Profile information
  profile: {
    firstName: {
      type: String,
      trim: true,
      maxlength: 50,
    },
    lastName: {
      type: String,
      trim: true,
      maxlength: 50,
    },
    displayName: String,
    avatar: String,
    bio: {
      type: String,
      maxlength: 500,
    },
    dateOfBirth: Date,
    nationality: String,
    timezone: {
      type: String,
      default: 'UTC',
    },
    language: {
      type: String,
      default: 'en',
    },
  },
  
  // Authentication
  password: {
    type: String,
    select: false,
  },
  socialAccounts: [SocialAccountSchema],
  
  // Email verification
  emailVerified: {
    type: Boolean,
    default: false,
  },
  emailVerificationToken: String,
  emailVerificationExpires: Date,
  
  // Phone verification
  phoneNumber: {
    type: String,
    sparse: true,
  },
  phoneVerified: {
    type: Boolean,
    default: false,
  },
  
  // Security
  twoFactorEnabled: {
    type: Boolean,
    default: false,
  },
  twoFactorSecret: {
    type: String,
    select: false,
  },
  twoFactorBackupCodes: [{
    code: String,
    used: {
      type: Boolean,
      default: false,
    },
  }],
  
  // Role and permissions
  role: {
    type: String,
    enum: ['user', 'moderator', 'admin', 'super_admin', 'business_head', 'technical_team', 'market_maker', 'liquidity_provider', 'white_label_client', 'prime_brokerage', 'listings_manager'],
    default: 'user',
  },
  permissions: [{
    type: String,
  }],
  roles: [{
    role: String,
    assignedAt: {
      type: Date,
      default: Date.now,
    },
    assignedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },
  }],
  
  // Account status
  status: {
    type: String,
    enum: ['active', 'suspended', 'banned', 'deleted', 'pending_verification'],
    default: 'pending_verification',
  },
  statusReason: String,
  statusChangedAt: Date,
  statusChangedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
  },
  
  // KYC
  kycLevel: {
    type: Number,
    default: 0,
    min: 0,
    max: 4,
  },
  kycStatus: {
    type: String,
    enum: ['not_started', 'pending', 'submitted', 'approved', 'rejected'],
    default: 'not_started',
  },
  kycDocuments: [{
    type: {
      type: String,
      enum: ['passport', 'id_card', 'drivers_license', 'proof_of_address', 'selfie'],
    },
    url: String,
    status: {
      type: String,
      enum: ['pending', 'approved', 'rejected'],
    },
    uploadedAt: Date,
    verifiedAt: Date,
  }],
  
  // Trading settings
  tradingSettings: {
    defaultLeverage: {
      type: Number,
      default: 1,
    },
    riskLevel: {
      type: String,
      enum: ['low', 'medium', 'high'],
      default: 'medium',
    },
    autoClosePositions: {
      type: Boolean,
      default: false,
    },
    tradingEnabled: {
      type: Boolean,
      default: true,
    },
    withdrawalEnabled: {
      type: Boolean,
      default: true,
    },
  },
  
  // Security settings
  securitySettings: {
    loginNotifications: {
      type: Boolean,
      default: true,
    },
    withdrawalNotifications: {
      type: Boolean,
      default: true,
    },
    antiPhishingCode: String,
    whitelistedIPs: [String],
    sessionTimeout: {
      type: Number,
      default: 30, // minutes
    },
  },
  
  // Referral system
  referral: {
    code: {
      type: String,
      unique: true,
      sparse: true,
    },
    referredBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
    },
    referrals: [{
      user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
      },
      earnedAt: Date,
      reward: Number,
    }],
    totalEarnings: {
      type: Number,
      default: 0,
    },
  },
  
  // Sessions
  activeSessions: [{
    token: String,
    device: String,
    browser: String,
    os: String,
    ip: String,
    location: String,
    lastActive: Date,
    expiresAt: Date,
  }],
  
  // Timestamps
  lastLogin: Date,
  lastLoginIP: String,
  lastActive: Date,
  createdAt: {
    type: Date,
    default: Date.now,
  },
  updatedAt: {
    type: Date,
    default: Date.now,
  },
  
  // Account lock
  lockUntil: Date,
  loginAttempts: {
    type: Number,
    default: 0,
  },
  
  // Password reset
  passwordResetToken: String,
  passwordResetExpires: Date,
  
  // Metadata
  metadata: {
    registrationSource: String,
    registrationIP: String,
    userAgent: String,
    campaign: String,
  },
}, {
  timestamps: true,
  toJSON: {
    virtuals: true,
    transform: function(doc, ret) {
      delete ret.password;
      delete ret.twoFactorSecret;
      delete ret.passwordResetToken;
      delete ret.emailVerificationToken;
      return ret;
    },
  },
});

// Indexes
UserSchema.index({ email: 1 });
UserSchema.index({ username: 1 });
UserSchema.index({ 'socialAccounts.provider': 1, 'socialAccounts.providerId': 1 });
UserSchema.index({ referralCode: 1 });
UserSchema.index({ status: 1 });
UserSchema.index({ createdAt: -1 });

// Virtual for full name
UserSchema.virtual('profile.fullName').get(function() {
  if (this.profile.firstName && this.profile.lastName) {
    return `${this.profile.firstName} ${this.profile.lastName}`;
  }
  return this.profile.displayName || this.username;
});

// Pre-save middleware
UserSchema.pre('save', async function(next) {
  if (this.isModified('password') && this.password) {
    this.password = await bcrypt.hash(this.password, 12);
  }
  
  if (this.isNew && !this.userId) {
    this.userId = `USR${Date.now()}${Math.random().toString(36).substr(2, 9).toUpperCase()}`;
  }
  
  if (this.isNew && !this.referral.code) {
    this.referral.code = crypto.randomBytes(6).toString('hex').toUpperCase();
  }
  
  this.updatedAt = Date.now();
  next();
});

// Methods
UserSchema.methods.comparePassword = async function(candidatePassword) {
  if (!this.password) return false;
  return bcrypt.compare(candidatePassword, this.password);
};

UserSchema.methods.generateJWT = function() {
  return jwt.sign(
    {
      id: this._id,
      userId: this.userId,
      email: this.email,
      role: this.role,
      permissions: this.permissions,
    },
    process.env.JWT_SECRET || 'tigerex-jwt-secret',
    { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
  );
};

UserSchema.methods.generateRefreshToken = function() {
  return jwt.sign(
    { id: this._id, type: 'refresh' },
    process.env.JWT_REFRESH_SECRET || 'tigerex-refresh-secret',
    { expiresIn: '30d' }
  );
};

UserSchema.methods.createEmailVerificationToken = function() {
  const token = crypto.randomBytes(32).toString('hex');
  this.emailVerificationToken = crypto
    .createHash('sha256')
    .update(token)
    .digest('hex');
  this.emailVerificationExpires = Date.now() + 24 * 60 * 60 * 1000; // 24 hours
  return token;
};

UserSchema.methods.createPasswordResetToken = function() {
  const token = crypto.randomBytes(32).toString('hex');
  this.passwordResetToken = crypto
    .createHash('sha256')
    .update(token)
    .digest('hex');
  this.passwordResetExpires = Date.now() + 60 * 60 * 1000; // 1 hour
  return token;
};

UserSchema.methods.isLocked = function() {
  return this.lockUntil && this.lockUntil > Date.now();
};

UserSchema.methods.incLoginAttempts = function() {
  if (this.lockUntil && this.lockUntil < Date.now()) {
    return this.updateOne({
      $set: { loginAttempts: 1 },
      $unset: { lockUntil: 1 },
    });
  }
  
  const maxAttempts = 5;
  const lockTime = 2 * 60 * 60 * 1000; // 2 hours
  
  if (this.loginAttempts + 1 >= maxAttempts) {
    return this.updateOne({
      $set: { lockUntil: Date.now() + lockTime },
      $inc: { loginAttempts: 1 },
    });
  }
  
  return this.updateOne({ $inc: { loginAttempts: 1 } });
};

UserSchema.methods.resetLoginAttempts = function() {
  return this.updateOne({
    $set: { loginAttempts: 0 },
    $unset: { lockUntil: 1 },
  });
};

UserSchema.methods.addSocialAccount = function(accountData) {
  const existingAccount = this.socialAccounts.find(
    (a) => a.provider === accountData.provider && a.providerId === accountData.providerId
  );
  
  if (existingAccount) {
    existingAccount.lastUsed = Date.now();
    existingAccount.accessToken = accountData.accessToken;
    existingAccount.refreshToken = accountData.refreshToken;
    return this.save();
  }
  
  // If this is the first social account, make it primary
  if (this.socialAccounts.length === 0) {
    accountData.isPrimary = true;
  }
  
  this.socialAccounts.push(accountData);
  return this.save();
};

UserSchema.methods.removeSocialAccount = function(provider) {
  this.socialAccounts = this.socialAccounts.filter((a) => a.provider !== provider);
  return this.save();
};

UserSchema.methods.hasSocialAccount = function(provider) {
  return this.socialAccounts.some((a) => a.provider === provider);
};

UserSchema.methods.getPrimarySocialAccount = function() {
  return this.socialAccounts.find((a) => a.isPrimary);
};

// Static methods
UserSchema.statics.findBySocialId = function(provider, providerId) {
  return this.findOne({
    'socialAccounts.provider': provider,
    'socialAccounts.providerId': providerId,
  });
};

UserSchema.statics.findByEmail = function(email) {
  return this.findOne({ email: email.toLowerCase() });
};

UserSchema.statics.findByUsername = function(username) {
  return this.findOne({ username: username.toLowerCase() });
};

UserSchema.statics.findByReferralCode = function(code) {
  return this.findOne({ 'referral.code': code.toUpperCase() });
};

const User = mongoose.model('User', UserSchema);
module.exports = User;export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
