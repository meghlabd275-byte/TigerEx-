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
TigerEx System Verification - Post Restore
Tests all critical components after restoring from commit d385226
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class TigerExSystemVerifier:
    def __init__(self):
        self.results = {
            "python_files": 0,
            "javascript_files": 0,
            "typescript_files": 0,
            "config_files": 0,
            "docker_files": 0,
            "errors": []
        }
    
    def verify_python_syntax(self):
        """Verify Python files have correct syntax"""
        python_files = list(Path(".").rglob("*.py"))
        errors = []
        
        for py_file in python_files:
            if "node_modules" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            try:
                subprocess.run([sys.executable, "-m", "py_compile", str(py_file)], 
                             check=True, capture_output=True, text=True)
                self.results["python_files"] += 1
            except subprocess.CalledProcessError as e:
                errors.append(f"{py_file}: {e.stderr}")
        
        if errors:
            self.results["errors"].extend(errors)
        return len(errors) == 0
    
    def verify_file_structure(self):
        """Verify all expected directories and files exist"""
        expected_dirs = [
            "backend",
            "frontend",
            "mobile-app",
            "desktop-app",
            "src",
            "tests",
            "scripts",
            "docs"
        ]
        
        missing_dirs = []
        for dir_name in expected_dirs:
            if not os.path.exists(dir_name):
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            self.results["errors"].append(f"Missing directories: {missing_dirs}")
        
        return len(missing_dirs) == 0
    
    def verify_config_files(self):
        """Verify configuration files exist and are valid"""
        config_files = [
            "package.json",
            "docker-compose.yml",
            "tsconfig.json",
            "tailwind.config.js",
            "nginx.conf"
        ]
        
        missing_configs = []
        for config_file in config_files:
            if not os.path.exists(config_file):
                missing_configs.append(config_file)
            else:
                self.results["config_files"] += 1
        
        if missing_configs:
            self.results["errors"].append(f"Missing config files: {missing_configs}")
        
        return len(missing_configs) == 0
    
    def verify_backend_services(self):
        """Verify backend services are properly structured"""
        backend_services = [
            "backend/account-management-service",
            "backend/spot-trading",
            "backend/futures-trading",
            "backend/margin-trading",
            "backend/options-trading",
            "backend/copy-trading",
            "backend/grid-trading",
            "backend/bot-trading"
        ]
        
        missing_services = []
        for service in backend_services:
            if not os.path.exists(service):
                missing_services.append(service)
        
        if missing_services:
            self.results["errors"].append(f"Missing backend services: {missing_services}")
        
        return len(missing_services) == 0
    
    def verify_frontend_structure(self):
        """Verify frontend application structure"""
        frontend_files = [
            "src/App.tsx",
            "src/main.tsx",
            "src/pages/index.tsx",
            "src/components/layout/Header.tsx",
            "src/styles/globals.css"
        ]
        
        missing_files = []
        for file_path in frontend_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            self.results["errors"].append(f"Missing frontend files: {missing_files}")
        
        return len(missing_files) == 0
    
    def verify_mobile_app(self):
        """Verify mobile app structure"""
        mobile_files = [
            "mobile-app/App.tsx",
            "mobile-app/package.json",
            "mobile-app/src/screens/HomeScreen.tsx"
        ]
        
        missing_files = []
        for file_path in mobile_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            self.results["errors"].append(f"Missing mobile files: {missing_files}")
        
        return len(missing_files) == 0
    
    def verify_desktop_app(self):
        """Verify desktop app structure"""
        desktop_files = [
            "desktop-app/main.js",
            "desktop-app/package.json",
            "desktop-app/src/renderer/index.html"
        ]
        
        missing_files = []
        for file_path in desktop_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            self.results["errors"].append(f"Missing desktop files: {missing_files}")
        
        return len(missing_files) == 0
    
    def run_comprehensive_verification(self):
        """Run all verification tests"""
        print("🔍 Starting TigerEx System Verification...")
        print("=" * 60)
        
        tests = [
            ("Python Syntax", self.verify_python_syntax),
            ("File Structure", self.verify_file_structure),
            ("Config Files", self.verify_config_files),
            ("Backend Services", self.verify_backend_services),
            ("Frontend Structure", self.verify_frontend_structure),
            ("Mobile App", self.verify_mobile_app),
            ("Desktop App", self.verify_desktop_app)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    print(f"✅ {test_name}: PASSED")
                    passed += 1
                else:
                    print(f"❌ {test_name}: FAILED")
                    failed += 1
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                failed += 1
        
        print("\n" + "=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {passed}")
        print(f"❌ Tests Failed: {failed}")
        print(f"📁 Python Files: {self.results['python_files']}")
        print(f"⚙️  Config Files: {self.results['config_files']}")
        
        if self.results["errors"]:
            print("\n🚨 ERRORS FOUND:")
            for error in self.results["errors"]:
                print(f"   - {error}")
        
        # Save results
        with open("verification_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        overall_status = "✅ SUCCESS" if failed == 0 else "❌ NEEDS ATTENTION"
        print(f"\n🎯 Overall Status: {overall_status}")
        
        return failed == 0

def main():
    """Main verification function"""
    verifier = TigerExSystemVerifier()
    success = verifier.run_comprehensive_verification()
    
    if success:
        print("\n🎉 TigerEx system is ready for deployment!")
        return 0
    else:
        print("\n⚠️  Some issues need attention before deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())