# TigerEx Platform - Complete Frontend Architecture

## Overview

TigerEx is a comprehensive cryptocurrency exchange platform with multiple frontend applications serving different user roles and platforms. All applications connect to the same unified backend services and database.

## Platform Structure

```
TigerEx-Platform/
├── mobile/
│   ├── android/
│   │   ├── kotlin/
│   │   │   ├── admin-app/          # Kotlin Admin Application
│   │   │   └── users-app/          # Kotlin Users Application
│   │   └── ios/
│   │       └── swift/
│   │           ├── admin-app/      # Swift Admin Application
│   │           └── users-app/      # Swift Users Application
│   ├── desktop/
│   │   ├── java/                 # JavaFX Desktop Applications
│   │   ├── python/               # PyQt/PySide Desktop Applications
│   │   ├── go/                  # Go + Fyne Desktop Applications
│   │   └── rust/                # Rust + Tauri Desktop Applications
│   ├── web/
│   │   └── apps/
│   │       ├── react/
│   │       │   └── typescript/    # React + Next.js Applications
│   │       └── vue/
│   │           └── typescript/    # Vue + Nuxt Applications
│   └── html/                   # Vanilla HTML/JS Applications
│       ├── admin-app/
│       └── users-app/
├── shared/
│   ├── api-clients/             # Shared API Clients
│   ├── config/                  # Shared Configuration
│   ├── database/               # Database Schemas
│   ├── docs/                  # Documentation
│   └── security/             # Security Utilities
└── backend/                   # Backend Services (unified)
```

## User Roles

### End Users
- **Traders**: Standard trading functionality
- **VIP**: Enhanced features and lower fees
- **Affiliate**: Referral system and commissions
- **Partner**: Business partnership features
- **Institution**: Institutional-grade features
- **P2P Merchant**: P2P trading platform operators
- **Liquidity Providers**: Market makers and liquidity providers
- **Market Maker**: Automated market making
- **Coin/Token Team**: Project teams listing their tokens
- **White Label**: Custom branded exchange users

### Admin Users
- **Super Admin**: Full system access
- **Admin**: Administrative functions
- **Moderator**: Content and user moderation
- **Listing Manager**: Asset listing management
- **BD Manager**: Business development
- **Support Team**: Customer support
- **Liquidity Manager**: Liquidity management
- **Technical Team**: Technical operations
- **Compliance Manager**: Compliance and KYC

## Features by App Type

### Users Applications
- Trading (Spot, Margin, Futures)
- Wallet Management
- P2P Trading
- Earn Products (Staking, Savings, Launchpool)
- API Trading
- Copy Trading
- KYC Verification
- Security Settings
- Customer Support

### Admin Applications
- User Management
- Trading Pair Management
- Wallet & Transaction Management
- P2P Management
- Launchpool Management
- Settings Configuration
- Audit Logs
- Role & Permission Management

## Technology Stack

### Mobile
- **Android**: Kotlin + Jetpack Compose + Hilt
- **iOS**: Swift + SwiftUI + Combine

### Desktop
- **Java**: JavaFX + Spring Boot
- **Python**: PyQt5/PySide6 + FastAPI Client
- **Go**: Fyne + Native HTTP Client
- **Rust**: Tauri + Yew/WebView

### Web Apps
- **React**: Next.js 14 + TypeScript + TailwindCSS
- **Vue**: Nuxt 3 + TypeScript + TailwindCSS
- **Angular**: Angular 17 + TypeScript

### Web
- **HTML/JS**: Vanilla JS + AJAX + TailwindCSS
- **PHP**: Laravel + Blade + Alpine.js

## Backend Configuration

### API Endpoints
```
Production: https://api.tigerex.com
Staging: https://api.staging.tigerex.com
Development: http://localhost:8000
```

### WebSocket
```
wss://stream.tigerex.com/ws
```

### Database
```yaml
PostgreSQL: 5432
Redis: 6379
MongoDB: 27017
```

## Security Features

- JWT Authentication with Refresh Tokens
- Two-Factor Authentication (TOTP)
- Biometric Authentication
- API Key Authentication
- IP Whitelisting
- Withdrawal Address Whitelisting
- Anti-Phishing Code
- Session Management
- Rate Limiting
- CSRF Protection
- XSS Prevention
- SQL Injection Prevention

## Build Instructions

### Android (Kotlin)
```bash
cd mobile/android/kotlin
./gradlew assembleDebug    # Debug build
./gradlew assembleRelease # Release build
```

### iOS (Swift)
```bash
cd mobile/ios/swift
xcodebuild -project TigerEx.xcodeproj -scheme TigerExUsers -sdk iphonesimulator
```

### React Web App
```bash
cd web/apps/react/typescript/users-app
npm install
npm run dev      # Development
npm run build   # Production
```

### Vue Web App
```bash
cd web/apps/vue/typescript/users-app
npm install
npm run dev      # Development
npm run build   # Production
```

### Desktop Python
```bash
cd desktop/python/users-app
pip install -r requirements.txt
python main.py
```

### HTML/JS Web
```bash
cd web/html/users-app
# Simply serve with any HTTP server
python -m http.server 8080
```

## Environment Variables

Create `.env` files in each app directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=https://api.tigerex.com
NEXT_PUBLIC_WS_URL=wss://stream.tigerex.com/ws

# Authentication
JWT_SECRET=your-jwt-secret
REFRESH_TOKEN_EXPIRY=7d

# Security
ENCRYPTION_KEY=your-encryption-key
API_RATE_LIMIT=100
```

## Deployment

### Docker Support
Each app includes Dockerfile for containerized deployment:

```bash
docker build -t tigerex-users-app .
docker run -p 3000:3000 tigerex-users-app
```

## Documentation

- [API Documentation](./docs/API.md)
- [Database Schema](./docs/DATABASE.md)
- [Security Guide](./docs/SECURITY.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)

## License

Proprietary - All rights reserved