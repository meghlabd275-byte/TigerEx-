# TigerEx Multi-Language Microservices

This directory contains implementations of TigerEx exchange components in multiple programming languages as requested. Each service is designed to work independently or as part of the larger microservices architecture.

## Services Overview

### 🟢 Go Trading Engine (`go-trading-engine`)
High-performance trading engine written in Go with the following features:
- Order book management with price-time priority
- Multiple order types (Limit, Market, IOC, FOK, Post-Only)
- Real-time WebSocket updates
- Fee tier integration
- Exchange status control (active/paused/halted/maintenance)
- PostgreSQL and Redis integration

**Port:** 8080

**Build & Run:**
```bash
cd go-trading-engine
go mod download
go run main.go
```

### 🦀 Rust Order Matching (`rust-order-matching`)
Ultra-high performance order matching engine written in Rust:
- Lock-free data structures for maximum throughput
- BTreeMap-based order book for O(log n) operations
- Actix-web HTTP server
- Decimal precision for financial calculations
- Multi-order type support

**Port:** 8081

**Build & Run:**
```bash
cd rust-order-matching
cargo build --release
cargo run --release
```

### 📘 Node.js API Gateway (`nodejs-api-gateway`)
TypeScript-based API gateway with comprehensive features:
- Service discovery and routing
- JWT authentication middleware
- Tier-based rate limiting
- WebSocket server for real-time data
- Redis-based session management
- Exchange status control
- White-label support

**Port:** 3000

**Build & Run:**
```bash
cd nodejs-api-gateway
npm install
npm run build
npm start
```

### ⚡ C++ Matching Engine (`cpp-matching-engine`)
Maximum performance matching engine in C++20:
- Custom fixed-point decimal arithmetic
- B-tree based order book
- Lock-free concurrent data structures
- HTTP REST API with cpp-httplib
- Sub-microsecond matching latency

**Port:** 8082

**Build & Run:**
```bash
cd cpp-matching-engine
mkdir build && cd build
cmake ..
make -j$(nproc)
./tigerex_matching
```

### ☕ Java Queue Service (`java-queue-service`)
Enterprise-grade message queue service:
- NATS message broker integration
- Redis persistence layer
- Multiple message types (orders, trades, notifications, etc.)
- Dead letter queue handling
- Automatic retry with exponential backoff
- Message priority support

**Build & Run:**
```bash
cd java-queue-service
mvn clean package
java -jar target/queue-service-1.0.0.jar
```

### ⚛️ TypeScript Admin Panel (`typescript-admin-panel`)
Modern Next.js admin dashboard:
- Real-time analytics and charts
- User management with role-based access
- Fee tier configuration
- Exchange status control
- White-label management
- Responsive design with Tailwind CSS

**Port:** 3001

**Build & Run:**
```bash
cd typescript-admin-panel
npm install
npm run dev
```

### ⛓️ Solidity Smart Contracts (`solidity-smart-contracts`)
DeFi smart contracts for blockchain integration:
- **TigerExToken (TGX)**: Governance token with mint/burn
- **TigerExDEX**: AMM-based decentralized exchange
- **TigerExStaking**: Tiered staking rewards
- **TigerExGovernance**: DAO voting and proposals

**Compile & Deploy:**
```bash
cd solidity-smart-contracts
npm install
npx hardhat compile
npx hardhat run scripts/deploy.ts
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (Node.js)                    │
│                    Port 3000 - JWT/RBAC                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
    ▼                 ▼                 ▼
┌───────────┐  ┌───────────┐  ┌───────────────┐
│  Go       │  │  Rust     │  │  C++          │
│  Trading  │  │  Order    │  │  Matching     │
│  Engine   │  │  Matching │  │  Engine       │
│  :8080    │  │  :8081    │  │  :8082        │
└─────┬─────┘  └─────┬─────┘  └───────┬───────┘
      │              │                │
      └──────────────┼────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌─────────┐  ┌────────────┐  ┌─────────────┐
│ Redis   │  │ PostgreSQL │  │ NATS        │
│ Cache   │  │ Database   │  │ Message Bus │
└─────────┘  └────────────┘  └─────────────┘
                     │
                     ▼
           ┌─────────────────┐
           │  Java Queue     │
           │  Service        │
           │  Event Processing│
           └─────────────────┘
```

## Environment Variables

All services support these common environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `EXCHANGE_ID` | Unique exchange identifier | `TIGEREX-MAIN` |
| `PORT` | Service port | Service-specific |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://localhost/tigerex` |
| `JWT_SECRET` | JWT signing secret | - |
| `NATS_URL` | NATS server URL | `nats://localhost:4222` |

## Exchange Status Control

All trading services support the following exchange states:
- **active**: Normal trading operations
- **paused**: Trading paused, orders preserved
- **halted**: Emergency stop, all operations suspended
- **maintenance**: Scheduled maintenance mode

## White-Label Support

The platform supports white-label deployments:
1. Each exchange gets a unique `exchange_id`
2. Parent exchange can manage child exchanges
3. Custom branding and domain support
4. Isolated user bases per exchange

## Technology Stack Summary

| Language | Service | Purpose |
|----------|---------|---------|
| **Go** | Trading Engine | High-concurrency order processing |
| **Rust** | Order Matching | Ultra-low latency matching |
| **C++** | Matching Engine | Maximum performance critical path |
| **TypeScript/Node.js** | API Gateway | Routing, authentication, rate limiting |
| **Java** | Queue Service | Enterprise messaging and events |
| **TypeScript/Next.js** | Admin Panel | Web-based administration |
| **Solidity** | Smart Contracts | DeFi and blockchain integration |

## License

Copyright © 2024 TigerEx. All rights reserved.