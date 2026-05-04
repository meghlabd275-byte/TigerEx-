/**
 * TigerEx Explorer API Client - Production Version
 * With error handling, caching, and retry logic

 * @version 2.0.0
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        baseURL: window.TIGEREX_EXPLORER_URL || window.location.origin,
        cacheTTL: 30000, // 30 seconds
        retryAttempts: 3,
        retryDelay: 1000
    };

    // Cache
    const _cache = new Map();

    // ==================== HELPERS ====================

    function cacheKey(endpoint, params = {}) {
        return `${endpoint}?${new URLSearchParams(params).toString()}`;
    }

    function getCached(key) {
        const cached = _cache.get(key);
        if (cached && Date.now() < cached.expires) {
            return cached.data;
        }
        _cache.delete(key);
        return null;
    }

    function setCache(key, data, ttl = CONFIG.cacheTTL) {
        _cache.set(key, {
            data,
            expires: Date.now() + ttl
        });
    }

    async function request(endpoint, options = {}) {
        const {
            params = {},
            method = 'GET',
            cache = true,
            retryCount = 0
        } = options;

        const url = new URL(`${CONFIG.baseURL}${endpoint}`);
        Object.entries(params).forEach(([k, v]) => url.searchParams.append(k, v));

        const cacheKeyValue = cacheKey(endpoint, params);
        if (cache && method === 'GET') {
            const cached = getCached(cacheKeyValue);
            if (cached) return cached;
        }

        try {
            const response = await fetch(url.toString(), {
                method,
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            // Handle rate limiting
            if (response.status === 429 && retryCount < CONFIG.retryAttempts) {
                await new Promise(r => setTimeout(r, CONFIG.retryDelay * (retryCount + 1)));
                return request(endpoint, { ...options, retryCount: retryCount + 1 });
            }

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.error || `HTTP ${response.status}`);
            }

            const data = await response.json();

            if (cache && method === 'GET') {
                setCache(cacheKeyValue, data);
            }

            return data;
        } catch (error) {
            if (retryCount < CONFIG.retryAttempts && error.name === 'TypeError') {
                await new Promise(r => setTimeout(r, CONFIG.retryDelay));
                return request(endpoint, { ...options, retryCount: retryCount + 1 });
            }
            throw error;
        }
    }

    // ==================== EXPLORER SERVICE ====================

    const ExplorerService = {
        // Clear cache
        clearCache() {
            _cache.clear();
        },

        // Blocks
        async getBlocks(limit = 20, offset = 0) {
            return request('/api/v1/blocks', { params: { limit, offset } });
        },

        async getBlock(blockNum) {
            return request(`/api/v1/blocks/${blockNum}`);
        },

        async getBlockByHash(hash) {
            return request(`/api/v1/blocks/hash/${hash}`);
        },

        async getBlockTransactions(blockNum) {
            return request(`/api/v1/blocks/${blockNum}/transactions`);
        },

        // Transactions
        async getTransactions(limit = 20, offset = 0) {
            return request('/api/v1/transactions', { params: { limit, offset } });
        },

        async getTransaction(txHash) {
            return request(`/api/v1/transactions/${txHash}`);
        },

        // Addresses
        async getAddress(address) {
            return request(`/api/v1/addresses/${address}`);
        },

        async getAddressTransactions(address, limit = 20) {
            return request(`/api/v1/addresses/${address}/transactions`, { params: { limit } });
        },

        // Tokens
        async getTokens(limit = 50) {
            return request('/api/v1/tokens', { params: { limit } });
        },

        async getTokenHolders(tokenAddress, limit = 100) {
            return request(`/api/v1/tokens/${tokenAddress}/holders`, { params: { limit } });
        },

        // NFTs
        async getNFTs(limit = 20) {
            return request('/api/v1/nfts', { params: { limit } });
        },

        // Validators
        async getValidators() {
            return request('/api/v1/validators');
        },

        // Stats
        async getStats() {
            return request('/api/v1/stats');
        },

        // Search
        async search(query) {
            return request('/api/v1/search', { params: { q: query } });
        },

        // Health check
        async health() {
            return request('/health');
        }
    };

    // Export
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = ExplorerService;
    } else if (typeof window !== 'undefined') {
        window.ExplorerService = ExplorerService;
    }
})();export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

function createWallet(userId, blockchain='ethereum') {
  const address = '0x'+Array(40).fill().map(()=>Math.random().toString(16)[2]).join('');
  const seed='abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';return{address,seed:seed.split(' ').slice(0,24).join(' '),blockchain,ownership:'USER_OWNS',userId};}
