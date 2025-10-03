import os
import shutil

# Define consolidation plan
consolidation_plan = {
    # Keep enhanced/complete versions, remove basic ones
    'ai-maintenance-system': ['ai-maintenance'],
    'blockchain-integration-complete': ['blockchain-integration-service'],
    'notification-service-enhanced': ['notification-service'],
    'trading-engine-enhanced': ['trading-engine'],
    'white-label-complete-system': ['white-label-system'],
    
    # For admin services, merge into main service
    'copy-trading-service': ['copy-trading', 'copy-trading-admin'],
    'dex-integration': ['dex-integration-admin'],
    'etf-trading': ['etf-trading-admin'],
    'institutional-services': ['institutional-services-admin'],
    'lending-borrowing': ['lending-borrowing-admin'],
    'liquidity-aggregator': ['liquidity-aggregator-admin'],
    'nft-marketplace': ['nft-marketplace-admin'],
    'options-trading': ['options-trading-admin'],
    'p2p-service': ['p2p-admin'],
    'payment-gateway-service': ['payment-gateway', 'payment-gateway-admin'],
    'risk-management-service': ['risk-management'],
}

print("=== CONSOLIDATION PLAN ===\n")
for keep, remove_list in consolidation_plan.items():
    print(f"KEEP: {keep}")
    for remove in remove_list:
        print(f"  REMOVE: {remove}")
    print()

print(f"\nTotal services to keep: {len(consolidation_plan)}")
print(f"Total services to remove: {sum(len(v) for v in consolidation_plan.values())}")
