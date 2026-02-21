from datetime import timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc
from pydantic import BaseModel, Field
import json

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.core.rbac import (
    get_admin_user,
    check_admin_permission,
    log_admin_action,
    AdminPermissionChecker,
    ROLE_PERMISSIONS
)
from app.models.user import User
from app.models.admin import (
    AdminUser,
    AdminRole,
    AdminPermission,
    AdminAuditLog,
    AdminRoleEnum,
    PermissionEnum
)
from app.schemas.auth import Token

router = APIRouter()


# Pydantic schemas
class AdminUserResponse(BaseModel):
    id: int
    user_id: int
    role_id: Optional[int]
    is_active: bool
    notes: Optional[str]
    created_at: str
    updated_at: str
    
    # User details
    email: str
    username: str
    full_name: Optional[str]
    
    # Role details
    role_name: Optional[str]
    role_display_name: Optional[str]
    
    class Config:
        from_attributes = True


class AdminRoleResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    is_active: bool
    permissions: List[str] = []
    
    class Config:
        from_attributes = True


class AdminPermissionResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    resource: str
    action: str
    
    class Config:
        from_attributes = True


class AdminAuditLogResponse(BaseModel):
    id: int
    admin_user_id: Optional[int]
    action: str
    resource_type: str
    resource_id: Optional[int]
    details: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    status: str
    created_at: str
    
    # Admin user details
    admin_username: Optional[str]
    admin_email: Optional[str]
    
    class Config:
        from_attributes = True


class CreateAdminUserRequest(BaseModel):
    user_id: int
    role_id: int
    notes: Optional[str] = None


class UpdateAdminUserRequest(BaseModel):
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class AdminStatsResponse(BaseModel):
    total_users: int
    active_agents: int
    marketplace_listings: int
    pending_support_tickets: int
    revenue: float
    system_health: str


class SwitchProfileRequest(BaseModel):
    identifier: str = Field(..., min_length=3, max_length=255)


# Admin authentication endpoints
@router.get("/me", response_model=AdminUserResponse)
async def get_current_admin(
    admin_user: AdminUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current admin user information"""
    return {
        "id": admin_user.id,
        "user_id": admin_user.user_id,
        "role_id": admin_user.role_id,
        "is_active": admin_user.is_active,
        "notes": admin_user.notes,
        "created_at": admin_user.created_at.isoformat(),
        "updated_at": admin_user.updated_at.isoformat(),
        "email": admin_user.user.email,
        "username": admin_user.user.username,
        "full_name": admin_user.user.full_name,
        "role_name": admin_user.role.name.value if admin_user.role else None,
        "role_display_name": admin_user.role.display_name if admin_user.role else None,
    }


@router.get("/me/permissions", response_model=List[str])
async def get_current_admin_permissions(
    admin_user: AdminUser = Depends(get_admin_user)
):
    """Get current admin user permissions"""
    checker = AdminPermissionChecker(admin_user)
    permissions = checker.get_permissions()
    return [perm.value for perm in permissions]


@router.post("/switch-profile/start", response_model=Token)
async def switch_profile_start(
    payload: SwitchProfileRequest,
    response: Response,
    request: Request,
    admin_user: AdminUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Start an admin impersonation session for a non-admin user."""
    identifier = payload.identifier.strip()
    user_result = await db.execute(
        select(User).where(
            or_(
                User.email == identifier.lower(),
                User.username == identifier,
            )
        )
    )
    target_user = user_result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found",
        )

    if not target_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target user is inactive",
        )

    target_admin_result = await db.execute(
        select(AdminUser).where(
            AdminUser.user_id == target_user.id,
            AdminUser.is_active == True,
        )
    )
    if target_admin_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Switch profile only supports non-admin target accounts",
        )

    impersonation_claims = {
        "is_impersonation": True,
        "impersonator_user_id": admin_user.user_id,
        "impersonator_admin_user_id": admin_user.id,
    }
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=target_user.id,
        expires_delta=access_token_expires,
        additional_claims=impersonation_claims,
    )
    refresh_token = create_refresh_token(
        subject=target_user.id,
        additional_claims=impersonation_claims,
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    await log_admin_action(
        admin_user=admin_user,
        action="switch_profile_start",
        resource_type="user",
        resource_id=target_user.id,
        details={
            "target_user_id": target_user.id,
            "target_username": target_user.username,
        },
        request=request,
        db=db,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


# Admin user management endpoints
@router.get("/users", response_model=List[AdminUserResponse])
async def list_admin_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    role_name: Optional[str] = None,
    admin_user: AdminUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all admin users (requires MANAGE_USERS permission)"""
    # Check permission
    has_permission = await check_admin_permission(
        admin_user, PermissionEnum.MANAGE_USERS, db
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: manage_users required"
        )
    
    # Build query
    query = select(AdminUser)
    
    if is_active is not None:
        query = query.where(AdminUser.is_active == is_active)
    
    if role_name:
        query = query.join(AdminRole).where(AdminRole.name == role_name)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    admin_users = result.scalars().all()
    
    return [
        {
            "id": au.id,
            "user_id": au.user_id,
            "role_id": au.role_id,
            "is_active": au.is_active,
            "notes": au.notes,
            "created_at": au.created_at.isoformat(),
            "updated_at": au.updated_at.isoformat(),
            "email": au.user.email,
            "username": au.user.username,
            "full_name": au.user.full_name,
            "role_name": au.role.name.value if au.role else None,
            "role_display_name": au.role.display_name if au.role else None,
        }
        for au in admin_users
    ]


@router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    data: CreateAdminUserRequest,
    request: Request,
    admin_user: AdminUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new admin user (requires MANAGE_USERS permission)"""
    # Check permission
    has_permission = await check_admin_permission(
        admin_user, PermissionEnum.MANAGE_USERS, db
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: manage_users required"
        )
    
    # Check if user exists
    user_result = await db.execute(select(User).where(User.id == data.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is already an admin
    existing_result = await db.execute(
        select(AdminUser).where(AdminUser.user_id == data.user_id)
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already an admin"
        )
    
    # Check if role exists
    role_result = await db.execute(select(AdminRole).where(AdminRole.id == data.role_id))
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Create admin user
    new_admin_user = AdminUser(
        user_id=data.user_id,
        role_id=data.role_id,
        notes=data.notes
    )
    
    db.add(new_admin_user)
    await db.commit()
    await db.refresh(new_admin_user)
    
    # Log action
    await log_admin_action(
        admin_user=admin_user,
        action="create_admin_user",
        resource_type="admin_user",
        resource_id=new_admin_user.id,
        details={"user_id": data.user_id, "role_id": data.role_id},
        request=request,
        db=db
    )
    
    return {
        "id": new_admin_user.id,
        "user_id": new_admin_user.user_id,
        "role_id": new_admin_user.role_id,
        "is_active": new_admin_user.is_active,
        "notes": new_admin_user.notes,
        "created_at": new_admin_user.created_at.isoformat(),
        "updated_at": new_admin_user.updated_at.isoformat(),
        "email": new_admin_user.user.email,
        "username": new_admin_user.user.username,
        "full_name": new_admin_user.user.full_name,
        "role_name": new_admin_user.role.name.value if new_admin_user.role else None,
        "role_display_name": new_admin_user.role.display_name if new_admin_user.role else None,
    }


@router.patch("/users/{admin_user_id}", response_model=AdminUserResponse)
async def update_admin_user(
    admin_user_id: int,
    data: UpdateAdminUserRequest,
    request: Request,
    admin_user: AdminUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update admin user (requires MANAGE_USERS permission)"""
    # Check permission
    has_permission = await check_admin_permission(
        admin_user, PermissionEnum.MANAGE_USERS, db
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: manage_users required"
        )
    
    # Get admin user
    result = await db.execute(select(AdminUser).where(AdminUser.id == admin_user_id))
    target_admin = result.scalar_one_or_none()
    if not target_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Update fields
    if data.role_id is not None:
        # Check if role exists
        role_result = await db.execute(select(AdminRole).where(AdminRole.id == data.role_id))
        if not role_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        target_admin.role_id = data.role_id
    
    if data.is_active is not None:
        target_admin.is_active = data.is_active
    
    if data.notes is not None:
        target_admin.notes = data.notes
    
    await db.commit()
    await db.refresh(target_admin)
    
    # Log action
    await log_admin_action(
        admin_user=admin_user,
        action="update_admin_user",
        resource_type="admin_user",
        resource_id=admin_user_id,
        details=data.dict(exclude_unset=True),
        request=request,
        db=db
    )
    
    return {
        "id": target_admin.id,
        "user_id": target_admin.user_id,
        "role_id": target_admin.role_id,
        "is_active": target_admin.is_active,
        "notes": target_admin.notes,
        "created_at": target_admin.created_at.isoformat(),
        "updated_at": target_admin.updated_at.isoformat(),
        "email": target_admin.user.email,
        "username": target_admin.user.username,
        "full_name": target_admin.user.full_name,
        "role_name": target_admin.role.name.value if target_admin.role else None,
        "role_display_name": target_admin.role.display_name if target_admin.role else None,
    }


@router.delete("/users/{admin_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_user(
    admin_user_id: int,
    request: Request,
    admin_user: AdminUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete admin user (requires MANAGE_USERS permission)"""
    # Check permission
    has_permission = await check_admin_permission(
        admin_user, PermissionEnum.MANAGE_USERS, db
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: manage_users required"
        )
    
    # Get admin user
    result = await db.execute(select(AdminUser).where(AdminUser.id == admin_user_id))
    target_admin = result.scalar_one_or_none()
    if not target_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Prevent self-deletion
    if target_admin.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own admin account"
        )
    
    # Log action before deletion
    await log_admin_action(
        admin_user=admin_user,
        action="delete_admin_user",
        resource_type="admin_user",
        resource_id=admin_user_id,
        details={"user_id": target_admin.user_id},
        request=request,
        db=db
    )
    
    await db.delete(target_admin)
    await db.commit()


# Role management endpoints
@router.get("/roles", response_model=List[AdminRoleResponse])
async def list_roles(
    admin_user: AdminUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all admin roles"""
    result = await db.execute(select(AdminRole))
    roles = result.scalars().all()
    
    return [
        {
            "id": role.id,
            "name": role.name.value,
            "display_name": role.display_name,
            "description": role.description,
            "is_active": role.is_active,
            "permissions": [perm.value for perm in ROLE_PERMISSIONS.get(role.name, [])]
        }
        for role in roles
    ]


# Audit log endpoints
@router.get("/audit-logs", response_model=List[AdminAuditLogResponse])
async def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    admin_user: AdminUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List audit logs (requires VIEW_AUDIT_LOGS permission)"""
    # Check permission
    has_permission = await check_admin_permission(
        admin_user, PermissionEnum.VIEW_AUDIT_LOGS, db
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: view_audit_logs required"
        )
    
    # Build query
    query = select(AdminAuditLog).order_by(desc(AdminAuditLog.created_at))
    
    if action:
        query = query.where(AdminAuditLog.action == action)
    
    if resource_type:
        query = query.where(AdminAuditLog.resource_type == resource_type)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return [
        {
            "id": log.id,
            "admin_user_id": log.admin_user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "status": log.status,
            "created_at": log.created_at.isoformat(),
            "admin_username": log.admin_user.user.username if log.admin_user else None,
            "admin_email": log.admin_user.user.email if log.admin_user else None,
        }
        for log in logs
    ]


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    admin_user: AdminUser = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get admin statistics"""
    # Count total users
    from app.models.user import User
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar()
    
    # Count active agents
    from app.models.agent import Agent
    active_agents_result = await db.execute(
        select(func.count(Agent.id)).where(Agent.is_active == True)
    )
    active_agents = active_agents_result.scalar()
    
    # Count marketplace listings
    from app.models.marketplace import MarketplaceListing
    marketplace_listings_result = await db.execute(
        select(func.count(MarketplaceListing.id)).where(MarketplaceListing.is_active == True)
    )
    marketplace_listings = marketplace_listings_result.scalar()
    
    # Count pending support tickets
    from app.models.support_system import SupportTicket
    pending_support_tickets_result = await db.execute(
        select(func.count(SupportTicket.id)).where(SupportTicket.status == "pending")
    )
    pending_support_tickets = pending_support_tickets_result.scalar()
    
    # Calculate revenue (mock data for now)
    revenue = 45678.90
    
    # System health (mock data for now)
    system_health = "good"
    
    return {
        "total_users": total_users,
        "active_agents": active_agents,
        "marketplace_listings": marketplace_listings,
        "pending_support_tickets": pending_support_tickets,
        "revenue": revenue,
        "system_health": system_health
    }
