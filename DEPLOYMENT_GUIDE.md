# TigerEx Platform - Complete Deployment Guide

This guide covers the deployment of all TigerEx platform components including backend services, frontend applications, mobile apps, and admin panel.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Backend Services Deployment](#backend-services-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Mobile App Deployment](#mobile-app-deployment)
6. [Admin Panel Deployment](#admin-panel-deployment)
7. [Database Setup](#database-setup)
8. [Monitoring & Logging](#monitoring--logging)
9. [Security Configuration](#security-configuration)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Docker 24.0+
- Docker Compose 2.20+
- Kubernetes 1.28+ (for production)
- Node.js 20.x
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- MongoDB 7+
- Nginx 1.24+

### Cloud Services (Recommended)
- AWS / Google Cloud / Azure
- CDN (CloudFlare / AWS CloudFront)
- Object Storage (S3 / GCS)
- Email Service (SendGrid / AWS SES)
- SMS Service (Twilio)

---

## Infrastructure Setup

### 1. Server Requirements

#### Production Environment

**Backend Services**
- CPU: 8 cores minimum
- RAM: 32GB minimum
- Storage: 500GB SSD
- Network: 1Gbps

**Database Servers**
- CPU: 16 cores
- RAM: 64GB
- Storage: 1TB NVMe SSD
- IOPS: 10,000+

**Load Balancers**
- CPU: 4 cores
- RAM: 8GB
- Network: 10Gbps

### 2. Network Configuration

```nginx
# /etc/nginx/nginx.conf
upstream backend_api {
    least_conn;
    server backend1.tigerex.com:8000;
    server backend2.tigerex.com:8000;
    server backend3.tigerex.com:8000;
}

upstream websocket {
    ip_hash;
    server ws1.tigerex.com:8080;
    server ws2.tigerex.com:8080;
}

server {
    listen 443 ssl http2;
    server_name api.tigerex.com;

    ssl_certificate /etc/ssl/certs/tigerex.crt;
    ssl_certificate_key /etc/ssl/private/tigerex.key;

    location / {
        proxy_pass http://backend_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /ws {
        proxy_pass http://websocket;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## Backend Services Deployment

### 1. Trading Bots Service

```bash
cd backend/trading-bots-service

# Build Docker image
docker build -t tigerex/trading-bots:latest .

# Run with Docker Compose
docker-compose up -d

# Or deploy to Kubernetes
kubectl apply -f k8s/trading-bots-deployment.yaml
```

**Environment Variables**:
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/trading_bots
REDIS_URL=redis://localhost:6379/0
API_PORT=8001
LOG_LEVEL=INFO
```

### 2. Unified Account Service

```bash
cd backend/unified-account-service

docker build -t tigerex/unified-account:latest .
docker-compose up -d
```

**Environment Variables**:
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/unified_account
API_PORT=8002
LOG_LEVEL=INFO
```

### 3. Staking Service

```bash
cd backend/staking-service

docker build -t tigerex/staking:latest .
docker-compose up -d
```

**Environment Variables**:
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/staking
API_PORT=8003
REWARD_DISTRIBUTION_INTERVAL=3600
LOG_LEVEL=INFO
```

### 4. Launchpad Service

```bash
cd backend/launchpad-service

docker build -t tigerex/launchpad:latest .
docker-compose up -d
```

**Environment Variables**:
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/launchpad
API_PORT=8004
KYC_SERVICE_URL=http://kyc-service:8005
LOG_LEVEL=INFO
```

### Docker Compose for All Services

```yaml
# docker-compose.yml
version: '3.8'

services:
  trading-bots:
    image: tigerex/trading-bots:latest
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://tigerex:password@postgres:5432/trading_bots
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  unified-account:
    image: tigerex/unified-account:latest
    ports:
      - "8002:8002"
    environment:
      - DATABASE_URL=postgresql://tigerex:password@postgres:5432/unified_account
    depends_on:
      - postgres

  staking:
    image: tigerex/staking:latest
    ports:
      - "8003:8003"
    environment:
      - DATABASE_URL=postgresql://tigerex:password@postgres:5432/staking
    depends_on:
      - postgres

  launchpad:
    image: tigerex/launchpad:latest
    ports:
      - "8004:8004"
    environment:
      - DATABASE_URL=postgresql://tigerex:password@postgres:5432/launchpad
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=tigerex
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## Frontend Deployment

### User Panel (Next.js)

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Start production server
npm start

# Or deploy to Vercel
vercel deploy --prod
```

**Environment Variables**:
```env
NEXT_PUBLIC_API_URL=https://api.tigerex.com
NEXT_PUBLIC_WS_URL=wss://api.tigerex.com/ws
NEXT_PUBLIC_SITE_URL=https://tigerex.com
```

### Static Deployment (Nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name tigerex.com;

    root /var/www/tigerex/out;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /_next/static {
        alias /var/www/tigerex/.next/static;
        expires 1y;
        access_log off;
    }
}
```

---

## Mobile App Deployment

### iOS Deployment

1. **Build the app**:
```bash
cd mobile/TigerExApp
expo build:ios
```

2. **Configure App Store Connect**:
   - Create app in App Store Connect
   - Upload screenshots
   - Set app metadata
   - Submit for review

3. **TestFlight Beta**:
```bash
expo upload:ios
```

### Android Deployment

1. **Build the app**:
```bash
cd mobile/TigerExApp
expo build:android
```

2. **Google Play Console**:
   - Create app in Play Console
   - Upload APK/AAB
   - Set app metadata
   - Submit for review

3. **Internal Testing**:
```bash
expo upload:android
```

### Over-the-Air Updates

```bash
# Publish update
expo publish

# Rollback if needed
expo publish:rollback
```

---

## Admin Panel Deployment

```bash
cd admin-panel

# Install dependencies
npm install

# Build for production
npm run build

# Start production server
npm start

# Or deploy to Vercel
vercel deploy --prod
```

**Environment Variables**:
```env
NEXT_PUBLIC_API_URL=https://api.tigerex.com
NEXT_PUBLIC_WS_URL=wss://api.tigerex.com/ws
NEXTAUTH_URL=https://admin.tigerex.com
NEXTAUTH_SECRET=your-secret-key
```

---

## Database Setup

### PostgreSQL Setup

```sql
-- Create databases
CREATE DATABASE trading_bots;
CREATE DATABASE unified_account;
CREATE DATABASE staking;
CREATE DATABASE launchpad;

-- Create user
CREATE USER tigerex WITH PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE trading_bots TO tigerex;
GRANT ALL PRIVILEGES ON DATABASE unified_account TO tigerex;
GRANT ALL PRIVILEGES ON DATABASE staking TO tigerex;
GRANT ALL PRIVILEGES ON DATABASE launchpad TO tigerex;
```

### Database Migration

```bash
# Trading Bots Service
cd backend/trading-bots-service
alembic upgrade head

# Unified Account Service
cd backend/unified-account-service
alembic upgrade head

# Staking Service
cd backend/staking-service
alembic upgrade head

# Launchpad Service
cd backend/launchpad-service
alembic upgrade head
```

### Database Backup

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"

pg_dump -U tigerex trading_bots > $BACKUP_DIR/trading_bots_$DATE.sql
pg_dump -U tigerex unified_account > $BACKUP_DIR/unified_account_$DATE.sql
pg_dump -U tigerex staking > $BACKUP_DIR/staking_$DATE.sql
pg_dump -U tigerex launchpad > $BACKUP_DIR/launchpad_$DATE.sql

# Upload to S3
aws s3 sync $BACKUP_DIR s3://tigerex-backups/postgres/
```

---

## Monitoring & Logging

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'trading-bots'
    static_configs:
      - targets: ['localhost:8001']

  - job_name: 'unified-account'
    static_configs:
      - targets: ['localhost:8002']

  - job_name: 'staking'
    static_configs:
      - targets: ['localhost:8003']

  - job_name: 'launchpad'
    static_configs:
      - targets: ['localhost:8004']
```

### Grafana Dashboards

Import pre-built dashboards:
- System Metrics
- API Performance
- Database Performance
- User Activity
- Trading Volume

### ELK Stack (Logging)

```yaml
# docker-compose-elk.yml
version: '3.8'

services:
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

---

## Security Configuration

### SSL/TLS Setup

```bash
# Generate SSL certificate with Let's Encrypt
certbot certonly --nginx -d tigerex.com -d www.tigerex.com -d api.tigerex.com
```

### Firewall Rules

```bash
# UFW Configuration
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### Security Headers

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

---

## Kubernetes Deployment (Production)

### Trading Bots Service

```yaml
# k8s/trading-bots-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trading-bots
spec:
  replicas: 3
  selector:
    matchLabels:
      app: trading-bots
  template:
    metadata:
      labels:
        app: trading-bots
    spec:
      containers:
      - name: trading-bots
        image: tigerex/trading-bots:latest
        ports:
        - containerPort: 8001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: trading-bots-url
---
apiVersion: v1
kind: Service
metadata:
  name: trading-bots-service
spec:
  selector:
    app: trading-bots
  ports:
  - port: 8001
    targetPort: 8001
  type: LoadBalancer
```

### Apply Kubernetes Configurations

```bash
# Create namespace
kubectl create namespace tigerex

# Apply configurations
kubectl apply -f k8s/ -n tigerex

# Check status
kubectl get pods -n tigerex
kubectl get services -n tigerex
```

---

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: |
          docker build -t tigerex/trading-bots:${{ github.sha }} backend/trading-bots-service
          docker build -t tigerex/unified-account:${{ github.sha }} backend/unified-account-service
          docker build -t tigerex/staking:${{ github.sha }} backend/staking-service
          docker build -t tigerex/launchpad:${{ github.sha }} backend/launchpad-service
      
      - name: Push to registry
        run: |
          docker push tigerex/trading-bots:${{ github.sha }}
          docker push tigerex/unified-account:${{ github.sha }}
          docker push tigerex/staking:${{ github.sha }}
          docker push tigerex/launchpad:${{ github.sha }}
      
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/trading-bots trading-bots=tigerex/trading-bots:${{ github.sha }}
          kubectl set image deployment/unified-account unified-account=tigerex/unified-account:${{ github.sha }}
          kubectl set image deployment/staking staking=tigerex/staking:${{ github.sha }}
          kubectl set image deployment/launchpad launchpad=tigerex/launchpad:${{ github.sha }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Vercel
        run: |
          cd frontend
          vercel deploy --prod --token=${{ secrets.VERCEL_TOKEN }}

  deploy-admin:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy Admin Panel
        run: |
          cd admin-panel
          vercel deploy --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

## Troubleshooting

### Common Issues

#### Service Not Starting
```bash
# Check logs
docker logs trading-bots-service

# Check service status
systemctl status trading-bots

# Restart service
docker-compose restart trading-bots
```

#### Database Connection Issues
```bash
# Test connection
psql -h localhost -U tigerex -d trading_bots

# Check PostgreSQL logs
tail -f /var/log/postgresql/postgresql-15-main.log
```

#### High Memory Usage
```bash
# Check memory usage
free -h
docker stats

# Restart services
docker-compose restart
```

---

## Health Checks

### Service Health Endpoints

```bash
# Trading Bots Service
curl http://localhost:8001/health

# Unified Account Service
curl http://localhost:8002/health

# Staking Service
curl http://localhost:8003/health

# Launchpad Service
curl http://localhost:8004/health
```

### Automated Health Monitoring

```bash
#!/bin/bash
# health-check.sh

SERVICES=("8001" "8002" "8003" "8004")

for port in "${SERVICES[@]}"; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health)
    if [ $response -eq 200 ]; then
        echo "Service on port $port is healthy"
    else
        echo "Service on port $port is unhealthy"
        # Send alert
        curl -X POST https://alerts.tigerex.com/webhook \
          -d "Service on port $port is down"
    fi
done
```

---

## Scaling Guidelines

### Horizontal Scaling

```bash
# Scale up
kubectl scale deployment trading-bots --replicas=5

# Auto-scaling
kubectl autoscale deployment trading-bots --min=3 --max=10 --cpu-percent=80
```

### Database Scaling

- Read replicas for read-heavy operations
- Connection pooling (PgBouncer)
- Partitioning for large tables
- Caching with Redis

---

## Backup & Recovery

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

# Database backup
pg_dump -U tigerex trading_bots | gzip > /backups/trading_bots_$(date +%Y%m%d).sql.gz

# Upload to S3
aws s3 cp /backups/ s3://tigerex-backups/ --recursive

# Cleanup old backups (keep 30 days)
find /backups -mtime +30 -delete
```

### Recovery Procedure

```bash
# Restore database
gunzip < backup.sql.gz | psql -U tigerex trading_bots

# Restore from S3
aws s3 cp s3://tigerex-backups/trading_bots_20241201.sql.gz .
gunzip < trading_bots_20241201.sql.gz | psql -U tigerex trading_bots
```

---

## Performance Tuning

### PostgreSQL Optimization

```sql
-- postgresql.conf
shared_buffers = 8GB
effective_cache_size = 24GB
maintenance_work_mem = 2GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 52MB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
```

### Redis Optimization

```conf
# redis.conf
maxmemory 4gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

---

## Support & Maintenance

### Regular Maintenance Tasks

- Daily: Check logs, monitor alerts
- Weekly: Review performance metrics, update dependencies
- Monthly: Security patches, database optimization
- Quarterly: Disaster recovery testing, capacity planning

### Contact Information

- Technical Support: support@tigerex.com
- Emergency: emergency@tigerex.com
- Documentation: docs.tigerex.com

---

**Last Updated**: December 2024  
**Version**: 2.0.0