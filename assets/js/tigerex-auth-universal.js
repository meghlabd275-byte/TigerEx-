/**
 * TigerEx Universal Authentication Service
 * Works across: React, Next.js, Vue, Angular, React Native, Node.js, PHP, ASP, Electron, and more
 * 
 * @version 1.0.0
 * @description Unified authentication for all TigerEx platforms
 */

'use strict';

// ============================================================================
// AUTH CONFIGURATION
// ============================================================================

const AUTH_CONFIG = {
    TOKEN_KEY: 'tigerex_token',
    USER_EMAIL_KEY: 'tigerex_user_email',
    USER_DATA_KEY: 'tigerex_user_data',
    REFRESH_TOKEN_KEY: 'tigerex_refresh_token',
    EXPIRY_KEY: 'tigerex_token_expiry',
    TOKEN_EXPIRY_HOURS: 24,
};

// ============================================================================
// BROADCAST CHANNEL FOR CROSS-TAB SYNC
// ============================================================================

let authChannel = null;
if (typeof window !== 'undefined' && typeof BroadcastChannel !== 'undefined') {
    authChannel = new BroadcastChannel('tigerex_auth');
    authChannel.onmessage = (event) => {
        if (event.data.type === 'LOGOUT') {
            logout();
        } else if (event.data.type === 'LOGIN') {
            setUserData(event.data.user);
        }
    };
}

// ============================================================================
// CORE AUTH METHODS
// ============================================================================

/**
 * Check if user is logged in
 * @returns {boolean}
 */
function isLoggedIn() {
    const token = getToken();
    if (!token) return false;
    
    // Check expiry
    const expiry = localStorage.getItem(AUTH_CONFIG.EXPIRY_KEY);
    if (expiry && new Date(expiry) < new Date()) {
        logout();
        return false;
    }
    
    return true;
}

/**
 * Get stored authentication token
 * @returns {string|null}
 */
function getToken() {
    if (typeof localStorage !== 'undefined') {
        return localStorage.getItem(AUTH_CONFIG.TOKEN_KEY);
    }
    return null;
}

/**
 * Get current user email
 * @returns {string}
 */
function getUserEmail() {
    if (typeof localStorage !== 'undefined') {
        return localStorage.getItem(AUTH_CONFIG.USER_EMAIL_KEY) || '';
    }
    return '';
}

/**
 * Get current user data
 * @returns {object|null}
 */
function getUserData() {
    if (typeof localStorage !== 'undefined') {
        const data = localStorage.getItem(AUTH_CONFIG.USER_DATA_KEY);
        return data ? JSON.parse(data) : null;
    }
    return null;
}

/**
 * Get user display name
 * @returns {string}
 */
function getDisplayName() {
    const userData = getUserData();
    if (userData && userData.name) return userData.name;
    
    const email = getUserEmail();
    if (email) return email.split('@')[0];
    
    return 'User';
}

/**
 * Get user avatar initial
 * @returns {string}
 */
function getUserAvatar() {
    return getDisplayName().charAt(0).toUpperCase();
}

// ============================================================================
// AUTH ACTIONS
// ============================================================================

/**
 * Perform login with credentials
 * @param {object} user - User data object
 * @param {string} user.email - User email
 * @param {string} user.name - Optional display name
 * @returns {boolean}
 */
function login(user) {
    if (!user || !user.email) return false;
    
    const token = 'tigerex_token_' + Date.now();
    const expiry = new Date();
    expiry.setHours(expiry.getHours() + AUTH_CONFIG.TOKEN_EXPIRY_HOURS);
    
    if (typeof localStorage !== 'undefined') {
        localStorage.setItem(AUTH_CONFIG.TOKEN_KEY, token);
        localStorage.setItem(AUTH_CONFIG.USER_EMAIL_KEY, user.email);
        localStorage.setItem(AUTH_CONFIG.USER_DATA_KEY, JSON.stringify(user));
        localStorage.setItem(AUTH_CONFIG.EXPIRY_KEY, expiry.toISOString());
    }
    
    // Broadcast to other tabs
    if (authChannel) {
        authChannel.postMessage({ type: 'LOGIN', user });
    }
    
    return true;
}

/**
 * Perform logout
 */
function logout() {
    if (typeof localStorage !== 'undefined') {
        localStorage.removeItem(AUTH_CONFIG.TOKEN_KEY);
        localStorage.removeItem(AUTH_CONFIG.USER_EMAIL_KEY);
        localStorage.removeItem(AUTH_CONFIG.USER_DATA_KEY);
        localStorage.removeItem(AUTH_CONFIG.REFRESH_TOKEN_KEY);
        localStorage.removeItem(AUTH_CONFIG.EXPIRY_KEY);
    }
    
    // Broadcast to other tabs
    if (authChannel) {
        authChannel.postMessage({ type: 'LOGOUT' });
    }
}

// ============================================================================
// REDUX/REACT HOOK
// ============================================================================

/**
 * React hook for authentication state
 * @returns {object} Auth state and methods
 */
function useAuth() {
    if (typeof window === 'undefined') {
        return { isLoggedIn: false, user: null, login: () => {}, logout: () => {} };
    }
    
    // Simple state tracking
    const [, setState] = React?.useState?.(0) || [0, () => {}];
    
    React?.useEffect?.(() => {
        const handler = () => setState(s => s + 1);
        window.addEventListener('authStateChanged', handler);
        return () => window.removeEventListener('authStateChanged', handler);
    }, []);
    
    return {
        isLoggedIn: isLoggedIn(),
        user: getUserData(),
        email: getUserEmail(),
        name: getDisplayName(),
        avatar: getUserAvatar(),
        login,
        logout,
    };
}

// ============================================================================
// VUE COMPOSITION API
// ============================================================================

/**
 * Vue composable for authentication
 * @returns {object}
 */
function useAuthComposable() {
    const isLoggedIn = Vue?.ref?.(false) || { value: false };
    const user = Vue?.ref?.(null);
    
    if (typeof window !== 'undefined') {
        const check = () => {
            isLoggedIn.value = window.TigerExAuth?.isLoggedIn?.() || isLoggedIn();
            user.value = window.TigerExAuth?.getUserData?.() || getUserData();
        };
        
        window.addEventListener('authStateChanged', check);
        check();
    }
    
    return {
        isLoggedIn,
        user,
        login: (userData) => login(userData),
        logout: () => logout(),
    };
}

// ============================================================================
// ANGULAR SERVICE
// ============================================================================

/**
 * Angular Authentication Service
 * @Injectable()
 */
const TigerExAuthService = {
    isLoggedIn: () => isLoggedIn(),
    getUser: () => getUserData(),
    getEmail: () => getUserEmail(),
    login: (user) => login(user),
    logout: () => logout(),
};

// ============================================================================
// REACT NATIVE
// ============================================================================

/**
 * React Native auth hooks
 */
const ReactNativeAuth = {
    isLoggedIn,
    getUser: getUserData,
    login,
    logout,
};

// ============================================================================
// NODE.JS/EXPRESS MIDDLEWARE
// ============================================================================

/**
 * Express middleware for protected routes
 * @param {object} req - Express request
 * @param {object} res - Express response  
 * @param {function} next - Express next
 */
function authMiddleware(req, res, next) {
    const token = req.headers.authorization?.replace('Bearer ', '') || req.cookies?.tigerex_token;
    
    if (!token) {
        return res.status(401).json({ error: 'No token provided' });
    }
    
    // Verify token (in real app, validate with server)
    if (token.startsWith('tigerex_token_')) {
        req.user = getUserData();
        return next();
    }
    
    return res.status(401).json({ error: 'Invalid token' });
}

// ============================================================================
// PHP IMPLEMENTATION
// ============================================================================

/**
 * PHP Auth Class - Returns template code
 */
const phpAuthTemplate = `<?php
/**
 * TigerEx PHP Authentication
 */

class TigerExAuth {
    private static $tokenKey = 'tigerex_token';
    private static $userKey = 'tigerex_user';
    
    public static function isLoggedIn() {
        return isset($_SESSION[self::$tokenKey]);
    }
    
    public static function getUser() {
        return $_SESSION[self::$userKey] ?? null;
    }
    
    public static function login($user) {
        $_SESSION[self::$tokenKey] = 'tigerex_token_' . time();
        $_SESSION[self::$userKey] = $user;
    }
    
    public static function logout() {
        unset($_SESSION[self::$tokenKey]);
        unset($_SESSION[self::$userKey]);
    }
}

// Usage:
// if (!TigerExAuth::isLoggedIn()) { header('Location: login.php'); exit; }
?>`;

// ============================================================================
// ASP.NET IMPLEMENTATION  
// ============================================================================

const aspAuthTemplate = `// TigerEx ASP.NET Authentication
public class TigerExAuth
{
    private const string TokenKey = "tigerex_token";
    private const string UserKey = "tigerex_user";
    
    public static bool IsLoggedIn(HttpContext context)
    {
        return context.Session[TokenKey] != null;
    }
    
    public static User GetUser(HttpContext context)
    {
        return context.Session[UserKey] as User;
    }
    
    public static void Login(HttpContext context, User user)
    {
        context.Session[TokenKey] = "tigerex_token_" + DateTime.Now.Ticks;
        context.Session[UserKey] = user;
    }
    
    public static void Logout(HttpContext context)
    {
        context.Session.Remove(TokenKey);
        context.Session.Remove(UserKey);
    }
}`;

// ============================================================================
// GO IMPLEMENTATION
// ============================================================================

const goAuthTemplate = `// TigerEx Go Authentication
package auth

import (
    "net/http"
    "time"
)

type User struct {
    Email string \`json:"email"\`
    Name  string \`json:"name"\`
}

type AuthSession struct {
    Token   string    \`json:"token"\`
    User   *User    \`json:"user"\`
    Expiry time.Time \`json:"expiry"\`
}

var sessions = make(map[string]*AuthSession)

func Login(w http.ResponseWriter, r *http.Request, user *User) {
    token := "tigerex_token_" + time.Now().Format("20060102150405")
    
    cookie := &http.Cookie{
        Name:    "tigerex_token",
        Value:   token,
        Expires: time.Now().Add(24 * time.Hour),
        Path:    "/",
    }
    http.SetCookie(w, cookie)
    
    sessions[token] = &AuthSession{
        Token: token,
        User:  user,
        Expiry: time.Now().Add(24 * time.Hour),
    }
}

func Logout(w http.ResponseWriter, r *http.Request) {
    cookie := &http.Cookie{
        Name:   "tigerex_token",
        Value:  "",
        Path:   "/",
        MaxAge: -1,
    }
    http.SetCookie(w, cookie)
}

func IsLoggedIn(r *http.Request) bool {
    cookie, err := r.Cookie("tigerex_token")
    if err != nil {
        return false
    }
    
    session, exists := sessions[cookie.Value]
    if !exists || session.Expiry.Before(time.Now()) {
        return false
    }
    
    return true
}`;

// ============================================================================
// RUST IMPLEMENTATION
// ============================================================================

const rustAuthTemplate = `// TigerEx Rust Authentication
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub email: String,
    pub name: Option<String>,
}

#[derive(Debug, Clone)]
pub struct AuthSession {
    pub token: String,
    pub user: User,
    pub expires_at: i64,
}

lazy_static! {
    pub static ref SESSIONS: Mutex<HashMap<String, AuthSession>> = Mutex::new(HashMap::new());
}

pub fn login(token: &str, user: User) {
    let expiry = time::now().timestamp() + (24 * 60 * 60);
    let session = AuthSession {
        token: token.to_string(),
        user,
        expires_at: expiry,
    };
    SESSIONS.lock().unwrap().insert(token.to_string(), session);
}

pub fn is_logged_in(token: &str) -> bool {
    let sessions = SESSIONS.lock().unwrap();
    if let Some(session) = sessions.get(token) {
        return session.expires_at > time::now().timestamp();
    }
    false
}

pub fn logout(token: &str) {
    SESSIONS.lock().unwrap().remove(token);
}`;

// ============================================================================
// PYTHON/PYSCRIPT IMPLEMENTATION
// ============================================================================

const pythonAuthTemplate = `"""
TigerEx Python Authentication
""""
import json
import time
from datetime import datetime, timedelta

class TigerExAuth:
    TOKEN_KEY = 'tigerex_token'
    USER_KEY = 'tigerex_user'
    SESSION_FILE = 'tigerex_session.txt'
    
    @staticmethod
    def is_logged_in():
        try:
            # Browser environment
            if 'window' in dir():
                return localStorage.getItem(TigerExAuth.TOKEN_KEY) is not None
            # Server environment  
            return hasattr(TigerExAuth, '_session')
        except:
            return False
    
    @staticmethod
    def login(user):
        token = f'tigerex_token_{int(time.time())}'
        if 'window' in dir():
            localStorage.setItem(TigerExAuth.TOKEN_KEY, token)
            localStorage.setItem(TigerExAuth.USER_KEY, json.dumps(user))
        return token
    
    @staticmethod
    def logout():
        if 'window' in dir():
            localStorage.removeItem(TigerExAuth.TOKEN_KEY)
            localStorage.removeItem(TigerExAuth.USER_KEY)
    
    @staticmethod
    def get_user():
        if 'window' in dir():
            data = localStorage.getItem(TigerExAuth.USER_KEY)
            return json.loads(data) if data else None
        return None`;

// ============================================================================
// C/C++ IMPLEMENTATION
// ============================================================================

const cAuthTemplate = `// TigerEx C/C++ Authentication
#ifndef TIGEREX_AUTH_H
#define TIGEREX_AUTH_H

#include <stdbool.h>
#include <time.h>

typedef struct {
    char email[256];
    char name[128];
    time_t login_time;
} TigerExUser;

typedef struct {
    char token[64];
    TigerExUser* user;
    time_t expires_at;
} TigerExSession;

// Global session storage (in real app, use secure storage)
static TigerExSession* current_session = NULL;

bool tigerex_is_logged_in() {
    if (current_session == NULL) return false;
    return time(NULL) < current_session->expires_at;
}

void tigerex_login(TigerExUser* user) {
    if (current_session == NULL) {
        current_session = malloc(sizeof(TigerExSession));
    }
    snprintf(current_session->token, 64, "tigerex_token_%ld", time(NULL));
    current_session->user = user;
    current_session->expires_at = time(NULL) + (24 * 60 * 60); // 24 hours
}

void tigerex_logout() {
    if (current_session != NULL) {
        free(current_session->user);
        free(current_session);
        current_session = NULL;
    }
}

#endif`;

// ============================================================================
// EXPORTS
// ============================================================================

// Export for different environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        isLoggedIn,
        getToken,
        getUserEmail,
        getUserData,
        getDisplayName,
        getUserAvatar,
        login,
        logout,
        authMiddleware,
        phpAuthTemplate,
        aspAuthTemplate,
        goAuthTemplate,
        rustAuthTemplate,
        pythonAuthTemplate,
        cAuthTemplate,
    };
} else if (typeof window !== 'undefined') {
    window.TigerExAuth = {
        isLoggedIn,
        getToken,
        getUserEmail,
        getUserData,
        getDisplayName,
        getUserAvatar,
        login,
        logout,
        useAuth,
        useAuthComposable,
        TigerExAuthService,
        ReactNativeAuth,
    };
}