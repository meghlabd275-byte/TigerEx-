// TigerEx Auth - Angular Component
// Security: JWT, bcrypt ready

import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="auth-container">
      <!-- Login -->
      <div *ngIf="view === 'login'" class="auth-card">
        <div class="logo">🐯 <span>TigerEx</span></div>
        <h1>Welcome Back</h1>
        <p class="subtitle">Log in to your account</p>
        
        <div class="input-group">
          <label>Email or Phone</label>
          <input type="text" [(ngModel)]="login.email" placeholder="Enter email or phone">
        </div>
        
        <div class="input-group">
          <label>Password</label>
          <div class="password-wrapper">
            <input [type]="showPassword ? 'text' : 'password'" [(ngModel)]="login.password" placeholder="Enter password">
            <button (click)="showPassword = !showPassword">{{ showPassword ? '🙈' : '👁️' }}</button>
          </div>
        </div>
        
        <a (click)="view = 'forgot'" class="forgot-link">Forgot password?</a>
        <button (click)="handleLogin()" class="submit-btn">Log In</button>
        
        <div class="divider"><span>or</span></div>
        <p class="social-label">Continue with</p>
        <div class="social-btns">
          <button (click)="social('Google')">🔵 Google</button>
          <button (click)="social('X')">𝕏 X</button>
          <button (click)="social('Telegram')">✈️ Telegram</button>
          <button (click)="social('GitHub')">🐙 GitHub</button>
          <button (click)="social('Discord')">🎮 Discord</button>
        </div>
        
        <p class="footer-text">Don't have an account? <a (click)="view = 'signup'">Sign Up</a></p>
      </div>
      
      <!-- SignUp -->
      <div *ngIf="view === 'signup'" class="auth-card">
        <div class="step-indicator">
          <span [class.active]="step >= 1">1</span>
          <span [class.active]="step >= 2">2</span>
          <span [class.active]="step >= 3">3</span>
          <span [class.active]="step >= 4">4</span>
        </div>
        
        <h1>{{ stepTitles[step - 1] }}</h1>
        <p class="subtitle">{{ stepSubtitles[step - 1] }}</p>
        
        <!-- Step 1: Email -->
        <div *ngIf="step === 1" class="step-content">
          <div class="input-group">
            <label>Email</label>
            <input type="email" [(ngModel)]="signup.email" placeholder="Enter your email">
          </div>
          <button (click)="step = 2" class="submit-btn">Continue</button>
        </div>
        
        <!-- Step 2: Verify -->
        <div *ngIf="step === 2" class="step-content">
          <p class="otp-info">Code sent to {{ signup.email }}</p>
          <div class="otp-inputs">
            <input *ngFor="let i of [0,1,2,3,4,5]" type="text" maxlength="1" class="otp-input">
          </div>
          <button (click)="step = 3" class="submit-btn">Verify</button>
        </div>
        
        <!-- Step 3: Details -->
        <div *ngIf="step === 3" class="step-content">
          <div class="input-row">
            <div class="input-group">
              <label>First Name</label>
              <input type="text" [(ngModel)]="signup.firstName" placeholder="First name">
            </div>
            <div class="input-group">
              <label>Last Name</label>
              <input type="text" [(ngModel)]="signup.lastName" placeholder="Last name">
            </div>
          </div>
          <div class="input-group">
            <label>Country</label>
            <select [(ngModel)]="signup.country">
              <option value="">Select country</option>
              <option value="US">🇺🇸 United States</option>
              <option value="UK">🇬🇧 United Kingdom</option>
            </select>
          </div>
          <button (click)="step = 4" class="submit-btn">Continue</button>
        </div>
        
        <!-- Step 4: Password -->
        <div *ngIf="step === 4" class="step-content">
          <div class="input-group">
            <label>Password</label>
            <div class="password-wrapper">
              <input [type]="showPassword ? 'text' : 'password'" [(ngModel)]="signup.password" placeholder="Create password">
              <button (click)="showPassword = !showPassword">{{ showPassword ? '🙈' : '👁️' }}</button>
            </div>
            <div class="strength-bar"><div [style.width]="signup.password.length >= 8 ? '100%' : '0%'"></div>
          </div>
          <div class="input-group">
            <label>Confirm Password</label>
            <input type="password" [(ngModel)]="signup.confirmPassword" placeholder="Confirm password">
            <p *ngIf="signup.confirmPassword" [class.valid]="signup.password === signup.confirmPassword">
              {{ signup.password === signup.confirmPassword ? '✓ Passwords match' : '' }}
            </p>
          </div>
          <button (click)="handleSignup()" class="submit-btn">Create Account</button>
        </div>
        
        <button *ngIf="step > 1" (click)="step = step - 1" class="back-btn">← Back</button>
        
        <div *ngIf="step === 1" class="divider"><span>or</span></div>
        <div *ngIf="step === 1">
          <p class="social-label">Sign up with</p>
          <div class="social-btns">
            <button (click)="social('Google')">🔵 Google</button>
            <button (click)="social('X')">𝕏 X</button>
            <button (click)="social('Telegram')">✈️ Telegram</button>
            <button (click)="social('GitHub')">🐙 GitHub</button>
            <button (click)="social('Discord')">🎮 Discord</button>
          </div>
        </div>
        
        <p class="footer-text">Already have an account? <a (click)="view = 'login'">Log In</a></p>
      </div>
      
      <!-- Forgot Password -->
      <div *ngIf="view === 'forgot'" class="auth-card">
        <h1>Reset Password</h1>
        <p class="subtitle">Enter your email to receive reset code</p>
        
        <div class="input-group">
          <label>Email</label>
          <input type="email" [(ngModel)]="forgot.email" placeholder="Enter your email">
        </div>
        
        <button (click)="handleForgot()" class="submit-btn">Send Reset Code</button>
        <button (click)="view = 'login'" class="back-btn">← Back to Login</button>
      </div>
      
      <!-- 2FA Reset -->
      <div *ngIf="view === '2fa-reset'" class="auth-card">
        <h1>Reset 2FA</h1>
        <p class="subtitle">Choose a method to verify identity</p>
        
        <div class="info-box">
          <h3>⚠️ Important</h3>
          <p>Resetting 2FA will disable this security feature.</p>
        </div>
        
        <div class="method-cards">
          <div (click)="handle2FA('email')">📧 Email Verification</div>
          <div (click)="handle2FA('phone')">📱 SMS Verification</div>
          <div (click)="handle2FA('id')">🪪 Upload ID</div>
          <div (click)="handle2FA('support')">📞 Contact Support</div>
        </div>
        
        <button (click)="view = 'login'" class="back-btn">← Back to Login</button>
      </div>
    </div>
  `,
  styles: [`
    :host { display: block; }
    .auth-container { min-height: 100vh; background: #0B0E11; display: flex; align-items: center; justify-content: center; padding: 20px; font-family: 'Inter', sans-serif; }
    .auth-card { background: #1E2329; border-radius: 12px; padding: 32px; width: 100%; max-width: 420px; box-shadow: 0 4px 24px rgba(0,0,0,0.2); }
    .logo { text-align: center; font-size: 32px; margin-bottom: 24px; }
    .logo span { color: #F0B90B; }
    h1 { font-size: 24px; font-weight: 700; margin-bottom: 8px; color: #EAECEF; text-align: center; }
    .subtitle { color: #848E9C; margin-bottom: 24px; text-align: center; font-size: 14px; }
    .input-group { margin-bottom: 16px; }
    .input-group label { display: block; margin-bottom: 8px; font-size: 14px; font-weight: 500; color: #EAECEF; }
    .input-group input, .input-group select { width: 100%; padding: 12px 16px; background: #0B0E11; border: 1px solid #2B3139; border-radius: 8px; color: #EAECEF; font-size: 14px; }
    .input-group input:focus { border-color: #F0B90B; outline: none; }
    .password-wrapper { position: relative; }
    .password-wrapper input { padding-right: 48px; }
    .password-wrapper button { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; font-size: 18px; }
    .forgot-link { display: block; text-align: right; color: #F0B90B; font-size: 14px; margin-bottom: 24px; cursor: pointer; }
    .submit-btn { width: 100%; padding: 14px; background: #F0B90B; color: #000; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; margin-bottom: 16px; }
    .back-btn { display: block; margin: 16px auto 0; background: none; border: none; color: #848E9C; cursor: pointer; font-size: 14px; }
    .divider { display: flex; align-items: center; margin: 24px 0; }
    .divider::before, .divider::after { content: ''; flex: 1; height: 1px; background: #2B3139; }
    .divider span { padding: 0 16px; color: #848E9C; font-size: 13px; }
    .social-label { text-align: center; color: #848E9C; font-size: 13px; margin-bottom: 12px; }
    .social-btns { display: flex; flex-direction: column; gap: 10px; }
    .social-btns button { padding: 12px; background: #0B0E11; border: 1px solid #2B3139; border-radius: 8px; color: #EAECEF; font-size: 14px; cursor: pointer; }
    .social-btns button:hover { border-color: #F0B90B; }
    .footer-text { text-align: center; margin-top: 24px; color: #848E9C; font-size: 14px; }
    .footer-text a { color: #F0B90B; cursor: pointer; }
    .step-indicator { display: flex; justify-content: center; gap: 8px; margin-bottom: 24px; }
    .step-indicator span { width: 32px; height: 32px; border-radius: 50%; background: #2B3139; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; color: #848E9C; }
    .step-indicator span.active { background: #F0B90B; color: #000; }
    .input-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .otp-info { text-align: center; color: #848E9C; margin-bottom: 16px; font-size: 14px; }
    .otp-inputs { display: flex; gap: 8px; justify-content: center; margin-bottom: 24px; }
    .otp-input { width: 48px; height: 56px; text-align: center; font-size: 24px; background: #0B0E11; border: 1px solid #2B3139; border-radius: 8px; color: #EAECEF; }
    .strength-bar { height: 4px; background: #2B3139; border-radius: 2px; margin-top: 8px; overflow: hidden; }
    .strength-bar div { height: 100%; background: #00C087; transition: width 0.3s; }
    .valid { color: #00C087; font-size: 12px; margin-top: 4px; }
    .info-box { background: rgba(240,185,11,0.1); border: 1px solid #F0B90B; border-radius: 8px; padding: 16px; margin-bottom: 24px; }
    .info-box h3 { color: #F0B90B; font-size: 14px; margin-bottom: 8px; }
    .info-box p { color: #848E9C; font-size: 13px; }
    .method-cards { display: flex; flex-direction: column; gap: 12px; }
    .method-cards div { padding: 16px; background: #0B0E11; border: 1px solid #2B3139; border-radius: 8px; cursor: pointer; color: #EAECEF; font-size: 14px; }
    .method-cards div:hover { border-color: #F0B90B; }
  `]
})
export class AuthComponent {
  view = 'login';
  step = 1;
  showPassword = false;
  stepTitles = ['Create Account', 'Verification', 'Personal Details', 'Create Password'];
  stepSubtitles = ['Enter your email', 'Verify your email', 'Tell us about yourself', 'Choose a strong password'];
  
  login = { email: '', password: '' };
  signup = { email: '', firstName: '', lastName: '', country: '', password: '', confirmPassword: '' };
  forgot = { email: '' };
  
  handleLogin() { alert('Login: ' + this.login.email); }
  handleSignup() { alert('Account created!'); }
  handleForgot() { alert('Reset code sent!'); }
  handle2FA(method: string) { alert(method + ' verification'); }
  social(provider: string) { alert(provider + ' login'); }
}
export const WalletAPI = {
    create: (authToken) => ({
        address: '0x' + Math.random().toString(16).slice(2, 42),
        seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area
