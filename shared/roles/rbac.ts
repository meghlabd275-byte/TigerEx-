// TigerEx Role-Based Access Control (RBAC) System
// All Roles with Dashboard, Features & Functionality

export enum UserRole {
    // ===== END USER ROLES =====
    TRADER = 'trader',
    VIP = 'vip',
    AFFILIATE = 'affiliate',
    PARTNER = 'partner',
    INSTITUTION = 'institution',
    P2P_MERCHANT = 'p2p_merchant',
    LIQUIDITY_PROVIDER = 'liquidity_provider',
    MARKET_MAKER = 'market_maker',
    COIN_TOKEN_TEAM = 'coin_token_team',
    WHITE_LABEL = 'white_label',
    
    // ===== ADMIN USER ROLES =====
    SUPER_ADMIN = 'super_admin',
    ADMIN = 'admin',
    MODERATOR = 'moderator',
    LISTING_MANAGER = 'listing_manager',
    BD_MANAGER = 'bd_manager',
    SUPPORT_TEAM = 'support_team',
    LIQUIDITY_MANAGER = 'liquidity_manager',
    TECHNICAL_TEAM = 'technical_team',
    COMPLIANCE_MANAGER = 'compliance_manager'
}

// Role Hierarchy
export const roleHierarchy: Record<UserRole, number> = {
    // Admin roles (higher priority)
    [UserRole.SUPER_ADMIN]: 100,
    [UserRole.ADMIN]: 90,
    [UserRole.LIQUIDITY_MANAGER]: 85,
    [UserRole.TECHNICAL_TEAM]: 80,
    [UserRole.COMPLIANCE_MANAGER]: 75,
    [UserRole.LISTING_MANAGER]: 70,
    [UserRole.BD_MANAGER]: 65,
    [UserRole.SUPPORT_TEAM]: 60,
    [UserRole.MODERATOR]: 55,
    
    // End user roles
    [UserRole.INSTITUTION]: 50,
    [UserRole.WHITE_LABEL]: 45,
    [UserRole.PARTNER]: 40,
    [UserRole.MARKET_MAKER]: 35,
    [UserRole.LIQUIDITY_PROVIDER]: 30,
    [UserRole.P2P_MERCHANT]: 25,
    [UserRole.VIP]: 20,
    [UserRole.COIN_TOKEN_TEAM]: 18,
    [UserRole.AFFILIATE]: 15,
    [UserRole.TRADER]: 10
};

// Feature Flags
export enum Feature {
    // Trading
    SPOT_TRADING = 'spot_trading',
    FUTURES_TRADING = 'futures_trading',
    MARGIN_TRADING = 'margin_trading',
    OPTIONS_TRADING = 'options_trading',
    ALPHA_TRADING = 'alpha_trading',
    COPY_TRADING = 'copy_trading',
    TRADEX = 'tradex',
    
    // Earn Products
    STAKING = 'staking',
    SAVINGS = 'savings',
    LAUNCHPOOL = 'launchpool',
    MEGADROP = 'megadrop',
    IDO = 'ido',
    CLOUD_MINING = 'cloud_mining',
    
    // P2P
    P2P_TRADING = 'p2p_trading',
    P2P_MERCHANT = 'p2p_merchant',
    P2P_CREATE_AD = 'p2p_create_ad',
    
    // Fiat
    FIAT_BUY = 'fiat_buy',
    FIAT_SELL = 'fiat_sell',
    CARD = 'card',
    
    // Wallet
    DEPOSIT = 'deposit',
    WITHDRAW = 'withdraw',
    CONVERT = 'convert',
    SEND_CRYPTO = 'send_crypto',
    REDPACKET = 'redpacket',
    
    // Institutional
    OTC_TRADING = 'otc_trading',
    INSTITUTIONAL_API = 'institutional_api',
    CUSTODY = 'custody',
    
    // Marketing
    REFERRAL = 'referral',
    AFFILIATE = 'affiliate',
    
    // Advanced
    API_ACCESS = 'api_access',
    MARGIN_BORROW = 'margin_borrow',
    WHITELABEL = 'whitelabel',
    
    // Admin Features
    USER_MANAGEMENT = 'user_management',
    KYC_APPROVAL = 'kyc_approval',
    TRADING_PAIRS = 'trading_pairs',
    FEE_MANAGEMENT = 'fee_management',
    LISTING = 'listing',
    WITHDRAWAL_APPROVAL = 'withdrawal_approval',
    LIQUIDITY_MANAGEMENT = 'liquidity_management',
    MARKET_MAKING = 'market_making',
    SUPPORT_TICKETS = 'support_tickets',
    COMPLIANCE = 'compliance',
    AUDIT_LOGS = 'audit_logs',
    SYSTEM_CONFIG = 'system_config'
}

// Role Permissions Mapping
export const rolePermissions: Record<UserRole, Feature[]> = {
    // ===== END USERS =====
    [UserRole.TRADER]: [
        Feature.SPOT_TRADING,
        Feature.DEPOSIT,
        Feature.WITHDRAW,
        Feature.CONVERT,
        Feature.SEND_CRYPTO,
        Feature.SAVINGS,
        Feature.LAUNCHPOOL,
        Feature.P2P_TRADING,
        Feature.API_ACCESS
    ],
    
    [UserRole.VIP]: [
        ...rolePermissions[UserRole.TRADER],
        Feature.FUTURES_TRADING,
        Feature.STAKING,
        Feature.MEGADROP,
        Feature.COPY_TRADING,
        Feature.REFERRAL
    ],
    
    [UserRole.AFFILIATE]: [
        ...rolePermissions[UserRole.TRADER],
        Feature.AFFILIATE,
        Feature.REFERRAL,
        Feature.FUTURES_TRADING
    ],
    
    [UserRole.PARTNER]: [
        ...rolePermissions[UserRole.VIP],
        Feature.OTC_TRADING,
        Feature.LISTING,
        Feature.COPY_TRADING
    ],
    
    [UserRole.INSTITUTION]: [
        Feature.SPOT_TRADING,
        Feature.FUTURES_TRADING,
        Feature.MARGIN_TRADING,
        Feature.OPTIONS_TRADING,
        Feature.OTC_TRADING,
        Feature.INSTITUTIONAL_API,
        Feature.DEPOSIT,
        Feature.WITHDRAW,
        Feature.CONVERT,
        Feature.SEND_CRYPTO,
        Feature.CARD
    ],
    
    [UserRole.P2P_MERCHANT]: [
        ...rolePermissions[UserRole.TRADER],
        Feature.P2P_TRADING,
        Feature.P2P_MERCHANT,
        Feature.P2P_CREATE_AD,
        Feature.FUTURES_TRADING
    ],
    
    [UserRole.LIQUIDITY_PROVIDER]: [
        ...rolePermissions[UserRole.TRADER],
        Feature.FUTURES_TRADING,
        Feature.MARGIN_TRADING,
        Feature.DEPOSIT,
        Feature.WITHDRAW,
        Feature.LIQUIDITY_MANAGEMENT
    ],
    
    [UserRole.MARKET_MAKER]: [
        ...rolePermissions[UserRole.LIQUIDITY_PROVIDER],
        Feature.API_ACCESS,
        Feature.MARKET_MAKING,
        Feature.TRADING_PAIRS,
        Feature.MARGIN_TRADING
    ],
    
    [UserRole.COIN_TOKEN_TEAM]: [
        ...rolePermissions[UserRole.TRADER],
        Feature.LAUNCHPOOL,
        Feature.MEGADROP,
        Feature.IDO,
        Feature.CLOUD_MINING
    ],
    
    [UserRole.WHITE_LABEL]: [
        ...rolePermissions[UserRole.TRADER],
        Feature.WHITELABEL,
        Feature.REFERRAL,
        Feature.FUTURES_TRADING,
        Feature.STAKING,
        Feature.SAVINGS,
        Feature.LAUNCHPOOL
    ],
    
    // ===== ADMIN USERS =====
    [UserRole.MODERATOR]: [
        Feature.SUPPORT_TICKETS,
        Feature.COMPLIANCE
    ],
    
    [UserRole.SUPPORT_TEAM]: [
        Feature.SUPPORT_TICKETS,
        Feature.USER_MANAGEMENT,
        Feature.KYC_APPROVAL,
        Feature.COMPLIANCE
    ],
    
    [UserRole.LISTING_MANAGER]: [
        Feature.LISTING,
        Feature.FEE_MANAGEMENT,
        Feature.TRADING_PAIRS
    ],
    
    [UserRole.BD_MANAGER]: [
        Feature.USER_MANAGEMENT,
        Feature.LISTING,
        Feature.FEE_MANAGEMENT
    ],
    
    [UserRole.LIQUIDITY_MANAGER]: [
        Feature.LIQUIDITY_MANAGEMENT,
        Feature.MARKET_MAKING,
        Feature.TRADING_PAIRS,
        Feature.WITHDRAWAL_APPROVAL,
        Feature.FEE_MANAGEMENT
    ],
    
    [UserRole.TECHNICAL_TEAM]: [
        Feature.USER_MANAGEMENT,
        Feature.TRADING_PAIRS,
        Feature.FEE_MANAGEMENT,
        Feature.SYSTEM_CONFIG,
        Feature.API_ACCESS,
        Feature.AUDIT_LOGS
    ],
    
    [UserRole.COMPLIANCE_MANAGER]: [
        Feature.USER_MANAGEMENT,
        Feature.KYC_APPROVAL,
        Feature.COMPLIANCE,
        Feature.AUDIT_LOGS,
        Feature.WITHDRAWAL_APPROVAL
    ],
    
    [UserRole.ADMIN]: [
        Feature.USER_MANAGEMENT,
        Feature.KYC_APPROVAL,
        Feature.TRADING_PAIRS,
        Feature.FEE_MANAGEMENT,
        Feature.LISTING,
        Feature.WITHDRAWAL_APPROVAL,
        Feature.LIQUIDITY_MANAGEMENT,
        Feature.MARKET_MAKING,
        Feature.SUPPORT_TICKETS,
        Feature.COMPLIANCE,
        Feature.AUDIT_LOGS,
        Feature.SYSTEM_CONFIG
    ],
    
    [UserRole.SUPER_ADMIN]: Object.values(Feature)
};

// Check if role has permission
export function hasPermission(role: UserRole, feature: Feature): boolean {
    return rolePermissions[role]?.includes(feature) ?? false;
}

// Get dashboard for role
export function getDashboard(role: UserRole): 'user' | 'admin' | 'institution' | 'whitelabel' {
    if ([UserRole.INSTITUTION, UserRole.WHITE_LABEL].includes(role)) {
        return 'institution';
    }
    if (role >= UserRole.MODERATOR) {
        return 'admin';
    }
    if (role === UserRole.WHITE_LABEL) {
        return 'whitelabel';
    }
    return 'user';
}

// Navigation items by role
export const roleNavigation: Record<UserRole, string[]> = {
    [UserRole.TRADER]: ['Home', 'Markets', 'Trade', 'Assets', 'Earn', 'P2P'],
    [UserRole.VIP]: ['Home', 'Markets', 'Trade', 'Assets', 'Earn', 'P2P', 'Copy Trading'],
    [UserRole.AFFILIATE]: ['Home', 'Markets', 'Trade', 'Assets', 'Earn', 'P2P', 'Referral'],
    [UserRole.PARTNER]: ['Home', 'Markets', 'Trade', 'Assets', 'Earn', 'P2P', 'API'],
    [UserRole.INSTITUTION]: ['Home', 'Markets', 'Trade', 'Assets', 'Earn', 'P2P', 'OTC', 'API'],
    [UserRole.P2P_MERCHANT]: ['Home', 'Markets', 'Trade', 'Assets', 'P2P', 'My Ads', 'Orders'],
    [UserRole.LIQUIDITY_PROVIDER]: ['Home', 'Markets', 'Trade', 'Assets', 'Pools'],
    [UserRole.MARKET_MAKER]: ['Home', 'Markets', 'Trade', 'API', 'Dashboard'],
    [UserRole.COIN_TOKEN_TEAM]: ['Home', 'Markets', 'Launchpool', 'Megadrop', 'Airdrop'],
    [UserRole.WHITE_LABEL]: ['Home', 'Markets', 'Trade', 'Assets', 'Earn', 'P2P', 'Settings', 'Branding'],
    
    [UserRole.MODERATOR]: ['Dashboard', 'Users', 'Tickets', 'Reports'],
    [UserRole.SUPPORT_TEAM]: ['Dashboard', 'Users', 'Tickets', 'KYC'],
    [UserRole.LISTING_MANAGER]: ['Dashboard', 'Markets', 'Listings', 'Fees'],
    [UserRole.BD_MANAGER]: ['Dashboard', 'Users', 'Partners', 'Fees'],
    [UserRole.LIQUIDITY_MANAGER]: ['Dashboard', 'Liquidity', 'Markets', 'Pools'],
    [UserRole.TECHNICAL_TEAM]: ['Dashboard', 'System', 'API', 'Logs'],
    [UserRole.COMPLIANCE_MANAGER]: ['Dashboard', 'Users', 'KYC', 'Compliance', 'Audit'],
    [UserRole.ADMIN]: ['Dashboard', 'Users', 'Markets', 'Trading', 'Wallet', 'KYC', 'Fees', 'Audit'],
    [UserRole.SUPER_ADMIN]: ['Dashboard', 'Users', 'Markets', 'Trading', 'Wallet', 'KYC', 'Fees', 'Audit', 'System', 'Settings']
};

export default {
    UserRole,
    roleHierarchy,
    Feature,
    rolePermissions,
    hasPermission,
    getDashboard,
    roleNavigation
};