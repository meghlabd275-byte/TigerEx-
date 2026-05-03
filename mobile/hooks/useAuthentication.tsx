/**
 * TigerEx Mobile Authentication Hook
 * @file useAuthentication.tsx
 * @description Authentication hook for React Native mobile apps
 * @author TigerEx Development Team
 */

import { useState, useEffect, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const TOKEN_KEY = '@tigerex_token';
const USER_KEY = '@tigerex_user';
const EXPIRY_KEY = '@tigerex_expiry';

export function useAuthentication() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    // Initialize - check for existing session
    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const token = await AsyncStorage.getItem(TOKEN_KEY);
            const expiryStr = await AsyncStorage.getItem(EXPIRY_KEY);
            
            if (!token) {
                setIsLoggedIn(false);
                setLoading(false);
                return;
            }
            
            // Check expiry
            if (expiryStr) {
                const expiry = new Date(expiryStr);
                if (expiry < new Date()) {
                    // Token expired - logout
                    await logout();
                    setLoading(false);
                    return;
                }
            }
            
            const userData = await AsyncStorage.getItem(USER_KEY);
            const parsed = userData ? JSON.parse(userData) : null;
            
            setUser(parsed);
            setIsLoggedIn(!!parsed);
        } catch (error) {
            console.error('Auth check error:', error);
            setIsLoggedIn(false);
        }
        setLoading(false);
    };

    const login = async (userData) => {
        try {
            if (!userData?.email) {
                throw new Error('Email is required');
            }
            
            const token = 'tigerex_token_' + Date.now();
            const expiry = new Date();
            expiry.setHours(expiry.getHours() + 24);
            
            await AsyncStorage.setItem(TOKEN_KEY, token);
            await AsyncStorage.setItem(USER_KEY, JSON.stringify(userData));
            await AsyncStorage.setItem(EXPIRY_KEY, expiry.toISOString());
            
            setUser(userData);
            setIsLoggedIn(true);
            
            return true;
        } catch (error) {
            console.error('Login error:', error);
            return false;
        }
    };

    const logout = async () => {
        try {
            await AsyncStorage.removeItem(TOKEN_KEY);
            await AsyncStorage.removeItem(USER_KEY);
            await AsyncStorage.removeItem(EXPIRY_KEY);
            
            setUser(null);
            setIsLoggedIn(false);
        } catch (error) {
            console.error('Logout error:', error);
        }
    };

    const getEmail = useCallback(() => user?.email || '', [user]);
    const getName = useCallback(() => user?.name || user?.email?.split('@')[0] || 'User', [user]);
    const getAvatar = useCallback(() => (getName()[0] || 'U').toUpperCase(), [getName]);

    return {
        user,
        loading,
        isLoggedIn,
        login,
        logout,
        getEmail,
        getName,
        getAvatar,
        checkAuth
    };
}

/**
 * Higher-order component for auth-protected screens
 */
export function withAuth(WrappedComponent) {
    return function AuthenticatedComponent(props) {
        const { isLoggedIn, loading } = useAuthentication();
        
        if (loading) {
            return null; // Or loading spinner
        }
        
        if (!isLoggedIn) {
            return null; // Or redirect to login
        }
        
        return <WrappedComponent {...props} />;
    };
}export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
