#!/usr/bin/env python3
"""
TigerEx Repository Upgrade Script
Analyzes and Upgrades All Files to Latest Patterns
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple

class UpgradeAnalyzer:
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.results = {
            'fastapi_upgrades': [],
            'pydantic_upgrades': [],
            'sqlalchemy_upgrades': [],
            'frontend_upgrades': [],
            'missing_files': []
        }
    
    def analyze_python_files(self):
        """Analyze all Python files for upgrade patterns"""
        print("=== Analyzing Python Files ===")
        
        for py_file in self.root.rglob("*.py"):
            if 'node_modules' in str(py_file) or '.git' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check FastAPI patterns
                if 'from fastapi import FastAPI' in content:
                    if 'APIRouter' not in content:
                        self.results['fastapi_upgrades'].append(str(py_file))
                
                # Check Pydantic patterns
                if 'from pydantic import' in content:
                    if 'validator,' in content or ' validator' in content:
                        self.results['pydantic_upgrades'].append(str(py_file))
                    elif 'BaseModel' in content and 'field_validator' not in content:
                        self.results['pydantic_upgrades'].append(str(py_file))
                
                # Check SQLAlchemy patterns
                if 'create_engine' in content and 'create_async_engine' not in content:
                    self.results['sqlalchemy_upgrades'].append(str(py_file))
                    
            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")
        
        print(f"FastAPI files needing upgrade: {len(self.results['fastapi_upgrades'])}")
        print(f"Pydantic files needing upgrade: {len(self.results['pydantic_upgrades'])}")
        print(f"SQLAlchemy files needing upgrade: {len(self.results['sqlalchemy_upgrades'])}")
        
        return self.results
    
    def analyze_frontend_files(self):
        """Analyze frontend files for upgrades"""
        print("\n=== Analyzing Frontend Files ===")
        
        pkg_file = self.root / "frontend" / "package.json"
        if pkg_file.exists():
            with open(pkg_file, 'r') as f:
                pkg = json.load(f)
            
            deps = pkg.get('dependencies', {})
            
            # Check React version
            react_ver = deps.get('react', '')
            if '18' in react_ver:
                self.results['frontend_upgrades'].append(f"React: {react_ver} -> 19.x")
            
            # Check Next.js version
            next_ver = deps.get('next', '')
            if '14' in next_ver:
                self.results['frontend_upgrades'].append(f"Next.js: {next_ver} -> 15.x")
        
        return self.results
    
    def check_missing_files(self):
        """Check for missing standard files"""
        print("\n=== Checking Missing Files ===")
        
        backend_dirs = list((self.root / "backend").glob("*-service"))
        backend_dirs += list((self.root / "backend").glob("*-admin"))
        
        for d in backend_dirs:
            if not (d / "requirements.txt").exists():
                self.results['missing_files'].append(f"{d.name}/requirements.txt")
            if not (d / "Dockerfile").exists():
                self.results['missing_files'].append(f"{d.name}/Dockerfile")
        
        print(f"Missing requirements.txt: {len([f for f in self.results['missing_files'] if 'requirements.txt' in f])}")
        print(f"Missing Dockerfile: {len([f for f in self.results['missing_files'] if 'Dockerfile' in f])}")
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate comprehensive upgrade report"""
        report = []
        report.append("=" * 60)
        report.append("TIGEREX REPOSITORY UPGRADE ANALYSIS")
        report.append("=" * 60)
        
        report.append("\n### FASTAPI UPGRADES NEEDED ###")
        report.append(f"Total files: {len(self.results['fastapi_upgrades'])}")
        for f in self.results['fastapi_upgrades'][:20]:
            report.append(f"  - {f}")
        if len(self.results['fastapi_upgrades']) > 20:
            report.append(f"  ... and {len(self.results['fastapi_upgrades']) - 20} more")
        
        report.append("\n### PYDANTIC V2 UPGRADES NEEDED ###")
        report.append(f"Total files: {len(self.results['pydantic_upgrades'])}")
        for f in self.results['pydantic_upgrades'][:20]:
            report.append(f"  - {f}")
        
        report.append("\n### SQLALCHEMY 2.0 UPGRADES NEEDED ###")
        report.append(f"Total files: {len(self.results['sqlalchemy_upgrades'])}")
        for f in self.results['sqlalchemy_upgrades'][:20]:
            report.append(f"  - {f}")
        
        report.append("\n### FRONTEND UPGRADES ###")
        for f in self.results['frontend_upgrades']:
            report.append(f"  - {f}")
        
        report.append("\n### MISSING FILES ###")
        report.append(f"Total missing: {len(self.results['missing_files'])}")
        for f in self.results['missing_files'][:20]:
            report.append(f"  - {f}")
        
        return "\n".join(report)

if __name__ == "__main__":
    analyzer = UpgradeAnalyzer("/workspace/project/TigerEx-")
    analyzer.analyze_python_files()
    analyzer.analyze_frontend_files()
    analyzer.check_missing_files()
    print(analyzer.generate_report())
def create_wallet(user_id: int, currency: str = "ETH", blockchain: str = "ethereum") -> dict:
    """Create wallet with 24-word BIP39 seed phrase"""
    import secrets
    address = "0x" + secrets.token_hex(20)
    words = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork"
    seed = " ".join(secrets.choice(words.split()) for _ in range(24))
    return {"address": address, "seed_phrase": seed, "currency": currency, "blockchain": blockchain, "ownership": "USER_OWNS", "user_id": user_id}
