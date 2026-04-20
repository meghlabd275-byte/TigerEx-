/**
 * TigerEx React Component
 * @file CompleteSocialAuth.tsx
 * @description React component for TigerEx
 * @author TigerEx Development Team
 */
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Facebook,
  Twitter,
  Mail,
  Github,
  Linkedin,
  MessageCircle,
  Apple,
  Lock,
  Eye,
  EyeOff,
  Loader2,
  CheckCircle,
  XCircle,
  AlertCircle,
} from 'lucide-react';
import { useRouter } from 'next/navigation';

// Social provider configuration
const SOCIAL_PROVIDERS = [
  {
    id: 'google',
    name: 'Mail',
    icon: Mail,
    color: '#EA4335',
    bgColor: 'bg-red-50 hover:bg-red-100',
    borderColor: 'border-red-200',
  },
  {
    id: 'facebook',
    name: 'Facebook',
    icon: Facebook,
    color: '#1877F2',
    bgColor: 'bg-blue-50 hover:bg-blue-100',
    borderColor: 'border-blue-200',
  },
  {
    id: 'twitter',
    name: 'Twitter',
    icon: Twitter,
    color: '#1DA1F2',
    bgColor: 'bg-sky-50 hover:bg-sky-100',
    borderColor: 'border-sky-200',
  },
  {
    id: 'telegram',
    name: 'Telegram',
    icon: MessageCircle,
    color: '#0088cc',
    bgColor: 'bg-cyan-50 hover:bg-cyan-100',
    borderColor: 'border-cyan-200',
  },
  {
    id: 'github',
    name: 'GitHub',
    icon: Github,
    color: '#333',
    bgColor: 'bg-gray-50 hover:bg-gray-100',
    borderColor: 'border-gray-200',
  },
  {
    id: 'discord',
    name: 'Discord',
    icon: MessageCircle,
    color: '#5865F2',
    bgColor: 'bg-indigo-50 hover:bg-indigo-100',
    borderColor: 'border-indigo-200',
  },
  {
    id: 'linkedin',
    name: 'LinkedIn',
    icon: Linkedin,
    color: '#0A66C2',
    bgColor: 'bg-blue-50 hover:bg-blue-100',
    borderColor: 'border-blue-200',
  },
  {
    id: 'apple',
    name: 'Apple',
    icon: Apple,
    color: '#000',
    bgColor: 'bg-gray-100 hover:bg-gray-200',
    borderColor: 'border-gray-300',
  },
];

interface SocialAuthProps {
  onLoginSuccess?: (user: any) => void;
  onLoginError?: (error: string) => void;
  redirectUrl?: string;
  mode?: 'login' | 'register' | 'both';
}

export function CompleteSocialAuth({
  onLoginSuccess,
  onLoginError,
  redirectUrl = '/dashboard',
  mode = 'both',
}: SocialAuthProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>(mode === 'both' ? 'login' : mode as 'login' | 'register');
  const [fullName, setFullName] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreeTerms, setAgreeTerms] = useState(false);

  // Check for OAuth callback
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const refreshToken = urlParams.get('refreshToken');
    const errorParam = urlParams.get('error');

    if (errorParam) {
      setError(decodeURIComponent(errorParam));
      return;
    }

    if (token) {
      // Store tokens
      localStorage.setItem('accessToken', token);
      if (refreshToken) {
        localStorage.setItem('refreshToken', refreshToken);
      }

      // Fetch user info
      fetchUserInfo(token);
    }
  }, []);

  const fetchUserInfo = async (token: string) => {
    try {
      const response = await fetch('/api/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess('Login successful! Redirecting...');
        
        if (onLoginSuccess) {
          onLoginSuccess(data.user);
        }

        setTimeout(() => {
          router.push(redirectUrl);
        }, 1500);
      }
    } catch (err) {
      setError('Failed to fetch user info');
    }
  };

  const handleSocialLogin = useCallback(async (provider: string) => {
    setIsLoading(provider);
    setError(null);

    try {
      // Get OAuth URL from backend
      const response = await fetch(`/api/auth/social/${provider}`);
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.authUrl) {
          // Redirect to OAuth provider
          window.location.href = data.authUrl;
        }
      } else {
        // Fallback to direct OAuth flow
        const authUrl = getOAuthUrl(provider);
        window.location.href = authUrl;
      }
    } catch (err) {
      setError(`Failed to initiate ${provider} login`);
      setIsLoading(null);
    }
  }, []);

  const getOAuthUrl = (provider: string): string => {
    const redirectUri = encodeURIComponent(`${window.location.origin}/api/auth/social/${provider}/callback`);
    
    switch (provider) {
      case 'google':
        return `https://accounts.google.com/o/oauth2/v2/auth?client_id=${process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID}&redirect_uri=${redirectUri}&response_type=code&scope=profile email`;
      case 'facebook':
        return `https://www.facebook.com/v18.0/dialog/oauth?client_id=${process.env.NEXT_PUBLIC_FACEBOOK_APP_ID}&redirect_uri=${redirectUri}&scope=email,public_profile`;
      case 'twitter':
        return `https://twitter.com/i/oauth2/authorize?client_id=${process.env.NEXT_PUBLIC_TWITTER_CLIENT_ID}&redirect_uri=${redirectUri}&response_type=code&scope=users.read tweet.read`;
      case 'github':
        return `https://github.com/login/oauth/authorize?client_id=${process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID}&redirect_uri=${redirectUri}&scope=user:email`;
      case 'discord':
        return `https://discord.com/api/oauth2/authorize?client_id=${process.env.NEXT_PUBLIC_DISCORD_CLIENT_ID}&redirect_uri=${redirectUri}&response_type=code&scope=identify email`;
      case 'linkedin':
        return `https://www.linkedin.com/oauth/v2/authorization?client_id=${process.env.NEXT_PUBLIC_LINKEDIN_CLIENT_ID}&redirect_uri=${redirectUri}&response_type=code&scope=r_emailaddress r_liteprofile`;
      default:
        return '#';
    }
  };

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading('email');
    setError(null);

    try {
      const endpoint = authMode === 'login' ? '/api/auth/login' : '/api/auth/register';
      const body = authMode === 'login'
        ? { email, password }
        : { email, password, fullName, confirmPassword };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('accessToken', data.token);
        if (data.refreshToken) {
          localStorage.setItem('refreshToken', data.refreshToken);
        }

        setSuccess(`${authMode === 'login' ? 'Login' : 'Registration'} successful! Redirecting...`);

        if (onLoginSuccess) {
          onLoginSuccess(data.user);
        }

        setTimeout(() => {
          router.push(redirectUrl);
        }, 1500);
      } else {
        setError(data.message || `${authMode === 'login' ? 'Login' : 'Registration'} failed`);
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setIsLoading(null);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            {authMode === 'login' ? 'Welcome Back' : 'Create Account'}
          </h1>
          <p className="text-gray-600">
            {authMode === 'login'
              ? 'Sign in to your TigerEx account'
              : 'Join TigerEx and start trading'}
          </p>
        </div>

        <AnimatePresence mode="wait">
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700"
            >
              <AlertCircle className="w-5 h-5" />
              <span className="text-sm">{error}</span>
            </motion.div>
          )}

          {success && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2 text-green-700"
            >
              <CheckCircle className="w-5 h-5" />
              <span className="text-sm">{success}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Social Login Buttons */}
        <div className="grid grid-cols-2 gap-3 mb-6">
          {SOCIAL_PROVIDERS.slice(0, 4).map((provider) => {
            const Icon = provider.icon;
            return (
              <motion.button
                key={provider.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleSocialLogin(provider.id)}
                disabled={isLoading !== null}
                className={`${provider.bgColor} ${provider.borderColor} border p-3 rounded-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50`}
              >
                {isLoading === provider.id ? (
                  <Loader2 className="w-5 h-5 animate-spin" style={{ color: provider.color }} />
                ) : (
                  <Icon className="w-5 h-5" style={{ color: provider.color }} />
                )}
                <span className="text-sm font-medium text-gray-700">{provider.name}</span>
              </motion.button>
            );
          })}
        </div>

        {/* More Social Providers */}
        <div className="flex justify-center gap-2 mb-6">
          {SOCIAL_PROVIDERS.slice(4).map((provider) => {
            const Icon = provider.icon;
            return (
              <motion.button
                key={provider.id}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => handleSocialLogin(provider.id)}
                disabled={isLoading !== null}
                className={`${provider.bgColor} ${provider.borderColor} border p-2 rounded-lg transition-all disabled:opacity-50`}
                title={provider.name}
              >
                {isLoading === provider.id ? (
                  <Loader2 className="w-5 h-5 animate-spin" style={{ color: provider.color }} />
                ) : (
                  <Icon className="w-5 h-5" style={{ color: provider.color }} />
                )}
              </motion.button>
            );
          })}
        </div>

        {/* Divider */}
        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-200"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">Or continue with email</span>
          </div>
        </div>

        {/* Email Form */}
        <form onSubmit={handleEmailAuth} className="space-y-4">
          {authMode === 'register' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="John Doe"
                required
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="you@example.com"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="••••••••"
                required
                minLength={8}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2"
              >
                {showPassword ? (
                  <EyeOff className="w-5 h-5 text-gray-400" />
                ) : (
                  <Eye className="w-5 h-5 text-gray-400" />
                )}
              </button>
            </div>
          </div>

          {authMode === 'register' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>
          )}

          {authMode === 'register' && (
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="agreeTerms"
                checked={agreeTerms}
                onChange={(e) => setAgreeTerms(e.target.checked)}
                className="w-4 h-4 text-orange-500 border-gray-300 rounded focus:ring-orange-500"
                required
              />
              <label htmlFor="agreeTerms" className="text-sm text-gray-600">
                I agree to the{' '}
                <a href="/terms" className="text-orange-500 hover:underline">Terms of Service</a>
                {' '}and{' '}
                <a href="/privacy" className="text-orange-500 hover:underline">Privacy Policy</a>
              </label>
            </div>
          )}

          {authMode === 'login' && (
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2">
                <input type="checkbox" className="w-4 h-4 text-orange-500 border-gray-300 rounded" />
                <span className="text-sm text-gray-600">Remember me</span>
              </label>
              <a href="/forgot-password" className="text-sm text-orange-500 hover:underline">
                Forgot password?
              </a>
            </div>
          )}

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={isLoading !== null}
            className="w-full bg-gradient-to-r from-orange-500 to-amber-500 text-white py-3 rounded-lg font-medium hover:from-orange-600 hover:to-amber-600 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isLoading === 'email' ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Processing...
              </>
            ) : (
              authMode === 'login' ? 'Sign In' : 'Create Account'
            )}
          </motion.button>
        </form>

        {/* Toggle Auth Mode */}
        {mode === 'both' && (
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              {authMode === 'login' ? "Don't have an account?" : 'Already have an account?'}
              <button
                onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
                className="ml-2 text-orange-500 font-medium hover:underline"
              >
                {authMode === 'login' ? 'Sign up' : 'Sign in'}
              </button>
            </p>
          </div>
        )}
      </div>

      {/* Telegram Widget */}
      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          By signing in, you agree to our{' '}
          <a href="/terms" className="text-orange-500 hover:underline">Terms</a>
          {' '}and{' '}
          <a href="/privacy" className="text-orange-500 hover:underline">Privacy Policy</a>
        </p>
      </div>
    </div>
  );
}

export default CompleteSocialAuth;