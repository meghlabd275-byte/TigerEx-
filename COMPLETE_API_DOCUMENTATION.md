# 📚 COMPLETE API DOCUMENTATION
## TigerEx Exchange - All 1,000+ Endpoints

### 🎯 OVERVIEW
This documentation covers all API endpoints for the TigerEx cryptocurrency exchange platform. All endpoints are RESTful and follow standard HTTP conventions.

### 🔐 AUTHENTICATION
All endpoints require authentication unless marked as public. Use Bearer token in Authorization header:
```
Authorization: Bearer <your_api_key>
```

---

### 📊 TRADING APIS

#### SPOT TRADING
```
GET    /api/v1/spot/symbols                    # Get trading pairs
GET    /api/v1/spot/ticker/24hr                # 24hr ticker
GET    /api/v1/spot/depth                      # Order book depth
GET    /api/v1/spot/trades                     # Recent trades
POST   /api/v1/spot/order                      # Place order
DELETE /api/v1/spot/order                      # Cancel order
GET    /api/v1/spot/order                      # Get order status
GET    /api/v1/spot/open-orders                # Get open orders
GET    /api/v1/spot/all-orders                 # Get all orders
GET    /api/v1/spot/account                    # Get account info
POST   /api/v1/spot/batch-orders               # Batch orders
DELETE /api/v1/spot/batch-orders               # Batch cancel
GET    /api/v1/spot/my-trades                  # Get user trades
POST   /api/v1/spot/oco                        # Place OCO order
GET    /api/v1/spot/oco                        # Get OCO orders
DELETE /api/v1/spot/oco                        # Cancel OCO order
```

#### FUTURES TRADING
```
GET    /api/v1/futures/exchangeInfo             # Exchange info
GET    /api/v1/futures/depth                    # Order book
GET    /api/v1/futures/trades                   # Recent trades
GET    /api/v1/futures/klines                   # Kline/candlestick data
GET    /api/v1/futures/ticker/24hr             # 24hr ticker
POST   /api/v1/futures/order                    # Place order
DELETE /api/v1/futures/order                    # Cancel order
GET    /api/v1/futures/order                    # Get order status
GET    /api/v1/futures/open-orders              # Get open orders
GET    /api/v1/futures/all-orders               # Get all orders
POST   /api/v1/futures/batch-orders             # Batch orders
DELETE /api/v1/futures/batch-orders             # Batch cancel
GET    /api/v1/futures/position                 # Get position
GET    /api/v1/futures/account                  # Get account info
POST   /api/v1/futures/leverage                 # Change leverage
POST   /api/v1/futures/margin-type              # Change margin type
POST   /api/v1/futures/position-margin          # Modify isolated position margin
GET    /api/v1/futures/position-margin/history  # Position margin history
GET    /api/v1/futures/income                   # Get income history
```

#### OPTIONS TRADING
```
GET    /api/v1/options/exchangeInfo             # Exchange info
GET    /api/v1/options/depth                    # Order book
GET    /api/v1/options/trades                   # Recent trades
GET    /api/v1/options/klines                   # Kline data
POST   /api/v1/options/order                    # Place order
DELETE /api/v1/options/order                    # Cancel order
GET    /api/v1/options/order                    # Get order status
GET    /api/v1/options/open-orders              # Get open orders
GET    /api/v1/options/all-orders               # Get all orders
GET    /api/v1/options/position                 # Get positions
GET    /api/v1/options/account                  # Get account info
```

#### MARGIN TRADING
```
GET    /api/v1/margin/asset                     # Get margin asset
GET    /api/v1/margin/pair                      # Get margin pair
GET    /api/v1/margin/all-assets                # Get all margin assets
GET    /api/v1/margin/all-pairs                 # Get all margin pairs
POST   /api/v1/margin/transfer                  # Transfer assets
POST   /api/v1/margin/loan                      # Apply for loan
GET    /api/v1/margin/loan                      # Query loan record
POST   /api/v1/margin/repay                     # Repay loan
GET    /api/v1/margin/repay                     # Query repay record
GET    /api/v1/margin/account                   # Get margin account info
POST   /api/v1/margin/order                     # Place margin order
DELETE /api/v1/margin/order                     # Cancel margin order
GET    /api/v1/margin/order                     # Get margin order status
GET    /api/v1/margin/open-orders               # Get open margin orders
GET    /api/v1/margin/all-orders                # Get all margin orders
GET    /api/v1/margin/my-trades                 # Get margin trades
GET    /api/v1/margin/max-borrowable            # Get max borrowable
GET    /api/v1/margin/max-transferable          # Get max transferable
```

---

### 🤖 TRADING BOTS APIS

#### GRID TRADING
```
POST   /api/v1/grid/enable                      # Enable grid trading
POST   /api/v1/grid/disable                     # Disable grid trading
GET    /api/v1/grid/orders                      # Get grid orders
POST   /api/v1/grid/order                       # Place grid order
DELETE /api/v1/grid/order                       # Cancel grid order
GET    /api/v1/grid/order                       # Get grid order status
GET    /api/v1/grid/sub-orders                  # Get grid sub-orders
GET    /api/v1/grid/sub-orders-details          # Get grid sub-orders details
```

#### COPY TRADING
```
GET    /api/v1/copy-trading/portfolio           # Get portfolio
GET    /api/v1/copy-trading/lead-portfolio      # Get lead portfolio
GET    /api/v1/copy-trading/followers           # Get followers
POST   /api/v1/copy-trading/follow              # Follow trader
POST   /api/v1/copy-trading/unfollow            # Unfollow trader
GET    /api/v1/copy-trading/following           # Get following list
GET    /api/v1/copy-trading/performance         # Get performance
GET    /api/v1/copy-trading/positions           # Get positions
GET    /api/v1/copy-trading/orders              # Get orders
```

#### DCA BOT
```
POST   /api/v1/dca/order                        # Create DCA order
DELETE /api/v1/dca/order                        # Cancel DCA order
GET    /api/v1/dca/order                        # Get DCA order
GET    /api/v1/dca/orders                       # Get all DCA orders
POST   /api/v1/dca/order/pause                  # Pause DCA order
POST   /api/v1/dca/order/resume                 # Resume DCA order
```

---

### 💰 EARN & STAKING APIS

#### SAVINGS
```
GET    /api/v1/savings/product-list             # Get product list
POST   /api/v1/savings/purchase                 # Purchase product
POST   /api/v1/savings/redeem                   # Redeem product
GET    /api/v1/savings/position                 # Get position
GET    /api/v1/savings/project/list             # Get project list
POST   /api/v1/savings/project/purchase         # Purchase project
POST   /api/v1/savings/project/redeem           # Redeem project
GET    /api/v1/savings/project/position         # Get project position
```

#### STAKING
```
GET    /api/v1/staking/product-list             # Get staking product list
POST   /api/v1/staking/stake                    # Stake
POST   /api/v1/staking/redeem                   # Redeem
GET    /api/v1/staking/position                 # Get staking position
GET    /api/v1/staking/history                  # Get staking history
GET    /api/v1/staking/eth2/product-list        # Get ETH2 product list
POST   /api/v1/staking/eth2/stake               # Stake ETH2
POST   /api/v1/staking/eth2/redeem              # Redeem ETH2
GET    /api/v1/staking/eth2/position            # Get ETH2 position
```

#### YIELD FARMING
```
GET    /api/v1/yield-farming/pairs              # Get farming pairs
POST   /api/v1/yield-farming/liquidity          # Add liquidity
DELETE /api/v1/yield-farming/liquidity          # Remove liquidity
GET    /api/v1/yield-farming/position           # Get position
GET    /api/v1/yield-farming/history            # Get history
```

---

### 💳 PAYMENT & CARD APIS

#### FIAT GATEWAY
```
GET    /api/v1/fiat/orders                      # Get fiat orders
POST   /api/v1/fiat/order                       # Create fiat order
GET    /api/v1/fiat/payments                    # Get payment methods
GET    /api/v1/fiat/rate                        # Get fiat rate
```

#### P2P TRADING
```
GET    /api/v1/p2p/ads                          # Get P2P ads
POST   /api/v1/p2p/ad                           # Create P2P ad
POST   /api/v1/p2p/order                        # Create P2P order
GET    /api/v1/p2p/order                        # Get P2P order
POST   /api/v1/p2p/order/cancel                 # Cancel P2P order
POST   /api/v1/p2p/order/confirm                # Confirm P2P order
GET    /api/v1/p2p/user-ads                      # Get user ads
```

#### CRYPTO CARD
```
POST   /api/v1/card/create                      # Create card
GET    /api/v1/card/list                        # Get cards
GET    /api/v1/card/balance                     # Get card balance
POST   /api/v1/card/transaction                 # Create transaction
GET    /api/v1/card/transactions                # Get transactions
POST   /api/v1/card/freeze                      # Freeze card
POST   /api/v1/card/unfreeze                    # Unfreeze card
```

---

### 🎨 NFT APIS

#### MARKETPLACE
```
GET    /api/v1/nft/marketplace/collections      # Get collections
GET    /api/v1/nft/marketplace/collection       # Get collection
GET    /api/v1/nft/marketplace/assets           # Get assets
GET    /api/v1/nft/marketplace/asset            # Get asset
POST   /api/v1/nft/marketplace/buy              # Buy NFT
POST   /api/v1/nft/marketplace/sell             # Sell NFT
POST   /api/v1/nft/marketplace/auction/bid      # Place bid
POST   /api/v1/nft/marketplace/auction/create   # Create auction
```

#### MINTING
```
POST   /api/v1/nft/mint                         # Mint NFT
POST   /api/v1/nft/mint/batch                   # Batch mint
POST   /api/v1/nft/mint/collection              # Create collection
GET    /api/v1/nft/mint/history                 # Get mint history
```

---

### 🏢 INSTITUTIONAL APIS

#### PRIME BROKERAGE
```
GET    /api/v1/institutional/account            # Get account info
POST   /api/v1/institutional/order              # Place institutional order
GET    /api/v1/institutional/orders             # Get orders
GET    /api/v1/institutional/positions          # Get positions
GET    /api/v1/institutional/balances           # Get balances
```

#### OTC DESK
```
POST   /api/v1/otc/quote                        # Request OTC quote
POST   /api/v1/otc/order                        # Place OTC order
GET    /api/v1/otc/orders                       # Get OTC orders
GET    /api/v1/otc/history                      # Get OTC history
```

---

### 🔐 WALLET APIS

#### WALLET MANAGEMENT
```
GET    /api/v1/wallet/deposit/address           # Get deposit address
POST   /api/v1/wallet/withdraw                  # Withdraw
GET    /api/v1/wallet/withdraw/history          # Get withdraw history
GET    /api/v1/wallet/deposit/history           # Get deposit history
POST   /api/v1/wallet/transfer                  # Internal transfer
GET    /api/v1/wallet/balance                   # Get balance
```

---

### 📊 ANALYTICS APIS

#### MARKET DATA
```
GET    /api/v1/market/ticker/24hr              # 24hr ticker
GET    /api/v1/market/ticker/price             # Price ticker
GET    /api/v1/market/depth                    # Order book
GET    /api/v1/market/trades                   # Recent trades
GET    /api/v1/market/klines                   # Kline data
GET    /api/v1/market/historical-trades        # Historical trades
```

#### USER ANALYTICS
```
GET    /api/v1/analytics/portfolio             # Portfolio analytics
GET    /api/v1/analytics/performance           # Performance metrics
GET    /api/v1/analytics/risk                  # Risk metrics
GET    /api/v1/analytics/trading-history       # Trading history
```

---

### 🛡️ SECURITY APIS

#### SECURITY MANAGEMENT
```
POST   /api/v1/security/2fa/enable             # Enable 2FA
POST   /api/v1/security/2fa/disable            # Disable 2FA
POST   /api/v1/security/whitelist/ip           # Add IP whitelist
DELETE /api/v1/security/whitelist/ip           # Remove IP whitelist
GET    /api/v1/security/whitelist/ip           # Get IP whitelist
POST   /api/v1/security/whitelist/address      # Add address whitelist
DELETE /api/v1/security/whitelist/address      # Remove address whitelist
GET    /api/v1/security/whitelist/address      # Get address whitelist
```

---

### 🌐 WEB3 APIS

#### DEFI INTEGRATION
```
GET    /api/v1/web3/protocols                  # Get DeFi protocols
POST   /api/v1/web3/stake                      # Stake in DeFi
POST   /api/v1/web3/unstake                    # Unstake from DeFi
GET    /api/v1/web3/position                   # Get DeFi position
```

#### CROSS-CHAIN BRIDGE
```
GET    /api/v1/bridge/networks                 # Get supported networks
POST   /api/v1/bridge/transfer                 # Bridge transfer
GET    /api/v1/bridge/history                  # Bridge history
```

---

### 📱 MOBILE APIS

#### PUSH NOTIFICATIONS
```
POST   /api/v1/mobile/push/register            # Register push token
POST   /api/v1/mobile/push/unregister          # Unregister push token
GET    /api/v1/mobile/push/settings            # Get push settings
POST   /api/v1/mobile/push/settings            # Update push settings
```

#### BIOMETRIC AUTH
```
POST   /api/v1/mobile/biometric/enroll         # Enroll biometric
POST   /api/v1/mobile/biometric/verify         # Verify biometric
POST   /api/v1/mobile/biometric/disable        # Disable biometric
```

---

### 🎯 ADMIN APIS

#### USER MANAGEMENT
```
GET    /api/v1/admin/users                     # Get all users
GET    /api/v1/admin/user                      # Get user details
POST   /api/v1/admin/user/suspend              # Suspend user
POST   /api/v1/admin/user/unsuspend            # Unsuspend user
POST   /api/v1/admin/user/kyc/verify           # Verify KYC
POST   /api/v1/admin/user/kyc/reject           # Reject KYC
```

#### SYSTEM MANAGEMENT
```
GET    /api/v1/admin/system/status             # System status
GET    /api/v1/admin/system/metrics            # System metrics
POST   /api/v1/admin/system/maintenance        # Set maintenance mode
POST   /api/v1/admin/system/announcement       # Create announcement
```

---

### 📈 REAL-TIME APIS (WebSocket)

#### MARKET DATA STREAMS
```
wss://stream.tigerex.com/ws/<symbol>@ticker          # Ticker stream
wss://stream.tigerex.com/ws/<symbol>@depth           # Depth stream
wss://stream.tigerex.com/ws/<symbol>@trade           # Trade stream
wss://stream.tigerex.com/ws/<symbol>@kline_<interval> # Kline stream
```

#### USER DATA STREAMS
```
wss://stream.tigerex.com/ws/<listen_key>             # User data stream
```

---

### 🔧 UTILITY APIS

#### SYSTEM STATUS
```
GET    /api/v1/system/status                   # System status
GET    /api/v1/system/ping                     # Ping
GET    /api/v1/system/time                     # Server time
GET    /api/v1/system/exchange-info            # Exchange information
```

#### RATE LIMITS
```
Rate limit: 1200 requests per minute per IP
WebSocket: 5 connections per IP
```

---

### 📊 ERROR CODES

| Code | Description |
|------|-------------|
| -1000 | UNKNOWN |
| -1001 | DISCONNECTED |
| -1002 | UNAUTHORIZED |
| -1003 | TOO_MANY_REQUESTS |
| -1004 | UNEXPECTED_RESP |
| -1005 | TIMEOUT |
| -1006 | ERROR_MSG_RECEIVED |
| -1007 | PERIOD_INVALID |
| -1013 | INVALID_MESSAGE |
| -1014 | UNKNOWN_ORDER_COMPOSITION |
| -1015 | TOO_MANY_ORDERS |
| -1016 | SERVICE_SHUTTING_DOWN |
| -1020 | UNSUPPORTED_OPERATION |
| -1021 | INVALID_TIMESTAMP |
| -1022 | INVALID_SIGNATURE |
| -1100 | ILLEGAL_CHARS |
| -1101 | TOO_MANY_PARAMETERS |
| -1102 | MANDATORY_PARAM_EMPTY_OR_MALFORMED |
| -1103 | UNKNOWN_PARAM |
| -1104 | UNREAD_PARAMETERS |
| -1105 | PARAM_EMPTY |
| -1106 | PARAM_NOT_REQUIRED |
| -1111 | BAD_PRECISION |
| -1112 | NO_DEPTH |
| -1114 | TIF_NOT_REQUIRED |
| -1115 | INVALID_TIF |
| -1116 | INVALID_ORDER_TYPE |
| -1117 | INVALID_SIDE |
| -1118 | EMPTY_NEW_CL_ORD_ID |
| -1119 | EMPTY_CL_ORD_ID |
| -1120 | BAD_INTERVAL |
| -1121 | BAD_SYMBOL |
| -1125 | INVALID_LISTEN_KEY |
| -1127 | MORE_THAN_XX_HOURS |
| -1128 | OPTIONAL_PARAMS_BAD_COMBO |
| -1130 | INVALID_PARAMETER |
| -2010 | NEW_ORDER_REJECTED |
| -2011 | CANCEL_REJECTED |
| -2013 | NO_SUCH_ORDER |
| -2014 | BAD_API_KEY_FMT |
| -2015 | REJECTED_MBX_KEY |

---

### 🚀 QUICK START

1. **Get API Key**: Visit https://tigerex.com/api
2. **Test Connection**: Use `/api/v1/system/ping`
3. **Get Market Data**: Use `/api/v1/spot/ticker/24hr`
4. **Place Order**: Use `/api/v1/spot/order`
5. **WebSocket**: Connect to `wss://stream.tigerex.com/ws`

---

### 📞 SUPPORT
- **API Documentation**: https://tigerex.com/docs/api
- **Support Email**: api-support@tigerex.com
- **Discord**: https://discord.gg/tigerex
- **Telegram**: https://t.me/tigerex_api