import axios from 'axios'
import type { IntegrationSubmissionCreate } from './integrationSubmissionService'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000'
const ADMIN_HUB_BASE = `${API_BASE_URL}/api/v1/admin/integrations/hub`

const authHeaders = () => ({
  Authorization: `Bearer ${localStorage.getItem('access_token') || ''}`,
  'Content-Type': 'application/json',
})

// ─── Code-review-specified interfaces ────────────────────────────────────────

export interface AdminIntegration {
  id: string
  name: string
  description: string
  category: string
  status: 'active' | 'inactive' | 'pending'
  created_at: string
  updated_at: string
  config_schema?: Record<string, unknown>
  icon_url?: string
  publisher?: string
  version?: string
}

export interface CreateIntegrationPayload {
  name: string
  description: string
  category: string
  config_schema?: Record<string, unknown>
  icon_url?: string
  publisher?: string
  version?: string
}

export interface UpdateIntegrationPayload extends Partial<CreateIntegrationPayload> {
  status?: 'active' | 'inactive' | 'pending'
}

export interface AdminIntegrationHubItem {
  id: number
  name: string
  subtitle?: string | null
  description?: string | null
  integration_type: string
  category: string
  icon?: string | null
  app_icon_url?: string | null
  version: string
  status: string
  visibility: string
  download_count: number
  review_count: number
  rating: number
  usage_count: number
  active_config_count: number
  total_config_count: number
  created_at: string
  updated_at: string
  published_at?: string | null
  is_workflow_node_enabled: boolean
}

export interface AdminIntegrationHubListResponse {
  items: AdminIntegrationHubItem[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

export interface AdminIntegrationHubDetail {
  integration: Record<string, any>
}

export interface AdminIntegrationHubStatistics {
  integration_id: number
  download_count: number
  review_count: number
  rating: number
  active_config_count: number
  total_config_count: number
  usage_count: number
  success_count: number
  error_count: number
  avg_response_time: number
}

export const adminIntegrationService = {
  async listHub(params?: {
    query?: string
    category?: string
    integration_type?: string
    status?: string
    page?: number
    page_size?: number
  }): Promise<AdminIntegrationHubListResponse> {
    const response = await axios.get<AdminIntegrationHubListResponse>(ADMIN_HUB_BASE, {
      headers: authHeaders(),
      params,
    })
    return response.data
  },

  async getHubIntegration(integrationId: number): Promise<AdminIntegrationHubDetail> {
    const response = await axios.get<AdminIntegrationHubDetail>(`${ADMIN_HUB_BASE}/${integrationId}`, {
      headers: authHeaders(),
    })
    return response.data
  },

  async getHubStatistics(integrationId: number): Promise<AdminIntegrationHubStatistics> {
    const response = await axios.get<AdminIntegrationHubStatistics>(`${ADMIN_HUB_BASE}/${integrationId}/statistics`, {
      headers: authHeaders(),
    })
    return response.data
  },

  async createHubIntegration(payload: IntegrationSubmissionCreate): Promise<Record<string, any>> {
    const response = await axios.post(`${ADMIN_HUB_BASE}`, payload, {
      headers: authHeaders(),
    })
    return response.data
  },

  async updateHubIntegration(
    integrationId: number,
    payload: Partial<IntegrationSubmissionCreate>,
  ): Promise<Record<string, any>> {
    const response = await axios.patch(`${ADMIN_HUB_BASE}/${integrationId}`, payload, {
      headers: authHeaders(),
    })
    return response.data
  },

  async deleteHubIntegration(integrationId: number): Promise<{ message: string; integration_id: number }> {
    const response = await axios.delete<{ message: string; integration_id: number }>(`${ADMIN_HUB_BASE}/${integrationId}`, {
      headers: authHeaders(),
    })
    return response.data
  },

  // ─── Code-review-specified CRUD methods ──────────────────────────────────

  async getIntegrations(): Promise<AdminIntegration[]> {
    const response = await axios.get<AdminIntegration[]>(`${API_BASE_URL}/api/admin/integrations`, {
      headers: authHeaders(),
    })
    return response.data
  },

  async getIntegration(id: string): Promise<AdminIntegration> {
    const response = await axios.get<AdminIntegration>(`${API_BASE_URL}/api/admin/integrations/${id}`, {
      headers: authHeaders(),
    })
    return response.data
  },

  async createIntegration(payload: CreateIntegrationPayload): Promise<AdminIntegration> {
    const response = await axios.post<AdminIntegration>(`${API_BASE_URL}/api/admin/integrations`, payload, {
      headers: authHeaders(),
    })
    return response.data
  },

  async updateIntegration(id: string, payload: UpdateIntegrationPayload): Promise<AdminIntegration> {
    const response = await axios.put<AdminIntegration>(`${API_BASE_URL}/api/admin/integrations/${id}`, payload, {
      headers: authHeaders(),
    })
    return response.data
  },

  async deleteIntegration(id: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/api/admin/integrations/${id}`, {
      headers: authHeaders(),
    })
  },
}

export default adminIntegrationService
