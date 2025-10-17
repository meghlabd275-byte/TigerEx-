# TigerEx Platform - Complete Deployment Guide

## 🚀 Production Deployment Guide

### Prerequisites

#### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 10+
- **CPU**: 8+ cores (16+ cores recommended)
- **RAM**: 32GB+ (64GB+ recommended)
- **Storage**: 500GB+ SSD (1TB+ recommended)
- **Network**: 1Gbps+ bandwidth

#### Software Requirements
- **Docker**: 20.10+
- **Docker Compose**: 1.29+
- **Kubernetes**: 1.20+ (optional)
- **Node.js**: 16+
- **Python**: 3.8+
- **Rust**: 1.60+ (for some services)
- **Nginx**: 1.18+ (for reverse proxy)

### 1. Environment Setup

#### Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git vim htop build-essential

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python
sudo apt install -y python3 python3-pip python3-venv

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### 2. Repository Setup

```bash
# Clone repository
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cd TigerEx-

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### 3. Database Setup

#### PostgreSQL Setup
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE tigerex;
CREATE USER tigerex_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE tigerex TO tigerex_user;
\q
```

#### Redis Setup
```bash
# Install Redis
sudo apt install -y redis-server

# Configure Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 4. Backend Services Deployment

#### Using Docker Compose
```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Manual Service Deployment
```bash
# Install Python dependencies
cd backend
pip3 install -r requirements.txt

# Start individual services
python3 account-management-service/main.py &
python3 trading-engine/src/main.py &
python3 wallet-service/main.py &
# ... continue for all services
```

### 5. Frontend Deployment

#### Next.js Frontend
```bash
cd frontend
npm install
npm run build
npm start
```

#### Static File Serving
```bash
# Build static files
npm run build
npm run export

# Serve with Nginx
sudo cp -r out/* /var/www/html/
```

### 6. Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # API Gateway
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 7. SSL/TLS Setup

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 8. Monitoring and Logging

#### Prometheus Setup
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'tigerex-backend'
    static_configs:
      - targets: ['localhost:8000', 'localhost:8001', 'localhost:8002']
```

#### Grafana Dashboard
```bash
# Install Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana
```

### 9. Security Configuration

#### Firewall Setup
```bash
# Configure UFW
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 5432/tcp  # PostgreSQL (internal only)
sudo ufw deny 6379/tcp  # Redis (internal only)
```

#### Security Headers
```nginx
# Add to Nginx config
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

### 10. Backup and Recovery

#### Database Backup
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U tigerex_user tigerex > backup_$DATE.sql
aws s3 cp backup_$DATE.sql s3://your-backup-bucket/
```

#### Service Backup
```bash
# Backup configuration files
tar -czf config_backup_$DATE.tar.gz .env nginx.conf docker-compose.yml
```

### 11. Performance Optimization

#### Database Optimization
```sql
-- PostgreSQL tuning
ALTER SYSTEM SET shared_buffers = '8GB';
ALTER SYSTEM SET effective_cache_size = '24GB';
ALTER SYSTEM SET maintenance_work_mem = '2GB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
SELECT pg_reload_conf();
```

#### Redis Optimization
```bash
# Redis configuration
echo 'vm.overcommit_memory = 1' >> /etc/sysctl.conf
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
sysctl -p
```

### 12. Scaling and Load Balancing

#### Horizontal Scaling
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  trading-engine:
    deploy:
      replicas: 3
  
  api-gateway:
    deploy:
      replicas: 2
```

#### Load Balancer Configuration
```nginx
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location /api/ {
        proxy_pass http://backend;
    }
}
```

### 13. White Label Deployment

#### Custom Branding
```bash
# Update branding files
cp custom-logo.png frontend/public/logo.png
cp custom-favicon.ico frontend/public/favicon.ico

# Update configuration
export BRAND_NAME="Your Exchange"
export BRAND_COLOR="#your-color"
export BRAND_DOMAIN="your-domain.com"
```

#### Multi-tenant Setup
```yaml
# docker-compose.multitenant.yml
services:
  tenant1-frontend:
    build: ./frontend
    environment:
      - TENANT_ID=tenant1
      - BRAND_CONFIG=/config/tenant1.json
  
  tenant2-frontend:
    build: ./frontend
    environment:
      - TENANT_ID=tenant2
      - BRAND_CONFIG=/config/tenant2.json
```

### 14. Troubleshooting

#### Common Issues
1. **Port conflicts**: Check with `netstat -tulpn`
2. **Memory issues**: Monitor with `htop` and adjust Docker limits
3. **Database connections**: Check PostgreSQL max_connections
4. **SSL certificate**: Verify with `certbot certificates`

#### Log Analysis
```bash
# Check service logs
docker-compose logs service-name

# Check system logs
journalctl -u docker
journalctl -u nginx

# Check application logs
tail -f backend/logs/app.log
```

### 15. Maintenance

#### Regular Updates
```bash
#!/bin/bash
# update.sh
git pull origin main
docker-compose pull
docker-compose up -d --build
docker system prune -f
```

#### Health Checks
```bash
# Health check script
curl -f http://localhost:8000/health || exit 1
curl -f http://localhost:3000/api/health || exit 1
```

## 🎯 Quick Start Commands

```bash
# Complete deployment in one command
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cd TigerEx-
cp .env.example .env
# Edit .env file
docker-compose up -d
```

## 📞 Support

For deployment support, please:
1. Check the troubleshooting section
2. Review logs for error messages
3. Contact the development team
4. Submit issues on GitHub

---

**Note**: This guide covers production deployment. For development setup, see SETUP.md