# TigerEx Authentication System Specification

## Project Overview

**Project Name:** TigerEx Exchange Platform
**Platforms:** Web, Mobile (iOS/Android), Desktop
**Core Functionality:** Complete authentication system with email/phone login, registration, and password recovery

---

## Features Implemented

### 1. Authentication Pages

#### Login Page (`login.html`)
- ✅ Email/Phone toggle tabs
- ✅ 200+ country codes with flags
- ✅ Password visibility toggle
- ✅ Remember me checkbox
- ✅ Forgot password link
- ✅ Social login (Google, Apple, GitHub)
- ✅ Theme toggle (dark/light)
- ✅ OTP verification flow
- ✅ 2FA support
- ✅ Session management
- ✅ LocalStorage for users

#### Register Page (`register.html`)
- ✅ Email/Phone toggle tabs
- ✅ 200+ country codes with flags
- ✅ Password confirmation
- ✅ Referral code optional
- ✅ Terms acceptance
- ✅ Social signup
- ✅ Theme toggle
- ✅ Email/Phone verification

#### Forgot Password Page (`forgot-password.html`)
- ✅ Email input
- ✅ OTP verification (6-digit)
- ✅ New password reset
- ✅ Step-by-step flow

---

## Platform Implementations

### Web Apps
- **login.html** - Web login page
- **register.html** - Web registration page  
- **forgot-password.html** - Web password recovery

### Mobile Apps (Existing)
- **mobile/App.jsx** - React Native web version
- **mobile/EnhancedMobileApp.jsx** - Enhanced React Native
- **mobile/complete_mobile_app_react_native.tsx** - Complete RN app
- **mobile/android/** - Android native code
- **mobile/ios/** - iOS native code

### Desktop Apps
- **desktop-app/index.html** - Desktop Electron-ready app

---

## Technical Stack

### Frontend
- HTML5, CSS3, Tailwind CSS
- JavaScript (Vanilla)
- React Native (Mobile)
- Flutter (Mobile)
- Electron (Desktop)

### Backend
- Node.js/Express (server/node/server.js)
- Python/Flask (server/app.py)

### API Endpoints
```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/session
GET  /api/user/profile
GET  /api/trading/markets
GET  /api/trading/orderbook/:symbol
POST /api/trading/order
GET  /api/wallet/balance
GET  /api/wallet/addresses
GET  /api/earn/products
```

---

## Design System

### Colors
- Primary: #F0B90B (Tiger Yellow)
- Background Dark: #0B0E11
- Card: #1E2329
- Text Primary: #EAECEF
- Text Secondary: #848E9C
- Success: #00C087
- Error: #F6465D

### Components
- Tab Toggle (Email | Phone)
- Country Selector with Flags
- Input Fields with validation
- OTP Input (6-digit)
- Social Login Buttons
- Theme Toggle

---

## Security Features
- JWT Token Authentication
- Password hashing (SHA256)
- Session management
- Rate limiting ready
- Input validation
- XSS protection

---

## Browser Support
- ✅ Chrome
- ✅ Firefox
- ✅ Microsoft Edge
- ✅ Safari
- ✅ Opera
- ✅ Mobile browsers

---

## Mobile Support
- ✅ iOS Safari
- ✅ Android Chrome
- ✅ React Native
- ✅ Flutter
- ✅ PWA ready

---

## Desktop Support
- ✅ Windows
- ✅ macOS
- ✅ Linux
- ✅ Electron ready

---

## File Structure
```
TigerEx-/
├── login.html                 # Web login
├── register.html            # Web register
├── forgot-password.html     # Web forgot password
├── index.html               # Main landing page
├── SPEC.md                  # This specification
├── assets/
│   └── js/
│       └── api.js          # API client
├── server/
│   ├── app.py              # Flask server
│   └── node/
│       ├── server.js       # Express server
│       └── package.json
├── mobile/                  # Mobile apps
│   ├── App.jsx
│   ├── android/
│   ├── ios/
│   └── src/
├── mobile-app/
│   ├── react-native/       # RN app
│   └── flutter/            # Flutter app
└── desktop-app/            # Desktop app
    └── index.html
```

---

## API Integration

### Frontend Usage
```javascript
// Login with email
await API.auth.login('email@example.com', 'password');

// Login with phone
await API.auth.login('+1234567890', 'password');

// Register
await API.auth.register({
  identifier: 'email or phone',
  password: 'password',
  referral: 'optional'
});

// Get session
const session = await API.auth.getSession();
```

---

## 2FA Reset Flow (SPEC.md)

Complete 2FA reset specification documented in original SPEC.md:
1. Email Verification
2. Phone Verification  
3. Liveness Check
4. 2FA Reset Confirmation

---

## Implementation Status

| Feature | Web | Mobile | Desktop |
|---------|-----|--------|----------|
| Login Email | ✅ | ✅ | ✅ |
| Login Phone | ✅ | ✅ | ✅ |
| Register Email | ✅ | ✅ | ✅ |
| Register Phone | ✅ | ✅ | ✅ |
| Forgot Password | ✅ | ✅ | ✅ |
| OTP Verification | ✅ | ✅ | ✅ |
| Theme Toggle | ✅ | ✅ | ✅ |
| Social Login | ✅ | ⚠️ | ✅ |
| 2FA Support | ✅ | ⚠️ | ✅ |

---

*Last Updated: 2026-04-24*
*Version: 1.0.0*
