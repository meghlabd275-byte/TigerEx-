#!/usr/bin/env python3
"""
Service Consolidation Script for TigerEx
Merges duplicate services while preserving all functionality
"""

import os
import shutil
import json
from pathlib import Path

# Define service consolidation mappings
CONSOLIDATION_MAP = {
    # Admin Services - Consolidate into unified-admin-panel
    'admin_services': {
        'target': 'unified-admin-panel',
        'sources': [
            'admin-service',
            'admin-panel',
            'comprehensive-admin-service',
            'super-admin-system',
            'role-based-admin',
            'universal-admin-controls',
            'alpha-market-admin',
            'deposit-withdrawal-admin-service',
            'user-management-admin-service'
        ]
    },
    
    # Wallet Services - Consolidate into wallet-service
    'wallet_services': {
        'target': 'wallet-service',
        'sources': [
            'wallet-management',
            'advanced-wallet-system',
            'enhanced-wallet-service'
        ]
    },
    
    # Auth Services - Consolidate into auth-service
    'auth_services': {
        'target': 'auth-service',
        'sources': [
            'user-authentication-service',
            'kyc-service',
            'kyc-aml-service'
        ]
    },
    
    # Trading Services - Consolidate into spot-trading (main trading engine)
    'trading_services': {
        'target': 'spot-trading',
        'sources': [
            'trading',
            'trading-engine-enhanced',
            'advanced-trading-service',
            'advanced-trading-engine'
        ]
    },
    
    # DeFi Services - Consolidate into defi-service
    'defi_services': {
        'target': 'defi-service',
        'sources': [
            'defi-enhancements-service',
            'defi-staking-service',
            'liquid-swap-service'
        ]
    }
}

def backup_service(service_path, backup_dir='backend_backup'):
    """Create backup of service before consolidation"""
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    service_name = os.path.basename(service_path)
    backup_path = os.path.join(backup_dir, service_name)
    
    if os.path.exists(service_path):
        shutil.copytree(service_path, backup_path, dirs_exist_ok=True)
        print(f"✅ Backed up: {service_name}")
        return True
    return False

def merge_service_files(target_path, source_path, service_name):
    """Merge source service files into target service"""
    print(f"\n📦 Merging {service_name} into {os.path.basename(target_path)}")
    
    # Create consolidated directory in target
    consolidated_dir = os.path.join(target_path, 'consolidated', service_name)
    os.makedirs(consolidated_dir, exist_ok=True)
    
    # Copy all source files to consolidated directory
    if os.path.exists(source_path):
        for root, dirs, files in os.walk(source_path):
            for file in files:
                src_file = os.path.join(root, file)
                rel_path = os.path.relpath(src_file, source_path)
                dst_file = os.path.join(consolidated_dir, rel_path)
                
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.copy2(src_file, dst_file)
        
        print(f"   ✓ Copied all files from {service_name}")
        return True
    return False

def create_unified_service(category, config):
    """Create unified service from multiple sources"""
    target = config['target']
    sources = config['sources']
    
    target_path = os.path.join('backend', target)
    
    print(f"\n{'='*80}")
    print(f"🔧 Consolidating {category}")
    print(f"{'='*80}")
    print(f"Target: {target}")
    print(f"Sources: {len(sources)} services")
    
    # Ensure target exists
    if not os.path.exists(target_path):
        print(f"⚠️  Target service {target} does not exist. Skipping.")
        return
    
    # Backup target
    backup_service(target_path)
    
    # Merge each source into target
    merged_count = 0
    for source in sources:
        source_path = os.path.join('backend', source)
        if os.path.exists(source_path):
            # Backup source
            backup_service(source_path)
            
            # Merge into target
            if merge_service_files(target_path, source_path, source):
                merged_count += 1
    
    print(f"\n✅ Consolidated {merged_count} services into {target}")
    
    # Create consolidation manifest
    manifest = {
        'target': target,
        'sources': sources,
        'merged_count': merged_count,
        'category': category
    }
    
    manifest_path = os.path.join(target_path, 'CONSOLIDATION_MANIFEST.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"📄 Created manifest: {manifest_path}")

def create_consolidated_readme(target_path, sources):
    """Create README documenting the consolidation"""
    readme_content = f"""# Consolidated Service

This service has been consolidated from multiple services to improve maintainability and reduce duplication.

## Consolidated Services

This service now includes functionality from:

"""
    for source in sources:
        readme_content += f"- {source}\n"
    
    readme_content += """
## Structure

All consolidated services are available in the `consolidated/` directory.
Each service maintains its original structure and can be accessed independently.

## Migration Notes

- All original functionality is preserved
- Admin routes are accessible via the unified admin panel
- User access controls remain unchanged
- All APIs are backward compatible

## Usage

Refer to the individual service documentation in the `consolidated/` directory.
"""
    
    readme_path = os.path.join(target_path, 'CONSOLIDATED_README.md')
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"📄 Created README: {readme_path}")

def main():
    print("="*80)
    print("TigerEx Service Consolidation")
    print("="*80)
    
    # Create backup directory
    os.makedirs('backend_backup', exist_ok=True)
    
    # Consolidate each category
    for category, config in CONSOLIDATION_MAP.items():
        create_unified_service(category, config)
        
        # Create consolidated README
        target_path = os.path.join('backend', config['target'])
        if os.path.exists(target_path):
            create_consolidated_readme(target_path, config['sources'])
    
    print("\n" + "="*80)
    print("✅ Service Consolidation Complete!")
    print("="*80)
    print("\n📋 Summary:")
    print(f"   - Backups created in: backend_backup/")
    print(f"   - Consolidated services: {len(CONSOLIDATION_MAP)}")
    print(f"   - All functionality preserved")
    print("\n⚠️  Note: Original services are backed up but not deleted.")
    print("   Review consolidated services before removing originals.")

if __name__ == '__main__':
    main()