/**
 * TigerEx Next.js Authentication
 * 
 * @version 1.0.0
 * @description Auth for Next.js App Router and Pages Router
 */

import { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

// Context
const AuthContext = createContext(null);

// Provider component
export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();
    
    useEffect(() => {
        checkAuth();
    }, []);
    
    const checkAuth = () => {
        if (typeof window === 'undefined') {
            setLoading(false);
            return;
        }
        
        const token = localStorage.getItem('tigerex_token');
        const expiry = localStorage.getItem('tigerex_token_expiry');
        
        if (!token || (expiry && new Date(expiry) < new Date())) {
            setUser(null);
            setLoading(false);
            return;
        }
        
        const userData = localStorage.getItem('tigerex_user_data');
        setUser(userData ? JSON.parse(userData) : null);
        setLoading(false);
    };
    
    const login = (userData) => {
        const token = 'tigerex_token_' + Date.now();
        const expiry = new Date();
        expiry.setHours(expiry.getHours() + 24);
        
        localStorage.setItem('tigerex_token', token);
        localStorage.setItem('tigerex_user_data', JSON.stringify(userData));
        localStorage.setItem('tigerex_token_expiry', expiry.toISOString());
        
        setUser(userData);
    };
    
    const logout = () => {
        localStorage.removeItem('tigerex_token');
        localStorage.removeItem('tigerex_user_data');
        localStorage.removeItem('tigerex_token_expiry');
        
        setUser(null);
    };
    
    const isLoggedIn = () => user !== null;
    
    const value = {
        user,
        loading,
        isLoggedIn,
        login,
        logout,
        getEmail: () => user?.email || '',
        getName: () => user?.name || user?.email?.split('@')[0] || 'User',
        getAvatar: () => (user?.name || user?.email?.[0] || 'U').toUpperCase()
    };
    
    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

// Hook
export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
}

// HOC for protected routes
export function withAuth(Component) {
    return function AuthComponent(props) {
        const { isLoggedIn, loading } = useAuth();
        const router = useRouter();
        
        useEffect(() => {
            if (!loading && !isLoggedIn()) {
                router.push('/login');
            }
        }, [loading, isLoggedIn]);
        
        if (loading) {
            return <div>Loading...</div>;
        }
        
        if (!isLoggedIn()) {
            return null;
        }
        
        return <Component {...props} />;
    };
}

// Middleware for Next.js
export function authMiddleware(req) {
    const token = req.cookies.get('tigerex_token')?.value;
    const expiry = req.cookies.get('tigerex_token_expiry')?.value;
    
    if (!token || (expiry && new Date(expiry) < new Date())) {
        return { redirect: { destination: '/login', permanent: false } };
    }
    
    return { props: {} };
}

// Client-side guard
export function AuthGuard({ children }) {
    const { isLoggedIn, loading } = useAuth();
    const router = useRouter();
    
    useEffect(() => {
        if (!loading && !isLoggedIn()) {
            router.push('/login');
        }
    }, [loading, isLoggedIn]);
    
    if (loading) return <div>Loading...</div>;
    if (!isLoggedIn()) return null;
    
    return children;
}

// User Menu component
export function UserMenu({ showEmail = true }) {
    const { user, getEmail, getAvatar, logout } = useAuth();
    const [menuOpen, setMenuOpen] = useState(false);
    
    if (!user) return null;
    
    return (
        <div className="user-menu">
            <button onClick={() => setMenuOpen(!menuOpen)}>
                <span className="avatar">{getAvatar()}</span>
                {showEmail && <span>{getEmail()}</span>}
            </button>
            {menuOpen && (
                <div className="dropdown">
                    <a href="/profile">Profile</a>
                    <a href="/wallet">Wallet</a>
                    <a href="/orders">Orders</a>
                    <button onClick={logout}>Logout</button>
                </div>
            )}
        </div>
    );
}