# 🐯 TigerEx Trading Dashboard

A comprehensive multi-platform trading dashboard with 100% TigerEx branding. Supports Android, iOS, Desktop, and Web platforms.

## 🌐 All Platforms

### 1. Web App
- **Location**: `/trading-dashboard/`
- **Files**: HTML, JavaScript, CSS
- **Features**: 
  - Homepage with profile, search, QR scanner, notifications
  - Trade page with chart, order book, positions
  - TradFi page with CFD trading
  - Assets page with wallets
  - Profile page with settings
  - More Services page

### 2. Android App
- **Location**: `/trading-dashboard/android/`
- **Technology**: Java/Kotlin + WebView
- **Features**: All web features in native shell

### 3. iOS App
- **Location**: `/trading-dashboard/ios/`
- **Technology**: SwiftUI
- **Features**: Native iOS trading interface

### 4. Desktop App
- **Location**: `/trading-dashboard/desktop/`
- **Technology**: Electron
- **Features**: Desktop trading experience

### 5. Mobile App (React Native)
- **Location**: `/mobile/app/src/`
- **Technology**: React Native
- **Features**: Full mobile trading app

## 🎨 Dark/Light Theme

✅ Theme works everywhere:
- Persists in localStorage
- Auto-detects system preference
- Real-time toggle
- All pages styled consistently

## 🔗 All CEX Links Working

### Home
- bitget.com

### Markets
- binance.com/en/markets/overview

### Trade
- Futures: bitget.com/futures/usdt/BTCUSDT
- Spot: bitget.com/spot/BTCUSDT
- Margin: bitget.com/spot/BTCUSDT?type=cross
- P2P: p2p.binance.com/en
- On-Chain: bitget.com/on-chain/sol/...
- Alpha: binance.com/en/alpha/bsc/...

### TradFi
- CFD: bitgettradfi.com/tradfi/XAUUSD
- Stocks: bitget.com/on-chain/bnb/...
- Stock Preps: bitget.com/futures/usdt/NVDAUSDT

### Assets
- All wallets at bitget.com/asset

## 📱 Features

### Homepage
- ✅ Profile icon with user avatar
- ✅ Coin/token search bar
- ✅ QR Scanner
- ✅ Customer Support
- ✅ Notifications
- ✅ Theme toggle

### Trade Page
- ✅ Chart with candlesticks
- ✅ Order book
- ✅ Positions panel
- ✅ Trade panel (Buy/Sell)
- ✅ Order history

### Assets Page
- ✅ Spot Wallet
- ✅ Futures Wallet
- ✅ P2P Wallet
- ✅ TigerPay
- ✅ TradFi Wallet
- ✅ Crypto Card
- ✅ Deposit/Withdrawal

### Profile Page
- ✅ User info
- ✅ KYC Verification
- ✅ API Keys
- ✅ Security settings
- ✅ Preferences
- ✅ Support

### More Services
- ✅ All trading services
- ✅ Earn products
- ✅ Financial services
- ✅ Settings
- ✅ Notifications toggles

## 🚀 Getting Started

### Web
```bash
cd trading-dashboard
# Open index.html in browser
```

### Android
```bash
cd trading-dashboard/android
# Build with Gradle
./gradlew assembleDebug
```

### iOS
```bash
cd trading-dashboard/ios
# Open in Xcode
open TradingDashboard.xcodeproj
```

### Desktop
```bash
cd trading-dashboard/desktop
npm install
npm start
```

## 🔒 Security

- FLAG_SECURE on Android
- CSP headers
- No sensitive data stored
- Secure theme storage

## 📄 License

MIT License - TigerEx Trading Dashboard
