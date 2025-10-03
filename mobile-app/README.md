# TigerEx Mobile App

**Complete Cryptocurrency Exchange Platform for iOS & Android**

## 📱 Overview

TigerEx Mobile is a comprehensive cryptocurrency exchange application built with React Native, offering professional trading features, P2P marketplace, staking opportunities, and advanced portfolio management.

## ✨ Features

### 🔐 Authentication & Security
- **Biometric Login** - Fingerprint and Face ID support
- **2FA Authentication** - Two-factor authentication
- **Secure Storage** - Encrypted local storage
- **PIN Protection** - Additional security layer

### 📊 Trading Features
- **Spot Trading** - Real-time spot trading with advanced charts
- **Market Data** - Live price feeds and market statistics
- **Order Types** - Limit, Market, Stop-Limit orders
- **Order Book** - Real-time order book display
- **Trade History** - Complete trading history

### 💰 Wallet Management
- **Multi-Asset Wallet** - Support for 100+ cryptocurrencies
- **Deposit & Withdrawal** - Easy fund management
- **Transfer** - Internal transfers between accounts
- **Transaction History** - Complete transaction records
- **Balance Overview** - Real-time balance updates

### 🤝 P2P Trading
- **Peer-to-Peer Marketplace** - Direct trading with other users
- **Multiple Payment Methods** - Bank transfer, PayPal, Wise, etc.
- **Merchant Ratings** - Trust system with user ratings
- **Secure Escrow** - Protected transactions
- **Chat System** - Built-in communication

### 💎 Earn & Staking
- **Flexible Staking** - Stake various cryptocurrencies
- **Fixed Savings** - Locked savings with higher APY
- **Liquidity Mining** - Provide liquidity and earn rewards
- **Launchpool** - Participate in new token launches
- **DeFi Integration** - Access to DeFi protocols

### 📈 Markets & Analytics
- **Market Overview** - Complete market data
- **Price Charts** - Advanced charting with indicators
- **Watchlist** - Track favorite trading pairs
- **Price Alerts** - Custom price notifications
- **Market Analysis** - Technical analysis tools

### 👨‍💼 Admin Features
- **Admin Dashboard** - Complete system overview
- **User Management** - User administration tools
- **Trading Controls** - Trading system management
- **Financial Controls** - Financial operations management
- **Analytics** - Comprehensive reporting

## 🏗️ Architecture

### Technology Stack
- **Framework**: React Native 0.72.6
- **Navigation**: React Navigation 6.x
- **State Management**: React Hooks + Context API
- **UI Components**: Custom components with Material Design
- **Icons**: React Native Vector Icons
- **Charts**: React Native Chart Kit
- **Storage**: AsyncStorage
- **Network**: Axios
- **Real-time**: Socket.IO

### Project Structure
```
mobile-app/
├── App.js                          # Main application entry
├── package.json                    # Dependencies and scripts
├── src/
│   └── screens/
│       ├── auth/                   # Authentication screens
│       │   ├── LoginScreen.js      # Login with biometric support
│       │   └── RegisterScreen.js   # User registration
│       ├── user/                   # User screens
│       │   ├── HomeScreen.js       # Dashboard and overview
│       │   ├── TradingScreen.js    # Basic trading interface
│       │   ├── WalletScreen.js     # Wallet management
│       │   └── ProfileScreen.js    # User profile and settings
│       ├── admin/                  # Admin screens
│       │   ├── AdminDashboard.js   # Admin overview
│       │   ├── UserManagement.js   # User administration
│       │   ├── TradingControls.js  # Trading management
│       │   └── FinanceControls.js  # Financial management
│       ├── markets/                # Market screens
│       │   └── MarketsScreen.js    # Market overview and data
│       ├── trading/                # Advanced trading
│       │   └── SpotTradingScreen.js # Professional spot trading
│       ├── earn/                   # Earning opportunities
│       │   └── EarnScreen.js       # Staking and savings
│       └── p2p/                    # P2P trading
│           └── P2PScreen.js        # P2P marketplace
```

## 🚀 Getting Started

### Prerequisites
- Node.js >= 18
- React Native CLI
- Android Studio (for Android)
- Xcode (for iOS)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cd TigerEx-/mobile-app
```

2. **Install dependencies**
```bash
npm install
```

3. **iOS Setup**
```bash
cd ios && pod install && cd ..
```

4. **Run the application**

For Android:
```bash
npm run android
```

For iOS:
```bash
npm run ios
```

### Development Scripts
```bash
npm start          # Start Metro bundler
npm run android    # Run on Android device/emulator
npm run ios        # Run on iOS device/simulator
npm test           # Run tests
npm run lint       # Run ESLint
```

## 📱 Screens Overview

### Authentication Flow
1. **Login Screen** - Email/password + biometric authentication
2. **Register Screen** - Complete user registration with validation

### User Flow (7 tabs)
1. **Home** - Dashboard with portfolio overview and quick actions
2. **Markets** - Market data, price charts, and trading pairs
3. **Trading** - Basic trading interface with order placement
4. **Earn** - Staking, savings, and earning opportunities
5. **P2P** - Peer-to-peer trading marketplace
6. **Wallet** - Multi-asset wallet with deposit/withdrawal
7. **Profile** - User settings, security, and preferences

### Admin Flow (4 tabs)
1. **Dashboard** - System overview and key metrics
2. **Users** - User management and administration
3. **Trading** - Trading system controls and monitoring
4. **Finance** - Financial operations and approvals

### Additional Screens
- **Spot Trading** - Advanced professional trading interface
- **Market Details** - Detailed market information and charts

## 🎨 UI/UX Features

### Design System
- **Material Design** - Following Google's Material Design principles
- **Consistent Colors** - Green (#4CAF50) primary, professional palette
- **Typography** - Clear, readable fonts with proper hierarchy
- **Icons** - Material Community Icons for consistency
- **Responsive** - Adapts to different screen sizes

### User Experience
- **Intuitive Navigation** - Easy-to-use tab and stack navigation
- **Real-time Updates** - Live data updates throughout the app
- **Loading States** - Proper loading indicators
- **Error Handling** - User-friendly error messages
- **Offline Support** - Graceful offline handling

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```
API_BASE_URL=https://api.tigerex.com
WEBSOCKET_URL=wss://ws.tigerex.com
ENVIRONMENT=development
```

### Build Configuration
- **Android**: Configure in `android/app/build.gradle`
- **iOS**: Configure in Xcode project settings

## 📦 Dependencies

### Core Dependencies
- **react-native**: 0.72.6 - Core framework
- **@react-navigation**: 6.x - Navigation system
- **react-native-vector-icons**: 10.x - Icon library
- **axios**: 1.6.x - HTTP client
- **socket.io-client**: 4.5.x - Real-time communication

### UI & UX
- **react-native-chart-kit**: 6.x - Charts and graphs
- **react-native-svg**: 13.x - SVG support
- **react-native-linear-gradient**: 2.x - Gradient backgrounds
- **react-native-modal**: 13.x - Modal components

### Security & Storage
- **@react-native-async-storage/async-storage**: 1.x - Local storage
- **react-native-biometrics**: 3.x - Biometric authentication
- **react-native-permissions**: 4.x - Permission management

## 🧪 Testing

### Test Structure
```bash
npm test                    # Run all tests
npm run test:watch         # Run tests in watch mode
npm run test:coverage      # Run tests with coverage
```

### Testing Libraries
- **Jest** - Testing framework
- **React Native Testing Library** - Component testing
- **Detox** - E2E testing (optional)

## 📱 Platform Support

### iOS
- **Minimum Version**: iOS 12.0
- **Target Version**: iOS 17.0
- **Devices**: iPhone 6s and newer, iPad Air 2 and newer

### Android
- **Minimum SDK**: API 21 (Android 5.0)
- **Target SDK**: API 34 (Android 14)
- **Architecture**: ARM64, ARMv7

## 🚀 Deployment

### Android Release
```bash
npm run build:android
```

### iOS Release
```bash
npm run build:ios
```

### App Store Submission
1. Build release version
2. Test on physical devices
3. Submit to App Store Connect
4. Submit to Google Play Console

## 🔄 Updates & Maintenance

### Over-the-Air Updates
- **CodePush** integration for instant updates
- **Automatic updates** for non-native changes
- **Rollback capability** for quick issue resolution

### Monitoring
- **Crash reporting** with detailed error logs
- **Performance monitoring** for optimization
- **User analytics** for feature usage insights

## 📞 Support

### Documentation
- **API Documentation**: Available in `/docs` directory
- **Component Library**: Storybook integration
- **User Guides**: In-app help and tutorials

### Contact
- **Email**: support@tigerex.com
- **Discord**: TigerEx Community
- **GitHub Issues**: Bug reports and feature requests

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 🎯 Roadmap

### Upcoming Features
- [ ] Advanced charting with TradingView
- [ ] Social trading features
- [ ] NFT marketplace integration
- [ ] DeFi protocol integrations
- [ ] Multi-language support
- [ ] Dark mode theme
- [ ] Tablet optimization
- [ ] Apple Watch companion app

---

**TigerEx Mobile** - The most comprehensive cryptocurrency exchange app for mobile devices.

*Built with ❤️ by the TigerEx Development Team*