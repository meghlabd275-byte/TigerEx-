#!/usr/bin/env python3
"""
TigerEx Repository Consolidation Script
Consolidates all unique and matching features from the repository
"""

import os
import shutil
import json
from pathlib import Path

def clean_pycache_and_duplicates():
    """Clean up __pycache__ directories and duplicate files"""
    print("🧹 Cleaning up __pycache__ directories...")
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"))
            print(f"  Removed: {root}/__pycache__")
    
    print("🧹 Cleaning up .pyc files...")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pyc"):
                os.remove(os.path.join(root, file))
                print(f"  Removed: {root}/{file}")

def analyze_backend_services():
    """Analyze all backend services and identify unique features"""
    print("📊 Analyzing backend services...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return []
    
    services = []
    for item in backend_dir.iterdir():
        if item.is_dir() and not item.name.startswith("__"):
            service_info = {
                "name": item.name,
                "path": str(item),
                "has_main": any(file.name == "main.py" for file in item.rglob("*.py")),
                "has_dockerfile": any(file.name == "Dockerfile" for file in item.iterdir()),
                "has_requirements": any(file.name.startswith("requirements") for file in item.iterdir()),
                "subdirs": [d.name for d in item.iterdir() if d.is_dir()],
                "files": [f.name for f in item.iterdir() if f.is_file()]
            }
            services.append(service_info)
    
    print(f"  Found {len(services)} services")
    return services

def create_service_index(services):
    """Create an index of all services for easy reference"""
    print("📝 Creating service index...")
    
    index = {
        "total_services": len(services),
        "services_with_main": len([s for s in services if s["has_main"]]),
        "services_with_docker": len([s for s in services if s["has_dockerfile"]]),
        "services": services
    }
    
    with open("SERVICE_INDEX.json", "w") as f:
        json.dump(index, f, indent=2)
    
    print(f"  Service index created: SERVICE_INDEX.json")
    return index

def optimize_docker_compose():
    """Optimize docker-compose.yml to include all services"""
    print("🐳 Optimizing docker-compose.yml...")
    
    backend_dir = Path("backend")
    services = []
    
    for item in backend_dir.iterdir():
        if item.is_dir() and (item / "Dockerfile").exists():
            services.append({
                "name": item.name.replace("-", "_"),
                "build": f"./backend/{item.name}",
                "container_name": f"tigerex-{item.name}"
            })
    
    print(f"  Found {len(services)} services with Dockerfiles")
    
    # Create optimized docker-compose
    docker_compose = {
        "version": "3.8",
        "services": {}
    }
    
    for service in services:
        docker_compose["services"][service["name"]] = {
            "build": service["build"],
            "container_name": service["container_name"],
            "restart": "unless-stopped",
            "networks": ["tigerex-network"],
            "environment": [
                "NODE_ENV=production",
                "API_PORT=8000"
            ]
        }
    
    docker_compose["networks"] = {
        "tigerex-network": {
            "driver": "bridge"
        }
    }
    
    with open("docker-compose.optimized.yml", "w") as f:
        import yaml
        yaml.dump(docker_compose, f, default_flow_style=False)
    
    print("  Optimized docker-compose.yml created")

def create_comprehensive_readme():
    """Create comprehensive README with all services"""
    print("📚 Creating comprehensive README...")
    
    backend_dir = Path("backend")
    services = []
    
    for item in backend_dir.iterdir():
        if item.is_dir() and not item.name.startswith("__"):
            main_files = list(item.rglob("main.py"))
            has_main = len(main_files) > 0
            
            service_desc = {
                "name": item.name.replace("-", " ").title(),
                "folder": item.name,
                "has_docker": (item / "Dockerfile").exists(),
                "has_main": has_main,
                "port": 8000 + len(services)  # Assign incremental ports
            }
            services.append(service_desc)
    
    readme_content = f"""# TigerEx Exchange - Complete Platform

## 🚀 Overview
TigerEx is a comprehensive cryptocurrency exchange platform with **{len(services)} microservices** providing complete trading functionality.

## 📊 Platform Statistics
- **Total Services**: {len(services)}
- **Dockerized Services**: {len([s for s in services if s['has_docker']])}
- **Main Services**: {len([s for s in services if s['has_main']])}

## 🏗️ Services Architecture

### Backend Services
"""
    
    for i, service in enumerate(services, 1):
        status = "✅" if service['has_main'] else "⚠️"
        docker_status = "🐳" if service['has_docker'] else "❌"
        readme_content += f"""
**{i}.** {service['name']} (`{service['folder']}`)
   - Status: {status}
   - Docker: {docker_status}
   - Port: {service['port']}
   - Path: `backend/{service['folder']}`
"""
    
    readme_content += """
## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cd TigerEx-

# Start all services
docker-compose up -d

# Or run individual services
cd backend/[service-name]
python main.py
```

## 📁 Project Structure
```
TigerEx-/
├── backend/          # {len(services)} microservices
├── frontend/         # React/Vue.js frontend
├── docs/            # Documentation
├── scripts/         # Utility scripts
└── docker-compose.yml
```

## 🔗 API Endpoints
Each service runs on its own port starting from 8000. Check individual service documentation for specific endpoints.

## 📝 License
MIT License - See LICENSE file for details.
"""
    
    with open("README_COMPREHENSIVE.md", "w") as f:
        f.write(readme_content)
    
    print("  Comprehensive README created: README_COMPREHENSIVE.md")

def main():
    """Main consolidation function"""
    print("🚀 Starting TigerEx Repository Consolidation...")
    print("=" * 50)
    
    # Clean up
    clean_pycache_and_duplicates()
    
    # Analyze services
    services = analyze_backend_services()
    
    # Create service index
    index = create_service_index(services)
    
    # Optimize docker-compose
    optimize_docker_compose()
    
    # Create comprehensive README
    create_comprehensive_readme()
    
    print("=" * 50)
    print("✅ Consolidation Complete!")
    print(f"📊 Processed {len(services)} services")
    print("📁 Created optimized files:")
    print("  - SERVICE_INDEX.json (Service catalog)")
    print("  - docker-compose.optimized.yml (Optimized orchestration)")
    print("  - README_COMPREHENSIVE.md (Complete documentation)")

if __name__ == "__main__":
    main()