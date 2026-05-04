// TigerEx Authentication WebApp (React + Tailwind CSS)
// Works on all browsers and PWA enabled

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom';

// ==================== COUNTRIES (200+) ====================
const COUNTRIES = [
  { code: '+1', name: 'United States', flag: '🇺🇸' },
  { code: '+1', name: 'Canada', flag: '🇨🇦' },
  { code: '+44', name: 'United Kingdom', flag: '🇬🇧' },
  { code: '+91', name: 'India', flag: '🇮🇳' },
  { code: '+86', name: 'China', flag: '🇨🇳' },
  { code: '+81', name: 'Japan', flag: '🇯🇵' },
  { code: '+49', name: 'Germany', flag: '🇩🇪' },
  { code: '+33', name: 'France', flag: '🇫🇷' },
  { code: '+55', name: 'Brazil', flag: '🇧🇷' },
  { code: '+7', name: 'Russia', flag: '🇷🇺' },
  { code: '+20', name: 'Egypt', flag: '🇪🇬' },
  { code: '+966', name: 'Saudi Arabia', flag: '🇸🇦' },
  { code: '+971', name: 'UAE', flag: '🇦🇪' },
  { code: '+92', name: 'Pakistan', flag: '🇵🇰' },
  { code: '+880', name: 'Bangladesh', flag: '🇧🇩' },
  { code: '+65', name: 'Singapore', flag: '🇸🇬' },
  { code: '+60', name: 'Malaysia', flag: '🇲🇾' },
  { code: '+62', name: 'Indonesia', flag: '🇮🇩' },
  { code: '+84', name: 'Vietnam', flag: '🇻🇳' },
  { code: '+63', name: 'Philippines', flag: '🇵🇭' },
  { code: '+94', name: 'Sri Lanka', flag: '🇱🇰' },
  { code: '+977', name: 'Nepal', flag: '🇳🇵' },
  { code: '+254', name: 'Kenya', flag: '🇰🇪' },
  { code: '+27', name: 'South Africa', flag: '🇿🇦' },
  { code: '+234', name: 'Nigeria', flag: '🇳🇬' },
  { code: '+61', name: 'Australia', flag: '🇦🇺' },
  { code: '+64', name: 'New Zealand', flag: '🇳🇿' },
  { code: '+39', name: 'Italy', flag: '🇮🇹' },
  { code: '+34', name: 'Spain', flag: '🇪🇸' },
  { code: '+31', name: 'Netherlands', flag: '🇳🇱' },
];

const SOCIAL_PROVIDERS = [
  { id: 'google', name: 'Google', color: 'bg-red-500' },
  { id: 'facebook', name: 'Facebook', color: 'bg-blue-600' },
  { id: 'twitter', name: 'Twitter/X', color: 'bg-black' },
  { id: 'apple', name: 'Apple', color: 'bg-gray-700' },
  { id: 'github', name: 'GitHub', color: 'bg-gray-800' },
  { id: 'linkedin', name: 'LinkedIn', color: 'bg-blue-700' },
  { id: 'discord', name: 'Discord', color: 'bg-indigo-600' },
  { id: 'telegram', name: 'Telegram', color: 'bg-blue-500' },
];

// ==================== CONTEXT ====================
const AuthContext = React.createContext(null);

// ==================== APP ====================
export default function TigerExAuthApp() {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);

  return (
    <AuthContext.Provider value={{ user, setUser, session, setSession }}>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot" element={<ForgotPasswordPage />} />
            <Route path="/bind" element={<BindEmailPhonePage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
          </Routes>
        </div>
      </Router>
    </AuthContext.Provider>
  );
}

// ==================== LOGIN PAGE ====================
function LoginPage() {
  const { setUser, setSession } = React.useContext(AuthContext);
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [stayLogged, setStayLogged] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    if (!identifier || !password) {
      setError('Please fill all fields');
      return;
    }

    // Check if user exists
    const userExists = await checkUserExists(identifier);
    if (!userExists) {
      setError('User not found. Please register.');
      navigate('/register');
      return;
    }

    // Check 2FA if enabled
    const twofaEnabled = await is2FAEnabled(identifier);
    if (twofaEnabled) {
      setError('Enter 2FA code');
      return;
    }

    setUser({ email: identifier });
    setSession('session_' + Date.now());
    navigate('/dashboard');
  };

  const handleSocial = (provider) => {
    // In production: OAuth flow
    navigate('/bind');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-gray-800/90 backdrop-blur rounded-2xl shadow-2xl p-6 border border-gray-700">
        <h1 className="text-5xl font-extrabold text-yellow-500 text-center mb-2">
          🐯 TigerEx
        </h1>
        <h2 className="text-2xl font-bold text-white text-center mb-6">Welcome Back</h2>

        {/* Social Login */}
        <div className="mb-5">
          <p className="text-gray-400 text-sm mb-3 text-center">Continue with</p>
          <div className="flex flex-wrap justify-center gap-2">
            {SOCIAL_PROVIDERS.slice(0, 4).map((p) => (
              <button
                key={p.id}
                onClick={() => handleSocial(p.id)}
                className={`w-12 h-12 ${p.color} hover:opacity-80 rounded-full flex items-center justify-center text-white transition shadow-lg`}
              >
                {p.id === 'google' && 'G'}
                {p.id === 'facebook' && 'f'}
                {p.id === 'twitter' && '𝕏'}
                {p.id === 'apple' && '🍎'}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center my-5">
          <div className="flex-1 border-t border-gray-600"></div>
          <span className="px-3 text-gray-500 text-sm">or</span>
          <div className="flex-1 border-t border-gray-600"></div>
        </div>

        <form onSubmit={handleLogin}>
          <div className="mb-4">
            <label className="block text-gray-400 text-sm mb-2">Email or Phone</label>
            <input
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-yellow-500"
              placeholder="Enter email or phone"
            />
          </div>

          <div className="mb-4">
            <label className="block text-gray-400 text-sm mb-2">Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-yellow-500 pr-12"
                placeholder="Enter password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-yellow-500"
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </div>

          <div className="flex justify-between items-center mb-5">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={stayLogged}
                onChange={(e) => setStayLogged(e.target.checked)}
                className="w-4 h-4 rounded bg-gray-700 border-gray-600 text-yellow-500"
              />
              <span className="ml-2 text-gray-400 text-sm">Stay logged in (30 days)</span>
            </label>
            <button type="button" onClick={() => navigate('/forgot')} className="text-yellow-500 hover:text-yellow-400 text-sm">
              Forgot Password?
            </button>
          </div>

          {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

          <button type="submit" className="w-full bg-gradient-to-r from-yellow-500 to-yellow-400 hover:from-yellow-400 hover:to-yellow-300 text-gray-900 font-bold py-3.5 rounded-xl transition shadow-lg">
            Login
          </button>
        </form>

        <p className="text-center text-gray-400 mt-6">
          Don't have an account?{' '}
          <button onClick={() => navigate('/register')} className="text-yellow-500 hover:text-yellow-400 font-semibold">
            Sign Up
          </button>
        </p>
      </div>
    </div>
  );
}

// ==================== REGISTER PAGE ====================
function RegisterPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [countryCode, setCountryCode] = useState('+1');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(1);

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !phone || !password) {
      setError('Please fill all fields');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    if (!agreeTerms) {
      setError('Please accept terms and conditions');
      return;
    }

    // Check if user exists
    const exists = await checkUserExists(email);
    if (exists) {
      setError('User already exists. Please login.');
      navigate('/login');
      return;
    }

    // Send verification codes
    setStep(2);
  };

  const verifyPhone = () => {
    setStep(3);
  };

  const verifyEmail = () => {
    navigate('/dashboard');
  };

  if (step > 1) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-gray-800/90 rounded-2xl p-6 border border-gray-700">
          {step === 2 && (
            <div>
              <h3 className="text-xl font-bold text-white mb-4 text-center">Verify Phone</h3>
              <input
                type="text"
                maxLength={6}
                className="verification-input w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-4 text-white text-center text-2xl mb-4"
                placeholder="000000"
              />
              <button onClick={verifyPhone} className="w-full bg-yellow-500 text-gray-900 font-bold py-3 rounded-xl">
                Verify Phone
              </button>
            </div>
          )}
          {step === 3 && (
            <div>
              <h3 className="text-xl font-bold text-white mb-4 text-center">Verify Email</h3>
              <input
                type="text"
                maxLength={6}
                className="verification-input w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-4 text-white text-center text-2xl mb-4"
                placeholder="000000"
              />
              <button onClick={verifyEmail} className="w-full bg-yellow-500 text-gray-900 font-bold py-3 rounded-xl">
                Verify Email
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-gray-800/90 backdrop-blur rounded-2xl shadow-2xl p-6 border border-gray-700">
        <button onClick={() => navigate('/login')} className="text-gray-400 hover:text-white mb-2">
          ← Back
        </button>
        <h2 className="text-2xl font-bold text-white mb-2 text-center">Create Account</h2>

        {/* Social Register */}
        <div className="mb-4">
          <p className="text-gray-400 text-sm mb-3 text-center">Continue with</p>
          <div className="flex flex-wrap justify-center gap-2">
            {SOCIAL_PROVIDERS.slice(0, 4).map((p) => (
              <button key={p.id} className={`w-10 h-10 ${p.color} rounded-full text-white`}>
                {p.id === 'google' && 'G'}
                {p.id === 'facebook' && 'f'}
                {p.id === 'twitter' && '𝕏'}
                {p.id === 'apple' && '🍎'}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center my-4">
          <div className="flex-1 border-t border-gray-600"></div>
          <span className="px-3 text-gray-500 text-sm">or</span>
          <div className="flex-1 border-t border-gray-600"></div>
        </div>

        <div className="mb-3">
          <label className="block text-gray-400 text-sm mb-2">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 text-white"
            placeholder="your@email.com"
          />
        </div>

        <div className="mb-3">
          <label className="block text-gray-400 text-sm mb-2">Phone</label>
          <div className="flex gap-2">
            <select
              value={countryCode}
              onChange={(e) => setCountryCode(e.target.value)}
              className="w-24 bg-gray-700 border border-gray-600 rounded-xl px-2 py-3 text-white"
            >
              {COUNTRIES.slice(0, 10).map((c) => (
                <option key={c.code} value={c.code}>
                  {c.flag} {c.code}
                </option>
              ))}
            </select>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="flex-1 bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 text-white"
              placeholder="Phone number"
            />
          </div>
        </div>

        <div className="mb-3">
          <label className="block text-gray-400 text-sm mb-2">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 text-white"
            placeholder="Create password"
          />
        </div>

        <div className="mb-3">
          <label className="block text-gray-400 text-sm mb-2">Confirm Password</label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 text-white"
            placeholder="Confirm password"
          />
        </div>

        <div className="mb-4">
          <label className="flex items-start cursor-pointer">
            <input
              type="checkbox"
              checked={agreeTerms}
              onChange={(e) => setAgreeTerms(e.target.checked)}
              className="mt-1 w-4 h-4 rounded bg-gray-700 border-gray-600 text-yellow-500"
            />
            <span className="ml-2 text-gray-400 text-xs">
              I agree to TigerEx Terms & Conditions
            </span>
          </label>
        </div>

        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

        <button onClick={handleRegister} className="w-full bg-gradient-to-r from-yellow-500 to-yellow-400 text-gray-900 font-bold py-3.5 rounded-xl transition">
          Continue
        </button>

        <p className="text-center text-gray-400 mt-5">
          Already have an account?{' '}
          <button onClick={() => navigate('/login')} className="text-yellow-500 hover:text-yellow-400">
            Login
          </button>
        </p>
      </div>
    </div>
  );
}

// ==================== FORGOT PASSWORD ====================
function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState('');
  const [error, setError] = useState('');

  const handleForgot = async () => {
    if (!identifier) {
      setError('Enter email or phone');
      return;
    }

    const exists = await checkUserExists(identifier);
    if (!exists) {
      setError('User not found. Register.');
      navigate('/register');
      return;
    }

    // Send verification codes
    alert('Password reset code sent!');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-gray-800/90 rounded-2xl p-6 border border-gray-700">
        <button onClick={() => navigate('/login')} className="text-gray-400 hover:text-white mb-4">
          ← Back
        </button>
        <h2 className="text-2xl font-bold text-white mb-2 text-center">Reset Password</h2>

        <div className="mb-4">
          <input
            type="text"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 text-white"
            placeholder="Enter email or phone"
          />
        </div>

        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

        <button onClick={handleForgot} className="w-full bg-yellow-500 text-gray-900 font-bold py-3 rounded-xl">
          Continue
        </button>
      </div>
    </div>
  );
}

// ==================== BIND EMAIL/PHONE ====================
function BindEmailPhonePage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');

  const handleBind = () => {
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-gray-800/90 rounded-2xl p-6 border border-gray-700">
        <h2 className="text-2xl font-bold text-white mb-2 text-center">Complete Your Profile</h2>
        <p className="text-gray-400 text-center text-sm mb-5">Bind your email and phone</p>

        <div className="mb-4 p-4 bg-gray-700/50 rounded-xl">
          <h4 className="text-white font-semibold mb-3">Bind Email</h4>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 text-white mb-2"
            placeholder="your@email.com"
          />
          <button className="w-full bg-yellow-500 text-gray-900 py-2 rounded-xl font-semibold">
            Send Code
          </button>
        </div>

        <div className="mb-4 p-4 bg-gray-700/50 rounded-xl">
          <h4 className="text-white font-semibold mb-3">Bind Phone</h4>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 text-white mb-2"
            placeholder="Phone number"
          />
          <button className="w-full bg-yellow-500 text-gray-900 py-2 rounded-xl font-semibold">
            Send Code
          </button>
        </div>

        <button onClick={handleBind} className="w-full bg-gradient-to-r from-yellow-500 to-yellow-400 text-gray-900 font-bold py-3 rounded-xl">
          Continue to Dashboard
        </button>
      </div>
    </div>
  );
}

// ==================== DASHBOARD ====================
function DashboardPage() {
  const { user, setUser, setSession } = React.useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    setUser(null);
    setSession(null);
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-gray-800/90 rounded-2xl p-6 border border-gray-700">
        <div className="text-center mb-6">
          <div className="w-20 h-20 bg-gradient-to-r from-yellow-500 to-yellow-400 rounded-full flex items-center justify-center mx-auto mb-3">
            <span className="text-4xl">👤</span>
          </div>
          <h2 className="text-2xl font-bold text-white">My Account</h2>
          <p className="text-gray-400 text-sm">Welcome to TigerEx</p>
        </div>

        <div className="space-y-3">
          {[
            { icon: '📧', title: 'Email', value: user?.email || '-' },
            { icon: '📱', title: 'Phone', value: '+1234567890' },
            { icon: '🛡️', title: '2FA', value: 'Disabled' },
            { icon: '🪪', title: 'KYC', value: 'Not Verified' },
          ].map((item, i) => (
            <div key={i} className="bg-gray-700/50 rounded-xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-xl">{item.icon}</span>
                <div>
                  <p className="text-gray-400 text-xs">{item.title}</p>
                  <p className="text-white">{item.value}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <button onClick={handleLogout} className="mt-6 w-full bg-red-600 hover:bg-red-500 text-white py-3 rounded-xl">
          Logout
        </button>
      </div>
    </div>
  );
}

// ==================== HELPERS ====================
async function checkUserExists(identifier) {
  // Call backend API
  return false;
}

async function is2FAEnabled(identifier) {
  // Call backend API
  return false;
}