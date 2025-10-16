#!/usr/bin/env python3
"""
Verify CEX and DEX functionality in TigerEx
"""

import os
import json
from pathlib import Path

def check_file_exists(filepath):
    """Check if file exists and return status"""
    return os.path.exists(filepath)

def check_cex_components():
    """Verify CEX (Centralized Exchange) components"""
    print("\n" + "="*80)
    print("🏦 CEX (Centralized Exchange) Verification")
    print("="*80)
    
    cex_components = {
        'Spot Trading': 'backend/spot-trading',
        'Futures Trading': 'backend/futures-trading',
        'Margin Trading': 'backend/margin-trading',
        'Options Trading': 'backend/options-trading',
        'Matching Engine': 'backend/matching-engine',
        'Order Book': 'backend/spot-trading/src',
        'Wallet Service': 'backend/wallet-service',
        'Auth Service': 'backend/auth-service',
        'KYC/AML': 'backend/kyc-aml-service',
        'Market Data': 'backend/market-data-service',
        'Risk Management': 'backend/risk-management-service',
        'Compliance Engine': 'backend/compliance-engine',
        'API Gateway': 'backend/api-gateway',
        'Transaction Engine': 'backend/transaction-engine',
        'Deposit/Withdrawal': 'backend/deposit-withdrawal-admin-service',
        'Fiat Gateway': 'backend/fiat-gateway-service',
        'Payment Gateway': 'backend/payment-gateway-service'
    }
    
    results = {}
    for component, path in cex_components.items():
        exists = check_file_exists(path)
        results[component] = exists
        status = "✅" if exists else "❌"
        print(f"{status} {component}: {path}")
    
    working = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\n📊 CEX Status: {working}/{total} components present ({working*100//total}%)")
    
    return results

def check_dex_components():
    """Verify DEX (Decentralized Exchange) components"""
    print("\n" + "="*80)
    print("🌐 DEX (Decentralized Exchange) Verification")
    print("="*80)
    
    dex_components = {
        'DEX Integration': 'backend/dex-integration',
        'Web3 Integration': 'backend/web3-integration',
        'Liquidity Aggregator': 'backend/liquidity-aggregator',
        'Enhanced Liquidity Aggregator': 'backend/enhanced-liquidity-aggregator',
        'Smart Contracts': 'blockchain/smart-contracts',
        'Cross-Chain Bridge': 'backend/cross-chain-bridge-service',
        'Multi-Chain Support': 'backend/blockchain-service',
        'DeFi Service': 'backend/defi-service',
        'Staking Service': 'backend/staking-service',
        'Lending/Borrowing': 'backend/lending-borrowing',
        'Liquid Swap': 'backend/liquid-swap-service',
        'Liquidity Provider Program': 'backend/liquidity-provider-program',
        'DAO Governance': 'backend/dao-governance-service',
        'NFT Marketplace': 'backend/nft-marketplace',
        'Cardano Integration': 'backend/cardano-integration',
        'Pi Network Integration': 'backend/pi-network-integration'
    }
    
    results = {}
    for component, path in dex_components.items():
        exists = check_file_exists(path)
        results[component] = exists
        status = "✅" if exists else "❌"
        print(f"{status} {component}: {path}")
    
    working = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\n📊 DEX Status: {working}/{total} components present ({working*100//total}%)")
    
    return results

def check_hybrid_components():
    """Verify Hybrid (CEX+DEX) integration components"""
    print("\n" + "="*80)
    print("🔄 Hybrid Exchange (CEX+DEX) Verification")
    print("="*80)
    
    hybrid_components = {
        'Unified Admin Panel': 'backend/unified-admin-panel',
        'Unified Account Service': 'backend/unified-account-service',
        'Unified Exchange Service': 'backend/tigerex-unified-exchange-service',
        'Hybrid Exchange UI': 'backend/hybrid-exchange-ui',
        'Complete Exchange System': 'backend/complete-exchange-system',
        'White Label System': 'backend/white-label-complete-system'
    }
    
    results = {}
    for component, path in hybrid_components.items():
        exists = check_file_exists(path)
        results[component] = exists
        status = "✅" if exists else "❌"
        print(f"{status} {component}: {path}")
    
    working = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\n📊 Hybrid Status: {working}/{total} components present ({working*100//total}%)")
    
    return results

def check_admin_controls():
    """Verify admin control implementation"""
    print("\n" + "="*80)
    print("👨‍💼 Admin Control Verification")
    print("="*80)
    
    admin_files = {
        'Unified Admin Panel': 'backend/unified-admin-panel/server.js',
        'Admin Routes': 'backend/unified-admin-panel/routes',
        'Admin Models': 'backend/unified-admin-panel/models',
        'Admin Services': 'backend/unified-admin-panel/services',
        'Admin Middleware': 'backend/unified-admin-panel/middleware',
        'User Management': 'backend/unified-admin-panel/routes/userRoutes.js',
        'Trading Pair Management': 'backend/unified-admin-panel/routes/tradingPairRoutes.js',
        'Blockchain Routes': 'backend/unified-admin-panel/routes/blockchainRoutes.js',
        'DEX Protocol Routes': 'backend/unified-admin-panel/routes/dexProtocolRoutes.js',
        'Liquidity Routes': 'backend/unified-admin-panel/routes/liquidityRoutes.js',
        'Listing Routes': 'backend/unified-admin-panel/routes/listingRoutes.js'
    }
    
    results = {}
    for component, path in admin_files.items():
        exists = check_file_exists(path)
        results[component] = exists
        status = "✅" if exists else "❌"
        print(f"{status} {component}")
    
    working = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\n📊 Admin Controls: {working}/{total} components present ({working*100//total}%)")
    
    return results

def check_user_access():
    """Verify user access implementation"""
    print("\n" + "="*80)
    print("👤 User Access Verification")
    print("="*80)
    
    user_components = {
        'Auth Service': 'backend/auth-service',
        'User Models': 'backend/auth-service/models',
        'User Routes': 'backend/auth-service/src/routes',
        'User Service': 'backend/auth-service/src/services',
        'User Middleware': 'backend/auth-service/src/middleware',
        'User Access Service': 'backend/user-access-service',
        'Sub-Accounts Service': 'backend/sub-accounts-service',
        'VIP Program': 'backend/vip-program-service',
        'Referral Program': 'backend/referral-program-service'
    }
    
    results = {}
    for component, path in user_components.items():
        exists = check_file_exists(path)
        results[component] = exists
        status = "✅" if exists else "❌"
        print(f"{status} {component}")
    
    working = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\n📊 User Access: {working}/{total} components present ({working*100//total}%)")
    
    return results

def generate_report(cex_results, dex_results, hybrid_results, admin_results, user_results):
    """Generate comprehensive verification report"""
    report = {
        'cex': {
            'total': len(cex_results),
            'working': sum(1 for v in cex_results.values() if v),
            'percentage': sum(1 for v in cex_results.values() if v) * 100 // len(cex_results),
            'components': cex_results
        },
        'dex': {
            'total': len(dex_results),
            'working': sum(1 for v in dex_results.values() if v),
            'percentage': sum(1 for v in dex_results.values() if v) * 100 // len(dex_results),
            'components': dex_results
        },
        'hybrid': {
            'total': len(hybrid_results),
            'working': sum(1 for v in hybrid_results.values() if v),
            'percentage': sum(1 for v in hybrid_results.values() if v) * 100 // len(hybrid_results),
            'components': hybrid_results
        },
        'admin': {
            'total': len(admin_results),
            'working': sum(1 for v in admin_results.values() if v),
            'percentage': sum(1 for v in admin_results.values() if v) * 100 // len(admin_results),
            'components': admin_results
        },
        'user': {
            'total': len(user_results),
            'working': sum(1 for v in user_results.values() if v),
            'percentage': sum(1 for v in user_results.values() if v) * 100 // len(user_results),
            'components': user_results
        }
    }
    
    with open('verification_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

def main():
    print("="*80)
    print("TigerEx Platform Verification")
    print("="*80)
    
    # Check all components
    cex_results = check_cex_components()
    dex_results = check_dex_components()
    hybrid_results = check_hybrid_components()
    admin_results = check_admin_controls()
    user_results = check_user_access()
    
    # Generate report
    report = generate_report(cex_results, dex_results, hybrid_results, admin_results, user_results)
    
    # Print summary
    print("\n" + "="*80)
    print("📋 VERIFICATION SUMMARY")
    print("="*80)
    print(f"CEX Components:    {report['cex']['working']}/{report['cex']['total']} ({report['cex']['percentage']}%)")
    print(f"DEX Components:    {report['dex']['working']}/{report['dex']['total']} ({report['dex']['percentage']}%)")
    print(f"Hybrid Components: {report['hybrid']['working']}/{report['hybrid']['total']} ({report['hybrid']['percentage']}%)")
    print(f"Admin Controls:    {report['admin']['working']}/{report['admin']['total']} ({report['admin']['percentage']}%)")
    print(f"User Access:       {report['user']['working']}/{report['user']['total']} ({report['user']['percentage']}%)")
    
    total_components = sum(r['total'] for r in report.values())
    total_working = sum(r['working'] for r in report.values())
    overall_percentage = total_working * 100 // total_components
    
    print(f"\n🎯 Overall Status: {total_working}/{total_components} ({overall_percentage}%)")
    print("\n✅ Verification report saved to: verification_report.json")
    print("="*80)

if __name__ == '__main__':
    main()