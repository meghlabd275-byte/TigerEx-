#!/bin/bash

echo "Creating advanced feature services..."

# Create advanced services
services=(
    "algo-orders-service"
    "block-trading-service"
    "leveraged-tokens-service"
    "liquid-swap-service"
    "social-trading-service"
    "trading-signals-service"
    "crypto-card-service"
    "fiat-gateway-service"
    "sub-accounts-service"
    "vote-to-list-service"
)

for service in "${services[@]}"; do
    echo "Creating $service..."
    mkdir -p "backend/$service/src"
    touch "backend/$service/src/__init__.py"
    echo "✓ Created $service"
done

echo "All advanced services created!"