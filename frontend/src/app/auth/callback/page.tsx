'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function AuthCallbackPage() {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [error, setError] = useState('');
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const handleCallback = async () => {
      if (!searchParams) {
        setStatus('error');
        setError('Invalid URL parameters');
        return;
      }
      
      const token = searchParams.get('token');
      const refreshToken = searchParams.get('refreshToken');
      const errorParam = searchParams.get('error');

      if (errorParam) {
        setStatus('error');
        setError(decodeURIComponent(errorParam));
        return;
      }

      if (!token) {
        setStatus('error');
        setError('No authentication token received');
        return;
      }

      try {
        // Store tokens
        localStorage.setItem('token', token);
        if (refreshToken) {
          localStorage.setItem('refreshToken', refreshToken);
        }

        // Fetch user data
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          localStorage.setItem('user', JSON.stringify(data.user));
          setStatus('success');
          
          // Redirect to dashboard after short delay
          setTimeout(() => {
            const redirect = searchParams.get('redirect') || '/dashboard';
            router.push(redirect);
          }, 1500);
        } else {
          throw new Error('Failed to fetch user data');
        }
      } catch (err: any) {
        setStatus('error');
        setError(err.message || 'Authentication failed');
      }
    };

    handleCallback();
  }, [searchParams, router]);

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #0f0f0f 0%, #1a1a2e 50%, #0f0f0f 100%)',
    }}>
      <div style={{
        textAlign: 'center',
        padding: '40px',
        background: 'rgba(26, 26, 46, 0.9)',
        borderRadius: '24px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
      }}>
        {status === 'loading' && (
          <>
            <div style={{
              width: '50px',
              height: '50px',
              border: '3px solid transparent',
              borderTopColor: '#10B981',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 20px',
            }} />
            <p style={{ color: '#fff', fontSize: '18px' }}>Completing authentication...</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
            <h2 style={{ color: '#10B981', fontSize: '24px', marginBottom: '8px' }}>
              Authentication Successful!
            </h2>
            <p style={{ color: '#9CA3AF' }}>Redirecting to dashboard...</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>❌</div>
            <h2 style={{ color: '#EF4444', fontSize: '24px', marginBottom: '8px' }}>
              Authentication Failed
            </h2>
            <p style={{ color: '#9CA3AF', marginBottom: '20px' }}>{error}</p>
            <button
              onClick={() => router.push('/auth')}
              style={{
                padding: '12px 24px',
                background: 'linear-gradient(135deg, #10B981, #059669)',
                border: 'none',
                borderRadius: '10px',
                color: '#fff',
                fontSize: '16px',
                cursor: 'pointer',
              }}
            >
              Try Again
            </button>
          </>
        )}
      </div>

      <style jsx>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}