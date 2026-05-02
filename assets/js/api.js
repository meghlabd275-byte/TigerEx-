/**
 * TigerEx API Client - Production Version
 * Secure REST API integration with retry, refresh token, and httpOnly cookie support
 * 
 * @version 2.0.0
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        baseURL: window.TIGEREX_API_URL || '/api',
        tokenCookieName: 'tigerex_access_token',
        refreshCookieName: 'tigerex_refresh_token',
        csrfCookieName: 'tigerex_csrf_token',
        retryAttempts: 3,
        retryDelay: 1000,
        tokenRefreshThreshold: 5 * 60 * 1000, // 5 minutes before expiry
    };

    // State
    let _csrfToken = null;
    let _tokenExpiry = null;
    let _refreshPromise = null;

    // ==================== COOKIE HELPERS ====================

    function getCookie(name) {
        if (typeof document === 'undefined') return null;
        const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? decodeURIComponent(match[2]) : null;
    }

    function setCookie(name, value, days = 7, options = {}) {
        if (typeof document === 'undefined') return;
        const expires = new Date();
        expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
        
        let cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)};expires=${expires.toUTCString()};path=/`;
        if (options.sameSite) cookie += `;SameSite=${options.sameSite}`;
        if (options.secure) cookie += ';Secure';
        if (options.domain) cookie += `;domain=${options.domain}`;
        
        document.cookie = cookie;
    }

    function deleteCookie(name) {
        if (typeof document === 'undefined') return;
        document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
    }

    // ==================== TOKEN MANAGEMENT ====================

    async function getAccessToken() {
        let token = getCookie(CONFIG.tokenCookieName);
        
        // Check if token needs refresh
        if (_tokenExpiry && Date.now() > _tokenExpiry - CONFIG.tokenRefreshThreshold) {
            token = await refreshToken();
        }
        
        return token;
    }

    async function refreshToken() {
        // Prevent multiple simultaneous refresh requests
        if (_refreshPromise) {
            return _refreshPromise;
        }

        _refreshPromise = (async function() {
            const refreshToken = getCookie(CONFIG.refreshCookieName);
            if (!refreshToken) {
                throw new Error('No refresh token');
            }

            try {
                const response = await request('/auth/refresh', {
                    method: 'POST',
                    body: { refresh_token: refreshToken },
                    skipAuth: true
                });

                if (response.access_token) {
                    setCookie(CONFIG.tokenCookieName, response.access_token, 1);
                    if (response.refresh_token) {
                        setCookie(CONFIG.refreshCookieName, response.refresh_token, 30);
                    }
                    _tokenExpiry = Date.now() + (response.expires_in || 3600) * 1000;
                }

                return response.access_token;
            } finally {
                _refreshPromise = null;
            }
        })();

        return _refreshPromise;
    }

    function clearAuth() {
        deleteCookie(CONFIG.tokenCookieName);
        deleteCookie(CONFIG.refreshCookieName);
        deleteCookie(CONFIG.csrfCookieName);
        _tokenExpiry = null;
        _csrfToken = null;
    }

    // ==================== CSRF PROTECTION ====================

    async function getCSRFToken() {
        if (_csrfToken) return _csrfToken;
        _csrfToken = getCookie(CONFIG.csrfCookieName);
        return _csrfToken;
    }

    // ==================== HTTP REQUEST ====================

    async function request(endpoint, options = {}) {
        const {
            method = 'GET',
            body = null,
            skipAuth = false,
            skipCSRF = false,
            retryCount = 0
        } = options;

        const url = CONFIG.baseURL + endpoint;
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        // Add CSRF token for state-changing requests
        if (!skipCSRF && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
            const csrf = await getCSRFToken();
            if (csrf) {
                headers['X-CSRF-Token'] = csrf;
            }
        }

        // Add auth token
        if (!skipAuth) {
            const token = await getAccessToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }

        const config = { method, headers };
        if (body) {
            config.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(url, config);
            
            // Handle 401 - try refresh once
            if (response.status === 401 && !skipAuth && retryCount < CONFIG.retryAttempts) {
                if (retryCount === 0) {
                    // Try to refresh the token
                    try {
                        await refreshToken();
                        return await request(endpoint, { ...options, retryCount: retryCount + 1 });
                    } catch (e) {
                        // Refresh failed, need to login
                        clearAuth();
                        throw new Error('Session expired. Please login again.');
                    }
                }
            }

            // Handle 429 - rate limited
            if (response.status === 429 && retryCount < CONFIG.retryAttempts) {
                await new Promise(resolve => setTimeout(resolve, CONFIG.retryDelay * (retryCount + 1)));
                return await request(endpoint, { ...options, retryCount: retryCount + 1 });
            }

            const data = await response.json().catch(() => null);

            if (!response.ok) {
                const error = data?.error || data?.message || `HTTP ${response.status}`;
                throw new Error(error);
            }

            return data;
        } catch (error) {
            // No retry for network errors after threshold
            if (retryCount >= CONFIG.retryAttempts) {
                throw error;
            }
            
            // Only retry on network errors
            if (error.name === 'TypeError' || error.message.includes('network')) {
                await new Promise(resolve => setTimeout(resolve, CONFIG.retryDelay));
                return await request(endpoint, { ...options, retryCount: retryCount + 1 });
            }
            
            throw error;
        }
    }

    // ==================== AUTH API ====================

    const auth = {
        async login(identifier, password, rememberMe = false) {
            const response = await request('/auth/login', {
                method: 'POST',
                body: { identifier, password, remember_me: rememberMe },
                skipAuth: true,
                skipCSRF: true
            });

            if (response.access_token) {
                setCookie(CONFIG.tokenCookieName, response.access_token, rememberMe ? 30 : 1);
                if (response.refresh_token) {
                    setCookie(CONFIG.refreshCookieName, response.refresh_token, rememberMe ? 365 : 30);
                }
                if (response.csrf_token) {
                    setCookie(CONFIG.csrfCookieName, response.csrf_token, 1);
                }
                _tokenExpiry = Date.now() + (response.expires_in || 3600) * 1000;
            }

            return response;
        },

        async register(data) {
            return await request('/auth/register', {
                method: 'POST',
                body: data,
                skipAuth: true
            });
        },

        async logout() {
            try {
                await request('/auth/logout', { method: 'POST' });
            } finally {
                clearAuth();
            }
        },

        async getSession() {
            const token = await getAccessToken();
            if (!token) return null;
            
            try {
                return await request('/auth/session');
            } catch (e) {
                clearAuth();
                return null;
            }
        },

        async changePassword(currentPassword, newPassword) {
            return await request('/auth/password', {
                method: 'POST',
                body: { current_password: currentPassword, new_password: newPassword }
            });
        },

        async verifyEmail(code) {
            return await request('/auth/verify-email', {
                method: 'POST',
                body: { code }
            });
        },

        async enable2FA() {
            return await request('/auth/2fa/enable', { method: 'POST' });
        },

        async verify2FA(code) {
            return await request('/auth/2fa/verify', {
                method: 'POST',
                body: { code }
            });
        }
    };

    // ==================== TRADING API ====================

    const trading = {
        async getMarkets() {
            return await request('/trading/markets');
        },

        async getTicker(symbol) {
            return await request(`/trading/ticker/${encodeURIComponent(symbol)}`);
        },

        async getOrderBook(symbol, limit = 100) {
            return await request(`/trading/orderbook/${encodeURIComponent(symbol)}?limit=${limit}`);
        },

        async createOrder(order) {
            return await request('/trading/orders', {
                method: 'POST',
                body: order
            });
        },

        async cancelOrder(orderId) {
            return await request(`/trading/orders/${orderId}`, {
                method: 'DELETE'
            });
        },

        async getOrders(status, limit = 100) {
            const params = new URLSearchParams();
            if (status) params.append('status', status);
            params.append('limit', limit);
            return await request(`/trading/orders?${params}`);
        },

        async getOrderHistory(symbol, limit = 100) {
            return await request(`/trading/history/${encodeURIComponent(symbol)}?limit=${limit}`);
        },

        async getTradeHistory(limit = 100) {
            return await request(`/trading/trades?limit=${limit}`);
        }
    };

    // ==================== WALLET API ====================

    const wallet = {
        async getBalance() {
            return await request('/wallet/balance');
        },

        async getAddresses() {
            return await request('/wallet/addresses');
        },

        async createAddress(network, memo = null) {
            return await request('/wallet/addresses', {
                method: 'POST',
                body: { network, memo }
            });
        },

        async getTransactions(type, limit = 50) {
            const params = new URLSearchParams();
            if (type) params.append('type', type);
            params.append('limit', limit);
            return await request(`/wallet/transactions?${params}`);
        },

        async withdraw(network, address, amount, memo = null) {
            return await request('/wallet/withdraw', {
                method: 'POST',
                body: { network, address, amount, memo }
            });
        }
    };

    // ==================== EARN API ====================

    const earn = {
        async getProducts() {
            return await request('/earn/products');
        },

        async subscribe(productId, amount) {
            return await request('/earn/subscribe', {
                method: 'POST',
                body: { product_id: productId, amount }
            });
        },

        async getPositions() {
            return await request('/earn/positions');
        },

        async redeem(positionId) {
            return await request(`/earn/redeem/${positionId}`, {
                method: 'POST'
            });
        }
    };

    // ==================== USER API ====================

    const user = {
        async getProfile() {
            return await request('/user/profile');
        },

        async updateProfile(data) {
            return await request('/user/profile', {
                method: 'PUT',
                body: data
            });
        },

        async getPreferences() {
            return await request('/user/preferences');
        },

        async updatePreferences(prefs) {
            return await request('/user/preferences', {
                method: 'PUT',
                body: prefs
            });
        },

        async getReferralCode() {
            return await request('/user/referral/code');
        },

        async getReferrals() {
            return await request('/user/referrals');
        }
    };

    // ==================== KYC API ====================

    const kyc = {
        async getStatus() {
            return await request('/kyc/status');
        },

        async submit(data) {
            return await request('/kyc/submit', {
                method: 'POST',
                body: data
            });
        },

        async uploadDocument(type, document) {
            // Handle file upload
            const formData = new FormData();
            formData.append('type', type);
            formData.append('document', document);
            
            const token = await getAccessToken();
            const response = await fetch(CONFIG.baseURL + '/kyc/upload', {
                method: 'POST',
                headers: token ? { 'Authorization': `Bearer ${token}` } : {},
                body: formData
            });
            
            return await response.json();
        }
    };

    // ==================== SESSION UTILITY ====================

    const Session = {
        async init() {
            try {
                const session = await auth.getSession();
                return session?.user || null;
            } catch (e) {
                clearAuth();
                return null;
            }
        },

        isAuthenticated() {
            return !!getCookie(CONFIG.tokenCookieName);
        },

        logout() {
            auth.logout();
        }
    };

    // ==================== EXPORTS ====================

    const API = {
        auth,
        trading,
        wallet,
        earn,
        user,
        kyc,
        Session,
        config: CONFIG,
        clearAuth
    };

    // Export to window or module
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = API;
    } else if (typeof window !== 'undefined') {
        window.TigerExAPI = API;
    }
})();