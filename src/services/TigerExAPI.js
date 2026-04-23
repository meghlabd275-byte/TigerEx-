/**
 * TigerEx API Service - Connects to all backend services
 */

const TigerExAPI = {
    config: { region: 'us', timezone: Intl.DateTimeFormat().resolvedOptions().timeZone },
    
    baseURL: 'https://api.tigerex.com',
    
    endpoints: {
        login: '/api/v1/auth/login',
        register: '/api/v1/auth/register',
        profile: '/api/v1/user/profile',
        ticker: '/api/v1/market/ticker',
        depth: '/api/v1/market/depth',
        trades: '/api/v1/market/trades',
        klines: '/api/v1/market/klines',
        exchangeInfo: '/api/v1/market/exchange-info',
        spotOrder: '/api/v1/trading/spot/order',
        spotOpenOrders: '/api/v1/trading/spot/open-orders',
        futuresOrder: '/api/v1/trading/futures/order',
        marginBorrow: '/api/v1/trading/margin/borrow',
        balance: '/api/v1/wallet/balance',
        depositAddress: '/api/v1/wallet/deposit/address',
        withdraw: '/api/v1/wallet/withdraw',
        convert: '/api/v1/wallet/convert',
        transfer: '/api/v1/wallet/transfer',
        p2pOrders: '/api/v1/p2p/orders',
        p2pCreateAd: '/api/v1/p2p/create-ad',
        staking: '/api/v1/staking',
        savings: '/api/v1/savings',
        launchpool: '/api/v1/launchpool',
        copyTraders: '/api/v1/copytrading/traders',
        cardApply: '/api/v1/card/apply',
        tickets: '/api/v1/support/tickets',
        adminUsers: '/api/v1/admin/users',
        adminKyc: '/api/v1/admin/kyc',
        adminWithdrawals: '/api/v1/admin/withdrawals',
    },
    
    async request(method, endpoint, data = null) {
        const url = this.baseURL + endpoint;
        const options = {
            method,
            headers: { 'Content-Type': 'application/json', 'X-Region': this.config.region },
        };
        if (data) options.body = JSON.stringify(data);
        
        const response = await fetch(url, options);
        if (!response.ok) throw new Error('Request failed');
        return response.json();
    },
    
    // Auth
    auth: {
        async login(email, password) {
            return TigerExAPI.request('POST', TigerExAPI.endpoints.login, { email, password });
        },
        async register(email, password, referralCode) {
            return TigerExAPI.request('POST', TigerExAPI.endpoints.register, { email, password, referralCode });
        },
    },
    
    // Market
    market: {
        async ticker(symbol) { return TigerExAPI.request('GET', `${TigerExAPI.endpoints.ticker}?symbol=${symbol}`); },
        async allTickers() { return TigerExAPI.request('GET', TigerExAPI.endpoints.ticker.replace('?symbol=BTCUSDT', '/all')); },
        async depth(symbol, limit = 20) { return TigerExAPI.request('GET', `${TigerExAPI.endpoints.depth}?symbol=${symbol}&limit=${limit}`); },
        async trades(symbol) { return TigerExAPI.request('GET', `${TigerExAPI.endpoints.trades}?symbol=${symbol}`); },
        async klines(symbol, interval = '1h') { return TigerExAPI.request('GET', `${TigerExAPI.endpoints.klines}?symbol=${symbol}&interval=${interval}`); },
    },
    
    // Trading
    trading: {
        async spotOrder(symbol, side, type, quantity, price) {
            return TigerExAPI.request('POST', TigerExAPI.endpoints.spotOrder, { symbol, side, type, quantity, price });
        },
        async getOpenOrders(symbol) { return TigerExAPI.request('GET', `${TigerExAPI.endpoints.spotOpenOrders}?symbol=${symbol}`); },
        async futuresOrder(symbol, side, quantity, leverage) {
            return TigerExAPI.request('POST', TigerExAPI.endpoints.futuresOrder, { symbol, side, quantity, leverage });
        },
    },
    
    // Wallet
    wallet: {
        async balance() { return TigerExAPI.request('GET', TigerExAPI.endpoints.balance); },
        async depositAddress(network) { return TigerExAPI.request('GET', `${TigerExAPI.endpoints.depositAddress}?network=${network}`); },
        async withdraw(address, network, amount) {
            return TigerExAPI.request('POST', TigerExAPI.endpoints.withdraw, { address, network, amount });
        },
        async convert(from, to, amount) {
            return TigerExAPI.request('POST', TigerExAPI.endpoints.convert, { fromCoin: from, toCoin: to, amount });
        },
    },
    
    // P2P
    p2p: {
        async orders() { return TigerExAPI.request('GET', TigerExAPI.endpoints.p2pOrders); },
        async createAd(data) { return TigerExAPI.request('POST', TigerExAPI.endpoints.p2pCreateAd, data); },
    },
    
    // Earn
    earn: {
        async staking() { return TigerExAPI.request('GET', TigerExAPI.endpoints.staking); },
        async savings() { return TigerExAPI.request('GET', TigerExAPI.endpoints.savings); },
        async launchpool() { return TigerExAPI.request('GET', TigerExAPI.endpoints.launchpool); },
    },
    
    // Copy Trading
    copyTrading: {
        async traders() { return TigerExAPI.request('GET', TigerExAPI.endpoints.copyTraders); },
    },
    
    // WebSocket
    ws: {
        socket: null,
        connect(onMessage) {
            this.socket = new WebSocket('wss://stream.tigerex.com/v1/ws');
            this.socket.onmessage = (e) => onMessage(JSON.parse(e.data));
            this.socket.onclose = () => setTimeout(() => this.connect(onMessage), 5000);
        },
        subscribe(channels) {
            if (this.socket?.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({ method: 'SUBSCRIBE', params: channels }));
            }
        },
    },
    
    init() {
        const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
        this.config.region = tz.includes('America') ? 'us' : tz.includes('Europe') ? 'eu' : 'asia';
    }
};

TigerExAPI.init();
if (typeof window !== 'undefined') window.TigerExAPI = TigerExAPI;
export default TigerExAPI;