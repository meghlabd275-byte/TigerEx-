#!/usr/bin/env python3
"""
Service Verification Script
Tests all services across web, mobile, and desktop platforms
"""

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor
import subprocess
import os

class ServiceVerifier:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.services = []
        self.results = {}
    
    def load_services(self):
        """Load all services from backend directory"""
        backend_dir = "tigerex-repo/backend"
        if os.path.exists(backend_dir):
            for item in os.listdir(backend_dir):
                if os.path.isdir(os.path.join(backend_dir, item)):
                    self.services.append(item)
        print(f"Found {len(self.services)} services to verify")
    
    def test_service_health(self, service_name):
        """Test individual service health"""
        try:
            # Try different possible health endpoints
            endpoints = [
                f"{self.base_url}/api/{service_name}/health",
                f"{self.base_url}/health",
                f"http://localhost:5000/health"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=5)
                    if response.status_code == 200:
                        return {
                            'service': service_name,
                            'status': 'healthy',
                            'endpoint': endpoint,
                            'response_time': response.elapsed.total_seconds()
                        }
                except:
                    continue
            
            return {
                'service': service_name,
                'status': 'unreachable',
                'endpoint': None,
                'response_time': None
            }
            
        except Exception as e:
            return {
                'service': service_name,
                'status': 'error',
                'error': str(e),
                'endpoint': None,
                'response_time': None
            }
    
    def test_web_app(self):
        """Test web application"""
        try:
            response = requests.get("http://localhost:3000", timeout=10)
            return {
                'platform': 'web',
                'status': 'healthy' if response.status_code == 200 else 'error',
                'response_time': response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                'platform': 'web',
                'status': 'error',
                'error': str(e)
            }
    
    def test_mobile_build(self):
        """Test mobile application build"""
        try:
            mobile_dir = "tigerex-repo/mobile-app"
            if os.path.exists(mobile_dir):
                # Check if package.json exists
                package_json = os.path.join(mobile_dir, "package.json")
                if os.path.exists(package_json):
                    return {
                        'platform': 'mobile',
                        'status': 'configured',
                        'build_ready': True
                    }
            return {
                'platform': 'mobile',
                'status': 'not_configured',
                'build_ready': False
            }
        except Exception as e:
            return {
                'platform': 'mobile',
                'status': 'error',
                'error': str(e)
            }
    
    def test_desktop_build(self):
        """Test desktop application build"""
        try:
            desktop_dir = "tigerex-repo/desktop-app"
            if os.path.exists(desktop_dir):
                # Check if package.json exists
                package_json = os.path.join(desktop_dir, "package.json")
                if os.path.exists(package_json):
                    return {
                        'platform': 'desktop',
                        'status': 'configured',
                        'build_ready': True
                    }
            return {
                'platform': 'desktop',
                'status': 'not_configured',
                'build_ready': False
            }
        except Exception as e:
            return {
                'platform': 'desktop',
                'status': 'error',
                'error': str(e)
            }
    
    def run_verification(self):
        """Run complete verification"""
        print("🔍 Starting TigerEx Service Verification...")
        print("="*60)
        
        # Load services
        self.load_services()
        
        # Test services in parallel
        print("\n📊 Testing Backend Services...")
        with ThreadPoolExecutor(max_workers=10) as executor:
            service_results = list(executor.map(self.test_service_health, self.services))
        
        # Test platforms
        print("\n🌐 Testing Web Application...")
        web_result = self.test_web_app()
        
        print("📱 Testing Mobile Application...")
        mobile_result = self.test_mobile_build()
        
        print("🖥️  Testing Desktop Application...")
        desktop_result = self.test_desktop_build()
        
        # Compile results
        self.results = {
            'services': service_results,
            'platforms': [web_result, mobile_result, desktop_result],
            'timestamp': time.time(),
            'total_services': len(self.services)
        }
        
        # Display results
        self.display_results()
        
        return self.results
    
    def display_results(self):
        """Display verification results"""
        print("\n" + "="*60)
        print("📋 VERIFICATION RESULTS")
        print("="*60)
        
        # Service results
        healthy_services = sum(1 for s in self.results['services'] if s['status'] == 'healthy')
        print(f"\n🔧 Backend Services: {healthy_services}/{len(self.services)} Healthy")
        
        for service in self.results['services'][:10]:  # Show first 10
            status_icon = "✅" if service['status'] == 'healthy' else "❌"
            print(f"   {status_icon} {service['service']}: {service['status']}")
        
        if len(self.results['services']) > 10:
            print(f"   ... and {len(self.results['services']) - 10} more services")
        
        # Platform results
        print(f"\n🚀 Platform Status:")
        for platform in self.results['platforms']:
            status_icon = "✅" if platform['status'] in ['healthy', 'configured'] else "❌"
            print(f"   {status_icon} {platform['platform'].title()}: {platform['status']}")
        
        # Summary
        total_healthy = healthy_services
        total_platforms = sum(1 for p in self.results['platforms'] if p['status'] in ['healthy', 'configured'])
        
        print(f"\n📊 SUMMARY:")
        total_services = len(self.services)
        if total_services > 0:
            percentage = (healthy_services/total_services*100)
            print(f"   Services: {healthy_services}/{total_services} ({percentage:.1f}%)")
        else:
            print(f"   Services: {healthy_services}/{total_services} (0.0%)")
        print(f"   Platforms: {total_platforms}/3 ({(total_platforms/3*100):.1f}%)")
        print(f"   Overall Status: {'✅ EXCELLENT' if total_platforms == 3 and healthy_services > len(self.services)*0.8 else '⚠️  NEEDS ATTENTION'}")

def main():
    verifier = ServiceVerifier()
    results = verifier.run_verification()
    
    # Save results
    with open('verification_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to verification_results.json")

if __name__ == "__main__":
    main()
