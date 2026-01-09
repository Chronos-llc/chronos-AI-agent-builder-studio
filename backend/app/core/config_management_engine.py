"""
Configuration Management Engine
Advanced Configuration Management System for Chronos AI Agent Builder Studio
"""

import enum
import json
import deepdiff
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session
from sqlalchemy import desc

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
    ValidationError,
    ConfigDiffRequest,
    ConfigDiffResponse,
    DiffEntry,
    PaginatedConfigSchemaResponse,
    PaginatedConfigVersionResponse,
    PaginatedConfigTemplateResponse,
    PaginatedConfigSnapshotResponse,
    RollbackResponse,
    ApplyTemplateResponse,
    ConfigurationCreate,
    ConfigurationUpdate,
    ConfigurationResponse,
)
from app.models.config_management import (
    ConfigSchema,
    ConfigVersion,
    ConfigSnapshot,
    ConfigTemplate,
    EnvironmentConfig,
    Configuration,
    SchemaType,
    SnapshotType,
    EnvironmentType,
)


class ConfigManagementEngine:
    """
    Core engine for managing configurations, schemas, versions, and templates.
    Provides validation, comparison, rollback, and template application functionality.
    """
    
    def __init__(self):
        """Initialize the configuration management engine"""
        pass
    
    # ============== Validation Methods ==============
    
    def validate_config(
        self,
        config_data: Dict[str, Any],
        schema_id: UUID,
        db: Session
    ) -> ConfigValidationResponse:
        """
        Validate a configuration against a schema.
        
        Args:
            config_data: The configuration data to validate
            schema_id: The ID of the schema to validate against
            db: Database session
            
        Returns:
            ConfigValidationResponse with validation results
        """
        errors = []
        
        try:
            # Get the schema
            schema = db.query(ConfigSchema).filter(
                ConfigSchema.id == schema_id,
                ConfigSchema.is_active == True
            ).first()
            
            if not schema:
                errors.append(ValidationError(
                    path="schema_id",
                    message=f"Schema with ID {schema_id} not found or inactive",
                    error_type="schema_not_found"
                ))
                return ConfigValidationResponse(
                    is_valid=False,
                    errors=errors,
                    schema_id=schema_id
                )
            
            schema_def = schema.schema_definition
            
            # Basic JSON schema validation (can be extended with jsonschema library)
            errors = self._validate_against_schema(config_data, schema_def, "")
            
            return ConfigValidationResponse(
                is_valid=len(errors) == 0,
                errors=errors,
                schema_id=schema_id
            )
            
        except Exception as e:
            errors.append(ValidationError(
                path="",
                message=f"Validation error: {str(e)}",
                error_type="validation_exception"
            ))
            return ConfigValidationResponse(
                is_valid=False,
                errors=errors,
                schema_id=schema_id
            )
    
    def _validate_against_schema(
        self,
        config_data: Dict[str, Any],
        schema_def: Dict[str, Any],
        path: str
    ) -> List[ValidationError]:
        """
        Validate configuration data against a JSON schema definition.
        
        Args:
            config_data: The configuration data to validate
            schema_def: The JSON schema definition
            path: Current path in the configuration (for error reporting)
            
        Returns:
            List of validation errors
        """
        errors = []
        
        try:
            # Check required fields
            if "required" in schema_def and isinstance(schema_def["required"], list):
                for required_field in schema_def["required"]:
                    if required_field not in config_data:
                        errors.append(ValidationError(
                            path=f"{path}.{required_field}" if path else required_field,
                            message=f"Required field '{required_field}' is missing",
                            error_type="required_field_missing"
                        ))
            
            # Check field types
            if "properties" in schema_def and isinstance(schema_def["properties"], dict):
                for field, field_schema in schema_def["properties"].items():
                    if field in config_data:
                        value = config_data[field]
                        field_type = field_schema.get("type")
                        
                        if field_type:
                            if field_type == "string" and not isinstance(value, str):
                                errors.append(ValidationError(
                                    path=f"{path}.{field}" if path else field,
                                    message=f"Field '{field}' must be a string",
                                    error_type="type_mismatch"
                                ))
                            elif field_type == "number" and not isinstance(value, (int, float)):
                                errors.append(ValidationError(
                                    path=f"{path}.{field}" if path else field,
                                    message=f"Field '{field}' must be a number",
                                    error_type="type_mismatch"
                                ))
                            elif field_type == "boolean" and not isinstance(value, bool):
                                errors.append(ValidationError(
                                    path=f"{path}.{field}" if path else field,
                                    message=f"Field '{field}' must be a boolean",
                                    error_type="type_mismatch"
                                ))
                            elif field_type == "array" and not isinstance(value, list):
                                errors.append(ValidationError(
                                    path=f"{path}.{field}" if path else field,
                                    message=f"Field '{field}' must be an array",
                                    error_type="type_mismatch"
                                ))
                            elif field_type == "object" and not isinstance(value, dict):
                                errors.append(ValidationError(
                                    path=f"{path}.{field}" if path else field,
                                    message=f"Field '{field}' must be an object",
                                    error_type="type_mismatch"
                                ))
            
            # Recursively validate nested objects
            if "properties" in schema_def and isinstance(schema_def["properties"], dict):
                for field, field_schema in schema_def["properties"].items():
                    if field in config_data and isinstance(config_data[field], dict):
                        nested_errors = self._validate_against_schema(
                            config_data[field],
                            field_schema,
                            f"{path}.{field}" if path else field
                        )
                        errors.extend(nested_errors)
            
            return errors
            
        except Exception as e:
            errors.append(ValidationError(
                path=path,
                message=f"Schema validation error: {str(e)}",
                error_type="schema_error"
            ))
            return errors
    
    # ============== Schema Methods ==============
    
    def create_schema(
        self,
        schema: ConfigSchemaCreate,
        db: Session
    ) -> ConfigSchemaResponse:
        """Create a new configuration schema"""
        db_schema = ConfigSchema(
            name=schema.name,
            description=schema.description,
            schema_type=SchemaType(schema.schema_type.value) if schema.schema_type else SchemaType.CUSTOM,
            schema_definition=schema.schema_definition,
            is_active=schema.is_active if schema.is_active is not None else True
        )
        db.add(db_schema)
        db.commit()
        db.refresh(db_schema)
        return ConfigSchemaResponse.model_validate(db_schema)
    
    def get_schema(self, schema_id: UUID, db: Session) -> Optional[ConfigSchemaResponse]:
        """Get a configuration schema by ID"""
        schema = db.query(ConfigSchema).filter(ConfigSchema.id == schema_id).first()
        if schema:
            return ConfigSchemaResponse.model_validate(schema)
        return None
    
    def list_schemas(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        schema_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> PaginatedConfigSchemaResponse:
        """List configuration schemas with optional filtering"""
        query = db.query(ConfigSchema)
        
        if schema_type:
            query = query.filter(ConfigSchema.schema_type == SchemaType(schema_type))
        if is_active is not None:
            query = query.filter(ConfigSchema.is_active == is_active)
        
        total = query.count()
        schemas = query.offset(skip).limit(limit).all()
        
        return PaginatedConfigSchemaResponse(
            items=[ConfigSchemaResponse.model_validate(s) for s in schemas],
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
            has_more=skip + limit < total
        )
    
    def update_schema(
        self,
        schema_id: UUID,
        schema_update: ConfigSchemaUpdate,
        db: Session
    ) -> Optional[ConfigSchemaResponse]:
        """Update an existing configuration schema"""
        schema = db.query(ConfigSchema).filter(ConfigSchema.id == schema_id).first()
        if not schema:
            return None
        
        update_data = schema_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(schema, field, value)
        
        schema.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(schema)
        
        return ConfigSchemaResponse.model_validate(schema)
    
    def delete_schema(self, schema_id: UUID, db: Session) -> bool:
        """Delete a configuration schema"""
        schema = db.query(ConfigSchema).filter(ConfigSchema.id == schema_id).first()
        if not schema:
            return False
        
        db.delete(schema)
        db.commit()
        return True
    
    # ============== Version Methods ==============
    
    def create_version(
        self,
        config_id: UUID,
        version: ConfigVersionCreate,
        db: Session
    ) -> ConfigVersionResponse:
        """Create a new version of a configuration"""
        # Get the latest version number
        last_version = db.query(ConfigVersion).filter(
            ConfigVersion.config_id == config_id
        ).order_by(desc(ConfigVersion.version_number)).first()
        
        new_version_number = (last_version.version_number + 1) if last_version else 1
        
        db_version = ConfigVersion(
            config_id=config_id,
            config_schema_id=version.config_schema_id,
            version_number=new_version_number,
            configuration_data=version.configuration_data,
            changelog=version.changelog,
            created_by=version.created_by
        )
        db.add(db_version)
        db.commit()
        db.refresh(db_version)
        
        return ConfigVersionResponse.model_validate(db_version)
    
    def get_version(self, version_id: UUID, db: Session) -> Optional[ConfigVersionResponse]:
        """Get a specific version by ID"""
        version = db.query(ConfigVersion).filter(ConfigVersion.id == version_id).first()
        if version:
            return ConfigVersionResponse.model_validate(version)
        return None
    
    def list_versions(
        self,
        config_id: UUID,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> PaginatedConfigVersionResponse:
        """List all versions of a configuration"""
        query = db.query(ConfigVersion).filter(ConfigVersion.config_id == config_id)
        total = query.count()
        versions = query.order_by(desc(ConfigVersion.version_number)).offset(skip).limit(limit).all()
        
        return PaginatedConfigVersionResponse(
            items=[ConfigVersionResponse.model_validate(v) for v in versions],
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
            has_more=skip + limit < total
        )
    
    def rollback(
        self,
        config_id: UUID,
        version_id: UUID,
        changelog: str,
        db: Session
    ) -> RollbackResponse:
        """Rollback a configuration to a previous version"""
        # Get the target version
        target_version = db.query(ConfigVersion).filter(ConfigVersion.id == version_id).first()
        if not target_version:
            return RollbackResponse(
                success=False,
                previous_version=None,
                new_version=None,
                message=f"Version {version_id} not found"
            )
        
        # Create a new version with the target version's data
        last_version = db.query(ConfigVersion).filter(
            ConfigVersion.config_id == config_id
        ).order_by(desc(ConfigVersion.version_number)).first()
        
        new_version_number = (last_version.version_number + 1) if last_version else 1
        
        new_version = ConfigVersion(
            config_id=config_id,
            config_schema_id=target_version.config_schema_id,
            version_number=new_version_number,
            configuration_data=target_version.configuration_data,
            changelog=changelog or f"Rolled back to version {target_version.version_number}",
            created_by="system"
        )
        db.add(new_version)
        db.commit()
        db.refresh(new_version)
        
        return RollbackResponse(
            success=True,
            previous_version=ConfigVersionResponse.model_validate(target_version),
            new_version=ConfigVersionResponse.model_validate(new_version),
            message=f"Successfully rolled back to version {target_version.version_number}"
        )
    
    # ============== Template Methods ==============
    
    def create_template(
        self,
        template: ConfigTemplateCreate,
        db: Session
    ) -> ConfigTemplateResponse:
        """Create a new configuration template"""
        db_template = ConfigTemplate(
            name=template.name,
            description=template.description,
            config_schema_id=template.config_schema_id,
            template_data=template.template_data,
            parameters=template.parameters,
            is_public=template.is_public if template.is_public is not None else False,
            user_id=template.user_id
        )
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        return ConfigTemplateResponse.model_validate(db_template)
    
    def get_template(self, template_id: UUID, db: Session) -> Optional[ConfigTemplateResponse]:
        """Get a template by ID"""
        template = db.query(ConfigTemplate).filter(ConfigTemplate.id == template_id).first()
        if template:
            return ConfigTemplateResponse.model_validate(template)
        return None
    
    def list_templates(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        schema_id: Optional[UUID] = None,
        is_public: Optional[bool] = None
    ) -> PaginatedConfigTemplateResponse:
        """List configuration templates with optional filtering"""
        query = db.query(ConfigTemplate)
        
        if schema_id:
            query = query.filter(ConfigTemplate.config_schema_id == schema_id)
        if is_public is not None:
            query = query.filter(ConfigTemplate.is_public == is_public)
        
        total = query.count()
        templates = query.offset(skip).limit(limit).all()
        
        return PaginatedConfigTemplateResponse(
            items=[ConfigTemplateResponse.model_validate(t) for t in templates],
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
            has_more=skip + limit < total
        )
    
    def update_template(
        self,
        template_id: UUID,
        template_update: ConfigTemplateUpdate,
        db: Session
    ) -> Optional[ConfigTemplateResponse]:
        """Update an existing template"""
        template = db.query(ConfigTemplate).filter(ConfigTemplate.id == template_id).first()
        if not template:
            return None
        
        update_data = template_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(template, field, value)
        
        template.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(template)
        
        return ConfigTemplateResponse.model_validate(template)
    
    def delete_template(self, template_id: UUID, db: Session) -> bool:
        """Delete a template"""
        template = db.query(ConfigTemplate).filter(ConfigTemplate.id == template_id).first()
        if not template:
            return False
        
        db.delete(template)
        db.commit()
        return True
    
    def apply_template(
        self,
        template_id: UUID,
        parameters: Dict[str, Any],
        db: Session
    ) -> ApplyTemplateResponse:
        """Apply a template with given parameters"""
        template = db.query(ConfigTemplate).filter(ConfigTemplate.id == template_id).first()
        if not template:
            return ApplyTemplateResponse(
                success=False,
                applied_config={},
                template_id=template_id,
                applied_at=datetime.utcnow()
            )
        
        # Apply parameters to template
        applied_config = self._apply_parameters(template.template_data, parameters)
        
        return ApplyTemplateResponse(
            success=True,
            applied_config=applied_config,
            template_id=template_id,
            applied_at=datetime.utcnow()
        )
    
    def _apply_parameters(
        self,
        template_data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply parameters to template data"""
        result = template_data.copy()
        
        for key, value in parameters.items():
            # Replace parameter placeholders with actual values
            if isinstance(value, str):
                result[key] = value
            elif isinstance(value, dict):
                if key in result and isinstance(result[key], dict):
                    result[key] = self._apply_parameters(result[key], value)
                else:
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    # ============== Environment Config Methods ==============
    
    def get_environment_config(
        self,
        config_id: UUID,
        environment: str,
        db: Session
    ) -> Optional[EnvironmentConfigResponse]:
        """Get environment-specific configuration"""
        env_config = db.query(EnvironmentConfig).filter(
            EnvironmentConfig.config_id == config_id,
            EnvironmentConfig.environment == EnvironmentType(environment),
            EnvironmentConfig.is_active == True
        ).first()
        
        if env_config:
            return EnvironmentConfigResponse.model_validate(env_config)
        return None
    
    def update_environment_config(
        self,
        config_id: UUID,
        environment: str,
        config_update: EnvironmentConfigUpdate,
        db: Session
    ) -> Optional[EnvironmentConfigResponse]:
        """Update environment-specific configuration"""
        env_config = db.query(EnvironmentConfig).filter(
            EnvironmentConfig.config_id == config_id,
            EnvironmentConfig.environment == EnvironmentType(environment)
        ).first()
        
        if not env_config:
            # Create if it doesn't exist
            env_config = EnvironmentConfig(
                config_id=config_id,
                environment=EnvironmentType(environment),
                config_data=config_update.config_data or {},
                overrides=config_update.overrides,
                is_active=config_update.is_active if config_update.is_active is not None else True
            )
            db.add(env_config)
        else:
            update_data = config_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None:
                    setattr(env_config, field, value)
        
        env_config.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(env_config)
        
        return EnvironmentConfigResponse.model_validate(env_config)
    
    # ============== Diff Methods ==============
    
    def compare_configs(
        self,
        config_a: Dict[str, Any],
        config_b: Dict[str, Any]
    ) -> ConfigDiffResponse:
        """Compare two configurations and return differences"""
        differences = []
        added_count = 0
        removed_count = 0
        modified_count = 0
        
        try:
            diff = deepdiff.DeepDiff(config_a, config_b, ignore_order=True)
            
            # Process added items
            for path, value in diff.get("dictionary_item_added", {}).items():
                differences.append(DiffEntry(
                    path=path,
                    old_value=None,
                    new_value=value,
                    change_type="ADDED"
                ))
                added_count += 1
            
            # Process removed items
            for path, value in diff.get("dictionary_item_removed", {}).items():
                differences.append(DiffEntry(
                    path=path,
                    old_value=value,
                    new_value=None,
                    change_type="REMOVED"
                ))
                removed_count += 1
            
            # Process changed values
            for path, change in diff.get("values_changed", {}).items():
                differences.append(DiffEntry(
                    path=path,
                    old_value=change.old_value,
                    new_value=change.new_value,
                    change_type="MODIFIED"
                ))
                modified_count += 1
            
            return ConfigDiffResponse(
                has_differences=len(differences) > 0,
                differences=differences,
                added_count=added_count,
                removed_count=removed_count,
                modified_count=modified_count
            )
            
        except Exception as e:
            return ConfigDiffResponse(
                has_differences=False,
                differences=[],
                added_count=0,
                removed_count=0,
                modified_count=0
            )
    
    # ============== Snapshot Methods ==============
    
    def create_snapshot(
        self,
        snapshot: ConfigSnapshotCreate,
        db: Session
    ) -> ConfigSnapshotResponse:
        """Create a point-in-time snapshot"""
        db_snapshot = ConfigSnapshot(
            config_id=snapshot.config_id,
            version_id=snapshot.version_id,
            snapshot_data=snapshot.snapshot_data,
            snapshot_type=SnapshotType(snapshot.snapshot_type.value) if snapshot.snapshot_type else SnapshotType.MANUAL
        )
        db.add(db_snapshot)
        db.commit()
        db.refresh(db_snapshot)
        
        return ConfigSnapshotResponse.model_validate(db_snapshot)
    
    def list_snapshots(
        self,
        config_id: UUID,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        snapshot_type: Optional[str] = None
    ) -> PaginatedConfigSnapshotResponse:
        """List all snapshots for a configuration"""
        query = db.query(ConfigSnapshot).filter(ConfigSnapshot.config_id == config_id)
        
        if snapshot_type:
            query = query.filter(ConfigSnapshot.snapshot_type == SnapshotType(snapshot_type))
        
        total = query.count()
        snapshots = query.order_by(desc(ConfigSnapshot.created_at)).offset(skip).limit(limit).all()
        
        return PaginatedConfigSnapshotResponse(
            items=[ConfigSnapshotResponse.model_validate(s) for s in snapshots],
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
            has_more=skip + limit < total
        )
    
    # ============== Main Configuration Methods ==============
    
    def create_configuration(
        self,
        configuration: ConfigurationCreate,
        db: Session
    ) -> ConfigurationResponse:
        """Create a new main configuration"""
        db_config = Configuration(
            name=configuration.name,
            description=configuration.description,
            config_schema_id=configuration.config_schema_id,
            created_by=configuration.created_by
        )
        db.add(db_config)
        db.commit()
        db.refresh(db_config)
        
        return ConfigurationResponse.model_validate(db_config)
    
    def get_configuration(self, config_id: UUID, db: Session) -> Optional[ConfigurationResponse]:
        """Get a configuration by ID"""
        config = db.query(Configuration).filter(Configuration.id == config_id).first()
        if config:
            return ConfigurationResponse.model_validate(config)
        return None
    
    def list_configurations(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        schema_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> List[ConfigurationResponse]:
        """List all configurations with optional filtering"""
        query = db.query(Configuration)
        
        if schema_id:
            query = query.filter(Configuration.config_schema_id == schema_id)
        if is_active is not None:
            query = query.filter(Configuration.is_active == is_active)
        
        configurations = query.offset(skip).limit(limit).all()
        return [ConfigurationResponse.model_validate(c) for c in configurations]
    
    def update_configuration(
        self,
        config_id: UUID,
        config_update: ConfigurationUpdate,
        db: Session
    ) -> Optional[ConfigurationResponse]:
        """Update an existing configuration"""
        config = db.query(Configuration).filter(Configuration.id == config_id).first()
        if not config:
            return None
        
        update_data = config_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(config, field, value)
        
        config.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(config)
        
        return ConfigurationResponse.model_validate(config)
    
    def delete_configuration(self, config_id: UUID, db: Session) -> bool:
        """Delete a configuration"""
        config = db.query(Configuration).filter(Configuration.id == config_id).first()
        if not config:
            return False
        
        db.delete(config)
        db.commit()
        return True
