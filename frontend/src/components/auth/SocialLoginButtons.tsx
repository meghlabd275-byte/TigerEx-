/**
 * TigerEx Social Login Component
 * Complete implementation for Google, Facebook, Twitter, Telegram, Apple, GitHub, Discord, LinkedIn
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import * as WebBrowser from 'expo-web-browser';
import * as AuthSession from 'expo-auth-session';
import { useAuth } from '../../contexts/AuthContext';

interface SocialLoginButtonsProps {
  onSuccess?: (user: any) => void;
  onError?: (error: string) => void;
  mode?: 'login' | 'register' | 'link';
}

const SOCIAL_PROVIDERS = {
  google: {
    name: 'Google',
    icon: '🔵',
    color: '#4285F4',
    clientId: process.env.EXPO_PUBLIC_GOOGLE_CLIENT_ID,
    scopes: ['profile', 'email'],
  },
  facebook: {
    name: 'Facebook',
    icon: '📘',
    color: '#1877F2',
    clientId: process.env.EXPO_PUBLIC_FACEBOOK_APP_ID,
    scopes: ['email', 'public_profile'],
  },
  twitter: {
    name: 'Twitter',
    icon: '🐦',
    color: '#1DA1F2',
    clientId: process.env.EXPO_PUBLIC_TWITTER_CLIENT_ID,
  },
  github: {
    name: 'GitHub',
    icon: '🐙',
    color: '#333',
    clientId: process.env.EXPO_PUBLIC_GITHUB_CLIENT_ID,
    scopes: ['user:email'],
  },
  discord: {
    name: 'Discord',
    icon: '💬',
    color: '#5865F2',
    clientId: process.env.EXPO_PUBLIC_DISCORD_CLIENT_ID,
    scopes: ['identify', 'email'],
  },
  telegram: {
    name: 'Telegram',
    icon: '✈️',
    color: '#0088cc',
    botUsername: process.env.EXPO_PUBLIC_TELEGRAM_BOT_USERNAME,
  },
  apple: {
    name: 'Apple',
    icon: '🍎',
    color: '#000000',
    clientId: process.env.EXPO_PUBLIC_APPLE_CLIENT_ID,
  },
  linkedin: {
    name: 'LinkedIn',
    icon: '💼',
    color: '#0A66C2',
    clientId: process.env.EXPO_PUBLIC_LINKEDIN_CLIENT_ID,
    scopes: ['r_emailaddress', 'r_liteprofile'],
  },
};

const SocialLoginButtons: React.FC<SocialLoginButtonsProps> = ({
  onSuccess,
  onError,
  mode = 'login',
}) => {
  const [loading, setLoading] = useState<string | null>(null);
  const [configs, setConfigs] = useState<any>({});
  const router = useRouter();
  const { login, linkAccount } = useAuth();

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/api/auth/social/configs`);
      if (response.ok) {
        const data = await response.json();
        setConfigs(data.configs || {});
      }
    } catch (error) {
      console.log('Failed to load social configs');
    }
  };

  const handleGoogleLogin = async () => {
    try {
      setLoading('google');
      
      const redirectUrl = AuthSession.makeRedirectUri({
        scheme: 'tigerex',
        path: 'auth/callback',
      });
      
      const authUrl = `${process.env.EXPO_PUBLIC_API_URL}/api/auth/social/google?redirect_uri=${encodeURIComponent(redirectUrl)}`;
      
      const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUrl);
      
      if (result.type === 'success' && result.url) {
        const url = new URL(result.url);
        const token = url.searchParams.get('token');
        const refreshToken = url.searchParams.get('refreshToken');
        
        if (token) {
          await handleAuthSuccess(token, refreshToken);
        }
      }
    } catch (error: any) {
      console.error('Google login error:', error);
      onError?.(error.message || 'Google login failed');
    } finally {
      setLoading(null);
    }
  };

  const handleFacebookLogin = async () => {
    try {
      setLoading('facebook');
      
      const redirectUrl = AuthSession.makeRedirectUri({
        scheme: 'tigerex',
        path: 'auth/callback',
      });
      
      const authUrl = `${process.env.EXPO_PUBLIC_API_URL}/api/auth/social/facebook?redirect_uri=${encodeURIComponent(redirectUrl)}`;
      
      const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUrl);
      
      if (result.type === 'success' && result.url) {
        const url = new URL(result.url);
        const token = url.searchParams.get('token');
        const refreshToken = url.searchParams.get('refreshToken');
        
        if (token) {
          await handleAuthSuccess(token, refreshToken);
        }
      }
    } catch (error: any) {
      console.error('Facebook login error:', error);
      onError?.(error.message || 'Facebook login failed');
    } finally {
      setLoading(null);
    }
  };

  const handleTwitterLogin = async () => {
    try {
      setLoading('twitter');
      
      const redirectUrl = AuthSession.makeRedirectUri({
        scheme: 'tigerex',
        path: 'auth/callback',
      });
      
      const authUrl = `${process.env.EXPO_PUBLIC_API_URL}/api/auth/social/twitter?redirect_uri=${encodeURIComponent(redirectUrl)}`;
      
      const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUrl);
      
      if (result.type === 'success' && result.url) {
        const url = new URL(result.url);
        const token = url.searchParams.get('token');
        const refreshToken = url.searchParams.get('refreshToken');
        
        if (token) {
          await handleAuthSuccess(token, refreshToken);
        }
      }
    } catch (error: any) {
      console.error('Twitter login error:', error);
      onError?.(error.message || 'Twitter login failed');
    } finally {
      setLoading(null);
    }
  };

  const handleGitHubLogin = async () => {
    try {
      setLoading('github');
      
      const redirectUrl = AuthSession.makeRedirectUri({
        scheme: 'tigerex',
        path: 'auth/callback',
      });
      
      const authUrl = `${process.env.EXPO_PUBLIC_API_URL}/api/auth/social/github?redirect_uri=${encodeURIComponent(redirectUrl)}`;
      
      const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUrl);
      
      if (result.type === 'success' && result.url) {
        const url = new URL(result.url);
        const token = url.searchParams.get('token');
        const refreshToken = url.searchParams.get('refreshToken');
        
        if (token) {
          await handleAuthSuccess(token, refreshToken);
        }
      }
    } catch (error: any) {
      console.error('GitHub login error:', error);
      onError?.(error.message || 'GitHub login failed');
    } finally {
      setLoading(null);
    }
  };

  const handleDiscordLogin = async () => {
    try {
      setLoading('discord');
      
      const redirectUrl = AuthSession.makeRedirectUri({
        scheme: 'tigerex',
        path: 'auth/callback',
      });
      
      const authUrl = `${process.env.EXPO_PUBLIC_API_URL}/api/auth/social/discord?redirect_uri=${encodeURIComponent(redirectUrl)}`;
      
      const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUrl);
      
      if (result.type === 'success' && result.url) {
        const url = new URL(result.url);
        const token = url.searchParams.get('token');
        const refreshToken = url.searchParams.get('refreshToken');
        
        if (token) {
          await handleAuthSuccess(token, refreshToken);
        }
      }
    } catch (error: any) {
      console.error('Discord login error:', error);
      onError?.(error.message || 'Discord login failed');
    } finally {
      setLoading(null);
    }
  };

  const handleTelegramLogin = () => {
    Alert.alert(
      'Telegram Login',
      'Would you like to login with Telegram?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Continue',
          onPress: async () => {
            try {
              setLoading('telegram');
              // Open Telegram bot
              const botUsername = configs.telegram?.botUsername || 'TigerExBot';
              const telegramUrl = `tg://resolve?domain=${botUsername}&start=auth_${Date.now()}`;
              
              const supported = await WebBrowser.canOpenUrlAsync(telegramUrl);
              if (supported) {
                await WebBrowser.openUrlAsync(telegramUrl);
              } else {
                // Fallback to web Telegram
                await WebBrowser.openUrlAsync(`https://t.me/${botUsername}?start=auth_${Date.now()}`);
              }
            } catch (error: any) {
              console.error('Telegram login error:', error);
              onError?.(error.message || 'Telegram login failed');
            } finally {
              setLoading(null);
            }
          },
        },
      ]
    );
  };

  const handleAppleLogin = async () => {
    try {
      setLoading('apple');
      
      const redirectUrl = AuthSession.makeRedirectUri({
        scheme: 'tigerex',
        path: 'auth/callback',
      });
      
      const authUrl = `${process.env.EXPO_PUBLIC_API_URL}/api/auth/social/apple?redirect_uri=${encodeURIComponent(redirectUrl)}`;
      
      const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUrl);
      
      if (result.type === 'success' && result.url) {
        const url = new URL(result.url);
        const token = url.searchParams.get('token');
        const refreshToken = url.searchParams.get('refreshToken');
        
        if (token) {
          await handleAuthSuccess(token, refreshToken);
        }
      }
    } catch (error: any) {
      console.error('Apple login error:', error);
      onError?.(error.message || 'Apple login failed');
    } finally {
      setLoading(null);
    }
  };

  const handleLinkedInLogin = async () => {
    try {
      setLoading('linkedin');
      
      const redirectUrl = AuthSession.makeRedirectUri({
        scheme: 'tigerex',
        path: 'auth/callback',
      });
      
      const authUrl = `${process.env.EXPO_PUBLIC_API_URL}/api/auth/social/linkedin?redirect_uri=${encodeURIComponent(redirectUrl)}`;
      
      const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUrl);
      
      if (result.type === 'success' && result.url) {
        const url = new URL(result.url);
        const token = url.searchParams.get('token');
        const refreshToken = url.searchParams.get('refreshToken');
        
        if (token) {
          await handleAuthSuccess(token, refreshToken);
        }
      }
    } catch (error: any) {
      console.error('LinkedIn login error:', error);
      onError?.(error.message || 'LinkedIn login failed');
    } finally {
      setLoading(null);
    }
  };

  const handleAuthSuccess = async (token: string, refreshToken?: string) => {
    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/api/auth/me`, {
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
        
        if (mode !== 'link') {
          router.replace('/(tabs)/home');
        }
      }
    } catch (error) {
      console.error('Auth success handling error:', error);
      onError?.('Failed to complete authentication');
    }
  };

  const SocialButton = ({ provider, onPress, disabled }: { provider: keyof typeof SOCIAL_PROVIDERS; onPress: () => void; disabled?: boolean }) => {
    const config = SOCIAL_PROVIDERS[provider];
    const isLoading = loading === provider;
    
    return (
      <TouchableOpacity
        style={[styles.socialButton, { backgroundColor: config.color }]}
        onPress={onPress}
        disabled={isLoading || disabled}
        activeOpacity={0.8}
      >
        {isLoading ? (
          <ActivityIndicator color="#fff" size="small" />
        ) : (
          <>
            <Text style={styles.socialIcon}>{config.icon}</Text>
            <Text style={styles.socialText}>
              {mode === 'link' ? 'Link ' : 'Continue with '}{config.name}
            </Text>
          </>
        )}
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.dividerText}>or continue with</Text>
      
      <View style={styles.buttonContainer}>
        <SocialButton provider="google" onPress={handleGoogleLogin} />
        <SocialButton provider="facebook" onPress={handleFacebookLogin} />
        <SocialButton provider="twitter" onPress={handleTwitterLogin} />
        <SocialButton provider="github" onPress={handleGitHubLogin} />
        <SocialButton provider="discord" onPress={handleDiscordLogin} />
        <SocialButton provider="telegram" onPress={handleTelegramLogin} />
        
        {Platform.OS === 'ios' && (
          <SocialButton provider="apple" onPress={handleAppleLogin} />
        )}
        
        <SocialButton provider="linkedin" onPress={handleLinkedInLogin} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
    marginTop: 24,
  },
  dividerText: {
    textAlign: 'center',
    color: '#6B7280',
    marginBottom: 16,
    fontSize: 14,
  },
  buttonContainer: {
    gap: 12,
  },
  socialButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 12,
    minHeight: 52,
  },
  socialIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  socialText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default SocialLoginButtons;