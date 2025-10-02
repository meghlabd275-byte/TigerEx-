#!/usr/bin/env python3
"""
Documentation cleanup script for TigerEx
Identifies and removes unnecessary documentation files
"""

import os
import shutil
from datetime import datetime

# Essential documentation files that should be kept
ESSENTIAL_DOCS = {
    "README.md",
    "CHANGELOG.md",
    "DEPLOYMENT_GUIDE.md",
    "COMPLETE_FEATURES_OUTLINE.md",
    "FEATURE_COMPARISON.md",
    "SETUP.md",
    "LICENSE",
    "API_DOCUMENTATION.md"
}

# Files to be archived (moved to docs/archive/)
ARCHIVE_DOCS = {
    "CLEANUP_ANALYSIS.md",
    "COMPREHENSIVE_AUDIT_REPORT.md",
    "DEPLOYMENT_READY.md",
    "DEVELOPMENT_ROADMAP.md",
    "FINAL_CLEANED_DOCUMENTATION.md",
    "FINAL_COMPREHENSIVE_AUDIT.md",
    "FINAL_DELIVERY_REPORT.md",
    "FINAL_SUMMARY.md",
    "FINAL_VERIFICATION.md",
    "FINAL_VERIFICATION_REPORT.md",
    "GITHUB_FINAL_STATUS.md",
    "IMPLEMENTATION_COMPLETE.md",
    "IMPLEMENTATION_STATUS_REPORT.md",
    "IMPLEMENTATION_SUMMARY.md",
    "STATUS_UPDATE.md",
    "WHATS_NEW.md"
}

def cleanup_documentation():
    """Clean up unnecessary documentation files"""
    print("Starting documentation cleanup...")
    
    # Create docs directory if it doesn't exist
    if not os.path.exists("docs"):
        os.makedirs("docs")
    
    # Create archive directory if it doesn't exist
    archive_dir = "docs/archive"
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        print(f"Created archive directory: {archive_dir}")
    
    # Move archive files to archive directory
    for filename in ARCHIVE_DOCS:
        if os.path.exists(filename):
            shutil.move(filename, os.path.join(archive_dir, filename))
            print(f"Archived: {filename}")
    
    # Remove other unnecessary markdown files
    all_md_files = [f for f in os.listdir(".") if f.endswith(".md")]
    for filename in all_md_files:
        if filename not in ESSENTIAL_DOCS and filename in ARCHIVE_DOCS:
            # File already moved to archive
            continue
        elif filename not in ESSENTIAL_DOCS:
            os.remove(filename)
            print(f"Removed: {filename}")
    
    print("Documentation cleanup completed!")

def main():
    """Main function"""
    # Clean up documentation
    cleanup_documentation()
    
    print("Documentation reorganization completed!")

if __name__ == "__main__":
    main()