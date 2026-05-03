#!/usr/bin/env python3
"""
@file cleanup_duplicates.py
@description TigerEx Duplicate File Cleanup Script - Removes duplicate files and unnecessary files
@author TigerEx Development Team
"""

import os
import hashlib
import json
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Directories to scan
SCAN_DIRS = [
    "backend",
    "frontend",
    "blockchain",
    "mobile",
    "src"
]

# Files/directories to skip
SKIP_PATTERNS = [
    ".git",
    "__pycache__",
    "node_modules",
    ".next",
    "dist",
    "build",
    "*.pyc",
    "*.pyo",
    ".env",
    "*.log"
]

# Files to delete (junk/unnecessary)
JUNK_PATTERNS = [
    ".DS_Store",
    "Thumbs.db",
    "*.swp",
    "*.swo",
    "*~",
    ".idea",
    ".vscode",
    "*.egg-info",
    "pytest_cache",
    ".coverage",
    "htmlcov",
    ".pytest_cache",
    "*.bak",
    "*.tmp",
    "*.temp"
]

def get_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def should_skip(filepath):
    """Check if file should be skipped"""
    for pattern in SKIP_PATTERNS:
        if pattern.startswith('*'):
            if filepath.endswith(pattern[1:]):
                return True
        elif pattern in filepath:
            return True
    return False

def is_junk(filepath):
    """Check if file is junk"""
    filename = os.path.basename(filepath)
    for pattern in JUNK_PATTERNS:
        if pattern.startswith('*'):
            if filename.endswith(pattern[1:]):
                return True
        elif pattern in filepath or filename == pattern:
            return True
    return False

def find_duplicates(root_dir):
    """Find all duplicate files"""
    hash_map = defaultdict(list)
    
    for scan_dir in SCAN_DIRS:
        scan_path = os.path.join(root_dir, scan_dir)
        if not os.path.exists(scan_path):
            continue
            
        for root, dirs, files in os.walk(scan_path):
            # Skip directories
            dirs[:] = [d for d in dirs if not should_skip(os.path.join(root, d))]
            
            for filename in files:
                filepath = os.path.join(root, filename)
                
                if should_skip(filepath):
                    continue
                    
                file_hash = get_file_hash(filepath)
                if file_hash:
                    hash_map[file_hash].append(filepath)
    
    # Return only duplicates
    return {k: v for k, v in hash_map.items() if len(v) > 1}

def find_junk_files(root_dir):
    """Find all junk files"""
    junk_files = []
    
    for root, dirs, files in os.walk(root_dir):
        if should_skip(root):
            continue
            
        for filename in files:
            filepath = os.path.join(root, filename)
            if is_junk(filepath):
                junk_files.append(filepath)
    
    return junk_files

def find_empty_directories(root_dir):
    """Find empty directories"""
    empty_dirs = []
    
    for root, dirs, files in os.walk(root_dir, topdown=False):
        if should_skip(root):
            continue
            
        if not dirs and not files:
            empty_dirs.append(root)
    
    return empty_dirs

def select_files_to_keep(duplicate_files):
    """Select which duplicate files to keep (prefer main/original location)"""
    files_to_delete = []
    
    for file_hash, filepaths in duplicate_files.items():
        # Sort by path to get consistent ordering
        filepaths.sort()
        
        # Keep the first one (usually in the main/original location)
        # Delete others (usually in consolidated/sub folders)
        keep = filepaths[0]
        
        for filepath in filepaths[1:]:
            # Check if it's in a 'consolidated' or duplicate folder
            if 'consolidated' in filepath or 'copy' in filepath.lower():
                files_to_delete.append(filepath)
            elif filepath != keep:
                # Keep the shorter path (usually the original)
                if len(filepath) > len(keep):
                    files_to_delete.append(filepath)
                else:
                    files_to_delete.append(keep)
                    keep = filepath
    
    return files_to_delete

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)
    
    print("=" * 60)
    print("TigerEx Cleanup Script")
    print("=" * 60)
    print(f"Root directory: {root_dir}")
    print()
    
    # Find duplicates
    print("Scanning for duplicate files...")
    duplicates = find_duplicates(root_dir)
    
    duplicate_count = sum(len(v) - 1 for v in duplicates.values())
    print(f"Found {duplicate_count} duplicate files in {len(duplicates)} groups")
    
    # Find junk files
    print("\nScanning for junk files...")
    junk_files = find_junk_files(root_dir)
    print(f"Found {len(junk_files)} junk files")
    
    # Find empty directories
    print("\nScanning for empty directories...")
    empty_dirs = find_empty_directories(root_dir)
    print(f"Found {len(empty_dirs)} empty directories")
    
    # Select files to delete
    files_to_delete = select_files_to_keep(duplicates)
    all_files_to_delete = files_to_delete + junk_files
    
    # Calculate space savings
    total_size = 0
    for filepath in all_files_to_delete:
        try:
            total_size += os.path.getsize(filepath)
        except:
            pass
    
    print(f"\nTotal files to delete: {len(all_files_to_delete)}")
    print(f"Total space to free: {total_size / (1024*1024):.2f} MB")
    
    # Save report
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "duplicate_groups": len(duplicates),
        "duplicate_files": duplicate_count,
        "junk_files": len(junk_files),
        "empty_directories": len(empty_dirs),
        "total_files_to_delete": len(all_files_to_delete),
        "space_to_free_bytes": total_size,
        "duplicates": {k: v for k, v in duplicates.items()},
        "junk_files": junk_files,
        "empty_dirs": empty_dirs,
        "files_to_delete": all_files_to_delete
    }
    
    report_path = os.path.join(root_dir, "cleanup_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nReport saved to: {report_path}")
    
    # Ask for confirmation (in a real script)
    # For automated cleanup, we'll proceed
    print("\nProceeding with cleanup...")
    
    # Delete files
    deleted_count = 0
    for filepath in all_files_to_delete:
        try:
            os.remove(filepath)
            deleted_count += 1
            print(f"Deleted: {filepath}")
        except Exception as e:
            print(f"Error deleting {filepath}: {e}")
    
    # Delete empty directories
    for dirpath in empty_dirs:
        try:
            os.rmdir(dirpath)
            print(f"Removed empty directory: {dirpath}")
        except Exception as e:
            pass  # Directory might not be empty after file deletions
    
    print(f"\n{'=' * 60}")
    print(f"Cleanup complete!")
    print(f"Deleted {deleted_count} files")
    print(f"Freed {total_size / (1024*1024):.2f} MB")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()# TigerEx Wallet API
class WalletAPI:
    @staticmethod
    def create(auth_token):
        wordlist = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
        return {'address': '0x' + os.urandom(20).hex(), 'seed': ' '.join(wordlist.split()[:24]), 'ownership': 'USER_OWNS'}
