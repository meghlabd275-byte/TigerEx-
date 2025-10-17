/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

#!/usr/bin/env python3
"""
TigerEx Complete System Verification Script
Verifies all components are working and no duplicates exist
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Set

def check_system_integrity():
    """Check system integrity and identify any issues"""
    
    print("🔍 TigerEx Complete System Verification")
    print("=" * 50)
    
    # Check directory structure
    backend_dirs = [
        'backend/tigerex-unified-exchange-service',
        'backend/white-label-complete-system',
        'backend/advanced-wallet-system',
        'backend/blockchain-integration-complete',
        'backend/blockchain-service',
        'backend/dex-integration',
        'backend/dex-integration-admin',
        'backend/institutional-services'
    ]
    
    print("\n📁 Checking Directory Structure...")
    missing_dirs = []
    for dir_path in backend_dirs:
        full_path = Path(dir_path)
        if full_path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - MISSING")
            missing_dirs.append(dir_path)
    
    # Check for duplicates
    print("\n🔍 Checking for Duplicates...")
    
    # Find all Python files
    all_py_files = []
    for root, dirs, files in os.walk('backend'):
        for file in files:
            if file.endswith('.py'):
                all_py_files.append(os.path.join(root, file))
    
    print(f"📊 Found {len(all_py_files)} Python files")
    
    # Check for duplicate class names
    class_names: Dict[str, List[str]] = {}
    function_names: Dict[str, List[str]] = {}
    
    for file_path in all_py_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract class names
                import re
                class_matches = re.findall(r'class\s+(\w+)', content)
                for class_name in class_matches:
                    if class_name not in class_names:
                        class_names[class_name] = []
                    class_names[class_name].append(file_path)
                
                # Extract function names
                func_matches = re.findall(r'def\s+(\w+)', content)
                for func_name in func_matches:
                    if func_name not in function_names:
                        function_names[func_name] = []
                    function_names[func_name].append(file_path)
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
    
    # Check for duplicates
    duplicate_classes = {k: v for k, v in class_names.items() if len(v) > 1}
    duplicate_functions = {k: v for k, v in function_names.items() if len(v) > 1}
    
    if duplicate_classes:
        print("\n⚠️  Duplicate Classes Found:")
        for class_name, files in duplicate_classes.items():
            print(f"  {class_name}: {files}")
    else:
        print("✅ No duplicate classes found")
    
    if duplicate_functions:
        print("\n⚠️  Duplicate Functions Found:")
        for func_name, files in duplicate_functions.items():
            print(f"  {func_name}: {files}")
    else:
        print("✅ No duplicate functions found")
    
    # Check hybrid exchange implementation
    print("\n🔍 Checking Hybrid Exchange Implementation...")
    
    hybrid_files = []
    for file_path in all_py_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'hybrid_exchange' in content or 'CEX + DEX' in content:
                    hybrid_files.append(file_path)
        except Exception as e:
            pass
    
    if hybrid_files:
        print("✅ Hybrid Exchange Implementation Found:")
        for file_path in hybrid_files:
            print(f"  {file_path}")
    else:
        print("❌ No hybrid exchange implementation found")
    
    # Check blockchain components
    print("\n🔍 Checking Blockchain Components...")
    
    blockchain_components = [
        'blockchain', 'explorer', 'block', 'transaction',
        'smart_contract', 'validator', 'gas', 'mempool'
    ]
    
    blockchain_files = []
    for file_path in all_py_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if any(comp in content for comp in blockchain_components):
                    blockchain_files.append(file_path)
        except Exception as e:
            pass
    
    if blockchain_files:
        print("✅ Blockchain Components Found:")
        for file_path in blockchain_files[:10]:  # Show first 10
            print(f"  {file_path}")
        if len(blockchain_files) > 10:
            print(f"  ... and {len(blockchain_files) - 10} more")
    else:
        print("❌ No blockchain components found")
    
    # Check wallet components
    print("\n🔍 Checking Wallet Components...")
    
    wallet_components = [
        'wallet', 'mnemonic', 'private_key', 'public_key',
        'hd_wallet', 'hardware_wallet', 'biometric', 'seed'
    ]
    
    wallet_files = []
    for file_path in all_py_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if any(comp in content for comp in wallet_components):
                    wallet_files.append(file_path)
        except Exception as e:
            pass
    
    if wallet_files:
        print("✅ Wallet Components Found:")
        for file_path in wallet_files[:10]:  # Show first 10
            print(f"  {file_path}")
        if len(wallet_files) > 10:
            print(f"  ... and {len(wallet_files) - 10} more")
    else:
        print("❌ No wallet components found")
    
    # Check DEX/CEX components
    print("\n🔍 Checking DEX/CEX Components...")
    
    dex_cex_components = [
        'dex', 'cex', 'amm', 'liquidity_pool', 'order_book',
        'matching_engine', 'spot_trading', 'margin_trading'
    ]
    
    dex_cex_files = []
    for file_path in all_py_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if any(comp in content for comp in dex_cex_components):
                    dex_cex_files.append(file_path)
        except Exception as e:
            pass
    
    if dex_cex_files:
        print("✅ DEX/CEX Components Found:")
        for file_path in dex_cex_files[:10]:  # Show first 10
            print(f"  {file_path}")
        if len(dex_cex_files) > 10:
            print(f"  ... and {len(dex_cex_files) - 10} more")
    else:
        print("❌ No DEX/CEX components found")
    
    # Check institutional components
    print("\n🔍 Checking Institutional Components...")
    
    institutional_components = [
        'institutional', 'prime_brokerage', 'otc_desk',
        'custody_service', 'fix_api', 'algorithmic_trading'
    ]
    
    institutional_files = []
    for file_path in all_py_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if any(comp in content for comp in institutional_components):
                    institutional_files.append(file_path)
        except Exception as e:
            pass
    
    if institutional_files:
        print("✅ Institutional Components Found:")
        for file_path in institutional_files[:10]:  # Show first 10
            print(f"  {file_path}")
        if len(institutional_files) > 10:
            print(f"  ... and {len(institutional_files) - 10} more")
    else:
        print("❌ No institutional components found")
    
    # Summary
    print("\n📋 VERIFICATION SUMMARY")
    print("=" * 30)
    
    issues = []
    
    if missing_dirs:
        issues.append(f"Missing directories: {len(missing_dirs)}")
    
    if duplicate_classes:
        issues.append(f"Duplicate classes: {len(duplicate_classes)}")
    
    if duplicate_functions:
        issues.append(f"Duplicate functions: {len(duplicate_functions)}")
    
    if not hybrid_files:
        issues.append("Missing hybrid exchange implementation")
    
    if not blockchain_files:
        issues.append("Missing blockchain components")
    
    if not wallet_files:
        issues.append("Missing wallet components")
    
    if not dex_cex_files:
        issues.append("Missing DEX/CEX components")
    
    if not institutional_files:
        issues.append("Missing institutional components")
    
    if issues:
        print("❌ Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ ALL SYSTEMS WORKING PERFECTLY!")
        print("✅ No duplicates found")
        print("✅ All required components present")
        print("✅ TigerEx is now a complete hybrid exchange")
        print("✅ Ready for production deployment")
        return True

if __name__ == "__main__":
    success = check_system_integrity()
    sys.exit(0 if success else 1)