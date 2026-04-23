/**
 * TigerEx Multi-Platform Configuration
 * Supports: Multi-VM, Multi-Domain, Multi-Timezone, Multi-Cloud
 */

const TigerExConfig = {
    // Multi-VM: Load balancer IPs
    vm: {
        loadBalancers: ['10.0.0.1', '10.0.0.2', '10.0.0.3', '10.0.0.4'],
        healthCheckPath: '/api/health',
        healthCheckInterval: 30000,
    },
    
    // Multi-Domain
    domains: {
        primary: { us: 'tigerex.us', eu: 'tigerex.eu', asia: 'tigerex.asia', global: 'tigerex.com' },
        api: { us: 'api-us.tigerex.com', eu: 'api-eu.tigerex.com', asia: 'api-asia.tigerex.com' },
        admin: { us: 'admin-us.tigerex.com', eu: 'admin-eu.tigerex.com' },
    },
    
    // Multi-Timezone
    timezone: {
        supported: ['America/New_York', 'Europe/London', 'Asia/Singapore', 'Asia/Tokyo'],
        userTimezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    },
    
    // Multi-Cloud
    cloud: {
        providers: ['aws', 'gcp', 'azure'],
        currentProvider: 'aws',
    },
    
    // Backend Services
    services: {
        gateway: 'https://api.tigerex.com',
        user: '/api/v1/user',
        auth: '/api/v1/auth',
        market: '/api/v1/market',
        trading: '/api/v1/trading',
        wallet: '/api/v1/wallet',
        p2p: '/api/v1/p2p',
        earn: '/api/v1/earn',
        staking: '/api/v1/staking',
        launchpool: '/api/v1/launchpool',
        copytrading: '/api/v1/copytrading',
        admin: '/api/v1/admin',
    },
    
    // Database
    database: {
        primary: { host: 'tigerex-db.c123456.rds.amazonaws.com', port: 5432, name: 'tigerex_prod' },
        readReplicas: [{ host: 'tigerex-read-1.c234567.rds.amazonaws.com' }, { host: 'tigerex-read-eu.c234567.rds.amazonaws.com' }],
        redis: [{ host: 'tigerex-cache-1.redis.amazonaws.com', port: 6379 }],
    }
};

if (typeof window !== 'undefined') window.TigerExConfig = TigerExConfig;
export default TigerExConfig;