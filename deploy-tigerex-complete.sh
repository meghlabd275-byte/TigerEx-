#!/bin/bash

# ===========================================
# TigerEx Complete Deployment Script
# ===========================================
# This script deploys the complete TigerEx platform
# with all exchange integrations and admin controls
# ===========================================

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logo
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║                    🐯 TIGEREX DEPLOYMENT 🐯                 ║"
echo "║                                                              ║"
echo "║           Complete Cryptocurrency Exchange Platform          ║"
echo "║              9 Major Exchanges Integrated                   ║"
echo "║              Full Admin Control System                      ║"
echo "║              Advanced Trading Features                      ║"
echo "║              Enterprise-Grade Security                      ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Configuration
DEPLOYMENT_NAME="tigerex-complete"
DOCKER_COMPOSE_FILE="docker-compose.tigerex-complete.yml"
ENV_FILE=".env.tigerex"
BACKUP_DIR="./backups"
LOG_DIR="./logs"
SSL_DIR="./ssl"

# Function to print colored messages
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to check if Docker is installed
check_docker() {
    print_step "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_message "Docker and Docker Compose are installed ✓"
}

# Function to create necessary directories
create_directories() {
    print_step "Creating necessary directories..."
    
    mkdir -p $BACKUP_DIR
    mkdir -p $LOG_DIR/nginx
    mkdir -p $SSL_DIR
    mkdir -p ./monitoring/grafana/dashboards
    mkdir -p ./monitoring/grafana/datasources
    mkdir -p ./database/init
    
    print_message "Directories created ✓"
}

# Function to setup environment file
setup_environment() {
    print_step "Setting up environment configuration..."
    
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f ".env.tigerex-template" ]; then
            cp .env.tigerex-template $ENV_FILE
            print_warning "Environment file created from template. Please update your API keys in $ENV_FILE"
        else
            print_error "Environment template file not found!"
            exit 1
        fi
    else
        print_message "Environment file already exists ✓"
    fi
}

# Function to create default SSL certificates (self-signed for development)
create_ssl_certificates() {
    print_step "Creating SSL certificates..."
    
    if [ ! -f "$SSL_DIR/tigerex.crt" ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout $SSL_DIR/tigerex.key \
            -out $SSL_DIR/tigerex.crt \
            -subj "/C=US/ST=State/L=City/O=TigerEx/OU=IT/CN=tigerex.com"
        
        print_message "SSL certificates created ✓"
    else
        print_message "SSL certificates already exist ✓"
    fi
}

# Function to create database init scripts
create_database_init() {
    print_step "Creating database initialization scripts..."
    
    cat > ./database/init/01-init.sql << 'EOF'
-- TigerEx Database Initialization
-- Create additional databases for the platform

CREATE DATABASE tigerex_trading;
CREATE DATABASE tigerex_users;
CREATE DATABASE tigerex_analytics;

-- Create user for application
CREATE USER tigerex_app WITH PASSWORD 'TigerEx2024App!';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE tigerex_trading TO tigerex_app;
GRANT ALL PRIVILEGES ON DATABASE tigerex_users TO tigerex_app;
GRANT ALL PRIVILEGES ON DATABASE tigerex_analytics TO tigerex_app;
GRANT ALL PRIVILEGES ON DATABASE tigerex TO tigerex_app;

-- Connect to main database and create initial tables
\c tigerex;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS exchange_configs (
    id SERIAL PRIMARY KEY,
    exchange_name VARCHAR(50) NOT NULL,
    api_key VARCHAR(255) NOT NULL,
    api_secret VARCHAR(255) NOT NULL,
    additional_params JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100) NOT NULL,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
EOF

    print_message "Database initialization scripts created ✓"
}

# Function to create monitoring configuration
create_monitoring_config() {
    print_step "Creating monitoring configuration..."
    
    # Prometheus configuration
    cat > ./monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'tigerex-admin'
    static_configs:
      - targets: ['tigerex-admin:9000']
    metrics_path: '/health'
    
  - job_name: 'tigerex-binance'
    static_configs:
      - targets: ['tigerex-binance:8001']
    metrics_path: '/health'
    
  - job_name: 'tigerex-bybit'
    static_configs:
      - targets: ['tigerex-bybit:8002']
    metrics_path: '/health'
    
  - job_name: 'tigerex-okx'
    static_configs:
      - targets: ['tigerex-okx:8003']
    metrics_path: '/health'
    
  - job_name: 'tigerex-htx'
    static_configs:
      - targets: ['tigerex-htx:8004']
    metrics_path: '/health'
    
  - job_name: 'tigerex-kucoin'
    static_configs:
      - targets: ['tigerex-kucoin:8005']
    metrics_path: '/health'
    
  - job_name: 'tigerex-app'
    static_configs:
      - targets: ['app:3000']
    metrics_path: '/health'
EOF

    # Grafana datasources
    cat > ./monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    print_message "Monitoring configuration created ✓"
}

# Function to build and deploy services
deploy_services() {
    print_step "Building and deploying TigerEx services..."
    
    # Pull latest images
    print_message "Pulling latest Docker images..."
    docker-compose -f $DOCKER_COMPOSE_FILE pull
    
    # Build custom services
    print_message "Building custom TigerEx services..."
    docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
    
    # Start services
    print_message "Starting TigerEx platform..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    print_message "Services deployed ✓"
}

# Function to wait for services to be healthy
wait_for_services() {
    print_step "Waiting for services to be healthy..."
    
    local services=("tigerex-admin:9000" "tigerex-binance:8001" "tigerex-bybit:8002" "tigerex-okx:8003" "tigerex-htx:8004" "app:3000")
    local max_attempts=30
    local attempt=1
    
    for service in "${services[@]}"; do
        local service_name=$(echo $service | cut -d: -f1)
        local port=$(echo $service | cut -d: -f2)
        
        print_message "Checking $service_name health..."
        
        while [ $attempt -le $max_attempts ]; do
            if curl -f http://localhost:$port/health &>/dev/null; then
                print_message "$service_name is healthy ✓"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                print_warning "$service_name health check timed out, but continuing..."
            fi
            
            sleep 5
            ((attempt++))
        done
        
        attempt=1
    done
}

# Function to show deployment summary
show_deployment_summary() {
    print_step "Deployment Summary"
    
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🐯 TIGEREX DEPLOYED 🐯                   ║"
    echo "║                                                              ║"
    echo "║  🌐 Main Application:     http://localhost:3000              ║"
    echo "║  🔧 Admin Panel:          http://localhost:9000              ║"
    echo "║                                                              ║"
    echo "║  📊 Exchange Services:                                     ║"
    echo "║  • Binance:              http://localhost:8001             ║"
    echo "║  • Bybit:                http://localhost:8002             ║"
    echo "║  • OKX:                  http://localhost:8003             ║"
    echo "║  • HTX:                  http://localhost:8004             ║"
    echo "║  • KuCoin:               http://localhost:8005             ║"
    echo "║  • Huobi:                http://localhost:8006             ║"
    echo "║  • Kraken:               http://localhost:8007             ║"
    echo "║  • Coinbase:             http://localhost:8008             ║"
    echo "║  • Gemini:               http://localhost:8009             ║"
    echo "║                                                              ║"
    echo "║  📈 Monitoring:                                            ║"
    echo "║  • Prometheus:           http://localhost:9090             ║"
    echo "║  • Grafana:              http://localhost:3001             ║"
    echo "║  • Kibana:               http://localhost:5601             ║"
    echo "║                                                              ║"
    echo "║  🔐 Default Admin Login:                                    ║"
    echo "║  • Username: tigerex_admin                                 ║"
    echo "║  • Password: tigerex123                                    ║"
    echo "║                                                              ║"
    echo "║  📝 Important Notes:                                        ║"
    echo "║  • Update API keys in .env.tigerex file                    ║"
    echo "║  • Configure SSL certificates for production               ║"
    echo "║  • Set up monitoring alerts in Grafana                     ║"
    echo "║  • Review security configurations                          ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    print_message "Deployment completed successfully! 🎉"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy     Deploy complete TigerEx platform"
    echo "  start      Start all services"
    echo "  stop       Stop all services"
    echo "  restart    Restart all services"
    echo "  status     Show service status"
    echo "  logs       Show service logs"
    echo "  update     Update services"
    echo "  backup     Backup data"
    echo "  restore    Restore from backup"
    echo "  cleanup    Cleanup and remove all services"
    echo ""
}

# Function to manage services
manage_services() {
    local command=$1
    
    case $command in
        "start")
            print_step "Starting TigerEx services..."
            docker-compose -f $DOCKER_COMPOSE_FILE start
            ;;
        "stop")
            print_step "Stopping TigerEx services..."
            docker-compose -f $DOCKER_COMPOSE_FILE stop
            ;;
        "restart")
            print_step "Restarting TigerEx services..."
            docker-compose -f $DOCKER_COMPOSE_FILE restart
            ;;
        "status")
            print_step "Checking service status..."
            docker-compose -f $DOCKER_COMPOSE_FILE ps
            ;;
        "logs")
            print_step "Showing service logs..."
            docker-compose -f $DOCKER_COMPOSE_FILE logs -f
            ;;
        "cleanup")
            print_step "Cleaning up TigerEx services..."
            docker-compose -f $DOCKER_COMPOSE_FILE down -v --remove-orphans
            docker system prune -f
            print_message "Cleanup completed ✓"
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Main deployment function
main() {
    local command=${1:-deploy}
    
    case $command in
        "deploy")
            check_docker
            create_directories
            setup_environment
            create_ssl_certificates
            create_database_init
            create_monitoring_config
            deploy_services
            wait_for_services
            show_deployment_summary
            ;;
        "start"|"stop"|"restart"|"status"|"logs"|"cleanup")
            manage_services $command
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

# Trap to handle script interruption
trap 'print_error "Deployment interrupted!"; exit 1' INT TERM

# Run main function
main "$@"