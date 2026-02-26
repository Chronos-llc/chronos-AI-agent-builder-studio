import type {
  HubIntegration,
  HubIntegrationsQuery,
  InstalledIntegrationsResponse,
} from '../types/integrationsHub'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

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

const parseResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(body.detail || `Request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

const buildQueryString = (params: HubIntegrationsQuery = {}): string => {
  const query = new URLSearchParams()
  if (params.query) query.set('query', params.query)
  if (params.category) query.set('category', params.category)
  if (params.integration_type) query.set('integration_type', params.integration_type)
  if (params.sort_by) query.set('sort_by', params.sort_by)
  if (params.page) query.set('page', String(params.page))
  if (params.page_size) query.set('page_size', String(params.page_size))
  const built = query.toString()
  return built ? `?${built}` : ''
}

export const integrationsHubService = {
  async getInstalledIntegrations(): Promise<InstalledIntegrationsResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/integrations/mine/installed`, withAuth())
    return parseResponse<InstalledIntegrationsResponse>(response)
  },

  async getHubIntegrations(params: HubIntegrationsQuery = {}): Promise<HubIntegration[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/integrations/hub${buildQueryString(params)}`,
      withAuth(),
    )
    return parseResponse<HubIntegration[]>(response)
  },
}

export default integrationsHubService
