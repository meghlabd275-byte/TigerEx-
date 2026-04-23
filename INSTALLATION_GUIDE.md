# TigerEx Complete Platform - Build & Installation Guide

## ⚡ Platform Priorities
- **Super First Speed**: 100ms page load, 50ms API response
- **Uncompromising Security**: JWT, 2FA, AES-256 encryption
- **Lightwave Fast**: CDN, Redis cache, optimized queries

---

## 📋 Table of Contents
1. [Android Users App](#android-users-app)
2. [Android Admin App](#android-admin-app)
3. [iOS Users App](#ios-users-app)
4. [iOS Admin App](#ios-admin-app)
5. [Web Users Apps](#web-users-apps)
6. [Web Admin Apps](#web-admin-apps)
7. [Desktop Apps](#desktop-apps)
8. [Backend Services](#backend-services)
9. [Database Setup](#database-setup)
10. [KYC Service](#kyc-service)

---

## 📱 Android Users App

### Tech Stack
- **Language**: Kotlin 1.9.x
- **UI**: Jetpack Compose + Material 3
- **Architecture**: MVVM + Clean Architecture
- **DI**: Hilt
- **Networking**: Retrofit + OkHttp
- **Async**: Coroutines + Flow

### Directory
```
mobile/android/kotlin/users-app/
├── src/main/java/com/tigerex/users/
│   ├── app/           # Application class
│   ├── data/          # Repository, API
│   ├── di/            # Hilt modules
│   ├── domain/        # Use cases
│   └── ui/           # Screens, ViewModels
└── src/main/res/
    ├── layout/        # XML layouts
    ├── values/       # Colors, themes
    └── drawable/     # Icons
```

### Build Commands
```bash
# Navigate to project
cd mobile/android/kotlin/users-app

# Build Debug APK
./gradlew assembleDebug

# Build Release APK
./gradlew assembleRelease

# Output location
# app/build/outputs/apk/debug/ OR app/build/outputs/apk/release/
```

### Installation
1. Enable "Install from unknown sources" in settings
2. Transfer APK to device
3. Open file manager and tap APK
4. Install and launch

### Features
- ✅ 5 Main Tabs: Home, Markets, Trade, TradFi, Assets
- ✅ 7 Trading Modes: Spot, Futures, Margin, Option, Alpha, Copy, TradeX
- ✅ Dark/Light Theme Toggle
- ✅ Social Login (Google, Apple, etc.)

---

## 📱 Android Admin App

### Tech Stack
- Same as Users App with additional admin features

### Directory
```
mobile/android/kotlin/admin-app/
```

### Build Commands
```bash
cd mobile/android/kotlin/admin-app
./gradlew assembleRelease
```

### Installation
Same as Users App

### Features
- ✅ User Management
- ✅ KYC Approval
- ✅ Liquidity Management
- ✅ Trading Pair Control
- ✅ Fee Management

---

## 🍎 iOS Users App

### Tech Stack
- **Language**: Swift 5.9
- **UI**: SwiftUI
- **Architecture**: MVVM
- **Networking**: URLSession + Combine

### Directory
```
mobile/ios/swift/users-app/TigerExUsers/
├── Sources/
│   ├── App/          # App entry
│   ├── Views/        # SwiftUI views
│   ├── ViewModels/  # Observable objects
│   └── Models/     # Data models
└── Resources/
```

### Build Commands
```bash
# Using Xcode
cd mobile/ios/swift/users-app
open TigerExUsers.xcworkspace

# Build via command line
xcodebuild -workspace TigerExUsers.xcworkspace \
  -scheme TigerExUsers \
  -configuration Debug \
  -destination 'generic/platform=iOS Simulator' \
  -derivedDataPath ./build

# Export IPA
xcodebuild -exportArchive \
  -archive_path build.xcarchive \
  -export_path ./output \
  -exportOptionsPlist ExportOptions.plist
```

### Installation
1. **Device**: Install via Xcode or TestFlight
2. **Simulator**: Select device and click Run

### Features
- ✅ 5 Main Tabs (Home, Markets, Trade, TradFi, Assets)
- ✅ 7 Trading Modes
- ✅ Dark/Light Theme Toggle
- ✅ Social Login

---

## 🍎 iOS Admin App

### Build Commands
```bash
cd mobile/ios/swift/admin-app
xcodebuild -workspace TigerExAdmin.xcworkspace \
  -scheme TigerExAdmin \
  -configuration Release
```

### Features
- ✅ User Management Dashboard
- ✅ KYC Verification
- ✅ Liquidity Management
- ✅ System Monitoring

---

## 🌐 Web Users Apps

### 1. Next.js App (Recommended)

### Tech Stack
- **Framework**: Next.js 14
- **Language**: TypeScript
- **UI**: Tailwind CSS
- **State**: React Context + SWR

### Directory
```
web/apps/react/typescript/users-app/
├── src/
│   ├── app/          # App router
│   ├── components/  # Reusable components
│   ├── hooks/       # Custom hooks
│   └── lib/         # Utilities
├── package.json
└── next.config.js
```

### Build & Run
```bash
cd web/apps/react/typescript/users-app

# Install dependencies
npm install

# Development
npm run dev
# Opens http://localhost:3000

# Production build
npm run build
npm run start

# Output: .next/
```

### 2. React + Vite App

### Build & Run
```bash
cd web/apps/react/users-app

npm install
npm run dev      # Development
npm run build   # Production
npm run preview # Preview build
```

---

## 🌐 Web Admin Apps

### Next.js Admin App

### Build & Run
```bash
cd web/apps/react/typescript/admin-app

npm install
npm run build
npm run start
```

### Features
- ✅ Dashboard with analytics
- ✅ User management
- ✅ KYC verification
- ✅ Liquidity management

---

## 💻 Desktop Apps

### 1. Tauri (Rust) - Recommended

### Tech Stack
- **Backend**: Rust
- **Frontend**: React + TypeScript
- **Framework**: Tauri 2.0

### Directory
```
desktop/rust/users-app/
├── src/              # Rust backend
├── src-tauri/        # Tauri config
├── src-web/         # React frontend
├── package.json
└── tauri.conf.json
```

### Build Commands
```bash
cd desktop/rust/users-app

# Install
npm install

# Development
npm run tauri dev

# Production build
npm run tauri build

# Output
# src-tauri/target/release/bundle/
```

### Installation
- **Windows**: Run .exe installer from `src-tauri/target/release/bundle/msi/`
- **macOS**: Open .dmg from `src-tauri/target/release/bundle/dmg/`
- **Linux**: Run AppImage from `src-tauri/target/release/bundle/appimage/`

### 2. Electron App

### Build Commands
```bash
cd desktop/users-app

npm install
npm run build  # Creates ./dist with executables

# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

---

## 🔧 Backend Services

### All Services Connect to Same Database

### Running All Services
```bash
# Main API Gateway
cd backend/api-gateway
python main.py --port 8000

# User Service
cd backend/user-service
python main.py --port 8001

# Trading Engine
cd backend/trading-engine-enhanced
python main.py --port 8002

# Wallet Service
cd backend/wallet-service
python main.py --port 8003
```

### Docker Compose (All Services)
```bash
cd backend
docker-compose up -d

# All services start on ports:
# - API Gateway: 8000
# - User: 8001
# - Trading: 8002
# - Wallet: 8003
# - Redis: 6379
# - PostgreSQL: 5432
```

---

## 🗄️ Database Setup

### PostgreSQL
```bash
# Using Docker
docker run -d \
  --name tigerex-postgres \
  -e POSTGRES_USER=tigerex \
  -e POSTGRES_PASSWORD=secure_password \
  -e POSTGRES_DB=tigerex_db \
  -p 5432:5432 \
  postgres:15

# Connnection
# Host: localhost
# Port: 5432
# Database: tigerex_db
# User: tigerex
# Password: secure_password
```

### Redis (Cache)
```bash
docker run -d \
  --name tigerex-redis \
  -p 6379:6379 \
  redis:7-alpine
```

### Connection String
```
postgresql://tigerex:secure_password@localhost:5432/tigerex_db
redis://localhost:6379
```

---

## 🔐 Environment Variables

Create `.env` file:
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/tigerex
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=your-secret-key-min-32-chars
JWT_EXPIRY=24h

# API Keys
API_KEY=your-api-key
API_SECRET=your-api-secret

# Security
ENCRYPTION_KEY=32-character-encryption-key
RATE_LIMIT=100

# Services
USER_SERVICE_URL=http://localhost:8001
TRADING_SERVICE_URL=http://localhost:8002
WALLET_SERVICE_URL=http://localhost:8003
```

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cd TigerEx-
```

### 2. Start Backend
```bash
cd backend
docker-compose up -d
```

### 3. Build Frontend (Choose One)

#### Web Users App
```bash
cd web/apps/react/typescript/users-app
npm install
npm run build
npm run start
```

#### Android App
```bash
cd mobile/android/kotlin/users-app
./gradlew assembleDebug
```

#### iOS App
```bash
cd mobile/ios/swift/users-app
open TigerExUsers.xcworkspace
```

#### Desktop App
```bash
cd desktop/rust/users-app
npm run tauri build
```

---

## 📋 Role Configuration

### End Users
| Role | Features |
|------|----------|
| Trader | Spot, P2P, Wallet |
| VIP | + Copy Trading, Lower Fees |
| Affiliate | + Referral Program |
| Partner | + OTC, API |
| Institution | + Margin, Options, Custody |
| P2P Merchant | + Create P2P Ads |
| Liquidity Provider | + LP Pools |
| Market Maker | + Auto Trading |
| Coin/Token Team | + Launchpool, IDO |
| White Label | + Custom Branding |

### Admin Users
| Role | Features |
|------|----------|
| Super Admin | Full System Access |
| Admin | Platform Management |
| Moderator | Content Moderation |
| Support Team | User Support |
| Liquidity Manager | Liquidity Control |
| Technical Team | System Operations |
| Compliance Manager | KYC/AML |
| Listing Manager | Asset Listings |

---

## 🆘 Troubleshooting

### Build Errors
```bash
# Clean and rebuild
./gradlew clean
./gradlew assembleDebug

# npm cache
npm cache clean --force
npm install
```

### Connection Issues
```bash
# Check services
docker ps
curl http://localhost:8000/health
```

---

## 🔐 KYC Service

### KYC Verification Features
- Document Upload (Passport, National ID, Driver's License)
- Liveness Face Verification (One Face = One Account)
- Address Proof (Advanced KYC)

### KYC Backend
```bash
cd backend/kyc-service
python complete_kyc.py
# Runs on port 8008
```

### KYC API Endpoints
```bash
# Upload document
curl -X POST http://localhost:8008/api/v1/kyc/upload-document

# Start liveness
curl -X POST http://localhost:8008/api/v1/kyc/liveness/start

# Check liveness
curl -X POST http://localhost:8008/api/v1/kyc/liveness/check

# Verify liveness
curl -X POST http://localhost:8008/api/v1/kyc/liveness/verify

# Unique face check
curl -X POST http://localhost:8008/api/v1/kyc/face/check-unique

# Address proof
curl -X POST http://localhost:8008/api/v1/kyc/address-proof

# Get status
curl http://localhost:8008/api/v1/kyc/status?user_id=xxx
```

### KYC Database Tables
- `kyc_applications` - User KYC records
- `face_embeddings` - Face data for uniqueness
- `kyc_documents` - ID documents
- `address_proofs` - Address documents
- `kyc_logs` - Audit trail

---

## 📄 License

MIT License - TigerEx 2025