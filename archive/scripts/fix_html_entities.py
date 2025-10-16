#!/usr/bin/env python3
"""
Fix HTML entities in Python files
Converts ", &, <, > to proper characters
"""

import os
import re
from pathlib import Path

def fix_html_entities_in_file(file_path):
    """Fix HTML entities in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace common HTML entities
        replacements = {
            '"': '"',
            '&': '&',
            '<': '<',
            '>': '>',
            ''': "'",
            ''': "'"
        }
        
        new_content = content
        for entity, replacement in replacements.items():
            new_content = new_content.replace(entity, replacement)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Fixed: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix all Python files"""
    root_dir = "."
    python_files = []
    
    # Find all Python files
    for path in Path(root_dir).rglob("*.py"):
        if "node_modules" not in str(path) and "__pycache__" not in str(path):
            python_files.append(str(path))
    
    print(f"Found {len(python_files)} Python files to check...")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_html_entities_in_file(file_path):
            fixed_count += 1
    
    print(f"Fixed HTML entities in {fixed_count} files")

if __name__ == "__main__":
    main()