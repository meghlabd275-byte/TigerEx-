/**
 * TigerEx API Configuration
 * All API endpoints for frontend integration
 */

export const API_CONFIG = {
  baseUrl: process.env.API_URL || 'https://api.tigerex.com',
  wsUrl: process.env.WS_URL || 'wss://stream.tigerex.com',
  endpoints: {
    auth: { login: '/api/v1/auth/login', register: '/api/v1/auth/register', logout: '/api/v1/auth/logout' },
    trading: { spot: '/api/v1/spot', margin: '/api/v1/margin', futures: '/api/v1/futures', orders: '/api/v1/orders' },
    wallet: { balance: '/api/v1/wallet/balance', deposit: '/api/v1/wallet/deposit', withdraw: '/api/v1/wallet/withdraw' },
    earn: { staking: '/api/v1/earn/staking', savings: '/api/v1/earn/savings', launchpool: '/api/v1/earn/launchpool' },
    nft: { collections: '/api/v1/nft/collections', items: '/api/v1/nft/items' },
    admin: { dashboard: '/api/v1/admin/dashboard', users: '/api/v1/admin/users', coins: '/api/v1/admin/coins' },
    market: { ticker: '/api/v1/market/ticker', prices: '/api/v1/market/prices', depth: '/api/v1/market/depth' }
  }
};

export const RBAC = {
  roles: {
    admin: { level: 5, permissions: ['*'] },
    mod: { level: 4, permissions: ['read', 'write', 'manageUsers'] },
    trader: { level: 3, permissions: ['read', 'write', 'trade'] },
    user: { level: 2, permissions: ['read', 'write'] },
    viewer: { level: 1, permissions: ['read'] }
  },
  checkPermission(role: string, permission: string): boolean {
    const roleConfig = this.roles[role];
    if (!roleConfig) return false;
    if (roleConfig.permissions.includes('*')) return true;
    return roleConfig.permissions.includes(permission);
  }
};

export const Platform = {
  isWeb: typeof window !== 'undefined',
  getPlatform(): string {
    if (typeof window === 'undefined') return 'server';
    if (/Android/.test(navigator.userAgent)) return 'android';
    if (/iPhone|iPad|iPod/.test(navigator.userAgent)) return 'ios';
    return 'web';
  }
};

export default { API_CONFIG, RBAC, Platform };