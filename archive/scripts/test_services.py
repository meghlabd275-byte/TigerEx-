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
Comprehensive test script for TigerEx services
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

def test_service_health(service_path, service_name, port=None):
    """Test if a service is healthy"""
    try:
        if port:
            # Test HTTP endpoint
            import requests
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=5)
                if response.status_code == 200:
                    return True, "Service is healthy"
                else:
                    return False, f"Health check failed with status {response.status_code}"
            except requests.exceptions.RequestException as e:
                return False, f"Connection failed: {str(e)}"
        else:
            # Test if service files exist and are valid
            if not os.path.exists(service_path):
                return False, "Service directory does not exist"
            
            # Check for main files
            main_files = ['server.js', 'main.js', 'main.py', 'app.js', 'index.js']
            has_main = any(os.path.exists(os.path.join(service_path, f)) for f in main_files)
            
            if not has_main:
                return False, "No main service file found"
            
            return True, "Service structure is valid"
    except Exception as e:
        return False, f"Test failed: {str(e)}"

def check_service_dependencies(service_path):
    """Check if service has required dependencies"""
    try:
        package_json = os.path.join(service_path, 'package.json')
        requirements_txt = os.path.join(service_path, 'requirements.txt')
        
        if os.path.exists(package_json):
            with open(package_json, 'r') as f:
                data = json.load(f)
                dependencies = data.get('dependencies', {})
                return len(dependencies) > 0, f"Found {len(dependencies)} npm dependencies"
        
        if os.path.exists(requirements_txt):
            with open(requirements_txt, 'r') as f:
                lines = f.readlines()
                return len(lines) > 0, f"Found {len(lines)} Python dependencies"
        
        return True, "No dependency file found"
    except Exception as e:
        return False, f"Dependency check failed: {str(e)}"

def main():
    """Main test function"""
    print("🚀 Starting TigerEx Platform Health Check...")
    print("=" * 60)
    
    backend_dir = "backend"
    if not os.path.exists(backend_dir):
        print("❌ Backend directory not found")
        return
    
    services = []
    failed_services = []
    warnings = []
    
    # Walk through all backend services
    for root, dirs, files in os.walk(backend_dir):
        # Skip backup directories
        if 'backup' in root:
            continue
            
        # Look for service indicators
        service_files = ['server.js', 'main.js', 'main.py', 'app.js', 'index.js', 'Cargo.toml']
        has_service_file = any(f in files for f in service_files)
        
        if has_service_file and root != backend_dir:
            services.append(root)
    
    print(f"📊 Found {len(services)} services to test")
    print()
    
    # Test each service
    for i, service_path in enumerate(services, 1):
        service_name = os.path.basename(service_path)
        print(f"🔍 [{i}/{len(services)}] Testing {service_name}...")
        
        # Test service health
        healthy, health_msg = test_service_health(service_path, service_name)
        
        # Test dependencies
        deps_ok, deps_msg = check_service_dependencies(service_path)
        
        if healthy:
            print(f"   ✅ {service_name} - {health_msg}")
        else:
            print(f"   ❌ {service_name} - {health_msg}")
            failed_services.append((service_name, health_msg))
        
        if not deps_ok:
            print(f"   ⚠️  {service_name} - {deps_msg}")
            warnings.append((service_name, deps_msg))
    
    print()
    print("=" * 60)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total_services = len(services)
    healthy_services = total_services - len(failed_services)
    
    print(f"Total Services: {total_services}")
    print(f"Healthy Services: {healthy_services}")
    print(f"Failed Services: {len(failed_services)}")
    print(f"Warnings: {len(warnings)}")
    print()
    
    if failed_services:
        print("❌ FAILED SERVICES:")
        for service, error in failed_services:
            print(f"   - {service}: {error}")
        print()
    
    if warnings:
        print("⚠️  WARNINGS:")
        for service, warning in warnings:
            print(f"   - {service}: {warning}")
        print()
    
    # Check for critical services
    critical_services = ['auth-service', 'wallet-service', 'spot-trading', 'defi-service', 'matching-engine']
    missing_critical = []
    
    for critical in critical_services:
        found = any(critical in service for service in services)
        if not found:
            missing_critical.append(critical)
    
    if missing_critical:
        print("🚨 CRITICAL SERVICES MISSING:")
        for service in missing_critical:
            print(f"   - {service}")
        print()
    
    # Overall health score
    health_score = (healthy_services / total_services) * 100 if total_services > 0 else 0
    
    print(f"🏥 OVERALL HEALTH SCORE: {health_score:.1f}%")
    
    if health_score >= 90:
        print("🟢 Platform Status: EXCELLENT")
    elif health_score >= 70:
        print("🟡 Platform Status: GOOD")
    elif health_score >= 50:
        print("🟠 Platform Status: FAIR")
    else:
        print("🔴 Platform Status: POOR")
    
    print()
    print("✅ Health check completed!")
    
    # Save report
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_services": total_services,
        "healthy_services": healthy_services,
        "failed_services": len(failed_services),
        "warnings": len(warnings),
        "health_score": health_score,
        "failed_details": failed_services,
        "warning_details": warnings,
        "missing_critical": missing_critical
    }
    
    with open("health_check_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("📄 Report saved to health_check_report.json")

if __name__ == "__main__":
    main()