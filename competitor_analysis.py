#!/usr/bin/env python3
"""
Comprehensive Competitor Feature Analysis
Analyzes features from major crypto exchanges
"""

import json
from collections import defaultdict

# Define competitor features
COMPETITOR_FEATURES = {
    "Binance": {
        "Trading": [
            "Spot Trading", "Margin Trading", "Futures Trading", "Options Trading",
            "Leveraged Tokens", "Auto-Invest", "Convert", "Swap Farming",
            "Liquid Swap", "Dual Investment", "Portfolio Margin", "Grid Trading Bot",
            "DCA Bot", "Rebalancing Bot", "Algo Orders", "TWAP", "Iceberg Orders"
        ],
        "Earn": [
            "Flexible Savings", "Locked Savings", "Staking", "DeFi Staking",
            "ETH 2.0 Staking", "Launchpool", "Liquid Swap", "BNB Vault",
            "Dual Investment", "Auto-Invest"
        ],
        "NFT": [
            "NFT Marketplace", "Mystery Box", "Fan Tokens", "IGO",
            "NFT Staking", "NFT Loan"
        ],
        "Institutional": [
            "VIP Program", "Institutional Trading", "OTC Trading",
            "Block Trading", "Custody Solutions", "Prime Brokerage"
        ],
        "Payment": [
            "Binance Pay", "Crypto Card", "Gift Card", "Merchant Solutions"
        ],
        "Other": [
            "Launchpad", "P2P Trading", "Fiat Gateway", "Referral Program",
            "Sub-Accounts", "API Trading", "Copy Trading", "Social Trading",
            "Trading Signals", "Proof of Reserves", "Insurance Fund",
            "Vote to List", "Binance Labs", "Binance Research"
        ]
    },
    "Bitget": {
        "Trading": [
            "Spot Trading", "Futures Trading", "Copy Trading", "Grid Trading Bot",
            "Martingale Bot", "DCA Bot", "Smart Order", "One-Click Copy"
        ],
        "Earn": [
            "Flexible Savings", "Locked Savings", "Launchpad", "Launchpool",
            "Shark Fin", "Dual Currency"
        ],
        "Social": [
            "Copy Trading", "Elite Traders", "Trading Competition",
            "Social Trading Feed"
        ],
        "Other": [
            "P2P Trading", "Fiat Gateway", "VIP Program", "Referral Program",
            "API Trading", "Sub-Accounts"
        ]
    },
    "Bybit": {
        "Trading": [
            "Spot Trading", "Derivatives Trading", "Options Trading",
            "Copy Trading", "Grid Trading Bot", "DCA Bot", "Martingale Bot"
        ],
        "Earn": [
            "Flexible Savings", "Locked Savings", "Launchpad", "Launchpool",
            "Dual Asset", "Liquidity Mining"
        ],
        "NFT": [
            "NFT Marketplace", "NFT Launchpad", "GrabPic NFT"
        ],
        "Other": [
            "P2P Trading", "Fiat Gateway", "VIP Program", "Affiliate Program",
            "Institutional Services", "API Trading", "Sub-Accounts"
        ]
    },
    "OKX": {
        "Trading": [
            "Spot Trading", "Margin Trading", "Futures Trading", "Options Trading",
            "Perpetual Swap", "Grid Trading Bot", "DCA Bot", "Iceberg Orders",
            "TWAP", "Algo Orders", "Copy Trading"
        ],
        "Earn": [
            "Flexible Savings", "Fixed Savings", "Staking", "DeFi Earn",
            "Dual Investment", "Structured Products", "Jumpstart"
        ],
        "NFT": [
            "NFT Marketplace", "NFT Launchpad", "NFT Aggregator"
        ],
        "DeFi": [
            "DEX", "DeFi Hub", "Multi-Chain Wallet", "Web3 Wallet"
        ],
        "Other": [
            "P2P Trading", "Fiat Gateway", "VIP Program", "Affiliate Program",
            "Block Trading", "API Trading", "Sub-Accounts", "Proof of Reserves"
        ]
    },
    "KuCoin": {
        "Trading": [
            "Spot Trading", "Margin Trading", "Futures Trading",
            "Grid Trading Bot", "DCA Bot", "Infinity Grid", "Smart Rebalance"
        ],
        "Earn": [
            "KuCoin Earn", "Staking", "Lending", "Pool-X", "Soft Staking"
        ],
        "NFT": [
            "NFT Marketplace", "Windvane NFT", "NFT ETF"
        ],
        "Other": [
            "P2P Trading", "Fiat Gateway", "VIP Program", "Referral Program",
            "KuCoin Labs", "API Trading", "Sub-Accounts"
        ]
    },
    "CoinW": {
        "Trading": [
            "Spot Trading", "Futures Trading", "Grid Trading Bot",
            "Copy Trading"
        ],
        "Earn": [
            "Flexible Savings", "Locked Savings", "Launchpad"
        ],
        "Other": [
            "P2P Trading", "Fiat Gateway", "VIP Program", "Referral Program"
        ]
    },
    "MEXC": {
        "Trading": [
            "Spot Trading", "Futures Trading", "ETF Trading",
            "Grid Trading Bot", "Copy Trading"
        ],
        "Earn": [
            "Flexible Savings", "Locked Savings", "Launchpad", "MX DeFi"
        ],
        "Other": [
            "P2P Trading", "Fiat Gateway", "VIP Program", "Referral Program",
            "API Trading", "Sub-Accounts"
        ]
    },
    "BitMart": {
        "Trading": [
            "Spot Trading", "Futures Trading", "Margin Trading",
            "Grid Trading Bot"
        ],
        "Earn": [
            "Flexible Savings", "Locked Savings", "Launchpad"
        ],
        "Other": [
            "P2P Trading", "Fiat Gateway", "VIP Program", "Referral Program"
        ]
    }
}

def analyze_features():
    """Analyze all competitor features"""
    
    # Collect all unique features
    all_features = set()
    feature_count = defaultdict(int)
    
    for exchange, categories in COMPETITOR_FEATURES.items():
        for category, features in categories.items():
            for feature in features:
                all_features.add(feature)
                feature_count[feature] += 1
    
    # Sort by popularity
    sorted_features = sorted(feature_count.items(), key=lambda x: x[1], reverse=True)
    
    print("=" * 80)
    print("COMPETITOR FEATURE ANALYSIS")
    print("=" * 80)
    
    print(f"\nTotal Unique Features: {len(all_features)}")
    print(f"Total Exchanges Analyzed: {len(COMPETITOR_FEATURES)}")
    
    print("\n" + "=" * 80)
    print("TOP FEATURES BY MARKET PRESENCE")
    print("=" * 80)
    
    print("\n🔥 High Priority (Present in 5+ exchanges):")
    high_priority = [f for f, c in sorted_features if c >= 5]
    for feature, count in sorted_features:
        if count >= 5:
            print(f"  ✓ {feature} ({count}/{len(COMPETITOR_FEATURES)} exchanges)")
    
    print(f"\nTotal High Priority Features: {len(high_priority)}")
    
    print("\n⚡ Medium Priority (Present in 3-4 exchanges):")
    medium_priority = [f for f, c in sorted_features if 3 <= c < 5]
    for feature, count in sorted_features:
        if 3 <= count < 5:
            print(f"  ✓ {feature} ({count}/{len(COMPETITOR_FEATURES)} exchanges)")
    
    print(f"\nTotal Medium Priority Features: {len(medium_priority)}")
    
    print("\n💡 Low Priority (Present in 1-2 exchanges):")
    low_priority = [f for f, c in sorted_features if c < 3]
    for feature, count in sorted_features[:20]:  # Show first 20
        if count < 3:
            print(f"  ✓ {feature} ({count}/{len(COMPETITOR_FEATURES)} exchanges)")
    
    print(f"\nTotal Low Priority Features: {len(low_priority)}")
    
    # Categorize features
    print("\n" + "=" * 80)
    print("FEATURES BY CATEGORY")
    print("=" * 80)
    
    categories = defaultdict(set)
    for exchange, cats in COMPETITOR_FEATURES.items():
        for category, features in cats.items():
            for feature in features:
                categories[category].add(feature)
    
    for category in sorted(categories.keys()):
        print(f"\n{category} ({len(categories[category])} features):")
        for feature in sorted(categories[category]):
            count = feature_count[feature]
            print(f"  - {feature} ({count} exchanges)")
    
    # Save report
    report = {
        "total_features": len(all_features),
        "total_exchanges": len(COMPETITOR_FEATURES),
        "high_priority": high_priority,
        "medium_priority": medium_priority,
        "low_priority": low_priority,
        "feature_count": dict(sorted_features),
        "by_category": {cat: list(features) for cat, features in categories.items()}
    }
    
    with open("competitor_features.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "=" * 80)
    print("✅ Report saved to: competitor_features.json")
    print("=" * 80)
    
    return report

if __name__ == "__main__":
    analyze_features()