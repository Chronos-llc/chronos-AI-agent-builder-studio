import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_BASE = `${API_BASE_URL}/api/v1/integrations`

export type SubmissionStatus =
  | 'draft'
  | 'submitted'
  | 'under_review'
  | 'approved'
  | 'rejected'
  | 'published'

export type SubmissionVisibility = 'private' | 'team' | 'public'
export type SubmissionType = 'mcp_server' | 'api'

export interface IntegrationSubmissionEvent {
  id: number
  integration_id: number
  action: string
  actor_user_id?: number
  payload: Record<string, any>
  created_at: string
}

export interface IntegrationSubmission {
  id: number
  name: string
  subtitle?: string
  description?: string
  category: string
  integration_type: SubmissionType
  visibility: SubmissionVisibility
  status: SubmissionStatus
  submission_notes?: string
  moderation_notes?: string
  app_icon_url?: string
  app_screenshots: string[]
  developer_name?: string
  website_url?: string
  support_url_or_email?: string
  privacy_policy_url?: string
  terms_url?: string
  demo_url?: string
  documentation_url?: string
  config_schema: Record<string, any>
  credentials_schema?: Record<string, any>
  supported_features: string[]
  is_workflow_node_enabled: boolean
  created_at: string
  updated_at: string
}

export interface IntegrationSubmissionCreate {
  name: string
  subtitle?: string
  description: string
  category: string
  integration_type: SubmissionType
  visibility: SubmissionVisibility
  submission_notes?: string
  app_icon_url?: string
  app_screenshots: string[]
  developer_name?: string
  website_url?: string
  support_url_or_email?: string
  privacy_policy_url?: string
  terms_url?: string
  demo_url?: string
  documentation_url?: string
  config_schema: Record<string, any>
  credentials_schema?: Record<string, any>
  supported_features: string[]
  is_workflow_node_enabled: boolean
  version?: string
}

export interface IntegrationNodeDefinition {
  node_type: 'integration_mcp_call' | 'integration_api_call'
  integration_id: number
  name: string
  description?: string
  category: string
  icon?: string
  config_schema: Record<string, any>
  credentials_schema: Record<string, any>
}

export const integrationSubmissionService = {
  async createIntegrationDirect(payload: IntegrationSubmissionCreate): Promise<IntegrationSubmission> {
    const response = await axios.post<IntegrationSubmission>(`${API_BASE}/`, payload)
    return response.data
  },

  async createSubmission(payload: IntegrationSubmissionCreate): Promise<IntegrationSubmission> {
    const response = await axios.post<IntegrationSubmission>(`${API_BASE}/submissions`, payload)
    return response.data
  },

  async updateSubmission(submissionId: number, payload: Partial<IntegrationSubmissionCreate>): Promise<IntegrationSubmission> {
    const response = await axios.put<IntegrationSubmission>(`${API_BASE}/submissions/${submissionId}`, payload)
    return response.data
  },

  async submitSubmission(submissionId: number): Promise<IntegrationSubmission> {
    const response = await axios.post<IntegrationSubmission>(`${API_BASE}/submissions/${submissionId}/submit`)
    return response.data
  },

  async listMySubmissions(): Promise<IntegrationSubmission[]> {
    const response = await axios.get<IntegrationSubmission[]>(`${API_BASE}/submissions/mine`)
    return response.data
  },

  async getSubmissionEvents(submissionId: number): Promise<IntegrationSubmissionEvent[]> {
    const response = await axios.get<IntegrationSubmissionEvent[]>(`${API_BASE}/submissions/${submissionId}/events`)
    return response.data
  },

  async uploadSubmissionImage(submissionId: number, imageUrl: string): Promise<{ image_url: string }> {
    const response = await axios.post<{ image_url: string }>(`${API_BASE}/submissions/${submissionId}/upload-image`, {
      image_url: imageUrl,
    })
    return response.data
  },

  async getWorkflowIntegrationNodes(): Promise<IntegrationNodeDefinition[]> {
    const response = await axios.get<{ nodes: IntegrationNodeDefinition[] }>('/api/v1/workflow-generation/integration-nodes')
    return response.data.nodes || []
  },
}
