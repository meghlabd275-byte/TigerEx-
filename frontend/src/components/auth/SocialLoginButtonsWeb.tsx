'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import styles from './SocialLoginButtons.module.css';

interface SocialLoginButtonsProps {
  onSuccess?: (user: any) => void;
  onError?: (error: string) => void;
  mode?: 'login' | 'register' | 'link';
  redirectUrl?: string;
}

const SOCIAL_PROVIDERS = [
  { id: 'google', name: 'Google', icon: '🔵', color: '#4285F4' },
  { id: 'facebook', name: 'Facebook', icon: '📘', color: '#1877F2' },
  { id: 'twitter', name: 'Twitter', icon: '🐦', color: '#1DA1F2' },
  { id: 'github', name: 'GitHub', icon: '🐙', color: '#333333' },
  { id: 'discord', name: 'Discord', icon: '💬', color: '#5865F2' },
  { id: 'telegram', name: 'Telegram', icon: '✈️', color: '#0088cc' },
  { id: 'apple', name: 'Apple', icon: '🍎', color: '#000000' },
  { id: 'linkedin', name: 'LinkedIn', icon: '💼', color: '#0A66C2' },
];

export default function SocialLoginButtons({
  onSuccess,
  onError,
  mode = 'login',
  redirectUrl,
}: SocialLoginButtonsProps) {
  const [loading, setLoading] = useState<string | null>(null);
  const [enabledProviders, setEnabledProviders] = useState<string[]>([]);
  const router = useRouter();
  const { login, linkAccount } = useAuth();

  useEffect(() => {
    fetchEnabledProviders();
    
    // Check for callback from OAuth
    const url = new URL(window.location.href);
    const token = url.searchParams.get('token');
    const refreshToken = url.searchParams.get('refreshToken');
    const error = url.searchParams.get('error');
    
    if (token) {
      handleAuthSuccess(token, refreshToken || undefined);
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    if (error) {
      onError?.(decodeURIComponent(error));
    }
  }, []);

  const fetchEnabledProviders = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/social/configs`);
      if (response.ok) {
        const data = await response.json();
        setEnabledProviders(data.enabledProviders || SOCIAL_PROVIDERS.map(p => p.id));
      }
    } catch (error) {
      // Default to all providers if config fetch fails
      setEnabledProviders(SOCIAL_PROVIDERS.map(p => p.id));
    }
  };

  const handleSocialLogin = (provider: string) => {
    setLoading(provider);
    
    const callbackUrl = `${window.location.origin}/auth/callback`;
    const state = btoa(JSON.stringify({
      redirect: redirectUrl || '/',
      mode,
    }));
    
    const authUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/auth/social/${provider}?state=${state}&redirect_uri=${encodeURIComponent(callbackUrl)}`;
    
    window.location.href = authUrl;
  };

  const handleAuthSuccess = async (token: string, refreshToken?: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        
        if (mode === 'link') {
          await linkAccount(token);
        } else {
          await login(token, refreshToken);
        }
        
        onSuccess?.(data.user);
        
        // Check for redirect
        const url = new URL(window.location.href);
        const state = url.searchParams.get('state');
        if (state) {
          try {
            const { redirect } = JSON.parse(atob(state));
            router.push(redirect);
            return;
          } catch {}
        }
        
        router.push('/dashboard');
      }
    } catch (error) {
      console.error('Auth success handling error:', error);
      onError?.('Failed to complete authentication');
    } finally {
      setLoading(null);
    }
  };

  const isProviderEnabled = (providerId: string) => {
    return enabledProviders.includes(providerId);
  };

  return (
    <div className={styles.container}>
      <div className={styles.divider}>
        <span className={styles.dividerText}>or continue with</span>
      </div>
      
      <div className={styles.buttonGrid}>
        {SOCIAL_PROVIDERS.map((provider) => (
          <button
            key={provider.id}
            className={`${styles.socialButton} ${styles[provider.id] || ''}`}
            style={{ backgroundColor: provider.color }}
            onClick={() => handleSocialLogin(provider.id)}
            disabled={loading !== null || !isProviderEnabled(provider.id)}
            aria-label={`${mode === 'link' ? 'Link' : 'Continue with'} ${provider.name}`}
          >
            {loading === provider.id ? (
              <span className={styles.spinner}></span>
            ) : (
              <>
                <span className={styles.icon}>{provider.icon}</span>
                <span className={styles.text}>
                  {mode === 'link' ? 'Link' : 'Continue with'} {provider.name}
                </span>
              </>
            )}
          </button>
        ))}
      </div>
      
      <p className={styles.terms}>
        By continuing, you agree to our{' '}
        <a href="/terms" className={styles.link}>Terms of Service</a>
        {' '}and{' '}
        <a href="/privacy" className={styles.link}>Privacy Policy</a>
      </p>
    </div>
  );
}