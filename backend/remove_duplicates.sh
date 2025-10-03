#!/bin/bash

# Remove duplicate services based on consolidation plan
echo "Removing duplicate backend services..."

# Remove basic versions, keep enhanced/complete
rm -rf ai-maintenance
rm -rf blockchain-integration-service
rm -rf notification-service
rm -rf trading-engine
rm -rf white-label-system

# Remove admin-only services (functionality merged into main)
rm -rf copy-trading
rm -rf copy-trading-admin
rm -rf dex-integration-admin
rm -rf etf-trading-admin
rm -rf institutional-services-admin
rm -rf lending-borrowing-admin
rm -rf liquidity-aggregator-admin
rm -rf nft-marketplace-admin
rm -rf options-trading-admin
rm -rf p2p-admin
rm -rf payment-gateway
rm -rf payment-gateway-admin
rm -rf risk-management

echo "Duplicate services removed successfully!"
echo "Services removed: 18"
