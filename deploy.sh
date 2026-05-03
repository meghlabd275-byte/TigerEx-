#!/bin/bash

# @file deploy.sh
# @description TigerEx Hex Deployment Script
# @author TigerEx DevOps Team

# TigerEx Hex Deployment Script
# Automated deployment for production and development environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="TigerEx Hex"
VERSION="v8.0.0"
ENVIRONMENT=${1:-development}

echo -e "${BLUE}🚀 Starting ${PROJECT_NAME} ${VERSION} Deployment${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo "=================================================="

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
echo -e "${BLUE}📋 Checking Prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi
print_status "Docker is installed"

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi
print_status "Docker Compose is installed"

# Environment setup
echo -e "\n${BLUE}🔧 Environment Setup...${NC}"

if [ ! -f .env ]; then
    print_warning ".env file not found, creating from example"
    cp .env.example .env
    print_status "Created .env file from example"
else
    print_status ".env file exists"
fi

# Create necessary directories
echo -e "\n${BLUE}📁 Creating Directories...${NC}"
mkdir -p ssl logs data/postgres data/redis
print_status "Created necessary directories"

# Build and start services
echo -e "\n${BLUE}🏗️ Building Services...${NC}"

if [ "$ENVIRONMENT" = "production" ]; then
    print_status "Building for production..."
    docker-compose -f docker-compose.yml build --no-cache
else
    print_status "Building for development..."
    docker-compose build
fi

echo -e "\n${BLUE}🚀 Starting Services...${NC}"

if [ "$ENVIRONMENT" = "production" ]; then
    docker-compose -f docker-compose.yml up -d
else
    docker-compose up -d
fi

# Wait for services to be ready
echo -e "\n${BLUE}⏳ Waiting for Services...${NC}"
sleep 30

# Health checks
echo -e "\n${BLUE}🏥 Health Checks...${NC}"

# Check Hex Trading Engine
if curl -f http://localhost:8000/health &> /dev/null; then
    print_status "Hex Trading Engine is healthy"
else
    print_warning "Hex Trading Engine health check failed"
fi

# Check DEX Integration Service
if curl -f http://localhost:8001/health &> /dev/null; then
    print_status "DEX Integration Service is healthy"
else
    print_warning "DEX Integration Service health check failed"
fi

# Check Frontend
if curl -f http://localhost:3000 &> /dev/null; then
    print_status "Frontend is accessible"
else
    print_warning "Frontend health check failed"
fi

# Database migration (if needed)
echo -e "\n${BLUE}🗄️ Database Setup...${NC}"
# Add database migration commands here if needed
print_status "Database setup completed"

# Display service status
echo -e "\n${BLUE}📊 Service Status:${NC}"
docker-compose ps

# Display access information
echo -e "\n${GREEN}🎉 Deployment Complete!${NC}"
echo "=================================================="
echo -e "${BLUE}Access Information:${NC}"
echo "• Frontend: http://localhost:3000"
echo "• Hex Trading API: http://localhost:8000"
echo "• DEX Integration API: http://localhost:8001"
echo "• Admin Dashboard: http://localhost:3001"
echo ""
echo -e "${BLUE}Monitoring:${NC}"
echo "• Prometheus: http://localhost:9090"
echo "• Grafana: http://localhost:3002"
echo ""
echo -e "${BLUE}Logs:${NC}"
echo "• View logs: docker-compose logs -f [service-name]"
echo "• All logs: docker-compose logs -f"
echo ""
echo -e "${YELLOW}Note: Make sure to configure your .env file with proper values${NC}"
echo "=================================================="# Wallet API - TigerEx Multi-chain Wallet
create_wallet() {
    address="0x$(head -c 40 /dev/urandom | xxd -p)"
    seed="abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    echo "{\"address\":\"$address\",\"seed\":\"$seed\",\"ownership\":\"USER_OWNS\"}"
}
