import { UserRole, Feature, rolePermissions, roleNavigation, hasPermission, getDashboard } from '../shared/roles/rbac'

// ===== USER INTERFACE =====
export interface ITigerExUser {
    id: string
    email: string
    role: UserRole
    kycStatus: 'none' | 'pending' | 'verified' | 'rejected'
    isActive: boolean
}

// ===== DASHBOARD COMPONENTS =====

// Trader Dashboard (Basic User)
export const traderDashboard = {
    name: 'Trader',
    features: [
        { id: 'home', label: 'Home', icon: '🏠' },
        { id: 'markets', label: 'Markets', icon: '📊' },
        { id: 'trade', label: 'Trade', icon: '💱' },
        { id: 'assets', label: 'Assets', icon: '💼' },
        { id: 'earn', label: 'Earn', icon: '📈' },
        { id: 'p2p', label: 'P2P', icon: '🤝' }
    ]
}

// VIP Dashboard (Enhanced Trader)
export const vipDashboard = {
    ...traderDashboard,
    name: 'VIP',
    additionalFeatures: [
        { id: 'copy', label: 'Copy Trading', icon: '📋' },
        { id: 'megadrop', label: 'Megadrop', icon: '🎁' }
    ]
}

// Affiliate Dashboard
export const affiliateDashboard = {
    name: 'Affiliate',
    features: [
        { id: 'home', label: 'Home', icon: '🏠' },
        { id: 'markets', label: 'Markets', icon: '📊' },
        { id: 'trade', label: 'Trade', icon: '💱' },
        { id: 'assets', label: 'Assets', icon: '💼' },
        { id: 'referral', label: 'Referral', icon: '👥' },
        { id: 'commissions', label: 'Commissions', icon: '💰' },
        { id: 'tools', label: 'Marketing Tools', icon: '🛠️' }
    ]
}

// Partner Dashboard
export const partnerDashboard = {
    name: 'Partner',
    features: [
        ...affiliateDashboard.features,
        { id: 'otc', label: 'OTC Trading', icon: '🏦' },
        { id: 'api', label: 'API Management', icon: '🔌' }
    ]
}

// Institution Dashboard
export const institutionDashboard = {
    name: 'Institution',
    features: [
        { id: 'home', label: 'Dashboard', icon: '📊' },
        { id: 'trading', label: 'Trading', icon: '💱' },
        { id: 'portfolio', label: 'Portfolio', icon: '💼' },
        { id: 'otc', label: 'OTC', icon: '🏦' },
        { id: 'api', label: 'API', icon: '🔌' },
        { id: 'reports', label: 'Reports', icon: '📄' },
        { id: 'team', label: 'Team', icon: '👥' },
        { id: 'settings', label: 'Settings', icon: '⚙️' }
    ]
}

// P2P Merchant Dashboard
export const p2pMerchantDashboard = {
    name: 'P2P Merchant',
    features: [
        { id: 'home', label: 'Home', icon: '🏠' },
        { id: 'trade', label: 'Trade', icon: '💱' },
        { id: 'ads', label: 'My Ads', icon: '📢' },
        { id: 'orders', label: 'Orders', icon: '📋' },
        { id: 'chat', label: 'Chat', icon: '💬' },
        { id: 'earnings', label: 'Earnings', icon: '💰' }
    ]
}

// Liquidity Provider Dashboard
export const liquidityProviderDashboard = {
    name: 'Liquidity Provider',
    features: [
        { id: 'dashboard', label: 'Dashboard', icon: '📊' },
        { id: 'pools', label: 'Pools', icon: '🏊' },
        { id: 'volume', label: 'Volume', icon: '📈' },
        { id: 'earnings', label: 'Earnings', icon: '💰' },
        { id: 'api', label: 'API', icon: '🔌' }
    ]
}

// Market Maker Dashboard
export const marketMakerDashboard = {
    name: 'Market Maker',
    features: [
        { id: 'dashboard', label: 'Dashboard', icon: '📊' },
        { id: 'strategies', label: 'Strategies', icon: '🎯' },
        { id: 'pairs', label: 'Trading Pairs', icon: '👥' },
        { id: 'performance', label: 'Performance', icon: '📈' },
        { id: 'api', label: 'API', icon: '🔌' },
        { id: 'logs', label: 'Logs', icon: '📋' }
    ]
}

// Coin/Token Team Dashboard
export const coinTeamDashboard = {
    name: 'Coin/Token Team',
    features: [
        { id: 'home', label: 'Home', icon: '🏠' },
        { id: 'launchpool', label: 'Launchpool', icon: '🔥' },
        { id: 'megadrop', label: 'Megadrop', icon: '🎁' },
        { id: 'ido', label: 'IDO', icon: '🆕' },
        { id: 'airdrops', label: 'Airdrops', icon: '💸' },
        { id: 'analytics', label: 'Analytics', icon: '📊' }
    ]
}

// White Label Dashboard
export const whiteLabelDashboard = {
    name: 'White Label',
    features: [
        { id: 'dashboard', label: 'Dashboard', icon: '📊' },
        { id: 'trading', label: 'Trading', icon: '💱' },
        { id: 'users', label: 'Users', icon: '👥' },
        { id: 'revenue', label: 'Revenue', icon: '💰' },
        { id: 'branding', label: 'Branding', icon: '🎨' },
        { id: 'settings', label: 'Settings', icon: '⚙️' },
        { id: 'api', label: 'API', icon: '🔌' }
    ]
}

// ===== ADMIN DASHBOARDS =====

// Moderator Dashboard
export const moderatorDashboard = {
    name: 'Moderator',
    features: [
        { id: 'dashboard', label: 'Dashboard', icon: '📊' },
        { id: 'users', label: 'Users', icon: '👥' },
        { id: 'tickets', label: 'Tickets', icon: '🎫' },
        { id: 'reports', label: 'Reports', icon: '📋' }
    ]
}

// Support Team Dashboard
export const supportDashboard = {
    name: 'Support Team',
    features: [
        { id: 'dashboard', label: 'Dashboard', icon: '📊' },
        { id: 'tickets', label: 'Tickets', icon: '🎫' },
        { id: 'users', label: 'Users', icon: '👥' },
        { id: 'kyc', label: 'KYC', icon: '🆔' },
        { id: 'chat', label: 'Live Chat', icon: '💬' }
    ]
}

// Listing Manager Dashboard
export const listingManagerDashboard = {
    name: 'Listing Manager',
    features: [
        { id: 'dashboard', label: 'Dashboard', icon: '📊' },
        { id: 'markets', label: 'Markets', icon: '📊' },
        { id: 'listings', label: 'Listings', icon: '🆕' },
        { id: 'fees', label: 'Fees', icon: '💰' },
        { id: 'applications', label: 'Applications', icon: '📝' }
    ]
}

// BD Manager Dashboard
export const bdManagerDashboard = {
    name: 'BD Manager',
    features: [
        { id: 'dashboard', label: 'Dashboard', icon: '📊' },
        { id: 'partners', label: 'Partners', icon: '🤝' },
        { id: 'users', label: 'Users', icon: '👥' },
        { id: 'fees', label: 'Fees', icon: '💰' },
        { id: 'accounts', label: 'Accounts', icon: '🏢' }
    ]
}

// Liquidity Manager Dashboard
export const liquidityManagerDashboard = {
    name: 'Liquidity Manager',
    features: [
        { id: 'dashboard', label: 'Dashboard', icon: '📊' },
        { id: 'liquidity', label: 'Liquidity', icon: '💧' },
        { id: 'pools', label: 'Pools', icon: '🏊' },
        { id: 'markets', label: 'Markets', icon: '📊' },
        { id: 'withdrawals', label: 'Withdrawals', icon: '📤' },
        { id: 'analytics', label: 'Analytics', icon: '📈' }
    ]
}

// Technical Team Dashboard
export const technicalTeamDashboard = {
    name: 'Technical Team',
    features: [
        { id: 'dashboard', label: 'Dashboard', icon: '📊' },
        { id: 'system', label: 'System', icon: '🖥️' },
        { id: 'api', label: 'API', icon: '🔌' },
        { id: 'logs', label: 'Logs', icon: '📋' },
        { id: 'alerts', label: 'Alerts', icon: '⚠️' },
        { id: 'maintenance', label: 'Maintenance', icon: '🔧' }
    ]
}

// Compliance Manager Dashboard
export const complianceDashboard = {
    name: 'Compliance Manager',
    features: [
        { id: 'dashboard', label: 'Dashboard', icon: '📊' },
        { id: 'users', label: 'Users', icon: '👥' },
        { id: 'kyc', label: 'KYC', icon: '🆔' },
        { id: 'compliance', label: 'Compliance', icon: '✅' },
        { id: 'audit', label: 'Audit', icon: '📋' },
        { id: 'reports', label: 'Reports', icon: '📄' }
    ]
}

// Admin Dashboard
export const adminDashboard = {
    name: 'Admin',
    features: [
        { id: 'dashboard', label: 'Dashboard', icon: '📊' },
        { id: 'users', label: 'Users', icon: '👥' },
        { id: 'markets', label: 'Markets', icon: '📊' },
        { id: 'trading', label: 'Trading', icon: '💱' },
        { id: 'wallet', label: 'Wallet', icon: '💼' },
        { id: 'kyc', label: 'KYC', icon: '🆔' },
        { id: 'fees', label: 'Fees', icon: '💰' },
        { id: 'audit', label: 'Audit', icon: '📋' }
    ]
}

// Super Admin Dashboard (Complete)
export const superAdminDashboard = {
    name: 'Super Admin',
    features: [
        { id: 'dashboard', label: 'Dashboard', icon: '📊' },
        { id: 'users', label: 'Users', icon: '👥' },
        { id: 'markets', label: 'Markets', icon: '📊' },
        { id: 'trading', label: 'Trading', icon: '💱' },
        { id: 'wallet', label: 'Wallet', icon: '💼' },
        { id: 'kyc', label: 'KYC', icon: '🆔' },
        { id: 'fees', label: 'Fees', icon: '💰' },
        { id: 'audit', label: 'Audit', icon: '📋' },
        { id: 'system', label: 'System', icon: '⚙️' },
        { id: 'settings', label: 'Settings', icon: '🔧' }
    ]
}

// ===== DASHBOARD MAPPING =====
export const roleDashboards = {
    // End Users
    [UserRole.TRADER]: traderDashboard,
    [UserRole.VIP]: vipDashboard,
    [UserRole.AFFILIATE]: affiliateDashboard,
    [UserRole.PARTNER]: partnerDashboard,
    [UserRole.INSTITUTION]: institutionDashboard,
    [UserRole.P2P_MERCHANT]: p2pMerchantDashboard,
    [UserRole.LIQUIDITY_PROVIDER]: liquidityProviderDashboard,
    [UserRole.MARKET_MAKER]: marketMakerDashboard,
    [UserRole.COIN_TOKEN_TEAM]: coinTeamDashboard,
    [UserRole.WHITE_LABEL]: whiteLabelDashboard,
    
    // Admin Users
    [UserRole.MODERATOR]: moderatorDashboard,
    [UserRole.SUPPORT_TEAM]: supportDashboard,
    [UserRole.LISTING_MANAGER]: listingManagerDashboard,
    [UserRole.BD_MANAGER]: bdManagerDashboard,
    [UserRole.LIQUIDITY_MANAGER]: liquidityManagerDashboard,
    [UserRole.TECHNICAL_TEAM]: technicalTeamDashboard,
    [UserRole.COMPLIANCE_MANAGER]: complianceDashboard,
    [UserRole.ADMIN]: adminDashboard,
    [UserRole.SUPER_ADMIN]: superAdminDashboard
}

// Get dashboard by user
export function getUserDashboard(user: ITigerExUser) {
    return roleDashboards[user.role] || traderDashboard
}

// Get allowed features
export function getAllowedFeatures(role: UserRole): Feature[] {
    return rolePermissions[role] || []
}

// Check feature access
export function canAccessFeature(user: ITigerExUser, feature: Feature): boolean {
    return hasPermission(user.role, feature)
}

// Get navigation items
export function getNavigationItems(role: UserRole) {
    return roleNavigation[role] || ['Home', 'Markets', 'Trade', 'Assets']
}

export default {
    UserRole,
    Feature,
    roleDashboards,
    getUserDashboard,
    getAllowedFeatures,
    canAccessFeature,
    getNavigationItems
};