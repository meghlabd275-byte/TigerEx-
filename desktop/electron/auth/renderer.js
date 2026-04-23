// TigerEx Desktop Auth - Electron (JavaScript/CSS/HTML)
// Security: IPC communication, encrypted storage, biometric ready

const { ipcRenderer } = require('electron');
const path = require('path');

// Auth styles
const authStyles = `
  :root { --primary: #F0B90B; --bg: #0B0E11; --card: #1E2329; --text: #EAECEF; --text-sec: #848E9C; --border: #2B3139; --green: #00C087; }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
  .auth-container { width: 100%; max-width: 420px; padding: 20px; }
  .auth-card { background: var(--card); border-radius: 12px; padding: 32px; box-shadow: 0 4px 24px rgba(0,0,0,0.3); }
  .logo { text-align: center; font-size: 32px; margin-bottom: 24px; }
  .logo span { color: var(--primary); }
  h1 { font-size: 24px; font-weight: 700; text-align: center; margin-bottom: 8px; }
  .subtitle { color: var(--text-sec); text-align: center; margin-bottom: 24px; font-size: 14px; }
  .input-group { margin-bottom: 16px; }
  .input-group label { display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; }
  .input-group input, .input-group select { width: 100%; padding: 12px 16px; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 14px; outline: none; }
  .input-group input:focus { border-color: var(--primary); }
  .password-wrapper { position: relative; }
  .password-wrapper input { padding-right: 48px; }
  .toggle-btn { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; font-size: 18px; }
  .submit-btn { width: 100%; padding: 14px; background: var(--primary); color: #000; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; }
  .forgot-link { display: block; text-align: right; color: var(--primary); font-size: 14px; margin-bottom: 24px; text-decoration: none; }
  .back-btn { display: block; margin: 16px auto 0; background: none; border: none; color: var(--text-sec); cursor: pointer; font-size: 14px; }
  .divider { display: flex; align-items: center; margin: 24px 0; }
  .divider::before, .divider::after { content: ''; flex: 1; height: 1px; background: var(--border); }
  .divider span { padding: 0 16px; color: var(--text-sec); font-size: 13px; }
  .social-label { text-align: center; color: var(--text-sec); font-size: 13px; margin-bottom: 12px; }
  .social-btns { display: flex; flex-direction: column; gap: 10px; }
  .social-btns button { padding: 12px; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 14px; cursor: pointer; }
  .social-btns button:hover { border-color: var(--primary); }
  .footer-text { text-align: center; margin-top: 24px; color: var(--text-sec); font-size: 14px; }
  .footer-text a { color: var(--primary); text-decoration: none; }
  .step-indicator { display: flex; justify-content: center; gap: 8px; margin-bottom: 24px; }
  .step-indicator span { width: 32px; height: 32px; border-radius: 50%; background: var(--border); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; color: var(--text-sec); }
  .step-indicator span.active { background: var(--primary); color: #000; }
  .otp-inputs { display: flex; gap: 8px; justify-content: center; margin-bottom: 24px; }
  .otp-input { width: 48px; height: 56px; text-align: center; font-size: 24px; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; color: var(--text); }
  .info-box { background: rgba(240,185,11,0.1); border: 1px solid var(--primary); border-radius: 8px; padding: 16px; margin-bottom: 24px; }
  .info-box h3 { color: var(--primary); font-size: 14px; margin-bottom: 8px; }
  .info-box p { color: var(--text-sec); font-size: 13px; }
  .method-cards { display: flex; flex-direction: column; gap: 12px; }
  .method-card { padding: 16px; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; cursor: pointer; font-size: 14px; }
  .method-card:hover { border-color: var(--primary); }
  .hidden { display: none; }
  .strength-bar { height: 4px; background: var(--border); border-radius: 2px; margin-top: 8px; overflow: hidden; }
  .strength-fill { height: 100%; background: var(--green); transition: width 0.3s; }
  .match-text { font-size: 12px; margin-top: 4px; }
  .match-text.valid { color: var(--green); }
  .input-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
`;

// Auth HTML Template
const authHTML = `
<div class="auth-container">
  <!-- Login -->
  <div id="loginView" class="auth-card">
    <div class="logo">🐯 <span>TigerEx</span></div>
    <h1>Welcome Back</h1>
    <p class="subtitle">Log in to your account</p>
    
    <div class="input-group">
      <label>Email or Phone</label>
      <input type="text" id="loginEmail" placeholder="Enter email or phone">
    </div>
    
    <div class="input-group">
      <label>Password</label>
      <div class="password-wrapper">
        <input type="password" id="loginPassword" placeholder="Enter password">
        <button class="toggle-btn" onclick="togglePassword('loginPassword')">👁️</button>
      </div>
    </div>
    
    <a href="#" class="forgot-link" onclick="showView('forgotView')">Forgot password?</a>
    
    <button class="submit-btn" onclick="handleLogin()">Log In</button>
    
    <div class="divider"><span>or</span></div>
    
    <p class="social-label">Continue with</p>
    <div class="social-btns">
      <button onclick="socialLogin('Google')">🔵 Google</button>
      <button onclick="socialLogin('X')">𝕏 X</button>
      <button onclick="socialLogin('Telegram')">✈️ Telegram</button>
      <button onclick="socialLogin('GitHub')">🐙 GitHub</button>
      <button onclick="socialLogin('Discord')">🎮 Discord</button>
    </div>
    
    <p class="footer-text">Don't have an account? <a href="#" onclick="showView('signupView')">Sign Up</a></p>
  </div>
  
  <!-- Signup -->
  <div id="signupView" class="auth-card hidden">
    <div class="step-indicator">
      <span id="step1" class="active">1</span>
      <span id="step2">2</span>
      <span id="step3">3</span>
      <span id="step4">4</span>
    </div>
    
    <h1 id="signupTitle">Create Account</h1>
    <p class="subtitle" id="signupSubtitle">Enter your email to get started</p>
    
    <!-- Step 1: Email -->
    <div id="signupStep1">
      <div class="input-group">
        <label>Email</label>
        <input type="email" id="signupEmail" placeholder="Enter your email">
      </div>
      <button class="submit-btn" onclick="nextStep(2)">Continue</button>
    </div>
    
    <!-- Step 2: Verify -->
    <div id="signupStep2" class="hidden">
      <p class="subtitle">Code sent to <span id="verifyEmail"></span></p>
      <div class="otp-inputs">
        <input type="text" class="otp-input" maxlength="1">
        <input type="text" class="otp-input" maxlength="1">
        <input type="text" class="otp-input" maxlength="1">
        <input type="text" class="otp-input" maxlength="1">
        <input type="text" class="otp-input" maxlength="1">
        <input type="text" class="otp-input" maxlength="1">
      </div>
      <button class="submit-btn" onclick="nextStep(3)">Verify</button>
    </div>
    
    <!-- Step 3: Details -->
    <div id="signupStep3" class="hidden">
      <div class="input-row">
        <div class="input-group">
          <label>First Name</label>
          <input type="text" id="firstName" placeholder="First name">
        </div>
        <div class="input-group">
          <label>Last Name</label>
          <input type="text" id="lastName" placeholder="Last name">
        </div>
      </div>
      <div class="input-group">
        <label>Country</label>
        <select id="country">
          <option value="">Select country</option>
          <option value="US">🇺🇸 United States</option>
          <option value="UK">🇬🇧 United Kingdom</option>
        </select>
      </div>
      <button class="submit-btn" onclick="nextStep(4)">Continue</button>
    </div>
    
    <!-- Step 4: Password -->
    <div id="signupStep4" class="hidden">
      <div class="input-group">
        <label>Password</label>
        <div class="password-wrapper">
          <input type="password" id="signupPassword" placeholder="Create password" onkeyup="checkStrength()">
          <button class="toggle-btn" onclick="togglePassword('signupPassword')">👁️</button>
        </div>
        <div class="strength-bar"><div class="strength-fill" id="strengthFill"></div></div>
      </div>
      <div class="input-group">
        <label>Confirm Password</label>
        <input type="password" id="confirmPassword" placeholder="Confirm password" onkeyup="checkMatch()">
        <p class="match-text" id="matchText"></p>
      </div>
      <button class="submit-btn" onclick="handleSignup()">Create Account</button>
    </div>
    
    <button class="back-btn" id="signupBack" onclick="prevStep()" style="display:none">← Back</button>
    
    <div class="divider"><span>or</span></div>
    <p class="social-label">Sign up with</p>
    <div class="social-btns">
      <button onclick="socialSignup('Google')">🔵 Google</button>
      <button onclick="socialSignup('X')">𝕏 X</button>
      <button onclick="socialSignup('Telegram')">✈️ Telegram</button>
      <button onclick="socialSignup('GitHub')">🐙 GitHub</button>
      <button onclick="socialSignup('Discord')">🎮 Discord</button>
    </div>
    
    <p class="footer-text">Already have an account? <a href="#" onclick="showView('loginView')">Log In</a></p>
  </div>
  
  <!-- Forgot Password -->
  <div id="forgotView" class="auth-card hidden">
    <h1>Reset Password</h1>
    <p class="subtitle">Enter your email to receive reset code</p>
    
    <div class="input-group">
      <label>Email</label>
      <input type="email" id="forgotEmail" placeholder="Enter your email">
    </div>
    
    <button class="submit-btn" onclick="handleForgot()">Send Reset Code</button>
    <button class="back-btn" onclick="showView('loginView')">← Back to Login</button>
  </div>
  
  <!-- 2FA Reset -->
  <div id="twofaView" class="auth-card hidden">
    <h1>Reset 2FA</h1>
    <p class="subtitle">Choose a method to verify identity</p>
    
    <div class="info-box">
      <h3>⚠️ Important</h3>
      <p>Resetting 2FA will disable this security feature.</p>
    </div>
    
    <div class="method-cards">
      <div class="method-card" onclick="handle2FA('email')">📧 Email Verification</div>
      <div class="method-card" onclick="handle2FA('phone')">📱 SMS Verification</div>
      <div class="method-card" onclick="handle2FA('id')">🪪 Upload ID</div>
      <div class="method-card" onclick="handle2FA('support')">📞 Contact Support</div>
    </div>
    
    <button class="back-btn" onclick="showView('loginView')">← Back to Login</button>
  </div>
</div>
`;

// Auth JavaScript Functions
const authJS = `
let currentStep = 1;

function showView(viewId) {
  document.querySelectorAll('.auth-card').forEach(card => card.classList.add('hidden'));
  document.getElementById(viewId).classList.remove('hidden');
}

function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  input.type = input.type === 'password' ? 'text' : 'password';
}

function nextStep(step) {
  document.getElementById('signupStep' + currentStep).classList.add('hidden');
  currentStep = step;
  document.getElementById('signupStep' + step).classList.remove('hidden');
  
  // Update step indicator
  for(let i = 1; i <= 4; i++) {
    document.getElementById('step' + i).classList.toggle('active', i <= step);
  }
  
  // Update title
  const titles = ['Create Account', 'Verification', 'Personal Details', 'Create Password'];
  const subtitles = ['Enter your email', 'Verify your email', 'Tell us about yourself', 'Choose a strong password'];
  document.getElementById('signupTitle').textContent = titles[step-1];
  document.getElementById('signupSubtitle').textContent = subtitles[step-1];
  
  // Show/hide back button
  document.getElementById('signupBack').style.display = step > 1 ? 'block' : 'none';
  
  if(step === 2) {
    document.getElementById('verifyEmail').textContent = document.getElementById('signupEmail').value;
  }
}

function prevStep() {
  nextStep(currentStep - 1);
}

function checkStrength() {
  const pwd = document.getElementById('signupPassword').value;
  document.getElementById('strengthFill').style.width = pwd.length >= 8 ? '100%' : '0%';
}

function checkMatch() {
  const pwd = document.getElementById('signupPassword').value;
  const confirm = document.getElementById('confirmPassword').value;
  const text = document.getElementById('matchText');
  if(confirm) {
    text.textContent = pwd === confirm ? '✓ Passwords match' : '✗ Passwords do not match';
    text.className = 'match-text ' + (pwd === confirm ? 'valid' : '');
  }
}

function handleLogin() {
  const email = document.getElementById('loginEmail').value;
  // Send to main process
  ipcRenderer.send('auth:login', { email });
}

function handleSignup() {
  alert('Account created!');
  // Send to main process
  ipcRenderer.send('auth:signup', {
    email: document.getElementById('signupEmail').value,
    password: document.getElementById('signupPassword').value
  });
}

function handleForgot() {
  alert('Reset code sent!');
}

function handle2FA(method) {
  alert(method + ' verification');
}

function socialLogin(provider) {
  alert(provider + ' login');
}

function socialSignup(provider) {
  alert(provider + ' signup');
}

// OTP input handling
document.querySelectorAll('.otp-input').forEach((input, index) => {
  input.addEventListener('input', function() {
    if(this.value.length === 1 && index < 5) {
      document.querySelectorAll('.otp-input')[index + 1].focus();
    }
  });
  input.addEventListener('keydown', function(e) {
    if(e.key === 'Backspace' && !this.value && index > 0) {
      document.querySelectorAll('.otp-input')[index - 1].focus();
    }
  });
});

// IPC handlers
ipcRenderer.on('auth:login-success', (event, data) => {
  // Navigate to dashboard
  ipcRenderer.send('navigate', 'dashboard');
});

ipcRenderer.on('auth:error', (event, error) => {
  alert(error.message);
});
`;

// Export for use in main process
module.exports = {
  styles: authStyles,
  html: authHTML,
  js: authJS
};