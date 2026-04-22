# TigerEx Trading Pair & Coin Management System

Complete system for managing coins, tokens, trading pairs, and blockchain addresses.

## Features

### Coin/Token Management
- Add new coins and tokens with logos
- Support for coins (native) and tokens (ERC20, BEP20, SPL, TRC20, etc.)
- Multiple blockchain networks per coin
- Deposit address generation
- Withdrawal address generation
- Whitepaper and documentation upload
- Social media links (Twitter, Telegram, Discord)
- Website URL

### Blockchain Networks Supported
1. **Bitcoin (BTC)** - main
2. **Ethereum (ETH)** - ERC20
3. **BNB Smart Chain (BSC)** - BEP20
4. **Solana (SOL)** - SPL
5. **Polygon (MATIC)** - ERC20
6. **Avalanche (AVAX)** - C-Chain
7. **Arbitrum (ARB)** - ERC20
8. **Optimism (OP)** - ERC20
9. **Tron (TRX)** - TRC20

### Trading Pair Management
- Create trading pairs (e.g., BTC/USDT, ETH/USDT)
- Configure maker/taker fees
- Set min/max trade amounts
- Price and quantity precision
- Enable/disable trading pairs

### Role-Based Access Control
- **Admin** - Full access to all features
  - Manage users and roles
  - Manage coins and tokens
  - System settings
  - View audit logs
  
- **Manager** - Trading and coin management
  - Manage coins and tokens
  - Manage trading pairs
  - View transactions
  
- **Trader** - Trading access only
  - View markets
  - Execute trades
  - View own transactions
  
- **Viewer** - Read-only access
  - View dashboard
  - View reports

## Folder Structure

```
coin-data/
├── data.json              # Database data
├── database_schema.sql   # SQL schema for PostgreSQL
├── logos/               # Coin logos
├── whitepapers/         # Coin whitepapers
├── documents/         # Additional documents
├── networks/          # Network configurations
└── qr-codes/         # QR codes for addresses
```

## Files Created

1. **coin-management.html** - Complete coin/trading pair management UI with:
   - Dashboard with statistics
   - Coin listing with search/filter
   - Add new coin modal with logo upload
   - Network address generation
   - Whitepaper and social media links
   - Trading pair management
   
2. **admin-dashboard-complete.html** - Role-based admin dashboard with:
   - Login with role selection
   - Role-based menu visibility
   - User management
   - Permission management
   - System settings
   
3. **coin-management-api.py** - RESTful API with:
   - `/api/coins` - Coin management
   - `/api/networks` - Network management
   - `/api/pairs` - Trading pair management
   - `/api/transactions` - Transaction management
   - Authentication with JWT
   - Role-based access control
   
4. **coin-data/database_schema.sql** - PostgreSQL schema

5. **coin-data/data.json** - Initial data

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout

### Coins
- `GET /api/coins` - List all coins
- `GET /api/coins/<id>` - Get single coin
- `POST /api/coins` - Create coin (admin)
- `PUT /api/coins/<id>` - Update coin (admin)
- `DELETE /api/coins/<id>` - Delete coin (admin)

### Networks
- `GET /api/networks` - List networks
- `POST /api/networks` - Create network (admin)

### Addresses
- `GET /api/coins/<id>/addresses` - Get addresses
- `POST /api/coins/<id>/addresses/deposit` - Generate deposit address
- `POST /api/coins/<id>/addresses/withdraw` - Generate withdrawal address

### Trading Pairs
- `GET /api/pairs` - List pairs
- `GET /api/pairs/<symbol>` - Get pair
- `POST /api/pairs` - Create pair (manager)
- `PUT /api/pairs/<symbol>` - Update pair (manager)

### Transactions
- `GET /api/transactions` - List user transactions
- `POST /api/transactions` - Create transaction

### Utility
- `GET /api/health` - Health check
- `GET /api/stats` - Statistics

## Running the API

```bash
# Install Flask
pip install flask

# Run the API
python coin-management-api.py
```

The API will start on port 5001.

## Demo Credentials

- Username: `admin`, Password: `admin123`, Role: `admin`
- Username: `manager`, Password: `manager123`, Role: `manager`
- Username: `trader`, Password: `trader123`, Role: `trader`

## Integration with Main Platform

The coin management system can be integrated with the main TigerEx platform:
- Connect to the main database
- Use the same authentication system
- Share wallet addresses with the trading engine

## Address Generation

The system generates valid cryptocurrency addresses:
- **Bitcoin**: bc1q... (Bech32)
- **Ethereum/BSC/Polygon/Arbitrum/Optimism**: 0x... (Hex)
- **Solana**: Base58 encoded
- **Tron**: T... (Base58)

All addresses are auto-generated for demonstration - in production, integrate with actual blockchain nodes.