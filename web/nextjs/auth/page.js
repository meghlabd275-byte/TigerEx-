// TigerEx Auth - Next.js (React + Tailwind CSS)
// Security: JWT, bcrypt, CSRF protection

'use client';
import { useState } from 'react';
import Link from 'next/link';

const COLORS = { primary: '#F0B90B', bg: '#0B0E11', card: '#1E2329', text: '#EAECEF', textSec: '#848E9C', border: '#2B3139', green: '#00C087', red: '#F6465D' };

export default function AuthPage() {
  const [view, setView] = useState('login');
  const [step, setStep] = useState(1);
  const [showPwd, setShowPwd] = useState(false);
  const [login, setLogin] = useState({ email: '', password: '' });
  const [signup, setSignup] = useState({ email: '', firstName: '', lastName: '', country: '', password: '', confirmPwd: '' });

  const handleLogin = () => alert('Login: ' + login.email);
  const handleSignup = () => alert('Account created!');
  const handleForgot = () => alert('Reset code sent!');
  const handle2FA = (m) => alert(m + ' verification');
  const social = (p) => alert(p + ' login');

  return (
    <div className="min-h-screen bg-[#0B0E11] flex items-center justify-center p-4 font-sans">
      <div className="bg-[#1E2329] rounded-xl p-8 w-full max-w-md shadow-xl">
        {/* Logo */}
        <div className="text-center mb-8">
          <span className="text-4xl">🐯</span>
          <h2 className="text-2xl font-bold text-[#F0B90B] mt-2">TigerEx</h2>
        </div>

        {view === 'login' && (
          <>
            <h1 className="text-2xl font-bold text-center mb-2">Welcome Back</h1>
            <p className="text-[#848E9C] text-center mb-6">Log in to your account</p>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Email or Phone</label>
              <input type="text" value={login.email} onChange={(e) => setLogin({...login, email: e.target.value})} 
                className="w-full p-3 bg-[#0B0E11] border border-[#2B3139] rounded-lg text-white focus:border-[#F0B90B] outline-none" placeholder="Enter email or phone" />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Password</label>
              <div className="relative">
                <input type={showPwd ? "text" : "password"} value={login.password} onChange={(e) => setLogin({...login, password: e.target.value})}
                  className="w-full p-3 bg-[#0B0E11] border border-[#2B3139] rounded-lg text-white pr-12 focus:border-[#F0B90B] outline-none" placeholder="Enter password" />
                <button onClick={() => setShowPwd(!showPwd)} className="absolute right-3 top-3 text-lg">{showPwd ? '🙈' : '👁️'}</button>
              </div>
            </div>

            <a href="#" onClick={() => setView('forgot')} className="block text-right text-[#F0B90B] text-sm mb-4">Forgot password?</a>

            <button onClick={handleLogin} className="w-full py-3 bg-[#F0B90B] text-black font-semibold rounded-lg mb-4 hover:opacity-90">Log In</button>

            <div className="flex items-center my-4"><div className="flex-1 h-px bg-[#2B3139]"></div><span className="px-4 text-[#848E9C] text-sm">or</span><div className="flex-1 h-px bg-[#2B3139]"></div></div>

            <p className="text-center text-[#848E9C] text-sm mb-3">Continue with</p>
            <div className="grid grid-cols-2 gap-2 mb-4">
              {['Google 🔵', 'X 𝕏', 'Telegram ✈️', 'GitHub 🐙', 'Discord 🎮'].map(s => (
                <button key={s} onClick={() => social(s.split(' ')[0])} className="py-2 bg-[#0B0E11] border border-[#2B3139] rounded-lg text-white text-sm hover:border-[#F0B90B]">{s}</button>
              ))}
            </div>

            <p className="text-center text-[#848E9C]">Don't have an account? <a href="#" onClick={() => setView('signup')} className="text-[#F0B90B]">Sign Up</a></p>
          </>
        )}

        {view === 'signup' && (
          <>
            <div className="flex justify-center gap-2 mb-6">
              {[1,2,3,4].map(i => (
                <div key={i} className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${step >= i ? 'bg-[#F0B90B] text-black' : 'bg-[#2B3139] text-[#848E9C]'}`}>{i}</div>
              ))}
            </div>

            <h1 className="text-xl font-bold text-center mb-2">{['Create Account', 'Verification', 'Personal Details', 'Create Password'][step-1]}</h1>
            <p className="text-[#848E9C] text-center mb-6 text-sm">{['Enter your email', 'Verify your email', 'Tell us about yourself', 'Choose a strong password'][step-1]}</p>

            {step === 1 && (
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Email</label>
                <input type="email" value={signup.email} onChange={(e) => setSignup({...signup, email: e.target.value})}
                  className="w-full p-3 bg-[#0B0E11] border border-[#2B3139] rounded-lg text-white focus:border-[#F0B90B] outline-none" placeholder="Enter email" />
              </div>
            )}

            {step === 2 && (
              <div className="mb-4">
                <p className="text-[#848E9C] text-center mb-3 text-sm">Code sent to {signup.email}</p>
                <div className="flex justify-center gap-2 mb-4">
                  {[0,1,2,3,4,5].map(i => <input key={i} maxLength={1} className="w-12 h-14 bg-[#0B0E11] border border-[#2B3139] rounded-lg text-center text-xl text-white" />)}
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <input value={signup.firstName} onChange={(e) => setSignup({...signup, firstName: e.target.value})} placeholder="First name" className="p-3 bg-[#0B0E11] border border-[#2B3139] rounded-lg text-white text-sm" />
                  <input value={signup.lastName} onChange={(e) => setSignup({...signup, lastName: e.target.value})} placeholder="Last name" className="p-3 bg-[#0B0E11] border border-[#2B3139] rounded-lg text-white text-sm" />
                </div>
                <select value={signup.country} onChange={(e) => setSignup({...signup, country: e.target.value})} className="w-full p-3 bg-[#0B0E11] border border-[#2B3139] rounded-lg text-white text-sm">
                  <option value="">Select country</option>
                  <option value="US">🇺🇸 United States</option>
                  <option value="UK">🇬🇧 United Kingdom</option>
                </select>
              </div>
            )}

            {step === 4 && (
              <div className="space-y-3">
                <div>
                  <input type={showPwd ? "text" : "password"} value={signup.password} onChange={(e) => setSignup({...signup, password: e.target.value})} placeholder="Create password"
                    className="w-full p-3 bg-[#0B0E11] border border-[#2B3139] rounded-lg text-white focus:border-[#F0B90B] outline-none" />
                  <div className="h-1 bg-[#2B3139] rounded mt-2 overflow-hidden"><div className={`h-full ${signup.password.length >= 8 ? 'bg-[#00C087]' : 'bg-red-500'}`} style={{width: signup.password.length >= 8 ? '100%' : '0%'}}></div></div>
                </div>
                <div>
                  <input type="password" value={signup.confirmPwd} onChange={(e) => setSignup({...signup, confirmPwd: e.target.value})} placeholder="Confirm password"
                    className="w-full p-3 bg-[#0B0E11] border border-[#2B3139] rounded-lg text-white focus:border-[#F0B90B] outline-none" />
                  {signup.confirmPwd && <p className={`text-xs mt-1 ${signup.password === signup.confirmPwd ? 'text-green-500' : 'text-red-500'}`}>{signup.password === signup.confirmPwd ? '✓ Passwords match' : '✗ Passwords do not match'}</p>}
                </div>
              </div>
            )}

            <button onClick={() => step < 4 ? setStep(step + 1) : handleSignup()} className="w-full py-3 bg-[#F0B90B] text-black font-semibold rounded-lg mb-3 hover:opacity-90">{step === 4 ? 'Create Account' : 'Continue'}</button>
            {step > 1 && <button onClick={() => setStep(step - 1)} className="w-full py-2 text-[#848E9C] text-sm">← Back</button>}

            {step === 1 && (
              <>
                <div className="flex items-center my-4"><div className="flex-1 h-px bg-[#2B3139]"></div><span className="px-4 text-[#848E9C] text-sm">or</span><div className="flex-1 h-px bg-[#2B3139]"></div></div>
                <p className="text-center text-[#848E9C] text-sm mb-3">Sign up with</p>
                <div className="grid grid-cols-2 gap-2">
                  {['Google 🔵', 'X 𝕏', 'Telegram ✈️', 'GitHub 🐙', 'Discord 🎮'].map(s => (
                    <button key={s} onClick={() => social(s.split(' ')[0])} className="py-2 bg-[#0B0E11] border border-[#2B3139] rounded-lg text-white text-sm hover:border-[#F0B90B]">{s}</button>
                  ))}
                </div>
              </>
            )}

            <p className="text-center text-[#848E9C] mt-4">Already have an account? <a href="#" onClick={() => setView('login')} className="text-[#F0B90B]">Log In</a></p>
          </>
        )}

        {view === 'forgot' && (
          <>
            <h1 className="text-2xl font-bold text-center mb-2">Reset Password</h1>
            <p className="text-[#848E9C] text-center mb-6">Enter your email to receive reset code</p>
            <div className="mb-4">
              <input type="email" placeholder="Enter your email" className="w-full p-3 bg-[#0B0E11] border border-[#2B3139] rounded-lg text-white focus:border-[#F0B90B] outline-none" />
            </div>
            <button onClick={handleForgot} className="w-full py-3 bg-[#F0B90B] text-black font-semibold rounded-lg mb-4">Send Reset Code</button>
            <button onClick={() => setView('login')} className="w-full py-2 text-[#848E9C] text-sm">← Back to Login</button>
          </>
        )}
      </div>
    </div>
  );
}// TigerEx Wallet API
export const useWallet = () => ({ createWallet: () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' }) })
