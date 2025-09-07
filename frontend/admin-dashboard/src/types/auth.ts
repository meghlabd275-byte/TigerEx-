export type AdminRole =
  | 'super_admin'
  | 'kyc_admin'
  | 'customer_support'
  | 'p2p_manager'
  | 'affiliate_manager'
  | 'bdm'
  | 'technical_team'
  | 'listing_manager'
  | 'compliance_officer'
  | 'risk_manager';

export interface AdminUser {
  id: string;
  email: string;
  username: string;
  firstName?: string;
  lastName?: string;
  role: AdminRole;
  permissions: string[];
  lastLoginAt?: string;
  createdAt: string;
  isActive: boolean;
  twoFactorEnabled: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
  twoFactorCode?: string;
  rememberMe?: boolean;
}

export interface AuthResponse {
  token: string;
  refreshToken: string;
  user: AdminUser;
  expiresIn: number;
}

export interface Permission {
  id: string;
  name: string;
  description: string;
  category: string;
}

export const ADMIN_PERMISSIONS = {
  // User Management
  VIEW_USERS: 'view_users',
  EDIT_USERS: 'edit_users',
  SUSPEND_USERS: 'suspend_users',
  DELETE_USERS: 'delete_users',

  // KYC Management
  VIEW_KYC: 'view_kyc',
  APPROVE_KYC: 'approve_kyc',
  REJECT_KYC: 'reject_kyc',
  BULK_KYC_ACTIONS: 'bulk_kyc_actions',

  // Trading Management
  VIEW_TRADES: 'view_trades',
  CANCEL_TRADES: 'cancel_trades',
  ADJUST_BALANCES: 'adjust_balances',
  VIEW_ORDER_BOOK: 'view_order_book',

  // P2P Management
  VIEW_P2P: 'view_p2p',
  MANAGE_P2P_DISPUTES: 'manage_p2p_disputes',
  MODERATE_P2P_ADS: 'moderate_p2p_ads',

  // System Management
  VIEW_SYSTEM_SETTINGS: 'view_system_settings',
  EDIT_SYSTEM_SETTINGS: 'edit_system_settings',
  VIEW_ANALYTICS: 'view_analytics',
  EXPORT_DATA: 'export_data',

  // Blockchain Management
  DEPLOY_BLOCKCHAIN: 'deploy_blockchain',
  MANAGE_WALLETS: 'manage_wallets',
  VIEW_BLOCKCHAIN_ANALYTICS: 'view_blockchain_analytics',

  // White Label Management
  CREATE_WHITE_LABEL: 'create_white_label',
  MANAGE_WHITE_LABEL: 'manage_white_label',
  DEPLOY_WHITE_LABEL: 'deploy_white_label',

  // Financial Management
  VIEW_FINANCIAL_REPORTS: 'view_financial_reports',
  MANAGE_FEES: 'manage_fees',
  PROCESS_WITHDRAWALS: 'process_withdrawals',

  // Support Management
  VIEW_SUPPORT_TICKETS: 'view_support_tickets',
  RESPOND_TO_TICKETS: 'respond_to_tickets',
  ESCALATE_TICKETS: 'escalate_tickets',

  // Affiliate Management
  VIEW_AFFILIATES: 'view_affiliates',
  MANAGE_AFFILIATE_PROGRAMS: 'manage_affiliate_programs',
  APPROVE_AFFILIATE_PAYOUTS: 'approve_affiliate_payouts',

  // Listing Management
  VIEW_LISTING_REQUESTS: 'view_listing_requests',
  APPROVE_LISTINGS: 'approve_listings',
  MANAGE_TRADING_PAIRS: 'manage_trading_pairs',
} as const;

export type PermissionKey = keyof typeof ADMIN_PERMISSIONS;
