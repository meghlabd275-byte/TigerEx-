# TigerEx Mobile App

React Native mobile application for TigerEx cryptocurrency exchange platform.

## Features

### Core Features
- **Authentication**
  - Email/Password login
  - Biometric authentication (Face ID/Touch ID)
  - Two-factor authentication (2FA)
  - Social login integration

- **Trading**
  - Spot trading
  - Futures trading
  - Margin trading
  - Quick trade functionality
  - Advanced order types (Limit, Market, Stop-Loss, Take-Profit)
  - Real-time price updates via WebSocket

- **Portfolio Management**
  - Real-time portfolio tracking
  - Asset allocation visualization
  - P&L tracking
  - Performance charts
  - Multi-wallet support

- **Wallet**
  - Deposit (Crypto & Fiat)
  - Withdrawal with multi-step verification
  - Internal transfers
  - Transaction history
  - QR code generation for deposits

- **P2P Trading**
  - Buy/Sell crypto with fiat
  - Multiple payment methods
  - Escrow protection
  - Real-time chat with sellers
  - Dispute resolution

- **Copy Trading**
  - Browse top traders
  - Copy trading strategies
  - Performance metrics
  - Risk management settings

- **Earn & Staking**
  - Flexible staking
  - Locked staking
  - Reward tracking
  - APY calculator

- **Trading Bots**
  - Grid trading bot
  - DCA bot
  - Martingale bot
  - Arbitrage bot
  - Market making bot

- **Launchpad**
  - Token sales participation
  - Vesting schedule tracking
  - KYC verification

- **Additional Features**
  - Push notifications for price alerts
  - News feed
  - Market analysis
  - Multi-language support
  - Dark mode
  - Offline mode support

## Tech Stack

- **Framework**: React Native with Expo
- **Navigation**: React Navigation
- **State Management**: Redux Toolkit
- **UI Library**: React Native Paper
- **Charts**: React Native Chart Kit
- **WebSocket**: Socket.io Client
- **HTTP Client**: Axios
- **Authentication**: Expo Local Authentication
- **Notifications**: Expo Notifications

## Project Structure

```
mobile/TigerExApp/
├── src/
│   ├── screens/          # Screen components
│   │   ├── Auth/         # Login, Register
│   │   ├── Home/         # Dashboard
│   │   ├── Markets/      # Market overview
│   │   ├── Trade/        # Trading interface
│   │   ├── Portfolio/    # Portfolio management
│   │   ├── Wallet/       # Wallet operations
│   │   ├── P2P/          # P2P trading
│   │   ├── CopyTrading/  # Copy trading
│   │   ├── Earn/         # Staking & earn
│   │   ├── TradingBots/  # Trading bots
│   │   ├── Launchpad/    # Token launchpad
│   │   └── Profile/      # User profile
│   ├── components/       # Reusable components
│   ├── store/           # Redux store
│   │   └── slices/      # Redux slices
│   ├── services/        # API services
│   ├── utils/           # Utility functions
│   └── theme/           # Theme configuration
├── App.tsx              # Main app component
├── package.json         # Dependencies
└── README.md           # This file
```

## Installation

```bash
cd mobile/TigerExApp
npm install
```

## Running the App

### iOS
```bash
npm run ios
```

### Android
```bash
npm run android
```

### Web (for testing)
```bash
npm run web
```

## Building for Production

### iOS
```bash
expo build:ios
```

### Android
```bash
expo build:android
```

## Key Screens

### 1. Home Screen
- Market overview
- Quick access to features
- Price alerts
- News feed

### 2. Markets Screen
- Real-time price list
- Search functionality
- Favorites
- Market statistics

### 3. Trade Screen
- Order book
- Trading chart
- Order placement
- Position management

### 4. Portfolio Screen
- Total balance
- Asset allocation
- P&L tracking
- Performance charts

### 5. Wallet Screen
- Deposit/Withdrawal
- Transaction history
- Multi-wallet support
- QR code scanner

## API Integration

The mobile app connects to the following backend services:

- Authentication Service: `http://api.tigerex.com/auth`
- Trading Service: `http://api.tigerex.com/trading`
- Wallet Service: `http://api.tigerex.com/wallet`
- Market Data Service: `ws://api.tigerex.com/market`
- P2P Service: `http://api.tigerex.com/p2p`
- Staking Service: `http://api.tigerex.com/staking`
- Trading Bots Service: `http://api.tigerex.com/bots`
- Launchpad Service: `http://api.tigerex.com/launchpad`

## Security Features

- Biometric authentication
- Encrypted local storage
- Secure API communication (HTTPS)
- Session management
- Auto-logout on inactivity
- Device fingerprinting

## Push Notifications

- Price alerts
- Order execution notifications
- Deposit/Withdrawal confirmations
- P2P trade updates
- Staking rewards
- Launchpad announcements

## Offline Mode

- Cache market data
- Queue transactions
- Sync when online
- Offline portfolio view

## Localization

Supported languages:
- English
- Spanish
- Chinese (Simplified)
- Chinese (Traditional)
- Japanese
- Korean
- French
- German
- Russian
- Arabic

## Performance Optimization

- Lazy loading of screens
- Image optimization
- Efficient list rendering (FlatList)
- Memoization of expensive computations
- WebSocket connection pooling
- API response caching

## Testing

```bash
npm test
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.