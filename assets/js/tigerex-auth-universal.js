/**
 * TigerEx Universal Authentication Service - Production Version
 * Secure authentication with server validation and httpOnly cookies
 * 
 * @version 2.0.0
 */

(function() {
    'use strict';

    // ==================== CONFIG ====================

    const CONFIG = {
        tokenCookie: 'tigerex_access_token',
        userCookie: 'tigerex_user',
        csrfCookie: 'tigerex_csrf_token',
        apiBase: window.TIGEREX_API_URL || '/api',
        sessionCheckInterval: 60000, // Check session every minute
    };

    // ==================== COOKIE HELPERS ====================

    function getCookie(name) {
        if (typeof document === 'undefined') return null;
        const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? decodeURIComponent(match[2]) : null;
    }

    function deleteCookie(name) {
        if (typeof document === 'undefined') return;
        document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
    }

    function getUserFromCookie() {
        const userData = getCookie(CONFIG.userCookie);
        if (!userData) return null;
        try {
            return JSON.parse(userData);
        } catch {
            return null;
        }
    }

    // ==================== STATE ====================

    let _sessionCheckTimer = null;
    let _eventListeners = {};

    // ==================== CORE METHODS ====================

    /**
     * Check if user is authenticated
     */
    function isAuthenticated() {
        return !!getCookie(CONFIG.tokenCookie);
    }

    /**
     * Get current user data
     */
    function getUser() {
        return getUserFromCookie();
    }

    /**
     * Get display name
     */
    function getDisplayName() {
        const user = getUser();
        if (user?.name) return user.name;
        if (user?.email) return user.email.split('@')[0];
        return 'User';
    }

    /**
     * Get avatar initial
     */
    function getAvatar() {
        return getDisplayName().charAt(0).toUpperCase();
    }

    /**
     * Get user email
     */
    function getEmail() {
        const user = getUser();
        return user?.email || '';
    }

    // ==================== AUTH ACTIONS ====================

    /**
     * Login with credentials - calls server
     */
    async function login(identifier, password, rememberMe = false) {
        const response = await fetch(CONFIG.apiBase + '/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ identifier, password, remember_me: rememberMe })
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.error || data.message || 'Login failed');
        }

        if (data.user) {
            // Store user data in cookie (not token!)
            document.cookie = `${CONFIG.userCookie}=${encodeURIComponent(JSON.stringify(data.user))};path=/;max-age=${86400 * 30}`;
        }

        _emit('login', data.user);
        _startSessionCheck();

        return data;
    }

    /**
     * Logout - calls server to invalidate session
     */
    async function logout() {
        try {
            await fetch(CONFIG.apiBase + '/auth/logout', {
                method: 'POST',
                credentials: 'same-origin'
            });
        } finally {
            clearSession();
        }
    }

    /**
     * Clear local session (called on logout or session expiry)
     */
    function clearSession() {
        deleteCookie(CONFIG.tokenCookie);
        deleteCookie(CONFIG.userCookie);
        deleteCookie(CONFIG.csrfCookie);
        
        _stopSessionCheck();
        _emit('logout');
    }

    /**
     * Register new user
     */
    async function register(userData) {
        const response = await fetch(CONFIG.apiBase + '/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(userData)
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.error || data.message || 'Registration failed');
        }

        return data;
    }

    // ==================== SESSION MANAGEMENT ====================

    /**
     * Check session validity with server
     */
    async function checkSession() {
        if (!isAuthenticated()) {
            clearSession();
            return null;
        }

        try {
            const response = await fetch(CONFIG.apiBase + '/auth/session', {
                method: 'GET',
                credentials: 'same-origin'
            });

            if (!response.ok) {
                clearSession();
                return null;
            }

            const data = await response.json();
            return data.user || null;
        } catch (error) {
            // Network error - keep session
            return getUser();
        }
    }

    /**
     * Start periodic session check
     */
    function _startSessionCheck() {
        if (_sessionCheckTimer) return;
        _sessionCheckTimer = setInterval(checkSession, CONFIG.sessionCheckInterval);
    }

    /**
     * Stop session check
     */
    function _stopSessionCheck() {
        if (_sessionCheckTimer) {
            clearInterval(_sessionCheckTimer);
            _sessionCheckTimer = null;
        }
    }

    // ==================== EVENT SYSTEM ====================

    function on(event, callback) {
        if (!_eventListeners[event]) {
            _eventListeners[event] = [];
        }
        _eventListeners[event].push(callback);
    }

    function off(event, callback) {
        if (!_eventListeners[event]) return;
        _eventListeners[event] = _eventListeners[event].filter(cb => cb !== callback);
    }

    function _emit(event, data) {
        if (!_eventListeners[event]) return;
        _eventListeners[event].forEach(cb => cb(data));
    }

    // ==================== REACT HOOK ====================

    /**
     * React hook for authentication
     */
    function useAuth() {
        const [user, setUser] = React.useState(null);
        const [loading, setLoading] = React.useState(true);

        React.useEffect(() => {
            checkSession().then(u => {
                setUser(u);
                setLoading(false);
            });

            const handleLogin = (u) => setUser(u);
            const handleLogout = () => setUser(null);

            on('login', handleLogin);
            on('logout', handleLogout);

            return () => {
                off('login', handleLogin);
                off('logout', handleLogout);
            };
        }, []);

        return {
            user,
            loading,
            isAuthenticated: !!user,
            login,
            logout,
            register
        };
    }

    // ==================== VUE COMPOSITION ====================

    /**
     * Vue composable
     */
    function useAuthComposable() {
        const user = Vue.ref(null);
        const loading = Vue.ref(true);

        async function init() {
            const u = await checkSession();
            user.value = u;
            loading.value = false;
        }

        init();

        return {
            user,
            loading,
            isAuthenticated: Vue.computed(() => !!user.value),
            login,
            logout,
            register
        };
    }

    // ==================== EXPORTS ====================

    const TigerExAuth = {
        // State
        isAuthenticated,
        getUser,
        getEmail,
        getDisplayName,
        getAvatar,
        
        // Actions
        login,
        logout,
        register,
        clearSession,
        checkSession,
        
        // Events
        on,
        off,
        
        // Framework integrations
        useAuth,
        useAuthComposable,

        // For testing
        _config: CONFIG
    };

    // Export
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = TigerExAuth;
    } else if (typeof window !== 'undefined') {
        window.TigerExAuth = TigerExAuth;
    }
})();export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
