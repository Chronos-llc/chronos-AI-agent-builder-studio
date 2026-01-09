"""
Configuration Management API Endpoints
Advanced Configuration Management System for Chronos AI Agent Builder Studio
"""

import enum
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config_management_engine import ConfigManagementEngine
from app.schemas.config_management import (
    ConfigSchemaCreate,
    ConfigSchemaUpdate,
    ConfigSchemaResponse,
    ConfigVersionCreate,
    ConfigVersionResponse,
    ConfigSnapshotCreate,
    ConfigSnapshotResponse,
    ConfigTemplateCreate,
    ConfigTemplateUpdate,
    ConfigTemplateResponse,
    EnvironmentConfigCreate,
    EnvironmentConfigUpdate,
    EnvironmentConfigResponse,
    ConfigValidationRequest,
    ConfigValidationResponse,
    ConfigDiffRequest,
    ConfigDiffResponse,
    PaginatedConfigSchemaResponse,
    PaginatedConfigVersionResponse,
    PaginatedConfigTemplateResponse,
    PaginatedConfigSnapshotResponse,
    RollbackRequest,
    RollbackResponse,
    ApplyTemplateRequest,
    ApplyTemplateResponse,
    ConfigurationCreate,
    ConfigurationUpdate,
    ConfigurationResponse,
)

router = APIRouter(prefix="/config-management", tags=["Configuration Management"])

# Initialize the config management engine
engine = ConfigManagementEngine()


# ============== Validation Endpoint ==============

@router.post("/validate", response_model=ConfigValidationResponse)
async def validate_configuration(
    request: ConfigValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Validate a configuration against a schema.
    Returns validation status and any errors found.
    """
    return engine.validate_config(request.config_data, request.schema_id, db)


# ============== Configuration Schemas ==============

@router.get("/schemas", response_model=PaginatedConfigSchemaResponse)
async def list_schemas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    schema_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all configuration schemas with optional filtering"""
    return engine.list_schemas(db, skip=skip, limit=limit, schema_type=schema_type, is_active=is_active)


@router.post("/schemas", response_model=ConfigSchemaResponse, status_code=201)
async def create_schema(
    schema: ConfigSchemaCreate,
    db: Session = Depends(get_db)
):
    """Create a new configuration schema"""
    return engine.create_schema(schema, db)


@router.get("/schemas/{schema_id}", response_model=ConfigSchemaResponse)
async def get_schema(
    schema_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific configuration schema by ID"""
    schema = engine.get_schema(schema_id, db)
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    return schema


@router.put("/schemas/{schema_id}", response_model=ConfigSchemaResponse)
async def update_schema(
    schema_id: UUID,
    schema_update: ConfigSchemaUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing configuration schema"""
    schema = engine.update_schema(schema_id, schema_update, db)
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    return schema


@router.delete("/schemas/{schema_id}", status_code=204)
async def delete_schema(
    schema_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a configuration schema"""
    success = engine.delete_schema(schema_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Schema not found")


# ============== Configuration Versions ==============

@router.get("/configs/{config_id}/versions", response_model=PaginatedConfigVersionResponse)
async def list_versions(
    config_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all versions of a configuration"""
    return engine.list_versions(config_id, db, skip=skip, limit=limit)


@router.post("/configs/{config_id}/versions", response_model=ConfigVersionResponse, status_code=201)
async def create_version(
    config_id: UUID,
    version: ConfigVersionCreate,
    db: Session = Depends(get_db)
):
    """Create a new version of a configuration"""
    return engine.create_version(config_id, version, db)


@router.get("/configs/{config_id}/versions/{version_id}", response_model=ConfigVersionResponse)
async def get_version(
    config_id: UUID,
    version_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific version of a configuration"""
    version = engine.get_version(version_id, db)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.post("/configs/{config_id}/rollback", response_model=RollbackResponse)
async def rollback_to_version(
    config_id: UUID,
    request: RollbackRequest,
    db: Session = Depends(get_db)
):
    """Rollback a configuration to a previous version"""
    return engine.rollback(config_id, request.version_id, request.changelog, db)


# ============== Configuration Templates ==============

@router.get("/templates", response_model=PaginatedConfigTemplateResponse)
async def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    schema_id: Optional[UUID] = None,
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all configuration templates with optional filtering"""
    return engine.list_templates(db, skip=skip, limit=limit, schema_id=schema_id, is_public=is_public)


@router.post("/templates", response_model=ConfigTemplateResponse, status_code=201)
async def create_template(
    template: ConfigTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new configuration template"""
    return engine.create_template(template, db)


@router.get("/templates/{template_id}", response_model=ConfigTemplateResponse)
async def get_template(
    template_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific configuration template"""
    template = engine.get_template(template_id, db)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/templates/{template_id}", response_model=ConfigTemplateResponse)
async def update_template(
    template_id: UUID,
    template_update: ConfigTemplateUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing configuration template"""
    template = engine.update_template(template_id, template_update, db)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a configuration template"""
    success = engine.delete_template(template_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")


@router.post("/templates/{template_id}/apply", response_model=ApplyTemplateResponse)
async def apply_template(
    template_id: UUID,
    request: ApplyTemplateRequest,
    db: Session = Depends(get_db)
):
    """Apply a template with given parameters"""
    return engine.apply_template(template_id, request.parameters, db)


# ============== Environment Configurations ==============

@router.get("/environments/{config_id}", response_model=EnvironmentConfigResponse)
async def get_environment_config(
    config_id: UUID,
    environment: str,
    db: Session = Depends(get_db)
):
    """Get environment-specific configuration"""
    config = engine.get_environment_config(config_id, environment, db)
    if not config:
        raise HTTPException(status_code=404, detail="Environment configuration not found")
    return config


@router.put("/environments/{config_id}", response_model=EnvironmentConfigResponse)
async def update_environment_config(
    config_id: UUID,
    environment: str,
    config_update: EnvironmentConfigUpdate,
    db: Session = Depends(get_db)
):
    """Update environment-specific configuration"""
    config = engine.update_environment_config(config_id, environment, config_update, db)
    if not config:
        raise HTTPException(status_code=404, detail="Environment configuration not found")
    return config


# ============== Configuration Diff ==============

@router.post("/diff", response_model=ConfigDiffResponse)
async def compare_configurations(
    request: ConfigDiffRequest,
    db: Session = Depends(get_db)
):
    """Compare two configurations and return differences"""
    return engine.compare_configs(request.config_a, request.config_b)


# ============== Configuration Snapshots ==============

@router.post("/snapshots", response_model=ConfigSnapshotResponse, status_code=201)
async def create_snapshot(
    snapshot: ConfigSnapshotCreate,
    db: Session = Depends(get_db)
):
    """Create a point-in-time snapshot of a configuration"""
    return engine.create_snapshot(snapshot, db)


@router.get("/snapshots/{config_id}", response_model=PaginatedConfigSnapshotResponse)
async def list_snapshots(
    config_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    snapshot_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all snapshots for a configuration"""
    return engine.list_snapshots(config_id, db, skip=skip, limit=limit, snapshot_type=snapshot_type)


# ============== Main Configurations ==============

@router.get("/configurations", response_model=List[ConfigurationResponse])
async def list_configurations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    schema_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all main configurations"""
    return engine.list_configurations(db, skip=skip, limit=limit, schema_id=schema_id, is_active=is_active)


@router.post("/configurations", response_model=ConfigurationResponse, status_code=201)
async def create_configuration(
    configuration: ConfigurationCreate,
    db: Session = Depends(get_db)
):
    """Create a new main configuration"""
    return engine.create_configuration(configuration, db)


@router.get("/configurations/{config_id}", response_model=ConfigurationResponse)
async def get_configuration(
    config_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific main configuration"""
    config = engine.get_configuration(config_id, db)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router.put("/configurations/{config_id}", response_model=ConfigurationResponse)
async def update_configuration(
    config_id: UUID,
    config_update: ConfigurationUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing main configuration"""
    config = engine.update_configuration(config_id, config_update, db)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router.delete("/configurations/{config_id}", status_code=204)
async def delete_configuration(
    config_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a main configuration"""
    success = engine.delete_configuration(config_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Configuration not found")
