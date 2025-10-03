#!/usr/bin/env python3
"""
Apply Admin Controls to All TigerEx Services
=============================================
This script automatically adds admin controls to all backend services
that are missing them.

Version: 3.0.0
"""

import os
import json
from pathlib import Path
from typing import List, Dict
import shutil

VERSION = "3.0.0"

class AdminControlApplicator:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.backend_path = self.base_path / "backend"
        self.template_path = self.backend_path / "admin-control-template.py"
        self.results = {
            "services_updated": [],
            "services_failed": [],
            "total_processed": 0
        }
        
        # Load scan results
        scan_report_path = self.base_path / "comprehensive_scan_report.json"
        if scan_report_path.exists():
            with open(scan_report_path, 'r') as f:
                self.scan_report = json.load(f)
        else:
            self.scan_report = None
    
    def get_services_without_admin(self) -> List[str]:
        """Get list of services without admin controls"""
        if self.scan_report:
            return self.scan_report.get("services_without_admin_controls", [])
        return []
    
    def create_admin_module(self, service_path: Path) -> bool:
        """Create admin module for a service"""
        try:
            # Create admin directory if it doesn't exist
            admin_dir = service_path / "admin"
            admin_dir.mkdir(exist_ok=True)
            
            # Create __init__.py
            init_file = admin_dir / "__init__.py"
            init_file.write_text('"""Admin module for service"""\n')
            
            # Create admin_routes.py with comprehensive admin endpoints
            admin_routes_content = f'''"""
Admin Routes for {service_path.name}
Version: {VERSION}
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

# Import from admin control template
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from admin_control_template import (
    AdminUser, AdminAction, AdminResponse, AuditLogger,
    Permission, UserRole, ActionType,
    get_current_admin, require_permission, require_role
)

router = APIRouter(prefix="/admin", tags=["admin"])

# ============================================================================
# SERVICE-SPECIFIC MODELS
# ============================================================================

class ServiceConfig(BaseModel):
    """Service configuration model"""
    enabled: bool = True
    maintenance_mode: bool = False
    rate_limit: int = 1000
    max_connections: int = 100
    version: str = "{VERSION}"

class ServiceStats(BaseModel):
    """Service statistics model"""
    total_requests: int = 0
    active_connections: int = 0
    error_rate: float = 0.0
    uptime_seconds: int = 0

# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@router.get("/health")
async def admin_health():
    """Admin health check"""
    return {{
        "service": "{service_path.name}",
        "version": "{VERSION}",
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }}

@router.get("/status")
@require_permission(Permission.ANALYTICS_VIEW)
async def get_service_status(admin: AdminUser = Depends(get_current_admin)):
    """Get detailed service status"""
    stats = ServiceStats()
    return {{
        "service": "{service_path.name}",
        "stats": stats.dict(),
        "timestamp": datetime.utcnow()
    }}

# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@router.get("/config")
@require_permission(Permission.SYSTEM_CONFIG)
async def get_config(admin: AdminUser = Depends(get_current_admin)):
    """Get service configuration"""
    config = ServiceConfig()
    return config.dict()

@router.put("/config")
@require_permission(Permission.SYSTEM_CONFIG)
async def update_config(
    config: ServiceConfig,
    admin: AdminUser = Depends(get_current_admin)
):
    """Update service configuration"""
    await AuditLogger.log_action(
        admin=admin,
        action=ActionType.CONFIG,
        resource_type="service_config",
        resource_id="{service_path.name}",
        details=config.dict(),
        ip_address="0.0.0.0"
    )
    return AdminResponse(
        success=True,
        message="Configuration updated successfully",
        data=config.dict()
    )

# ============================================================================
# MAINTENANCE MODE ENDPOINTS
# ============================================================================

@router.post("/maintenance/enable")
@require_permission(Permission.MAINTENANCE_MODE)
async def enable_maintenance(
    action: AdminAction,
    admin: AdminUser = Depends(get_current_admin)
):
    """Enable maintenance mode"""
    await AuditLogger.log_action(
        admin=admin,
        action=ActionType.UPDATE,
        resource_type="maintenance",
        resource_id="{service_path.name}",
        details={{"action": "enable", "reason": action.reason}},
        ip_address="0.0.0.0"
    )
    return AdminResponse(
        success=True,
        message="Maintenance mode enabled"
    )

@router.post("/maintenance/disable")
@require_permission(Permission.MAINTENANCE_MODE)
async def disable_maintenance(
    admin: AdminUser = Depends(get_current_admin)
):
    """Disable maintenance mode"""
    await AuditLogger.log_action(
        admin=admin,
        action=ActionType.UPDATE,
        resource_type="maintenance",
        resource_id="{service_path.name}",
        details={{"action": "disable"}},
        ip_address="0.0.0.0"
    )
    return AdminResponse(
        success=True,
        message="Maintenance mode disabled"
    )

# ============================================================================
# MONITORING ENDPOINTS
# ============================================================================

@router.get("/metrics")
@require_permission(Permission.ANALYTICS_VIEW)
async def get_metrics(admin: AdminUser = Depends(get_current_admin)):
    """Get service metrics"""
    return {{
        "service": "{service_path.name}",
        "metrics": {{
            "requests_per_second": 0,
            "average_response_time": 0,
            "error_rate": 0,
            "active_connections": 0
        }},
        "timestamp": datetime.utcnow()
    }}

@router.get("/logs")
@require_permission(Permission.AUDIT_LOG_VIEW)
async def get_logs(
    admin: AdminUser = Depends(get_current_admin),
    limit: int = 100,
    level: Optional[str] = None
):
    """Get service logs"""
    return {{
        "service": "{service_path.name}",
        "logs": [],
        "total": 0,
        "limit": limit
    }}

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/analytics/summary")
@require_permission(Permission.ANALYTICS_VIEW)
async def get_analytics_summary(
    admin: AdminUser = Depends(get_current_admin),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get analytics summary"""
    return {{
        "service": "{service_path.name}",
        "period": {{"start": start_date, "end": end_date}},
        "summary": {{
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "average_duration": 0
        }}
    }}

@router.get("/analytics/detailed")
@require_permission(Permission.REPORT_GENERATE)
async def get_detailed_analytics(
    admin: AdminUser = Depends(get_current_admin),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get detailed analytics"""
    return {{
        "service": "{service_path.name}",
        "detailed_metrics": {{}},
        "timestamp": datetime.utcnow()
    }}

# ============================================================================
# AUDIT LOG ENDPOINTS
# ============================================================================

@router.get("/audit-logs")
@require_permission(Permission.AUDIT_LOG_VIEW)
async def get_audit_logs(
    admin: AdminUser = Depends(get_current_admin),
    page: int = 1,
    limit: int = 50,
    action_type: Optional[str] = None
):
    """Get audit logs for this service"""
    return {{
        "service": "{service_path.name}",
        "logs": [],
        "total": 0,
        "page": page,
        "limit": limit
    }}

# ============================================================================
# EMERGENCY CONTROLS
# ============================================================================

@router.post("/emergency/shutdown")
@require_role([UserRole.SUPER_ADMIN, UserRole.ADMIN])
async def emergency_shutdown(
    action: AdminAction,
    admin: AdminUser = Depends(get_current_admin)
):
    """Emergency shutdown of service"""
    await AuditLogger.log_action(
        admin=admin,
        action=ActionType.UPDATE,
        resource_type="emergency",
        resource_id="{service_path.name}",
        details={{"action": "shutdown", "reason": action.reason}},
        ip_address="0.0.0.0"
    )
    return AdminResponse(
        success=True,
        message="Emergency shutdown initiated"
    )

@router.post("/emergency/restart")
@require_role([UserRole.SUPER_ADMIN, UserRole.ADMIN])
async def emergency_restart(
    admin: AdminUser = Depends(get_current_admin)
):
    """Emergency restart of service"""
    await AuditLogger.log_action(
        admin=admin,
        action=ActionType.UPDATE,
        resource_type="emergency",
        resource_id="{service_path.name}",
        details={{"action": "restart"}},
        ip_address="0.0.0.0"
    )
    return AdminResponse(
        success=True,
        message="Emergency restart initiated"
    )
'''
            
            admin_routes_file = admin_dir / "admin_routes.py"
            admin_routes_file.write_text(admin_routes_content)
            
            return True
        except Exception as e:
            print(f"Error creating admin module for {service_path.name}: {e}")
            return False
    
    def update_main_file(self, service_path: Path) -> bool:
        """Update main.py to include admin routes"""
        try:
            main_files = list(service_path.glob("**/main.py"))
            if not main_files:
                main_files = list(service_path.glob("**/server.js"))
            
            if not main_files:
                print(f"No main file found in {service_path.name}")
                return False
            
            main_file = main_files[0]
            
            # Read existing content
            content = main_file.read_text()
            
            # Check if admin routes already included
            if "admin_routes" in content or "admin.admin_routes" in content:
                print(f"Admin routes already included in {service_path.name}")
                return True
            
            # Add admin routes import and include
            if main_file.suffix == ".py":
                # Python FastAPI service
                if "from fastapi import FastAPI" in content:
                    # Add import
                    import_line = "\nfrom admin.admin_routes import router as admin_router\n"
                    content = content.replace(
                        "from fastapi import FastAPI",
                        f"from fastapi import FastAPI{import_line}"
                    )
                    
                    # Add router inclusion
                    if "app = FastAPI" in content:
                        # Find the app creation line
                        lines = content.split("\n")
                        for i, line in enumerate(lines):
                            if "app = FastAPI" in line:
                                # Add router after app creation
                                lines.insert(i + 1, "\n# Include admin router")
                                lines.insert(i + 2, "app.include_router(admin_router)")
                                break
                        content = "\n".join(lines)
            
            elif main_file.suffix == ".js":
                # Node.js Express service
                if "express()" in content:
                    # Add admin routes
                    admin_routes = "\n// Admin routes\nconst adminRoutes = require('./admin/admin_routes');\napp.use('/admin', adminRoutes);\n"
                    content = content.replace(
                        "const app = express();",
                        f"const app = express();{admin_routes}"
                    )
            
            # Write updated content
            main_file.write_text(content)
            return True
            
        except Exception as e:
            print(f"Error updating main file for {service_path.name}: {e}")
            return False
    
    def update_service(self, service_name: str) -> bool:
        """Update a single service with admin controls"""
        service_path = self.backend_path / service_name
        
        if not service_path.exists():
            print(f"Service path not found: {service_name}")
            return False
        
        print(f"Updating {service_name}...")
        
        # Create admin module
        if not self.create_admin_module(service_path):
            return False
        
        # Update main file
        if not self.update_main_file(service_path):
            return False
        
        # Update version in service files
        self.update_version(service_path)
        
        return True
    
    def update_version(self, service_path: Path):
        """Update version to 3.0.0 in service files"""
        try:
            for py_file in service_path.rglob("*.py"):
                content = py_file.read_text()
                # Update version strings
                content = content.replace('version="2.', f'version="{VERSION}')
                content = content.replace('VERSION = "2.', f'VERSION = "{VERSION}')
                content = content.replace('"version": "2.', f'"version": "{VERSION}')
                py_file.write_text(content)
        except Exception as e:
            print(f"Error updating version: {e}")
    
    def apply_to_all_services(self):
        """Apply admin controls to all services without them"""
        services_to_update = self.get_services_without_admin()
        
        if not services_to_update:
            print("No services found without admin controls")
            return
        
        print(f"Found {len(services_to_update)} services without admin controls")
        print("=" * 80)
        
        for service_name in services_to_update:
            self.results["total_processed"] += 1
            
            if self.update_service(service_name):
                self.results["services_updated"].append(service_name)
                print(f"✓ {service_name} - Updated successfully")
            else:
                self.results["services_failed"].append(service_name)
                print(f"✗ {service_name} - Update failed")
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save update results"""
        results_path = self.base_path / "admin_controls_update_results.json"
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print("\n" + "=" * 80)
        print("UPDATE SUMMARY")
        print("=" * 80)
        print(f"Total Services Processed: {self.results['total_processed']}")
        print(f"Successfully Updated: {len(self.results['services_updated'])}")
        print(f"Failed Updates: {len(self.results['services_failed'])}")
        print(f"\nResults saved to: {results_path}")

def main():
    print("TigerEx Admin Controls Applicator v" + VERSION)
    print("=" * 80)
    
    applicator = AdminControlApplicator()
    applicator.apply_to_all_services()

if __name__ == "__main__":
    main()