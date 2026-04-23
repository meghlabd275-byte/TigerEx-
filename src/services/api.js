/**
 * TigerEx Unified API - All Services Connected
 * Version: 2.0.0
 * Features: Multi-VM, Multi-Domain, Multi-Timezone, Multi-Cloud
 */

// Base URL (Load balanced)
const BASE_URL = 'https://api.tigerex.com';
const WS_URL = 'wss://stream.tigerex.com';

// Service Endpoints Map
const SERVICES = {
    // Auth & User
    auth: {
        login: '/api/v1/auth/login',
        register: '/api/v1/auth/register',
        logout: '/api/v1/auth/logout',
        refreshToken: '/api/v1/auth/refresh',
        forgotPassword: '/api/v1/auth/forgot-password',
        verifyEmail: '/api/v1/auth/verify-email',
        twoFactor: '/api/v1/auth/2fa',
    },
    user: {
        profile: '/api/v1/user/profile',
        updateProfile: '/api/v1/user/profile/update',
        kyc: '/api/v1/user/kyc',
        documents: '/api/v1/user/documents',
        preferences: '/api/v1/user/preferences',
        security: '/api/v1/user/security',
    },
    
    // Market Data
    market: {
        ticker: '/api/v1/market/ticker',
        tickerAll: '/api/v1/market/ticker/all',
        depth: '/api/v1/market/depth',
        trades: '/api/v1/market/trades',
        klines: '/api/v1/market/klines',
        exchangeInfo: '/api/v1/market/exchange-info',
        candles: '/api/v1/market/candles',
       24hr: '/api/v1/market/24hr',
    },
    
    // Trading - Spot
    spot: {
        order: '/api/v1/trading/spot/order',
        cancel: '/api/v1/trading/spot/cancel',
        openOrders: '/api/v1/trading/spot/open-orders',
        history: '/api/v1/trading/spot/history',
        myTrades: '/api/v1/trading/spot/my-trades',
        orderBook: '/api/v1/trading/spot/order-book',
    },
    
    // Trading - Futures
    futures: {
        order: '/api/v1/trading/futures/order',
        cancel: '/api/v1/trading/futures/cancel',
        position: '/api/v1/trading/futures/position',
        positions: '/api/v1/trading/futures/positions',
        openOrders: '/api/v1/trading/futures/open-orders',
        history: '/api/v1/trading/futures/history',
        funding: '/api/v1/trading/futures/funding',
    },
    
    // Trading - Margin
    margin: {
        borrow: '/api/v1/trading/margin/borrow',
        repay: '/api/v1/trading/margin/repay',
        borrowHistory: '/api/v1/trading/margin/borrow-history',
        account: '/api/v1/trading/margin/account',
        maxBorrow: '/api/v1/trading/margin/max-borrow',
    },
    
    // Trading - Options
    options: {
        order: '/api/v1/trading/options/order',
        positions: '/api/v1/trading/options/positions',
        openOrders: '/api/v1/trading/options/open-orders',
    },
    
    // Wallet
    wallet: {
        balance: '/api/v1/wallet/balance',
        allBalances: '/api/v1/wallet/balances',
        depositAddress: '/api/v1/wallet/deposit/address',
        depositList: '/api/v1/wallet/deposit/list',
        withdraw: '/api/v1/wallet/withdraw',
        withdrawList: '/api/v1/wallet/withdraw/list',
        withdrawFee: '/api/v1/wallet/withdraw-fee',
        convert: '/api/v1/wallet/convert',
        transfer: '/api/v1/wallet/transfer',
       dust: '/api/v1/wallet/dust',
    },
    
    // P2P
    p2p: {
        orders: '/api/v1/p2p/orders',
        createAd: '/api/v1/p2p/create-ad',
        myAds: '/api/v1/p2p/my-ads',
        orderDetail: '/api/v1/p2p/order',
        buy: '/api/v1/p2p/buy',
        sell: '/api/v1/p2p/sell',
        chat: '/api/v1/p2p/chat',
        release: '/api/v1/p2p/release',
        cancel: '/api/v1/p2p/cancel',
    },
    
    // Earn - Staking
    staking: {
        products: '/api/v1/staking/products',
        join: '/api/v1/staking/join',
        leave: '/api/v1/staking/leave',
        history: '/api/v1/staking/history',
        rewards: '/api/v1/staking/rewards',
    },
    
    // Earn - Savings
    savings: {
        products: '/api/v1/savings/products',
        deposit: '/api/v1/savings/deposit',
        withdraw: '/api/v1/savings/withdraw',
        history: '/api/v1/savings/history',
    },
    
    // Earn - Launchpool
    launchpool: {
        products: '/api/v1/launchpool/products',
        stake: '/api/v1/launchpool/stake',
        unstake: '/api/v1/launchpool/unstake',
        rewards: '/api/v1/launchpool/rewards',
    },
    
    // Earn - Megadrop
    megadrop: {
        products: '/api/v1/megadrop/products',
        claim: '/api/v1/megadrop/claim',
    },
    
    // Copy Trading
    copyTrading: {
        traders: '/api/v1/copytrading/traders',
        follow: '/api/v1/copytrading/follow',
        unfollow: '/api/v1/copytrading/unfollow',
        myTrades: '/api/v1/copytrading/my-trades',
        copyTraders: '/api/v1/copytrading/copy-traders',
    },
    
    // Card
    card: {
        apply: '/api/v1/card/apply',
        details: '/api/v1/card/details',
        freeze: '/api/v1/card/freeze',
        transactions: '/api/v1/card/transactions',
    },
    
    // NFT
    nft: {
        collections: '/api/v1/nft/collections',
        products: '/api/v1/nft/products',
        buy: '/api/v1/nft/buy',
        list: '/api/v1/nft/mylist',
    },
    
    // Red Packet
    redPacket: {
        create: '/api/v1/redpacket/create',
        claim: '/api/v1/redpacket/claim',
        records: '/api/v1/redpacket/records',
    },
    
    // Air drop
    airdrop: {
        list: '/api/v1/airdrop/list',
        claim: '/api/v1/airdrop/claim',
        records: '/api/v1/airdrop/records',
    },
    
    // Support
    support: {
        tickets: '/api/v1/support/tickets',
        createTicket: '/api/v1/support/ticket/create',
        ticketDetail: '/api/v1/support/ticket',
        reply: '/api/v1/support/reply',
    },
    
    // Admin
    admin: {
        users: '/api/v1/admin/users',
        userDetail: '/api/v1/admin/user',
        kyc: '/api/v1/admin/kyc',
        kycApprove: '/api/v1/admin/kyc/approve',
        kycReject: '/api/v1/admin/kyc/reject',
        withdrawals: '/api/v1/admin/withdrawals',
        withdrawalApprove: '/api/v1/admin/withdrawals/approve',
        withdrawalReject: '/api/v1/admin/withdrawals/reject',
        trading: '/api/v1/admin/trading',
        tradingPairs: '/api/v1/admin/trading-pairs',
        liquidity: '/api/v1/admin/liquidity',
        analytics: '/api/v1/admin/analytics',
        settings: '/api/v1/admin/settings',
        auditLogs: '/api/v1/admin/audit-logs',
        createUser: '/api/v1/admin/user/create',
    },
};

// API Client
class TigerExClient {
    constructor() {
        this.config = {
            region: this.detectRegion(),
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            cloud: 'aws',
        };
        this.token = localStorage.getItem('tigerex_token');
    }
    
    detectRegion() {
        const tz = this.config.timezone;
        if (tz.includes('America')) return 'us';
        if (tz.includes('Europe')) return 'eu';
        if (tz.includes('Asia')) return 'asia';
        return 'us';
    }
    
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
            'X-Region': this.config.region,
            'X-Timezone': this.config.timezone,
            'X-Cloud': this.config.cloud,
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }
    
    async request(method, service, endpoint, data = null) {
        const url = BASE_URL + SERVICES[service][endpoint];
        const options = {
            method,
            headers: this.getHeaders(),
        };
        if (data) options.body = JSON.stringify(data);
        
        const response = await fetch(url, options);
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.message || `HTTP ${response.status}`);
        }
        return response.json();
    }
    
    get(service, endpoint) {
        return this.request('GET', service, endpoint);
    }
    
    post(service, endpoint, data) {
        return this.request('POST', service, endpoint, data);
    }
    
    // Auth
    auth = {
        login: (email, password, twoFa) => this.post('auth', 'login', { email, password, twoFactorCode: twoFa }),
        register: (email, password, referral) => this.post('auth', 'register', { email, password, referralCode: referral }),
        logout: () => this.post('auth', 'logout'),
    };
    
    // User
    user = {
        profile: () => this.get('user', 'profile'),
        update: (data) => this.post('user', 'updateProfile', data),
        kyc: () => this.get('user', 'kyc'),
    };
    
    // Market
    market = {
        ticker: (symbol) => this.get('market', symbol ? `ticker?symbol=${symbol}` : 'tickerAll'),
        depth: (symbol, limit = 20) => this.get('market', `depth?symbol=${symbol}&limit=${limit}`),
        trades: (symbol) => this.get('market', `trades?symbol=${symbol}`),
        klines: (symbol, interval = '1h') => this.get('market', `klines?symbol=${symbol}&interval=${interval}`),
    };
    
    // Trading
    trading = {
        spot: (symbol, side, type, qty, price) => this.post('spot', 'order', { symbol, side, type, quantity: qty, price }),
        futures: (symbol, side, qty, leverage = 20) => this.post('futures', 'order', { symbol, side, quantity: qty, leverage }),
        margin: (symbol, side, qty) => this.post('margin', side === 'borrow' ? 'borrow' : 'repay', { symbol, quantity: qty }),
    };
    
    // Wallet
    wallet = {
        balance: () => this.get('wallet', 'balance'),
        depositAddress: (network) => this.get('wallet', `depositAddress?network=${network}`),
        withdraw: (addr, network, amount) => this.post('wallet', 'withdraw', { address: addr, network, amount }),
        convert: (from, to, amount) => this.post('wallet', 'convert', { fromCoin: from, toCoin: to, amount }),
    };
    
    // P2P
    p2p = {
        orders: (filters = {}) => this.get('p2p', 'orders?' + new URLSearchParams(filters).toString()),
        createAd: (data) => this.post('p2p', 'createAd', data),
    };
    
    // Earn
    earn = {
        staking: () => this.get('staking', 'products'),
        stakingJoin: (productId, amount) => this.post('staking', 'join', { productId, amount }),
        savings: () => this.get('savings', 'products'),
        launchpool: () => this.get('launchpool', 'products'),
    };
    
    // Copy Trading
    copyTrading = {
        traders: () => this.get('copyTrading', 'traders'),
        follow: (traderId, amount) => this.post('copyTrading', 'follow', { traderId, amount }),
    };
    
    // Card
    card = {
        apply: () => this.post('card', 'apply'),
        details: () => this.get('card', 'details'),
    };
    
    // Admin
    admin = {
        users: (page = 1) => this.get('admin', `users?page=${page}`),
        kyc: () => this.get('admin', 'kyc'),
        kycApprove: (userId) => this.post('admin', 'kycApprove', { userId }),
        kycReject: (userId, reason) => this.post('admin', 'kycReject', { userId, reason }),
        withdrawals: () => this.get('admin', 'withdrawals'),
        withdrawApprove: (id) => this.post('admin', 'withdrawalApprove', { transactionId: id }),
        withdrawReject: (id, reason) => this.post('admin', 'withdrawalReject', { transactionId: id, reason }),
    };
    
    // WebSocket
    ws = {
        socket: null,
        connect(channels = ['btcusdt@trade']) {
            this.socket = new WebSocket(WS_URL);
            this.socket.onopen = () => this.ws.subscribe(channels);
            this.socket.onclose = () => setTimeout(() => this.ws.connect(), 5000);
        },
        subscribe(channels) {
            if (this.socket?.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({ method: 'SUBSCRIBE', params: channels }));
            }
        },
    };
    
    setToken(token) {
        this.token = token;
        localStorage.setItem('tigerex_token', token);
    }
    
    clearToken() {
        this.token = null;
        localStorage.removeItem('tigerex_token');
    }
}

// Export
const api = new TigerExClient();
export default api;
if (typeof window !== 'undefined') window.TigerExAPI = api;