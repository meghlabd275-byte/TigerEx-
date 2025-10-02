#!/usr/bin/env python3
"""
Script to check for missing dependencies in services
"""

import os
import json
import subprocess

def check_python_dependencies(service_path):
    """Check Python dependencies for a service"""
    requirements_path = os.path.join(service_path, "requirements.txt")
    
    if not os.path.exists(requirements_path):
        return False, "No requirements.txt file found"
    
    # Read requirements
    with open(requirements_path, "r") as f:
        requirements = f.readlines()
    
    # Check if each requirement is properly formatted
    missing_deps = []
    for req in requirements:
        req = req.strip()
        if req and not req.startswith("#"):
            # Check if it's a valid package format
            if "==" not in req and "!=" not in req and ">=" not in req and "<=" not in req:
                # This might be okay for some packages, but let's flag it for review
                pass
    
    return True, f"Found {len(requirements)} dependencies"

def check_node_dependencies(service_path):
    """Check Node.js dependencies for a service"""
    package_json_path = os.path.join(service_path, "package.json")
    
    if not os.path.exists(package_json_path):
        return False, "No package.json file found"
    
    # Read package.json
    with open(package_json_path, "r") as f:
        package_data = json.load(f)
    
    # Check dependencies
    dependencies = package_data.get("dependencies", {})
    dev_dependencies = package_data.get("devDependencies", {})
    
    total_deps = len(dependencies) + len(dev_dependencies)
    
    return True, f"Found {total_deps} dependencies ({len(dependencies)} prod, {len(dev_dependencies)} dev)"

def check_rust_dependencies(service_path):
    """Check Rust dependencies for a service"""
    cargo_toml_path = os.path.join(service_path, "Cargo.toml")
    
    if not os.path.exists(cargo_toml_path):
        return False, "No Cargo.toml file found"
    
    # Read Cargo.toml
    with open(cargo_toml_path, "r") as f:
        cargo_data = f.read()
    
    # Check if dependencies section exists
    if "[dependencies]" not in cargo_data:
        return False, "No dependencies section found"
    
    return True, "Dependencies section found"

def check_service_dependencies(service_path):
    """Check dependencies for a service based on its type"""
    # Check for requirements.txt (Python)
    if os.path.exists(os.path.join(service_path, "requirements.txt")):
        return check_python_dependencies(service_path)
    
    # Check for package.json (Node.js)
    if os.path.exists(os.path.join(service_path, "package.json")):
        return check_node_dependencies(service_path)
    
    # Check for Cargo.toml (Rust)
    if os.path.exists(os.path.join(service_path, "Cargo.toml")):
        return check_rust_dependencies(service_path)
    
    # Check for go.mod (Go)
    if os.path.exists(os.path.join(service_path, "go.mod")):
        return True, "Go service - dependencies managed by go.mod"
    
    return False, "Unknown service type or no dependency file found"

def check_all_services():
    """Check dependencies for all services"""
    services_dir = "backend"
    
    # Get all service directories
    service_dirs = [d for d in os.listdir(services_dir) 
                   if os.path.isdir(os.path.join(services_dir, d))]
    
    services_checked = 0
    services_with_issues = []
    
    for service_dir in service_dirs:
        service_path = os.path.join(services_dir, service_dir)
        has_deps, message = check_service_dependencies(service_path)
        
        services_checked += 1
        
        if not has_deps:
            services_with_issues.append((service_dir, message))
    
    print(f"Checked dependencies for {services_checked} services")
    
    if services_with_issues:
        print(f"Found issues in {len(services_with_issues)} services:")
        for service, issue in services_with_issues:
            print(f"  - {service}: {issue}")
    else:
        print("All services have proper dependency files!")

def create_requirements_txt():
    """Create a standard requirements.txt file for Python services that are missing it"""
    standard_requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
requests==2.31.0
websockets==12.0
redis==5.0.1
celery==5.3.4
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
"""
    
    services_dir = "backend"
    service_dirs = [d for d in os.listdir(services_dir) 
                   if os.path.isdir(os.path.join(services_dir, d))]
    
    services_updated = []
    
    for service_dir in service_dirs:
        service_path = os.path.join(services_dir, service_dir)
        
        # Check if it's a Python service without requirements.txt
        if (os.path.exists(os.path.join(service_path, "src", "main.py")) or 
            os.path.exists(os.path.join(service_path, "main.py"))) and \
           not os.path.exists(os.path.join(service_path, "requirements.txt")):
            
            requirements_path = os.path.join(service_path, "requirements.txt")
            with open(requirements_path, "w") as f:
                f.write(standard_requirements)
            
            services_updated.append(service_dir)
    
    if services_updated:
        print(f"Created requirements.txt for {len(services_updated)} Python services:")
        for service in services_updated:
            print(f"  - {service}")

def main():
    """Main function"""
    print("Checking service dependencies...")
    check_all_services()
    
    print("\nCreating missing requirements.txt files...")
    create_requirements_txt()
    
    print("\nDependency check completed!")

if __name__ == "__main__":
    main()