# TigerEx Complete Platform - API Services Manifest

## Platform Coverage

| Platform | Technology | Status |
|----------|-----------|-------|
| Web (App) | Next.js + React | ✅ |
| Web (HTML) | Vanilla JS | ✅ |
| Mobile Android | React Native + Kotlin | ✅ |
| Mobile iOS | React Native + Swift | ✅ |
| Desktop | Electron + React | ✅ |

## User Roles

| Role | Permissions |
|------|-----------|
| super_admin | Full access: users, services, fees, settings |
| admin | User management, service control, fees |
| moderator | Limited user management |
| trader | Trading, portfolio, withdrawals |
| viewer | Read-only access |

## API Services (Backend 348 services)

### Core Services
- `auth-service/` - Authentication & Authorization
- `api-gateway/` - API Gateway
- `user-service/` - User Management
- `account-service/` - Account Management
- `wallet-service/` - Wallet Operations

### Trading Services
- `trading-engine/` - Trading Engine
- `advanced-order-types-service/` - Order Types
- `margin-trading/` - Margin Trading
- `futures-trading/` - Futures Trading

### TradFi Services
- `tradfi-system/` - CFD, Forex, Stock Tokens, Derivatives

### Admin Services
- `admin-service/` - Admin Operations
- `unified-admin-control/` - Complete Admin Control

### Fee Services
- `fee-management-service/` - Fee Collection

### Social & Integration
- `social-auth-service/` - Social Login (Google, Facebook, Twitter, Telegram)
- `affiliate-system/` - Affiliate System

## Mobile App Features
- Android: Native Kotlin + React Native
- iOS: Native Swift + React Native

## Desktop App Features
- Electron + React
- Windows, macOS, Linux support

## Admin Dashboard
- ComprehensiveTradingAdmin.tsx
- CompleteAdminDashboard.jsx
- admin-panel/