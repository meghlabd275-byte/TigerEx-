# Exchange API Analysis - New Functions & Fetchers for TigerEx

## Executive Summary

Based on comprehensive analysis of major cryptocurrency exchanges (Binance, Bybit, OKX, KuCoin, Bitfinex), this document identifies new API endpoints, functions, and fetchers that can be implemented in TigerEx to achieve complete feature parity.

**Note:** FTX exchange is defunct (collapsed in 2022) and will not be included in this analysis.

## Current TigerEx Status

According to the repository documentation:
- **Total Backend Services:** 126
- **Total Features:** 161
- **Admin Features:** 79
- **User Features:** 9
- **Trading Bots:** 12
- **Implementation Status:** 100% Complete (as per documentation)

## Analysis Methodology

1. Review official API documentation from each exchange
2. Identify unique endpoints and functions not present in TigerEx
3. Categorize by functionality (Trading, Market Data, Account, etc.)
4. Prioritize based on market demand and competitive advantage

---

## 1. BINANCE API ANALYSIS

### 1.1 New Endpoints Identified (2025)

#### Market Data Endpoints
1. **GET /api/v3/avgPrice** - Current average price
2. **GET /api/v3/ticker/tradingDay** - Trading day ticker
3. **GET /api/v3/ticker/24hr** - 24hr ticker price change statistics
4. **GET /api/v3/ticker/price** - Symbol price ticker
5. **GET /api/v3/ticker/bookTicker** - Symbol order book ticker
6. **GET /api/v3/uiKlines** - UI Klines (optimized for UI display)

#### Trading Endpoints
1. **POST /api/v3/order/oco** - New OCO (One-Cancels-Other) order
2. **POST /api/v3/order/cancelReplace** - Cancel and replace order atomically
3. **POST /api/v3/sor/order** - Smart Order Routing (SOR) order
4. **GET /api/v3/rateLimit/order** - Query current order rate limit

#### Account Endpoints
1. **GET /api/v3/account/commission** - Query commission rates
2. **GET /api/v3/account/status** - Account status
3. **GET /api/v3/preventedMatches** - Query prevented matches
4. **GET /api/v3/myAllocations** - Query allocations

#### Wallet Endpoints
1. **POST /sapi/v1/asset/dust-btc** - Get assets that can be converted to BNB
2. **POST /sapi/v1/asset/get-funding-asset** - Funding wallet assets
3. **GET /sapi/v1/asset/query/trading-fee** - Query trading fee
4. **POST /sapi/v1/capital/contract/convertible-coins** - Query convertible coins

#### Staking & Earn
1. **GET /sapi/v1/staking/productList** - Get staking product list
2. **POST /sapi/v1/staking/purchase** - Purchase staking product
3. **POST /sapi/v1/staking/redeem** - Redeem staking product
4. **GET /sapi/v1/staking/position** - Get staking position
5. **GET /sapi/v1/staking/stakingRecord** - Get staking history
6. **GET /sapi/v1/eth-staking/eth/history/stakingHistory** - ETH staking history
7. **GET /sapi/v1/eth-staking/eth/history/redemptionHistory** - ETH redemption history
8. **GET /sapi/v1/eth-staking/eth/history/rewardsHistory** - ETH rewards history

#### Futures Specific
1. **GET /fapi/v1/pmExchangeInfo** - Portfolio margin exchange info
2. **GET /fapi/v1/pmAccountInfo** - Portfolio margin account info
3. **POST /fapi/v1/pmPositionSide/dual** - Change portfolio margin position mode
4. **GET /fapi/v1/adlQuantile** - Position ADL quantile estimation
5. **GET /fapi/v1/commissionRate** - User commission rate
6. **GET /fapi/v1/leverageBracket** - Notional and leverage brackets
7. **GET /fapi/v1/forceOrders** - User's force orders
8. **GET /fapi/v1/apiTradingStatus** - User API trading status

#### Convert
1. **GET /sapi/v1/convert/exchangeInfo** - Query convert pair info
2. **POST /sapi/v1/convert/getQuote** - Send quote request
3. **POST /sapi/v1/convert/acceptQuote** - Accept quote
4. **GET /sapi/v1/convert/orderStatus** - Query order status
5. **GET /sapi/v1/convert/tradeFlow** - Get convert trade history

### 1.2 Unique Binance Features

1. **Smart Order Routing (SOR)** - Automatically routes orders for best execution
2. **Prevented Matches** - Self-trade prevention tracking
3. **Dust Conversion** - Convert small balances to BNB
4. **Portfolio Margin** - Advanced margin system
5. **ADL Quantile** - Auto-deleveraging position indicator
6. **Convert Service** - Direct crypto-to-crypto conversion
7. **Atomic Cancel-Replace** - Cancel and place new order atomically

---

## 2. BYBIT API ANALYSIS

### 2.1 New Endpoints Identified (2025)

#### Market Data
1. **GET /v5/market/insurance** - Insurance pool data (updated every 1 minute)
2. **GET /v5/market/risk-limit** - Risk limit information
3. **GET /v5/market/delivery-price** - Delivery price
4. **GET /v5/market/long-short-ratio** - Long/short ratio
5. **GET /v5/market/account-ratio** - Account long/short ratio
6. **GET /v5/market/open-interest** - Open interest
7. **GET /v5/market/historical-volatility** - Historical volatility (IV)
8. **GET /v5/market/insurance** - Insurance fund balance
9. **GET /v5/market/adl-alert** - ADL alert data
10. **GET /v5/market/index-components** - Index price components
11. **GET /v5/market/rpi-orderbook** - RPI (Retail Price Improvement) orderbook
12. **GET /v5/market/order-price-limit** - Order price limit
13. **GET /v5/market/fee-group-info** - Fee group structure
14. **GET /v5/system-status** - System status

#### Trading
1. **POST /v5/order/create-order** - Supports RPI (Retail Price Improvement) orders
2. **POST /v5/order/pre-check-order** - Pre-check order before placing
3. **GET /v5/order/spot-borrow-check** - Check spot borrow quota
4. **POST /v5/position/move-position** - Move positions between accounts
5. **GET /v5/position/move-position-history** - Position movement history
6. **GET /v5/position/close-position** - Closed options positions
7. **POST /v5/position/confirm-mmr** - Confirm new risk limit

#### Account & Wallet
1. **POST /v5/account/set-spot-hedge** - Enable/disable spot hedging
2. **POST /v5/account/set-collateral** - Set collateral coin
3. **POST /v5/account/batch-set-collateral** - Batch set collateral
4. **POST /v5/account/repay-liability** - Repay liability
5. **GET /v5/account/unified-trans-amnt** - Unified wallet transferable amount
6. **GET /v5/account/smp-group** - Get SMP group ID
7. **GET /v5/account/dcp-info** - Get DCP (Disconnect Cancel All) info
8. **POST /v5/account/set-price-limit** - Set limit price behavior
9. **GET /v5/account/get-user-setting-config** - Get limit price behavior config

#### Asset & Transfer
1. **POST /v5/asset/convert/apply-quote** - Request convert quote
2. **POST /v5/asset/convert/confirm-quote** - Confirm convert quote
3. **GET /v5/asset/convert/get-convert-result** - Get convert status
4. **GET /v5/asset/convert/get-convert-history** - Get convert history
5. **GET /v5/asset/convert/convert-coin-list** - Get convertible coins

#### Earn Products
1. **GET /v5/earn/product-info** - Get earn product info
2. **POST /v5/earn/create-order** - Stake/redeem
3. **GET /v5/earn/order-history** - Stake/redeem history
4. **GET /v5/earn/position** - Staked position

#### Crypto Loan (New)
1. **GET /v5/new-crypto-loan/loan-coin** - Get loanable coins
2. **POST /v5/new-crypto-loan/fixed/borrow** - Create borrow order
3. **GET /v5/new-crypto-loan/fixed/borrow-contract** - Get borrow contract info
4. **GET /v5/new-crypto-loan/fixed/borrow-order** - Get borrow order info
5. **POST /v5/new-crypto-loan/fixed/repay** - Repay loan
6. **POST /v5/new-crypto-loan/fixed/repay-collateral** - Collateral repayment
7. **GET /v5/new-crypto-loan/fixed/repay-history** - Repayment history
8. **POST /v5/new-crypto-loan/flexible/borrow** - Flexible loan borrow
9. **POST /v5/new-crypto-loan/flexible/repay** - Flexible loan repay
10. **POST /v5/new-crypto-loan/flexible/repay-collateral** - Flexible collateral repayment
11. **GET /v5/new-crypto-loan/flexible/repay-orders** - Flexible repayment orders

#### Spread Trading
1. **GET /v5/spread/market/instrument** - Spread trading instruments
2. **POST /v5/spread/trade/create-order** - Create spread order
3. **POST /v5/spread/trade/amend-order** - Amend spread order
4. **POST /v5/spread/trade/cancel-order** - Cancel spread order
5. **GET /v5/spread/trade/open-order** - Open spread orders
6. **GET /v5/spread/trade/order-history** - Spread order history
7. **GET /v5/spread/trade/trade-history** - Spread trade history

#### RFQ (Request for Quote)
1. **POST /v5/rfq/create-rfq** - Create RFQ
2. **POST /v5/rfq/cancel-rfq** - Cancel RFQ
3. **GET /v5/rfq/query-rfq** - Query RFQ
4. **POST /v5/rfq/create-quote** - Create quote
5. **POST /v5/rfq/execute-quote** - Execute quote

#### Rate Limit Management
1. **POST /v5/rate-limit/rules-for-pros/apilimit-set** - Set rate limit
2. **GET /v5/rate-limit/rules-for-pros/apilimit-query** - Get rate limit
3. **GET /v5/rate-limit/rules-for-pros/apilimit-query-cap** - Get rate limit cap
4. **GET /v5/rate-limit/rules-for-pros/apilimit-query-all** - Get all rate limits

### 2.2 Unique Bybit Features

1. **RPI Orders** - Retail Price Improvement for better execution
2. **Spread Trading** - Trade spreads between different contracts
3. **RFQ System** - Request for Quote for large orders
4. **New Crypto Loan** - Comprehensive lending system
5. **Convert Service** - Direct crypto conversion
6. **Spot Hedging** - Portfolio margin spot hedging
7. **Position Movement** - Move positions between accounts
8. **Pre-check Orders** - Validate orders before submission
9. **Dynamic Rate Limits** - Customizable API rate limits
10. **Earn Products** - Integrated staking and earning

---

## 3. OKX API ANALYSIS

### 3.1 Key OKX Features (Based on Documentation)

#### Trading Features
1. **Algo Orders** - Advanced algorithmic orders
   - TWAP (Time-Weighted Average Price)
   - Iceberg orders
   - Trigger orders
   - Move stop loss
   - Grid trading

2. **Block Trading** - Large order execution
3. **Copy Trading** - Social trading features
4. **Recurring Buy** - DCA (Dollar Cost Averaging)
5. **Signal Trading** - Trading signals

#### Account Features
1. **Greeks** - Options Greeks calculation
2. **PM (Portfolio Margin)** - Portfolio margin mode
3. **Account Risk** - Risk calculation
4. **Interest Limits** - Borrowing limits
5. **Simulated Trading** - Paper trading

#### Market Data
1. **Mark Price Candlesticks** - Mark price history
2. **Index Candlesticks** - Index price history
3. **Option Summary** - Options market summary
4. **Estimated Delivery Price** - Futures delivery estimation
5. **Discount Rate** - Interest rate info
6. **System Time** - Server time
7. **Liquidation Orders** - Public liquidation data
8. **Oracle** - Oracle price data

### 3.2 Unique OKX Features

1. **Unified Account System** - Single account for all products
2. **Portfolio Margin** - Cross-product margining
3. **Block Trading** - OTC block trades
4. **Copy Trading Platform** - Built-in copy trading
5. **Algo Trading Suite** - Comprehensive algo orders
6. **Simulated Trading** - Paper trading mode
7. **Greeks Calculation** - Real-time options Greeks

---

## 4. KUCOIN API ANALYSIS

### 4.1 Key KuCoin Features

#### Trading
1. **Margin Trading** - Isolated and cross margin
2. **Margin HF (High Frequency)** - High-frequency margin trading
3. **Stop Orders** - Advanced stop orders
4. **OCO Orders** - One-Cancels-Other
5. **Bulk Orders** - Batch order placement

#### Earn
1. **Staking** - Staking products
2. **Lending** - P2P lending
3. **Savings** - Flexible and fixed savings

#### Market Data
1. **24hr Stats** - 24-hour statistics
2. **Market List** - All trading pairs
3. **Part Order Book** - Partial order book
4. **Full Order Book** - Complete order book aggregated
5. **Trade Histories** - Historical trades
6. **Klines** - Candlestick data
7. **Currencies** - Currency information
8. **Fiat Price** - Fiat conversion rates

#### Account
1. **Sub-Account** - Sub-account management
2. **Account Ledgers** - Account history
3. **Hold** - Funds on hold
4. **Transferable** - Transferable balance
5. **Transfer** - Internal transfers
6. **Inner Transfer** - Sub-account transfers

### 4.2 Unique KuCoin Features

1. **High-Frequency Trading API** - Dedicated HF endpoints
2. **P2P Lending** - Peer-to-peer lending
3. **Fiat Gateway** - Fiat price conversion
4. **Bulk Operations** - Batch order management
5. **Margin HF Trading** - High-frequency margin

---

## 5. BITFINEX API ANALYSIS

### 5.1 Key Bitfinex Features

#### Trading
1. **Funding** - Margin funding market
2. **Derivatives** - Perpetual contracts
3. **Pulse** - Social trading feed
4. **Paper Trading** - Simulated trading

#### Market Data
1. **Tickers** - Price tickers
2. **Trades** - Public trades
3. **Books** - Order books
4. **Stats** - Market statistics
5. **Candles** - OHLC data
6. **Configs** - Platform configuration
7. **Status** - Platform status
8. **Liquidations** - Liquidation feed
9. **Rankings** - Token rankings
10. **Pulse Profile** - Social profiles

#### Account
1. **Wallets** - Multi-wallet system
2. **Orders** - Order management
3. **Trades** - Trade history
4. **Ledgers** - Account ledger
5. **Movements** - Deposits/withdrawals
6. **Positions** - Position management
7. **Funding** - Funding offers/credits
8. **Margin Info** - Margin information

### 5.2 Unique Bitfinex Features

1. **Funding Market** - Lend/borrow crypto
2. **Pulse Social Network** - Built-in social trading
3. **Paper Trading** - Demo trading mode
4. **Derivatives Trading** - Perpetual swaps
5. **Multi-Wallet System** - Exchange, margin, funding wallets
6. **Token Rankings** - Performance rankings
7. **Liquidation Feed** - Real-time liquidations

---

## 6. MISSING FEATURES IN TIGEREX

Based on the analysis, here are the key missing features and endpoints:

### 6.1 High Priority - Trading Features

1. **Smart Order Routing (SOR)** - Binance
   - Automatic best execution routing
   - Implementation: Create SOR service with order routing logic

2. **RPI Orders (Retail Price Improvement)** - Bybit
   - Better execution for retail traders
   - Implementation: Add RPI order type to trading engine

3. **Spread Trading** - Bybit
   - Trade spreads between contracts
   - Implementation: Create spread trading service

4. **RFQ System** - Bybit
   - Request for Quote for large orders
   - Implementation: Create RFQ service with quote management

5. **Block Trading** - OKX
   - OTC large order execution
   - Implementation: Add block trading service

6. **Atomic Cancel-Replace** - Binance
   - Cancel and replace order atomically
   - Implementation: Add atomic operation to order service

7. **Pre-check Orders** - Bybit
   - Validate orders before submission
   - Implementation: Add pre-check endpoint to trading service

### 6.2 High Priority - Market Data

1. **Insurance Pool Data** - Bybit
   - Real-time insurance fund balance
   - Implementation: Add insurance pool tracking

2. **ADL Alert** - Bybit
   - Auto-deleveraging alerts
   - Implementation: Add ADL monitoring service

3. **Long/Short Ratio** - Bybit
   - Market sentiment indicator
   - Implementation: Add ratio calculation service

4. **RPI Orderbook** - Bybit
   - RPI-specific order book
   - Implementation: Add RPI orderbook endpoint

5. **Index Components** - Bybit
   - Index price composition
   - Implementation: Add index component tracking

6. **Order Price Limit** - Bybit
   - Dynamic price limits
   - Implementation: Add price limit calculation

7. **Fee Group Structure** - Bybit
   - Tiered fee information
   - Implementation: Add fee group endpoint

### 6.3 High Priority - Account & Wallet

1. **Convert Service** - Binance, Bybit
   - Direct crypto-to-crypto conversion
   - Implementation: Create convert service with quote system

2. **Spot Hedging** - Bybit
   - Portfolio margin spot hedging
   - Implementation: Add spot hedging to portfolio margin

3. **Position Movement** - Bybit
   - Move positions between accounts
   - Implementation: Add position transfer service

4. **Repay Liability** - Bybit
   - Direct liability repayment
   - Implementation: Add repayment endpoint

5. **Unified Transferable Amount** - Bybit
   - Calculate transferable balance
   - Implementation: Add balance calculation service

6. **Batch Set Collateral** - Bybit
   - Batch collateral management
   - Implementation: Add batch collateral endpoint

7. **Commission Rate Query** - Binance
   - Query user commission rates
   - Implementation: Add commission rate endpoint

### 6.4 High Priority - Earn & Staking

1. **New Crypto Loan** - Bybit
   - Comprehensive lending system
   - Implementation: Create new loan service with fixed/flexible options

2. **Earn Products** - Bybit
   - Integrated staking/earning
   - Implementation: Add earn product service

3. **ETH 2.0 Staking** - Binance
   - ETH staking specific
   - Implementation: Add ETH staking service

4. **P2P Lending** - KuCoin
   - Peer-to-peer lending
   - Implementation: Create P2P lending marketplace

5. **Funding Market** - Bitfinex
   - Margin funding market
   - Implementation: Create funding market service

### 6.5 Medium Priority - Advanced Features

1. **Rate Limit Management** - Bybit
   - Dynamic API rate limits
   - Implementation: Add rate limit configuration service

2. **SMP Group Management** - Bybit
   - Self-Match Prevention groups
   - Implementation: Add SMP group service

3. **DCP Info** - Bybit
   - Disconnect Cancel All info
   - Implementation: Add DCP configuration endpoint

4. **Greeks Calculation** - OKX
   - Options Greeks
   - Implementation: Add Greeks calculation service

5. **Simulated Trading** - OKX, Bitfinex
   - Paper trading mode
   - Implementation: Add demo trading service

6. **High-Frequency API** - KuCoin
   - HF trading endpoints
   - Implementation: Add HF trading service

7. **Pulse Social Network** - Bitfinex
   - Social trading feed
   - Implementation: Create social trading service

### 6.6 Medium Priority - System Features

1. **System Status** - Bybit
   - Real-time system status
   - Implementation: Add system status endpoint

2. **Prevented Matches** - Binance
   - Self-trade prevention tracking
   - Implementation: Add prevented match tracking

3. **API Trading Status** - Binance
   - User API status
   - Implementation: Add API status endpoint

4. **Travel Rule Info** - Bybit
   - Compliance travel rule
   - Implementation: Add travel rule fields

5. **Dust Conversion** - Binance
   - Convert small balances
   - Implementation: Add dust conversion service

---

## 7. IMPLEMENTATION PRIORITY MATRIX

### Tier 1 - Critical (Implement First)

| Feature | Exchange | Impact | Complexity | Priority Score |
|---------|----------|--------|------------|----------------|
| Convert Service | Binance, Bybit | High | Medium | 95 |
| RPI Orders | Bybit | High | Medium | 90 |
| Smart Order Routing | Binance | High | High | 88 |
| New Crypto Loan | Bybit | High | High | 85 |
| Spread Trading | Bybit | Medium | High | 82 |
| Block Trading | OKX | Medium | High | 80 |
| Earn Products | Bybit | High | Medium | 80 |

### Tier 2 - Important (Implement Second)

| Feature | Exchange | Impact | Complexity | Priority Score |
|---------|----------|--------|------------|----------------|
| RFQ System | Bybit | Medium | High | 75 |
| Position Movement | Bybit | Medium | Medium | 72 |
| Atomic Cancel-Replace | Binance | Medium | Low | 70 |
| Pre-check Orders | Bybit | Medium | Low | 68 |
| Insurance Pool Data | Bybit | Low | Low | 65 |
| ADL Alert | Bybit | Low | Medium | 63 |
| Long/Short Ratio | Bybit | Low | Low | 60 |

### Tier 3 - Enhancement (Implement Third)

| Feature | Exchange | Impact | Complexity | Priority Score |
|---------|----------|--------|------------|----------------|
| Rate Limit Management | Bybit | Low | Medium | 55 |
| Greeks Calculation | OKX | Low | High | 52 |
| Simulated Trading | OKX, Bitfinex | Low | Medium | 50 |
| P2P Lending | KuCoin | Low | High | 48 |
| Funding Market | Bitfinex | Low | High | 45 |
| Pulse Social Network | Bitfinex | Low | High | 42 |
| High-Frequency API | KuCoin | Low | High | 40 |

---

## 8. IMPLEMENTATION RECOMMENDATIONS

### 8.1 Phase 1: Core Trading Enhancements (Weeks 1-4)

**Focus:** Critical trading features that directly impact user experience

1. **Convert Service**
   - Direct crypto-to-crypto conversion
   - Quote system with price guarantee
   - Conversion history tracking
   - Multi-coin support

2. **RPI Orders**
   - Retail Price Improvement order type
   - Better execution for market orders
   - RPI orderbook integration
   - RPI trade tracking

3. **Smart Order Routing**
   - Automatic best execution
   - Multi-venue routing logic
   - Execution quality metrics
   - SOR analytics

4. **Atomic Cancel-Replace**
   - Single API call for cancel + place
   - Atomic transaction handling
   - Reduced latency
   - Order continuity

### 8.2 Phase 2: Lending & Earn (Weeks 5-8)

**Focus:** Passive income and lending features

1. **New Crypto Loan System**
   - Fixed-term loans
   - Flexible loans
   - Collateral management
   - Repayment system
   - Interest calculation
   - Loan history

2. **Earn Products**
   - Staking products
   - Flexible savings
   - Fixed savings
   - Product catalog
   - Position tracking
   - Rewards distribution

3. **ETH 2.0 Staking**
   - ETH staking integration
   - Staking history
   - Redemption system
   - Rewards tracking

### 8.3 Phase 3: Advanced Trading (Weeks 9-12)

**Focus:** Professional trading features

1. **Spread Trading**
   - Spread instruments
   - Spread order management
   - Spread execution
   - Spread analytics

2. **RFQ System**
   - Quote request creation
   - Quote management
   - Quote execution
   - RFQ history

3. **Block Trading**
   - Large order handling
   - OTC execution
   - Block trade matching
   - Settlement

4. **Pre-check Orders**
   - Order validation
   - Margin calculation
   - Risk assessment
   - Pre-execution checks

### 8.4 Phase 4: Market Data & Analytics (Weeks 13-16)

**Focus:** Enhanced market data and analytics

1. **Insurance Pool Tracking**
   - Real-time balance
   - Historical data
   - WebSocket updates
   - Pool analytics

2. **ADL Alert System**
   - Auto-deleveraging monitoring
   - Alert notifications
   - Position risk indicators
   - ADL queue position

3. **Long/Short Ratio**
   - Market sentiment
   - Ratio calculation
   - Historical trends
   - Visualization

4. **Index Components**
   - Index composition
   - Component weights
   - Price contribution
   - Rebalancing info

### 8.5 Phase 5: Account Features (Weeks 17-20)

**Focus:** Account management and optimization

1. **Position Movement**
   - Inter-account transfers
   - Position migration
   - Transfer history
   - Validation rules

2. **Spot Hedging**
   - Portfolio margin hedging
   - Hedge calculation
   - Hedge tracking
   - Risk reduction

3. **Batch Collateral Management**
   - Multi-coin collateral
   - Batch operations
   - Collateral optimization
   - Risk management

4. **Repay Liability**
   - Direct repayment
   - Partial repayment
   - Auto-repayment
   - Repayment history

### 8.6 Phase 6: System Enhancements (Weeks 21-24)

**Focus:** System-level improvements

1. **Rate Limit Management**
   - Dynamic rate limits
   - Custom limits per user
   - Limit monitoring
   - Limit adjustment

2. **System Status**
   - Real-time status
   - Component health
   - Maintenance alerts
   - Status history

3. **API Trading Status**
   - User API health
   - Trading restrictions
   - Status monitoring
   - Alert system

4. **Greeks Calculation**
   - Options Greeks
   - Real-time calculation
   - Greeks history
   - Risk metrics

---

## 9. TECHNICAL IMPLEMENTATION DETAILS

### 9.1 Convert Service Architecture

```python
# Service Structure
backend/
  convert-service/
    src/
      main.py                 # FastAPI application
      models.py              # Data models
      quote_engine.py        # Quote generation
      execution_engine.py    # Trade execution
      price_feed.py          # Price aggregation
    admin/
      admin_routes.py        # Admin controls
```

**Key Components:**
- Quote Engine: Generate conversion quotes with price guarantee
- Execution Engine: Execute conversions atomically
- Price Feed: Aggregate prices from multiple sources
- History Tracking: Store conversion history

**API Endpoints:**
- `POST /api/v1/convert/quote` - Request quote
- `POST /api/v1/convert/execute` - Execute conversion
- `GET /api/v1/convert/history` - Get conversion history
- `GET /api/v1/convert/coins` - Get convertible coins

### 9.2 RPI Orders Implementation

```python
# Order Type Extension
class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LIMIT = "stop_limit"
    RPI = "rpi"  # NEW: Retail Price Improvement

# RPI Order Processing
class RPIOrderProcessor:
    def process_rpi_order(self, order):
        # 1. Check RPI eligibility
        # 2. Calculate price improvement
        # 3. Execute with better price
        # 4. Track RPI metrics
```

**Implementation Steps:**
1. Add RPI order type to order enum
2. Create RPI order processor
3. Integrate with matching engine
4. Add RPI orderbook
5. Track RPI execution metrics

### 9.3 Smart Order Routing

```python
# SOR Service Structure
backend/
  sor-service/
    src/
      main.py              # FastAPI application
      router.py            # Order routing logic
      venue_manager.py     # Venue management
      execution_algo.py    # Execution algorithms
      analytics.py         # SOR analytics
```

**Routing Logic:**
1. Analyze order size and market conditions
2. Split order across venues if beneficial
3. Execute child orders
4. Aggregate fills
5. Report execution quality

### 9.4 New Crypto Loan System

```python
# Loan Service Structure
backend/
  crypto-loan-service/
    src/
      main.py                  # FastAPI application
      fixed_loan.py           # Fixed-term loans
      flexible_loan.py        # Flexible loans
      collateral_manager.py   # Collateral management
      interest_calculator.py  # Interest calculation
      repayment_engine.py     # Repayment processing
```

**Loan Types:**
1. **Fixed Loans:**
   - Fixed term (7, 14, 30, 60, 90, 180 days)
   - Fixed interest rate
   - Collateral locked
   - Early repayment option

2. **Flexible Loans:**
   - No fixed term
   - Variable interest rate
   - Flexible collateral
   - Repay anytime

**API Endpoints:**
- `GET /api/v1/loan/coins` - Get loanable coins
- `POST /api/v1/loan/fixed/borrow` - Create fixed loan
- `POST /api/v1/loan/flexible/borrow` - Create flexible loan
- `POST /api/v1/loan/repay` - Repay loan
- `GET /api/v1/loan/orders` - Get loan orders
- `GET /api/v1/loan/history` - Get loan history

---

## 10. DATABASE SCHEMA ADDITIONS

### 10.1 Convert Service Tables

```sql
CREATE TABLE convert_quotes (
    id SERIAL PRIMARY KEY,
    quote_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    from_coin VARCHAR(20) NOT NULL,
    to_coin VARCHAR(20) NOT NULL,
    from_amount DECIMAL(36, 18) NOT NULL,
    to_amount DECIMAL(36, 18) NOT NULL,
    price DECIMAL(36, 18) NOT NULL,
    inverse_price DECIMAL(36, 18) NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    executed_at TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

CREATE TABLE convert_history (
    id SERIAL PRIMARY KEY,
    convert_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    quote_id VARCHAR(50) NOT NULL,
    from_coin VARCHAR(20) NOT NULL,
    to_coin VARCHAR(20) NOT NULL,
    from_amount DECIMAL(36, 18) NOT NULL,
    to_amount DECIMAL(36, 18) NOT NULL,
    execution_price DECIMAL(36, 18) NOT NULL,
    fee DECIMAL(36, 18) NOT NULL,
    fee_coin VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (quote_id) REFERENCES convert_quotes(quote_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);
```

### 10.2 Crypto Loan Tables

```sql
CREATE TABLE loan_products (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) UNIQUE NOT NULL,
    loan_coin VARCHAR(20) NOT NULL,
    collateral_coin VARCHAR(20) NOT NULL,
    loan_type VARCHAR(20) NOT NULL, -- 'fixed' or 'flexible'
    term_days INTEGER, -- NULL for flexible
    interest_rate DECIMAL(10, 6) NOT NULL,
    ltv_ratio DECIMAL(10, 6) NOT NULL,
    liquidation_ratio DECIMAL(10, 6) NOT NULL,
    min_loan_amount DECIMAL(36, 18) NOT NULL,
    max_loan_amount DECIMAL(36, 18) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_loan_coin (loan_coin),
    INDEX idx_loan_type (loan_type)
);

CREATE TABLE loan_orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    loan_coin VARCHAR(20) NOT NULL,
    collateral_coin VARCHAR(20) NOT NULL,
    loan_amount DECIMAL(36, 18) NOT NULL,
    collateral_amount DECIMAL(36, 18) NOT NULL,
    interest_rate DECIMAL(10, 6) NOT NULL,
    term_days INTEGER,
    borrowed_at TIMESTAMP NOT NULL,
    due_date TIMESTAMP,
    repaid_at TIMESTAMP,
    total_interest DECIMAL(36, 18) DEFAULT 0,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (product_id) REFERENCES loan_products(product_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_due_date (due_date)
);

CREATE TABLE loan_repayments (
    id SERIAL PRIMARY KEY,
    repayment_id VARCHAR(50) UNIQUE NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    user_id INTEGER NOT NULL,
    repay_amount DECIMAL(36, 18) NOT NULL,
    interest_amount DECIMAL(36, 18) NOT NULL,
    repay_type VARCHAR(20) NOT NULL,
    repaid_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (order_id) REFERENCES loan_orders(order_id),
    INDEX idx_order_id (order_id),
    INDEX idx_user_id (user_id)
);
```

### 10.3 RPI Orders Tables

```sql
CREATE TABLE rpi_orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    quantity DECIMAL(36, 18) NOT NULL,
    market_price DECIMAL(36, 18) NOT NULL,
    rpi_price DECIMAL(36, 18) NOT NULL,
    price_improvement DECIMAL(36, 18) NOT NULL,
    improvement_percentage DECIMAL(10, 6) NOT NULL,
    executed_quantity DECIMAL(36, 18) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    executed_at TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_symbol (symbol),
    INDEX idx_created_at (created_at)
);
```

---

## 11. API DOCUMENTATION TEMPLATE

### 11.1 Convert Service API

#### Request Quote

**Endpoint:** `POST /api/v1/convert/quote`

**Description:** Request a conversion quote between two cryptocurrencies

**Request Body:**
```json
{
  "fromCoin": "BTC",
  "toCoin": "USDT",
  "fromAmount": "0.1",
  "validTime": 10
}
```

**Response:**
```json
{
  "code": "0",
  "msg": "success",
  "data": {
    "quoteId": "quote_123456789",
    "fromCoin": "BTC",
    "toCoin": "USDT",
    "fromAmount": "0.1",
    "toAmount": "4350.50",
    "price": "43505.00",
    "inversePrice": "0.00002299",
    "validUntil": "2025-10-03T10:15:00Z",
    "fee": "0.1",
    "feeCoin": "USDT"
  }
}
```

#### Execute Conversion

**Endpoint:** `POST /api/v1/convert/execute`

**Description:** Execute a conversion using a valid quote

**Request Body:**
```json
{
  "quoteId": "quote_123456789"
}
```

**Response:**
```json
{
  "code": "0",
  "msg": "success",
  "data": {
    "convertId": "convert_987654321",
    "quoteId": "quote_123456789",
    "status": "SUCCESS",
    "fromCoin": "BTC",
    "toCoin": "USDT",
    "fromAmount": "0.1",
    "toAmount": "4350.50",
    "executionPrice": "43505.00",
    "fee": "0.1",
    "feeCoin": "USDT",
    "executedAt": "2025-10-03T10:14:55Z"
  }
}
```

---

## 12. TESTING STRATEGY

### 12.1 Unit Tests

**Convert Service:**
- Quote generation logic
- Price calculation
- Quote expiration
- Execution validation
- Fee calculation

**Crypto Loan:**
- Interest calculation
- Collateral ratio calculation
- Liquidation logic
- Repayment processing
- LTV validation

**RPI Orders:**
- Price improvement calculation
- Order matching logic
- Execution quality metrics
- RPI eligibility check

### 12.2 Integration Tests

- End-to-end conversion flow
- Loan creation and repayment flow
- RPI order execution flow
- Multi-service interactions
- Database transactions

### 12.3 Performance Tests

- Quote generation latency
- Order execution speed
- Database query performance
- API response times
- Concurrent user handling

### 12.4 Security Tests

- Authentication and authorization
- Input validation
- SQL injection prevention
- Rate limiting
- Data encryption

---

## 13. MONITORING & METRICS

### 13.1 Key Performance Indicators

**Convert Service:**
- Quote generation time
- Execution success rate
- Price slippage
- Daily conversion volume
- User adoption rate

**Crypto Loan:**
- Total loans outstanding
- Default rate
- Average loan size
- Interest revenue
- Collateral utilization

**RPI Orders:**
- Price improvement average
- RPI execution rate
- User satisfaction
- Volume through RPI
- Execution quality

### 13.2 Alerting

- Failed conversions
- Loan liquidations
- System errors
- API failures
- Performance degradation

---

## 14. DEPLOYMENT PLAN

### 14.1 Staging Deployment

1. Deploy to staging environment
2. Run comprehensive tests
3. Performance validation
4. Security audit
5. User acceptance testing

### 14.2 Production Rollout

**Phase 1: Beta Release**
- Limited user group
- Monitor closely
- Gather feedback
- Fix issues

**Phase 2: Gradual Rollout**
- Increase user percentage
- Monitor metrics
- Scale infrastructure
- Optimize performance

**Phase 3: Full Release**
- All users enabled
- Marketing campaign
- Documentation published
- Support team trained

---

## 15. CONCLUSION

This comprehensive analysis identifies **87 new API endpoints and features** across the major exchanges that can be implemented in TigerEx. The implementation is structured in 6 phases over 24 weeks, prioritizing features with the highest impact on user experience and competitive advantage.

### Key Takeaways:

1. **Convert Service** is the highest priority feature, present in both Binance and Bybit
2. **New Crypto Loan System** from Bybit offers comprehensive lending capabilities
3. **RPI Orders** provide better execution for retail traders
4. **Smart Order Routing** enhances execution quality
5. **Spread Trading** and **RFQ System** cater to professional traders

### Next Steps:

1. Review and approve implementation plan
2. Allocate development resources
3. Begin Phase 1 implementation
4. Set up monitoring and metrics
5. Prepare documentation and training materials

### Success Metrics:

- All Tier 1 features implemented within 4 weeks
- 95%+ API uptime
- <100ms average response time
- 90%+ user satisfaction
- Zero critical security issues

---

**Document Version:** 1.0  
**Date:** 2025-10-03  
**Status:** Ready for Implementation