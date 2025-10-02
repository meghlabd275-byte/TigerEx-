#!/usr/bin/env python3
"""
Scan all backend services for admin control endpoints and features
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

class AdminControlScanner:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.services = defaultdict(dict)
        self.admin_endpoints = defaultdict(list)
        self.missing_features = defaultdict(list)
        
    def scan_python_service(self, filepath):
        """Scan Python service for admin endpoints"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            service_name = filepath.parent.name
            
            # Look for admin routes
            admin_routes = re.findall(r'@app\.(get|post|put|delete|patch)\(["\']([^"\']*admin[^"\']*)["\']', content, re.IGNORECASE)
            
            # Look for admin decorators
            admin_decorators = re.findall(r'@(admin_required|require_admin|admin_only)', content)
            
            # Look for admin functions
            admin_functions = re.findall(r'def\s+(admin_\w+|.*_admin)\s*\(', content)
            
            # Check for CRUD operations
            has_create = bool(re.search(r'(create|add|insert).*admin', content, re.IGNORECASE))
            has_read = bool(re.search(r'(get|list|fetch|read).*admin', content, re.IGNORECASE))
            has_update = bool(re.search(r'(update|modify|edit).*admin', content, re.IGNORECASE))
            has_delete = bool(re.search(r'(delete|remove).*admin', content, re.IGNORECASE))
            
            return {
                'service': service_name,
                'file': str(filepath.relative_to(self.root_dir)),
                'admin_routes': admin_routes,
                'admin_decorators': admin_decorators,
                'admin_functions': admin_functions,
                'crud': {
                    'create': has_create,
                    'read': has_read,
                    'update': has_update,
                    'delete': has_delete
                },
                'has_admin_control': len(admin_routes) > 0 or len(admin_decorators) > 0 or len(admin_functions) > 0
            }
        except Exception as e:
            return None
    
    def scan_javascript_service(self, filepath):
        """Scan JavaScript/Node.js service for admin endpoints"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            service_name = filepath.parent.name
            
            # Look for admin routes
            admin_routes = re.findall(r'(router|app)\.(get|post|put|delete|patch)\(["\']([^"\']*admin[^"\']*)["\']', content, re.IGNORECASE)
            
            # Look for admin middleware
            admin_middleware = re.findall(r'(adminAuth|requireAdmin|isAdmin)', content)
            
            # Look for admin functions
            admin_functions = re.findall(r'(const|function|async)\s+(admin\w+|.*Admin)\s*[=\(]', content)
            
            return {
                'service': service_name,
                'file': str(filepath.relative_to(self.root_dir)),
                'admin_routes': admin_routes,
                'admin_middleware': admin_middleware,
                'admin_functions': admin_functions,
                'has_admin_control': len(admin_routes) > 0 or len(admin_middleware) > 0 or len(admin_functions) > 0
            }
        except Exception as e:
            return None
    
    def scan_all_services(self):
        """Scan all backend services"""
        print("Scanning all backend services for admin control features...")
        
        # Scan Python services
        python_files = list(self.root_dir.glob('backend/*/main.py')) + \
                      list(self.root_dir.glob('backend/*/src/main.py'))
        
        for filepath in python_files:
            result = self.scan_python_service(filepath)
            if result:
                service_name = result['service']
                self.services[service_name] = result
                if result['has_admin_control']:
                    self.admin_endpoints[service_name] = result['admin_routes']
        
        # Scan JavaScript services
        js_files = list(self.root_dir.glob('backend/*/main.js')) + \
                  list(self.root_dir.glob('backend/*/src/main.js'))
        
        for filepath in js_files:
            result = self.scan_javascript_service(filepath)
            if result:
                service_name = result['service']
                self.services[service_name] = result
                if result['has_admin_control']:
                    self.admin_endpoints[service_name] = result['admin_routes']
        
        print(f"\nScanned {len(self.services)} services")
        print(f"Found {len(self.admin_endpoints)} services with admin control")
    
    def identify_missing_features(self):
        """Identify services missing admin control"""
        print("\nIdentifying services missing admin control features...")
        
        required_admin_services = [
            'user-management-admin-service',
            'token-listing-admin',
            'trading-pair-admin',
            'liquidity-pool-admin',
            'deposit-withdrawal-admin-service',
            'blockchain-integration-admin',
            'iou-token-admin',
            'virtual-liquidity-admin',
            'system-configuration-service',
            'comprehensive-admin-service',
            'kyc-aml-admin',
            'compliance-admin',
            'fee-management-admin',
            'announcement-admin',
            'promotion-admin',
            'referral-admin',
            'api-key-admin',
            'security-admin'
        ]
        
        for service in required_admin_services:
            if service not in self.services:
                self.missing_features[service] = ['Service not found']
            elif not self.services[service].get('has_admin_control'):
                self.missing_features[service] = ['Missing admin control endpoints']
        
        print(f"Found {len(self.missing_features)} services with missing admin features")
    
    def generate_report(self):
        """Generate comprehensive report"""
        report = {
            'summary': {
                'total_services': len(self.services),
                'services_with_admin': len(self.admin_endpoints),
                'services_missing_admin': len(self.missing_features),
                'admin_coverage': f"{(len(self.admin_endpoints) / max(len(self.services), 1) * 100):.1f}%"
            },
            'services': dict(self.services),
            'admin_endpoints': dict(self.admin_endpoints),
            'missing_features': dict(self.missing_features)
        }
        
        return report
    
    def print_summary(self):
        """Print summary to console"""
        print("\n" + "="*80)
        print("ADMIN CONTROL SCAN SUMMARY")
        print("="*80)
        print(f"\nTotal Services Scanned: {len(self.services)}")
        print(f"Services with Admin Control: {len(self.admin_endpoints)}")
        print(f"Services Missing Admin Control: {len(self.missing_features)}")
        
        if self.missing_features:
            print("\n" + "-"*80)
            print("SERVICES MISSING ADMIN CONTROL:")
            print("-"*80)
            for service, issues in self.missing_features.items():
                print(f"\n❌ {service}")
                for issue in issues:
                    print(f"   - {issue}")

def main():
    scanner = AdminControlScanner('.')
    scanner.scan_all_services()
    scanner.identify_missing_features()
    
    report = scanner.generate_report()
    
    # Save report
    with open('admin_control_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    scanner.print_summary()
    
    print(f"\n\nDetailed report saved to: admin_control_report.json")
    
    return report

if __name__ == '__main__':
    main()