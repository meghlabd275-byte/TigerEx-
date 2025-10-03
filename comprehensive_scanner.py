#!/usr/bin/env python3
"""
Comprehensive scanner for TigerEx platform
- Scans all backend services for admin controls
- Checks for role-based access control (RBAC)
- Compares features with major exchanges
- Identifies missing features
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set

class TigerExScanner:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.backend_path = self.base_path / "backend"
        self.results = {
            "services_scanned": 0,
            "services_with_admin": 0,
            "services_with_rbac": 0,
            "services_without_admin": [],
            "admin_features": {},
            "missing_features": {},
            "version_info": {}
        }
        
        # Major exchange features to compare
        self.major_exchange_admin_features = {
            "binance": [
                "user_management", "kyc_approval", "withdrawal_approval",
                "trading_pair_management", "fee_management", "liquidity_management",
                "risk_management", "compliance_monitoring", "transaction_monitoring",
                "system_configuration", "api_key_management", "security_settings",
                "announcement_management", "promotion_management", "vip_tier_management",
                "staking_pool_management", "launchpad_management", "nft_management",
                "p2p_dispute_resolution", "customer_support_tools", "analytics_dashboard",
                "audit_logs", "backup_management", "disaster_recovery"
            ],
            "bybit": [
                "user_management", "kyc_verification", "withdrawal_control",
                "trading_management", "fee_configuration", "liquidity_control",
                "risk_parameters", "compliance_tools", "transaction_review",
                "system_settings", "api_management", "security_controls",
                "content_management", "marketing_tools", "vip_management",
                "derivatives_management", "copy_trading_oversight", "institutional_services",
                "dispute_management", "support_dashboard", "reporting_tools"
            ],
            "okx": [
                "account_management", "identity_verification", "fund_control",
                "market_management", "fee_structure", "liquidity_provision",
                "risk_control", "regulatory_compliance", "monitoring_system",
                "platform_configuration", "developer_tools", "security_management",
                "announcement_system", "campaign_management", "tier_management",
                "earn_product_management", "trading_bot_oversight", "web3_management",
                "resolution_center", "helpdesk_system", "business_intelligence"
            ]
        }
        
        self.major_exchange_user_features = {
            "binance": [
                "spot_trading", "futures_trading", "margin_trading", "options_trading",
                "staking", "savings", "launchpad", "launchpool", "nft_marketplace",
                "p2p_trading", "convert", "otc_trading", "copy_trading", "trading_bots",
                "earn_products", "liquidity_farming", "dual_investment", "auto_invest",
                "gift_cards", "pay", "card", "loans", "portfolio_margin"
            ],
            "bybit": [
                "spot_trading", "derivatives_trading", "margin_trading", "options_trading",
                "staking", "savings", "launchpad", "nft_marketplace", "copy_trading",
                "trading_bots", "earn_products", "liquidity_mining", "dual_investment",
                "structured_products", "lending", "borrowing", "convert", "otc_desk"
            ],
            "okx": [
                "spot_trading", "futures_trading", "margin_trading", "options_trading",
                "perpetual_swaps", "staking", "earn", "jumpstart", "nft_marketplace",
                "dex", "web3_wallet", "copy_trading", "trading_bots", "structured_products",
                "lending", "borrowing", "convert", "block_trading", "algo_orders"
            ]
        }
    
    def scan_file_for_patterns(self, file_path: Path) -> Dict:
        """Scan a file for admin and RBAC patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            patterns = {
                "admin_routes": len(re.findall(r'@.*admin|/admin/|admin_only|require_admin', content, re.IGNORECASE)),
                "rbac": len(re.findall(r'role.*based|@role|check_role|has_role|permission|authorize', content, re.IGNORECASE)),
                "user_management": len(re.findall(r'user.*manage|create_user|delete_user|update_user|list_users', content, re.IGNORECASE)),
                "kyc": len(re.findall(r'kyc|know.*your.*customer|identity.*verif', content, re.IGNORECASE)),
                "withdrawal_approval": len(re.findall(r'withdrawal.*approv|approve.*withdrawal|pending.*withdrawal', content, re.IGNORECASE)),
                "trading_control": len(re.findall(r'trading.*control|pause.*trading|enable.*trading|trading.*pair.*manage', content, re.IGNORECASE)),
                "fee_management": len(re.findall(r'fee.*manage|set.*fee|update.*fee|fee.*config', content, re.IGNORECASE)),
                "risk_management": len(re.findall(r'risk.*manage|risk.*param|risk.*control|risk.*limit', content, re.IGNORECASE)),
                "audit_logs": len(re.findall(r'audit.*log|activity.*log|admin.*log|action.*log', content, re.IGNORECASE)),
                "system_config": len(re.findall(r'system.*config|platform.*config|settings.*manage', content, re.IGNORECASE)),
                "version": self.extract_version(content)
            }
            
            return patterns
        except Exception as e:
            return {"error": str(e)}
    
    def extract_version(self, content: str) -> str:
        """Extract version information from file content"""
        version_patterns = [
            r'version\s*=\s*["\']([0-9.]+)["\']',
            r'VERSION\s*=\s*["\']([0-9.]+)["\']',
            r'__version__\s*=\s*["\']([0-9.]+)["\']',
            r'"version":\s*"([0-9.]+)"'
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        return "unknown"
    
    def scan_service(self, service_path: Path) -> Dict:
        """Scan a single service directory"""
        service_info = {
            "name": service_path.name,
            "has_admin": False,
            "has_rbac": False,
            "admin_features": [],
            "files_scanned": 0,
            "patterns_found": {}
        }
        
        # Scan all Python, JavaScript, and TypeScript files
        for ext in ['*.py', '*.js', '*.ts', '*.jsx', '*.tsx']:
            for file_path in service_path.rglob(ext):
                service_info["files_scanned"] += 1
                patterns = self.scan_file_for_patterns(file_path)
                
                if patterns.get("admin_routes", 0) > 0:
                    service_info["has_admin"] = True
                
                if patterns.get("rbac", 0) > 0:
                    service_info["has_rbac"] = True
                
                # Aggregate patterns
                for key, value in patterns.items():
                    if key != "error" and key != "version":
                        if key not in service_info["patterns_found"]:
                            service_info["patterns_found"][key] = 0
                        service_info["patterns_found"][key] += value
                    elif key == "version" and value != "unknown":
                        service_info["version"] = value
        
        # Determine admin features present
        for feature, count in service_info["patterns_found"].items():
            if count > 0 and feature not in ["admin_routes", "rbac"]:
                service_info["admin_features"].append(feature)
        
        return service_info
    
    def scan_all_services(self):
        """Scan all backend services"""
        if not self.backend_path.exists():
            print(f"Backend path not found: {self.backend_path}")
            return
        
        services = [d for d in self.backend_path.iterdir() if d.is_dir()]
        
        for service_path in services:
            print(f"Scanning: {service_path.name}")
            service_info = self.scan_service(service_path)
            
            self.results["services_scanned"] += 1
            
            if service_info["has_admin"]:
                self.results["services_with_admin"] += 1
            else:
                self.results["services_without_admin"].append(service_path.name)
            
            if service_info["has_rbac"]:
                self.results["services_with_rbac"] += 1
            
            self.results["admin_features"][service_path.name] = service_info
            
            if "version" in service_info:
                self.results["version_info"][service_path.name] = service_info["version"]
    
    def compare_with_exchanges(self):
        """Compare TigerEx features with major exchanges"""
        # Extract all unique admin features from TigerEx
        tigerex_admin_features = set()
        for service_info in self.results["admin_features"].values():
            tigerex_admin_features.update(service_info.get("admin_features", []))
        
        # Compare with each major exchange
        for exchange, features in self.major_exchange_admin_features.items():
            missing = []
            for feature in features:
                # Check if feature exists in any form
                feature_found = False
                for tigerex_feature in tigerex_admin_features:
                    if feature.replace("_", " ") in tigerex_feature.replace("_", " ") or \
                       tigerex_feature.replace("_", " ") in feature.replace("_", " "):
                        feature_found = True
                        break
                
                if not feature_found:
                    missing.append(feature)
            
            self.results["missing_features"][exchange] = missing
    
    def generate_report(self):
        """Generate comprehensive report"""
        report = {
            "summary": {
                "total_services": self.results["services_scanned"],
                "services_with_admin_controls": self.results["services_with_admin"],
                "services_with_rbac": self.results["services_with_rbac"],
                "services_without_admin": len(self.results["services_without_admin"]),
                "coverage_percentage": round((self.results["services_with_admin"] / self.results["services_scanned"] * 100), 2) if self.results["services_scanned"] > 0 else 0
            },
            "services_without_admin_controls": self.results["services_without_admin"],
            "detailed_service_analysis": self.results["admin_features"],
            "version_information": self.results["version_info"],
            "missing_features_comparison": self.results["missing_features"]
        }
        
        return report
    
    def save_report(self, filename: str = "comprehensive_scan_report.json"):
        """Save report to JSON file"""
        report = self.generate_report()
        output_path = self.base_path / filename
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to: {output_path}")
        return report

def main():
    scanner = TigerExScanner()
    print("Starting comprehensive scan of TigerEx platform...")
    print("=" * 80)
    
    scanner.scan_all_services()
    scanner.compare_with_exchanges()
    report = scanner.save_report()
    
    # Print summary
    print("\n" + "=" * 80)
    print("SCAN SUMMARY")
    print("=" * 80)
    print(f"Total Services Scanned: {report['summary']['total_services']}")
    print(f"Services with Admin Controls: {report['summary']['services_with_admin_controls']}")
    print(f"Services with RBAC: {report['summary']['services_with_rbac']}")
    print(f"Services without Admin: {report['summary']['services_without_admin']}")
    print(f"Admin Coverage: {report['summary']['coverage_percentage']}%")
    
    print("\n" + "=" * 80)
    print("SERVICES WITHOUT ADMIN CONTROLS")
    print("=" * 80)
    for service in report['services_without_admin_controls'][:20]:
        print(f"  - {service}")
    if len(report['services_without_admin_controls']) > 20:
        print(f"  ... and {len(report['services_without_admin_controls']) - 20} more")
    
    print("\n" + "=" * 80)
    print("MISSING FEATURES (vs Major Exchanges)")
    print("=" * 80)
    for exchange, missing in report['missing_features_comparison'].items():
        print(f"\n{exchange.upper()}:")
        for feature in missing[:10]:
            print(f"  - {feature}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")

if __name__ == "__main__":
    main()