#!/bin/bash

# TigerEx Complete Deployment Script
# This script deploys all services including the new market making bot system

set -e

echo "=========================================="
echo "TigerEx Complete Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

print_status "Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Docker Compose is installed"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/mongodb

# Build and start services
print_status "Building and starting services..."

# Start infrastructure services first
print_status "Starting infrastructure services (databases, cache, etc.)..."
docker-compose up -d postgres redis mongodb

# Wait for databases to be ready
print_status "Waiting for databases to be ready..."
sleep 10

# Start backend services
print_status "Starting backend services..."
docker-compose up -d \
    market-making-bot-system \
    comprehensive-data-fetchers \
    security-service \
    api-gateway \
    auth-service \
    trading-engine \
    matching-engine

# Wait for backend services
sleep 5

# Start frontend services
print_status "Starting frontend services..."
docker-compose up -d \
    web-app \
    mobile-app \
    desktop-app

print_status "All services started successfully!"

# Display service status
echo ""
echo "=========================================="
echo "Service Status"
echo "=========================================="
docker-compose ps

# Display access URLs
echo ""
echo "=========================================="
echo "Access URLs"
echo "=========================================="
echo "Web Application: http://localhost:3000"
echo "API Gateway: http://localhost:8000"
echo "Market Making Bot System: http://localhost:8001"
echo "Data Fetchers: http://localhost:8002"
echo "Security Service: http://localhost:8003"
echo "Admin Panel: http://localhost:8004"
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="

# Show logs
print_warning "Showing logs (Ctrl+C to exit)..."
docker-compose logs -f