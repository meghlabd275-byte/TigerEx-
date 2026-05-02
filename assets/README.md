# TigerEx Frontend Assets

Production-ready frontend assets for TigerEx exchange.

## Directory Structure

```
assets/
├── android/           # Android theme (Kotlin)
├── components/        # Reusable HTML components
├── css/              # CSS stylesheets
│   ├── responsive.css # Responsive framework
│   └── theme.css      # Theme variables
├── java/             # Java theme
├── js/               # JavaScript libraries
│   ├── api.js        # API client (v2.0)
│   └── tigerex-auth-universal.js  # Auth service (v2.0)
├── logo/             # Logos and images
├── screenshots/     # App screenshots
├── swift/            # iOS theme
├── typescript/       # TypeScript definitions
│   └── tigerex-api-types.ts
└── videos/           # Demo videos
```

## Quick Start

### Using the API Client

```html
<script src="/assets/js/api.js"></script>
<script>
    // Login
    await TigerExAPI.auth.login('email@example.com', 'password');
    
    // Get balance
    const balance = await TigerExAPI.wallet.getBalance();
    
    // Create order
    await TigerExAPI.trading.createOrder({
        pair_symbol: 'BTC/USDT',
        side: 'BUY',
        type: 'market',
        quantity: 0.1
    });
</script>
```

### Using Authentication

```html
<script src="/assets/js/tigerex-auth-universal.js"></script>
<script>
    // Check login status
    if (TigerExAuth.isAuthenticated()) {
        console.log('User:', TigerExAuth.getUser());
    }
    
    // Listen for auth events
    TigerExAuth.on('login', (user) => {
        console.log('Logged in:', user);
    });
</script>
```

## Version History

### v2.0 (Current)
- ✅ Server-side authentication
- ✅ httpOnly cookies (no localStorage)
- ✅ Token refresh
- ✅ CSRF protection
- ✅ Retry logic
- ✅ TypeScript types

### v1.0 (Legacy)
- ❌ Client-side only
- ❌ localStorage tokens
- ❌ No refresh

## Security

v2.0 uses secure cookie-based authentication:
- Access tokens stored in httpOnly cookies
- CSRF tokens for state-changing requests
- Automatic token refresh before expiry
- Session validation with server

## License

Proprietary - All rights reserved