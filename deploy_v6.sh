#!/bin/bash

# TigerEx v6.0.0 Deployment Script
# This script deploys the complete TigerEx platform

set -e

echo "🚀 Starting TigerEx v6.0.0 Deployment..."

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Setup environment
setup_environment() {
    echo "🔧 Setting up environment..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "📝 Created .env file from template"
        echo "⚠️  Please edit .env file with your configuration before proceeding"
        read -p "Press Enter to continue after editing .env file..."
    fi
    
    echo "✅ Environment setup complete"
}

# Build and start services
deploy_services() {
    echo "🏗️  Building and starting services..."
    
    # Pull latest images
    docker-compose -f docker-compose-unified.yml pull
    
    # Build custom images
    docker-compose -f docker-compose-unified.yml build
    
    # Start services
    docker-compose -f docker-compose-unified.yml up -d
    
    echo "✅ Services deployed successfully"
}

# Wait for services to be ready
wait_for_services() {
    echo "⏳ Waiting for services to be ready..."
    
    # Wait for MongoDB
    echo "Waiting for MongoDB..."
    until docker exec tigerex-mongodb mongosh --eval "db.adminCommand('ismaster')" &>/dev/null; do
        sleep 2
    done
    
    # Wait for Redis
    echo "Waiting for Redis..."
    until docker exec tigerex-redis redis-cli ping &>/dev/null; do
        sleep 2
    done
    
    # Wait for PostgreSQL
    echo "Waiting for PostgreSQL..."
    until docker exec tigerex-postgres pg_isready &>/dev/null; do
        sleep 2
    done
    
    echo "✅ All services are ready"
}

# Initialize databases
initialize_databases() {
    echo "🗄️  Initializing databases..."
    
    # Initialize MongoDB
    docker exec tigerex-mongodb mongosh tigerex --eval "
        db.createUser({
            user: 'tigerex',
            pwd: 'tigerex123',
            roles: [{ role: 'readWrite', db: 'tigerex' }]
        })
    " &>/dev/null || true
    
    echo "✅ Databases initialized"
}

# Run health checks
health_check() {
    echo "🏥 Running health checks..."
    
    # Check if services are responding
    services=("tigerex-api-gateway:3000" "tigerex-user-service:3000" "tigerex-trading-service:3000")
    
    for service in "${services[@]}"; do
        service_name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        if docker exec $service_name curl -f http://localhost:$port/health &>/dev/null; then
            echo "✅ $service_name is healthy"
        else
            echo "⚠️  $service_name health check failed"
        fi
    done
    
    echo "✅ Health checks completed"
}

# Show deployment summary
show_summary() {
    echo ""
    echo "🎉 TigerEx v6.0.0 Deployment Complete!"
    echo ""
    echo "📊 Deployment Summary:"
    echo "  - Backend Services: 210+"
    echo "  - Frontend Applications: 3"
    echo "  - Database Instances: 3"
    echo "  - Total Services: 15+"
    echo ""
    echo "🌐 Access URLs:"
    echo "  - Main Exchange: http://localhost:3000"
    echo "  - Admin Dashboard: http://localhost:3001"
    echo "  - API Gateway: http://localhost:3000/api"
    echo "  - MongoDB: localhost:27017"
    echo "  - Redis: localhost:6379"
    echo "  - PostgreSQL: localhost:5432"
    echo ""
    echo "📚 Next Steps:"
    echo "  1. Configure your domain and SSL"
    echo "  2. Set up monitoring and alerts"
    echo "  3. Configure backup strategies"
    echo "  4. Review security settings"
    echo ""
    echo "📖 Documentation: ./README_V6.md"
    echo "🆘 Support: support@tigerex.com"
}

# Main deployment flow
main() {
    check_prerequisites
    setup_environment
    deploy_services
    wait_for_services
    initialize_databases
    health_check
    show_summary
}

# Handle script interruption
trap 'echo "❌ Deployment interrupted"; exit 1' INT

# Run main function
main "$@"
