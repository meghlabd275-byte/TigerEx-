# TigerEx - Complete Cryptocurrency Exchange Platform

## 🚀 Overview

TigerEx is a comprehensive, enterprise-grade cryptocurrency exchange platform featuring separate admin and user applications for all major platforms with unified backend services.

### Key Features

- **Multi-Platform Support**: Web, Mobile (Android/iOS), Desktop applications
- **Role-Based Access Control**: Traders, VIP, Affiliates, Institutions, Admin roles
- **High-Performance Trading**: Real-time order matching, WebSocket updates
- **Advanced Security**: JWT auth, 2FA, biometric, rate limiting
- **P2P Trading**: User-to-user trading with escrow
- **Earn Products**: Staking, Launchpool, Savings
- **Copy Trading**: Follow successful traders

---

## 📁 Platform Structure

```
TigerEx/
├── mobile/
│   ├── android/kotlin/          # Android Admin & Users Apps (Kotlin)
│   │   ├── admin-app/            # Jetpack Compose + Hilt DI
│   │   └── users-app/            # Trading & Wallet App
│   └── ios/swift/                # iOS Admin & Users Apps (Swift)
│       ├── admin-app/             # SwiftUI Application
│       └── users-app/            # Trading & Wallet App
│
├── desktop/
│   ├── java/                    # JavaFX Admin & Users Apps
│   ├── python/                   # PyQt5 Admin & Users Apps
│   ├── go/                      # Fyne Admin & Users Apps
│   └── rust/                    # Tauri Admin & Users Apps
│
├── web/
│   ├── apps/
│   │   ├── react/typescript/     # React + Next.js Applications
│   │   │   ├── admin-app/        # Next.js 14 Admin Dashboard
│   │   │   └── users-app/        # Next.js 14 Trading Platform
│   │   └── vue/typescript/       # Vue + Nuxt Applications
│   │       ├── admin-app/        # Nuxt 3 Admin Dashboard
│   │       └── users-app/        # Nuxt 3 Trading Platform
│   │
│   ├── node/                     # Node.js Backend Services
│   │   ├── admin-app/            # Express Admin Server
│   │   └── users-app/           # Express Users Server
│   │
│   ├── angular/                  # Angular Applications
│   │   ├── admin-app/            # Angular 17 Admin
│   │   └── users-app/           # Angular 17 Users
│   │
│   ├── html/                     # Vanilla HTML/JS Applications
│   │   ├── admin-app/           # Alpine.js + TailwindCSS
│   │   └── users-app/           # Trading Interface
│   │
│   └── php/                      # PHP/Laravel Applications
│       ├── admin-app/             # Laravel Admin Panel
│       └── users-app/            # Laravel Users App
│
├── desktop/
│   ├── java/                    # JavaFX Applications
│   ├── python/                   # PyQt5/PySide Applications
│   ├── go/                     # Fyne Applications
│   └── rust/                   # Tauri Applications
│
├── shared/
│   └── config/                 # Unified Configuration
│
├── backend/                    # Unified Backend Services
└── docs/                       # Documentation
```

---

## 👥 User Roles

### End Users
| Role | Features |
|------|---------|
| **Trader** | Spot trading, wallet, P2P |
| **VIP** | Lower fees, priority support |
| **Affiliate** | Referral system, commissions |
| **Partner** | Business partnership |
| **Institution** | Institutional features, API |
| **P2P Merchant** | P2P platform operator |
| **Liquidity Provider** | Market making |
| **Market Maker** | Automated trading |
| **Coin/Token Team** | Project listing |
| **White Label** | Custom branding |

### Admin Roles
| Role | Permissions |
|------|------------|
| **Super Admin** | Full system access |
| **Admin** | User, trading, wallet management |
| **Moderator** | Content moderation |
| **Listing Manager** | Asset listing |
| **BD Manager** | Business development |
| **Support Team** | Ticket management |
| **Liquidity Manager** | Liquidity control |
| **Technical Team** | Technical operations |
| **Compliance Manager** | KYC, compliance |

---

## 🛠️ Technology Stack

### Mobile
- **Android**: Kotlin 1.9, Jetpack Compose, Hilt DI, Coroutines
- **iOS**: Swift 5.9, SwiftUI, Combine

### Desktop
- **Java**: Java 17, JavaFX, Spring Boot
- **Python**: Python 3.11, PyQt5/PySide6
- **Go**: Go 1.21, Fyne
- **Rust**: Rust 1.70, Tauri

### Web Applications
- **React**: Next.js 14, TypeScript, TailwindCSS
- **Vue**: Nuxt 3, TypeScript, Pinia
- **Angular**: Angular 17, TypeScript
- **Node.js**: Express, Fastify

### Web
- **HTML/JS**: Vanilla JS, Alpine.js, TailwindCSS
- **PHP**: Laravel 10, PHP 8.2

---

## 🔐 Security Features

- JWT Authentication with refresh tokens
- Two-Factor Authentication (TOTP/SMS)
- Biometric Authentication (mobile)
- API Key Authentication
- Withdrawal address whitelisting
- Anti-phishing code
- Rate limiting
- CSRF/XSS/SQL Injection prevention
- IP whitelisting
- Session management

---

## 🔌 API Configuration

### Production
```env
API_BASE_URL=https://api.tigerex.com
WS_BASE_URL=wss://stream.tigerex.com
```

### Staging
```env
API_BASE_URL=https://api.staging.tigerex.com
WS_BASE_URL=wss://stream.staging.tigerex.com
```

### Development
```env
API_BASE_URL=http://localhost:8000
WS_BASE_URL=ws://localhost:8001
```

---

## 📦 Installation

### React Users App
```bash
cd web/apps/react/typescript/users-app
npm install
npm run dev
npm run build
```

### React Admin App
```bash
cd web/apps/react/typescript/admin-app
npm install
npm run dev
npm run build
```

### Vue Users App
```bash
cd web/apps/vue/typescript/users-app
npm install
npm run dev
npm run build
```

### Angular Admin App
```bash
cd web/angular/admin-app
npm install
ng serve
ng build
```

### Node.js Admin Server
```bash
cd web/node/admin-app
npm install
npm run dev
```

### Android App
```bash
cd mobile/android/kotlin
./gradlew assembleDebug
```

### iOS App
```bash
cd mobile/ios/swift
xcodebuild -project TigerExUsers.xcodeproj -scheme TigerExUsers -sdk iphonesimulator
```

### Python Desktop App
```bash
cd desktop/python/users-app
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### HTML/JS (No Build Required)
```bash
cd web/html/users-app
python -m http.server 8080
```

---

## 🌐 Backend Services

All frontend applications connect to unified backend:

- **API Server**: Port 8000
- **Admin Server**: Port 8002
- **WebSocket Server**: Port 8001
- **Database**: PostgreSQL 5432
- **Cache**: Redis 6379
- **Logs**: MongoDB 27017

---

## 📱 Features Matrix

| Feature | Users App | Admin App |
|---------|----------|----------|
| Trading (Spot) | ✅ | ✅ |
| Trading (Margin) | ✅ | - |
| Wallet | ✅ | ✅ |
| P2P Trading | ✅ | ✅ |
| Staking | ✅ | ✅ |
| Launchpool | ✅ | ✅ |
| Copy Trading | ✅ | - |
| API Trading | ✅ | - |
| User Management | - | ✅ |
| KYC Management | - | ✅ |
| Settings | ✅ | ✅ |
| Audit Logs | - | ✅ |

---

## 🔗 Links

- **API Documentation**: https://api.tigerex.com/docs
- **WebSocket**: wss://stream.tigerex.com
- **Support**: support@tigerex.com

---

## 📄 License

Proprietary - All rights reserved

---

**Built with ❤️ by TigerEx Team**

*This documentation and all included code was created by an AI assistant (OpenHands) on behalf of the user.*