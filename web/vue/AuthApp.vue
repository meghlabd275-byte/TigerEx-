<template>
  <div class="auth-container">
    <!-- Login -->
    <div v-if="currentView === 'login'" class="auth-card">
      <div class="logo">🐯 <span>TigerEx</span></div>
      <h1>Welcome Back</h1>
      <p class="subtitle">Log in to your account</p>
      
      <div class="input-group">
        <label>Email or Phone</label>
        <input type="text" v-model="login.email" placeholder="Enter email or phone" />
      </div>
      
      <div class="input-group">
        <label>Password</label>
        <div class="password-wrapper">
          <input :type="showPassword ? 'text' : 'password'" v-model="login.password" placeholder="Enter password" />
          <button class="toggle-btn" @click="showPassword = !showPassword">{{ showPassword ? '🙈' : '👁️' }}</button>
        </div>
      </div>
      
      <a href="#" class="forgot-link" @click.prevent="currentView = 'forgot'">Forgot password?</a>
      
      <button class="submit-btn" @click="handleLogin">Log In</button>
      
      <div class="divider"><span>or</span></div>
      
      <p class="social-label">Continue with</p>
      <div class="social-btns">
        <button @click="socialLogin('google')">🔵 Google</button>
        <button @click="socialLogin('x')">𝕏 X</button>
        <button @click="socialLogin('telegram')">✈️ Telegram</button>
        <button @click="socialLogin('github')">🐙 GitHub</button>
        <button @click="socialLogin('discord')">🎮 Discord</button>
      </div>
      
      <p class="footer-text">Don't have an account? <a href="#" @click.prevent="currentView = 'signup'">Sign Up</a></p>
    </div>
    
    <!-- SignUp -->
    <div v-if="currentView === 'signup'" class="auth-card">
      <div class="step-indicator">
        <span :class="{ active: step >= 1 }">1</span>
        <span :class="{ active: step >= 2 }">2</span>
        <span :class="{ active: step >= 3 }">3</span>
        <span :class="{ active: step >= 4 }">4</span>
      </div>
      
      <h1>{{ stepTitles[step - 1] }}</h1>
      <p class="subtitle">{{ stepSubtitles[step - 1] }}</p>
      
      <!-- Step 1: Email -->
      <div v-if="step === 1" class="step-content">
        <div class="input-group">
          <label>Email</label>
          <input type="email" v-model="signup.email" placeholder="Enter your email" />
        </div>
        <button class="submit-btn" @click="step = 2">Continue</button>
      </div>
      
      <!-- Step 2: Verify -->
      <div v-if="step === 2" class="step-content">
        <p class="otp-info">Code sent to {{ signup.email }}</p>
        <div class="otp-inputs">
          <input v-for="i in 6" :key="i" type="text" maxlength="1" class="otp-input" />
        </div>
        <button class="submit-btn" @click="step = 3">Verify</button>
        <p class="resend-link"><a href="#">Resend Code</a></p>
      </div>
      
      <!-- Step 3: Personal Details -->
      <div v-if="step === 3" class="step-content">
        <div class="input-row">
          <div class="input-group">
            <label>First Name</label>
            <input type="text" v-model="signup.firstName" placeholder="First name" />
          </div>
          <div class="input-group">
            <label>Last Name</label>
            <input type="text" v-model="signup.lastName" placeholder="Last name" />
          </div>
        </div>
        <div class="input-group">
          <label>Country</label>
          <select v-model="signup.country">
            <option value="">Select country</option>
            <option value="US">🇺🇸 United States</option>
            <option value="UK">🇬🇧 United Kingdom</option>
            <option value="OTHER">🌍 Other</option>
          </select>
        </div>
        <button class="submit-btn" @click="step = 4">Continue</button>
      </div>
      
      <!-- Step 4: Password -->
      <div v-if="step === 4" class="step-content">
        <div class="input-group">
          <label>Password</label>
          <div class="password-wrapper">
            <input :type="showPassword ? 'text' : 'password'" v-model="signup.password" placeholder="Create password" />
            <button class="toggle-btn" @click="showPassword = !showPassword">{{ showPassword ? '🙈' : '👁️' }}</button>
          </div>
          <div class="strength-bar"><div :style="{ width: signup.password.length >= 8 ? '100%' : '0%' }"></div></div>
        </div>
        <div class="input-group">
          <label>Confirm Password</label>
          <input type="password" v-model="signup.confirmPassword" placeholder="Confirm password" />
          <p class="match-text" :class="{ valid: signup.password === signup.confirmPassword && signup.confirmPassword }">
            {{ signup.password === signup.confirmPassword && signup.confirmPassword ? '✓ Passwords match' : '' }}
          </p>
        </div>
        <button class="submit-btn" @click="handleSignup">Create Account</button>
      </div>
      
      <button v-if="step > 1" class="back-btn" @click="step--">← Back</button>
      
      <div v-if="step === 1" class="divider"><span>or</span></div>
      <div v-if="step === 1">
        <p class="social-label">Sign up with</p>
        <div class="social-btns">
          <button @click="socialSignup('google')">🔵 Google</button>
          <button @click="socialSignup('x')">𝕏 X</button>
          <button @click="socialSignup('telegram')">✈️ Telegram</button>
          <button @click="socialSignup('github')">🐙 GitHub</button>
          <button @click="socialSignup('discord')">🎮 Discord</button>
        </div>
      </div>
      
      <p class="footer-text">Already have an account? <a href="#" @click.prevent="currentView = 'login'">Log In</a></p>
    </div>
    
    <!-- Forgot Password -->
    <div v-if="currentView === 'forgot'" class="auth-card">
      <h1>Reset Password</h1>
      <p class="subtitle">Enter your email to receive reset code</p>
      
      <div class="input-group">
        <label>Email</label>
        <input type="email" v-model="forgot.email" placeholder="Enter your email" />
      </div>
      
      <button class="submit-btn" @click="handleForgot">Send Reset Code</button>
      
      <button class="back-btn" @click="currentView = 'login'">← Back to Login</button>
    </div>
    
    <!-- 2FA Reset -->
    <div v-if="currentView === '2fa-reset'" class="auth-card">
      <h1>Reset 2FA</h1>
      <p class="subtitle">Choose a method to verify identity</p>
      
      <div class="info-box">
        <h3>⚠️ Important</h3>
        <p>Resetting 2FA will disable this security feature.</p>
      </div>
      
      <div class="method-cards">
        <div class="method-card" @click="handle2FAReset('email')">📧 Email Verification</div>
        <div class="method-card" @click="handle2FAReset('phone')">📱 SMS Verification</div>
        <div class="method-card" @click="handle2FAReset('id')">🪪 Upload ID</div>
        <div class="method-card" @click="handle2FAReset('support')">📞 Contact Support</div>
      </div>
      
      <button class="back-btn" @click="currentView = 'login'">← Back to Login</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthApp',
  data() {
    return {
      currentView: 'login',
      step: 1,
      stepTitles: ['Create Account', 'Verification', 'Personal Details', 'Create Password'],
      stepSubtitles: ['Enter your email', 'Verify your email', 'Tell us about yourself', 'Choose a strong password'],
      showPassword: false,
      login: { email: '', password: '' },
      signup: { email: '', firstName: '', lastName: '', country: '', password: '', confirmPassword: '' },
      forgot: { email: '' }
    }
  },
  methods: {
    handleLogin() { alert('Login: ' + this.login.email); },
    handleSignup() { alert('Account created!'); },
    handleForgot() { alert('Reset code sent!'); },
    handle2FAReset(method) { alert(method + ' verification selected'); },
    socialLogin(provider) { alert(provider + ' login'); },
    socialSignup(provider) { alert(provider + ' signup'); }
  }
}
</script>

<style scoped>
:root { --primary: #F0B90B; --bg: #0B0E11; --card: #1E2329; --text: #EAECEF; --text-secondary: #848E9C; --border: #2B3139; --green: #00C087; }
.auth-container { min-height: 100vh; background: var(--bg); display: flex; align-items: center; justify-content: center; padding: 20px; font-family: 'Inter', sans-serif; }
.auth-card { background: var(--card); border-radius: 12px; padding: 32px; width: 100%; max-width: 420px; box-shadow: 0 4px 24px rgba(0,0,0,0.2); }
.logo { text-align: center; font-size: 32px; margin-bottom: 24px; }
.logo span { color: var(--primary); }
h1 { font-size: 24px; font-weight: 700; margin-bottom: 8px; color: var(--text); text-align: center; }
.subtitle { color: var(--text-secondary); margin-bottom: 24px; text-align: center; font-size: 14px; }
.input-group { margin-bottom: 16px; }
.input-group label { display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: var(--text); }
.input-group input, .input-group select { width: 100%; padding: 12px 16px; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 14px; outline: none; }
.input-group input:focus { border-color: var(--primary); }
.input-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.password-wrapper { position: relative; }
.password-wrapper input { padding-right: 48px; }
.toggle-btn { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; font-size: 18px; }
.forgot-link { display: block; text-align: right; color: var(--primary); font-size: 14px; margin-bottom: 24px; text-decoration: none; }
.submit-btn { width: 100%; padding: 14px; background: var(--primary); color: #000; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; margin-bottom: 16px; }
.back-btn { display: block; margin: 16px auto 0; background: none; border: none; color: var(--text-secondary); cursor: pointer; font-size: 14px; }
.divider { display: flex; align-items: center; margin: 24px 0; }
.divider::before, .divider::after { content: ''; flex: 1; height: 1px; background: var(--border); }
.divider span { padding: 0 16px; color: var(--text-secondary); font-size: 13px; }
.social-label { text-align: center; color: var(--text-secondary); font-size: 13px; margin-bottom: 12px; }
.social-btns { display: flex; flex-direction: column; gap: 10px; }
.social-btns button { padding: 12px; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 14px; cursor: pointer; }
.social-btns button:hover { border-color: var(--primary); }
.footer-text { text-align: center; margin-top: 24px; color: var(--text-secondary); font-size: 14px; }
.footer-text a { color: var(--primary); text-decoration: none; }
.step-indicator { display: flex; justify-content: center; gap: 8px; margin-bottom: 24px; }
.step-indicator span { width: 32px; height: 32px; border-radius: 50%; background: var(--border); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; color: var(--text-secondary); }
.step-indicator span.active { background: var(--primary); color: #000; }
.step-content { margin-bottom: 16px; }
.otp-inputs { display: flex; gap: 8px; justify-content: center; margin-bottom: 24px; }
.otp-input { width: 48px; height: 56px; text-align: center; font-size: 24px; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; color: var(--text); }
.otp-info { text-align: center; color: var(--text-secondary); margin-bottom: 16px; font-size: 14px; }
.resend-link { text-align: center; font-size: 13px; }
.resend-link a { color: var(--primary); text-decoration: none; }
.strength-bar { height: 4px; background: var(--border); border-radius: 2px; margin-top: 8px; overflow: hidden; }
.strength-bar div { height: 100%; background: var(--green); transition: width 0.3s; }
.match-text { font-size: 12px; margin-top: 4px; color: var(--green); }
.info-box { background: rgba(240,185,11,0.1); border: 1px solid var(--primary); border-radius: 8px; padding: 16px; margin-bottom: 24px; }
.info-box h3 { color: var(--primary); font-size: 14px; margin-bottom: 8px; }
.info-box p { color: var(--text-secondary); font-size: 13px; }
.method-cards { display: flex; flex-direction: column; gap: 12px; }
.method-card { padding: 16px; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; cursor: pointer; color: var(--text); font-size: 14px; }
.method-card:hover { border-color: var(--primary); }
</style><script setup>
const useWallet = () => ({
  createWallet: () => ({
    address: '0x' + Math.random().toString(16).slice(2, 42),
    seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '),
    ownership: 'USER_OWNS'
  })
})
</script>
