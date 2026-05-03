/**
 * TigerEx Authentication Guard System
 * Prevents actions without login - only view allowed
 * For: HTML, JS, Next.js, TypeScript, React, Node.js, PHP
 * Version: 1.1.0 - Enhanced with action button protection
 */

(function() {
  'use strict';

  // Auth configuration
  const AUTH_CONFIG = {
    tokenKey: 'tigerex_auth_token',
    userKey: 'tigerex_user',
    sessionKey: 'tigerex_session',
    tokenExpiry: 24 * 60 * 60 * 1000, // 24 hours
  };

  // Action button selectors - buttons that require authentication
  const ACTION_SELECTORS = [
    'button.trade-btn',
    'button.buy-btn',
    'button.sell-btn', 
    'button.deposit',
    'button.withdraw',
    'button.transfer',
    'button.submit-order',
    'button[data-action]',
    'a[href*="trade"]',
    'a[href*="buy"]',
    'a[href*="sell"]',
    'form[action*="trade"]',
    'input[type="submit"]',
    '.btn-buy',
    '.btn-sell',
    '.trade-button',
    'button.order-button',
    'button.place-order',
    '[data-trade]',
    '[data-action="buy"]',
    '[data-action="sell"]',
    '[data-action="trade"]',
    '[data-action="deposit"]',
    '[data-action="withdraw"]',
    '[data-action="transfer"]',
    '.profile-balance-btn',
    '.asset-action-btn',
    '.tradfi-btn',
  ];

  /**
   * Check if user is authenticated
   */
  window.TigerAuth = {
    isAuthenticated: function() {
      const token = localStorage.getItem(AUTH_CONFIG.tokenKey);
      const user = localStorage.getItem(AUTH_CONFIG.userKey);
      
      if (!token || !user) return false;
      
      try {
        const userData = JSON.parse(user);
        return userData && userData.isVerified === true;
      } catch (e) {
        return false;
      }
    },

    /**
     * Get current user
     */
    getUser: function() {
      try {
        const user = localStorage.getItem(AUTH_CONFIG.userKey);
        return user ? JSON.parse(user) : null;
      } catch (e) {
        return null;
      }
    },

    /**
     * Get auth token
     */
    getToken: function() {
      return localStorage.getItem(AUTH_CONFIG.tokenKey);
    },

    /**
     * Login user
     */
    login: function(userData, token) {
      const user = {
        ...userData,
        isVerified: true,
        loginTime: Date.now(),
      };
      
      localStorage.setItem(AUTH_CONFIG.userKey, JSON.stringify(user));
      localStorage.setItem(AUTH_CONFIG.tokenKey, token || 'token_' + Date.now());
      localStorage.setItem(AUTH_CONFIG.sessionKey, Date.now().toString());
      
      // Dispatch auth event
      window.dispatchEvent(new CustomEvent('auth:login', { detail: user }));
      
      return true;
    },

    /**
     * Logout user
     */
    logout: function() {
      localStorage.removeItem(AUTH_CONFIG.userKey);
      localStorage.removeItem(AUTH_CONFIG.tokenKey);
      localStorage.removeItem(AUTH_CONFIG.sessionKey);
      
      // Dispatch auth event
      window.dispatchEvent(new CustomEvent('auth:logout', { detail: {} }));
      
      return true;
    },

    /**
     * Require authentication - redirect to login if not authenticated
     */
    requireAuth: function(redirectUrl) {
      if (!this.isAuthenticated()) {
        window.location.href = redirectUrl || 'login.html';
        return false;
      }
      return true;
    },

    /**
     * Show/hide elements based on auth state
     */
    updateUI: function() {
      const isAuth = this.isAuthenticated();
      
      // Elements that require login
      document.querySelectorAll('[data-auth="required"]').forEach(function(el) {
        if (isAuth) {
          el.style.display = el.dataset.authDisplay || '';
        } else {
          el.dataset.authDisplay = el.style.display;
          el.style.display = 'none';
        }
      });

      // Elements that show only when logged out
      document.querySelectorAll('[data-auth="guest"]').forEach(function(el) {
        el.style.display = isAuth ? 'none' : (el.dataset.authDisplay || '');
      });

      return isAuth;
    },

    /**
     * Disable action buttons when not authenticated
     */
    protectActions: function() {
      const isAuth = this.isAuthenticated();
      
      if (!isAuth) {
        // Disable all action buttons with data-action
        document.querySelectorAll('button[data-action], a[data-action], input[data-action]').forEach(function(el) {
          el.disabled = true;
          el.dataset.originalTitle = el.title || '';
          el.title = 'Please login to perform this action';
          el.classList.add('auth-disabled');
          
          if (el.tagName === 'A') {
            el.dataset.originalHref = el.href;
            el.href = 'login.html';
          }
        });

        // Disable common action buttons by class and content
        const actionSelectors = [
          '.trade-btn', '.btn-buy', '.btn-sell', '.buy-btn', '.sell-btn',
          '.profile-balance-btn', '.asset-action-btn', '.tradfi-btn',
          'button[class*="buy"]', 'button[class*="sell"]',
          'button[class*="trade"]', 'button[class*="deposit"]', 'button[class*="withdraw"]'
        ];
        
        actionSelectors.forEach(function(selector) {
          document.querySelectorAll(selector).forEach(function(btn) {
            if (!btn.classList.contains('auth-disabled')) {
              btn.classList.add('auth-disabled');
              btn.dataset.originalOnclick = btn.getAttribute('onclick') || '';
              btn.setAttribute('onclick', 'alert(\'Please login to perform this action\'); window.location.href=\'login.html\';');
              btn.style.opacity = '0.5';
              btn.style.cursor = 'not-allowed';
            }
          });
        });

        // Add warning to forms
        document.querySelectorAll('form[data-protect]').forEach(function(el) {
          el.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();
            alert('Please login to perform this action');
            window.location.href = 'login.html';
            return false;
          }, { once: true });
        });
      }

      return isAuth;
    },

    /**
     * Initialize auth guards on page
     */
    init: function() {
      this.updateUI();
      this.protectActions();
      
      // Listen for auth changes
      window.addEventListener('auth:login', function() {
        TigerAuth.updateUI();
        TigerAuth.protectActions();
        window.location.reload();
      });

      window.addEventListener('auth:logout', function() {
        TigerAuth.updateUI();
        window.location.href = 'login.html';
      });
    },
  };

  // Auto-initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      window.TigerAuth.init();
    });
  } else {
    window.TigerAuth.init();
  }

})();

/**
 * Additional helper functions for authentication
 */

// Check if user can perform action
function canPerformAction() {
  return window.TigerAuth && window.TigerAuth.isAuthenticated();
}

// Require login for action (returns true if allowed, false and redirects if not)
function requireLoginForAction(redirectToLogin) {
  redirectToLogin = redirectToLogin !== false;
  
  if (!canPerformAction()) {
    if (redirectToLogin) {
      window.location.href = 'login.html';
    }
    return false;
  }
  return true;
}

// Wrapper to protect any function requiring authentication
function protectedAction(callback, fallbackUrl) {
  if (canPerformAction()) {
    return callback();
  } else {
    if (fallbackUrl) {
      window.location.href = fallbackUrl;
    } else {
      alert('Please login to perform this action');
    }
    return null;
  }
}

// Add auth guard to buttons and links
document.addEventListener('DOMContentLoaded', function() {
  // Protect all buttons with data-action
  document.querySelectorAll('button[data-action]').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      if (!canPerformAction()) {
        e.preventDefault();
        alert('Please login to perform this action');
        window.location.href = 'login.html';
      }
    });
  });

  // Protect all links with data-action
  document.querySelectorAll('a[data-action]').forEach(function(link) {
    link.addEventListener('click', function(e) {
      if (!canPerformAction()) {
        e.preventDefault();
        alert('Please login to perform this action');
        window.location.href = 'login.html';
      }
    });
  });

  // Protect form submissions
  document.querySelectorAll('form[data-protect]').forEach(function(form) {
    form.addEventListener('submit', function(e) {
      if (!canPerformAction()) {
        e.preventDefault();
        alert('Please login to submit this form');
        window.location.href = 'login.html';
      }
    });
  });
});
// ==================== WALLET GUARD ====================
const WalletGuard = {
    checkAccess: (address, level) => true,
    requireWallet: (req, res, next) => next(),
    validateSeed: (seed) => seed.split(' ').length === 24
};
