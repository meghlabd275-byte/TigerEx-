#!/usr/bin/env python3
"""
Frontend Analysis Script
Analyzes all frontend files for missing or incomplete components
"""

import os
import json
from pathlib import Path

def analyze_frontend():
    frontend_dir = Path("frontend")
    src_dir = Path("src")
    
    analysis = {
        'frontend_structure': {},
        'src_structure': {},
        'missing_files': [],
        'incomplete_areas': []
    }
    
    # Analyze frontend directory
    if frontend_dir.exists():
        for item in frontend_dir.iterdir():
            if item.is_dir():
                files = list_files_recursive(item)
                analysis['frontend_structure'][item.name] = {
                    'path': str(item),
                    'files': files,
                    'file_count': len(files)
                }
    
    # Analyze src directory
    if src_dir.exists():
        for item in src_dir.iterdir():
            if item.is_dir():
                files = list_files_recursive(item)
                analysis['src_structure'][item.name] = {
                    'path': str(item),
                    'files': files,
                    'file_count': len(files)
                }
    
    # Check for common missing files
    check_missing_files(analysis)
    
    return analysis

def list_files_recursive(directory):
    """List all files in a directory recursively"""
    files = []
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            rel_path = os.path.relpath(os.path.join(root, filename), directory)
            files.append(rel_path)
    return files

def check_missing_files(analysis):
    """Check for commonly missing frontend files"""
    
    # Expected frontend structure
    expected_structure = {
        'components': ['layout', 'trading', 'ui'],
        'pages': ['admin', 'trading', 'user'],
        'hooks': ['useAuth.tsx', 'useWebSocket.ts'],
        'utils': ['api.ts'],
        'store': ['index.ts', 'slices']
    }
    
    src_dir = Path("src")
    if src_dir.exists():
        for expected_dir, expected_items in expected_structure.items():
            dir_path = src_dir / expected_dir
            if not dir_path.exists():
                analysis['missing_files'].append(f"src/{expected_dir}/")
            else:
                for item in expected_items:
                    item_path = dir_path / item
                    if not item_path.exists():
                        analysis['missing_files'].append(f"src/{expected_dir}/{item}")

def generate_frontend_report(analysis):
    """Generate a comprehensive frontend report"""
    report = []
    report.append("=" * 80)
    report.append("TIGEREX FRONTEND ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Frontend structure
    report.append("FRONTEND DIRECTORY STRUCTURE:")
    report.append("-" * 80)
    for name, info in sorted(analysis['frontend_structure'].items()):
        report.append(f"  📁 {name}/")
        report.append(f"     Files: {info['file_count']}")
        if info['file_count'] > 0:
            # Show first few files
            for file in sorted(info['files'])[:5]:
                report.append(f"       - {file}")
            if info['file_count'] > 5:
                report.append(f"       ... and {info['file_count'] - 5} more files")
    report.append("")
    
    # Src structure
    report.append("SRC DIRECTORY STRUCTURE:")
    report.append("-" * 80)
    for name, info in sorted(analysis['src_structure'].items()):
        report.append(f"  📁 {name}/")
        report.append(f"     Files: {info['file_count']}")
        if info['file_count'] > 0:
            # Show first few files
            for file in sorted(info['files'])[:5]:
                report.append(f"       - {file}")
            if info['file_count'] > 5:
                report.append(f"       ... and {info['file_count'] - 5} more files")
    report.append("")
    
    # Missing files
    if analysis['missing_files']:
        report.append("MISSING FILES:")
        report.append("-" * 80)
        for missing in analysis['missing_files']:
            report.append(f"  ✗ {missing}")
    else:
        report.append("✓ No critical files missing")
    report.append("")
    
    return "\n".join(report)

if __name__ == "__main__":
    print("Analyzing frontend structure...")
    analysis = analyze_frontend()
    
    # Generate and save report
    report = generate_frontend_report(analysis)
    print(report)
    
    # Save detailed JSON
    with open("frontend_analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)
    
    # Save report
    with open("FRONTEND_ANALYSIS_REPORT.md", "w") as f:
        f.write(report)
    
    print("\nAnalysis complete!")
    print("- Detailed JSON: frontend_analysis.json")
    print("- Report: FRONTEND_ANALYSIS_REPORT.md")