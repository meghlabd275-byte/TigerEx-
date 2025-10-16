#!/usr/bin/env python3
"""
Check for missing implementations, bugs, and code issues
"""

import os
import re
from pathlib import Path

def check_python_file(filepath):
    """Check Python file for common issues"""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            
            # Check for TODO/FIXME comments
            for i, line in enumerate(lines, 1):
                if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                    issues.append({
                        'type': 'TODO',
                        'line': i,
                        'content': line.strip()
                    })
                
                # Check for pass statements in functions (potential incomplete implementation)
                if re.search(r'def\s+\w+.*:\s*pass', line):
                    issues.append({
                        'type': 'INCOMPLETE',
                        'line': i,
                        'content': 'Function with only pass statement'
                    })
                
                # Check for NotImplementedError
                if 'NotImplementedError' in line:
                    issues.append({
                        'type': 'NOT_IMPLEMENTED',
                        'line': i,
                        'content': line.strip()
                    })
    
    except Exception as e:
        issues.append({
            'type': 'ERROR',
            'line': 0,
            'content': f'Error reading file: {str(e)}'
        })
    
    return issues

def check_javascript_file(filepath):
    """Check JavaScript file for common issues"""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            
            # Check for TODO/FIXME comments
            for i, line in enumerate(lines, 1):
                if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                    issues.append({
                        'type': 'TODO',
                        'line': i,
                        'content': line.strip()
                    })
                
                # Check for empty functions
                if re.search(r'function\s+\w+.*{\s*}', line):
                    issues.append({
                        'type': 'INCOMPLETE',
                        'line': i,
                        'content': 'Empty function'
                    })
    
    except Exception as e:
        issues.append({
            'type': 'ERROR',
            'line': 0,
            'content': f'Error reading file: {str(e)}'
        })
    
    return issues

def scan_directory(directory, extensions=['.py', '.js', '.ts']):
    """Scan directory for code issues"""
    all_issues = {}
    
    for root, dirs, files in os.walk(directory):
        # Skip node_modules and other common directories
        dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git', 'venv', 'env']]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, directory)
                
                if file.endswith('.py'):
                    issues = check_python_file(filepath)
                elif file.endswith(('.js', '.ts')):
                    issues = check_javascript_file(filepath)
                else:
                    continue
                
                if issues:
                    all_issues[rel_path] = issues
    
    return all_issues

def check_critical_services():
    """Check critical services for implementation completeness"""
    print("\n" + "="*80)
    print("🔍 Checking Critical Services")
    print("="*80)
    
    critical_services = [
        'backend/spot-trading',
        'backend/futures-trading',
        'backend/wallet-service',
        'backend/auth-service',
        'backend/unified-admin-panel',
        'backend/dex-integration',
        'backend/matching-engine'
    ]
    
    for service in critical_services:
        if os.path.exists(service):
            print(f"\n📦 Scanning: {service}")
            issues = scan_directory(service)
            
            if issues:
                print(f"   ⚠️  Found {len(issues)} files with issues")
                for filepath, file_issues in list(issues.items())[:3]:  # Show first 3
                    print(f"      - {filepath}: {len(file_issues)} issues")
            else:
                print(f"   ✅ No issues found")

def check_missing_dependencies():
    """Check for missing dependencies in requirements files"""
    print("\n" + "="*80)
    print("📦 Checking Dependencies")
    print("="*80)
    
    requirements_files = []
    for root, dirs, files in os.walk('backend'):
        for file in files:
            if file == 'requirements.txt':
                requirements_files.append(os.path.join(root, file))
    
    print(f"Found {len(requirements_files)} requirements.txt files")
    
    # Check for common missing dependencies
    common_deps = ['fastapi', 'flask', 'sqlalchemy', 'pydantic', 'web3', 'ccxt']
    
    for req_file in requirements_files[:5]:  # Check first 5
        try:
            with open(req_file, 'r') as f:
                content = f.read().lower()
                missing = [dep for dep in common_deps if dep not in content]
                if missing:
                    print(f"\n   {req_file}")
                    print(f"   Potentially missing: {', '.join(missing)}")
        except:
            pass

def main():
    print("="*80)
    print("TigerEx Implementation Check")
    print("="*80)
    
    # Check critical services
    check_critical_services()
    
    # Check dependencies
    check_missing_dependencies()
    
    print("\n" + "="*80)
    print("✅ Implementation Check Complete")
    print("="*80)

if __name__ == '__main__':
    main()