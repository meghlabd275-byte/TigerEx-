# TigerEx Desktop App

Desktop trading platform with authentication.

## Files

```
desktop-app/
├── index.html              # Login page
├── assets/
│   ├── css/
│   │   └── responsive.css # Responsive styles
│   └── js/
│       └── auth-guard.js  # Auth guard
└── social/
    └── index.html        # Social login
```

## Features

**Authentication:**
- Email login
- Phone login
- Registration
- Forgot password

**Social Login (Electron-ready):**
- Google
- Apple
- Facebook
- GitHub
- Twitter
- Discord
- Telegram

**Responsive:**
- Mobile (≤480px)
- Tablet (481-768px)
- Desktop (769-1024px)
- Large Desktop (≥1025px)

## Auth Guard API

```javascript
// Check authentication
if (TigerExAuth.isAuthenticated()) {
    console.log('Logged in');
}

// Get current user
const user = TigerExAuth.getCurrentUser();

// Require auth
if (!TigerExAuth.requireAuth()) {
    // Redirected to login
}

// Login
TigerExAuth.login(token, userData);

// Logout
TigerExAuth.logout();
```

## Session

- Session expires after 24 hours
- Stored in localStorage

## Usage

Open `index.html` in browser to test.