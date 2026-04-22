# TigerEx Roles & Permissions - Complete Documentation

## User Roles Hierarchy

```
SUPER_ADMIN
    │
    ├── ADMIN
    │   │
    │   ├── MODERATOR
    │   │   │
    │   │   ├── TRADER
    │   │   │   │
    │   │   │   ├── VIEWER
    │   │   │   │
    │   │   │   └── (Inherited by all below)
    │   │   │
    │   │   └── (Inherited)
    │   │
    │   └── (Inherited)
    │
    └── (Inherited)
```

---

## Role Definitions & Permissions

### 1. SUPER_ADMIN 👑

**Description**: Full system control with absolute privileges

| Permission | Access |
|------------|--------|
| **USER MANAGEMENT** | |
| Create admin | ✅ |
| Delete admin | ✅ |
| Edit admin role | ✅ |
| Suspend admin | ✅ |
| Ban admin | ✅ |
| View all admins | ✅ |
| **USER CONTROL** | |
| Create user | ✅ |
| Delete user | ✅ |
| Edit any user | ✅ |
| Suspend any user | ✅ |
| Ban any user | ✅ |
| Resume any user | ✅ |
| View all users | ✅ |
| Export user data | ✅ |
| **SERVICE CONTROL** | |
| Start service | ✅ |
| Stop service | ✅ |
| Pause service | ✅ |
| Resume service | ✅ |
| Halt service | ✅ |
| Restart service | ✅ |
| View all services | ✅ |
| **FEE MANAGEMENT** | |
| Set trading fees | ✅ |
| Set withdrawal fees | ✅ |
| Set deposit fees | ✅ |
| Set role-based fees | ✅ |
| Edit fee profiles | ✅ |
| **EXCHANGE CONTROL** | |
| Enable exchange | ✅ |
| Disable exchange | ✅ |
| Maintenance mode | ✅ |
| White Label settings | ✅ |
| Exchange ID config | ✅ |
| **SYSTEM CONFIG** | |
| View all settings | ✅ |
| Edit all settings | ✅ |
| API key management | ✅ |
| Webhook config | ✅ |
| **AUDIT & LOGS** | |
| View all logs | ✅ |
| Export audit logs | ✅ |
| Security alerts | ✅ |

---

### 2. ADMIN 🛡️

**Description**: Administrative control for day-to-day operations

| Permission | Access |
|------------|--------|
| **USER MANAGEMENT** | |
| Create moderator/trader | ✅ |
| Delete user | ✅ |
| Edit user roles | ✅ |
| Suspend user | ✅ |
| Ban user | ✅ |
| View all users | ✅ |
| **USER CONTROL** | |
| Create user | ✅ |
| Delete user | ✅ |
| Edit user | ✅ |
| Suspend user | ✅ |
| Ban user | ✅ |
| Resume user | ✅ |
| View all users | ✅ |
| Export user data | ✅ |
| **SERVICE CONTROL** | |
| Start service | ✅ |
| Stop service | ✅ |
| Pause service | ✅ |
| Resume service | ✅ |
| Halt service | ✅ |
| View all services | ✅ |
| **FEE MANAGEMENT** | |
| Set trading fees | ✅ |
| Set withdrawal fees | ✅ |
| Set role-based fees | ✅ |
| View fee profiles | ✅ |
| **EXCHANGE CONTROL** | |
| View exchange status | ✅ |
| Enable/disable trading | ✅ |
| Maintenance mode | ✅ |
| **AUDIT & LOGS** | |
| View admin logs | ✅ |
| View user logs | ✅ |

---

### 3. MODERATOR 👮

**Description**: Limited moderaton capabilities

| Permission | Access |
|------------|--------|
| **USER MANAGEMENT** | |
| View users | ✅ |
| Edit user profile | ✅ |
| Suspend user | ✅ |
| Resume user | ✅ |
| View user details | ✅ |
| **SERVICE CONTROL** | |
| View services status | ✅ |
| **TICKET MANAGEMENT** | |
| View support tickets | ✅ |
| Reply to tickets | ✅ |
| Close tickets | ✅ |
| Escalate tickets | ✅ |
| **CONTENT MODERATION** | |
| View flagged content | ✅ |
| Remove content | ✅ |
| **AUDIT & LOGS** | |
| View own actions | ✅ |

---

### 4. TRADER 💰

**Description**: Standard trading user

| Permission | Access |
|------------|--------|
| **TRADING** | |
| Place buy order | ✅ |
| Place sell order | ✅ |
| Cancel order | ✅ |
| View order history | ✅ |
| View open orders | ✅ |
| **WALLET** | |
| View balance | ✅ |
| Deposit crypto | ✅ |
| Withdraw crypto | ✅ |
| View deposit address | ✅ |
| **PORTFOLIO** | |
| View portfolio | ✅ |
| View performance | ✅ |
| **ACCOUNT** | |
| View profile | ✅ |
| Edit profile | ✅ |
| Enable 2FA | ✅ |
| Change password | ✅ |
| **EARN** | |
| Stake tokens | ✅ |
| Use Earn products | ✅ |
| View Earn history | ✅ |
| **NFT** | |
| View NFTs | ✅ |
| Buy NFTs | ✅ |
| List NFTs | ✅ |
| **P2P** | |
| Create P2P ad | ✅ |
| Trade P2P | ✅ |
| **SOCIAL** | |
| Follow traders | ✅ |
| Copy trade | ✅ |

---

### 5. VIEWER 🔍

**Description**: Read-only access (guest/demo)

| Permission | Access |
|------------|--------|
| **MARKET DATA** | |
| View prices | ✅ |
| View charts | ✅ |
| View order book | ✅ |
| View trades | ✅ |
| **PUBLIC INFO** | |
| View fees | ✅ |
| View trading rules | ✅ |
| View announce | ✅ |
| **LIMITED ACCOUNT** | |
| Register account | ✅ |
| Login | ✅ |

---

## API Endpoints by Role

### User Management Endpoints

| Endpoint | SUPER_ADMIN | ADMIN | MODERATOR | TRADER | VIEWER |
|---------|:--------:|:-----:|:--------:|:-----:|:-----:|
| POST /admin/create | ✅ | ❌ | ❌ | ❌ | ❌ |
| DELETE /admin/:id | ✅ | ❌ | ❌ | ❌ | ❌ |
| PUT /admin/:id/role | ✅ | ❌ | ❌ | ❌ | ❌ |
| POST /user/create | ✅ | ✅ | ❌ | ❌ | ❌ |
| DELETE /user/:id | ✅ | ✅ | ❌ | ❌ | ❌ |
| PUT /user/:id | ✅ | ✅ | ✅ | ❌ | ❌ |
| PUT /user/:id/suspend | ✅ | ✅ | ✅ | ❌ | ❌ |
| PUT /user/:id/ban | ✅ | ✅ | ❌ | ❌ | ❌ |
| PUT /user/:id/resume | ✅ | ✅ | ✅ | ❌ | ❌ |
| GET /users | ✅ | ✅ | ✅ | ❌ | ❌ |
| GET /users/:id | ✅ | ✅ | ✅ | ✅ | ❌ |

### Service Control Endpoints

| Endpoint | SUPER_ADMIN | ADMIN | MODERATOR | TRADER | VIEWER |
|---------|:--------:|:-----:|:--------:|:-----:|:-----:|
| POST /service/start | ✅ | ✅ | ❌ | ❌ | ❌ |
| POST /service/stop | ✅ | ✅ | ❌ | ❌ | ❌ |
| POST /service/pause | ✅ | ✅ | ❌ | ❌ | ❌ |
| POST /service/resume | ✅ | ✅ | ❌ | ❌ | ❌ |
| POST /service/halt | ✅ | ✅ | ❌ | ❌ | ❌ |
| GET /services | ✅ | ✅ | ✅ | ❌ | ❌ |

### Fee Management Endpoints

| Endpoint | SUPER_ADMIN | ADMIN | MODERATOR | TRADER | VIEWER |
|---------|:--------:|:-----:|:--------:|:-----:|:-----:|
| PUT /fees/trading | ✅ | ✅ | ❌ | ❌ | ❌ |
| PUT /fees/withdrawal | ✅ | ✅ | ❌ | ❌ | ❌ |
| PUT /fees/role/:role | ✅ | ✅ | ❌ | ❌ | ❌ |
| GET /fees | ✅ | ✅ | ✅ | ✅ | ✅ |

### Exchange Control Endpoints

| Endpoint | SUPER_ADMIN | ADMIN | MODERATOR | TRADER | VIEWER |
|---------|:--------:|:-----:|:--------:|:-----:|:-----:|
| PUT /exchange/status | ✅ | ❌ | ❌ | ❌ | ❌ |
| PUT /exchange/whitelabel | ✅ | ❌ | ❌ | ❌ |
| PUT /exchange/id | ✅ | ❌ | ❌ | ❌ | ❌ |
| GET /exchange/status | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Admin Dashboard Screens by Role

### SUPER_ADMIN Dashboard
- System Overview
- All Users Management
- All Admins Management
- Service Control Panel
- Fee Management
- Exchange Settings
- Security Settings
- Audit Logs
- API Management
- White Label Config
- Exchange ID Config

### ADMIN Dashboard
- User Management
- Service Monitoring
- Fee Configuration
- Exchange Status
- Audit Logs
- Support Tickets

### MODERATOR Dashboard
- User List
- User Warnings
- Content Moderation
- Support Tickets

### TRADER Dashboard
- Trading Interface
- Portfolio
- Wallet
- Order History
- Earn
- NFTs
- P2P Trading
- Settings

### VIEWER Dashboard
- Market Data (Read-only)
- Public Pages

---

## Code Implementation

```python
# Role-based permissions in backend
class UserRole:
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    TRADER = "trader"
    VIEWER = "viewer"

ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: ["*"],  # All permissions
    UserRole.ADMIN: [
        "user.create", "user.edit", "user.delete", "user.suspend", "user.ban",
        "service.start", "service.stop", "service.pause", "service.resume",
        "fee.set", "fee.view",
        "exchange.status", "logs.view"
    ],
    UserRole.MODERATOR: [
        "user.view", "user.edit", "user.suspend", "user.resume",
        "service.view",
        "ticket.manage", "content.moderate"
    ],
    UserRole.TRADER: [
        "trade.execute", "wallet.deposit", "wallet.withdraw",
        "portfolio.view", "earn.use", "nft.trade", "p2p.trade"
    ],
    UserRole.VIEWER: [
        "market.view", "fees.view", "public.info"
    ]
}
```

---

## Example API Calls by Role

### Create User (SUPER_ADMIN, ADMIN only)
```bash
curl -X POST https://api.tigerex.com/user/create \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "role": "trader"}'
```

### Suspend User (SUPER_ADMIN, ADMIN, MODERATOR)
```bash
curl -X PUT https://api.tigerex.com/user/123/suspend \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

### Set Trading Fee (SUPER_ADMIN, ADMIN)
```bash
curl -X PUT https://api.tigerex.com/fees/trading \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"maker_fee": 0.001, "taker_fee": 0.002}'
```

### Start Service (SUPER_ADMIN only)
```bash
curl -X POST https://api.tigerex.com/service/trading/start \
  -H "Authorization: Bearer <SUPER_ADMIN_TOKEN>"
```

---

## Frontend Role Guards

```typescript
// React role-based access
const RoleGuard = ({ allowedRoles, children }) => {
  const { user } = useAuth();
  
  if (!allowedRoles.includes(user.role)) {
    return <AccessDenied />;
  }
  
  return children;
};

// Usage
<RoleGuard allowedRoles={['super_admin', 'admin']}>
  <AdminPanel />
</RoleGuard>
```

---

*Last Updated: 2026-04-22*
*Document Version: 1.0*