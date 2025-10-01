#!/bin/bash

# Script to create directory structure for missing services

echo "Creating missing backend services..."

# Array of missing services
services=(
    "dca-bot-service"
    "grid-trading-bot-service"
    "referral-program-service"
    "earn-service"
    "insurance-fund-service"
    "portfolio-margin-service"
    "martingale-bot-service"
    "dual-investment-service"
    "proof-of-reserves-service"
    "launchpool-service"
)

# Create directory structure for each service
for service in "${services[@]}"; do
    echo "Creating $service..."
    mkdir -p "backend/$service/src"
    
    # Create basic __init__.py
    touch "backend/$service/src/__init__.py"
    
    echo "✓ Created $service"
done

echo "All service directories created successfully!"