#!/usr/bin/env python3
"""
Comprehensive testing script for enhanced TigerEx services
Tests all new unique features across exchanges
"""

import requests
import json
import time
import subprocess
import sys
from threading import Thread
import signal
import os

class ServiceTester:
    def __init__(self):
        self.services = {
            "kucoin": {"port": 8001, "file": "backend/kucoin-advanced-service/main.py"},
            "huobi": {"port": 8003, "file": "backend/huobi-advanced-service/main.py"},
            "kraken": {"port": 8004, "file": "backend/kraken-advanced-service/main.py"},
            "coinbase": {"port": 8007, "file": "backend/coinbase-advanced-service/main.py"},
            "gemini": {"port": 8003, "file": "backend/gemini-advanced-service/main.py"},
            "ultimate_fetchers": {"port": 8001, "file": "backend/ultimate-exchange-fetchers/main.py"},
            "user_access": {"port": 8002, "file": "backend/user-access-system-complete/main.py"},
            "super_admin": {"port": 8000, "file": "backend/super-admin-system/src/main.py"}
        }
        self.running_processes = {}
        self.test_results = {}

    def start_service(self, service_name):
        """Start a service in the background"""
        if service_name in self.services:
            service = self.services[service_name]
            try:
                # Use python3 to run the service
                cmd = [sys.executable, service["file"]]
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd="/workspace/TigerEx-"
                )
                self.running_processes[service_name] = process
                print(f"✓ Started {service_name} service on port {service['port']}")
                time.sleep(2)  # Give service time to start
                return True
            except Exception as e:
                print(f"✗ Failed to start {service_name}: {e}")
                return False
        return False

    def stop_service(self, service_name):
        """Stop a running service"""
        if service_name in self.running_processes:
            try:
                process = self.running_processes[service_name]
                process.terminate()
                process.wait(timeout=5)
                print(f"✓ Stopped {service_name} service")
                return True
            except Exception as e:
                print(f"✗ Failed to stop {service_name}: {e}")
                return False
        return False

    def test_endpoint(self, service_name, endpoint, expected_keys=None):
        """Test a specific endpoint"""
        service = self.services.get(service_name)
        if not service:
            return False
        
        url = f"http://localhost:{service['port']}{endpoint}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if expected_keys:
                    for key in expected_keys:
                        if key not in data:
                            print(f"✗ {service_name}{endpoint}: Missing key '{key}'")
                            return False
                
                print(f"✓ {service_name}{endpoint}: OK")
                self.test_results[f"{service_name}{endpoint}"] = True
                return True
            else:
                print(f"✗ {service_name}{endpoint}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ {service_name}{endpoint}: {e}")
            return False

    def test_kucoin_features(self):
        """Test KuCoin enhanced features"""
        print("\n--- Testing KuCoin Enhanced Features ---")
        
        endpoints = [
            ("/win/lottery/games", ["games"]),
            ("/spotlight/projects", ["projects"]),
            ("/candy/bonus", ["active_campaigns"]),
            ("/cloud/services", ["services"]),
            ("/bot/marketplace", ["featured_bots"]),
            ("/leveraged/tokens/pro", ["tokens"]),
            ("/polkadot/ecosystem", ["supported_chains"])
        ]
        
        success = True
        for endpoint, keys in endpoints:
            if not self.test_endpoint("kucoin", endpoint, keys):
                success = False
        
        return success

    def test_huobi_features(self):
        """Test Huobi enhanced features"""
        print("\n--- Testing Huobi Enhanced Features ---")
        
        endpoints = [
            ("/huobi/pool/mining", ["pools"]),
            ("/huobi/ventures/portfolio", ["portfolio"]),
            ("/heco/chain/pro", ["features"]),
            ("/huobi/global/elite", ["membership_tiers"]),
            ("/huobi/cloud/services", ["services"]),
            ("/heco/smart/chain", ["chain_info"]),
            ("/huobi/launchpad/pro", ["features"])
        ]
        
        success = True
        for endpoint, keys in endpoints:
            if not self.test_endpoint("huobi", endpoint, keys):
                success = False
        
        return success

    def test_kraken_features(self):
        """Test Kraken enhanced features"""
        print("\n--- Testing Kraken Enhanced Features ---")
        
        endpoints = [
            ("/kraken/pro/features", ["features"]),
            ("/kraken/card/services", ["card_types"]),
            ("/kraken/bank/services", ["banking_services"]),
            ("/kraken/securities/trading", ["available_securities"]),
            ("/cryptowatch/analytics", ["analytics_tools"]),
            ("/kraken/margin/trading/pro", ["margin_products"]),
            ("/kraken/direct/listing", ["listing_services"])
        ]
        
        success = True
        for endpoint, keys in endpoints:
            if not self.test_endpoint("kraken", endpoint, keys):
                success = False
        
        return success

    def test_coinbase_features(self):
        """Test Coinbase enhanced features"""
        print("\n--- Testing Coinbase Enhanced Features ---")
        
        endpoints = [
            ("/earn/learn", ["courses"]),
            ("/coinbase/card", ["card_features"]),
            ("/coinbase/one", ["benefits"]),
            ("/coinbase/cloud", ["services"]),
            ("/commerce", ["payment_solution"]),
            ("/nft/platform", ["platform"]),
            ("/base/layer2", ["network"])
        ]
        
        success = True
        for endpoint, keys in endpoints:
            if not self.test_endpoint("coinbase", endpoint, keys):
                success = False
        
        return success

    def test_gemini_features(self):
        """Test Gemini enhanced features"""
        print("\n--- Testing Gemini Enhanced Features ---")
        
        endpoints = [
            ("/activetrader/pro", ["features"]),
            ("/gemini/pay", ["payment_solution"]),
            ("/gemini/card", ["rewards_structure"]),
            ("/gemini/earn/enhanced", ["interest_rates"]),
            ("/custody/advanced", ["security_features"]),
            ("/clearing/settlement", ["services"]),
            ("/derivatives/exchange", ["planned_products"])
        ]
        
        success = True
        for endpoint, keys in endpoints:
            if not self.test_endpoint("gemini", endpoint, keys):
                success = False
        
        return success

    def test_ultimate_fetchers(self):
        """Test ultimate exchange fetchers"""
        print("\n--- Testing Ultimate Exchange Fetchers ---")
        
        endpoints = [
            ("/exchange-features/binance", ["unique_features"]),
            ("/exchange-features/kucoin", ["unique_features"]),
            ("/cross-exchange-analytics", ["market_overview"]),
            ("/real-time-monitoring", ["system_status"])
        ]
        
        success = True
        for endpoint, keys in endpoints:
            if not self.test_endpoint("ultimate_fetchers", endpoint, keys):
                success = False
        
        return success

    def run_comprehensive_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Service Testing")
        print("=" * 50)
        
        # Test in phases to avoid port conflicts
        test_phases = [
            {
                "name": "Exchange Services",
                "services": ["kucoin", "huobi", "kraken", "coinbase", "gemini"],
                "tests": [self.test_kucoin_features, self.test_huobi_features, 
                         self.test_kraken_features, self.test_coinbase_features, 
                         self.test_gemini_features]
            },
            {
                "name": "Integration Services", 
                "services": ["ultimate_fetchers"],
                "tests": [self.test_ultimate_fetchers]
            }
        ]
        
        total_success = True
        
        for phase in test_phases:
            print(f"\n📋 {phase['name']}")
            print("-" * 30)
            
            # Start services for this phase
            started_services = []
            for service_name in phase["services"]:
                if self.start_service(service_name):
                    started_services.append(service_name)
            
            # Wait for services to fully start
            time.sleep(3)
            
            # Run tests
            for test_func in phase["tests"]:
                try:
                    if not test_func():
                        total_success = False
                except Exception as e:
                    print(f"✗ Test failed with exception: {e}")
                    total_success = False
            
            # Stop services
            for service_name in started_services:
                self.stop_service(service_name)
            
            # Brief pause between phases
            time.sleep(2)
        
        return total_success

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 50)
        print("📊 TEST REPORT")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for test_name, result in self.test_results.items():
                if not result:
                    print(f"  - {test_name}")
        
        print(f"\n🎯 Implementation Status: {'COMPLETE' if failed_tests == 0 else 'NEEDS FIXES'}")

    def cleanup(self):
        """Clean up all running processes"""
        print("\n🧹 Cleaning up...")
        for service_name in list(self.running_processes.keys()):
            self.stop_service(service_name)

if __name__ == "__main__":
    tester = ServiceTester()
    
    try:
        success = tester.run_comprehensive_tests()
        tester.generate_report()
        
        if success:
            print("\n🎉 All tests passed! Implementation is ready for deployment.")
            sys.exit(0)
        else:
            print("\n⚠️  Some tests failed. Please check the issues above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        tester.cleanup()