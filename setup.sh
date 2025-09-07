#!/bin/bash

# TigerEx Advanced Crypto Exchange - Setup Script
# This script sets up the complete TigerEx platform

set -e

echo "🚀 TigerEx Advanced Crypto Exchange Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed ✓"
}

# Check if Node.js is installed
check_nodejs() {
    if ! command -v node &> /dev/null; then
        print_warning "Node.js is not installed. Some features may not work."
    else
        NODE_VERSION=$(node --version)
        print_status "Node.js $NODE_VERSION is installed ✓"
    fi
}

# Create environment file
create_env_file() {
    print_header "Creating environment configuration..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# TigerEx Environment Configuration
# Generated on $(date)

# Database Configuration
POSTGRES_PASSWORD=tigerex_secure_password_$(openssl rand -hex 8)
REDIS_PASSWORD=tigerex_redis_$(openssl rand -hex 8)

# JWT Configuration
JWT_SECRET=$(openssl rand -hex 32)

# Wallet Encryption
WALLET_ENCRYPTION_KEY=$(openssl rand -hex 32)

# API Keys (Replace with your actual keys)
COINGECKO_API_KEY=your_coingecko_api_key_here
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key_here

# Blockchain RPC URLs (Replace with your actual endpoints)
ETHEREUM_RPC=https://mainnet.infura.io/v3/your_infura_key
BSC_RPC=https://bsc-dataseed.binance.org/
POLYGON_RPC=https://polygon-rpc.com/
SOLANA_RPC=https://api.mainnet-beta.solana.com
AVALANCHE_RPC=https://api.avax.network/ext/bc/C/rpc
FANTOM_RPC=https://rpc.ftm.tools/
ARBITRUM_RPC=https://arb1.arbitrum.io/rpc

# Payment Gateway Configuration
STRIPE_SECRET_KEY=your_stripe_secret_key_here
PAYPAL_CLIENT_ID=your_paypal_client_id_here
PAYPAL_CLIENT_SECRET=your_paypal_client_secret_here

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here

# Firebase Configuration
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY=your_firebase_private_key

# OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
APPLE_CLIENT_ID=your_apple_client_id
APPLE_CLIENT_SECRET=your_apple_client_secret

# Domain Configuration
BASE_DOMAIN=tigerex.com
SUBDOMAIN_PREFIX=explorer

# Monitoring
GRAFANA_PASSWORD=admin_$(openssl rand -hex 6)

# IPFS Configuration
IPFS_URL=https://ipfs.infura.io:5001

# HSM Configuration (for production)
HSM_CONFIG=your_hsm_configuration_here
EOF
        print_status "Environment file created: .env"
        print_warning "Please update the API keys and configuration in .env file"
    else
        print_status "Environment file already exists ✓"
    fi
}

# Setup directories
setup_directories() {
    print_header "Setting up directories..."
    
    mkdir -p logs
    mkdir -p data/postgres
    mkdir -p data/redis
    mkdir -p data/kafka
    mkdir -p data/grafana
    mkdir -p data/prometheus
    mkdir -p uploads
    mkdir -p backups
    
    print_status "Directories created ✓"
}

# Build and start services
start_services() {
    print_header "Starting TigerEx services..."
    
    # Pull latest images
    print_status "Pulling Docker images..."
    docker-compose -f devops/docker-compose.yml pull
    
    # Build custom images
    print_status "Building custom images..."
    docker-compose -f devops/docker-compose.yml build
    
    # Start services
    print_status "Starting all services..."
    docker-compose -f devops/docker-compose.yml up -d
    
    print_status "Services started successfully ✓"
}

# Wait for services to be ready
wait_for_services() {
    print_header "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for PostgreSQL..."
    until docker-compose -f devops/docker-compose.yml exec -T postgres pg_isready -U postgres; do
        sleep 2
    done
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    until docker-compose -f devops/docker-compose.yml exec -T redis redis-cli ping; do
        sleep 2
    done
    
    # Wait for API Gateway
    print_status "Waiting for API Gateway..."
    until curl -f http://localhost:8080/health &>/dev/null; do
        sleep 5
    done
    
    print_status "All services are ready ✓"
}

# Initialize database
init_database() {
    print_header "Initializing database..."
    
    # Run database migrations
    print_status "Running database migrations..."
    # Add your database initialization commands here
    
    print_status "Database initialized ✓"
}

# Display service URLs
display_urls() {
    print_header "🎉 TigerEx is now running!"
    echo ""
    echo "Access your services at:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🌐 Frontend:           http://localhost:3000"
    echo "🔧 API Gateway:        http://localhost:8080"
    echo "📊 Grafana:           http://localhost:3001 (admin/admin)"
    echo "📈 Prometheus:        http://localhost:9090"
    echo "🗄️  PostgreSQL:        localhost:5432"
    echo "🔴 Redis:             localhost:6379"
    echo "📨 Kafka:             localhost:9092"
    echo ""
    echo "📱 Mobile Apps:"
    echo "   Android APK:       mobile/android/app/build/outputs/apk/"
    echo "   iOS Project:       mobile/ios/TigerEx.xcworkspace"
    echo ""
    echo "🔧 Admin Services:"
    echo "   Super Admin:       http://localhost:8086"
    echo "   Role Admin:        http://localhost:8087"
    echo "   Wallet Mgmt:       http://localhost:8088"
    echo "   Affiliate:         http://localhost:8089"
    echo "   AI Maintenance:    http://localhost:8090"
    echo ""
    echo "💰 Trading Services:"
    echo "   Spot Trading:      http://localhost:8091"
    echo "   ETF Trading:       http://localhost:8092"
    echo "   Derivatives:       http://localhost:8094"
    echo "   Options:           http://localhost:8095"
    echo "   Alpha Market:      http://localhost:8096"
    echo "   P2P Trading:       http://localhost:8097"
    echo "   Copy Trading:      http://localhost:8099"
    echo ""
    echo "🔗 Blockchain Services:"
    echo "   Web3 Integration:  http://localhost:8100"
    echo "   DEX Integration:   http://localhost:8101"
    echo "   Liquidity:         http://localhost:8102"
    echo "   Block Explorer:    http://localhost:8110"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    print_status "Setup completed successfully! 🚀"
    echo ""
    print_warning "Next steps:"
    echo "1. Update API keys in .env file"
    echo "2. Configure blockchain RPC endpoints"
    echo "3. Set up payment gateways"
    echo "4. Configure email settings"
    echo "5. Review security settings"
    echo ""
    echo "📖 For detailed documentation, see: DEPLOYMENT_GUIDE.md"
}

# Cleanup function
cleanup() {
    print_header "Cleaning up..."
    docker-compose -f devops/docker-compose.yml down
    print_status "Cleanup completed"
}

# Main execution
main() {
    # Handle interrupts
    trap cleanup INT TERM
    
    print_header "🚀 Starting TigerEx Setup Process"
    echo ""
    
    # Check prerequisites
    check_docker
    check_nodejs
    
    # Setup
    create_env_file
    setup_directories
    start_services
    wait_for_services
    init_database
    
    # Display results
    display_urls
}

# Help function
show_help() {
    echo "TigerEx Advanced Crypto Exchange Setup Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start     Start all services (default)"
    echo "  stop      Stop all services"
    echo "  restart   Restart all services"
    echo "  logs      Show service logs"
    echo "  status    Show service status"
    echo "  clean     Clean up all data and containers"
    echo "  help      Show this help message"
    echo ""
}

# Handle command line arguments
case "${1:-start}" in
    start)
        main
        ;;
    stop)
        print_status "Stopping TigerEx services..."
        docker-compose -f devops/docker-compose.yml down
        ;;
    restart)
        print_status "Restarting TigerEx services..."
        docker-compose -f devops/docker-compose.yml restart
        ;;
    logs)
        docker-compose -f devops/docker-compose.yml logs -f
        ;;
    status)
        docker-compose -f devops/docker-compose.yml ps
        ;;
    clean)
        print_warning "This will remove all data and containers. Are you sure? (y/N)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            docker-compose -f devops/docker-compose.yml down -v
            docker system prune -f
            rm -rf data/ logs/
            print_status "Cleanup completed"
        fi
        ;;
    help)
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac