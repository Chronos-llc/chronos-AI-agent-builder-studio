import type { AgentHomeCardsResponse } from '../types/dashboard'

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

const handleResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(body.detail || `Request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

export const dashboardService = {
  async getAgentHomeCards(): Promise<AgentHomeCardsResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/agents/home/cards`, withAuth())
    return handleResponse<AgentHomeCardsResponse>(response)
  },
}

