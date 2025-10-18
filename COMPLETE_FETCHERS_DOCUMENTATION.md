# TigerEx Complete Data Fetchers & Admin Controls Documentation

## Overview

This document provides comprehensive documentation for the TigerEx Complete Exchange Data Fetchers and Universal Admin Control Service. These services provide full administrative control over all trading operations across multiple exchanges with complete user access management.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Supported Exchanges](#supported-exchanges)
3. [Supported Trading Types](#supported-trading-types)
4. [Admin Control Features](#admin-control-features)
5. [User Access Management](#user-access-management)
6. [API Endpoints](#api-endpoints)
7. [Security Features](#security-features)
8. [Deployment Guide](#deployment-guide)

## Architecture Overview

### Services

1. **Complete Exchange Data Fetchers Service** (Port 8003)
   - Provides real-time market data for all trading types
   - Supports all major exchanges
   - Includes admin controls for contract management

2. **Universal Admin Control Service** (Port 8004)
   - Complete user management system
   - Role-based access control (RBAC)
   - Audit logging and emergency controls

### Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **Authentication**: JWT (JSON Web Tokens)
- **Security**: HTTPBearer, bcrypt password hashing
- **API Documentation**: OpenAPI/Swagger

## Supported Exchanges

The system supports the following major cryptocurrency exchanges:

1. **Binance** - World's largest crypto exchange
2. **KuCoin** - Popular altcoin exchange
3. **Bybit** - Derivatives-focused exchange
4. **OKX** - Comprehensive trading platform
5. **MEXC** - High-liquidity exchange
6. **Bitget** - Copy trading specialist
7. **Bitfinex** - Advanced trading platform

## Supported Trading Types

### 1. Spot Trading
- Direct cryptocurrency trading
- Immediate settlement
- No leverage

### 2. Futures Trading
- **Perpetual Futures**: No expiry date, funding rate mechanism
- **Cross Margin Futures**: Shared margin across positions
- **Delivery Futures**: Fixed settlement date

### 3. Margin Trading
- **Cross Margin**: Shared margin across all positions
- **Isolated Margin**: Separate margin per position
- Leverage up to 125x (configurable)

### 4. Options Trading
- Call and Put options
- Multiple strike prices
- Various expiry dates
- Greeks calculation (Delta, Gamma, Theta, Vega)

### 5. Derivatives Trading
- Complex derivative products
- Structured products
- Custom contracts

### 6. Copy Trading
- Follow expert traders
- Automatic position mirroring
- Risk management controls

### 7. ETF Trading
- Crypto ETF products
- Basket of assets
- Automatic rebalancing

### 8. Leveraged Tokens
- Built-in leverage
- No liquidation risk
- Daily rebalancing

### 9. Structured Products
- Fixed income products
- Yield enhancement
- Capital protection options

## Admin Control Features

### Contract Management

#### 1. Create Contract
```python
POST /api/v1/admin/contract/create
```

**Features:**
- Create new trading contracts for any exchange
- Support all trading types
- Configure leverage, fees, and limits
- Set contract metadata

**Request Body:**
```json
{
  "exchange": "binance",
  "trading_type": "futures_perpetual",
  "symbol": "BTC/USDT",
  "base_asset": "BTC",
  "quote_asset": "USDT",
  "leverage_available": [1, 2, 3, 5, 10, 20, 50, 100, 125],
  "min_order_size": 0.001,
  "max_order_size": 1000000,
  "price_precision": 8,
  "quantity_precision": 8,
  "maker_fee": 0.001,
  "taker_fee": 0.001,
  "funding_rate": 0.0001,
  "funding_interval": 8
}
```

#### 2. Launch Contract
```python
POST /api/v1/admin/contract/{contract_id}/launch
```

**Features:**
- Activate pending contracts
- Make contracts available for trading
- Audit trail logging

#### 3. Pause Contract
```python
POST /api/v1/admin/contract/{contract_id}/pause
```

**Features:**
- Temporarily suspend trading
- Maintain existing positions
- Prevent new orders

#### 4. Resume Contract
```python
POST /api/v1/admin/contract/{contract_id}/resume
```

**Features:**
- Reactivate paused contracts
- Resume normal trading operations

#### 5. Delete Contract
```python
DELETE /api/v1/admin/contract/{contract_id}
```

**Features:**
- Soft delete (mark as delisted)
- Preserve historical data
- Audit trail maintained

#### 6. Update Contract
```python
PUT /api/v1/admin/contract/{contract_id}
```

**Features:**
- Modify contract parameters
- Update fees and limits
- Change leverage options
- Update metadata

### Contract Status Flow

```
PENDING → ACTIVE → PAUSED → ACTIVE
                 ↓
              SUSPENDED
                 ↓
              DELISTED
```

## User Access Management

### User Roles

1. **SUPER_ADMIN**
   - Full system access
   - Can create/modify admins
   - Emergency controls
   - All permissions

2. **ADMIN**
   - Contract management
   - User management
   - View analytics
   - Cannot modify super admins

3. **MODERATOR**
   - Limited contract control
   - User support functions
   - View-only analytics

4. **TRADER**
   - All trading permissions
   - Wallet operations
   - No admin functions

5. **VIEWER**
   - Read-only access
   - Analytics viewing
   - No trading or admin functions

6. **SUSPENDED**
   - No permissions
   - Account suspended

### Permissions System

#### Trading Permissions
- `SPOT_TRADING` - Spot market access
- `FUTURES_TRADING` - Futures trading
- `OPTIONS_TRADING` - Options trading
- `MARGIN_TRADING` - Margin trading
- `DERIVATIVES_TRADING` - Derivatives access
- `COPY_TRADING` - Copy trading features
- `ETF_TRADING` - ETF trading

#### Wallet Permissions
- `DEPOSIT` - Deposit funds
- `WITHDRAW` - Withdraw funds
- `TRANSFER` - Internal transfers

#### Admin Permissions
- `CREATE_CONTRACT` - Create new contracts
- `LAUNCH_CONTRACT` - Launch contracts
- `PAUSE_CONTRACT` - Pause contracts
- `RESUME_CONTRACT` - Resume contracts
- `DELETE_CONTRACT` - Delete contracts
- `UPDATE_CONTRACT` - Update contracts

#### User Management Permissions
- `CREATE_USER` - Create new users
- `UPDATE_USER` - Modify user accounts
- `DELETE_USER` - Delete users
- `MANAGE_ROLES` - Assign roles
- `MANAGE_PERMISSIONS` - Manage permissions

#### System Permissions
- `VIEW_ANALYTICS` - View system analytics
- `VIEW_AUDIT_LOG` - Access audit logs
- `SYSTEM_CONFIG` - System configuration
- `EMERGENCY_STOP` - Emergency controls

### User Management Endpoints

#### 1. Create User
```python
POST /api/v1/admin/users/create
```

**Features:**
- Create new user accounts
- Assign roles and permissions
- Set trading limits
- Configure KYC requirements

#### 2. List Users
```python
GET /api/v1/admin/users
```

**Features:**
- Filter by role, status, KYC
- Pagination support
- Search functionality

#### 3. Get User Details
```python
GET /api/v1/admin/users/{user_id}
```

**Features:**
- Complete user information
- Trading history
- Permission details

#### 4. Update User
```python
PUT /api/v1/admin/users/{user_id}
```

**Features:**
- Modify user details
- Update permissions
- Change trading limits
- Update KYC status

#### 5. Suspend User
```python
POST /api/v1/admin/users/{user_id}/suspend
```

**Features:**
- Temporarily suspend account
- Disable trading
- Maintain data integrity
- Audit trail

#### 6. Activate User
```python
POST /api/v1/admin/users/{user_id}/activate
```

**Features:**
- Reactivate suspended accounts
- Restore trading access
- Audit logging

#### 7. Update Trading Permission
```python
POST /api/v1/admin/users/{user_id}/trading-permission
```

**Features:**
- Enable/disable specific trading types
- Set leverage limits
- Configure position sizes
- Per-trading-type control

### KYC Status Management

**KYC Levels:**
- **Level 0**: Not submitted - Basic access
- **Level 1**: Pending - Limited access
- **Level 2**: Approved - Standard access
- **Level 3**: Enhanced - Full access

**KYC Statuses:**
- `NOT_SUBMITTED` - No KYC submitted
- `PENDING` - Under review
- `APPROVED` - Verified
- `REJECTED` - Failed verification
- `EXPIRED` - Needs renewal

## API Endpoints

### Data Fetcher Endpoints

#### Spot Trading
```
GET /api/v1/{exchange}/spot/pairs
GET /api/v1/{exchange}/spot/ticker/{symbol}
GET /api/v1/{exchange}/spot/orderbook/{symbol}
GET /api/v1/{exchange}/spot/trades/{symbol}
GET /api/v1/{exchange}/spot/klines/{symbol}
```

#### Futures Trading
```
GET /api/v1/{exchange}/futures/pairs
GET /api/v1/{exchange}/futures/ticker/{symbol}
GET /api/v1/{exchange}/futures/orderbook/{symbol}
GET /api/v1/{exchange}/futures/funding-rate/{symbol}
```

#### Options Trading
```
GET /api/v1/{exchange}/options/chains
GET /api/v1/{exchange}/options/ticker/{symbol}
```

#### Margin Trading
```
GET /api/v1/{exchange}/margin/info/{symbol}
GET /api/v1/{exchange}/margin/pairs
```

#### Copy Trading
```
GET /api/v1/{exchange}/copy-trading/leaders
GET /api/v1/{exchange}/copy-trading/leader/{leader_id}
```

#### ETF Trading
```
GET /api/v1/{exchange}/etf/list
GET /api/v1/{exchange}/etf/info/{symbol}
```

### Admin Control Endpoints

#### Contract Management
```
POST   /api/v1/admin/contract/create
POST   /api/v1/admin/contract/{contract_id}/launch
POST   /api/v1/admin/contract/{contract_id}/pause
POST   /api/v1/admin/contract/{contract_id}/resume
DELETE /api/v1/admin/contract/{contract_id}
PUT    /api/v1/admin/contract/{contract_id}
GET    /api/v1/admin/contracts
```

#### User Management
```
POST   /api/v1/admin/users/create
GET    /api/v1/admin/users
GET    /api/v1/admin/users/{user_id}
PUT    /api/v1/admin/users/{user_id}
DELETE /api/v1/admin/users/{user_id}
POST   /api/v1/admin/users/{user_id}/suspend
POST   /api/v1/admin/users/{user_id}/activate
POST   /api/v1/admin/users/{user_id}/trading-permission
```

#### Role Management
```
POST /api/v1/admin/roles/{user_id}/assign
GET  /api/v1/admin/roles
```

#### Audit Logs
```
GET /api/v1/admin/audit-logs
```

#### Emergency Controls
```
POST /api/v1/admin/emergency/halt-trading
POST /api/v1/admin/emergency/resume-trading
POST /api/v1/admin/emergency/halt-withdrawals
GET  /api/v1/admin/emergency/actions
```

#### System Statistics
```
GET /api/v1/admin/statistics
```

## Security Features

### 1. Authentication
- JWT-based authentication
- Token expiration
- Secure token generation
- HTTPBearer security scheme

### 2. Authorization
- Role-based access control (RBAC)
- Permission-based access
- Hierarchical role system
- Fine-grained permissions

### 3. Audit Logging
- All admin actions logged
- Timestamp and user tracking
- Action details recorded
- Immutable audit trail

### 4. Emergency Controls
- System-wide trading halt
- Withdrawal suspension
- Emergency action logging
- Quick response capabilities

### 5. Data Protection
- Password hashing (bcrypt)
- Secure token storage
- Input validation
- SQL injection prevention

### 6. Rate Limiting
- API rate limiting (configurable)
- DDoS protection
- Request throttling

## Deployment Guide

### Prerequisites

```bash
# Python 3.11+
python --version

# Install dependencies
pip install fastapi uvicorn pydantic python-jose[cryptography] passlib[bcrypt]
```

### Running the Services

#### 1. Data Fetchers Service

```bash
cd TigerEx/backend/comprehensive-data-fetchers
python complete_exchange_fetchers.py
```

Service will be available at: `http://localhost:8003`

#### 2. Admin Control Service

```bash
cd TigerEx/backend/universal-admin-controls
python complete_admin_service.py
```

Service will be available at: `http://localhost:8004`

### Docker Deployment

```dockerfile
# Dockerfile for Data Fetchers
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY complete_exchange_fetchers.py .
CMD ["python", "complete_exchange_fetchers.py"]
```

```dockerfile
# Dockerfile for Admin Controls
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY complete_admin_service.py .
CMD ["python", "complete_admin_service.py"]
```

### Environment Variables

```bash
# JWT Configuration
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Service Ports
DATA_FETCHERS_PORT=8003
ADMIN_CONTROL_PORT=8004

# CORS Configuration
ALLOWED_ORIGINS=*
```

### API Documentation

Once services are running, access interactive API documentation:

- Data Fetchers: `http://localhost:8003/docs`
- Admin Controls: `http://localhost:8004/docs`

## Usage Examples

### Example 1: Create and Launch a Futures Contract

```python
import requests

# Admin authentication
headers = {
    "Authorization": "Bearer YOUR_ADMIN_TOKEN"
}

# Create contract
create_response = requests.post(
    "http://localhost:8003/api/v1/admin/contract/create",
    headers=headers,
    json={
        "exchange": "binance",
        "trading_type": "futures_perpetual",
        "symbol": "BTC/USDT",
        "base_asset": "BTC",
        "quote_asset": "USDT",
        "leverage_available": [1, 2, 5, 10, 20, 50, 100],
        "min_order_size": 0.001,
        "max_order_size": 1000000,
        "maker_fee": 0.0002,
        "taker_fee": 0.0004
    }
)

contract_id = create_response.json()["contract_id"]

# Launch contract
launch_response = requests.post(
    f"http://localhost:8003/api/v1/admin/contract/{contract_id}/launch",
    headers=headers
)

print(f"Contract {contract_id} launched successfully!")
```

### Example 2: Create User with Trading Permissions

```python
import requests

headers = {
    "Authorization": "Bearer YOUR_ADMIN_TOKEN"
}

# Create user
user_response = requests.post(
    "http://localhost:8004/api/v1/admin/users/create",
    headers=headers,
    json={
        "email": "trader@example.com",
        "username": "trader123",
        "password": "SecurePassword123!",
        "full_name": "John Trader",
        "role": "trader",
        "permissions": [
            "spot_trading",
            "futures_trading",
            "deposit",
            "withdraw"
        ]
    }
)

user_id = user_response.json()["user_id"]
print(f"User {user_id} created successfully!")
```

### Example 3: Emergency Trading Halt

```python
import requests

headers = {
    "Authorization": "Bearer YOUR_SUPER_ADMIN_TOKEN"
}

# Halt all trading
halt_response = requests.post(
    "http://localhost:8004/api/v1/admin/emergency/halt-trading",
    headers=headers,
    json={
        "reason": "Security incident detected"
    }
)

print("Trading halted system-wide!")
```

## Best Practices

### 1. Security
- Change default JWT secret in production
- Use HTTPS in production
- Implement rate limiting
- Regular security audits
- Monitor audit logs

### 2. User Management
- Implement proper KYC procedures
- Regular permission reviews
- Monitor suspicious activities
- Enforce strong passwords
- Enable 2FA for admins

### 3. Contract Management
- Test contracts before launch
- Monitor contract performance
- Regular fee reviews
- Maintain adequate liquidity
- Document all changes

### 4. Emergency Procedures
- Define emergency protocols
- Train admin staff
- Test emergency controls
- Maintain communication channels
- Document all incidents

### 5. Monitoring
- Set up alerting
- Monitor system health
- Track user activities
- Review audit logs regularly
- Performance monitoring

## Support and Maintenance

### Logging

All services include comprehensive logging:
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: System errors
- CRITICAL: Emergency situations

### Health Checks

```bash
# Data Fetchers
curl http://localhost:8003/api/v1/health

# Admin Controls
curl http://localhost:8004/api/v1/health
```

### Troubleshooting

Common issues and solutions:

1. **Authentication Errors**
   - Verify JWT token validity
   - Check token expiration
   - Ensure correct secret key

2. **Permission Denied**
   - Verify user role
   - Check user permissions
   - Review audit logs

3. **Contract Not Found**
   - Verify contract ID
   - Check contract status
   - Review contract list

## Conclusion

This comprehensive system provides full administrative control over all trading operations with complete user access management. The modular architecture allows for easy extension and customization while maintaining security and reliability.

For additional support or questions, please refer to the API documentation or contact the development team.

---

**Version**: 2.0.0  
**Last Updated**: 2025-10-18  
**Maintained By**: TigerEx Development Team