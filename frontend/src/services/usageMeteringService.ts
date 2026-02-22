import type {
  AddonAllocation,
  AddonAllocationCreateRequest,
  AgentUsageResourcesResponse,
  UsageResourcesResponse,
} from '../types/usageMetering'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const getAccessToken = () => {
  if (typeof globalThis === 'undefined' || !('localStorage' in globalThis)) return null
  return globalThis.localStorage.getItem('chronos_access_token') || globalThis.localStorage.getItem('access_token')
}

const withAuth = (init: RequestInit = {}): RequestInit => {
  const token = getAccessToken()
  const headers = new Headers(init.headers || {})
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  return {
    ...init,
    headers,
    credentials: 'include',
  }
}

const handleResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(body.detail || `Request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

export const usageMeteringService = {
  async getUserUsageResources(): Promise<UsageResourcesResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/usage/resources`, withAuth())
    return handleResponse<UsageResourcesResponse>(response)
  },

  async getAgentUsageResources(agentId: number): Promise<AgentUsageResourcesResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/usage/resources/agents/${agentId}`, withAuth())
    return handleResponse<AgentUsageResourcesResponse>(response)
  },

  async listAddons(userId?: number): Promise<AddonAllocation[]> {
    const query = userId ? `?user_id=${userId}` : ''
    const response = await fetch(`${API_BASE_URL}/api/v1/admin/usage/addons${query}`, withAuth())
    return handleResponse<AddonAllocation[]>(response)
  },

  async createAddon(payload: AddonAllocationCreateRequest): Promise<AddonAllocation> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/admin/usage/addons`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }),
    )
    return handleResponse<AddonAllocation>(response)
  },

  async deleteAddon(allocationId: number): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/admin/usage/addons/${allocationId}`,
      withAuth({ method: 'DELETE' }),
    )
    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(body.detail || `Request failed (${response.status})`)
    }
  },
}

