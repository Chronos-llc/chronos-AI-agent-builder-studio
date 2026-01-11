from typing import List, Optional, Callable
from functools import wraps
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
from datetime import datetime

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.admin import AdminUser, AdminRole, AdminPermission, AdminAuditLog, AdminRoleEnum, PermissionEnum


# Role-based permission mapping
ROLE_PERMISSIONS = {
    AdminRoleEnum.SUPER_ADMIN: [
        # Super admin has all permissions
        PermissionEnum.MANAGE_USERS,
        PermissionEnum.VIEW_USERS,
        PermissionEnum.BAN_USERS,
        PermissionEnum.MANAGE_AGENTS,
        PermissionEnum.VIEW_AGENTS,
        PermissionEnum.DELETE_AGENTS,
        PermissionEnum.MANAGE_MARKETPLACE,
        PermissionEnum.APPROVE_LISTINGS,
        PermissionEnum.REJECT_LISTINGS,
        PermissionEnum.FEATURE_LISTINGS,
        PermissionEnum.MANAGE_SUPPORT,
        PermissionEnum.VIEW_SUPPORT_TICKETS,
        PermissionEnum.RESPOND_TO_TICKETS,
        PermissionEnum.MANAGE_SYSTEM,
        PermissionEnum.VIEW_ANALYTICS,
        PermissionEnum.MANAGE_SETTINGS,
        PermissionEnum.VIEW_AUDIT_LOGS,
    ],
    AdminRoleEnum.ADMIN: [
        PermissionEnum.MANAGE_USERS,
        PermissionEnum.VIEW_USERS,
        PermissionEnum.BAN_USERS,
        PermissionEnum.MANAGE_AGENTS,
        PermissionEnum.VIEW_AGENTS,
        PermissionEnum.DELETE_AGENTS,
        PermissionEnum.MANAGE_MARKETPLACE,
        PermissionEnum.APPROVE_LISTINGS,
        PermissionEnum.REJECT_LISTINGS,
        PermissionEnum.FEATURE_LISTINGS,
        PermissionEnum.VIEW_ANALYTICS,
    ],
    AdminRoleEnum.MODERATOR: [
        PermissionEnum.VIEW_USERS,
        PermissionEnum.VIEW_AGENTS,
        PermissionEnum.APPROVE_LISTINGS,
        PermissionEnum.REJECT_LISTINGS,
        PermissionEnum.VIEW_SUPPORT_TICKETS,
        PermissionEnum.RESPOND_TO_TICKETS,
    ],
    AdminRoleEnum.SUPPORT: [
        PermissionEnum.VIEW_USERS,
        PermissionEnum.VIEW_AGENTS,
        PermissionEnum.MANAGE_SUPPORT,
        PermissionEnum.VIEW_SUPPORT_TICKETS,
        PermissionEnum.RESPOND_TO_TICKETS,
    ],
}


async def get_admin_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AdminUser:
    """Get current admin user with role and permissions"""
    result = await db.execute(
        select(AdminUser).where(
            AdminUser.user_id == current_user.id,
            AdminUser.is_active == True
        )
    )
    admin_user = result.scalar_one_or_none()
    
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    if not admin_user.role or not admin_user.role.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or inactive admin role"
        )
    
    return admin_user


async def check_admin_permission(
    admin_user: AdminUser,
    required_permission: PermissionEnum,
    db: AsyncSession
) -> bool:
    """Check if admin user has required permission"""
    if not admin_user.role:
        return False
    
    # Super admin has all permissions
    if admin_user.role.name == AdminRoleEnum.SUPER_ADMIN:
        return True
    
    # Check if role has the required permission
    role_permissions = ROLE_PERMISSIONS.get(admin_user.role.name, [])
    return required_permission in role_permissions


def require_permission(permission: PermissionEnum):
    """Decorator to require specific permission for endpoint"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract dependencies from kwargs
            admin_user = kwargs.get('admin_user')
            db = kwargs.get('db')
            
            if not admin_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Missing required dependencies"
                )
            
            has_permission = await check_admin_permission(admin_user, permission, db)
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission.value} required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: AdminRoleEnum):
    """Decorator to require specific role for endpoint"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            admin_user = kwargs.get('admin_user')
            
            if not admin_user or not admin_user.role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin role required"
                )
            
            if admin_user.role.name != role and admin_user.role.name != AdminRoleEnum.SUPER_ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role {role.value} required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def log_admin_action(
    admin_user: AdminUser,
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    details: Optional[dict] = None,
    request: Optional[Request] = None,
    status_result: str = "success",
    db: AsyncSession = None
):
    """Log admin action to audit log"""
    if not db:
        return
    
    ip_address = None
    user_agent = None
    
    if request:
        # Get IP address from request
        ip_address = request.client.host if request.client else None
        # Get user agent from headers
        user_agent = request.headers.get("user-agent")
    
    audit_log = AdminAuditLog(
        admin_user_id=admin_user.id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=json.dumps(details) if details else None,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status_result
    )
    
    db.add(audit_log)
    await db.commit()


class AdminPermissionChecker:
    """Helper class for checking admin permissions"""
    
    def __init__(self, admin_user: AdminUser):
        self.admin_user = admin_user
    
    def has_permission(self, permission: PermissionEnum) -> bool:
        """Check if admin has specific permission"""
        if not self.admin_user.role:
            return False
        
        if self.admin_user.role.name == AdminRoleEnum.SUPER_ADMIN:
            return True
        
        role_permissions = ROLE_PERMISSIONS.get(self.admin_user.role.name, [])
        return permission in role_permissions
    
    def has_any_permission(self, permissions: List[PermissionEnum]) -> bool:
        """Check if admin has any of the specified permissions"""
        return any(self.has_permission(perm) for perm in permissions)
    
    def has_all_permissions(self, permissions: List[PermissionEnum]) -> bool:
        """Check if admin has all of the specified permissions"""
        return all(self.has_permission(perm) for perm in permissions)
    
    def is_super_admin(self) -> bool:
        """Check if admin is super admin"""
        return self.admin_user.role and self.admin_user.role.name == AdminRoleEnum.SUPER_ADMIN
    
    def get_permissions(self) -> List[PermissionEnum]:
        """Get all permissions for admin user"""
        if not self.admin_user.role:
            return []
        
        return ROLE_PERMISSIONS.get(self.admin_user.role.name, [])
