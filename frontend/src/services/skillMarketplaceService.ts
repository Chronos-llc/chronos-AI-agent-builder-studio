import type {
  SkillCompareResponse,
  SkillFileContentResponse,
  SkillInstallRequest,
  SkillInstallResponse,
  SkillMarketplaceDetailResponse,
  SkillMarketplaceListResponse,
  SkillScanResponse,
  SkillSubmissionDetailResponse,
  SkillSubmissionListResponse,
  SkillUploadResponse,
  SkillVersionListResponse,
} from '../types/skillMarketplace'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const API_BASE = `${API_BASE_URL}/api/skills`

const getAccessToken = () => {
  if (typeof globalThis === 'undefined' || !('localStorage' in globalThis)) {
    return null
  }
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

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorPayload = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(errorPayload.detail || `HTTP ${response.status}`)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}

function buildQuery(params: Record<string, string | number | boolean | undefined | null>): string {
  const qs = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      qs.set(key, String(value))
    }
  }
  return qs.toString() ? `?${qs.toString()}` : ''
}

export const skillMarketplaceService = {
  async listMarketplace(params?: {
    page?: number
    page_size?: number
    search_query?: string
    category?: string
    sort_by?: string
    sort_order?: string
  }) {
    const query = buildQuery({
      page: params?.page ?? 1,
      page_size: params?.page_size ?? 20,
      search_query: params?.search_query,
      category: params?.category,
      sort_by: params?.sort_by ?? 'created_at',
      sort_order: params?.sort_order ?? 'desc',
    })
    const response = await fetch(`${API_BASE}/marketplace${query}`, withAuth())
    return handleResponse<SkillMarketplaceListResponse>(response)
  },

  async getSkill(skillId: number) {
    const response = await fetch(`${API_BASE}/marketplace/${skillId}`, withAuth())
    return handleResponse<SkillMarketplaceDetailResponse>(response)
  },

  async listVersions(skillId: number) {
    const response = await fetch(`${API_BASE}/marketplace/${skillId}/versions`, withAuth())
    return handleResponse<SkillVersionListResponse>(response)
  },

  async getVersionFile(skillId: number, versionId: number) {
    const response = await fetch(`${API_BASE}/marketplace/${skillId}/versions/${versionId}/file`, withAuth())
    return handleResponse<SkillFileContentResponse>(response)
  },

  async compareVersions(skillId: number, baseVersionId: number, headVersionId: number) {
    const query = buildQuery({
      base_version_id: baseVersionId,
      head_version_id: headVersionId,
    })
    const response = await fetch(`${API_BASE}/marketplace/${skillId}/compare${query}`, withAuth())
    return handleResponse<SkillCompareResponse>(response)
  },

  async uploadSkill(formData: FormData) {
    const response = await fetch(
      `${API_BASE}/marketplace/upload`,
      withAuth({
        method: 'POST',
        body: formData,
      }),
    )
    return handleResponse<SkillUploadResponse>(response)
  },

  async installSkill(skillId: number, payload: SkillInstallRequest) {
    const response = await fetch(
      `${API_BASE}/marketplace/${skillId}/install`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }),
    )
    return handleResponse<SkillInstallResponse>(response)
  },

  async downloadSkill(skillId: number, versionId?: number) {
    const query = buildQuery({ version_id: versionId })
    const response = await fetch(
      `${API_BASE}/marketplace/${skillId}/download${query}`,
      withAuth(),
    )
    if (!response.ok) {
      const payload = await response.json().catch(() => ({ detail: 'Download failed' }))
      throw new Error(payload.detail || 'Download failed')
    }
    const blob = await response.blob()
    const disposition = response.headers.get('content-disposition') || ''
    const match = disposition.match(/filename=\"?([^\";]+)\"?/)
    return {
      blob,
      filename: match?.[1] || 'skill.zip',
    }
  },

  async listSubmissions(statusFilter?: string) {
    const query = buildQuery({ status: statusFilter })
    const response = await fetch(`${API_BASE}/admin/submissions${query}`, withAuth())
    return handleResponse<SkillSubmissionListResponse>(response)
  },

  async getSubmission(skillId: number) {
    const response = await fetch(`${API_BASE}/admin/submissions/${skillId}`, withAuth())
    return handleResponse<SkillSubmissionDetailResponse>(response)
  },

  async scanSubmission(skillId: number, versionId?: number) {
    const query = buildQuery({ version_id: versionId })
    const response = await fetch(
      `${API_BASE}/admin/submissions/${skillId}/scan${query}`,
      withAuth({ method: 'POST' }),
    )
    return handleResponse<SkillScanResponse>(response)
  },

  async reviewSubmission(skillId: number, action: 'approve' | 'reject' | 'quarantine', notes?: string) {
    const response = await fetch(
      `${API_BASE}/admin/submissions/${skillId}/review`,
      withAuth({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, notes }),
      }),
    )
    return handleResponse<SkillSubmissionDetailResponse>(response)
  },

  async publishSubmission(skillId: number) {
    const response = await fetch(
      `${API_BASE}/admin/submissions/${skillId}/publish`,
      withAuth({ method: 'POST' }),
    )
    return handleResponse<SkillSubmissionDetailResponse>(response)
  },
}
