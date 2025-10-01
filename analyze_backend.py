#!/usr/bin/env python3
"""
Backend Services Analysis Script
Analyzes all backend services for missing or incomplete files
"""

import os
import json
from pathlib import Path

def analyze_backend_services():
    backend_dir = Path("backend")
    services = {}
    
    # Expected files for different service types
    expected_files = {
        'python': ['Dockerfile', 'requirements.txt', 'src/main.py'],
        'node': ['Dockerfile', 'package.json', 'src/server.js'],
        'go': ['Dockerfile', 'go.mod', 'main.go'],
        'rust': ['Dockerfile', 'Cargo.toml', 'src/main.rs'],
        'cpp': ['Dockerfile', 'CMakeLists.txt', 'src/main.cpp'],
        'java': ['Dockerfile', 'pom.xml', 'src/main/java']
    }
    
    # Iterate through all backend service directories
    for service_dir in sorted(backend_dir.iterdir()):
        if not service_dir.is_dir() or service_dir.name.startswith('.'):
            continue
            
        service_name = service_dir.name
        service_info = {
            'name': service_name,
            'path': str(service_dir),
            'files': [],
            'missing_files': [],
            'service_type': None,
            'status': 'unknown'
        }
        
        # List all files in the service directory
        all_files = []
        for root, dirs, files in os.walk(service_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), service_dir)
                all_files.append(rel_path)
        
        service_info['files'] = all_files
        
        # Determine service type
        if any('requirements.txt' in f for f in all_files):
            service_info['service_type'] = 'python'
        elif any('package.json' in f for f in all_files):
            service_info['service_type'] = 'node'
        elif any('go.mod' in f for f in all_files):
            service_info['service_type'] = 'go'
        elif any('Cargo.toml' in f for f in all_files):
            service_info['service_type'] = 'rust'
        elif any('CMakeLists.txt' in f for f in all_files):
            service_info['service_type'] = 'cpp'
        elif any('pom.xml' in f for f in all_files):
            service_info['service_type'] = 'java'
        
        # Check for missing files based on service type
        if service_info['service_type']:
            expected = expected_files.get(service_info['service_type'], [])
            for exp_file in expected:
                # Check if file exists (flexible matching)
                found = False
                for actual_file in all_files:
                    if exp_file in actual_file or actual_file.endswith(exp_file.split('/')[-1]):
                        found = True
                        break
                if not found:
                    service_info['missing_files'].append(exp_file)
        
        # Determine status
        if not service_info['files']:
            service_info['status'] = 'empty'
        elif service_info['missing_files']:
            service_info['status'] = 'incomplete'
        else:
            service_info['status'] = 'complete'
        
        services[service_name] = service_info
    
    return services

def generate_report(services):
    """Generate a comprehensive report"""
    report = []
    report.append("=" * 80)
    report.append("TIGEREX BACKEND SERVICES ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Summary statistics
    total = len(services)
    complete = sum(1 for s in services.values() if s['status'] == 'complete')
    incomplete = sum(1 for s in services.values() if s['status'] == 'incomplete')
    empty = sum(1 for s in services.values() if s['status'] == 'empty')
    
    report.append(f"Total Services: {total}")
    report.append(f"Complete Services: {complete} ({complete/total*100:.1f}%)")
    report.append(f"Incomplete Services: {incomplete} ({incomplete/total*100:.1f}%)")
    report.append(f"Empty Services: {empty} ({empty/total*100:.1f}%)")
    report.append("")
    
    # Service type breakdown
    report.append("SERVICE TYPE BREAKDOWN:")
    report.append("-" * 80)
    type_counts = {}
    for service in services.values():
        stype = service['service_type'] or 'unknown'
        type_counts[stype] = type_counts.get(stype, 0) + 1
    
    for stype, count in sorted(type_counts.items()):
        report.append(f"  {stype.upper()}: {count} services")
    report.append("")
    
    # Complete services
    report.append("COMPLETE SERVICES:")
    report.append("-" * 80)
    for name, info in sorted(services.items()):
        if info['status'] == 'complete':
            report.append(f"  ✓ {name} ({info['service_type']})")
    report.append("")
    
    # Incomplete services
    report.append("INCOMPLETE SERVICES (MISSING FILES):")
    report.append("-" * 80)
    for name, info in sorted(services.items()):
        if info['status'] == 'incomplete':
            report.append(f"  ⚠ {name} ({info['service_type']})")
            for missing in info['missing_files']:
                report.append(f"      - Missing: {missing}")
    report.append("")
    
    # Empty services
    report.append("EMPTY SERVICES (NO FILES):")
    report.append("-" * 80)
    for name, info in sorted(services.items()):
        if info['status'] == 'empty':
            report.append(f"  ✗ {name}")
    report.append("")
    
    return "\n".join(report)

if __name__ == "__main__":
    print("Analyzing backend services...")
    services = analyze_backend_services()
    
    # Generate and save report
    report = generate_report(services)
    print(report)
    
    # Save detailed JSON
    with open("backend_analysis.json", "w") as f:
        json.dump(services, f, indent=2)
    
    # Save report
    with open("BACKEND_ANALYSIS_REPORT.md", "w") as f:
        f.write(report)
    
    print("\nAnalysis complete!")
    print("- Detailed JSON: backend_analysis.json")
    print("- Report: BACKEND_ANALYSIS_REPORT.md")