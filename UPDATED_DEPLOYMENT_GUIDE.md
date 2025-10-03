# TigerEx Deployment Guide (Updated)

**Version:** 2.0 (Consolidated)  
**Date:** 2025-10-03  
**Status:** Production Ready

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Service Configuration](#service-configuration)
4. [Database Setup](#database-setup)
5. [Docker Deployment](#docker-deployment)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [Cloud Deployment](#cloud-deployment)
8. [Monitoring & Logging](#monitoring--logging)
9. [Security Configuration](#security-configuration)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum (Development)**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB SSD
- OS: Ubuntu 20.04+ / macOS / Windows with WSL2

**Recommended (Production)**
- CPU: 16+ cores
- RAM: 32+ GB
- Storage: 500+ GB NVMe SSD
- OS: Ubuntu 22.04 LTS

### Software Requirements

```bash
# Docker & Docker Compose
Docker: 24.0+
Docker Compose: 2.20+

# Programming Languages
Node.js: 18.x or 20.x
Python: 3.11+
Go: 1.21+
Rust: 1.70+

# Databases
PostgreSQL: 14+
MongoDB: 6+
Redis: 7+

# Tools
Git: 2.40+
kubectl: 1.28+ (for Kubernetes)
helm: 3.12+ (for Kubernetes)
```

---

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cd TigerEx-
```

### 2. Environment Variables

Create `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# ============================================
# GENERAL CONFIGURATION
# ============================================
NODE_ENV=production
APP_NAME=TigerEx
APP_URL=https://tigerex.com
API_VERSION=v1

# ============================================
# DATABASE CONFIGURATION
# ============================================
# PostgreSQL
DATABASE_URL=postgresql://tigerex:secure_password@postgres:5432/tigerex
DATABASE_POOL_SIZE=20
DATABASE_MAX_CONNECTIONS=100

# MongoDB
MONGODB_URL=mongodb://tigerex:secure_password@mongodb:27017/tigerex
MONGODB_DATABASE=tigerex

# Redis
REDIS_URL=redis://:secure_password@redis:6379
REDIS_DB=0
REDIS_CACHE_TTL=3600

# TimescaleDB (for time-series data)
TIMESCALE_URL=postgresql://tigerex:secure_password@timescaledb:5432/tigerex_timeseries

# ============================================
# SECURITY
# ============================================
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_EXPIRATION=24h
REFRESH_TOKEN_EXPIRATION=7d
ENCRYPTION_KEY=your-32-character-encryption-key
API_KEY_SECRET=your-api-key-secret

# ============================================
# BLOCKCHAIN CONFIGURATION
# ============================================
# Ethereum
ETHEREUM_RPC=https://mainnet.infura.io/v3/YOUR-INFURA-KEY
ETHEREUM_CHAIN_ID=1
ETHEREUM_PRIVATE_KEY=your-ethereum-private-key

# Binance Smart Chain
BSC_RPC=https://bsc-dataseed.binance.org
BSC_CHAIN_ID=56
BSC_PRIVATE_KEY=your-bsc-private-key

# Polygon
POLYGON_RPC=https://polygon-rpc.com
POLYGON_CHAIN_ID=137
POLYGON_PRIVATE_KEY=your-polygon-private-key

# Solana
SOLANA_RPC=https://api.mainnet-beta.solana.com
SOLANA_PRIVATE_KEY=your-solana-private-key

# ============================================
# SERVICE PORTS
# ============================================
API_GATEWAY_PORT=8000
MATCHING_ENGINE_PORT=8001
WALLET_SERVICE_PORT=8002
AUTH_SERVICE_PORT=8003
ADMIN_PANEL_PORT=8004
SPOT_TRADING_PORT=8005
FUTURES_TRADING_PORT=8006
DEX_INTEGRATION_PORT=8007
WEB3_INTEGRATION_PORT=8008

# ============================================
# EXTERNAL SERVICES
# ============================================
# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@tigerex.com

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# AWS (for S3, SES, etc.)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=tigerex-assets

# ============================================
# PAYMENT GATEWAYS
# ============================================
# Stripe
STRIPE_PUBLIC_KEY=pk_live_your-stripe-public-key
STRIPE_SECRET_KEY=sk_live_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# PayPal
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
PAYPAL_MODE=live

# ============================================
# KYC/AML PROVIDERS
# ============================================
# Jumio
JUMIO_API_TOKEN=your-jumio-token
JUMIO_API_SECRET=your-jumio-secret
JUMIO_BASE_URL=https://netverify.com

# Onfido
ONFIDO_API_TOKEN=your-onfido-token
ONFIDO_REGION=us

# ============================================
# MONITORING & LOGGING
# ============================================
# Sentry
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Prometheus
PROMETHEUS_PORT=9090

# Grafana
GRAFANA_PORT=3000
GRAFANA_ADMIN_PASSWORD=secure-grafana-password

# ELK Stack
ELASTICSEARCH_URL=http://elasticsearch:9200
KIBANA_PORT=5601
LOGSTASH_PORT=5000

# ============================================
# RATE LIMITING
# ============================================
RATE_LIMIT_WINDOW=15m
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_SKIP_SUCCESSFUL_REQUESTS=false

# ============================================
# WEBSOCKET
# ============================================
WEBSOCKET_PORT=8080
WEBSOCKET_PATH=/ws
WEBSOCKET_PING_INTERVAL=30000
WEBSOCKET_PING_TIMEOUT=5000

# ============================================
# FEATURES FLAGS
# ============================================
ENABLE_CEX=true
ENABLE_DEX=true
ENABLE_P2P=true
ENABLE_FUTURES=true
ENABLE_MARGIN=true
ENABLE_OPTIONS=true
ENABLE_STAKING=true
ENABLE_LENDING=true
ENABLE_NFT=true
ENABLE_LAUNCHPAD=true

# ============================================
# ADMIN CONFIGURATION
# ============================================
ADMIN_EMAIL=admin@tigerex.com
ADMIN_PASSWORD=change-this-secure-password
SUPER_ADMIN_KEY=your-super-admin-key

# ============================================
# BACKUP CONFIGURATION
# ============================================
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
BACKUP_S3_BUCKET=tigerex-backups
```

---

## Service Configuration

### Consolidated Services

The following services have been consolidated for better performance:

1. **unified-admin-panel** (9 services consolidated)
2. **wallet-service** (3 services consolidated)
3. **auth-service** (3 services consolidated)
4. **spot-trading** (4 services consolidated)
5. **defi-service** (3 services consolidated)

### Service Dependencies

```yaml
# Service dependency graph
api-gateway:
  depends_on:
    - auth-service
    - spot-trading
    - wallet-service

spot-trading:
  depends_on:
    - matching-engine
    - wallet-service
    - market-data-service

wallet-service:
  depends_on:
    - blockchain-service
    - transaction-engine

auth-service:
  depends_on:
    - database
    - redis
```

---

## Database Setup

### 1. PostgreSQL Setup

```bash
# Create database
createdb tigerex

# Run migrations
cd backend/database
python main.py migrate

# Seed initial data
python main.py seed
```

### 2. MongoDB Setup

```bash
# Create database and collections
mongosh
use tigerex
db.createCollection("users")
db.createCollection("orders")
db.createCollection("trades")
```

### 3. Redis Setup

```bash
# Test connection
redis-cli ping

# Set up persistence
redis-cli CONFIG SET save "900 1 300 10 60 10000"
```

---

## Docker Deployment

### 1. Build Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build spot-trading
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d api-gateway spot-trading wallet-service

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f spot-trading
```

### 3. Scale Services

```bash
# Scale spot trading service
docker-compose up -d --scale spot-trading=3

# Scale multiple services
docker-compose up -d --scale spot-trading=3 --scale futures-trading=2
```

### 4. Health Checks

```bash
# Check service health
docker-compose ps

# Check specific service
curl http://localhost:8000/health

# Check all services
./scripts/health-check.sh
```

---

## Kubernetes Deployment

### 1. Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installation
kubectl version --client
helm version
```

### 2. Create Namespace

```bash
kubectl create namespace tigerex
kubectl config set-context --current --namespace=tigerex
```

### 3. Deploy Services

```bash
# Apply configurations
kubectl apply -f devops/kubernetes/

# Or use helm
helm install tigerex ./helm/tigerex

# Check deployment status
kubectl get pods
kubectl get services
kubectl get deployments
```

### 4. Configure Ingress

```bash
# Install nginx ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Apply ingress rules
kubectl apply -f devops/kubernetes/ingress.yaml

# Get ingress IP
kubectl get ingress
```

### 5. Configure SSL/TLS

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create certificate
kubectl apply -f devops/kubernetes/certificate.yaml
```

---

## Cloud Deployment

### AWS Deployment

#### Using ECS

```bash
# Install AWS CLI
pip install awscli

# Configure AWS
aws configure

# Create ECS cluster
aws ecs create-cluster --cluster-name tigerex-cluster

# Deploy services
./scripts/deploy-aws-ecs.sh
```

#### Using EKS

```bash
# Create EKS cluster
eksctl create cluster \
  --name tigerex-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.large \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 10

# Deploy to EKS
kubectl apply -f devops/kubernetes/
```

### Google Cloud Deployment

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Initialize gcloud
gcloud init

# Create GKE cluster
gcloud container clusters create tigerex-cluster \
  --num-nodes=3 \
  --machine-type=n1-standard-4 \
  --region=us-central1

# Deploy to GKE
kubectl apply -f devops/kubernetes/
```

### Azure Deployment

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Create AKS cluster
az aks create \
  --resource-group tigerex-rg \
  --name tigerex-cluster \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-addons monitoring

# Deploy to AKS
kubectl apply -f devops/kubernetes/
```

---

## Monitoring & Logging

### 1. Prometheus Setup

```bash
# Deploy Prometheus
kubectl apply -f devops/monitoring/prometheus/

# Access Prometheus
kubectl port-forward svc/prometheus 9090:9090
# Open http://localhost:9090
```

### 2. Grafana Setup

```bash
# Deploy Grafana
kubectl apply -f devops/monitoring/grafana/

# Get admin password
kubectl get secret grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# Access Grafana
kubectl port-forward svc/grafana 3000:3000
# Open http://localhost:3000
```

### 3. ELK Stack Setup

```bash
# Deploy Elasticsearch
kubectl apply -f devops/monitoring/elasticsearch/

# Deploy Logstash
kubectl apply -f devops/monitoring/logstash/

# Deploy Kibana
kubectl apply -f devops/monitoring/kibana/

# Access Kibana
kubectl port-forward svc/kibana 5601:5601
# Open http://localhost:5601
```

---

## Security Configuration

### 1. SSL/TLS Certificates

```bash
# Using Let's Encrypt
certbot certonly --standalone -d tigerex.com -d www.tigerex.com

# Or use cert-manager in Kubernetes
kubectl apply -f devops/kubernetes/certificate.yaml
```

### 2. Firewall Rules

```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp  # API Gateway
ufw enable
```

### 3. Database Security

```bash
# PostgreSQL
# Edit postgresql.conf
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'

# MongoDB
# Edit mongod.conf
security:
  authorization: enabled
net:
  ssl:
    mode: requireSSL
    PEMKeyFile: /path/to/mongodb.pem
```

### 4. Secrets Management

```bash
# Using Kubernetes Secrets
kubectl create secret generic tigerex-secrets \
  --from-literal=jwt-secret=your-jwt-secret \
  --from-literal=db-password=your-db-password

# Using HashiCorp Vault
vault kv put secret/tigerex \
  jwt-secret=your-jwt-secret \
  db-password=your-db-password
```

---

## Troubleshooting

### Common Issues

#### 1. Service Won't Start

```bash
# Check logs
docker-compose logs service-name

# Check resource usage
docker stats

# Restart service
docker-compose restart service-name
```

#### 2. Database Connection Issues

```bash
# Test PostgreSQL connection
psql -h localhost -U tigerex -d tigerex

# Test MongoDB connection
mongosh mongodb://localhost:27017/tigerex

# Test Redis connection
redis-cli ping
```

#### 3. Port Conflicts

```bash
# Check port usage
netstat -tulpn | grep LISTEN

# Kill process on port
kill -9 $(lsof -t -i:8000)
```

#### 4. Memory Issues

```bash
# Increase Docker memory
# Edit Docker Desktop settings or docker-compose.yml

# Check memory usage
docker stats

# Clear unused resources
docker system prune -a
```

### Health Check Script

```bash
#!/bin/bash
# scripts/health-check.sh

services=(
  "api-gateway:8000"
  "spot-trading:8005"
  "wallet-service:8002"
  "auth-service:8003"
)

for service in "${services[@]}"; do
  name="${service%%:*}"
  port="${service##*:}"
  
  if curl -f http://localhost:$port/health > /dev/null 2>&1; then
    echo "✅ $name is healthy"
  else
    echo "❌ $name is unhealthy"
  fi
done
```

---

## Post-Deployment Checklist

- [ ] All services are running
- [ ] Databases are accessible
- [ ] SSL/TLS certificates are valid
- [ ] Monitoring is configured
- [ ] Logging is working
- [ ] Backups are scheduled
- [ ] Security scans completed
- [ ] Load testing performed
- [ ] Documentation updated
- [ ] Team trained on operations

---

## Maintenance

### Regular Tasks

**Daily**
- Monitor service health
- Check error logs
- Review security alerts

**Weekly**
- Database backups verification
- Performance metrics review
- Security updates

**Monthly**
- Full system backup
- Security audit
- Capacity planning
- Update dependencies

---

## Support

For deployment support:
- 📧 Email: devops@tigerex.com
- 💬 Slack: #tigerex-deployment
- 📖 Docs: https://docs.tigerex.com/deployment

---

**Last Updated:** 2025-10-03  
**Version:** 2.0  
**Status:** Production Ready