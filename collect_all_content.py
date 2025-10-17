#!/usr/bin/env python3
"""
Collect all code and documentation from all branches and tags
Consolidate into main branch with proper versioning
"""

import os
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.returncode == 0, result.stdout, result.stderr

def collect_from_branch(branch_name):
    """Collect files from a specific branch"""
    print(f"Collecting from branch: {branch_name}")
    
    # Checkout the branch
    success, _, error = run_command(f"git checkout {branch_name}")
    if not success:
        print(f"Failed to checkout {branch_name}: {error}")
        return
    
    # Create directory for this branch
    branch_dir = f"collected_content/{branch_name.replace('/', '_')}"
    os.makedirs(branch_dir, exist_ok=True)
    
    # Collect all code files
    code_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.php', '.rb', '.swift', '.kt']
    
    for ext in code_extensions:
        success, output, _ = run_command(f"find . -name '*{ext}' -type f")
        if success and output.strip():
            for file_path in output.strip().split('\n'):
                if file_path and os.path.isfile(file_path):
                    dest_path = os.path.join(branch_dir, file_path[2:])  # Remove './'
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(file_path, dest_path)
    
    # Collect documentation files
    success, output, _ = run_command("find . -name '*.md' -type f")
    if success and output.strip():
        for file_path in output.strip().split('\n'):
            if file_path and os.path.isfile(file_path):
                dest_path = os.path.join(branch_dir, file_path[2:])
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(file_path, dest_path)

def collect_from_tag(tag_name):
    """Collect files from a specific tag"""
    print(f"Collecting from tag: {tag_name}")
    
    # Checkout the tag
    success, _, error = run_command(f"git checkout {tag_name}")
    if not success:
        print(f"Failed to checkout {tag_name}: {error}")
        return
    
    # Create directory for this tag
    tag_dir = f"collected_content/tags/{tag_name}"
    os.makedirs(tag_dir, exist_ok=True)
    
    # Collect all code files
    code_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.php', '.rb', '.swift', '.kt']
    
    for ext in code_extensions:
        success, output, _ = run_command(f"find . -name '*{ext}' -type f")
        if success and output.strip():
            for file_path in output.strip().split('\n'):
                if file_path and os.path.isfile(file_path):
                    dest_path = os.path.join(tag_dir, file_path[2:])
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(file_path, dest_path)
    
    # Collect documentation files
    success, output, _ = run_command("find . -name '*.md' -type f")
    if success and output.strip():
        for file_path in output.strip().split('\n'):
            if file_path and os.path.isfile(file_path):
                dest_path = os.path.join(tag_dir, file_path[2:])
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(file_path, dest_path)

def consolidate_to_main():
    """Consolidate all collected content to main branch"""
    print("Consolidating content to main branch...")
    
    # Switch back to main
    run_command("git checkout main")
    
    # Create versioned directories
    os.makedirs("versioned_code", exist_ok=True)
    os.makedirs("versioned_docs", exist_ok=True)
    
    # Process collected content
    collected_dir = Path("collected_content")
    if collected_dir.exists():
        for item in collected_dir.iterdir():
            if item.is_dir():
                version_name = item.name
                print(f"Processing {version_name}")
                
                # Copy code files with versioning
                code_dir = item / "backend"
                if code_dir.exists():
                    dest_code_dir = Path(f"versioned_code/{version_name}/backend")
                    shutil.copytree(code_dir, dest_code_dir, dirs_exist_ok=True)
                
                # Copy frontend files with versioning
                frontend_dir = item / "frontend"
                if frontend_dir.exists():
                    dest_frontend_dir = Path(f"versioned_code/{version_name}/frontend")
                    shutil.copytree(frontend_dir, dest_frontend_dir, dirs_exist_ok=True)
                
                # Copy documentation with versioning
                for md_file in item.glob("**/*.md"):
                    relative_path = md_file.relative_to(item)
                    dest_path = Path(f"versioned_docs/{version_name}") / relative_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(md_file, dest_path)

def add_version_headers():
    """Add version headers to all code files"""
    print("Adding version headers to code files...")
    
    versioned_code_dir = Path("versioned_code")
    if not versioned_code_dir.exists():
        return
    
    for version_dir in versioned_code_dir.iterdir():
        if version_dir.is_dir():
            version_name = version_dir.name
            print(f"Adding headers for version: {version_name}")
            
            for code_file in version_dir.rglob("*"):
                if code_file.is_file() and code_file.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx']:
                    # Read original content
                    try:
                        with open(code_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Add version header
                        header = f"""/*
 * TigerEx Exchange Platform
 * Version: {version_name}
 * File: {code_file.relative_to(version_dir)}
 * 
 * Complete cryptocurrency exchange platform
 * with CEX/DEX hybrid functionality
 */

"""
                        
                        # Write back with header
                        with open(code_file, 'w', encoding='utf-8') as f:
                            f.write(header + content)
                    
                    except Exception as e:
                        print(f"Error processing {code_file}: {e}")

def main():
    """Main consolidation process"""
    print("Starting content collection and consolidation...")
    
    # Create collection directory
    os.makedirs("collected_content", exist_ok=True)
    
    # Get all branches
    success, output, _ = run_command("git branch -r")
    if success:
        branches = [line.strip() for line in output.split('\n') if line.strip() and 'origin/' in line]
        branches = [b.replace('origin/', '') for b in branches if 'HEAD' not in b]
        
        for branch in branches:
            if branch != 'main':  # Skip main as we're already on it
                collect_from_branch(branch)
    
    # Get all tags
    success, output, _ = run_command("git tag -l")
    if success:
        tags = [line.strip() for line in output.split('\n') if line.strip()]
        
        for tag in tags:
            collect_from_tag(tag)
    
    # Consolidate to main
    consolidate_to_main()
    
    # Add version headers
    add_version_headers()
    
    # Clean up
    if os.path.exists("collected_content"):
        shutil.rmtree("collected_content")
    
    print("Content collection and consolidation complete!")

if __name__ == "__main__":
    main()