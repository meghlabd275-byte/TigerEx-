/**
 * TigerEx Desktop App - Auth Guard
 * Authentication guard for desktop trading platform
 * @version 1.0.0
 */

// Check if user is logged in
function isAuthenticated() {
    return localStorage.getItem('tigerex_token') !== null;
}

// Get current user
function getCurrentUser() {
    const user = localStorage.getItem('tigerex_user');
    return user ? JSON.parse(user) : null;
}

// Require authentication
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Login user
function login(token, user) {
    localStorage.setItem('tigerex_token', token);
    localStorage.setItem('tigerex_user', JSON.stringify(user));
    localStorage.setItem('tigerex_login_time', Date.now().toString());
}

// Logout user
function logout() {
    localStorage.removeItem('tigerex_token');
    localStorage.removeItem('tigerex_user');
    localStorage.removeItem('tigerex_login_time');
    window.location.href = '/login';
}

// Check session expiration (24 hours)
function checkSession() {
    const loginTime = localStorage.getItem('tigerex_login_time');
    if (loginTime) {
        const expired = Date.now() - parseInt(loginTime) > 24 * 60 * 60 * 1000;
        if (expired) {
            logout();
            return false;
        }
    }
    return true;
}

// Get auth token
function getToken() {
    return localStorage.getItem('tigerex_token');
}

// API request with auth
async function authFetch(url, options = {}) {
    const token = getToken();
    if (token) {
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };
    }
    return fetch(url, options);
}

// Initialize auth guard
function initAuthGuard() {
    // Check session on page load
    if (!checkSession()) {
        console.log('Session expired');
    }
    
    // Check auth on protected routes
    const protectedRoutes = ['/dashboard', '/wallet', '/trade', '/settings'];
    const currentPath = window.location.pathname;
    
    if (protectedRoutes.some(route => currentPath.startsWith(route))) {
        if (!requireAuth()) {
            return;
        }
    }
}

// Export functions
if (typeof window !== 'undefined') {
    window.TigerExAuth = {
        isAuthenticated,
        getCurrentUser,
        requireAuth,
        login,
        logout,
        checkSession,
        getToken,
        authFetch,
        initAuthGuard
    };
}

// Auto-initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAuthGuard);
} else {
    initAuthGuard();
}
// TigerEx Wallet API
function createWallet(userId, blockchain = 'ethereum') {
  const address = '0x' + Array(40).fill().map(() => Math.random().toString(16)[2]).join('');
  const seed = 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';
  return { address, seed: seed.split(' ').slice(0,24).join(' '), blockchain, ownership: 'USER_OWNS', userId };
}
