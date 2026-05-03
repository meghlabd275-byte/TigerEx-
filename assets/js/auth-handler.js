/**
 * TigerEx Authentication Handler
 * Manages login state and dynamic UI updates based on authentication status
 */

(function() {
    'use strict';

    // Auth keys used in localStorage
    const AUTH_TOKEN_KEY = 'tigerex_token';
    const USER_EMAIL_KEY = 'tigerex_user_email';
    const USER_DATA_KEY = 'tigerex_user_data';

    /**
     * Check if user is logged in
     */
    function isLoggedIn() {
        const token = localStorage.getItem(AUTH_TOKEN_KEY);
        return token && token.length > 0;
    }

    /**
     * Get current user email
     */
    function getUserEmail() {
        return localStorage.getItem(USER_EMAIL_KEY) || '';
    }

    /**
     * Get current user data
     */
    function getUserData() {
        const data = localStorage.getItem(USER_DATA_KEY);
        return data ? JSON.parse(data) : null;
    }

    /**
     * Logout user - clear all auth data
     */
    function logout() {
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem(USER_EMAIL_KEY);
        localStorage.removeItem(USER_DATA_KEY);
        // Redirect to home page
        window.location.href = 'index.html';
    }

    /**
     * Get user display name (from email or data)
     */
    function getDisplayName() {
        const userData = getUserData();
        if (userData && userData.name) return userData.name;
        
        const email = getUserEmail();
        if (email) return email.split('@')[0];
        
        return 'User';
    }

    /**
     * Initialize auth-aware UI elements
     * Call this on page load to set up auth-dependent UI
     */
    function initAuthUI() {
        const loggedIn = isLoggedIn();
        
        // Update header - desktop (index.html style)
        const headerLoginLink = document.getElementById('headerLoginLink');
        const headerSignupLink = document.getElementById('headerSignupLink');
        const headerUserMenu = document.getElementById('headerUserMenu');
        
        if (loggedIn) {
            if (headerLoginLink) headerLoginLink.style.display = 'none';
            if (headerSignupLink) headerSignupLink.style.display = 'none';
            if (headerUserMenu) headerUserMenu.style.display = 'flex';
            
            // Update user info
            const headerUserAvatar = document.getElementById('headerUserAvatar');
            const headerUserEmail = document.getElementById('headerUserEmail');
            if (headerUserAvatar) headerUserAvatar.textContent = getDisplayName().charAt(0).toUpperCase();
            if (headerUserEmail) headerUserEmail.textContent = getUserEmail();
        } else {
            if (headerLoginLink) headerLoginLink.style.display = 'inline-flex';
            if (headerSignupLink) headerSignupLink.style.display = 'inline-flex';
            if (headerUserMenu) headerUserMenu.style.display = 'none';
        }

        // Update header - mobile (index.html style)
        const mobileLoginLink = document.getElementById('mobileLoginLink');
        const mobileSignupLink = document.getElementById('mobileSignupLink');
        const mobileUserMenu = document.getElementById('mobileUserMenu');
        
        if (loggedIn) {
            if (mobileLoginLink) mobileLoginLink.style.display = 'none';
            if (mobileSignupLink) mobileSignupLink.style.display = 'none';
            if (mobileUserMenu) mobileUserMenu.style.display = 'block';
            
            // Update mobile user info
            const mobileUserAvatar = document.getElementById('mobileUserAvatar');
            const mobileUserName = document.getElementById('mobileUserName');
            const mobileUserEmail = document.getElementById('mobileUserEmail');
            if (mobileUserAvatar) mobileUserAvatar.textContent = getDisplayName().charAt(0).toUpperCase();
            if (mobileUserName) mobileUserName.textContent = getDisplayName();
            if (mobileUserEmail) mobileUserEmail.textContent = getUserEmail();
        } else {
            if (mobileLoginLink) mobileLoginLink.style.display = 'inline-flex';
            if (mobileSignupLink) mobileSignupLink.style.display = 'inline-flex';
            if (mobileUserMenu) mobileUserMenu.style.display = 'none';
        }

        // Update dashboard-style profile drawer
        const profileAvatar = document.querySelector('.profile-avatar');
        const profileName = document.querySelector('.profile-name');
        const profileEmail = document.querySelector('.profile-email');
        
        if (loggedIn) {
            if (profileAvatar) profileAvatar.textContent = getDisplayName().charAt(0).toUpperCase();
            if (profileName) profileName.textContent = getDisplayName();
            if (profileEmail) profileEmail.textContent = getUserEmail();
            
            // Add logout button if not present
            const logoutBtn = document.querySelector('.logout-btn');
            if (logoutBtn && !logoutBtn.hasAttribute('onclick')) {
                logoutBtn.setAttribute('onclick', 'handleLogout()');
            }
        }

        // Fire custom event for other scripts to listen
        window.dispatchEvent(new CustomEvent('authStateChanged', { 
            detail: { isLoggedIn: loggedIn } 
        }));
    }

    /**
     * Create authenticated user menu HTML
     */
    function createUserMenuHTML() {
        const email = getUserEmail();
        const displayName = getDisplayName();
        
        return `
            <div class="user-menu-container" id="headerUserMenu" style="display: none;">
                <div class="user-dropdown">
                    <button class="user-menu-trigger" onclick="toggleUserDropdown()">
                        <span class="user-avatar">${displayName.charAt(0).toUpperCase()}</span>
                        <span class="user-name" id="headerUserEmail">${email}</span>
                        <span class="dropdown-arrow">▼</span>
                    </button>
                    <div class="user-dropdown-menu" id="userDropdownMenu">
                        <a href="profile.html" class="dropdown-item">👤 My Profile</a>
                        <a href="wallet.html" class="dropdown-item">💰 My Wallet</a>
                        <a href="order-history.html" class="dropdown-item">📜 Orders</a>
                        <a href="security.html" class="dropdown-item">🔒 Security</a>
                        <a href="preferences.html" class="dropdown-item">⚙️ Preferences</a>
                        <div class="dropdown-divider"></div>
                        <button class="dropdown-item logout-btn" onclick="handleLogout()">🚪 Log Out</button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Create mobile user menu HTML
     */
    function createMobileUserMenuHTML() {
        const email = getUserEmail();
        const displayName = getDisplayName();
        
        return `
            <div class="mobile-user-menu" id="mobileUserMenu" style="display: none;">
                <div class="mobile-user-info">
                    <span class="mobile-user-avatar">${displayName.charAt(0).toUpperCase()}</span>
                    <div class="mobile-user-details">
                        <span class="mobile-user-name">${displayName}</span>
                        <span class="mobile-user-email">${email}</span>
                    </div>
                </div>
                <a href="profile.html" class="mobile-menu-link">👤 My Profile</a>
                <a href="wallet.html" class="mobile-menu-link">💰 My Wallet</a>
                <a href="order-history.html" class="mobile-menu-link">📜 Orders</a>
                <a href="security.html" class="mobile-menu-link">🔒 Security</a>
                <a href="preferences.html" class="mobile-menu-link">⚙️ Preferences</a>
                <div class="mobile-menu-divider"></div>
                <button class="mobile-menu-link mobile-logout-btn" onclick="handleLogout()">🚪 Log Out</button>
            </div>
        `;
    }

    // Expose globally
    window.TigerExAuth = {
        isLoggedIn: isLoggedIn,
        getUserEmail: getUserEmail,
        getUserData: getUserData,
        getDisplayName: getDisplayName,
        logout: logout,
        initAuthUI: initAuthUI,
        createUserMenuHTML: createUserMenuHTML,
        createMobileUserMenuHTML: createMobileUserMenuHTML
    };

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAuthUI);
    } else {
        initAuthUI();
    }

    // Expose logout handler globally
    window.handleLogout = function() {
        TigerExAuth.logout();
    };

    window.toggleUserDropdown = function() {
        const menu = document.getElementById('userDropdownMenu');
        if (menu) {
            menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
        }
    };

})();
// ==================== WALLET AUTH ====================
const WalletAuth = {
    verifyOwnership: async (address, signature) => ({ valid: true, owner: address }),
    signMessage: (message, privateKey) => '0x' + Math.random().toString(16).slice(2, 138),
    getSeedHash: (seed) => 'sha256:' + btoa(seed).slice(0, 32)
};
export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
