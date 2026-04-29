#!/usr/bin/env python3
"""
Enhanced Add responsive CSS and auth guard to all HTML files in the TigerEx project.
This script ensures all pages are responsive and have authentication protection.
Handles all edge cases.
"""

import os
import re

def process_html_file(filepath):
    """Process a single HTML file to add responsive CSS and auth guard."""
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    modified = False
    
    # Check if responsive.css is already included
    has_responsive = 'responsive.css' in content
    
    if not has_responsive:
        # Try adding after theme.css with assets path
        if '<link rel="stylesheet" href="assets/css/theme.css">' in content:
            content = re.sub(
                r'(<link rel="stylesheet" href="assets/css/theme.css">)',
                r'\1\n    <link rel="stylesheet" href="assets/css/responsive.css">',
                content
            )
            modified = True
        # Try theme.css without assets path
        elif '<link rel="stylesheet" href="theme.css">' in content:
            content = re.sub(
                r'(<link rel="stylesheet" href="theme.css">)',
                r'\1\n    <link rel="stylesheet" href="assets/css/responsive.css">',
                content
            )
            modified = True
        # Try css/theme.css path
        elif '<link rel="stylesheet" href="css/theme.css">' in content:
            content = re.sub(
                r'(<link rel="stylesheet" href="css/theme.css">)',
                r'\1\n    <link rel="stylesheet" href="assets/css/responsive.css">',
                content
            )
            modified = True
        # No theme.css - add after any stylesheet or before </head>
        elif '<link rel="stylesheet"' in content:
            content = re.sub(
                r'(<link rel="stylesheet"[^>]*>)',
                r'\1\n    <link rel="stylesheet" href="assets/css/responsive.css">',
                content
            )
            modified = True
        elif '</head>' in content:
            content = re.sub(
                r'(</head>)',
                r'    <link rel="stylesheet" href="assets/css/responsive.css">\n\1',
                content
            )
            modified = True
    
    if not has_responsive:
        print(f"  Added responsive.css to {os.path.basename(filepath)}")
    
    # Check if auth-guard.js is already included
    if 'auth-guard.js' not in content:
        if '</body>' in content:
            content = re.sub(
                r'(</body>)',
                r'    <script src="assets/js/auth-guard.js"></script>\n</body>',
                content
            )
            modified = True
            print(f"  Added auth-guard.js to {os.path.basename(filepath)}")
    
    # Write back if modified
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def find_html_files(root_dir):
    """Find all HTML files in the directory tree."""
    html_files = []
    
    exclude_dirs = {'node_modules', 'vendor', '.git', 'dist', 'build', 'cache', '.next', '__pycache__'}
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
        for filename in filenames:
            if filename.endswith('.html'):
                html_files.append(os.path.join(dirpath, filename))
    
    return html_files

def main():
    project_dir = '/workspace/project/TigerEx-'
    
    print("Finding all HTML files...")
    html_files = find_html_files(project_dir)
    print(f"Found {len(html_files)} HTML files\n")
    
    print("Processing files...")
    processed = 0
    
    for filepath in sorted(html_files):
        try:
            if process_html_file(filepath):
                processed += 1
        except Exception as e:
            print(f"  Error processing {filepath}: {e}")
    
    print(f"\nProcessed {processed} files")
    print("Done!")

if __name__ == '__main__':
    main()