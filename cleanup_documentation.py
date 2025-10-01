#!/usr/bin/env python3
"""
Documentation cleanup script for TigerEx
Removes duplicate and unnecessary documentation files
"""

import os
import shutil
from pathlib import Path

def cleanup_documentation():
    """Clean up documentation files"""
    
    # Files to keep (essential documentation)
    keep_files = [
        'README.md',
        'FINAL_IMPLEMENTATION_REPORT.md',
        'DEPLOYMENT_GUIDE.md',
        'API_DOCUMENTATION.md',
        'COMPLETE_FEATURES_OUTLINE.md',
        'MISSING_FEATURES_ANALYSIS.md',
        'SETUP.md',
        'LICENSE',
        'CHANGELOG.md'
    ]
    
    # Move all other documentation to archive
    archive_dir = Path('docs/archive')
    archive_dir.mkdir(exist_ok=True)
    
    # List of all .md files
    all_files = list(Path('.').glob('*.md'))
    
    moved_count = 0
    
    for file_path in all_files:
        if file_path.name not in keep_files:
            dest_path = archive_dir / file_path.name
            if file_path.exists():
                shutil.move(str(file_path), str(dest_path))
                moved_count += 1
                print(f"Moved: {file_path.name} -> docs/archive/")
    
    print(f"\nDocumentation cleanup completed:")
    print(f"- Total files: {len(all_files)}")
    print(f"- Kept files: {len(keep_files)}")
    print(f"- Archived files: {moved_count}")
    print(f"- Final count: {len(keep_files)}")

if __name__ == "__main__":
    cleanup_documentation()