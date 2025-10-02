#!/bin/bash

# TigerEx Admin Features Verification Script
# This script verifies that all admin features are properly set up

echo "=========================================="
echo "TigerEx Admin Features Verification"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check database migrations
echo "1. Checking Database Migrations..."
if [ -f "backend/database/migrations/2025_03_03_000035_create_liquidity_and_virtual_assets.sql" ]; then
    echo -e "${GREEN}✓${NC} Liquidity and virtual assets migration found"
else
    echo -e "${RED}✗${NC} Liquidity and virtual assets migration NOT found"
fi

if [ -f "backend/database/migrations/2025_03_03_000036_insert_default_virtual_reserves.sql" ]; then
    echo -e "${GREEN}✓${NC} Default virtual reserves migration found"
else
    echo -e "${RED}✗${NC} Default virtual reserves migration NOT found"
fi

echo ""

# Check services
echo "2. Checking Services..."
if [ -d "backend/virtual-liquidity-service" ]; then
    echo -e "${GREEN}✓${NC} Virtual Liquidity Service directory found"
    if [ -f "backend/virtual-liquidity-service/src/main.py" ]; then
        echo -e "${GREEN}✓${NC} Virtual Liquidity Service main.py found"
    else
        echo -e "${RED}✗${NC} Virtual Liquidity Service main.py NOT found"
    fi
else
    echo -e "${RED}✗${NC} Virtual Liquidity Service directory NOT found"
fi

if [ -d "backend/comprehensive-admin-service" ]; then
    echo -e "${GREEN}✓${NC} Comprehensive Admin Service directory found"
    if [ -f "backend/comprehensive-admin-service/src/main.py" ]; then
        echo -e "${GREEN}✓${NC} Comprehensive Admin Service main.py found"
    else
        echo -e "${RED}✗${NC} Comprehensive Admin Service main.py NOT found"
    fi
else
    echo -e "${RED}✗${NC} Comprehensive Admin Service directory NOT found"
fi

echo ""

# Check documentation
echo "3. Checking Documentation..."
if [ -f "ADMIN_FEATURES_IMPLEMENTATION.md" ]; then
    echo -e "${GREEN}✓${NC} Implementation guide found"
else
    echo -e "${RED}✗${NC} Implementation guide NOT found"
fi

if [ -f "QUICK_START_ADMIN.md" ]; then
    echo -e "${GREEN}✓${NC} Quick start guide found"
else
    echo -e "${RED}✗${NC} Quick start guide NOT found"
fi

if [ -f "IMPLEMENTATION_SUMMARY.md" ]; then
    echo -e "${GREEN}✓${NC} Implementation summary found"
else
    echo -e "${RED}✗${NC} Implementation summary NOT found"
fi

echo ""

# Check Docker configuration
echo "4. Checking Docker Configuration..."
if grep -q "virtual-liquidity-service" docker-compose.yml; then
    echo -e "${GREEN}✓${NC} Virtual Liquidity Service in docker-compose.yml"
else
    echo -e "${RED}✗${NC} Virtual Liquidity Service NOT in docker-compose.yml"
fi

if grep -q "comprehensive-admin-service" docker-compose.yml; then
    echo -e "${GREEN}✓${NC} Comprehensive Admin Service in docker-compose.yml"
else
    echo -e "${RED}✗${NC} Comprehensive Admin Service NOT in docker-compose.yml"
fi

echo ""

# Check if services are running (optional)
echo "5. Checking Running Services (optional)..."
if curl -s http://localhost:8150/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Virtual Liquidity Service is running on port 8150"
else
    echo -e "${YELLOW}⚠${NC} Virtual Liquidity Service is NOT running (this is OK if not started yet)"
fi

if curl -s http://localhost:8160/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Comprehensive Admin Service is running on port 8160"
else
    echo -e "${YELLOW}⚠${NC} Comprehensive Admin Service is NOT running (this is OK if not started yet)"
fi

echo ""
echo "=========================================="
echo "Verification Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Run database migrations:"
echo "   cd backend/database"
echo "   psql -U postgres -d tigerex -f migrations/2025_03_03_000035_create_liquidity_and_virtual_assets.sql"
echo "   psql -U postgres -d tigerex -f migrations/2025_03_03_000036_insert_default_virtual_reserves.sql"
echo ""
echo "2. Start services:"
echo "   docker-compose up -d virtual-liquidity-service comprehensive-admin-service"
echo ""
echo "3. Verify services:"
echo "   curl http://localhost:8150/health"
echo "   curl http://localhost:8160/health"
echo ""
echo "4. Read documentation:"
echo "   - QUICK_START_ADMIN.md for quick start"
echo "   - ADMIN_FEATURES_IMPLEMENTATION.md for complete guide"
echo "   - IMPLEMENTATION_SUMMARY.md for overview"
echo ""