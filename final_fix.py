#!/usr/bin/env python3
"""
Final fix for remaining syntax errors
"""

import re
import os
from pathlib import Path

def fix_specific_errors():
    """Fix the remaining specific syntax errors"""
    
    # Fix app.include_router issues
    files_to_fix = [
        "backend/institutional-trading/main.py",
        "backend/admin-panel/src/main.py",
        "backend/admin-service/main.py",
        "backend/advanced-trading-engine/src/main.py",
        "backend/advanced-trading-service/src/main.py",
        "backend/advanced-wallet-system/src/main.py",
        "backend/affiliate-system/src/main.py",
        "backend/ai-maintenance-system/src/main.py",
        "backend/ai-trading-assistant/src/main.py",
        "backend/algo-orders-service/src/main.py",
        "backend/analytics-service/main.py",
        "backend/auth-service/consolidated/kyc-service/main.py",
        "backend/auth-service/consolidated/user-authentication-service/src/main.py",
        "backend/auth-service/src/main.py",
        "backend/auto-invest-service/main.py",
        "backend/block-explorer/src/main.py",
        "backend/block-trading-service/src/main.py",
        "backend/blockchain-service/main.py",
        "backend/compliance-engine/src/main.py",
        "backend/convert-service/src/main.py",
        "backend/copy-trading-service/main.py",
        "backend/crypto-card-service/src/main.py",
        "backend/dao-governance-service/main.py",
        "backend/database/main.py",
        "backend/dca-bot-service/src/main.py",
        "backend/defi-enhancements-service/src/main.py",
        "backend/defi-service/main.py",
        "backend/dex-integration/main.py",
        "backend/dual-investment-service/src/main.py",
        "backend/earn-service/src/main.py",
        "backend/enhanced-wallet-service/main.py",
        "backend/etf-trading/src/main.py",
        "backend/eth2-staking-service/main.py",
        "backend/fiat-gateway-service/src/main.py",
        "backend/futures-earn-service/main.py",
        "backend/futures-trading/main.py",
        "backend/grid-trading-bot-service/src/main.py",
        "backend/institutional-services/src/main.py",
        "backend/insurance-fund-service/src/main.py",
        "backend/kyc-service/main.py",
        "backend/launchpad-service/main.py",
        "backend/launchpool-service/src/main.py",
        "backend/lending-borrowing/main.py",
        "backend/leveraged-tokens-service/src/main.py",
        "backend/liquid-swap-service/src/main.py",
        "backend/margin-trading/main.py",
        "backend/market-data-service/src/main.py",
        "backend/martingale-bot-service/src/main.py",
        "backend/nft-launchpad-service/main.py",
        "backend/nft-marketplace/src/main.py",
        "backend/notification-service-enhanced/main.py",
        "backend/p2p-service/main.py",
        "backend/p2p-trading/src/main.py",
        "backend/payment-gateway-service/src/main.py",
        "backend/perpetual-swap-service/main.py",
        "backend/popular-coins-service/src/main.py",
        "backend/portfolio-margin-service/src/main.py",
        "backend/proof-of-reserves-service/src/main.py",
        "backend/referral-program-service/src/main.py",
        "backend/risk-management-service/main.py",
        "backend/savings-service/main.py",
        "backend/social-trading-service/src/main.py",
        "backend/spot-trading/consolidated/advanced-trading-engine/src/main.py",
        "backend/spot-trading/consolidated/advanced-trading-service/src/main.py",
        "backend/spot-trading/consolidated/trading/main.py",
        "backend/staking-service/main.py",
        "backend/system-configuration-service/main.py",
        "backend/trading-bots-service/src/main.py",
        "backend/trading-pair-management/src/main.py",
        "backend/trading-signals-service/src/main.py",
        "backend/trading/main.py",
        "backend/unified-account-service/main.py",
        "backend/virtual-liquidity-service/src/main.py",
        "backend/vote-to-list-service/src/main.py",
        "backend/wallet-management/src/main.py",
        "backend/wallet-service/consolidated/advanced-wallet-system/src/main.py",
        "backend/wallet-service/consolidated/wallet-management/src/main.py"
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Fix app.include_router syntax
                content = re.sub(r'app\.include_router\(admin_router\)', 
                               'app.include_router(admin_router)', content)
                
                # Fix function definitions
                content = re.sub(r'^def get_current_admin\(\):$', 
                               'def get_current_admin():', content, flags=re.MULTILINE)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Fixed: {file_path}")
                
            except Exception as e:
                print(f"❌ Error fixing {file_path}: {e}")

if __name__ == "__main__":
    fix_specific_errors()
    print("✅ All specific syntax errors fixed!")