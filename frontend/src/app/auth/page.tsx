/**
 * TigerEx Frontend Component
 * @file page.tsx
 * @description React component for TigerEx platform
 * @author TigerEx Development Team
 */
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import SocialLoginButtons from '@/components/auth/SocialLoginButtonsWeb';
import styles from './Auth.module.css';

type AuthMode = 'login' | 'register' | 'forgot-password';

export default function AuthPage() {
  const [mode, setMode] = useState<AuthMode>('login');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [referralCode, setReferralCode] = useState('');
  const [twoFactorCode, setTwoFactorCode] = useState('');
  const [showTwoFactor, setShowTwoFactor] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (mode === 'register') {
        if (password !== confirmPassword) {
          setError('Passwords do not match');
          setLoading(false);
          return;
        }

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email,
            username,
            password,
            firstName,
            lastName,
            referralCode,
          }),
        });

        const data = await response.json();

        if (data.success) {
          setSuccess('Registration successful! Please check your email for verification.');
          localStorage.setItem('token', data.data.token);
          if (data.data.refreshToken) {
            localStorage.setItem('refreshToken', data.data.refreshToken);
          }
          setTimeout(() => router.push('/dashboard'), 2000);
        } else {
          setError(data.message || 'Registration failed');
        }
      } else if (mode === 'login') {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            emailOrUsername: email,
            password,
            twoFactorCode,
          }),
        });

        const data = await response.json();

        if (data.success) {
          if (data.requiresTwoFactor) {
            setShowTwoFactor(true);
            setLoading(false);
            return;
          }

          localStorage.setItem('token', data.data.token);
          if (data.data.refreshToken) {
            localStorage.setItem('refreshToken', data.data.refreshToken);
          }
          router.push('/dashboard');
        } else {
          setError(data.message || 'Login failed');
        }
      } else if (mode === 'forgot-password') {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/forgot-password`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email }),
        });

        const data = await response.json();
        setSuccess(data.message);
        setMode('login');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleSocialSuccess = (user: any) => {
    router.push('/dashboard');
  };

  const handleSocialError = (error: string) => {
    setError(error);
  };

  return (
    <div className={styles.container}>
      <div className={styles.background}>
        <div className={styles.gradient}></div>
      </div>

      <div className={styles.formWrapper}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>🐯</span>
          <span className={styles.logoText}>TigerEx</span>
        </div>

        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${mode === 'login' ? styles.activeTab : ''}`}
            onClick={() => { setMode('login'); setError(''); setSuccess(''); }}
          >
            Sign In
          </button>
          <button
            className={`${styles.tab} ${mode === 'register' ? styles.activeTab : ''}`}
            onClick={() => { setMode('register'); setError(''); setSuccess(''); }}
          >
            Sign Up
          </button>
        </div>

        {error && <div className={styles.error}>{error}</div>}
        {success && <div className={styles.success}>{success}</div>}

        <form onSubmit={handleSubmit} className={styles.form}>
          {mode === 'register' && (
            <>
              <div className={styles.nameRow}>
                <div className={styles.inputGroup}>
                  <label className={styles.label}>First Name</label>
                  <input
                    type="text"
                    className={styles.input}
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    placeholder="John"
                  />
                </div>
                <div className={styles.inputGroup}>
                  <label className={styles.label}>Last Name</label>
                  <input
                    type="text"
                    className={styles.input}
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    placeholder="Doe"
                  />
                </div>
              </div>

              <div className={styles.inputGroup}>
                <label className={styles.label}>Username</label>
                <input
                  type="text"
                  className={styles.input}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="johndoe"
                  required
                />
              </div>
            </>
          )}

          <div className={styles.inputGroup}>
            <label className={styles.label}>Email</label>
            <input
              type="email"
              className={styles.input}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="john@example.com"
              required
            />
          </div>

          {mode !== 'forgot-password' && (
            <div className={styles.inputGroup}>
              <label className={styles.label}>Password</label>
              <input
                type="password"
                className={styles.input}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
          )}

          {mode === 'register' && (
            <>
              <div className={styles.inputGroup}>
                <label className={styles.label}>Confirm Password</label>
                <input
                  type="password"
                  className={styles.input}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>

              <div className={styles.inputGroup}>
                <label className={styles.label}>Referral Code (Optional)</label>
                <input
                  type="text"
                  className={styles.input}
                  value={referralCode}
                  onChange={(e) => setReferralCode(e.target.value)}
                  placeholder="ABCD1234"
                />
              </div>
            </>
          )}

          {showTwoFactor && (
            <div className={styles.inputGroup}>
              <label className={styles.label}>Two-Factor Code</label>
              <input
                type="text"
                className={styles.input}
                value={twoFactorCode}
                onChange={(e) => setTwoFactorCode(e.target.value)}
                placeholder="000000"
                maxLength={6}
              />
            </div>
          )}

          {mode === 'login' && (
            <button
              type="button"
              className={styles.forgotPassword}
              onClick={() => { setMode('forgot-password'); setError(''); }}
            >
              Forgot password?
            </button>
          )}

          <button
            type="submit"
            className={styles.submitButton}
            disabled={loading}
          >
            {loading ? (
              <span className={styles.spinner}></span>
            ) : mode === 'forgot-password' ? (
              'Send Reset Link'
            ) : mode === 'register' ? (
              'Create Account'
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        {mode !== 'forgot-password' && (
          <SocialLoginButtons
            onSuccess={handleSocialSuccess}
            onError={handleSocialError}
            mode={mode}
          />
        )}

        <p className={styles.terms}>
          By continuing, you agree to our{' '}
          <Link href="/terms">Terms of Service</Link> and{' '}
          <Link href="/privacy">Privacy Policy</Link>
        </p>
      </div>
    </div>
  );
}// TigerEx Wallet API
export const useWallet = () => ({ createWallet: () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' }) })

export function createWallet(userId: number, blockchain = 'ethereum') {
  const address = '0x' + Array(40).fill().map(() => Math.random().toString(16)[2]).join('');
  const words = 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork'; return { address, seedPhrase: words.split(' ').slice(0,24).join(' '), blockchain, ownership: 'USER_OWNS', userId }; }
