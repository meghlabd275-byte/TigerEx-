"""
TigerEx Complete Admin Operations Service
Implements production-style RBAC and full admin controls.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="TigerEx Admin Operations Service")


def now_ms() -> int:
    return int(datetime.utcnow().timestamp() * 1000)


class AdminContext(BaseModel):
    admin_id: str
    role: str


class UserRecord(BaseModel):
    userId: str
    email: str
    role: str = "trader"
    status: str = "active"  # active|paused|suspended|banned|deleted
    kycStatus: str = "pending"
    serviceAccess: bool = True
    createdAt: int = Field(default_factory=now_ms)
    updatedAt: int = Field(default_factory=now_ms)


class UserCreateRequest(BaseModel):
    userId: str
    email: str
    role: str = "trader"
    status: str = "active"


class UserStatusUpdateRequest(BaseModel):
    status: str = Field(pattern="^(active|paused|suspended|banned|deleted)$")
    reason: Optional[str] = None


class UserRoleUpdateRequest(BaseModel):
    role: str


class ServiceControlRequest(BaseModel):
    service: str
    action: str = Field(pattern="^(pause|resume|halt|stop)$")
    reason: Optional[str] = None


class GlobalControlRequest(BaseModel):
    action: str = Field(pattern="^(pause|resume|halt|stop)$")
    reason: Optional[str] = None


ADMIN_KEYS: Dict[str, AdminContext] = {
    "super-admin-key": AdminContext(admin_id="admin_root", role="super_admin"),
    "ops-admin-key": AdminContext(admin_id="admin_ops", role="operations_admin"),
    "support-admin-key": AdminContext(admin_id="admin_support", role="support_admin"),
}

ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "super_admin": {
        "users:read",
        "users:create",
        "users:update",
        "users:delete",
        "users:service_access",
        "roles:update",
        "trading:control",
        "services:control",
        "system:control",
        "audit:read",
        "kyc:manage",
        "finance:manage",
    },
    "operations_admin": {
        "users:read",
        "users:update",
        "users:service_access",
        "trading:control",
        "services:control",
        "system:control",
        "audit:read",
        "finance:manage",
    },
    "support_admin": {
        "users:read",
        "users:update",
        "kyc:manage",
        "audit:read",
    },
}

USERS: Dict[str, UserRecord] = {
    "user_001": UserRecord(
        userId="user_001",
        email="trader1@tigerex.test",
        role="trader",
        status="active",
        kycStatus="verified",
    ),
    "user_002": UserRecord(
        userId="user_002",
        email="marketmaker@tigerex.test",
        role="market_maker",
        status="active",
        kycStatus="verified",
    ),
}

SYSTEM_STATE: Dict[str, Any] = {
    "maintenanceMode": False,
    "maintenanceMessage": "",
    "globalTradingStatus": "active",  # active|paused|halted|stopped
    "services": {
        "spot": "active",
        "futures": "active",
        "margin": "active",
        "withdrawals": "active",
        "deposits": "active",
    },
}

AUDIT_LOGS: List[Dict[str, Any]] = []


def log_action(actor: AdminContext, action: str, payload: Dict[str, Any]) -> None:
    AUDIT_LOGS.append(
        {
            "id": len(AUDIT_LOGS) + 1,
            "timestamp": now_ms(),
            "actor": actor.admin_id,
            "role": actor.role,
            "action": action,
            "payload": payload,
        }
    )


async def verify_admin_key(x_admin_key: str = Header(...)) -> AdminContext:
    admin = ADMIN_KEYS.get(x_admin_key)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key",
        )
    return admin


def require_permission(permission: str):
    def checker(admin: AdminContext = Depends(verify_admin_key)) -> AdminContext:
        granted = ROLE_PERMISSIONS.get(admin.role, set())
        if permission not in granted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' is required",
            )
        return admin

    return checker


@app.get("/api/v1/admin/users")
async def get_all_users(
    page: int = 1,
    limit: int = 100,
    status_filter: Optional[str] = None,
    admin: AdminContext = Depends(require_permission("users:read")),
):
    users = list(USERS.values())
    if status_filter:
        users = [u for u in users if u.status == status_filter]
    start = max(0, (page - 1) * limit)
    end = start + limit
    return {
        "users": [u.model_dump() for u in users[start:end]],
        "total": len(users),
        "page": page,
        "limit": limit,
        "requestedBy": admin.admin_id,
    }


@app.post("/api/v1/admin/users")
async def create_user(
    body: UserCreateRequest,
    admin: AdminContext = Depends(require_permission("users:create")),
):
    if body.userId in USERS:
        raise HTTPException(status_code=409, detail="User already exists")
    user = UserRecord(
        userId=body.userId,
        email=body.email,
        role=body.role,
        status=body.status,
    )
    USERS[user.userId] = user
    log_action(admin, "users:create", {"userId": user.userId})
    return user.model_dump()


@app.get("/api/v1/admin/users/{user_id}")
async def get_user_details(
    user_id: str,
    admin: AdminContext = Depends(require_permission("users:read")),
):
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {**user.model_dump(), "requestedBy": admin.admin_id}


@app.put("/api/v1/admin/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    body: UserStatusUpdateRequest,
    admin: AdminContext = Depends(require_permission("users:update")),
):
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = body.status
    user.updatedAt = now_ms()
    log_action(
        admin,
        "users:update_status",
        {"userId": user_id, "status": body.status, "reason": body.reason},
    )
    return user.model_dump()


@app.put("/api/v1/admin/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    body: UserRoleUpdateRequest,
    admin: AdminContext = Depends(require_permission("roles:update")),
):
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    old_role = user.role
    user.role = body.role
    user.updatedAt = now_ms()
    log_action(
        admin,
        "users:update_role",
        {"userId": user_id, "oldRole": old_role, "newRole": body.role},
    )
    return user.model_dump()


@app.put("/api/v1/admin/users/{user_id}/service-access")
async def set_user_service_access(
    user_id: str,
    enabled: bool,
    admin: AdminContext = Depends(require_permission("users:service_access")),
):
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.serviceAccess = enabled
    user.updatedAt = now_ms()
    log_action(
        admin,
        "users:service_access",
        {"userId": user_id, "enabled": enabled},
    )
    return user.model_dump()


@app.delete("/api/v1/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: AdminContext = Depends(require_permission("users:delete")),
):
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = "deleted"
    user.serviceAccess = False
    user.updatedAt = now_ms()
    log_action(admin, "users:delete", {"userId": user_id})
    return {"message": f"User {user_id} deleted successfully"}


@app.post("/api/v1/admin/trading/control")
async def control_global_trading(
    body: GlobalControlRequest,
    admin: AdminContext = Depends(require_permission("trading:control")),
):
    SYSTEM_STATE["globalTradingStatus"] = {
        "pause": "paused",
        "resume": "active",
        "halt": "halted",
        "stop": "stopped",
    }[body.action]
    log_action(admin, "trading:control", body.model_dump())
    return {
        "globalTradingStatus": SYSTEM_STATE["globalTradingStatus"],
        "reason": body.reason,
        "updatedAt": now_ms(),
    }


@app.post("/api/v1/admin/services/control")
async def control_service(
    body: ServiceControlRequest,
    admin: AdminContext = Depends(require_permission("services:control")),
):
    if body.service not in SYSTEM_STATE["services"]:
        raise HTTPException(status_code=404, detail="Service not found")
    SYSTEM_STATE["services"][body.service] = {
        "pause": "paused",
        "resume": "active",
        "halt": "halted",
        "stop": "stopped",
    }[body.action]
    log_action(admin, "services:control", body.model_dump())
    return {
        "service": body.service,
        "status": SYSTEM_STATE["services"][body.service],
        "reason": body.reason,
        "updatedAt": now_ms(),
    }


@app.post("/api/v1/admin/maintenance/enable")
async def enable_maintenance_mode(
    message: str = "System maintenance in progress",
    admin: AdminContext = Depends(require_permission("system:control")),
):
    SYSTEM_STATE["maintenanceMode"] = True
    SYSTEM_STATE["maintenanceMessage"] = message
    log_action(admin, "system:maintenance_enable", {"message": message})
    return {
        "maintenanceMode": True,
        "message": message,
        "updatedAt": now_ms(),
    }


@app.post("/api/v1/admin/maintenance/disable")
async def disable_maintenance_mode(
    admin: AdminContext = Depends(require_permission("system:control")),
):
    SYSTEM_STATE["maintenanceMode"] = False
    SYSTEM_STATE["maintenanceMessage"] = ""
    log_action(admin, "system:maintenance_disable", {})
    return {"maintenanceMode": False, "updatedAt": now_ms()}


@app.get("/api/v1/admin/config/system")
async def get_system_config(admin: AdminContext = Depends(require_permission("audit:read"))):
    return {**SYSTEM_STATE, "requestedBy": admin.admin_id}


@app.get("/api/v1/admin/audit-logs")
async def get_audit_logs(
    limit: int = 200,
    admin: AdminContext = Depends(require_permission("audit:read")),
):
    return {
        "logs": AUDIT_LOGS[-limit:],
        "count": min(limit, len(AUDIT_LOGS)),
        "requestedBy": admin.admin_id,
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "time": now_ms()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
