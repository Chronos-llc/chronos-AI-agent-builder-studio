"""
Pydantic Schemas for Configuration Management
Advanced Configuration Management System for Chronos AI Agent Builder Studio
"""

import enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


# Enums matching database models
class SchemaType(str, enum.Enum):
    AGENT = "AGENT"
    WORKFLOW = "WORKFLOW"
    SYSTEM = "SYSTEM"
    CUSTOM = "CUSTOM"


class SnapshotType(str, enum.Enum):
    MANUAL = "MANUAL"
    AUTOMATED = "AUTOMATED"
    SCHEDULED = "SCHEDULED"


class EnvironmentType(str, enum.Enum):
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


# ============== ConfigSchema Schemas ==============

class ConfigSchemaBase(BaseModel):
    """Base schema for ConfigSchema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    schema_type: SchemaType = SchemaType.CUSTOM
    schema_definition: Dict[str, Any]


class ConfigSchemaCreate(ConfigSchemaBase):
    """Schema for creating a new ConfigSchema"""
    is_active: Optional[bool] = True


class ConfigSchemaUpdate(BaseModel):
    """Schema for updating a ConfigSchema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    schema_type: Optional[SchemaType] = None
    schema_definition: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ConfigSchemaResponse(ConfigSchemaBase):
    """Schema for ConfigSchema response"""
    id: UUID
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== ConfigVersion Schemas ==============

class ConfigVersionBase(BaseModel):
    """Base schema for ConfigVersion"""
    config_schema_id: UUID
    configuration_data: Dict[str, Any]
    changelog: Optional[str] = None


class ConfigVersionCreate(ConfigVersionBase):
    """Schema for creating a new ConfigVersion"""
    config_id: Optional[UUID] = None
    created_by: Optional[str] = None


class ConfigVersionResponse(BaseModel):
    """Schema for ConfigVersion response"""
    id: UUID
    config_id: Optional[UUID]
    config_schema_id: UUID
    version_number: int
    configuration_data: Dict[str, Any]
    changelog: Optional[str]
    created_by: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConfigVersionWithSchema(ConfigVersionResponse):
    """Schema for ConfigVersion with included schema info"""
    config_schema: Optional[ConfigSchemaResponse] = None


# ============== ConfigSnapshot Schemas ==============

class ConfigSnapshotBase(BaseModel):
    """Base schema for ConfigSnapshot"""
    config_id: UUID
    version_id: UUID
    snapshot_data: Dict[str, Any]
    snapshot_type: SnapshotType = SnapshotType.MANUAL


class ConfigSnapshotCreate(ConfigSnapshotBase):
    """Schema for creating a new ConfigSnapshot"""
    pass


class ConfigSnapshotResponse(BaseModel):
    """Schema for ConfigSnapshot response"""
    id: UUID
    config_id: UUID
    version_id: UUID
    snapshot_data: Dict[str, Any]
    snapshot_type: SnapshotType
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== ConfigTemplate Schemas ==============

class ConfigTemplateBase(BaseModel):
    """Base schema for ConfigTemplate"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    config_schema_id: UUID
    template_data: Dict[str, Any]
    parameters: Optional[Dict[str, Any]] = None


class ConfigTemplateCreate(ConfigTemplateBase):
    """Schema for creating a new ConfigTemplate"""
    is_public: Optional[bool] = False
    user_id: Optional[UUID] = None


class ConfigTemplateUpdate(BaseModel):
    """Schema for updating a ConfigTemplate"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


class ConfigTemplateResponse(ConfigTemplateBase):
    """Schema for ConfigTemplate response"""
    id: UUID
    is_public: bool
    user_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== EnvironmentConfig Schemas ==============

class EnvironmentConfigBase(BaseModel):
    """Base schema for EnvironmentConfig"""
    config_id: UUID
    environment: EnvironmentType
    config_data: Dict[str, Any]
    overrides: Optional[Dict[str, Any]] = None


class EnvironmentConfigCreate(EnvironmentConfigBase):
    """Schema for creating a new EnvironmentConfig"""
    is_active: Optional[bool] = True


class EnvironmentConfigUpdate(BaseModel):
    """Schema for updating an EnvironmentConfig"""
    config_data: Optional[Dict[str, Any]] = None
    overrides: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class EnvironmentConfigResponse(EnvironmentConfigBase):
    """Schema for EnvironmentConfig response"""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== Configuration Schemas ==============

class ConfigurationBase(BaseModel):
    """Base schema for Configuration"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    config_schema_id: UUID


class ConfigurationCreate(ConfigurationBase):
    """Schema for creating a new Configuration"""
    created_by: Optional[str] = None


class ConfigurationUpdate(BaseModel):
    """Schema for updating a Configuration"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    current_version_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class ConfigurationResponse(ConfigurationBase):
    """Schema for Configuration response"""
    id: UUID
    current_version_id: Optional[UUID]
    is_active: bool
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== Validation Schemas ==============

class ConfigValidationRequest(BaseModel):
    """Request schema for config validation"""
    config_data: Dict[str, Any]
    schema_id: UUID


class ValidationError(BaseModel):
    """Schema for individual validation errors"""
    path: str
    message: str
    error_type: str


class ConfigValidationResponse(BaseModel):
    """Response schema for config validation"""
    is_valid: bool
    errors: List[ValidationError] = []
    schema_id: UUID
    validated_at: datetime = Field(default_factory=datetime.utcnow)


# ============== Diff Schemas ==============

class DiffEntry(BaseModel):
    """Schema for a single diff entry"""
    path: str
    old_value: Any
    new_value: Any
    change_type: str  # ADDED, REMOVED, MODIFIED


class ConfigDiffRequest(BaseModel):
    """Request schema for config diff"""
    config_a: Dict[str, Any]
    config_b: Dict[str, Any]


class ConfigDiffResponse(BaseModel):
    """Response schema for config diff"""
    has_differences: bool
    differences: List[DiffEntry] = []
    added_count: int = 0
    removed_count: int = 0
    modified_count: int = 0
    compared_at: datetime = Field(default_factory=datetime.utcnow)


# ============== Rollback Schemas ==============

class RollbackRequest(BaseModel):
    """Request schema for rollback operation"""
    version_id: UUID
    changelog: Optional[str] = "Rollback to previous version"


class RollbackResponse(BaseModel):
    """Response schema for rollback operation"""
    success: bool
    previous_version: Optional[ConfigVersionResponse]
    new_version: Optional[ConfigVersionResponse]
    message: str


# ============== Template Application Schemas ==============

class ApplyTemplateRequest(BaseModel):
    """Request schema for applying a template"""
    template_id: UUID
    parameters: Dict[str, Any] = {}


class ApplyTemplateResponse(BaseModel):
    """Response schema for template application"""
    success: bool
    applied_config: Dict[str, Any]
    template_id: UUID
    applied_at: datetime = Field(default_factory=datetime.utcnow)


# ============== List/Paginated Response Schemas ==============

class PaginatedConfigSchemaResponse(BaseModel):
    """Paginated response for config schemas"""
    items: List[ConfigSchemaResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class PaginatedConfigVersionResponse(BaseModel):
    """Paginated response for config versions"""
    items: List[ConfigVersionResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class PaginatedConfigTemplateResponse(BaseModel):
    """Paginated response for config templates"""
    items: List[ConfigTemplateResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class PaginatedConfigSnapshotResponse(BaseModel):
    """Paginated response for config snapshots"""
    items: List[ConfigSnapshotResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
