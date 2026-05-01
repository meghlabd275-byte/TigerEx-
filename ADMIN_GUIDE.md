# TigerEx - Admin Guide
## Complete Admin Features & Functionality
---

## Admin Access
### Getting Admin Access
1. Contact senior admin to grant permissions
2. Access: `/admin` or `/admin-panel`
### Admin Roles
| Role | Access Level |
|------|-------------|
| Super Admin | Full access |
| Admin | User/pairs management |
| Compliance | KYC verification |
| Finance | Withdrawals |
| Support | Tickets |
| Trading | Pairs, orders |

---

## User Management
### View Users
- List with filters (status, KYC, date, volume)
- User details (profile, history, wallets, 2FA)
### Actions
- Suspend/unsuspend
- Reset password
- Reset 2FA
- Adjust KYC level
- Freeze wallet
- Cancel orders

---

## KYC & Compliance
### Tiers
| Level | Requirements | Limits |
|-------|-------------|--------|
| 0 | Email verified | Low |
| 1 | ID + Selfie | Medium |
| 2 | Address proof | High |
| 3 | Enhanced | Unlimited |

### Compliance
- AML screening
- Sanctions check
- PEP check
- Transaction monitoring

---

## Finance Management
### Deposits/Withdrawals
- Approve large transactions
- Manual credit/ debit

### Fees
- Trading fees by pair
- Withdrawal fees
- VIP tier settings

---

## Trading Pairs
### Add/Manage Pairs
- Configure min/max orders, tick size, fees
- Enable/disable trading
- Adjust fees

---

## Analytics
- Dashboard (volume, users, revenue)
- Reports (daily/weekly/monthly)
- Logs (trading, user actions)

---

## Security
- 2FA requirements
- IP whitelist
- Fraud detection
- Rate limiting

---

## Tech Operations
- Service control (start/stop/restart)
- Database backup/restore
- Cache management

---

## Emergency Actions
### Halt Trading
```bash
curl -X POST http://localhost:8000/Api/emergency/halt
```
### Cancel All Orders
```bash
curl -X POST http://localhost:8000/Api/orders/cancel-all
```
### Freeze Platform
```bash
curl -X POST http://localhost:8000/Api/emergency/Freeze
```

---

## Daily Checklist
- [ ] Check pending withdrawals
- [ ] Review KYC queue
- [ ] Monitor trading volume
- [ ] Check support tickets
