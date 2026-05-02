# TigerEx Custom Database

Database configuration and schema for TigerEx exchange.

## Files

```
custom-database/
├── schema.sql           # PostgreSQL schema
├── config.py            # Python config loader
├── .env.example        # Environment template
├── scripts/
│   └── backup.sh       # Backup script
```

## Setup

1. Copy environment template:
```bash
cp .env.example .env
# Edit .env with real credentials
```

2. Load environment and use in Python:
```python
from config import Config, load_env_file

load_env_file('.env')
Config.validate()

# Use Config.database.url, etc.
```

3. Run schema:
```bash
psql -h localhost -U tigerex -d tigerex_db -f schema.sql
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| DB_HOST | PostgreSQL host |
| DB_PORT | PostgreSQL port |
| DB_USER | Database user |
| DB_PASSWORD | **Required** - password |
| DB_NAME | Database name |
| REDIS_HOST | Redis host |
| REDIS_PASSWORD | Redis password |
| BACKUP_S3_BUCKET | S3 bucket for backups |

## Schema Tables

- `users` - User accounts
- `accounts` - Trading accounts
- `orders` - Trading orders
- `transactions` - Transaction history
- `deposits` - Deposit records
- `withdrawals` - Withdrawal records
- `blocks` - Blockchain blocks
- `block_accounts` - Blockchain accounts
- `tokens` - Token registry
- `liquidity_pools` - AMM pools

## Backup

Set up cron job:
```bash
0 2 * * * /path/to/scripts/backup.sh
```