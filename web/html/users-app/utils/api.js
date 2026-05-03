/**
 * TigerEx API Utility
 * Connects all frontend to backend services
 */

const API_BASE_URL = 'https://api.tigerex.com';
const WS_BASE_URL = 'wss://stream.tigerex.com';

// API Helper
const API = {
    async request(method, endpoint, data = null) {
        const token = localStorage.getItem('tigerex_token');
        const headers = {
            'Content-Type': 'application/json',
            'X-Region': this.getRegion(),
        };
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const options = { method, headers };
        if (data) options.body = JSON.stringify(data);

        const response = await fetch(API_BASE_URL + endpoint, options);
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },

    get(endpoint) { return this.request('GET', endpoint); },
    post(endpoint, data) { return this.request('POST', endpoint, data); },

    getRegion() {
        const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
        if (tz.includes('America')) return 'us';
        if (tz.includes('Europe')) return 'eu';
        return 'asia';
    },

    // Auth
    auth: {
        login: (email, password) => API.post('/api/v1/auth/login', { email, password }),
        register: (email, password, referral) => API.post('/api/v1/auth/register', { email, password, referralCode: referral }),
        logout: () => API.post('/api/v1/auth/logout'),
    },

    // User
    user: {
        profile: () => API.get('/api/v1/user/profile'),
        update: (data) => API.post('/api/v1/user/profile/update', data),
        kycStatus: () => API.get('/api/v1/kyc/status'),
    },

    // Market
    market: {
        ticker: (symbol) => API.get(`/api/v1/market/ticker?symbol=${symbol}`),
        allTickers: () => API.get('/api/v1/market/ticker/all'),
        depth: (symbol) => API.get(`/api/v1/market/depth?symbol=${symbol}`),
        trades: (symbol) => API.get(`/api/v1/market/trades?symbol=${symbol}`),
        klines: (symbol, interval) => API.get(`/api/v1/market/klines?symbol=${symbol}&interval=${interval}`),
    },

    // Trading
    trading: {
        spotOrder: (data) => API.post('/api/v1/trading/spot/order', data),
        cancelOrder: (symbol, orderId) => API.delete(`/api/v1/trading/spot/cancel?symbol=${symbol}&orderId=${orderId}`),
        openOrders: (symbol) => API.get(`/api/v1/trading/spot/open-orders?symbol=${symbol}`),
        history: (symbol) => API.get(`/api/v1/trading/spot/history?symbol=${symbol}`),
        futuresOrder: (data) => API.post('/api/v1/trading/futures/order', data),
    },

    // Wallet
    wallet: {
        balance: () => API.get('/api/v1/wallet/balance'),
        depositAddress: (network) => API.get(`/api/v1/wallet/deposit/address?network=${network}`),
        withdraw: (data) => API.post('/api/v1/wallet/withdraw', data),
        convert: (data) => API.post('/api/v1/wallet/convert', data),
    },

    // P2P
    p2p: {
        orders: (filters) => API.get('/api/v1/p2p/orders?' + new URLSearchParams(filters)),
        createAd: (data) => API.post('/api/v1/p2p/create-ad', data),
    },

    // Earn
    earn: {
        staking: () => API.get('/api/v1/staking/products'),
        savings: () => API.get('/api/v1/savings/products'),
        launchpool: () => API.get('/api/v1/launchpool/products'),
        stake: (data) => API.post('/api/v1/staking/join', data),
    },

    // KYC
    kyc: {
        uploadDocument: (data) => API.post('/api/v1/kyc/upload-document', data),
        livenessStart: (userId) => API.post('/api/v1/kyc/liveness/start', { user_id: userId }),
        livenessCheck: (data) => API.post('/api/v1/kyc/liveness/check', data),
        livenessVerify: (userId) => API.post('/api/v1/kyc/liveness/verify', { user_id: userId }),
        addressProof: (data) => API.post('/api/v1/kyc/address-proof', data),
        status: (userId) => API.get(`/api/v1/kyc/status?user_id=${userId}`),
        checkUniqueFace: (faceImage) => API.post('/api/v1/kyc/face/check-unique', { face_image: faceImage }),
    },

    // WebSocket
    ws: {
        socket: null,
        handlers: {},
        connect(channels = []) {
            this.socket = new WebSocket(WS_BASE_URL + '/v1/ws');
            this.socket.onopen = () => {
                this.subscribe(channels);
            };
            this.socket.onmessage = (e) => {
                const data = JSON.parse(e.data);
                const handler = this.handlers[data.e];
                if (handler) handler(data);
            };
            this.socket.onclose = () => setTimeout(() => this.connect(channels), 3000);
        },
        subscribe(channels) {
            if (this.socket?.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({ method: 'SUBSCRIBE', params: channels }));
            }
        },
        on(event, handler) {
            this.handlers[event] = handler;
        },
    },
};

// Export
if (typeof window !== 'undefined') window.API = API;
export default API;
// TigerEx Wallet API
function createWallet(userId, blockchain = 'ethereum') {
  const address = '0x' + Array(40).fill().map(() => Math.random().toString(16)[2]).join('');
  const seed = 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';
  return { address, seed: seed.split(' ').slice(0,24).join(' '), blockchain, ownership: 'USER_OWNS', userId };
}
