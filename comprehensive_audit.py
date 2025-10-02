#!/usr/bin/env python3
"""
TigerEx Comprehensive Platform Audit Script
Analyzes all backend services, frontend components, and generates detailed reports
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

class TigerExAuditor:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.backend_path = self.base_path / "backend"
        self.frontend_path = self.base_path / "frontend"
        self.admin_panel_path = self.base_path / "admin-panel"
        self.mobile_path = self.base_path / "mobile"
        self.desktop_path = self.base_path / "desktop"
        
        self.results = {
            "backend_services": {},
            "frontend_components": {},
            "admin_capabilities": {},
            "user_capabilities": {},
            "blockchain_support": {},
            "missing_features": [],
            "statistics": {}
        }
    
    def scan_backend_services(self):
        """Scan all backend services and analyze their capabilities"""
        print("🔍 Scanning backend services...")
        
        if not self.backend_path.exists():
            print("❌ Backend directory not found")
            return
        
        services = {}
        admin_services = []
        
        for service_dir in self.backend_path.iterdir():
            if not service_dir.is_dir() or service_dir.name.startswith('.'):
                continue
            
            service_info = self.analyze_service(service_dir)
            if service_info:
                services[service_dir.name] = service_info
                
                if 'admin' in service_dir.name.lower():
                    admin_services.append(service_dir.name)
        
        self.results["backend_services"] = services
        self.results["statistics"]["total_services"] = len(services)
        self.results["statistics"]["admin_services"] = len(admin_services)
        
        print(f"✅ Found {len(services)} backend services")
        print(f"✅ Found {len(admin_services)} admin services")
    
    def analyze_service(self, service_dir: Path) -> Dict[str, Any]:
        """Analyze a single service directory"""
        service_info = {
            "name": service_dir.name,
            "path": str(service_dir),
            "main_files": [],
            "endpoints": [],
            "features": [],
            "lines_of_code": 0,
            "has_dockerfile": False,
            "has_requirements": False,
            "language": "unknown"
        }
        
        # Check for main files
        main_files = [
            "main.py", "main.js", "main.go", "main.cpp", "main.rs",
            "app.py", "server.py", "index.js", "server.js"
        ]
        
        for root, dirs, files in os.walk(service_dir):
            for file in files:
                file_path = Path(root) / file
                
                # Check main files
                if file in main_files:
                    service_info["main_files"].append(str(file_path))
                    service_info["language"] = self.detect_language(file)
                    
                    # Count lines of code
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            service_info["lines_of_code"] += len(lines)
                            
                            # Extract endpoints and features
                            content = ''.join(lines)
                            service_info["endpoints"].extend(self.extract_endpoints(content))
                            service_info["features"].extend(self.extract_features(content))
                    except Exception as e:
                        print(f"⚠️  Error reading {file_path}: {e}")
                
                # Check for Dockerfile
                if file == "Dockerfile":
                    service_info["has_dockerfile"] = True
                
                # Check for requirements
                if file in ["requirements.txt", "package.json", "go.mod", "Cargo.toml"]:
                    service_info["has_requirements"] = True
        
        return service_info if service_info["main_files"] else None
    
    def detect_language(self, filename: str) -> str:
        """Detect programming language from filename"""
        ext_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".go": "Go",
            ".cpp": "C++",
            ".rs": "Rust",
            ".java": "Java"
        }
        ext = Path(filename).suffix
        return ext_map.get(ext, "Unknown")
    
    def extract_endpoints(self, content: str) -> List[str]:
        """Extract API endpoints from code"""
        endpoints = []
        
        # Python FastAPI/Flask patterns
        patterns = [
            r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            r'app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    method = match[0].upper()
                    path = match[1]
                    endpoints.append(f"{method} {path}")
        
        return list(set(endpoints))
    
    def extract_features(self, content: str) -> List[str]:
        """Extract feature keywords from code"""
        features = []
        
        feature_keywords = [
            "token", "listing", "trading", "pair", "liquidity", "pool",
            "deposit", "withdrawal", "blockchain", "evm", "non-evm",
            "admin", "user", "kyc", "aml", "compliance", "virtual",
            "iou", "staking", "swap", "futures", "options", "margin",
            "spot", "p2p", "wallet", "address", "generation"
        ]
        
        content_lower = content.lower()
        for keyword in feature_keywords:
            if keyword in content_lower:
                features.append(keyword)
        
        return list(set(features))
    
    def scan_frontend_components(self):
        """Scan frontend components"""
        print("🔍 Scanning frontend components...")
        
        components = {}
        admin_components = []
        
        for frontend_dir in [self.frontend_path, self.admin_panel_path]:
            if not frontend_dir.exists():
                continue
            
            for root, dirs, files in os.walk(frontend_dir):
                for file in files:
                    if file.endswith(('.tsx', '.jsx', '.ts', '.js')):
                        file_path = Path(root) / file
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                                component_info = {
                                    "path": str(file_path),
                                    "lines": len(content.split('\n')),
                                    "is_admin": 'admin' in str(file_path).lower(),
                                    "features": self.extract_features(content)
                                }
                                
                                components[file] = component_info
                                
                                if component_info["is_admin"]:
                                    admin_components.append(file)
                        except Exception as e:
                            print(f"⚠️  Error reading {file_path}: {e}")
        
        self.results["frontend_components"] = components
        self.results["statistics"]["total_components"] = len(components)
        self.results["statistics"]["admin_components"] = len(admin_components)
        
        print(f"✅ Found {len(components)} frontend components")
        print(f"✅ Found {len(admin_components)} admin components")
    
    def analyze_admin_capabilities(self):
        """Analyze admin capabilities from services"""
        print("🔍 Analyzing admin capabilities...")
        
        capabilities = {
            "token_listing": False,
            "trading_pair_management": False,
            "liquidity_pool_management": False,
            "deposit_withdrawal_control": False,
            "evm_blockchain_integration": False,
            "non_evm_blockchain_integration": False,
            "iou_token_creation": False,
            "virtual_liquidity_management": False,
            "user_management": False,
            "kyc_management": False,
            "compliance_management": False,
            "system_configuration": False
        }
        
        # Check services for admin capabilities
        for service_name, service_info in self.results["backend_services"].items():
            features = service_info.get("features", [])
            
            if "token" in features and "listing" in features:
                capabilities["token_listing"] = True
            
            if "trading" in features and "pair" in features:
                capabilities["trading_pair_management"] = True
            
            if "liquidity" in features and "pool" in features:
                capabilities["liquidity_pool_management"] = True
            
            if "deposit" in features and "withdrawal" in features:
                capabilities["deposit_withdrawal_control"] = True
            
            if "blockchain" in features and "evm" in features:
                capabilities["evm_blockchain_integration"] = True
            
            if "blockchain" in features and "non-evm" in features:
                capabilities["non_evm_blockchain_integration"] = True
            
            if "iou" in features:
                capabilities["iou_token_creation"] = True
            
            if "virtual" in features and "liquidity" in features:
                capabilities["virtual_liquidity_management"] = True
            
            if "user" in features and "admin" in service_name.lower():
                capabilities["user_management"] = True
            
            if "kyc" in features:
                capabilities["kyc_management"] = True
            
            if "compliance" in features or "aml" in features:
                capabilities["compliance_management"] = True
        
        self.results["admin_capabilities"] = capabilities
        
        enabled_count = sum(1 for v in capabilities.values() if v)
        print(f"✅ Found {enabled_count}/{len(capabilities)} admin capabilities")
    
    def analyze_blockchain_support(self):
        """Analyze blockchain support"""
        print("🔍 Analyzing blockchain support...")
        
        blockchains = {
            "evm_chains": [],
            "non_evm_chains": [],
            "address_generation": False,
            "wallet_management": False
        }
        
        # Check for blockchain services
        for service_name, service_info in self.results["backend_services"].items():
            if "blockchain" in service_name.lower():
                features = service_info.get("features", [])
                
                if "evm" in features:
                    blockchains["evm_chains"].append(service_name)
                
                if "non-evm" in features or "solana" in features or "ton" in features:
                    blockchains["non_evm_chains"].append(service_name)
            
            if "address" in service_name.lower() and "generation" in service_name.lower():
                blockchains["address_generation"] = True
            
            if "wallet" in service_name.lower():
                blockchains["wallet_management"] = True
        
        self.results["blockchain_support"] = blockchains
        
        print(f"✅ EVM chains support: {len(blockchains['evm_chains'])} services")
        print(f"✅ Non-EVM chains support: {len(blockchains['non_evm_chains'])} services")
    
    def identify_missing_features(self):
        """Identify missing features compared to major exchanges"""
        print("🔍 Identifying missing features...")
        
        required_features = {
            "Admin Features": [
                "Complete token listing system",
                "Trading pair management",
                "Liquidity pool administration",
                "Deposit/withdrawal controls per blockchain",
                "EVM blockchain integration",
                "Non-EVM blockchain integration (TON, Solana, Pi)",
                "IOU token creation",
                "Virtual liquidity management",
                "Role-based admin access",
                "System configuration",
                "Analytics dashboard",
                "User management"
            ],
            "User Features": [
                "Deposit/withdrawal for all chains",
                "Spot trading",
                "Futures trading",
                "Margin trading",
                "Options trading",
                "P2P trading",
                "Coin conversion",
                "Staking",
                "Lending/borrowing",
                "NFT marketplace",
                "Copy trading",
                "Trading bots",
                "KYC submission",
                "Customer support"
            ],
            "Platform Features": [
                "Web application",
                "Mobile app (iOS/Android)",
                "Desktop app",
                "API access",
                "WebSocket real-time data",
                "Multi-language support",
                "Dark/light theme"
            ]
        }
        
        missing = []
        
        # Check admin features
        admin_caps = self.results["admin_capabilities"]
        if not admin_caps.get("token_listing"):
            missing.append("Complete token listing system")
        if not admin_caps.get("trading_pair_management"):
            missing.append("Trading pair management")
        if not admin_caps.get("liquidity_pool_management"):
            missing.append("Liquidity pool administration")
        
        self.results["missing_features"] = missing
        
        print(f"⚠️  Found {len(missing)} missing features")
    
    def generate_report(self):
        """Generate comprehensive audit report"""
        print("\n" + "="*80)
        print("📊 TIGEREX COMPREHENSIVE AUDIT REPORT")
        print("="*80 + "\n")
        
        # Backend Services Summary
        print("🔧 BACKEND SERVICES")
        print("-" * 80)
        print(f"Total Services: {self.results['statistics'].get('total_services', 0)}")
        print(f"Admin Services: {self.results['statistics'].get('admin_services', 0)}")
        
        total_loc = sum(s.get('lines_of_code', 0) for s in self.results['backend_services'].values())
        print(f"Total Lines of Code: {total_loc:,}")
        
        # Language breakdown
        languages = defaultdict(int)
        for service in self.results['backend_services'].values():
            lang = service.get('language', 'Unknown')
            languages[lang] += 1
        
        print("\nLanguage Distribution:")
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {lang}: {count} services")
        
        # Frontend Components Summary
        print("\n🎨 FRONTEND COMPONENTS")
        print("-" * 80)
        print(f"Total Components: {self.results['statistics'].get('total_components', 0)}")
        print(f"Admin Components: {self.results['statistics'].get('admin_components', 0)}")
        
        # Admin Capabilities
        print("\n👑 ADMIN CAPABILITIES")
        print("-" * 80)
        for capability, enabled in self.results['admin_capabilities'].items():
            status = "✅" if enabled else "❌"
            print(f"{status} {capability.replace('_', ' ').title()}")
        
        # Blockchain Support
        print("\n⛓️  BLOCKCHAIN SUPPORT")
        print("-" * 80)
        bc_support = self.results['blockchain_support']
        print(f"EVM Chains: {len(bc_support.get('evm_chains', []))} services")
        print(f"Non-EVM Chains: {len(bc_support.get('non_evm_chains', []))} services")
        print(f"Address Generation: {'✅' if bc_support.get('address_generation') else '❌'}")
        print(f"Wallet Management: {'✅' if bc_support.get('wallet_management') else '❌'}")
        
        # Missing Features
        if self.results['missing_features']:
            print("\n⚠️  MISSING FEATURES")
            print("-" * 80)
            for feature in self.results['missing_features']:
                print(f"  - {feature}")
        
        print("\n" + "="*80)
    
    def save_report(self, output_file: str = "audit_report.json"):
        """Save audit results to JSON file"""
        output_path = self.base_path / output_file
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Report saved to: {output_path}")
    
    def run_full_audit(self):
        """Run complete audit"""
        print("🚀 Starting TigerEx Comprehensive Audit...\n")
        
        self.scan_backend_services()
        self.scan_frontend_components()
        self.analyze_admin_capabilities()
        self.analyze_blockchain_support()
        self.identify_missing_features()
        self.generate_report()
        self.save_report()
        
        print("\n✅ Audit completed successfully!")

if __name__ == "__main__":
    auditor = TigerExAuditor("/workspace/TigerEx")
    auditor.run_full_audit()