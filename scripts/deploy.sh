#!/bin/bash

# TigerEx Deployment Script
# This script handles the deployment of the TigerEx platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
PROJECT_NAME="tigerex"
DOCKER_COMPOSE_FILE="docker-compose.yml"
BACKUP_DIR="./backups"
LOG_DIR="./logs"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Check available disk space (minimum 10GB)
    AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
    if [ $AVAILABLE_SPACE -lt 10485760 ]; then
        log_warning "Less than 10GB disk space available. Deployment may fail."
    fi
    
    log_success "System requirements check passed"
}

setup_environment() {
    log_info "Setting up environment for: $ENVIRONMENT"
    
    # Create necessary directories
    mkdir -p $BACKUP_DIR
    mkdir -p $LOG_DIR
    mkdir -p ./data/{postgres,redis,mongodb,influxdb}
    
    # Set environment-specific Docker Compose file
    case $ENVIRONMENT in
        "production")
            DOCKER_COMPOSE_FILE="docker-compose.production.yml"
            ;;
        "staging")
            DOCKER_COMPOSE_FILE="docker-compose.staging.yml"
            ;;
        "development")
            DOCKER_COMPOSE_FILE="docker-compose.yml"
            ;;
        *)
            log_error "Unknown environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
    
    # Copy environment file
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            log_warning "Created .env file from .env.example. Please review and update the configuration."
        else
            log_error ".env.example file not found. Please create environment configuration."
            exit 1
        fi
    fi
    
    log_success "Environment setup completed"
}

backup_database() {
    if [ "$ENVIRONMENT" != "development" ]; then
        log_info "Creating database backup..."
        
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        BACKUP_FILE="$BACKUP_DIR/tigerex_backup_$TIMESTAMP.sql"
        
        # Create PostgreSQL backup
        docker-compose exec -T postgres pg_dump -U tigerex tigerex > $BACKUP_FILE
        
        if [ $? -eq 0 ]; then
            log_success "Database backup created: $BACKUP_FILE"
        else
            log_error "Database backup failed"
            exit 1
        fi
    fi
}

build_services() {
    log_info "Building services..."
    
    # Install dependencies
    log_info "Installing Node.js dependencies..."
    npm run install:all
    
    # Build frontend applications
    log_info "Building frontend applications..."
    npm run build:frontend
    
    # Build backend services
    log_info "Building backend services..."
    npm run build:backend
    
    # Build Docker images
    log_info "Building Docker images..."
    docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
    
    log_success "Services built successfully"
}

deploy_infrastructure() {
    log_info "Deploying infrastructure services..."
    
    # Start database services first
    docker-compose -f $DOCKER_COMPOSE_FILE up -d postgres redis mongodb influxdb
    
    # Wait for databases to be ready
    log_info "Waiting for databases to be ready..."
    sleep 30
    
    # Run database migrations
    log_info "Running database migrations..."
    npm run migrate
    
    # Seed initial data (only for development)
    if [ "$ENVIRONMENT" = "development" ]; then
        log_info "Seeding initial data..."
        npm run seed
    fi
    
    log_success "Infrastructure deployed successfully"
}

deploy_services() {
    log_info "Deploying application services..."
    
    # Start message queue services
    docker-compose -f $DOCKER_COMPOSE_FILE up -d kafka zookeeper rabbitmq
    
    # Wait for message queues to be ready
    sleep 20
    
    # Start backend services
    docker-compose -f $DOCKER_COMPOSE_FILE up -d \
        auth-service \
        trading-engine \
        wallet-service \
        kyc-service \
        notification-service \
        analytics-service \
        admin-service \
        blockchain-service \
        p2p-service \
        copy-trading-service
    
    # Wait for backend services to be ready
    sleep 30
    
    # Start frontend services
    docker-compose -f $DOCKER_COMPOSE_FILE up -d \
        web-app \
        admin-dashboard \
        landing-pages
    
    # Start API gateway
    docker-compose -f $DOCKER_COMPOSE_FILE up -d nginx
    
    # Start monitoring services
    if [ "$ENVIRONMENT" != "development" ]; then
        docker-compose -f $DOCKER_COMPOSE_FILE up -d prometheus grafana
    fi
    
    log_success "Application services deployed successfully"
}

health_check() {
    log_info "Performing health checks..."
    
    # Wait for services to be fully ready
    sleep 60
    
    # Check service health
    SERVICES=(
        "http://localhost:8080/health"
        "http://localhost:3001/health"
        "http://localhost:3002/health"
        "http://localhost:3003/health"
    )
    
    for service in "${SERVICES[@]}"; do
        if curl -f -s $service > /dev/null; then
            log_success "Health check passed: $service"
        else
            log_error "Health check failed: $service"
        fi
    done
    
    # Check database connectivity
    if docker-compose exec -T postgres pg_isready -U tigerex > /dev/null; then
        log_success "PostgreSQL is ready"
    else
        log_error "PostgreSQL is not ready"
    fi
    
    # Check Redis connectivity
    if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
        log_success "Redis is ready"
    else
        log_error "Redis is not ready"
    fi
    
    log_success "Health checks completed"
}

setup_ssl() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Setting up SSL certificates..."
        
        # Create SSL directory
        mkdir -p ./ssl
        
        # Generate self-signed certificate for testing (replace with real certificates)
        if [ ! -f ./ssl/tigerex.crt ]; then
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout ./ssl/tigerex.key \
                -out ./ssl/tigerex.crt \
                -subj "/C=US/ST=State/L=City/O=TigerEx/CN=tigerex.com"
            
            log_warning "Self-signed SSL certificate created. Replace with real certificate for production."
        fi
        
        log_success "SSL setup completed"
    fi
}

setup_monitoring() {
    if [ "$ENVIRONMENT" != "development" ]; then
        log_info "Setting up monitoring and logging..."
        
        # Create monitoring directories
        mkdir -p ./monitoring/{prometheus,grafana,logs}
        
        # Copy monitoring configurations
        if [ -f ./monitoring/prometheus.yml.example ]; then
            cp ./monitoring/prometheus.yml.example ./monitoring/prometheus.yml
        fi
        
        if [ -f ./monitoring/grafana-dashboard.json.example ]; then
            cp ./monitoring/grafana-dashboard.json.example ./monitoring/grafana-dashboard.json
        fi
        
        log_success "Monitoring setup completed"
    fi
}

cleanup() {
    log_info "Cleaning up old resources..."
    
    # Remove unused Docker images
    docker image prune -f
    
    # Remove old backups (keep last 7 days)
    find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
    
    # Remove old logs (keep last 30 days)
    find $LOG_DIR -name "*.log" -mtime +30 -delete
    
    log_success "Cleanup completed"
}

show_deployment_info() {
    log_success "Deployment completed successfully!"
    echo ""
    echo "=== TigerEx Platform Information ==="
    echo "Environment: $ENVIRONMENT"
    echo "Web Application: http://localhost:3000"
    echo "Admin Dashboard: http://localhost:3100"
    echo "Landing Pages: http://localhost:3200"
    echo "API Gateway: http://localhost:8080"
    
    if [ "$ENVIRONMENT" != "development" ]; then
        echo "Monitoring (Grafana): http://localhost:3300"
        echo "Metrics (Prometheus): http://localhost:9090"
    fi
    
    echo ""
    echo "=== Useful Commands ==="
    echo "View logs: docker-compose logs -f [service-name]"
    echo "Stop services: docker-compose down"
    echo "Restart service: docker-compose restart [service-name]"
    echo "Scale service: docker-compose up -d --scale [service-name]=3"
    echo ""
    
    if [ "$ENVIRONMENT" = "development" ]; then
        echo "=== Development Notes ==="
        echo "- Default admin credentials: admin@tigerex.com / admin123"
        echo "- Database is seeded with test data"
        echo "- All services are running in development mode"
        echo ""
    fi
}

# Main deployment flow
main() {
    log_info "Starting TigerEx deployment..."
    log_info "Environment: $ENVIRONMENT"
    
    check_requirements
    setup_environment
    
    if [ "$ENVIRONMENT" != "development" ]; then
        backup_database
    fi
    
    build_services
    setup_ssl
    setup_monitoring
    deploy_infrastructure
    deploy_services
    health_check
    cleanup
    show_deployment_info
    
    log_success "TigerEx deployment completed successfully!"
}

# Handle script interruption
trap 'log_error "Deployment interrupted"; exit 1' INT TERM

# Run main function
main "$@"