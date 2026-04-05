const mongoose = require('mongoose');

const AuditLogSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    index: true,
  },
  action: {
    type: String,
    required: true,
    enum: [
      'login', 'logout', 'register', 'password_change', 'password_reset',
      'email_verification', 'phone_verification', 'two_factor_enable',
      'two_factor_disable', 'social_link', 'social_unlink', 'social_login',
      'profile_update', 'security_settings_change', 'account_suspend',
      'account_activate', 'account_delete', 'role_change', 'permission_change',
      'api_key_create', 'api_key_revoke', 'withdrawal_request', 'deposit',
      'trade', 'admin_action', 'failed_login', 'account_lock', 'account_unlock',
    ],
  },
  category: {
    type: String,
    enum: ['auth', 'security', 'trading', 'wallet', 'admin', 'profile'],
    default: 'auth',
  },
  details: {
    type: mongoose.Schema.Types.Mixed,
  },
  ipAddress: String,
  userAgent: String,
  device: String,
  browser: String,
  os: String,
  location: {
    country: String,
    city: String,
    latitude: Number,
    longitude: Number,
  },
  status: {
    type: String,
    enum: ['success', 'failed', 'pending'],
    default: 'success',
  },
  errorMessage: String,
  metadata: {
    type: mongoose.Schema.Types.Mixed,
  },
  timestamp: {
    type: Date,
    default: Date.now,
    index: true,
  },
});

AuditLogSchema.index({ userId: 1, timestamp: -1 });
AuditLogSchema.index({ action: 1, timestamp: -1 });
AuditLogSchema.index({ ipAddress: 1 });

AuditLogSchema.statics.log = async function(data) {
  return this.create(data);
};

AuditLogSchema.statics.getUserLogs = function(userId, limit = 50) {
  return this.find({ userId })
    .sort({ timestamp: -1 })
    .limit(limit);
};

AuditLogSchema.statics.getFailedLogins = function(ipAddress, hours = 24) {
  const since = new Date(Date.now() - hours * 60 * 60 * 1000);
  return this.countDocuments({
    action: { $in: ['failed_login', 'account_lock'] },
    ipAddress,
    timestamp: { $gte: since },
  });
};

module.exports = mongoose.model('AuditLog', AuditLogSchema);