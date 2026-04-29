<?php
/**
 * TigerEx PHP Authentication Library
 * 
 * Provides authentication functionality for PHP-based TigerEx applications
 * @version 1.0.0
 */

session_start();

class TigerExAuth {
    
    private static $tokenKey = 'tigerex_token';
    private static $userKey = 'tigerex_user';
    private static $expiryKey = 'tigerex_expiry';
    
    /**
     * Check if user is logged in
     * @return bool
     */
    public static function isLoggedIn() {
        if (!isset($_SESSION[self::$tokenKey])) {
            return false;
        }
        
        // Check token expiry
        if (isset($_SESSION[self::$expiryKey])) {
            $expiry = $_SESSION[self::$expiryKey];
            if (strtotime($expiry) < time()) {
                self::logout();
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Get current user data
     * @return array|null
     */
    public static function getUser() {
        return $_SESSION[self::$userKey] ?? null;
    }
    
    /**
     * Get user email
     * @return string
     */
    public static function getEmail() {
        $user = self::getUser();
        return $user['email'] ?? '';
    }
    
    /**
     * Get display name
     * @return string
     */
    public static function getDisplayName() {
        $user = self::getUser();
        if ($user && isset($user['name'])) {
            return $user['name'];
        }
        $email = self::getEmail();
        return $email ? explode('@', $email)[0] : 'User';
    }
    
    /**
     * Get user avatar initial
     * @return string
     */
    public static function getAvatar() {
        return strtoupper(self::getDisplayName()[0]);
    }
    
    /**
     * Login user
     * @param array $user User data
     * @return bool
     */
    public static function login($user) {
        if (!$user || !isset($user['email'])) {
            return false;
        }
        
        $_SESSION[self::$tokenKey] = 'tigerex_token_' . time();
        $_SESSION[self::$userKey] = $user;
        
        // Set expiry (24 hours)
        $expiry = date('Y-m-d H:i:s', time() + 86400);
        $_SESSION[self::$expiryKey] = $expiry;
        
        return true;
    }
    
    /**
     * Logout user
     */
    public static function logout() {
        unset($_SESSION[self::$tokenKey]);
        unset($_SESSION[self::$userKey]);
        unset($_SESSION[self::$expiryKey]);
    }
    
    /**
     * Require login - redirect if not logged in
     */
    public static function requireLogin() {
        if (!self::isLoggedIn()) {
            header('Location: login.html');
            exit;
        }
    }
    
    /**
     * Require guest - redirect if logged in
     */
    public static function requireGuest() {
        if (self::isLoggedIn()) {
            header('Location: dashboard.html');
            exit;
        }
    }
}

/**
 * Middleware function for protected routes
 */
function requireAuth() {
    if (!TigerExAuth::isLoggedIn()) {
        header('Content-Type: application/json');
        http_response_code(401);
        echo json_encode(['error' => 'Authentication required']);
        exit;
    }
}