/**
 * Configuration Management API Service
 * Advanced Configuration Management System for Chronos AI Agent Builder Studio
 */

import type {
  ConfigSchema,
  ConfigSchemaCreate,
  ConfigSchemaUpdate,
  ConfigVersion,
  ConfigVersionCreate,
  ConfigSnapshot,
  ConfigSnapshotCreate,
  ConfigTemplate,
  ConfigTemplateCreate,
  ConfigTemplateUpdate,
  EnvironmentConfig,
  EnvironmentConfigUpdate,
  ConfigValidationRequest,
  ConfigValidationResponse,
  ConfigDiffRequest,
  ConfigDiffResponse,
  RollbackRequest,
  RollbackResponse,
  ApplyTemplateRequest,
  ApplyTemplateResponse,
  Configuration,
  ConfigurationCreate,
  ConfigurationUpdate,
  PaginatedConfigSchemaResponse,
  PaginatedConfigVersionResponse,
  PaginatedConfigTemplateResponse,
  PaginatedConfigSnapshotResponse,
} from '../types/configManagement';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = `${API_BASE_URL}/api/config-management`;

// ============== Helper Functions ==============

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error ${response.status}`);
  }
  return response.json();
}

function buildQueryString(params: Record<string, unknown>): string {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      query.append(key, String(value));
    }
  });
  return query.toString() ? `?${query.toString()}` : '';
}

// ============== Validation API ==============

export async function validateConfig(
  configData: Record<string, unknown>,
  schemaId: string
): Promise<ConfigValidationResponse> {
  const response = await fetch(`${API_BASE}/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ config_data: configData, schema_id: schemaId }),
  });
  return handleResponse<ConfigValidationResponse>(response);
}

// ============== Schema API ==============

export async function listSchemas(
  skip = 0,
  limit = 100,
  schemaType?: string,
  isActive?: boolean
): Promise<PaginatedConfigSchemaResponse> {
  const params: Record<string, unknown> = { skip, limit };
  if (schemaType) params.schema_type = schemaType;
  if (isActive !== undefined) params.is_active = isActive;
  
  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/schemas${queryString}`);
  return handleResponse<PaginatedConfigSchemaResponse>(response);
}

export async function createSchema(schema: ConfigSchemaCreate): Promise<ConfigSchema> {
  const response = await fetch(`${API_BASE}/schemas`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(schema),
  });
  return handleResponse<ConfigSchema>(response);
}

export async function getSchema(schemaId: string): Promise<ConfigSchema> {
  const response = await fetch(`${API_BASE}/schemas/${schemaId}`);
  return handleResponse<ConfigSchema>(response);
}

export async function updateSchema(
  schemaId: string,
  schema: ConfigSchemaUpdate
): Promise<ConfigSchema> {
  const response = await fetch(`${API_BASE}/schemas/${schemaId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(schema),
  });
  return handleResponse<ConfigSchema>(response);
}

export async function deleteSchema(schemaId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/schemas/${schemaId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete schema');
  }
}

// ============== Version API ==============

export async function listVersions(
  configId: string,
  skip = 0,
  limit = 100
): Promise<PaginatedConfigVersionResponse> {
  const queryString = buildQueryString({ skip, limit });
  const response = await fetch(`${API_BASE}/configs/${configId}/versions${queryString}`);
  return handleResponse<PaginatedConfigVersionResponse>(response);
}

export async function createVersion(
  configId: string,
  version: ConfigVersionCreate
): Promise<ConfigVersion> {
  const response = await fetch(`${API_BASE}/configs/${configId}/versions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(version),
  });
  return handleResponse<ConfigVersion>(response);
}

export async function getVersion(
  configId: string,
  versionId: string
): Promise<ConfigVersion> {
  const response = await fetch(`${API_BASE}/configs/${configId}/versions/${versionId}`);
  return handleResponse<ConfigVersion>(response);
}

export async function rollback(
  configId: string,
  versionId: string,
  changelog?: string
): Promise<RollbackResponse> {
  const response = await fetch(`${API_BASE}/configs/${configId}/rollback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ version_id: versionId, changelog }),
  });
  return handleResponse<RollbackResponse>(response);
}

// ============== Template API ==============

export async function listTemplates(
  skip = 0,
  limit = 100,
  schemaId?: string,
  isPublic?: boolean
): Promise<PaginatedConfigTemplateResponse> {
  const params: Record<string, unknown> = { skip, limit };
  if (schemaId) params.schema_id = schemaId;
  if (isPublic !== undefined) params.is_public = isPublic;
  
  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/templates${queryString}`);
  return handleResponse<PaginatedConfigTemplateResponse>(response);
}

export async function createTemplate(template: ConfigTemplateCreate): Promise<ConfigTemplate> {
  const response = await fetch(`${API_BASE}/templates`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(template),
  });
  return handleResponse<ConfigTemplate>(response);
}

export async function getTemplate(templateId: string): Promise<ConfigTemplate> {
  const response = await fetch(`${API_BASE}/templates/${templateId}`);
  return handleResponse<ConfigTemplate>(response);
}

export async function updateTemplate(
  templateId: string,
  template: ConfigTemplateUpdate
): Promise<ConfigTemplate> {
  const response = await fetch(`${API_BASE}/templates/${templateId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(template),
  });
  return handleResponse<ConfigTemplate>(response);
}

export async function deleteTemplate(templateId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/templates/${templateId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete template');
  }
}

export async function applyTemplate(
  templateId: string,
  parameters: Record<string, unknown>
): Promise<ApplyTemplateResponse> {
  const response = await fetch(`${API_BASE}/templates/${templateId}/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ template_id: templateId, parameters }),
  });
  return handleResponse<ApplyTemplateResponse>(response);
}

// ============== Environment API ==============

export async function getEnvironmentConfig(
  configId: string,
  environment: string
): Promise<EnvironmentConfig> {
  const response = await fetch(`${API_BASE}/environments/${configId}?environment=${environment}`);
  return handleResponse<EnvironmentConfig>(response);
}

export async function updateEnvironmentConfig(
  configId: string,
  environment: string,
  config: EnvironmentConfigUpdate
): Promise<EnvironmentConfig> {
  const response = await fetch(`${API_BASE}/environments/${configId}?environment=${environment}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  return handleResponse<EnvironmentConfig>(response);
}

// ============== Diff API ==============

export async function compareConfigs(
  configA: Record<string, unknown>,
  configB: Record<string, unknown>
): Promise<ConfigDiffResponse> {
  const response = await fetch(`${API_BASE}/diff`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ config_a: configA, config_b: configB }),
  });
  return handleResponse<ConfigDiffResponse>(response);
}

// ============== Snapshot API ==============

export async function createSnapshot(snapshot: ConfigSnapshotCreate): Promise<ConfigSnapshot> {
  const response = await fetch(`${API_BASE}/snapshots`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(snapshot),
  });
  return handleResponse<ConfigSnapshot>(response);
}

export async function listSnapshots(
  configId: string,
  skip = 0,
  limit = 100,
  snapshotType?: string
): Promise<PaginatedConfigSnapshotResponse> {
  const params: Record<string, unknown> = { skip, limit };
  if (snapshotType) params.snapshot_type = snapshotType;
  
  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/snapshots/${configId}${queryString}`);
  return handleResponse<PaginatedConfigSnapshotResponse>(response);
}

// ============== Configuration API ==============

export async function listConfigurations(
  skip = 0,
  limit = 100,
  schemaId?: string,
  isActive?: boolean
): Promise<Configuration[]> {
  const params: Record<string, unknown> = { skip, limit };
  if (schemaId) params.schema_id = schemaId;
  if (isActive !== undefined) params.is_active = isActive;
  
  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/configurations${queryString}`);
  return handleResponse<Configuration[]>(response);
}

export async function createConfiguration(
  configuration: ConfigurationCreate
): Promise<Configuration> {
  const response = await fetch(`${API_BASE}/configurations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(configuration),
  });
  return handleResponse<Configuration>(response);
}

export async function getConfiguration(configId: string): Promise<Configuration> {
  const response = await fetch(`${API_BASE}/configurations/${configId}`);
  return handleResponse<Configuration>(response);
}

export async function updateConfiguration(
  configId: string,
  configuration: ConfigurationUpdate
): Promise<Configuration> {
  const response = await fetch(`${API_BASE}/configurations/${configId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(configuration),
  });
  return handleResponse<Configuration>(response);
}

export async function deleteConfiguration(configId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/configurations/${configId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete configuration');
  }
}
