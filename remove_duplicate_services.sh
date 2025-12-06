#!/bin/bash

# Script to remove duplicate services and consolidate functionality
echo "Starting duplicate services removal and consolidation..."

# Remove duplicate admin services (keeping unified-admin-panel as main)
echo "Removing duplicate admin services..."
rm -rf backend/enhanced-admin-control-system
rm -rf backend/unified-admin-control
rm -rf backend/unified-admin-control-system
rm -rf backend/super-admin-system
rm -rf backend/universal-admin-controls
rm -rf backend/tiger-admin-service
rm -rf backend/comprehensive-trading-admin
rm -rf backend/exchange-admin-control

# Remove duplicate trading engines (keeping trading-engine as main)
echo "Removing duplicate trading engines..."
rm -rf backend/advanced-trading-engine
rm -rf backend/high-speed-trading-engine
rm -rf backend/hex-trading-engine
rm -rf backend/trading-engine-enhanced

# Remove duplicate liquidity services (keeping liquidity-aggregator as main)
echo "Removing duplicate liquidity services..."
rm -rf backend/enhanced-liquidity-aggregator
rm -rf backend/multi-exchange-liquidity-service
rm -rf backend/virtual-liquidity-service
rm -rf backend/own-liquidity-system
rm -rf backend/own-liquidity-system-complete
rm -rf backend/liquidity-enhancement

# Remove duplicate blockchain services (keeping blockchain-service as main)
echo "Removing duplicate blockchain services..."
rm -rf backend/blockchain-integration
rm -rf backend/blockchain-integration-service
rm -rf backend/blockchain-integration-complete

# Remove duplicate wallet services (keeping wallet-management as main)
echo "Removing duplicate wallet services..."
rm -rf backend/advanced-wallet-system
rm -rf backend/multisig-wallet-service
rm -rf backend/tiger-wallet-service

# Remove duplicate copy trading services (keeping copy-trading-service as main)
echo "Removing duplicate copy trading services..."
rm -rf backend/copy-trading
rm -rf backend/copy-trading-admin
rm -rf backend/social-trading-platform

# Remove duplicate notification services (keeping notification-service as main)
echo "Removing duplicate notification services..."
rm -rf backend/notification-service-enhanced

# Remove duplicate analytics services (keeping analytics-service as main)
echo "Removing duplicate analytics services..."
rm -rf backend/analytics-dashboard-service

# Remove duplicate DeFi services (keeping defi-service as main)
echo "Removing duplicate DeFi services..."
rm -rf backend/defi-enhancements-service
rm -rf backend/cross-chain-defi-integration
rm -rf backend/cross-chain-dex-aggregator-enhanced
rm -rf backend/crosschain-dex-aggregator

# Remove duplicate trading services (keeping spot-trading as main)
echo "Removing duplicate trading services..."
rm -rf backend/advanced-trading-service

# Remove duplicate risk management services (keeping risk-management as main)
echo "Removing duplicate risk management services..."
rm -rf backend/advanced-risk-management-service

# Remove duplicate institutional services (keeping institutional-services as main)
echo "Removing duplicate institutional services..."
rm -rf backend/institutional-features-service
rm -rf backend/institutional-features
rm -rf backend/institutional-prime-brokerage

echo "Duplicate services removal completed!"
echo "Consolidated services preserved:"
echo "- unified-admin-panel"
echo "- trading-engine"
echo "- liquidity-aggregator"
echo "- blockchain-service"
echo "- wallet-management"
echo "- copy-trading-service"
echo "- notification-service"
echo "- analytics-service"
echo "- defi-service"
echo "- spot-trading"
echo "- risk-management"
echo "- institutional-services"