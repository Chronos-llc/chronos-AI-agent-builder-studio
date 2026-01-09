"""
Configuration Management Database Models
Advanced Configuration Management System for Chronos AI Agent Builder Studio
"""

import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base


class SchemaType(str, enum.Enum):
    """Configuration schema types"""
    AGENT = "AGENT"
    WORKFLOW = "WORKFLOW"
    SYSTEM = "SYSTEM"
    CUSTOM = "CUSTOM"


class SnapshotType(str, enum.Enum):
    """Types of configuration snapshots"""
    MANUAL = "MANUAL"
    AUTOMATED = "AUTOMATED"
    SCHEDULED = "SCHEDULED"


class EnvironmentType(str, enum.Enum):
    """Deployment environments"""
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


class ConfigSchema(Base):
    """
    Configuration schema definitions
    Defines the structure and validation rules for configurations
    """
    __tablename__ = "config_schemas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    schema_type = Column(Enum(SchemaType), nullable=False, default=SchemaType.CUSTOM)
    schema_definition = Column(JSON, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    versions = relationship("ConfigVersion", back_populates="config_schema", cascade="all, delete-orphan")
    templates = relationship("ConfigTemplate", back_populates="config_schema", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ConfigSchema(id={self.id}, name='{self.name}', type={self.schema_type})>"


class ConfigVersion(Base):
    """
    Version history for configurations
    Tracks all changes made to configurations over time
    """
    __tablename__ = "config_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_id = Column(UUID(as_uuid=True), ForeignKey("config_versions.id"), nullable=True)
    config_schema_id = Column(UUID(as_uuid=True), ForeignKey("config_schemas.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    configuration_data = Column(JSON, nullable=False)
    changelog = Column(Text, nullable=True)
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    config_schema = relationship("ConfigSchema", back_populates="versions")
    snapshots = relationship("ConfigSnapshot", back_populates="version")
    
    # Self-referential relationship for parent config
    parent_config = relationship("ConfigVersion", remote_side=[id], backref="child_versions")
    
    def __repr__(self):
        return f"<ConfigVersion(id={self.id}, config_id={self.config_id}, v{self.version_number})>"


class ConfigSnapshot(Base):
    """
    Point-in-time snapshots of configurations
    Preserves the exact state of a configuration at a specific moment
    """
    __tablename__ = "config_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_id = Column(UUID(as_uuid=True), ForeignKey("config_versions.id"), nullable=False)
    version_id = Column(UUID(as_uuid=True), ForeignKey("config_versions.id"), nullable=False)
    snapshot_data = Column(JSON, nullable=False)
    snapshot_type = Column(Enum(SnapshotType), nullable=False, default=SnapshotType.MANUAL)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    version = relationship("ConfigVersion", back_populates="snapshots")
    
    def __repr__(self):
        return f"<ConfigSnapshot(id={self.id}, type={self.snapshot_type}, created_at={self.created_at})>"


class ConfigTemplate(Base):
    """
    Reusable configuration templates
    Provides pre-defined configuration patterns that can be customized
    """
    __tablename__ = "config_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    config_schema_id = Column(UUID(as_uuid=True), ForeignKey("config_schemas.id"), nullable=False)
    template_data = Column(JSON, nullable=False)
    parameters = Column(JSON, nullable=True)
    is_public = Column(Boolean, default=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    config_schema = relationship("ConfigSchema", back_populates="templates")
    
    def __repr__(self):
        return f"<ConfigTemplate(id={self.id}, name='{self.name}', is_public={self.is_public})>"


class EnvironmentConfig(Base):
    """
    Environment-specific configurations
    Allows different settings for development, staging, and production environments
    """
    __tablename__ = "environment_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_id = Column(UUID(as_uuid=True), ForeignKey("config_versions.id"), nullable=False)
    environment = Column(Enum(EnvironmentType), nullable=False)
    config_data = Column(JSON, nullable=False)
    overrides = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<EnvironmentConfig(id={self.id}, config_id={self.config_id}, env={self.environment})>"


class Configuration(Base):
    """
    Main configuration entity
    Represents an active configuration that can be versioned and deployed
    """
    __tablename__ = "configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    config_schema_id = Column(UUID(as_uuid=True), ForeignKey("config_schemas.id"), nullable=False)
    current_version_id = Column(UUID(as_uuid=True), ForeignKey("config_versions.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    config_schema = relationship("ConfigSchema")
    current_version = relationship("ConfigVersion", foreign_keys=[current_version_id])
    
    def __repr__(self):
        return f"<Configuration(id={self.id}, name='{self.name}', is_active={self.is_active})>"
