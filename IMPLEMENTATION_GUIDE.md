# TigerEx - New Features Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing the 87 new features identified in the exchange API analysis. The implementation is organized into 6 phases over 24 weeks.

---

## Phase 1: Core Trading Enhancements (Weeks 1-4)

### 1.1 Convert Service Enhancement

**Status:** Service exists but needs enhancement with quote system

**Current Location:** `backend/convert-service/`

**Required Enhancements:**

1. **Add Quote System**
   - Implement quote generation with time-limited validity
   - Add quote storage in database
   - Implement quote validation before execution

2. **Add Price Feed Integration**
   - Connect to market data service for real-time prices
   - Implement price aggregation from multiple sources
   - Add price slippage protection

3. **Database Schema Updates**
```sql
-- Add to convert service database
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
    INDEX idx_status (status)
);
```

4. **API Endpoints to Add**
   - `POST /api/v1/convert/quote` - Request quote
   - `POST /api/v1/convert/execute` - Execute quote
   - `GET /api/v1/convert/status/{id}` - Get conversion status

**Implementation Steps:**

```bash
# 1. Update database schema
cd backend/convert-service
psql -U tigerex -d tigerex_convert < schema_updates.sql

# 2. Update requirements.txt
echo "python-decimal==1.0.0" >> requirements.txt

# 3. Implement quote engine
# Edit src/quote_engine.py

# 4. Update main.py with new endpoints
# Edit src/main.py

# 5. Add tests
# Create tests/test_quote_system.py

# 6. Deploy
docker-compose up -d convert-service
```

---

### 1.2 RPI Orders Implementation

**Status:** New feature - needs full implementation

**Location:** Create `backend/rpi-order-service/`

**Architecture:**

```
backend/rpi-order-service/
├── src/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Data models
│   ├── rpi_engine.py        # RPI calculation engine
│   ├── order_processor.py   # Order processing
│   └── price_improvement.py # Price improvement logic
├── admin/
│   ├── __init__.py
│   └── admin_routes.py      # Admin controls
├── tests/
│   └── test_rpi.py
├── Dockerfile
└── requirements.txt
```

**Database Schema:**

```sql
CREATE DATABASE tigerex_rpi;

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

CREATE TABLE rpi_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    total_orders INTEGER DEFAULT 0,
    total_improvement DECIMAL(36, 18) DEFAULT 0,
    avg_improvement_pct DECIMAL(10, 6) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, symbol)
);
```

**Implementation Steps:**

```bash
# 1. Create service directory
mkdir -p backend/rpi-order-service/{src,admin,tests}

# 2. Create database
psql -U tigerex -c "CREATE DATABASE tigerex_rpi;"

# 3. Create schema
psql -U tigerex -d tigerex_rpi < rpi_schema.sql

# 4. Create requirements.txt
cat > backend/rpi-order-service/requirements.txt << EOF
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
python-decimal==1.0.0
EOF

# 5. Implement service (see code template below)

# 6. Add to docker-compose.yml
# 7. Deploy
docker-compose up -d rpi-order-service
```

**Key Implementation Points:**

1. **RPI Calculation Logic:**
```python
def calculate_rpi_price(market_price: Decimal, side: str, liquidity: Decimal) -> Decimal:
    """
    Calculate RPI price with improvement
    
    Args:
        market_price: Current market price
        side: 'buy' or 'sell'
        liquidity: Available liquidity
    
    Returns:
        Improved price
    """
    # Base improvement: 0.01% - 0.05% depending on liquidity
    improvement_rate = min(Decimal("0.0005"), liquidity / Decimal("1000000"))
    
    if side == "buy":
        # Better price = lower price for buyers
        return market_price * (Decimal("1") - improvement_rate)
    else:
        # Better price = higher price for sellers
        return market_price * (Decimal("1") + improvement_rate)
```

2. **Order Processing:**
```python
async def process_rpi_order(order: RPIOrder) -> RPIExecution:
    """Process RPI order with price improvement"""
    
    # 1. Get current market price
    market_price = await get_market_price(order.symbol)
    
    # 2. Calculate RPI price
    rpi_price = calculate_rpi_price(
        market_price, 
        order.side, 
        order.quantity
    )
    
    # 3. Execute at improved price
    execution = await execute_order(
        order.symbol,
        order.side,
        order.quantity,
        rpi_price
    )
    
    # 4. Record improvement
    improvement = abs(rpi_price - market_price)
    improvement_pct = (improvement / market_price) * 100
    
    return RPIExecution(
        order_id=order.order_id,
        executed_price=rpi_price,
        market_price=market_price,
        improvement=improvement,
        improvement_percentage=improvement_pct
    )
```

---

### 1.3 Smart Order Routing (SOR)

**Status:** New feature - needs full implementation

**Location:** Create `backend/sor-service/`

**Architecture:**

```
backend/sor-service/
├── src/
│   ├── main.py              # FastAPI application
│   ├── router.py            # Order routing logic
│   ├── venue_manager.py     # Venue management
│   ├── execution_algo.py    # Execution algorithms
│   ├── analytics.py         # SOR analytics
│   └── models.py            # Data models
├── admin/
│   ├── __init__.py
│   └── admin_routes.py
├── tests/
│   └── test_sor.py
├── Dockerfile
└── requirements.txt
```

**Key Features:**

1. **Venue Management:**
   - Track multiple execution venues
   - Monitor venue liquidity
   - Calculate venue costs (fees, slippage)

2. **Routing Logic:**
   - Analyze order size vs. venue liquidity
   - Calculate optimal split across venues
   - Minimize total execution cost

3. **Execution Algorithms:**
   - VWAP (Volume Weighted Average Price)
   - TWAP (Time Weighted Average Price)
   - Implementation Shortfall
   - Arrival Price

**Implementation Priority:** High (Week 2-3)

---

### 1.4 Atomic Cancel-Replace

**Status:** Enhancement to existing order service

**Location:** `backend/advanced-trading-service/`

**Implementation:**

Add new endpoint to existing trading service:

```python
@app.post("/api/v1/order/cancel-replace")
async def atomic_cancel_replace(
    cancel_order_id: str,
    new_order: OrderRequest,
    db: Session = Depends(get_db)
):
    """
    Atomically cancel an order and place a new one
    
    This ensures no gap between cancel and new order placement
    """
    async with db.begin():
        # 1. Validate original order exists and is cancelable
        original_order = await get_order(cancel_order_id)
        if not original_order or original_order.status not in ["open", "partial"]:
            raise HTTPException(400, "Order cannot be cancelled")
        
        # 2. Cancel original order
        await cancel_order_internal(cancel_order_id)
        
        # 3. Place new order
        new_order_result = await place_order_internal(new_order)
        
        # 4. If new order fails, rollback cancel
        if not new_order_result.success:
            raise HTTPException(500, "Failed to place new order")
        
        return {
            "cancelledOrderId": cancel_order_id,
            "newOrderId": new_order_result.order_id,
            "status": "success"
        }
```

**Implementation Priority:** Medium (Week 3)

---

## Phase 2: Lending & Earn (Weeks 5-8)

### 2.1 New Crypto Loan System

**Status:** New feature - needs full implementation

**Location:** Create `backend/crypto-loan-service/`

**Architecture:**

```
backend/crypto-loan-service/
├── src/
│   ├── main.py                  # FastAPI application
│   ├── fixed_loan.py           # Fixed-term loans
│   ├── flexible_loan.py        # Flexible loans
│   ├── collateral_manager.py   # Collateral management
│   ├── interest_calculator.py  # Interest calculation
│   ├── repayment_engine.py     # Repayment processing
│   ├── liquidation_engine.py   # Liquidation logic
│   └── models.py               # Data models
├── admin/
│   ├── __init__.py
│   └── admin_routes.py
├── tests/
│   └── test_loans.py
├── Dockerfile
└── requirements.txt
```

**Database Schema:**

```sql
CREATE DATABASE tigerex_crypto_loan;

-- Loan Products
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
    created_at TIMESTAMP DEFAULT NOW()
);

-- Loan Orders
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
    outstanding_amount DECIMAL(36, 18) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (product_id) REFERENCES loan_products(product_id)
);

-- Repayment History
CREATE TABLE loan_repayments (
    id SERIAL PRIMARY KEY,
    repayment_id VARCHAR(50) UNIQUE NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    user_id INTEGER NOT NULL,
    repay_amount DECIMAL(36, 18) NOT NULL,
    interest_amount DECIMAL(36, 18) NOT NULL,
    repay_type VARCHAR(20) NOT NULL,
    repaid_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (order_id) REFERENCES loan_orders(order_id)
);

-- Collateral Tracking
CREATE TABLE collateral_positions (
    id SERIAL PRIMARY KEY,
    position_id VARCHAR(50) UNIQUE NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    user_id INTEGER NOT NULL,
    collateral_coin VARCHAR(20) NOT NULL,
    collateral_amount DECIMAL(36, 18) NOT NULL,
    locked_amount DECIMAL(36, 18) NOT NULL,
    current_value_usd DECIMAL(36, 18) NOT NULL,
    ltv_ratio DECIMAL(10, 6) NOT NULL,
    liquidation_price DECIMAL(36, 18) NOT NULL,
    status VARCHAR(20) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (order_id) REFERENCES loan_orders(order_id)
);
```

**Key Features:**

1. **Fixed-Term Loans:**
   - 7, 14, 30, 60, 90, 180 day terms
   - Fixed interest rate
   - Locked collateral
   - Early repayment with penalty

2. **Flexible Loans:**
   - No fixed term
   - Variable interest rate (daily)
   - Flexible collateral
   - Repay anytime without penalty

3. **Interest Calculation:**
```python
def calculate_interest(
    principal: Decimal,
    rate: Decimal,
    days: int,
    compound: bool = True
) -> Decimal:
    """Calculate loan interest"""
    if compound:
        # Compound daily
        daily_rate = rate / Decimal("365")
        return principal * ((Decimal("1") + daily_rate) ** days - Decimal("1"))
    else:
        # Simple interest
        return principal * rate * Decimal(days) / Decimal("365")
```

4. **Liquidation Logic:**
```python
async def check_liquidation(position: CollateralPosition):
    """Check if position needs liquidation"""
    
    # Get current collateral value
    current_value = await get_collateral_value(
        position.collateral_coin,
        position.collateral_amount
    )
    
    # Get loan value
    loan_value = await get_loan_value(position.order_id)
    
    # Calculate current LTV
    current_ltv = loan_value / current_value
    
    # Check liquidation threshold
    if current_ltv >= position.liquidation_ratio:
        await liquidate_position(position)
```

**API Endpoints:**

```
POST   /api/v1/loan/products              - Get loan products
POST   /api/v1/loan/fixed/borrow          - Create fixed loan
POST   /api/v1/loan/flexible/borrow       - Create flexible loan
POST   /api/v1/loan/repay                 - Repay loan
POST   /api/v1/loan/repay-collateral      - Repay with collateral
GET    /api/v1/loan/orders                - Get loan orders
GET    /api/v1/loan/history               - Get loan history
GET    /api/v1/loan/collateral            - Get collateral positions
POST   /api/v1/loan/adjust-collateral     - Adjust collateral
```

**Implementation Priority:** High (Week 5-7)

---

### 2.2 Earn Products Service

**Status:** Partial - needs enhancement

**Location:** Enhance existing staking services

**Required Enhancements:**

1. **Unified Earn Interface:**
   - Combine all earn products under one API
   - Flexible savings
   - Fixed savings
   - Staking
   - Liquidity mining

2. **Product Catalog:**
```python
class EarnProduct(BaseModel):
    product_id: str
    category: str  # 'flexible', 'fixed', 'staking', 'liquidity'
    coin: str
    apy: Decimal
    min_amount: Decimal
    max_amount: Decimal
    lock_period: Optional[int]  # days, None for flexible
    early_redemption: bool
    auto_compound: bool
```

3. **Position Tracking:**
   - Track all earn positions
   - Calculate rewards
   - Auto-compound if enabled
   - Redemption management

**Implementation Priority:** Medium (Week 7-8)

---

## Phase 3: Advanced Trading (Weeks 9-12)

### 3.1 Spread Trading Service

**Status:** New feature

**Location:** Create `backend/spread-trading-service/`

**Key Features:**

1. **Spread Instruments:**
   - Calendar spreads
   - Inter-commodity spreads
   - Intra-commodity spreads

2. **Spread Order Management:**
   - Create spread orders
   - Manage spread positions
   - Calculate spread P&L

**Implementation Priority:** Medium (Week 9-10)

---

### 3.2 RFQ (Request for Quote) System

**Status:** New feature

**Location:** Create `backend/rfq-service/`

**Key Features:**

1. **Quote Requests:**
   - Create RFQ for large orders
   - Broadcast to market makers
   - Collect quotes

2. **Quote Management:**
   - Compare quotes
   - Select best quote
   - Execute trade

**Implementation Priority:** Medium (Week 11-12)

---

## Phase 4: Market Data & Analytics (Weeks 13-16)

### 4.1 Insurance Pool Tracking

**Location:** Enhance `backend/insurance-fund-service/`

**Enhancements:**

1. Real-time balance updates (every 1 minute)
2. WebSocket streaming
3. Historical data
4. Pool analytics

**Implementation Priority:** Low (Week 13)

---

### 4.2 ADL Alert System

**Location:** Create `backend/adl-alert-service/`

**Features:**

1. Monitor ADL queue positions
2. Send alerts to users
3. Track ADL events
4. Provide risk indicators

**Implementation Priority:** Low (Week 14)

---

### 4.3 Long/Short Ratio Service

**Location:** Create `backend/market-sentiment-service/`

**Features:**

1. Calculate long/short ratios
2. Track sentiment trends
3. Provide historical data
4. Visualization support

**Implementation Priority:** Low (Week 15)

---

## Phase 5: Account Features (Weeks 17-20)

### 5.1 Position Movement Service

**Location:** Create `backend/position-transfer-service/`

**Features:**

1. Transfer positions between accounts
2. Validate transfers
3. Track transfer history
4. Handle margin requirements

**Implementation Priority:** Medium (Week 17-18)

---

### 5.2 Spot Hedging

**Location:** Enhance `backend/portfolio-margin-service/`

**Features:**

1. Enable/disable spot hedging
2. Calculate hedge ratios
3. Track hedged positions
4. Risk reduction metrics

**Implementation Priority:** Medium (Week 19)

---

## Phase 6: System Enhancements (Weeks 21-24)

### 6.1 Rate Limit Management

**Location:** Enhance `backend/api-gateway/`

**Features:**

1. Dynamic rate limits per user
2. Custom limit configuration
3. Limit monitoring
4. Auto-adjustment based on tier

**Implementation Priority:** Low (Week 21)

---

### 6.2 System Status Service

**Location:** Create `backend/system-status-service/`

**Features:**

1. Real-time system health
2. Component monitoring
3. Maintenance alerts
4. Status history

**Implementation Priority:** Low (Week 22)

---

## Testing Strategy

### Unit Tests

For each service:

```bash
# Run unit tests
cd backend/<service-name>
pytest tests/ -v --cov=src --cov-report=html
```

### Integration Tests

```bash
# Run integration tests
cd tests/integration
pytest test_convert_flow.py -v
pytest test_loan_flow.py -v
pytest test_rpi_flow.py -v
```

### Load Tests

```bash
# Run load tests
cd tests/load
locust -f test_convert_load.py --host=http://localhost:8200
```

---

## Deployment Checklist

For each new service:

- [ ] Database schema created
- [ ] Service code implemented
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] API documentation updated
- [ ] Admin controls implemented
- [ ] Monitoring configured
- [ ] Logging configured
- [ ] Docker image built
- [ ] Added to docker-compose.yml
- [ ] Environment variables configured
- [ ] Deployed to staging
- [ ] Staging tests passed
- [ ] Deployed to production
- [ ] Production smoke tests passed
- [ ] User documentation updated

---

## Monitoring & Alerts

### Key Metrics to Monitor

1. **Convert Service:**
   - Quote generation time
   - Execution success rate
   - Daily conversion volume
   - Price slippage

2. **Crypto Loan:**
   - Total loans outstanding
   - Liquidation events
   - Interest revenue
   - Default rate

3. **RPI Orders:**
   - Average price improvement
   - RPI execution rate
   - User adoption

### Alert Thresholds

```yaml
alerts:
  convert_service:
    - metric: quote_generation_time
      threshold: 100ms
      severity: warning
    - metric: execution_failure_rate
      threshold: 1%
      severity: critical
  
  crypto_loan:
    - metric: liquidation_rate
      threshold: 5%
      severity: warning
    - metric: default_rate
      threshold: 1%
      severity: critical
  
  rpi_orders:
    - metric: execution_failure_rate
      threshold: 2%
      severity: warning
```

---

## Documentation Updates

### API Documentation

Update Swagger/OpenAPI specs for:
- All new endpoints
- Request/response models
- Error codes
- Rate limits

### User Documentation

Create guides for:
- How to use Convert service
- How to borrow with Crypto Loan
- How to use RPI orders
- How to use Spread Trading
- How to use RFQ system

### Developer Documentation

Update:
- Architecture diagrams
- Service dependencies
- Database schemas
- Deployment procedures

---

## Success Criteria

### Phase 1 Success Criteria

- [ ] Convert service with quote system operational
- [ ] RPI orders processing with >0.01% average improvement
- [ ] SOR routing orders across venues
- [ ] Atomic cancel-replace working

### Phase 2 Success Criteria

- [ ] Crypto loan system accepting loans
- [ ] Interest calculation accurate
- [ ] Liquidation engine operational
- [ ] Earn products integrated

### Overall Success Criteria

- [ ] All 87 features implemented
- [ ] 95%+ API uptime
- [ ] <100ms average response time
- [ ] 90%+ user satisfaction
- [ ] Zero critical security issues
- [ ] Complete documentation

---

## Rollback Procedures

For each service deployment:

1. **Pre-deployment:**
   - Create database backup
   - Tag current production version
   - Document rollback steps

2. **Rollback triggers:**
   - Critical bugs discovered
   - Performance degradation >20%
   - Security vulnerability found
   - User-facing errors >5%

3. **Rollback steps:**
```bash
# 1. Stop new service
docker-compose stop <service-name>

# 2. Restore previous version
docker-compose up -d <service-name>:previous

# 3. Restore database if needed
psql -U tigerex -d <database> < backup.sql

# 4. Verify rollback
curl http://localhost:<port>/health
```

---

## Contact & Support

For implementation questions:
- Technical Lead: [Contact Info]
- DevOps Team: [Contact Info]
- Database Team: [Contact Info]

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-03  
**Status:** Ready for Implementation