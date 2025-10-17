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
Comprehensive duplicate service analyzer for TigerEx
"""

import os
import json
from pathlib import Path
from collections import defaultdict
import hashlib

def get_file_hash(filepath):
    """Calculate MD5 hash of file content"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def analyze_service_structure(backend_path):
    """Analyze backend services for duplicates"""
    services = {}
    duplicates = defaultdict(list)
    
    # Get all service directories
    for item in os.listdir(backend_path):
        service_path = os.path.join(backend_path, item)
        if os.path.isdir(service_path):
            services[item] = {
                'path': service_path,
                'files': [],
                'main_files': [],
                'admin_files': [],
                'has_dockerfile': False,
                'has_requirements': False,
                'language': None
            }
            
            # Analyze service contents
            for root, dirs, files in os.walk(service_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, service_path)
                    services[item]['files'].append(rel_path)
                    
                    # Identify main files
                    if file in ['main.py', 'main.js', 'main.go', 'server.js', 'server.py']:
                        services[item]['main_files'].append(rel_path)
                        if file.endswith('.py'):
                            services[item]['language'] = 'Python'
                        elif file.endswith('.js'):
                            services[item]['language'] = 'JavaScript'
                        elif file.endswith('.go'):
                            services[item]['language'] = 'Go'
                    
                    # Identify admin files
                    if 'admin' in file.lower():
                        services[item]['admin_files'].append(rel_path)
                    
                    # Check for Dockerfile
                    if file == 'Dockerfile':
                        services[item]['has_dockerfile'] = True
                    
                    # Check for requirements
                    if file in ['requirements.txt', 'package.json', 'go.mod']:
                        services[item]['has_requirements'] = True
    
    return services

def find_duplicate_services(services):
    """Find services with similar names or functionality"""
    duplicates = []
    service_names = list(services.keys())
    
    # Group similar services
    groups = defaultdict(list)
    
    for name in service_names:
        # Extract base name (remove suffixes like -service, -admin, etc.)
        base_name = name.replace('-service', '').replace('-admin', '').replace('-system', '')
        base_name = base_name.replace('_service', '').replace('_admin', '').replace('_system', '')
        groups[base_name].append(name)
    
    # Find groups with multiple services
    for base_name, service_list in groups.items():
        if len(service_list) > 1:
            duplicates.append({
                'base_name': base_name,
                'services': service_list,
                'count': len(service_list)
            })
    
    return duplicates

def analyze_admin_services(services):
    """Analyze admin-related services"""
    admin_services = []
    
    for name, info in services.items():
        if 'admin' in name.lower() or len(info['admin_files']) > 0:
            admin_services.append({
                'name': name,
                'admin_files': info['admin_files'],
                'main_files': info['main_files'],
                'language': info['language']
            })
    
    return admin_services

def analyze_trading_services(services):
    """Analyze trading-related services"""
    trading_services = []
    
    for name, info in services.items():
        if any(keyword in name.lower() for keyword in ['trading', 'spot', 'futures', 'margin', 'derivatives', 'options']):
            trading_services.append({
                'name': name,
                'main_files': info['main_files'],
                'language': info['language']
            })
    
    return trading_services

def analyze_wallet_services(services):
    """Analyze wallet-related services"""
    wallet_services = []
    
    for name, info in services.items():
        if 'wallet' in name.lower():
            wallet_services.append({
                'name': name,
                'main_files': info['main_files'],
                'language': info['language']
            })
    
    return wallet_services

def analyze_auth_services(services):
    """Analyze authentication-related services"""
    auth_services = []
    
    for name, info in services.items():
        if any(keyword in name.lower() for keyword in ['auth', 'kyc', 'user-authentication']):
            auth_services.append({
                'name': name,
                'main_files': info['main_files'],
                'language': info['language']
            })
    
    return auth_services

def analyze_defi_services(services):
    """Analyze DeFi-related services"""
    defi_services = []
    
    for name, info in services.items():
        if any(keyword in name.lower() for keyword in ['defi', 'staking', 'lending', 'liquidity', 'swap']):
            defi_services.append({
                'name': name,
                'main_files': info['main_files'],
                'language': info['language']
            })
    
    return defi_services

def main():
    backend_path = 'backend'
    
    print("=" * 80)
    print("TigerEx Duplicate Service Analysis")
    print("=" * 80)
    
    # Analyze services
    services = analyze_service_structure(backend_path)
    
    print(f"\n📊 Total Services Found: {len(services)}")
    print("=" * 80)
    
    # Find duplicate services
    duplicates = find_duplicate_services(services)
    
    print(f"\n🔍 Duplicate Service Groups: {len(duplicates)}")
    print("=" * 80)
    
    for dup in duplicates:
        print(f"\n📦 Base Name: {dup['base_name']}")
        print(f"   Count: {dup['count']}")
        print(f"   Services:")
        for svc in dup['services']:
            lang = services[svc]['language'] or 'Unknown'
            print(f"      - {svc} ({lang})")
    
    # Analyze admin services
    admin_services = analyze_admin_services(services)
    print(f"\n\n👨‍💼 Admin Services: {len(admin_services)}")
    print("=" * 80)
    for svc in admin_services:
        print(f"   - {svc['name']} ({svc['language']})")
        if svc['admin_files']:
            print(f"     Admin files: {len(svc['admin_files'])}")
    
    # Analyze trading services
    trading_services = analyze_trading_services(services)
    print(f"\n\n📈 Trading Services: {len(trading_services)}")
    print("=" * 80)
    for svc in trading_services:
        print(f"   - {svc['name']} ({svc['language']})")
    
    # Analyze wallet services
    wallet_services = analyze_wallet_services(services)
    print(f"\n\n💰 Wallet Services: {len(wallet_services)}")
    print("=" * 80)
    for svc in wallet_services:
        print(f"   - {svc['name']} ({svc['language']})")
    
    # Analyze auth services
    auth_services = analyze_auth_services(services)
    print(f"\n\n🔐 Authentication Services: {len(auth_services)}")
    print("=" * 80)
    for svc in auth_services:
        print(f"   - {svc['name']} ({svc['language']})")
    
    # Analyze DeFi services
    defi_services = analyze_defi_services(services)
    print(f"\n\n🏦 DeFi Services: {len(defi_services)}")
    print("=" * 80)
    for svc in defi_services:
        print(f"   - {svc['name']} ({svc['language']})")
    
    # Save detailed report
    report = {
        'total_services': len(services),
        'duplicate_groups': duplicates,
        'admin_services': admin_services,
        'trading_services': trading_services,
        'wallet_services': wallet_services,
        'auth_services': auth_services,
        'defi_services': defi_services,
        'all_services': {name: {
            'language': info['language'],
            'has_dockerfile': info['has_dockerfile'],
            'has_requirements': info['has_requirements'],
            'file_count': len(info['files'])
        } for name, info in services.items()}
    }
    
    with open('duplicate_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n\n✅ Detailed report saved to: duplicate_analysis_report.json")
    print("=" * 80)

if __name__ == '__main__':
    main()