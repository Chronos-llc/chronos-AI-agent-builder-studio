/**
 * Configuration Management Types
 * Advanced Configuration Management System for Chronos AI Agent Builder Studio
 */

// ============== Enum Types ==============

export type SchemaType = 'AGENT' | 'WORKFLOW' | 'SYSTEM' | 'CUSTOM';

export type SnapshotType = 'MANUAL' | 'AUTOMATED' | 'SCHEDULED';

export type EnvironmentType = 'DEVELOPMENT' | 'STAGING' | 'PRODUCTION';

export type ChangeType = 'ADDED' | 'REMOVED' | 'MODIFIED';

// ============== ConfigSchema Types ==============

export interface ConfigSchema {
  id: string;
  name: string;
  description?: string;
  schema_type: SchemaType;
  schema_definition: Record<string, unknown>;
  version: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ConfigSchemaCreate {
  name: string;
  description?: string;
  schema_type: SchemaType;
  schema_definition: Record<string, unknown>;
  is_active?: boolean;
}

export interface ConfigSchemaUpdate {
  name?: string;
  description?: string;
  schema_type?: SchemaType;
  schema_definition?: Record<string, unknown>;
  is_active?: boolean;
}

// ============== ConfigVersion Types ==============

export interface ConfigVersion {
  id: string;
  config_id?: string;
  config_schema_id: string;
  version_number: number;
  configuration_data: Record<string, unknown>;
  changelog?: string;
  created_by?: string;
  created_at: string;
}

export interface ConfigVersionCreate {
  config_id?: string;
  config_schema_id: string;
  configuration_data: Record<string, unknown>;
  changelog?: string;
  created_by?: string;
}

// ============== ConfigSnapshot Types ==============

export interface ConfigSnapshot {
  id: string;
  config_id: string;
  version_id: string;
  snapshot_data: Record<string, unknown>;
  snapshot_type: SnapshotType;
  created_at: string;
}

export interface ConfigSnapshotCreate {
  config_id: string;
  version_id: string;
  snapshot_data: Record<string, unknown>;
  snapshot_type?: SnapshotType;
}

// ============== ConfigTemplate Types ==============

export interface ConfigTemplate {
  id: string;
  name: string;
  description?: string;
  config_schema_id: string;
  template_data: Record<string, unknown>;
  parameters?: Record<string, unknown>;
  is_public: boolean;
  user_id?: string;
  created_at: string;
  updated_at: string;
}

export interface ConfigTemplateCreate {
  name: string;
  description?: string;
  config_schema_id: string;
  template_data: Record<string, unknown>;
  parameters?: Record<string, unknown>;
  is_public?: boolean;
  user_id?: string;
}

export interface ConfigTemplateUpdate {
  name?: string;
  description?: string;
  template_data?: Record<string, unknown>;
  parameters?: Record<string, unknown>;
  is_public?: boolean;
}

// ============== EnvironmentConfig Types ==============

export interface EnvironmentConfig {
  id: string;
  config_id: string;
  environment: EnvironmentType;
  config_data: Record<string, unknown>;
  overrides?: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface EnvironmentConfigCreate {
  config_id: string;
  environment: EnvironmentType;
  config_data: Record<string, unknown>;
  overrides?: Record<string, unknown>;
  is_active?: boolean;
}

export interface EnvironmentConfigUpdate {
  config_data?: Record<string, unknown>;
  overrides?: Record<string, unknown>;
  is_active?: boolean;
}

// ============== Configuration Types ==============

export interface Configuration {
  id: string;
  name: string;
  description?: string;
  config_schema_id: string;
  current_version_id?: string;
  is_active: boolean;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface ConfigurationCreate {
  name: string;
  description?: string;
  config_schema_id: string;
  created_by?: string;
}

export interface ConfigurationUpdate {
  name?: string;
  description?: string;
  current_version_id?: string;
  is_active?: boolean;
}

// ============== Validation Types ==============

export interface ValidationError {
  path: string;
  message: string;
  error_type: string;
}

export interface ConfigValidationResponse {
  is_valid: boolean;
  errors: ValidationError[];
  schema_id: string;
  validated_at: string;
}

export interface ConfigValidationRequest {
  config_data: Record<string, unknown>;
  schema_id: string;
}

// ============== Diff Types ==============

export interface DiffEntry {
  path: string;
  old_value: unknown;
  new_value: unknown;
  change_type: ChangeType;
}

export interface ConfigDiffResponse {
  has_differences: boolean;
  differences: DiffEntry[];
  added_count: number;
  removed_count: number;
  modified_count: number;
  compared_at: string;
}

export interface ConfigDiffRequest {
  config_a: Record<string, unknown>;
  config_b: Record<string, unknown>;
}

// ============== Rollback Types ==============

export interface RollbackRequest {
  version_id: string;
  changelog?: string;
}

export interface RollbackResponse {
  success: boolean;
  previous_version?: ConfigVersion;
  new_version?: ConfigVersion;
  message: string;
}

// ============== Template Application Types ==============

export interface ApplyTemplateRequest {
  template_id: string;
  parameters?: Record<string, unknown>;
}

export interface ApplyTemplateResponse {
  success: boolean;
  applied_config: Record<string, unknown>;
  template_id: string;
  applied_at: string;
}

// ============== Paginated Response Types ==============

export interface PaginatedConfigSchemaResponse {
  items: ConfigSchema[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface PaginatedConfigVersionResponse {
  items: ConfigVersion[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface PaginatedConfigTemplateResponse {
  items: ConfigTemplate[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface PaginatedConfigSnapshotResponse {
  items: ConfigSnapshot[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

// ============== UI State Types ==============

export interface ConfigEditorState {
  currentConfig: Record<string, unknown> | null;
  selectedSchemaId: string | null;
  selectedVersionId: string | null;
  selectedEnvironment: EnvironmentType;
  isDirty: boolean;
  isValidating: boolean;
  validationErrors: ValidationError[];
}

export interface DiffViewerState {
  configA: Record<string, unknown> | null;
  configB: Record<string, unknown> | null;
  differences: DiffEntry[];
  filter: ChangeType | 'ALL';
}

export interface TemplateGalleryState {
  templates: ConfigTemplate[];
  selectedTemplate: ConfigTemplate | null;
  previewParameters: Record<string, unknown>;
  isApplying: boolean;
}

// ============== JSON Schema Types ==============

export interface JSONSchema {
  type?: string;
  properties?: Record<string, JSONSchema>;
  required?: string[];
  description?: string;
  enum?: unknown[];
  default?: unknown;
  items?: JSONSchema;
  additionalProperties?: boolean | JSONSchema;
}
