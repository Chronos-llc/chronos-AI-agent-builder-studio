from sqlalchemy import Column, String, Boolean, Integer, Text, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class AdminRoleEnum(str, enum.Enum):
    """Admin role types"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"


class PermissionEnum(str, enum.Enum):
    """Permission types"""
    # User management
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    BAN_USERS = "ban_users"
    
    # Agent management
    MANAGE_AGENTS = "manage_agents"
    VIEW_AGENTS = "view_agents"
    DELETE_AGENTS = "delete_agents"
    
    # Marketplace management
    MANAGE_MARKETPLACE = "manage_marketplace"
    APPROVE_LISTINGS = "approve_listings"
    REJECT_LISTINGS = "reject_listings"
    FEATURE_LISTINGS = "feature_listings"
    
    # Support management
    MANAGE_SUPPORT = "manage_support"
    VIEW_SUPPORT_TICKETS = "view_support_tickets"
    RESPOND_TO_TICKETS = "respond_to_tickets"
    
    # System management
    MANAGE_SYSTEM = "manage_system"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_SETTINGS = "manage_settings"
    
    # Audit logs
    VIEW_AUDIT_LOGS = "view_audit_logs"


# Association table for many-to-many relationship between roles and permissions
role_permissions = Table(
    'admin_role_permissions',
    BaseModel.metadata,
    Column('role_id', Integer, ForeignKey('admin_roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('admin_permissions.id', ondelete='CASCADE'), primary_key=True)
)


class AdminRole(BaseModel):
    """Admin role model"""
    __tablename__ = "admin_roles"
    
    name = Column(SQLEnum(AdminRoleEnum), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    permissions = relationship(
        "AdminPermission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin"
    )
    users = relationship("AdminUser", back_populates="role", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AdminRole(id={self.id}, name='{self.name}')>"


class AdminPermission(BaseModel):
    """Admin permission model"""
    __tablename__ = "admin_permissions"
    
    name = Column(SQLEnum(PermissionEnum), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    resource = Column(String(50), nullable=False)  # users, agents, marketplace, support, system
    action = Column(String(50), nullable=False)  # view, create, update, delete, manage
    
    # Relationships
    roles = relationship(
        "AdminRole",
        secondary=role_permissions,
        back_populates="permissions",
        lazy="selectin"
    )
    
    def __repr__(self):
        return f"<AdminPermission(id={self.id}, name='{self.name}')>"


class AdminUser(BaseModel):
    """Admin user model - extends regular user with admin capabilities"""
    __tablename__ = "admin_users"
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    role_id = Column(Integer, ForeignKey('admin_roles.id', ondelete='SET NULL'), nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", backref="admin_profile", lazy="selectin")
    role = relationship("AdminRole", back_populates="users", lazy="selectin")
    audit_logs = relationship("AdminAuditLog", back_populates="admin_user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AdminUser(id={self.id}, user_id={self.user_id}, role={self.role.name if self.role else None})>"


class AdminAuditLog(BaseModel):
    """Admin audit log model - tracks all admin actions"""
    __tablename__ = "admin_audit_logs"
    
    admin_user_id = Column(Integer, ForeignKey('admin_users.id', ondelete='SET NULL'), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)  # user, agent, marketplace_listing, etc.
    resource_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)  # JSON string with additional details
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(255), nullable=True)
    status = Column(String(20), default="success")  # success, failed, error
    
    # Relationships
    admin_user = relationship("AdminUser", back_populates="audit_logs", lazy="selectin")
    
    def __repr__(self):
        return f"<AdminAuditLog(id={self.id}, action='{self.action}', resource_type='{self.resource_type}')>"
