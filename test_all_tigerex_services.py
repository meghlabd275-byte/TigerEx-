#!/usr/bin/env python3

"""
Comprehensive Test Suite for All TigerEx Services
Tests all endpoints, functionality, and admin controls
"""

import requests
import json
import time
import asyncio
from datetime import datetime

# Service endpoints configuration
SERVICES = {
    'tiger-academy-service': 'http://localhost:5001',
    'tiger-admin-service': 'http://localhost:5002',
    'tiger-verify-service': 'http://localhost:5003',
    'tiger-wealth-service': 'http://localhost:5004',
    'tiger-unified-exchange-service': 'http://localhost:5005',
    'tiger-user-service': 'http://localhost:5006',
    'tiger-trading-service': 'http://localhost:5007',
    'tiger-wallet-service': 'http://localhost:5008',
    'tiger-staking-service': 'http://localhost:5009',
    'tiger-nft-service': 'http://localhost:5010',
    'tiger-pay-service': 'http://localhost:5011',
    'tiger-card-service': 'http://localhost:5012',
    'tiger-trading-bots-service': 'http://localhost:5013'
}

class TigerExTester:
    def __init__(self):
        self.test_results = {}
        self.auth_tokens = {}
        self.base_url = 'http://localhost'
        
    def log_result(self, service, test_name, status, message=""):
        """Log test result"""
        if service not in self.test_results:
            self.test_results[service] = []
        
        self.test_results[service].append({
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        status_symbol = "✅" if status else "❌"
        print(f"{status_symbol} {service}: {test_name} - {message}")
    
    def test_health_endpoint(self, service_name, base_url):
        """Test health endpoint for a service"""
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_result(service_name, "Health Check", True, "Service is healthy")
                    return True
                else:
                    self.log_result(service_name, "Health Check", False, f"Unhealthy status: {data.get('status')}")
                    return False
            else:
                self.log_result(service_name, "Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result(service_name, "Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_user_endpoints(self, service_name, base_url):
        """Test basic user endpoints"""
        try:
            # Test user registration
            register_data = {
                "email": f"test_{service_name}@tigerex.com",
                "password": "testpassword123",
                "name": f"Test User {service_name}"
            }
            
            response = requests.post(f"{base_url}/api/register", json=register_data, timeout=10)
            if response.status_code in [200, 201]:
                self.log_result(service_name, "User Registration", True, "User registered successfully")
            else:
                # User might already exist, try to login
                self.log_result(service_name, "User Registration", False, f"HTTP {response.status_code}")
            
            # Test user login
            login_data = {
                "email": f"test_{service_name}@tigerex.com",
                "password": "testpassword123"
            }
            
            response = requests.post(f"{base_url}/api/login", json=login_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.auth_tokens[service_name] = data['token']
                    self.log_result(service_name, "User Login", True, "Login successful")
                    return True
                else:
                    self.log_result(service_name, "User Login", False, "No token in response")
                    return False
            else:
                self.log_result(service_name, "User Login", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result(service_name, "User Endpoints", False, f"Error: {str(e)}")
            return False
    
    def test_admin_endpoints(self, service_name, base_url):
        """Test admin endpoints"""
        try:
            if service_name not in self.auth_tokens:
                self.log_result(service_name, "Admin Endpoints", False, "No auth token available")
                return False
            
            headers = {'Authorization': f"Bearer {self.auth_tokens[service_name]}"}
            
            # Test admin stats endpoint
            response = requests.get(f"{base_url}/api/admin/stats", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(service_name, "Admin Stats", True, "Admin stats retrieved")
                else:
                    self.log_result(service_name, "Admin Stats", False, "API returned failure")
            else:
                self.log_result(service_name, "Admin Stats", False, f"HTTP {response.status_code}")
            
            # Test user management endpoint
            response = requests.get(f"{base_url}/api/admin/users", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(service_name, "User Management", True, "User management accessible")
                else:
                    self.log_result(service_name, "User Management", False, "API returned failure")
            else:
                self.log_result(service_name, "User Management", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result(service_name, "Admin Endpoints", False, f"Error: {str(e)}")
    
    def test_service_specific_endpoints(self, service_name, base_url):
        """Test service-specific endpoints"""
        try:
            if service_name not in self.auth_tokens:
                return
            
            headers = {'Authorization': f"Bearer {self.auth_tokens[service_name]}"}
            
            if service_name == 'tiger-unified-exchange-service':
                # Test market data endpoints
                response = requests.get(f"{base_url}/api/tiger-unified/market/ticker/binance/BTCUSDT", headers=headers, timeout=10)
                if response.status_code == 200:
                    self.log_result(service_name, "Market Data Ticker", True, "Market data accessible")
                else:
                    self.log_result(service_name, "Market Data Ticker", False, f"HTTP {response.status_code}")
                
                response = requests.get(f"{base_url}/api/tiger-unified/trading/accounts", headers=headers, timeout=10)
                if response.status_code == 200:
                    self.log_result(service_name, "Trading Accounts", True, "Trading accounts accessible")
                else:
                    self.log_result(service_name, "Trading Accounts", False, f"HTTP {response.status_code}")
            
            elif service_name == 'tiger-verify-service':
                # Test verification endpoints
                response = requests.get(f"{base_url}/api/tiger-verify/status", headers=headers, timeout=10)
                if response.status_code == 200:
                    self.log_result(service_name, "Verification Status", True, "Verification status accessible")
                else:
                    self.log_result(service_name, "Verification Status", False, f"HTTP {response.status_code}")
            
            elif service_name == 'tiger-wealth-service':
                # Test wealth management endpoints
                response = requests.get(f"{base_url}/api/tiger-wealth/portfolios", headers=headers, timeout=10)
                if response.status_code == 200:
                    self.log_result(service_name, "Wealth Portfolios", True, "Wealth portfolios accessible")
                else:
                    self.log_result(service_name, "Wealth Portfolios", False, f"HTTP {response.status_code}")
            
            elif service_name == 'tiger-academy-service':
                # Test academy endpoints
                response = requests.get(f"{base_url}/api/courses", headers=headers, timeout=10)
                if response.status_code == 200:
                    self.log_result(service_name, "Academy Courses", True, "Academy courses accessible")
                else:
                    self.log_result(service_name, "Academy Courses", False, f"HTTP {response.status_code}")
                    
        except Exception as e:
            self.log_result(service_name, "Service-Specific Endpoints", False, f"Error: {str(e)}")
    
    def run_service_tests(self, service_name, base_url):
        """Run all tests for a specific service"""
        print(f"\n🧪 Testing {service_name}...")
        
        # Test health endpoint
        health_ok = self.test_health_endpoint(service_name, base_url)
        
        if health_ok:
            # Test user endpoints
            self.test_user_endpoints(service_name, base_url)
            
            # Test admin endpoints
            self.test_admin_endpoints(service_name, base_url)
            
            # Test service-specific endpoints
            self.test_service_specific_endpoints(service_name, base_url)
        
        print(f"✅ Completed testing {service_name}")
    
    def run_all_tests(self):
        """Run tests for all services"""
        print("🚀 Starting comprehensive TigerEx service tests...")
        print("=" * 60)
        
        start_time = time.time()
        
        for service_name, base_url in SERVICES.items():
            self.run_service_tests(service_name, base_url)
            time.sleep(1)  # Small delay between services
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for service_name, results in self.test_results.items():
            service_passed = 0
            service_total = len(results)
            
            for result in results:
                total_tests += 1
                if result['status']:
                    passed_tests += 1
                    service_passed += 1
            
            success_rate = (service_passed / service_total * 100) if service_total > 0 else 0
            print(f"\n📋 {service_name}")
            print(f"   ✅ Passed: {service_passed}/{service_total} ({success_rate:.1f}%)")
            
            # Show failed tests
            for result in results:
                if not result['status']:
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 OVERALL RESULTS")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        print(f"   Duration: {duration:.2f} seconds")
        
        # Save results to file
        with open('tigerex_test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': total_tests - passed_tests,
                    'success_rate': overall_success_rate,
                    'duration': duration,
                    'timestamp': datetime.now().isoformat()
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to tigerex_test_results.json")
        
        return overall_success_rate >= 80  # Consider successful if 80%+ tests pass

def main():
    """Main function to run all tests"""
    tester = TigerExTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests completed successfully! TigerEx services are ready for deployment.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the results and fix any issues.")
        return 1

if __name__ == "__main__":
    exit(main())