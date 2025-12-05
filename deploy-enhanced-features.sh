#!/bin/bash

# TigerEx Enhanced Features Deployment Script
# This script deploys all the new advanced features to make TigerEx competitive

set -e

echo "🐅 TigerEx Enhanced Features Deployment"
echo "========================================="

# Configuration
BACKEND_DIR="backend"
SERVICES=(
    "advanced-order-types-service"
    "order-sharing-service" 
    "copy-trading-service"
    "technical-indicators-service"
    "task-center-service"
)

PORTS=(
    "5004"
    "5005"
    "5006"
    "8003"
    "8004"
)

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

# Check if running from correct directory
if [ ! -d "$BACKEND_DIR" ]; then
    print_error "Backend directory not found. Please run this script from the TigerEx root directory."
    exit 1
fi

print_status "Starting deployment of enhanced features..."

# Function to check if a port is in use
is_port_in_use() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to stop existing service on a port
stop_service_on_port() {
    local port=$1
    if is_port_in_use $port; then
        print_warning "Port $port is in use. Stopping existing service..."
        fuser -k $port/tcp 2>/dev/null || true
        sleep 2
    fi
}

# Function to start a service
start_service() {
    local service_name=$1
    local port=$2
    
    print_status "Starting $service_name on port $port..."
    
    cd "$BACKEND_DIR/$service_name"
    
    # Check if requirements.txt exists and install dependencies
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies for $service_name..."
        pip3 install -r requirements.txt
    fi
    
    # Install common dependencies
    pip3 install flask flask-sqlalchemy flask-jwt-extended flask-cors numpy pandas talib
    
    # Set environment variables
    export DATABASE_URL="postgresql://user:password@localhost/tigerex"
    export JWT_SECRET_KEY="tiger-${service_name}-secret-key"
    export PORT=$port
    
    # Start the service in background
    nohup python3 main.py > "../logs/${service_name}.log" 2>&1 &
    
    # Get the PID
    local pid=$!
    echo $pid > "../pids/${service_name}.pid"
    
    # Wait a moment for the service to start
    sleep 3
    
    # Check if service is running
    if is_port_in_use $port; then
        print_success "$service_name started successfully on port $port (PID: $pid)"
    else
        print_error "$service_name failed to start on port $port"
        return 1
    fi
    
    cd - > /dev/null
}

# Function to test service health
test_service_health() {
    local service_name=$1
    local port=$2
    
    print_status "Testing health of $service_name..."
    
    # Try to curl the health endpoint
    if curl -f -s "http://localhost:$port/health" > /dev/null; then
        print_success "$service_name health check passed"
        return 0
    else
        print_error "$service_name health check failed"
        return 1
    fi
}

# Function to create database tables
create_database_tables() {
    local service_name=$1
    local port=$2
    
    print_status "Creating database tables for $service_name..."
    
    cd "$BACKEND_DIR/$service_name"
    
    # Create a simple script to initialize database
    cat > init_db.py << 'EOF'
import sys
import os
sys.path.append('.')
from main import app, db

with app.app_context():
    db.create_all()
    print("Database tables created successfully")
EOF
    
    # Run the initialization
    export DATABASE_URL="postgresql://user:password@localhost/tigerex"
    export JWT_SECRET_KEY="tiger-${service_name}-secret-key"
    python3 init_db.py
    
    # Clean up
    rm init_db.py
    
    cd - > /dev/null
}

# Create necessary directories
mkdir -p "$BACKEND_DIR/logs"
mkdir -p "$BACKEND_DIR/pids"

# Stop any existing services
print_status "Stopping any existing services..."
for i in "${!SERVICES[@]}"; do
    service_name="${SERVICES[$i]}"
    port="${PORTS[$i]}"
    stop_service_on_port $port
done

# Start all services
print_status "Starting all enhanced feature services..."
failed_services=()

for i in "${!SERVICES[@]}"; do
    service_name="${SERVICES[$i]}"
    port="${PORTS[$i]}"
    
    if start_service "$service_name" "$port; then
        # Create database tables
        create_database_tables "$service_name" "$port"
        
        # Test health
        if ! test_service_health "$service_name" "$port"; then
            failed_services+=("$service_name")
        fi
    else
        failed_services+=("$service_name")
    fi
done

# Summary
echo ""
echo "========================================="
echo "🐅 Deployment Summary"
echo "========================================="

if [ ${#failed_services[@]} -eq 0 ]; then
    print_success "All services deployed successfully!"
    echo ""
    echo "📊 Enhanced Features Available:"
    echo "  • Advanced Order Types:     http://localhost:5004"
    echo "  • Order Sharing:            http://localhost:5005"
    echo "  • Copy Trading:             http://localhost:5006"
    echo "  • Technical Indicators:     http://localhost:8003"
    echo "  • Task Center & Rewards:    http://localhost:8004"
    echo ""
    echo "🔗 Integration Examples:"
    echo "  • POST /api/v1/advanced-orders (Chase Limit, Iceberg, TWAP)"
    echo "  • POST /api/v1/orders/share (Share trades with community)"
    echo "  • POST /api/v1/copy-trading/copy (Start copying strategies)"
    echo "  • POST /api/v1/indicators/skdj (SKDJ technical indicator)"
    echo "  • GET  /api/v1/tasks (Available tasks and rewards)"
    echo ""
    print_success "TigerEx is now competitive with Binance, OKX, Bybit, and other top exchanges!"
else
    print_error "Some services failed to deploy:"
    for service in "${failed_services[@]}"; do
        echo "  ❌ $service"
    done
    echo ""
    echo "📋 Check the logs for more details:"
    for service in "${failed_services[@]}"; do
        echo "  • $BACKEND_DIR/logs/${service}.log"
    done
    exit 1
fi

echo ""
print_status "Next steps:"
echo "1. Update your frontend to integrate with the new API endpoints"
echo "2. Test the new features with your trading interface"
echo "3. Configure your database connection in production"
echo "4. Set up proper authentication and authorization"
echo "5. Configure SSL certificates for production deployment"

echo ""
print_success "🎉 TigerEx Enhanced Features Deployment Complete!"