#!/usr/bin/env python3
"""
Final verification script for TigerEx platform
"""

import os
import json
from collections import defaultdict

def verify_service_structure(service_path):
    """Verify that a service has the proper structure"""
    issues = []
    
    # Check if service directory exists
    if not os.path.exists(service_path):
        issues.append("Service directory does not exist")
        return issues
    
    # Check for source code
    src_path = os.path.join(service_path, "src")
    main_py = os.path.join(service_path, "src", "main.py")
    main_rs = os.path.join(service_path, "src", "main.rs")
    main_cpp = os.path.join(service_path, "src", "main.cpp")
    server_js = os.path.join(service_path, "src", "server.js")
    main_go = os.path.join(service_path, "src", "main.go")
    
    main_py_root = os.path.join(service_path, "main.py")
    server_js_root = os.path.join(service_path, "server.js")
    main_rs_root = os.path.join(service_path, "main.rs")
    main_cpp_root = os.path.join(service_path, "main.cpp")
    main_go_root = os.path.join(service_path, "main.go")
    
    has_source = (os.path.exists(main_py) or os.path.exists(main_py_root) or 
                  os.path.exists(main_rs) or os.path.exists(main_rs_root) or
                  os.path.exists(main_cpp) or os.path.exists(main_cpp_root) or
                  os.path.exists(server_js) or os.path.exists(server_js_root) or
                  os.path.exists(main_go) or os.path.exists(main_go_root))
    
    if not has_source:
        issues.append("No main source file found")
    
    # Check for Dockerfile
    dockerfile_path = os.path.join(service_path, "Dockerfile")
    if not os.path.exists(dockerfile_path):
        issues.append("No Dockerfile found")
    
    # Check for dependency files
    requirements_path = os.path.join(service_path, "requirements.txt")
    package_json_path = os.path.join(service_path, "package.json")
    cargo_toml_path = os.path.join(service_path, "Cargo.toml")
    go_mod_path = os.path.join(service_path, "go.mod")
    
    has_deps = (os.path.exists(requirements_path) or 
                os.path.exists(package_json_path) or 
                os.path.exists(cargo_toml_path) or 
                os.path.exists(go_mod_path))
    
    if not has_deps and has_source:
        issues.append("No dependency file found")
    
    # Check for health endpoint in source code
    health_check_found = False
    
    # Check Python services
    python_files = [main_py, main_py_root]
    for py_file in python_files:
        if os.path.exists(py_file):
            with open(py_file, "r") as f:
                content = f.read()
            if "/health" in content or "health" in content.lower():
                health_check_found = True
                break
    
    # Check Node.js services
    node_files = [server_js, server_js_root]
    for js_file in node_files:
        if os.path.exists(js_file):
            with open(js_file, "r") as f:
                content = f.read()
            if "/health" in content or "health" in content.lower():
                health_check_found = True
                break
    
    # Check Rust services
    rust_files = [main_rs, main_rs_root]
    for rs_file in rust_files:
        if os.path.exists(rs_file):
            with open(rs_file, "r") as f:
                content = f.read()
            if "health" in content.lower():
                health_check_found = True
                break
    
    # Check C++ services
    cpp_files = [main_cpp, main_cpp_root]
    for cpp_file in cpp_files:
        if os.path.exists(cpp_file):
            with open(cpp_file, "r") as f:
                content = f.read()
            if "health" in content.lower():
                health_check_found = True
                break
    
    # Check Go services
    go_files = [main_go, main_go_root]
    for go_file in go_files:
        if os.path.exists(go_file):
            with open(go_file, "r") as f:
                content = f.read()
            if "/health" in content or "health" in content.lower():
                health_check_found = True
                break
    
    if not health_check_found and has_source:
        issues.append("No health check endpoint found")
    
    return issues

def verify_documentation():
    """Verify documentation files"""
    essential_docs = [
        "README.md",
        "CHANGELOG.md", 
        "DEPLOYMENT_GUIDE.md",
        "COMPLETE_FEATURES_OUTLINE.md",
        "FEATURE_COMPARISON.md",
        "SETUP.md",
        "LICENSE",
        "API_DOCUMENTATION.md"
    ]
    
    missing_docs = []
    for doc in essential_docs:
        if not os.path.exists(doc):
            missing_docs.append(doc)
    
    return missing_docs

def verify_smart_contracts():
    """Verify smart contracts"""
    contracts_dir = "blockchain/smart-contracts/contracts"
    
    if not os.path.exists(contracts_dir):
        return []
    
    contracts = []
    for root, dirs, files in os.walk(contracts_dir):
        for file in files:
            if file.endswith(".sol"):
                contracts.append(os.path.join(root, file))
    
    return contracts

def main():
    """Main verification function"""
    print("=== TigerEx Final Verification ===\n")
    
    # 1. Verify backend services
    print("1. Verifying backend services...")
    services_dir = "backend"
    
    service_dirs = [d for d in os.listdir(services_dir) 
                   if os.path.isdir(os.path.join(services_dir, d))]
    
    services_without_issues = []
    services_with_issues = []
    
    for service_dir in service_dirs:
        service_path = os.path.join(services_dir, service_dir)
        issues = verify_service_structure(service_path)
        
        if not issues:
            services_without_issues.append(service_dir)
        else:
            services_with_issues.append((service_dir, issues))
    
    print(f"Verified {len(service_dirs)} services")
    print(f"Services without issues: {len(services_without_issues)}")
    print(f"Services with issues: {len(services_with_issues)}\n")
    
    if services_with_issues:
        print("Services with issues:")
        for service, issues in services_with_issues:
            print(f"  - {service}:")
            for issue in issues:
                print(f"    * {issue}")
        print()
    
    # 2. Verify documentation
    print("2. Verifying documentation...")
    missing_docs = verify_documentation()
    
    if missing_docs:
        print(f"Missing documentation files: {missing_docs}")
    else:
        print("All essential documentation files are present")
    print()
    
    # 3. Verify smart contracts
    print("3. Verifying smart contracts...")
    contracts = verify_smart_contracts()
    
    if contracts:
        print(f"Found {len(contracts)} smart contracts:")
        for contract in contracts:
            print(f"  - {contract}")
    else:
        print("Smart contracts directory not found")
    print()
    
    # Summary
    print("=== Verification Summary ===")
    if not services_with_issues and not missing_docs:
        print("✅ All verifications passed!")
    else:
        print("❌ Some verifications failed. Please check the issues above.")

if __name__ == "__main__":
    main()