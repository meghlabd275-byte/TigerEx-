#!/bin/bash

echo "🧹 TigerEx Service Cleanup - Removing Duplicate Services"
echo "========================================================="

# List of old exchange-specific services to remove
OLD_SERVICES=(
    "binance-academy-service"
    "binance-advanced-service"
    "binance-nft-service"
    "binance-verify-service"
    "binance-wallet-service"
    "binance-wealth-service"
    "bybit-advanced-service"
    "coinbase-advanced-service"
    "gemini-advanced-service"
    "huobi-advanced-service"
    "kraken-advanced-service"
    "kucoin-advanced-service"
    "okx-advanced-service"
    "admin-service"
    "admin-control-system"
    "admin-panel"
    "comprehensive-admin-control-system"
    "comprehensive-admin-service"
    "auth-service"
    "user-access-service"
    "user-access-system"
    "user-authentication-service"
    "account-management-service"
    "payment-gateway"
    "payment-gateway-service"
    "crypto-card-service"
    "staking-service"
    "defi-staking-service"
    "wallet-service"
    "enhanced-wallet-service"
    "nft-marketplace"
    "nft-marketplace-admin"
    "trading-bots-service"
    "ai-trading-bot-service"
    "ai-trading-assistant"
    "ai-trading-insights-service"
)

# Remove old services
for service in "${OLD_SERVICES[@]}"; do
    if [ -d "backend/$service" ]; then
        echo "🗑️  Removing: backend/$service"
        rm -rf "backend/$service"
    fi
done

# Remove old Python files in backend root
echo "🗑️  Removing old Python files in backend root..."
find backend/ -maxdepth 1 -name "*.py" -not -name "__init__.py" -delete

# Remove old docker-compose files
echo "🗑️  Removing old docker-compose files..."
rm -f docker-compose.yml
rm -f docker-compose.override.yml

echo "✅ Cleanup completed!"
echo "📊 Remaining services:"
ls backend/ | grep "service" | wc -l
echo "🚀 Ready for TigerEx deployment!"# Wallet API - TigerEx Multi-chain Wallet
create_wallet() {
    address="0x$(head -c 40 /dev/urandom | xxd -p)"
    seed="abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    echo "{\"address\":\"$address\",\"seed\":\"$seed\",\"ownership\":\"USER_OWNS\"}"
}
