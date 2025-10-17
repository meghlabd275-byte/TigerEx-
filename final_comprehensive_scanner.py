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
Final Comprehensive Scanner for TigerEx v3.0.0
Complete verification and gap analysis
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set
import subprocess

VERSION = "3.0.0"

class FinalComprehensiveScanner:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.backend_path = self.base_path / "backend"
        self.results = {
            "total_services": 0,
            "services_scanned": 0,
            "services_with_admin": 0,
            "services_with_rbac": 0,
            "outdated_services": [],
            "missing_admin_features": {},
            "version_mismatches": [],
            "incomplete_admin_controls": [],
            "frontend_gaps": {},
            "user_feature_gaps": {}
        }
        
        # Major exchange features for comparison
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
    
    def scan_service_comprehensively(self, service_path: Path) -> Dict:
        """Comprehensive scan of a single service"""
        service_info = {
            "name": service_path.name,
            "has_admin": False,
            "has_rbac": False,
            "version": "unknown",
            "admin_features": [],
            "missing_features": [],
            "outdated_code": False,
            "frontend_status": "missing",
            "user_features": [],
            "issues": []
        }
        
        try:
            # Scan all files in service
            for file_path in service_path.rglob("*"):
                if file_path.is_file():
                    content = ""
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                    except:
                        continue
                    
                    # Check for admin features
                    if self.detect_admin_features(content):
                        service_info["has_admin"] = True
                    
                    # Check for RBAC
                    if self.detect_rbac(content):
                        service_info["has_rbac"] = True
                    
                    # Check version
                    version = self.extract_version(content)
                    if version != "unknown":
                        service_info["version"] = version
                    
                    # Check for outdated code
                    if self.detect_outdated_code(content):
                        service_info["outdated_code"] = True
                    
                    # Extract admin features
                    features = self.extract_admin_features(content)
                    service_info["admin_features"].extend(features)
                    
                    # Extract user features
                    user_features = self.extract_user_features(content)
                    service_info["user_features"].extend(user_features)
            
            # Remove duplicates
            service_info["admin_features"] = list(set(service_info["admin_features"]))
            service_info["user_features"] = list(set(service_info["user_features"]))
            
            # Check for missing features
            service_info["missing_features"] = self.identify_missing_features(service_info["admin_features"])
            
            # Check frontend status
            service_info["frontend_status"] = self.check_frontend_status(service_path)
            
            return service_info
            
        except Exception as e:
            return {"name": service_path.name, "error": str(e)}
    
    def detect_admin_features(self, content: str) -> bool:
        """Detect if content has admin features"""
        admin_patterns = [
            r'@.*admin|/admin/|admin_only|require_admin|admin_router',
            r'AdminUser|AdminAction|AdminResponse|AdminRouter',
            r'Permission\.|UserRole\.|require_permission|require_role'
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in admin_patterns)
    
    def detect_rbac(self, content: str) -> bool:
        """Detect if content has RBAC"""
        rbac_patterns = [
            r'role.*based|@role|check_role|has_role|permission|authorize',
            r'UserRole|ROLE_|PERMISSION_',
            r'ROLE_PERMISSIONS|require_permission|require_role'
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in rbac_patterns)
    
    def extract_version(self, content: str) -> str:
        """Extract version from content"""
        version_patterns = [
            r'version\s*=\s*["\']([0-9.]+)["\']',
            r'VERSION\s*=\s*["\']([0-9.]+)["\']',
            r'__version__\s*=\s*["\']([0-9.]+)["\']',
            r'"version":\s*"([0-9.]+)"',
            r'const VERSION\s*=\s*["\']([0-9.]+)["\']'
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        return "unknown"
    
    def detect_outdated_code(self, content: str) -> bool:
        """Detect outdated code patterns"""
        outdated_patterns = [
            r'version\s*=\s*["\']2\.[0-9]+["\']',
            r'VERSION\s*=\s*["\']2\.[0-9]+["\']',
            r'__version__\s*=\s*["\']2\.[0-9]+["\']',
            r'"version":\s*"2\.[0-9]+"',
            r'const VERSION\s*=\s*["\']2\.[0-9]+["\']'
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in outdated_patterns)
    
    def extract_admin_features(self, content: str) -> List[str]:
        """Extract admin features from content"""
        features = []
        
        feature_patterns = {
            "user_management": [r'user.*manage|create_user|delete_user|update_user|list_users'],
            "kyc_approval": [r'kyc.*approv|approve.*kyc|kyc.*verif'],
            "withdrawal_approval": [r'withdrawal.*approv|approve.*withdrawal'],
            "trading_pair_management": [r'trading.*pair.*manage|pair.*manage'],
            "fee_management": [r'fee.*manage|set.*fee|update.*fee'],
            "liquidity_management": [r'liquidity.*manage|manage.*liquidity'],
            "risk_management": [r'risk.*manage|risk.*param|risk.*control'],
            "compliance_monitoring": [r'compliance.*monitor|aml.*monitor'],
            "transaction_monitoring": [r'transaction.*monitor|monitor.*transaction'],
            "system_configuration": [r'system.*config|platform.*config'],
            "api_key_management": [r'api.*key.*manage|manage.*api.*key'],
            "security_settings": [r'security.*setting|security.*config'],
            "announcement_management": [r'announcement.*manage|manage.*announcement'],
            "promotion_management": [r'promotion.*manage|manage.*promotion'],
            "vip_tier_management": [r'vip.*manage|tier.*manage'],
            "staking_pool_management": [r'staking.*pool.*manage|pool.*manage'],
            "launchpad_management": [r'launchpad.*manage|manage.*launchpad'],
            "nft_management": [r'nft.*manage|manage.*nft'],
            "p2p_dispute_resolution": [r'p2p.*dispute|dispute.*resolution'],
            "customer_support_tools": [r'support.*tool|customer.*support'],
            "analytics_dashboard": [r'analytics.*dashboard|dashboard.*analytics'],
            "audit_logs": [r'audit.*log|admin.*log'],
            "backup_management": [r'backup.*manage|manage.*backup'],
            "disaster_recovery": [r'disaster.*recovery|emergency.*recovery']
        }
        
        for feature, patterns in feature_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    features.append(feature)
                    break
        
        return features
    
    def extract_user_features(self, content: str) -> List[str]:
        """Extract user/trader features from content"""
        features = []
        
        user_feature_patterns = {
            "spot_trading": [r'spot.*trade|trade.*spot'],
            "futures_trading": [r'future.*trade|trade.*future'],
            "margin_trading": [r'margin.*trade|trade.*margin'],
            "options_trading": [r'option.*trade|trade.*option'],
            "staking": [r'staking|stake'],
            "savings": [r'saving|savings'],
            "launchpad": [r'launchpad|launch.*pad'],
            "launchpool": [r'launchpool|launch.*pool'],
            "nft_marketplace": [r'nft.*marketplace|marketplace.*nft'],
            "p2p_trading": [r'p2p.*trade|trade.*p2p'],
            "convert": [r'convert.*service|service.*convert'],
            "otc_trading": [r'otc.*trade|trade.*otc'],
            "copy_trading": [r'copy.*trade|trade.*copy'],
            "trading_bots": [r'trading.*bot|bot.*trading'],
            "earn_products": [r'earn.*product|product.*earn'],
            "liquidity_farming": [r'liquidity.*farm|farm.*liquidity'],
            "dual_investment": [r'dual.*investment|investment.*dual'],
            "auto_invest": [r'auto.*invest|invest.*auto'],
            "gift_cards": [r'gift.*card|card.*gift'],
            "crypto_pay": [r'crypto.*pay|pay.*crypto'],
            "crypto_card": [r'crypto.*card|card.*crypto'],
            "loans": [r'loan|loans'],
            "portfolio_margin": [r'portfolio.*margin|margin.*portfolio']
        }
        
        for feature, patterns in user_feature_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    features.append(feature)
                    break
        
        return features
    
    def identify_missing_features(self, detected_features: List[str]) -> List[str]:
        """Identify missing features compared to major exchanges"""
        all_features = set()
        for exchange_features in self.major_exchange_admin_features.values():
            all_features.update(exchange_features)
        
        detected_set = set(detected_features)
        missing = list(all_features - detected_set)
        return missing
    
    def check_frontend_status(self, service_path: Path) -> str:
        """Check frontend implementation status"""
        # Check for frontend files
        frontend_indicators = [
            "frontend/", "web-app/", "admin-dashboard/", "components/",
            "pages/", "views/", "templates/", "static/"
        ]
        
        for indicator in frontend_indicators:
            if (service_path / indicator).exists():
                return "partial"
        
        return "missing"
    
    def scan_all_services(self):
        """Scan all backend services comprehensively"""
        if not self.backend_path.exists():
            print(f"Backend path not found: {self.backend_path}")
            return
        
        services = [d for d in self.backend_path.iterdir() if d.is_dir()]
        self.results["total_services"] = len(services)
        
        for service_path in services:
            print(f"Scanning: {service_path.name}")
            service_info = self.scan_service_comprehensively(service_path)
            
            self.results["services_scanned"] += 1
            
            if service_info.get("has_admin"):
                self.results["services_with_admin"] += 1
            else:
                self.results["incomplete_admin_controls"].append(service_path.name)
            
            if service_info.get("has_rbac"):
                self.results["services_with_rbac"] += 1
            
            if service_info.get("version") != VERSION:
                self.results["version_mismatches"].append(service_path.name)
            
            if service_info.get("outdated_code"):
                self.results["outdated_services"].append(service_path.name)
            
            if service_info.get("missing_features"):
                self.results["missing_admin_features"][service_path.name] = service_info["missing_features"]
            
            if service_info.get("frontend_status") == "missing":
                self.results["frontend_gaps"][service_path.name] = "missing_frontend"
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        report = {
            "summary": {
                "total_services": self.results["total_services"],
                "services_with_admin": self.results["services_with_admin"],
                "services_with_rbac": self.results["services_with_rbac"],
                "admin_coverage": round((self.results["services_with_admin"] / self.results["total_services"] * 100), 2) if self.results["total_services"] > 0 else 0,
                "rbac_coverage": round((self.results["services_with_rbac"] / self.results["total_services"] * 100), 2) if self.results["total_services"] > 0 else 0
            },
            "issues_found": {
                "outdated_services": self.results["outdated_services"],
                "version_mismatches": self.results["version_mismatches"],
                "incomplete_admin_controls": self.results["incomplete_admin_controls"],
                "missing_admin_features": self.results["missing_admin_features"],
                "frontend_gaps": self.results["frontend_gaps"]
            },
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on scan results"""
        recommendations = []
        
        if self.results["outdated_services"]:
            recommendations.append(f"Update version to {VERSION} in {len(self.results['outdated_services'])} services")
        
        if self.results["incomplete_admin_controls"]:
            recommendations.append(f"Implement admin controls in {len(self.results['incomplete_admin_controls'])} services")
        
        if self.results["missing_admin_features"]:
            recommendations.append(f"Add missing admin features to {len(self.results['missing_admin_features'])} services")
        
        if self.results["frontend_gaps"]:
            recommendations.append(f"Implement frontend admin UI for {len(self.results['frontend_gaps'])} services")
        
        return recommendations

def main():
    scanner = FinalComprehensiveScanner()
    print("=" * 80)
    print("FINAL COMPREHENSIVE SCAN")
    print("=" * 80)
    
    scanner.scan_all_services()
    report = scanner.generate_final_report()
    
    # Save report
    with open("final_comprehensive_scan_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\\n" + "=" * 80)
    print("FINAL SCAN SUMMARY")
    print("=" * 80)
    print(f"Total Services: {report['summary']['total_services']}")
    print(f"Services with Admin: {report['summary']['services_with_admin']}")
    print(f"Services with RBAC: {report['summary']['services_with_rbac']}")
    print(f"Admin Coverage: {report['summary']['admin_coverage']}%")
    print(f"RBAC Coverage: {report['summary']['rbac_coverage']}%")
    
    if report['issues_found']['outdated_services']:
        print(f"\\nOutdated Services: {len(report['issues_found']['outdated_services'])}")
    
    if report['issues_found']['incomplete_admin_controls']:
        print(f"Incomplete Admin Controls: {len(report['issues_found']['incomplete_admin_controls'])}")
    
    if report['recommendations']:
        print("\\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  - {rec}")

if __name__ == "__main__":
    main()