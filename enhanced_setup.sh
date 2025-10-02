#!/bin/bash

# TigerEx Exchange - Enhanced Setup Script
# This script sets up the complete exchange platform with all features

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root"
   exit 1
fi

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check RAM
    total_ram=$(free -m | awk '/^Mem:/{print $2}')
    if [[ $total_ram -lt 8192 ]]; then
        warning "System has less than 8GB RAM. Recommended: 16GB+"
    fi
    
    # Check disk space
    available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $available_space -lt 50 ]]; then
        error "Insufficient disk space. Required: 50GB+, Available: ${available_space}GB"
        exit 1
    fi
    
    # Check for required tools
    command -v docker >/dev/null 2>&1 || { error "Docker is required but not installed. Aborting."; exit 1; }
    command -v docker-compose >/dev/null 2>&1 || { error "Docker Compose is required but not installed. Aborting."; exit 1; }
    command -v node >/dev/null 2>&1 || { error "Node.js is required but not installed. Aborting."; exit 1; }
    command -v python3 >/dev/null 2>&1 || { error "Python 3 is required but not installed. Aborting."; exit 1; }
    
    success "System requirements check passed"
}

# Create environment file
create_env_file() {
    log "Creating environment configuration..."
    
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://postgres:password@postgres:5432/tigerex
REDIS_URL=redis://redis:6379

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# Blockchain Configuration
ETH_RPC=https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID
BSC_RPC=https://bsc-dataseed.binance.org/
POLYGON_RPC=https://polygon-rpc.com/
ARBITRUM_RPC=https://arb1.arbitrum.io/rpc
SOLANA_RPC=https://api.mainnet-beta.solana.com
TON_RPC=https://toncenter.com/api/v2/jsonRPC

# API Keys (Replace with your actual keys)
INFURA_PROJECT_ID=your_infura_project_id
ALCHEMY_API_KEY=your_alchemy_api_key
MORALIS_API_KEY=your_moralis_api_key
COINGECKO_API_KEY=your_coingecko_api_key

# Service URLs
API_GATEWAY_URL=http://api-gateway:8000
AUTH_SERVICE_URL=http://auth-service:8001
TRADING_ENGINE_URL=http://trading-engine:8080
BLOCKCHAIN_INTEGRATION_URL=http://blockchain-integration-service:8100
VIRTUAL_LIQUIDITY_URL=http://virtual-liquidity-service:8150
ADMIN_SERVICE_URL=http://comprehensive-admin-service:8160

# Security Configuration
ADMIN_TOKEN=admin-token-change-this-in-production
API_RATE_LIMIT=1000
CORS_ORIGINS=*

# Trading Configuration
MAX_LEVERAGE=125
DEFAULT_LEVERAGE=1
MIN_ORDER_SIZE=0.001
MAX_ORDER_SIZE=1000000
TRADING_FEE=0.001
WITHDRAWAL_FEE=0.0005

# Blockchain Settings
CONFIRMATIONS_REQUIRED=6
GAS_PRICE_MULTIPLIER=1.2
PRIORITY_FEE=2

# Monitoring
LOG_LEVEL=INFO
METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=30

# Exchange Information
EXCHANGE_NAME=TigerEx
EXCHANGE_URL=https://tigerex.com
SUPPORT_EMAIL=support@tigerex.com
EOF

    success "Environment file created"
}

# Setup database
setup_database() {
    log "Setting up database..."
    
    # Create database initialization script
    mkdir -p backend/database/migrations
    
    cat > backend/database/migrations/01-init.sql << EOF
-- Initialize TigerEx database
CREATE DATABASE IF NOT EXISTS tigerex;
USE tigerex;

-- Create admin user
CREATE USER 'tigerex_admin'@'%' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON tigerex.* TO 'tigerex_admin'@'%';
FLUSH PRIVILEGES;
EOF

    success "Database setup completed"
}

# Install Python dependencies
install_python_deps() {
    log "Installing Python dependencies for all services..."
    
    services=(
        "backend/blockchain-integration-service"
        "backend/virtual-liquidity-service"
        "backend/trading-engine"
        "backend/comprehensive-admin-service"
    )
    
    for service in "${services[@]}"; do
        if [[ -f "$service/requirements.txt" ]]; then
            log "Installing dependencies for $service"
            pip install -r "$service/requirements.txt"
        fi
    done
    
    success "Python dependencies installed"
}

# Setup frontend dependencies
setup_frontend() {
    log "Setting up frontend dependencies..."
    
    # Install admin dashboard dependencies
    if [[ -d "frontend/admin-dashboard" ]]; then
        cd frontend/admin-dashboard
        if [[ -f "package.json" ]]; then
            npm install
        fi
        cd ../..
    fi
    
    # Install main frontend dependencies
    if [[ -d "frontend" ]] && [[ -f "frontend/package.json" ]]; then
        cd frontend
        npm install
        cd ..
    fi
    
    success "Frontend dependencies installed"
}

# Create systemd services
create_systemd_services() {
    log "Creating systemd services..."
    
    sudo tee /etc/systemd/system/tigerex-exchange.service > /dev/null << EOF
[Unit]
Description=TigerEx Exchange Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    success "Systemd service created"
}

# Setup SSL certificates
setup_ssl() {
    log "Setting up SSL certificates..."
    
    # Create SSL directory
    mkdir -p ssl
    
    # Generate self-signed certificate for development
    openssl req -x509 -newkey rsa:4096 -keyout ssl/private.key -out ssl/certificate.crt -days 365 -nodes -subj "/C=US/ST=State/L=City/O=TigerEx/CN=localhost"
    
    success "SSL certificates generated"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Create monitoring configuration
    mkdir -p monitoring/prometheus
    mkdir -p monitoring/grafana
    
    cat > monitoring/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'tigerex-services'
    static_configs:
      - targets: ['api-gateway:8000', 'trading-engine:8080', 'blockchain-integration-service:8100']
EOF

    success "Monitoring setup completed"
}

# Create backup script
create_backup_script() {
    log "Creating backup script..."
    
    cat > scripts/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/var/backups/tigerex"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker exec tigerex-postgres pg_dump -U postgres tigerex > $BACKUP_DIR/database_$DATE.sql

# Backup Redis
docker exec tigerex-redis redis-cli SAVE
docker cp tigerex-redis:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Backup configuration files
tar -czf $BACKUP_DIR/config_$DATE.tar.gz .env docker-compose.yml nginx.conf

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/*_$DATE.*"
EOF

    chmod +x scripts/backup.sh
    success "Backup script created"
}

# Create health check script
create_health_check() {
    log "Creating health check script..."
    
    cat > scripts/health-check.sh << 'EOF'
#!/bin/bash

SERVICES=(
    "api-gateway:8000"
    "trading-engine:8080"
    "blockchain-integration-service:8100"
    "virtual-liquidity-service:8150"
    "comprehensive-admin-service:8160"
)

echo "TigerEx Health Check - $(date)"
echo "=========================================="

for service in "${SERVICES[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -s -f "http://localhost:$port/health" > /dev/null; then
        echo "✅ $name is healthy"
    else
        echo "❌ $name is down"
    fi
done

# Check database
if docker exec tigerex-postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Database is healthy"
else
    echo "❌ Database is down"
fi

# Check Redis
if docker exec tigerex-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis is down"
fi
EOF

    chmod +x scripts/health-check.sh
    success "Health check script created"
}

# Main setup function
main() {
    log "Starting TigerEx Exchange setup..."
    
    check_requirements
    create_env_file
    setup_database
    install_python_deps
    setup_frontend
    create_systemd_services
    setup_ssl
    setup_monitoring
    create_backup_script
    create_health_check
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p uploads
    mkdir -p backups
    mkdir -p scripts
    
    # Set proper permissions
    chmod +x scripts/*.sh
    
    success "TigerEx Exchange setup completed successfully!"
    
    echo ""
    echo "=============================================="
    echo "TigerEx Exchange Setup Complete!"
    echo "=============================================="
    echo ""
    echo "Next steps:"
    echo "1. Review and update the .env file with your configuration"
    echo "2. Start the services: docker-compose up -d"
    echo "3. Access the admin panel: http://localhost:3001"
    echo "4. Access the main frontend: http://localhost:3000"
    echo "5. Run health check: ./scripts/health-check.sh"
    echo ""
    echo "Important URLs:"
    echo "- Admin Dashboard: http://localhost:3001"
    echo "- Trading Interface: http://localhost:3000"
    echo "- API Documentation: http://localhost:8000/docs"
    echo "- Blockchain Integration: http://localhost:8100/docs"
    echo ""
    echo "For support, please contact: support@tigerex.com"
    echo "=============================================="
}

# Run main function
main "$@"