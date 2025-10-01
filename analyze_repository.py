#!/usr/bin/env python3
"""
Comprehensive Repository Analysis Script
Analyzes all backend services, smart contracts, and documentation
"""

import os
import json
from pathlib import Path
from collections import defaultdict

def analyze_backend_services():
    """Analyze all backend services"""
    backend_path = Path("backend")
    services = []
    
    if not backend_path.exists():
        return []
    
    for service_dir in sorted(backend_path.iterdir()):
        if service_dir.is_dir():
            service_info = {
                "name": service_dir.name,
                "path": str(service_dir),
                "has_dockerfile": (service_dir / "Dockerfile").exists(),
                "has_requirements": (service_dir / "requirements.txt").exists(),
                "has_main": False,
                "language": "unknown"
            }
            
            # Check for main files
            main_files = [
                "main.py", "app.py", "server.py", "index.js", 
                "main.go", "main.rs", "main.cpp", "Main.java"
            ]
            
            for main_file in main_files:
                if (service_dir / main_file).exists():
                    service_info["has_main"] = True
                    if main_file.endswith(".py"):
                        service_info["language"] = "Python"
                    elif main_file.endswith(".js"):
                        service_info["language"] = "Node.js"
                    elif main_file.endswith(".go"):
                        service_info["language"] = "Go"
                    elif main_file.endswith(".rs"):
                        service_info["language"] = "Rust"
                    elif main_file.endswith(".cpp"):
                        service_info["language"] = "C++"
                    elif main_file.endswith(".java"):
                        service_info["language"] = "Java"
                    break
            
            services.append(service_info)
    
    return services

def analyze_smart_contracts():
    """Analyze smart contracts"""
    contracts_path = Path("blockchain/smart-contracts/contracts")
    contracts = []
    
    if not contracts_path.exists():
        return []
    
    for contract_file in contracts_path.rglob("*.sol"):
        contracts.append({
            "name": contract_file.stem,
            "path": str(contract_file),
            "category": contract_file.parent.name
        })
    
    return contracts

def analyze_documentation():
    """Analyze documentation files"""
    docs = []
    
    # Root level docs
    for doc_file in Path(".").glob("*.md"):
        docs.append({
            "name": doc_file.name,
            "path": str(doc_file),
            "location": "root",
            "size": doc_file.stat().st_size
        })
    
    # Archive docs
    archive_path = Path("docs/archive")
    if archive_path.exists():
        for doc_file in archive_path.rglob("*.md"):
            docs.append({
                "name": doc_file.name,
                "path": str(doc_file),
                "location": "archive",
                "size": doc_file.stat().st_size
            })
    
    return docs

def check_service_completeness(services):
    """Check which services are incomplete"""
    incomplete = []
    
    for service in services:
        issues = []
        
        if not service["has_dockerfile"]:
            issues.append("Missing Dockerfile")
        if not service["has_requirements"] and service["language"] == "Python":
            issues.append("Missing requirements.txt")
        if not service["has_main"]:
            issues.append("Missing main file")
        
        if issues:
            incomplete.append({
                "service": service["name"],
                "issues": issues
            })
    
    return incomplete

def main():
    print("=" * 80)
    print("COMPREHENSIVE REPOSITORY ANALYSIS")
    print("=" * 80)
    
    # Analyze backend services
    print("\n📦 BACKEND SERVICES ANALYSIS")
    print("-" * 80)
    services = analyze_backend_services()
    print(f"Total Services: {len(services)}")
    
    # Group by language
    by_language = defaultdict(int)
    for service in services:
        by_language[service["language"]] += 1
    
    print("\nServices by Language:")
    for lang, count in sorted(by_language.items(), key=lambda x: x[1], reverse=True):
        print(f"  {lang}: {count}")
    
    # Check completeness
    incomplete = check_service_completeness(services)
    if incomplete:
        print(f"\n⚠️  Incomplete Services: {len(incomplete)}")
        for item in incomplete[:10]:  # Show first 10
            print(f"  - {item['service']}: {', '.join(item['issues'])}")
    else:
        print("\n✅ All services are complete!")
    
    # Analyze smart contracts
    print("\n" + "=" * 80)
    print("📜 SMART CONTRACTS ANALYSIS")
    print("-" * 80)
    contracts = analyze_smart_contracts()
    print(f"Total Contracts: {len(contracts)}")
    
    if contracts:
        print("\nContracts by Category:")
        by_category = defaultdict(list)
        for contract in contracts:
            by_category[contract["category"]].append(contract["name"])
        
        for category, names in sorted(by_category.items()):
            print(f"  {category}:")
            for name in names:
                print(f"    - {name}")
    
    # Analyze documentation
    print("\n" + "=" * 80)
    print("📚 DOCUMENTATION ANALYSIS")
    print("-" * 80)
    docs = analyze_documentation()
    
    root_docs = [d for d in docs if d["location"] == "root"]
    archive_docs = [d for d in docs if d["location"] == "archive"]
    
    print(f"Root Documentation Files: {len(root_docs)}")
    print(f"Archived Documentation Files: {len(archive_docs)}")
    print(f"Total Documentation Files: {len(docs)}")
    
    # Find duplicates
    print("\n🔍 Checking for duplicate documentation...")
    doc_names = defaultdict(list)
    for doc in docs:
        doc_names[doc["name"]].append(doc["path"])
    
    duplicates = {name: paths for name, paths in doc_names.items() if len(paths) > 1}
    if duplicates:
        print(f"\n⚠️  Found {len(duplicates)} duplicate document names:")
        for name, paths in list(duplicates.items())[:10]:  # Show first 10
            print(f"  {name}:")
            for path in paths:
                print(f"    - {path}")
    else:
        print("✅ No duplicate documentation found!")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("-" * 80)
    print(f"Backend Services: {len(services)}")
    print(f"Smart Contracts: {len(contracts)}")
    print(f"Documentation Files: {len(docs)}")
    print(f"Incomplete Services: {len(incomplete)}")
    print(f"Duplicate Docs: {len(duplicates)}")
    
    # Save detailed report
    report = {
        "services": services,
        "contracts": contracts,
        "documentation": docs,
        "incomplete_services": incomplete,
        "duplicate_docs": duplicates
    }
    
    with open("repository_analysis.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n✅ Detailed report saved to: repository_analysis.json")
    print("=" * 80)

if __name__ == "__main__":
    main()