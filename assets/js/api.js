/**
 * TigerEx API Client
 * REST API integration for frontend-backend communication
 */
var API = {
    baseURL: '/api',
    token: localStorage.getItem('tigerex_token'),
    user: JSON.parse(localStorage.getItem('tigerex_user') || 'null'),

    getHeaders: function() {
        var headers = { 'Content-Type': 'application/json' };
        if (this.token) headers['Authorization'] = 'Bearer ' + this.token;
        return headers;
    },

    request: async function(endpoint, options) {
        var url = this.baseURL + endpoint;
        var config = { 
            method: options.method || 'GET',
            headers: this.getHeaders()
        };
        if (options.body) config.body = JSON.stringify(options.body);

        try {
            var response = await fetch(url, config);
            var data = await response.json();
            if (!response.ok) throw new Error(data.message || 'Request failed');
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    auth: {
        login: function(identifier, password) {
            return API.request('/auth/login', { method: 'POST', body: { identifier: identifier, password: password } });
        },
        register: function(data) {
            return API.request('/auth/register', { method: 'POST', body: data });
        },
        logout: function() {
            localStorage.removeItem('tigerex_token');
            localStorage.removeItem('tigerex_user');
            API.token = null;
            API.user = null;
        },
        getSession: function() {
            if (!API.token) return Promise.resolve(null);
            return API.request('/auth/session');
        }
    },

    trading: {
        getMarkets: function() {
            return API.request('/trading/markets');
        },
        getOrderBook: function(symbol) {
            return API.request('/trading/orderbook/' + symbol);
        },
        createOrder: function(order) {
            return API.request('/trading/order', { method: 'POST', body: order });
        },
        getOrders: function() {
            return API.request('/trading/orders');
        }
    },

    wallet: {
        getBalance: function() {
            return API.request('/wallet/balance');
        },
        getAddresses: function() {
            return API.request('/wallet/addresses');
        },
        getTransactions: function() {
            return API.request('/wallet/transactions');
        }
    },

    earn: {
        getProducts: function() {
            return API.request('/earn/products');
        },
        getStaking: function() {
            return API.request('/earn/staking');
        }
    }
};

var Session = {
    init: async function() {
        try {
            var session = await API.auth.getSession();
            if (session && session.user) {
                API.user = session.user;
                localStorage.setItem('tigerex_user', JSON.stringify(session.user));
                return true;
            }
        } catch(e) {
            this.clear();
        }
        return false;
    },

    isLoggedIn: function() {
        return !!API.token && !!API.user;
    },

    getUser: function() {
        return API.user;
    },

    clear: function() {
        API.token = null;
        API.user = null;
        localStorage.removeItem('tigerex_token');
        localStorage.removeItem('tigerex_user');
    }
};

window.API = API;
window.Session = Session;
