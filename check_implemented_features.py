#!/usr/bin/env python3
"""
Check which competitor features are already implemented in TigerEx
"""

import json
from pathlib import Path

# Load competitor features
with open("competitor_features.json", "r") as f:
    competitor_data = json.load(f)

# Map of service directories to features they implement
SERVICE_FEATURE_MAP = {
    # Trading Services
    "spot-trading": ["Spot Trading"],
    "futures-trading": ["Futures Trading"],
    "options-trading": ["Options Trading"],
    "margin-trading": ["Margin Trading"],
    "grid-trading-bot-service": ["Grid Trading Bot"],
    "dca-bot-service": ["DCA Bot"],
    "martingale-bot-service": ["Martingale Bot"],
    "algo-orders-service": ["Algo Orders", "TWAP", "Iceberg Orders"],
    "copy-trading": ["Copy Trading"],
    "copy-trading-service": ["Copy Trading"],
    "social-trading-service": ["Social Trading"],
    "trading-signals-service": ["Trading Signals"],
    "convert-service": ["Convert"],
    "leveraged-tokens-service": ["Leveraged Tokens"],
    "liquid-swap-service": ["Liquid Swap"],
    "portfolio-margin-service": ["Portfolio Margin"],
    "block-trading-service": ["Block Trading"],
    "etf-trading": ["ETF Trading"],
    
    # Earn Services
    "staking-service": ["Staking", "Flexible Savings", "Locked Savings"],
    "earn-service": ["Flexible Savings", "Locked Savings"],
    "launchpad-service": ["Launchpad"],
    "launchpool-service": ["Launchpool"],
    "dual-investment-service": ["Dual Investment"],
    "lending-borrowing": ["Lending"],
    
    # NFT Services
    "nft-marketplace": ["NFT Marketplace"],
    
    # Payment Services
    "payment-gateway": ["Fiat Gateway"],
    "payment-gateway-service": ["Fiat Gateway"],
    "crypto-card-service": ["Crypto Card"],
    "fiat-gateway-service": ["Fiat Gateway"],
    
    # P2P Services
    "p2p-trading": ["P2P Trading"],
    "p2p-service": ["P2P Trading"],
    
    # VIP & Referral
    "vip-program-service": ["VIP Program"],
    "referral-program-service": ["Referral Program"],
    "affiliate-system": ["Affiliate Program"],
    
    # Institutional
    "institutional-services": ["Institutional Trading", "OTC Trading"],
    "institutional-trading": ["Institutional Trading"],
    
    # Other Services
    "sub-accounts-service": ["Sub-Accounts"],
    "vote-to-list-service": ["Vote to List"],
    "proof-of-reserves-service": ["Proof of Reserves"],
    "insurance-fund-service": ["Insurance Fund"],
    
    # DeFi Services
    "dex-integration": ["DEX"],
    "web3-integration": ["Web3 Wallet"],
    "defi-enhancements-service": ["DeFi Earn"],
}

def check_implemented_features():
    """Check which features are implemented"""
    
    backend_path = Path("backend")
    existing_services = set()
    
    if backend_path.exists():
        for service_dir in backend_path.iterdir():
            if service_dir.is_dir():
                existing_services.add(service_dir.name)
    
    # Determine implemented features
    implemented_features = set()
    for service, features in SERVICE_FEATURE_MAP.items():
        if service in existing_services:
            implemented_features.update(features)
    
    # Get all competitor features
    all_features = set(competitor_data["feature_count"].keys())
    
    # Calculate missing features
    missing_features = all_features - implemented_features
    
    # Categorize by priority
    high_priority = set(competitor_data["high_priority"])
    medium_priority = set(competitor_data["medium_priority"])
    low_priority = set(competitor_data["low_priority"])
    
    missing_high = missing_features & high_priority
    missing_medium = missing_features & medium_priority
    missing_low = missing_features & low_priority
    
    print("=" * 80)
    print("TIGEREX FEATURE IMPLEMENTATION STATUS")
    print("=" * 80)
    
    print(f"\nTotal Competitor Features: {len(all_features)}")
    print(f"Implemented Features: {len(implemented_features)}")
    print(f"Missing Features: {len(missing_features)}")
    print(f"Implementation Rate: {len(implemented_features)/len(all_features)*100:.1f}%")
    
    print("\n" + "=" * 80)
    print("✅ IMPLEMENTED FEATURES")
    print("=" * 80)
    for feature in sorted(implemented_features):
        count = competitor_data["feature_count"].get(feature, 0)
        print(f"  ✓ {feature} ({count} exchanges)")
    
    print("\n" + "=" * 80)
    print("❌ MISSING HIGH PRIORITY FEATURES")
    print("=" * 80)
    if missing_high:
        for feature in sorted(missing_high):
            count = competitor_data["feature_count"][feature]
            print(f"  ✗ {feature} ({count}/{len(competitor_data['feature_count'])} exchanges)")
    else:
        print("  ✅ All high priority features implemented!")
    
    print("\n" + "=" * 80)
    print("⚠️  MISSING MEDIUM PRIORITY FEATURES")
    print("=" * 80)
    if missing_medium:
        for feature in sorted(missing_medium):
            count = competitor_data["feature_count"][feature]
            print(f"  ✗ {feature} ({count}/{len(competitor_data['feature_count'])} exchanges)")
    else:
        print("  ✅ All medium priority features implemented!")
    
    print("\n" + "=" * 80)
    print("💡 MISSING LOW PRIORITY FEATURES (Sample)")
    print("=" * 80)
    for feature in sorted(missing_low)[:20]:  # Show first 20
        count = competitor_data["feature_count"][feature]
        print(f"  ✗ {feature} ({count}/{len(competitor_data['feature_count'])} exchanges)")
    
    if len(missing_low) > 20:
        print(f"\n  ... and {len(missing_low) - 20} more low priority features")
    
    # Save report
    report = {
        "total_features": len(all_features),
        "implemented": list(implemented_features),
        "missing": list(missing_features),
        "missing_high_priority": list(missing_high),
        "missing_medium_priority": list(missing_medium),
        "missing_low_priority": list(missing_low),
        "implementation_rate": len(implemented_features)/len(all_features)*100
    }
    
    with open("implementation_status.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "=" * 80)
    print("✅ Report saved to: implementation_status.json")
    print("=" * 80)
    
    return report

if __name__ == "__main__":
    check_implemented_features()