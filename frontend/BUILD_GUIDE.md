# TigerEx Complete Platform - Build & Installation Guide

## Platform Overview
- **Super First Speed**: Optimized with latest tech stack
- **Uncompromising Security**: End-to-end encryption, rate limiting, WAF
- **Lightwave Fast**: CDN, caching, optimized queries

## Directory Structure

### Frontend Apps (Separated by Role & Platform)

```
frontend/
├── android/
│   ├── admin/           # Admin App (Kotlin + Jetpack Compose)
│   │   └── src/
│   └── users/          # Users App (Kotlin + Jetpack Compose)
│       └── src/
├── ios/
│   ├── admin/          # Admin App (Swift + SwiftUI)
│   │   └── TigerExAdmin/
│   └── users/          # Users App (Swift + SwiftUI)
│       └── TigerExUsers/
├── desktop/
│   ├── admin/          # Admin Desktop Apps
│   │   ├── java/       # JavaFX
│   │   ├── python/     # Python (Tkinter/PyQt)
│   │   ├── go/        # Go (Fyne/Tauri)
│   │   └── rust/      # Rust (Tauri)
│   └── users/          # Users Desktop Apps
│       ├── java/
│       ├── python/
│       ├── go/
│       └── rust/
└── web/
    ├── admin/          # Admin Web Apps
    │   ├── next/      # Next.js (React)
    │   ├── react/     # React + TypeScript
    │   ├── vue/       # Vue.js
    │   ├── node/     # Node.js + Express
    │   └── php/      # PHP (Laravel)
    └── users/         # Users Web Apps
        ├── next/       # Next.js
        ├── react/     # React
        ├── vue/       # Vue.js
        ├── node/     # Node.js
        └── php/      # PHP
```

## Technology Stack

### Admin Apps (Performance Priority)
- **Android**: Kotlin, Jetpack Compose, Hilt, Material 3
- **iOS**: Swift, SwiftUI, Combine
- **Web**: Next.js 14, TypeScript, Tailwind CSS
- **Desktop**: Tauri (Rust) for cross-platform

### Users Apps (Speed Priority)
- **Android**: Kotlin, Jetpack Compose, Coroutines
- **iOS**: Swift, SwiftUI
- **Web**: React 18, TypeScript, Vite, Tailwind
- **Desktop**: Electron, React

## Security Features
- ✅ JWT Authentication with refresh tokens
- ✅ End-to-end encryption
- ✅ Rate limiting & DDoS protection
- ✅ WAF integration
- ✅ Biometric authentication
- ✅ 2FA (Google Authenticator)
- ✅ Anti-phishing code
- ✅ Secure session management
- ✅ APIKey with IP whitelist

## User Roles (End Users)
1. **Trader** - Basic trading
2. **VIP** - Premium features, lower fees
3. **Affiliate** - Referral program
4. **Partner** - Business partnerships
5. **Institution** - OTC, API, custody
6. **P2P Merchant** - P2P trading
7. **Liquidity Provider** - Market making
8. **Market Maker** - Automated trading
9. **Coin/Token Team** - Project listings
10. **White Label** - Branded solution

## Admin Roles
1. **Super Admin** - Full system access
2. **Admin** - Platform management
3. **Moderator** - Content moderation
4. **Support Team** - User support
5. **Liquidity Manager** - Liquidity control
6. **Technical Team** - System operations
7. **Compliance Manager** - KYC/AML
8. **Listing Manager** - Asset listing
9. **BD Manager** - Business development

## Backend Services
All apps connect to the same backend:
- **API Gateway**: `/backend/api-gateway/`
- **Trading Engine**: `/backend/trading-engine-enhanced/`
- **User Service**: `/backend/user-service/`
- **Wallet Service**: `/backend/wallet-service/`
- **Order Service**: `/backend/order-service/`

## Database Connections
- **Primary**: PostgreSQL (user data, orders)
- **Cache**: Redis (sessions, cache)
- **Message Queue**: RabbitMQ (async tasks)
- **Time Series**: InfluxDB (market data)

## Features for All Users
- Spot/Futures/Margin/Options trading
- P2P marketplace
- Staking & Earn products
- Launchpool & Megadrop
- Copy trading
- Crypto card
- API trading
- Convert & Transfer
- Red packets
- Airdrops & Campaigns

## Build Commands

### Android
```bash
cd frontend/android/users
./gradlew assembleRelease
```

### iOS
```bash
cd frontend/ios/users
xcodebuild -exportArchive
```

### Web (Next.js)
```bash
cd frontend/web/users/next
npm run build
npm run start
```

### Desktop (Tauri)
```bash
cd frontend/desktop/users/rust
cargo tauri build
```

## Installation

### Android App
1. Download APK from releases
2. Enable "Install from unknown sources"
3. Install and open
4. Login or register

### iOS App
1. Download from App Store
2. Install via TestFlight (beta)
3. Login or register

### Web App
1. Navigate to https://tigerex.com
2. Login or register
3. Complete KYC (optional)

## Performance Targets
- **Page Load**: < 100ms
- **API Response**: < 50ms
- **Trade Execution**: < 10ms
- **Real-time Updates**: WebSocket

## Security Targets
- ✅ SOC 2 compliant
- ✅ GDPR compliant
- ✅ ISO 27001 certified

## Support
- Email: support@tigerex.com
- Live Chat: 24/7
- Telegram: @TigerExSupport