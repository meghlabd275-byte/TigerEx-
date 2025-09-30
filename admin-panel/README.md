# TigerEx Admin Panel

Comprehensive admin panel for managing the TigerEx cryptocurrency exchange platform.

## Features

### 1. Financial Reports Dashboard
- **Revenue Analytics**
  - Daily/Weekly/Monthly revenue charts
  - Revenue by trading pair
  - Fee collection breakdown
  - Profit/Loss statements
  - Revenue forecasting

- **Trading Volume Analysis**
  - 24h/7d/30d trading volume
  - Volume by asset
  - Volume trends
  - Market share analysis

- **Fee Reports**
  - Trading fees collected
  - Withdrawal fees
  - Deposit fees
  - Total fee revenue

### 2. System Monitoring Dashboard
- **Server Health**
  - CPU usage
  - Memory usage
  - Disk space
  - Network traffic
  - Uptime monitoring

- **Service Status**
  - All microservices status
  - API response times
  - Database performance
  - Cache hit rates
  - Queue lengths

- **Performance Metrics**
  - Request latency
  - Throughput
  - Error rates
  - Success rates

- **Error Logs**
  - Real-time error tracking
  - Error categorization
  - Stack traces
  - Error frequency

### 3. Compliance Dashboard
- **KYC Verification Queue**
  - Pending verifications
  - Document review
  - Approval/Rejection workflow
  - Verification statistics

- **AML Monitoring**
  - Suspicious activity detection
  - Transaction monitoring
  - Risk scoring
  - Compliance reports

- **Regulatory Reports**
  - Transaction reports
  - User activity reports
  - Compliance metrics
  - Audit logs

### 4. Risk Management Dashboard
- **Position Monitoring**
  - Open positions overview
  - Position sizes
  - Leverage usage
  - Margin levels

- **Liquidation Alerts**
  - At-risk positions
  - Liquidation queue
  - Liquidation history
  - Risk exposure

- **Risk Exposure Analysis**
  - Market risk
  - Credit risk
  - Operational risk
  - Concentration risk

- **Circuit Breaker Controls**
  - Trading halts
  - Price limits
  - Position limits
  - Emergency controls

### 5. Trading Analytics Dashboard
- **Trading Pair Performance**
  - Volume by pair
  - Liquidity metrics
  - Spread analysis
  - Order book depth

- **Order Book Analysis**
  - Bid/Ask spread
  - Order distribution
  - Market depth
  - Imbalance detection

- **Market Maker Activity**
  - MM performance
  - Liquidity provision
  - Spread maintenance
  - Volume contribution

- **Trading Bot Performance**
  - Active bots
  - Bot profitability
  - Strategy performance
  - Risk metrics

### 6. User Analytics Dashboard
- **User Growth Metrics**
  - New registrations
  - Active users
  - User retention
  - Churn rate

- **User Segmentation**
  - By trading volume
  - By account age
  - By verification level
  - By geography

- **Engagement Metrics**
  - Daily active users
  - Session duration
  - Feature usage
  - Trading frequency

- **Retention Analysis**
  - Cohort analysis
  - Retention curves
  - Lifetime value
  - Engagement scores

### 7. Token Listing Dashboard
- **Listing Requests**
  - New token applications
  - Application status
  - Review workflow
  - Approval pipeline

- **Due Diligence**
  - Project evaluation
  - Team verification
  - Smart contract audit
  - Market analysis

- **Listing Management**
  - Active listings
  - Trading pairs
  - Listing fees
  - Delisting process

### 8. Blockchain Deployment Dashboard
- **Smart Contract Deployment**
  - Contract templates
  - Deployment wizard
  - Contract verification
  - Upgrade management

- **Network Status**
  - Blockchain health
  - Node status
  - Sync status
  - Network congestion

- **Gas Price Monitoring**
  - Current gas prices
  - Gas optimization
  - Transaction costs
  - Fee estimation

### 9. White-Label Management Dashboard
- **Partner Management**
  - Partner list
  - Partner onboarding
  - Account management
  - Performance tracking

- **Branding Customization**
  - Logo upload
  - Color schemes
  - Custom domains
  - UI customization

- **Revenue Sharing**
  - Commission rates
  - Revenue distribution
  - Payment schedules
  - Financial reports

- **API Management**
  - API keys
  - Rate limits
  - Usage statistics
  - Documentation

### 10. Affiliate Management Dashboard
- **Affiliate Tracking**
  - Affiliate list
  - Referral links
  - Click tracking
  - Conversion rates

- **Commission Calculation**
  - Commission tiers
  - Revenue tracking
  - Commission rules
  - Bonus programs

- **Payout Management**
  - Pending payouts
  - Payment processing
  - Payment history
  - Payment methods

- **Performance Reports**
  - Top affiliates
  - Conversion metrics
  - Revenue generated
  - ROI analysis

## Tech Stack

- **Framework**: Next.js 14
- **UI Library**: Material-UI (MUI)
- **State Management**: Redux Toolkit
- **Charts**: Recharts, MUI X Charts
- **Data Grid**: MUI X Data Grid
- **Authentication**: NextAuth.js
- **HTTP Client**: Axios
- **Real-time**: Socket.io Client

## Project Structure

```
admin-panel/
├── src/
│   ├── pages/
│   │   ├── index.tsx                    # Main dashboard
│   │   ├── financial-reports.tsx        # Financial dashboard
│   │   ├── system-monitoring.tsx        # System health
│   │   ├── compliance.tsx               # Compliance dashboard
│   │   ├── risk-management.tsx          # Risk dashboard
│   │   ├── trading-analytics.tsx        # Trading analytics
│   │   ├── user-analytics.tsx           # User analytics
│   │   ├── token-listing.tsx            # Token listing
│   │   ├── blockchain-deployment.tsx    # Blockchain tools
│   │   ├── white-label.tsx              # White-label management
│   │   └── affiliate.tsx                # Affiliate management
│   ├── components/
│   │   ├── Layout/
│   │   │   ├── DashboardLayout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Header.tsx
│   │   ├── Dashboard/
│   │   │   ├── StatCard.tsx
│   │   │   ├── RevenueChart.tsx
│   │   │   ├── UserGrowthChart.tsx
│   │   │   └── SystemHealth.tsx
│   │   ├── Financial/
│   │   ├── Compliance/
│   │   ├── Risk/
│   │   ├── Trading/
│   │   ├── Users/
│   │   └── Common/
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── websocket.ts
│   ├── store/
│   │   ├── index.ts
│   │   └── slices/
│   ├── utils/
│   └── styles/
├── public/
├── package.json
└── README.md
```

## Installation

```bash
cd admin-panel
npm install
```

## Running the App

### Development
```bash
npm run dev
```

Access at: http://localhost:3001

### Production Build
```bash
npm run build
npm start
```

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://api.tigerex.com
NEXT_PUBLIC_WS_URL=ws://api.tigerex.com
NEXTAUTH_URL=http://localhost:3001
NEXTAUTH_SECRET=your-secret-key
```

## Authentication

The admin panel uses NextAuth.js for authentication with role-based access control:

- **Super Admin**: Full access to all features
- **Admin**: Access to most features except critical settings
- **Compliance Officer**: Access to compliance and KYC features
- **Support**: Access to user management and support features
- **Analyst**: Read-only access to analytics and reports

## Key Features

### Real-time Updates
- WebSocket connections for live data
- Auto-refresh dashboards
- Real-time notifications
- Live system monitoring

### Data Export
- Export to CSV
- Export to Excel
- Export to PDF
- Custom date ranges

### Advanced Filtering
- Multi-column filtering
- Date range filters
- Custom filters
- Saved filter presets

### Responsive Design
- Mobile-friendly
- Tablet optimized
- Desktop layouts
- Adaptive charts

## Security Features

- Role-based access control (RBAC)
- Two-factor authentication
- Session management
- Audit logging
- IP whitelisting
- Activity monitoring

## Performance Optimization

- Server-side rendering (SSR)
- Static site generation (SSG)
- Code splitting
- Image optimization
- API response caching
- Lazy loading

## Monitoring & Alerts

- System health alerts
- Performance alerts
- Security alerts
- Compliance alerts
- Custom alert rules
- Email/SMS notifications

## API Integration

The admin panel connects to all backend services:

- Authentication Service
- User Management Service
- Trading Service
- Wallet Service
- Compliance Service
- Risk Management Service
- Analytics Service
- Notification Service

## Testing

```bash
npm test
```

## Deployment

### Vercel
```bash
vercel deploy
```

### Docker
```bash
docker build -t tigerex-admin .
docker run -p 3001:3001 tigerex-admin
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.