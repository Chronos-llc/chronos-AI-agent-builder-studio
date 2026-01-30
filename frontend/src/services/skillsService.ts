/**
 * Skills API Service
 * Handles all skills-related API calls for Chronos AI Agent Builder Studio
 */

import type {
  Skill,
  SkillCreate,
  SkillUpdate,
  SkillList,
  AgentSkillInstallation,
  AgentSkillInstallationCreate,
  AgentSkillInstallationUpdate,
  AgentSkillInstallationList,
  SkillSearchParams,
  SkillExecutionRequest,
  SkillExecutionResponse,
  SkillStatistics
} from '../types/skills';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = `${API_BASE_URL}/api/skills`;

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
      if (Array.isArray(value)) {
        value.forEach(item => query.append(key, String(item)));
      } else {
        query.append(key, String(value));
      }
    }
  });
  return query.toString() ? `?${query.toString()}` : '';
}

// ============== Skills API ==============

export async function getSkills(
  category?: string,
  tags?: string[],
  isActive?: boolean,
  isPremium?: boolean,
  searchQuery?: string,
  sortBy: string = 'created_at',
  sortOrder: string = 'desc',
  page: number = 1,
  pageSize: number = 20
): Promise<SkillList> {
  const params: Record<string, unknown> = {
    page,
    page_size: pageSize,
    sort_by: sortBy,
    sort_order: sortOrder
  };

  if (category) params.category = category;
  if (tags) params.tags = tags;
  if (isActive !== undefined) params.is_active = isActive;
  if (isPremium !== undefined) params.is_premium = isPremium;
  if (searchQuery) params.search_query = searchQuery;

  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/skills${queryString}`);
  return handleResponse<SkillList>(response);
}

export async function getSkill(skillId: number): Promise<Skill> {
  const response = await fetch(`${API_BASE}/skills/${skillId}`);
  return handleResponse<Skill>(response);
}

export async function createSkill(skill: SkillCreate): Promise<Skill> {
  const response = await fetch(`${API_BASE}/skills`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(skill),
  });
  return handleResponse<Skill>(response);
}

export async function updateSkill(skillId: number, skill: SkillUpdate): Promise<Skill> {
  const response = await fetch(`${API_BASE}/skills/${skillId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(skill),
  });
  return handleResponse<Skill>(response);
}

export async function deleteSkill(skillId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/skills/${skillId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete skill');
  }
}

export async function discoverSkills(): Promise<{ message: string; discovered: number; created: number; updated: number; errors: string[] }> {
  const response = await fetch(`${API_BASE}/skills/discover`, {
    method: 'POST',
  });
  return handleResponse<{ message: string; discovered: number; created: number; updated: number; errors: string[] }>(response);
}

export async function getSkillCategories(): Promise<{ categories: { name: string; count: number }[] }> {
  const response = await fetch(`${API_BASE}/skills/categories/list`);
  return handleResponse<{ categories: { name: string; count: number }[] }>(response);
}

// ============== Agent Skill Installation API ==============

export async function getAgentSkills(agentId: number): Promise<AgentSkillInstallationList> {
  const response = await fetch(`${API_BASE}/agents/${agentId}/skills`);
  return handleResponse<AgentSkillInstallationList>(response);
}

export async function installSkillToAgent(agentId: number, installation: AgentSkillInstallationCreate): Promise<AgentSkillInstallation> {
  const response = await fetch(`${API_BASE}/agents/${agentId}/skills`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(installation),
  });
  return handleResponse<AgentSkillInstallation>(response);
}

export async function updateAgentSkillInstallation(
  agentId: number,
  installationId: number,
  installation: AgentSkillInstallationUpdate
): Promise<AgentSkillInstallation> {
  const response = await fetch(`${API_BASE}/agents/${agentId}/skills/${installationId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(installation),
  });
  return handleResponse<AgentSkillInstallation>(response);
}

export async function uninstallSkillFromAgent(agentId: number, installationId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/agents/${agentId}/skills/${installationId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to uninstall skill');
  }
}

// ============== Skill Execution API ==============

export async function executeSkill(skillId: number, request: SkillExecutionRequest): Promise<SkillExecutionResponse> {
  const response = await fetch(`${API_BASE}/skills/${skillId}/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  return handleResponse<SkillExecutionResponse>(response);
}

// ============== Statistics API ==============

export async function getSkillsStatistics(): Promise<SkillStatistics> {
  const response = await fetch(`${API_BASE}/skills/statistics/overview`);
  return handleResponse<SkillStatistics>(response);
}

// ============== File Upload Helper ==============

export async function uploadSkillFile(file: File): Promise<string> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('File upload failed');
  }

  const result = await response.json();
  return result.url; // Return the URL of the uploaded file
}