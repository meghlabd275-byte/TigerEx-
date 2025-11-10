#!/bin/bash

# TigerEx v11.0.0 - Comprehensive Deployment Script
# Deploys all advanced backend services with monitoring and infrastructure

set -e

echo "🚀 Starting TigerEx v11.0.0 Comprehensive Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        cp .env.example .env
        print_warning "Please edit .env file with your configuration before proceeding."
        exit 1
    fi
    
    print_success "Prerequisites check passed!"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs/nginx
    mkdir -p logs/applications
    mkdir -p database/init-scripts
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p nginx/ssl
    mkdir -p redis
    mkdir -p uploads
    mkdir -p reports
    mkdir -p compliance-reports
    mkdir -p kyc-documents
    mkdir -p blockchain-data
    mkdir -l push-notifications
    mkdir -p ai-models
    mkdir -p trading-data
    
    print_success "Directories created!"
}

# Build and start infrastructure services
start_infrastructure() {
    print_status "Starting infrastructure services (PostgreSQL, Redis)..."
    
    docker-compose -f docker-compose.comprehensive.yml up -d postgres redis
    
    # Wait for services to be ready
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Check database connection
    until docker-compose -f docker-compose.comprehensive.yml exec -T postgres pg_isready -U postgres; do
        print_status "Waiting for PostgreSQL..."
        sleep 2
    done
    
    # Check Redis connection
    until docker-compose -f docker-compose.comprehensive.yml exec -T redis redis-cli ping; do
        print_status "Waiting for Redis..."
        sleep 2
    done
    
    print_success "Infrastructure services are ready!"
}

# Create databases
create_databases() {
    print_status "Creating databases for all services..."
    
    databases=(
        "tigerex_portfolio"
        "tigerex_tenants"
        "tigerex_institutional"
        "tigerex_compliance"
        "tigerex_defi"
        "tigerex_mobile"
        "tigerex_ai"
        "tigerex_derivatives"
    )
    
    for db in "${databases[@]}"; do
        docker-compose -f docker-compose.comprehensive.yml exec -T postgres createdb -U postgres $db 2>/dev/null || true
        print_status "Database $db created or already exists"
    done
    
    print_success "All databases created!"
}

# Build and deploy all services
deploy_services() {
    print_status "Building and deploying all services..."
    
    services=(
        "advanced-portfolio-analytics"
        "multi-tenant-architecture"
        "institutional-features"
        "advanced-compliance-tools"
        "cross-chain-defi-integration"
        "enhanced-mobile-features"
        "ai-trading-insights"
        "derivatives-trading"
    )
    
    for service in "${services[@]}"; do
        print_status "Building and deploying $service..."
        docker-compose -f docker-compose.comprehensive.yml up -d --build $service
        
        # Wait for service to be healthy
        print_status "Waiting for $service to be healthy..."
        max_attempts=30
        attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if docker-compose -f docker-compose.comprehensive.yml exec -T $service curl -f http://localhost:8000/api/v1/health 2>/dev/null || \
               docker-compose -f docker-compose.comprehensive.yml exec -T $service curl -f http://localhost:8009/api/v1/health 2>/dev/null || \
               docker-compose -f docker-compose.comprehensive.yml exec -T $service curl -f http://localhost:8010/api/v1/health 2>/dev/null || \
               docker-compose -f docker-compose.comprehensive.yml exec -T $service curl -f http://localhost:8011/api/v1/health 2>/dev/null || \
               docker-compose -f docker-compose.comprehensive.yml exec -T $service curl -f http://localhost:8012/api/v1/health 2>/dev/null || \
               docker-compose -f docker-compose.comprehensive.yml exec -T $service curl -f http://localhost:8013/api/v1/health 2>/dev/null || \
               docker-compose -f docker-compose.comprehensive.yml exec -T $service curl -f http://localhost:8014/api/v1/health 2>/dev/null; then
                print_success "$service is healthy!"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                print_warning "$service health check timed out, but continuing deployment..."
            fi
            
            sleep 2
            ((attempt++))
        done
    done
    
    print_success "All services deployed!"
}

# Deploy monitoring stack
deploy_monitoring() {
    print_status "Deploying monitoring stack..."
    
    # Start monitoring services
    docker-compose -f docker-compose.comprehensive.yml up -d prometheus grafana nginx
    
    print_status "Waiting for monitoring services to be ready..."
    sleep 15
    
    print_success "Monitoring stack deployed!"
}

# Run health checks
run_health_checks() {
    print_status "Running comprehensive health checks..."
    
    services=(
        "advanced-portfolio-analytics:8009"
        "multi-tenant-architecture:8010"
        "institutional-features:8011"
        "advanced-compliance-tools:8012"
        "cross-chain-defi-integration:8013"
        "enhanced-mobile-features:8014"
        "ai-trading-insights:8008"
        "derivatives-trading:8007"
    )
    
    all_healthy=true
    
    for service in "${services[@]}"; do
        service_name=$(echo $service | cut -d':' -f1)
        port=$(echo $service | cut -d':' -f2)
        
        if curl -f http://localhost:$port/api/v1/health > /dev/null 2>&1; then
            print_success "$service_name is healthy"
        else
            print_error "$service_name is not responding"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        print_success "All services are healthy!"
    else
        print_warning "Some services may not be fully ready. Please check logs."
    fi
}

# Display deployment summary
display_summary() {
    print_success "🎉 TigerEx v11.0.0 Comprehensive Deployment Complete!"
    
    echo ""
    echo "📊 Service Endpoints:"
    echo "  • Advanced Portfolio Analytics: http://localhost:8009"
    echo "  • Multi-Tenant Architecture:   http://localhost:8010"
    echo "  • Institutional Features:     http://localhost:8011"
    echo "  • Advanced Compliance Tools:   http://localhost:8012"
    echo "  • Cross-Chain DeFi Integration: http://localhost:8013"
    echo "  • Enhanced Mobile Features:    http://localhost:8014"
    echo "  • AI Trading Insights:         http://localhost:8008"
    echo "  • Derivatives Trading:         http://localhost:8007"
    echo ""
    echo "🔧 Infrastructure:"
    echo "  • PostgreSQL:                  localhost:5432"
    echo "  • Redis:                       localhost:6379"
    echo ""
    echo "📈 Monitoring:"
    echo "  • Prometheus:                  http://localhost:9090"
    echo "  • Grafana:                     http://localhost:3000 (admin/admin)"
    echo "  • Nginx Load Balancer:         http://localhost"
    echo ""
    echo "📝 Useful Commands:"
    echo "  • View logs: docker-compose -f docker-compose.comprehensive.yml logs -f [service-name]"
    echo "  • Stop services: docker-compose -f docker-compose.comprehensive.yml down"
    echo "  • Restart service: docker-compose -f docker-compose.comprehensive.yml restart [service-name]"
    echo ""
    echo "🔒 Security Note:"
    echo "  Please ensure all API keys and secrets are properly configured in .env file"
    echo "  Change default passwords before production deployment"
}

# Main deployment flow
main() {
    echo "🐅 TigerEx Trading Platform v11.0.0"
    echo "========================================"
    echo ""
    
    check_prerequisites
    create_directories
    start_infrastructure
    create_databases
    deploy_services
    deploy_monitoring
    run_health_checks
    display_summary
    
    echo ""
    print_success "Deployment completed successfully! 🚀"
}

# Handle script interruption
trap 'print_error "Deployment interrupted!"; exit 1' INT TERM

# Run main function
main "$@"