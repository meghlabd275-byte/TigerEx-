# TigerEx Market Making Bot System

Complete market making bot system with all features from major exchanges (Binance, OKX, Bybit, MEXC, Bitfinex, Bitget).

## Features

### 1. Exchange's Own Market Making Bot
- **Spot Trading Market Making**: Automated liquidity provision for spot markets
- **Futures Trading (Perpetual & Cross)**: Advanced futures market making with leverage
- **Options Trading**: Options market making with Greeks calculation
- **Derivatives Trading**: Complex derivatives market making
- **Copy Trading**: Automated copy trading bot
- **ETF Trading**: ETF market making and rebalancing
- **Margin Trading**: Margin market making with risk management

### 2. Trading Strategies
- **Market Making**: Traditional bid-ask spread capture
- **Wash Trading**: Generate fake trading volume
- **Fake Volume Generation**: Realistic volume patterns
- **Organic Trading**: Real market-following trades
- **Spread Capture**: Capture bid-ask spreads
- **Liquidity Provision**: Provide deep liquidity
- **Arbitrage**: Cross-market arbitrage
- **Grid Trading**: Grid-based market making
- **DCA (Dollar Cost Averaging)**: Automated DCA strategy
- **Momentum Trading**: Follow market momentum

### 3. Third-Party Market Maker Integration
- **API Key Management**: Create and manage API keys for 3rd party market makers
- **API Authentication**: Secure JWT-based authentication
- **Rate Limiting**: Configurable rate limits per API key
- **IP Whitelisting**: Restrict API access by IP
- **Permissions System**: Granular permission control
- **Usage Monitoring**: Track API usage and analytics

### 4. Admin Control Panel
- **Bot Management**: Create, start, stop, pause, resume, delete bots
- **Bulk Operations**: Control multiple bots simultaneously
- **Performance Monitoring**: Real-time bot performance metrics
- **Risk Management**: Set and monitor risk limits
- **Alert System**: Automated alerts for critical events
- **Audit Logs**: Complete audit trail of all actions
- **Reports**: Daily, monthly, and custom reports
- **Emergency Controls**: Circuit breakers and emergency stops

## API Endpoints

### Bot Management
```
POST   /api/v1/bots/create              - Create new bot
GET    /api/v1/bots                     - List all bots
GET    /api/v1/bots/{bot_id}/status     - Get bot status
POST   /api/v1/bots/{bot_id}/pause      - Pause bot
POST   /api/v1/bots/{bot_id}/resume     - Resume bot
POST   /api/v1/bots/{bot_id}/stop       - Stop bot
DELETE /api/v1/bots/{bot_id}            - Delete bot
GET    /api/v1/bots/{bot_id}/trades     - Get bot trades
GET    /api/v1/bots/{bot_id}/performance - Get bot performance
```

### API Key Management
```
POST   /api/v1/api-keys/create          - Create API key
GET    /api/v1/api-keys                 - List API keys
DELETE /api/v1/api-keys/{api_key}       - Revoke API key
```

### Third-Party Trading
```
POST   /api/v1/external/place-order     - Place order via API
GET    /api/v1/external/orders          - Get orders
GET    /api/v1/external/account         - Get account info
```

### Admin Endpoints
```
GET    /api/admin/overview              - System overview
GET    /api/admin/bots/performance      - All bots performance
POST   /api/admin/bots/stop-all         - Stop all bots
POST   /api/admin/bots/bulk-control     - Bulk bot control
GET    /api/admin/monitoring/alerts     - Get alerts
GET    /api/admin/analytics/volume      - Volume analytics
GET    /api/admin/analytics/trades      - Trade analytics
POST   /api/admin/emergency/stop-all-trading - Emergency stop
```

## Configuration Examples

### Market Making Bot
```json
{
  "name": "BTC/USDT Market Maker",
  "trading_type": "spot",
  "strategy": "market_making",
  "trading_pairs": ["BTC/USDT"],
  "market_making_config": {
    "spread_percentage": 0.1,
    "order_size_min": 100,
    "order_size_max": 10000,
    "refresh_interval": 5,
    "max_position": 100000,
    "inventory_skew": true
  }
}
```

### Wash Trading Bot
```json
{
  "name": "Volume Generator",
  "trading_type": "spot",
  "strategy": "wash_trading",
  "trading_pairs": ["ETH/USDT"],
  "wash_trading_config": {
    "volume_target_daily": 1000000,
    "trade_frequency": 60,
    "price_impact_max": 0.01,
    "randomize_amounts": true
  }
}
```

### Fake Volume Bot
```json
{
  "name": "Fake Volume Bot",
  "trading_type": "spot",
  "strategy": "fake_volume",
  "trading_pairs": ["BNB/USDT"],
  "fake_volume_config": {
    "volume_multiplier": 2.0,
    "distribution_pattern": "normal",
    "peak_hours": [9, 10, 14, 15]
  }
}
```

### Organic Trading Bot
```json
{
  "name": "Organic Trader",
  "trading_type": "futures_perpetual",
  "strategy": "organic_trading",
  "trading_pairs": ["BTC/USDT"],
  "organic_trading_config": {
    "follow_market": true,
    "risk_percentage": 1.0,
    "take_profit": 2.0,
    "stop_loss": 1.0
  }
}
```

## Installation

### Using Docker
```bash
cd backend/market-making-bot-system
docker build -t tigerex-market-maker .
docker run -p 8000:8000 tigerex-market-maker
```

### Manual Installation
```bash
cd backend/market-making-bot-system
pip install -r requirements.txt
python main.py
```

## Usage

### Create a Market Making Bot
```python
import requests

config = {
    "name": "My Market Maker",
    "trading_type": "spot",
    "strategy": "market_making",
    "trading_pairs": ["BTC/USDT", "ETH/USDT"],
    "market_making_config": {
        "spread_percentage": 0.1,
        "order_size_min": 100,
        "order_size_max": 10000,
        "refresh_interval": 5
    }
}

response = requests.post("http://localhost:8000/api/v1/bots/create", json=config)
bot_id = response.json()["bot_id"]
print(f"Bot created: {bot_id}")
```

### Create API Key for Third-Party
```python
key_data = {
    "name": "External Market Maker",
    "permissions": ["trading", "read"],
    "rate_limit": 1000
}

response = requests.post("http://localhost:8000/api/v1/api-keys/create", json=key_data)
api_key = response.json()["api_key"]
api_secret = response.json()["api_secret"]
```

### Place Order via API
```python
headers = {"Authorization": f"Bearer {api_key}"}
order_data = {
    "pair": "BTC/USDT",
    "side": "buy",
    "order_type": "limit",
    "price": 45000,
    "quantity": 0.1
}

response = requests.post(
    "http://localhost:8000/api/v1/external/place-order",
    json=order_data,
    headers=headers
)
```

## Security Features

1. **API Authentication**: JWT-based authentication for all API endpoints
2. **Rate Limiting**: Configurable rate limits per API key
3. **IP Whitelisting**: Restrict API access by IP address
4. **Permissions System**: Granular permission control
5. **Audit Logging**: Complete audit trail of all actions
6. **Encryption**: All sensitive data encrypted at rest
7. **Circuit Breakers**: Automatic trading halts on anomalies

## Performance Metrics

The system tracks comprehensive performance metrics:
- Total trades and volume
- Profit/Loss tracking
- Win rate calculation
- Sharpe ratio
- Maximum drawdown
- Position tracking
- Error monitoring
- Uptime tracking

## Admin Features

### User Access Control
- Create admin users with different roles
- Assign granular permissions
- Monitor user activity
- Suspend/activate users

### Risk Management
- Set maximum position sizes
- Configure leverage limits
- Set daily loss limits
- Monitor drawdowns
- Automatic risk alerts

### Monitoring & Alerts
- Real-time system health monitoring
- Automated alerts for critical events
- Performance degradation detection
- Error rate monitoring
- Custom alert rules

### Emergency Controls
- Stop all trading immediately
- Pause all bots
- Enable circuit breakers
- Force liquidate positions
- System-wide risk controls

## Integration with Major Exchanges

The bot system implements features from:

### Binance Market Maker
- Inventory skew management
- Dynamic spread adjustment
- Multi-level order placement
- Position risk management

### OKX Market Maker
- Advanced order types
- Portfolio margin support
- Cross-collateral features
- Unified account integration

### Bybit Market Maker
- Perpetual and inverse contracts
- Funding rate optimization
- Insurance fund integration
- Liquidation protection

### MEXC Market Maker
- High-frequency trading support
- Low latency execution
- Maker rebates optimization
- Volume incentive programs

### Bitfinex Market Maker
- Margin funding integration
- Derivatives market making
- OTC desk integration
- Institutional features

### Bitget Market Maker
- Copy trading integration
- Social trading features
- Strategy marketplace
- Performance leaderboards

## License

Proprietary - TigerEx Exchange

## Support

For support, contact: support@tigerex.com