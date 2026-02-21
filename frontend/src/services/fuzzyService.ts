/**
 * FUZZY Meta-Agent API Service
 * Handles all FUZZY-related API calls for admin management
 */

import type {
    FuzzyConfiguration,
    FuzzyConfigurationUpdate,
    FuzzyConfigurationExport,
    FuzzyConfigurationImport,
    FuzzyTool,
    FuzzyToolConfig,
    FuzzySession,
    FuzzySessionCreate,
    FuzzyAction,
    FuzzyActionList,
    FuzzyUsageStatistics,
    FuzzyPerformanceMetrics,
    FuzzyHealthStatus,
    FuzzyTestRequest,
    FuzzyTestResponse,
    FuzzyRateLimitStatus,
    FuzzyDashboardData,
    FuzzyActivityLog,
    FuzzyApiResponse,
    FuzzyToolResponse
} from '../types/fuzzy'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = `${API_BASE_URL}/api/fuzzy-tools`

// ============== Helper Functions ==============
const getAccessToken = () => {
    if (typeof globalThis === 'undefined' || !('localStorage' in globalThis)) {
        return null
    }
    return globalThis.localStorage.getItem('chronos_access_token') || globalThis.localStorage.getItem('access_token')
}

function withAuth(init: RequestInit = {}): RequestInit {
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

const authFetch = (input: RequestInfo | URL, init: RequestInit = {}) => fetch(input, withAuth(init))

async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || `HTTP error ${response.status}`)
    }
    return response.json()
}

function buildQueryString(params: Record<string, unknown>): string {
    const query = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
            if (Array.isArray(value)) {
                value.forEach(item => query.append(key, String(item)))
            } else {
                query.append(key, String(value))
            }
        }
    })
    return query.toString() ? `?${query.toString()}` : ''
}

// ============== Configuration API ==============

export async function getFuzzyConfiguration(): Promise<FuzzyConfiguration> {
    const response = await authFetch(`${API_BASE}/configuration`)
    return handleResponse<FuzzyConfiguration>(response)
}

export async function updateFuzzyConfiguration(
    config: FuzzyConfigurationUpdate
): Promise<FuzzyConfiguration> {
    const response = await authFetch(`${API_BASE}/configuration`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
    })
    return handleResponse<FuzzyConfiguration>(response)
}

export async function exportFuzzyConfiguration(): Promise<FuzzyConfigurationExport> {
    const response = await authFetch(`${API_BASE}/configuration/export`)
    return handleResponse<FuzzyConfigurationExport>(response)
}

export async function importFuzzyConfiguration(
    importData: FuzzyConfigurationImport
): Promise<FuzzyConfiguration> {
    const response = await authFetch(`${API_BASE}/configuration/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(importData)
    })
    return handleResponse<FuzzyConfiguration>(response)
}

// ============== Tool Management API ==============

export async function getFuzzyTools(): Promise<FuzzyTool[]> {
    const response = await authFetch(`${API_BASE}/tools`)
    return handleResponse<FuzzyTool[]>(response)
}

export async function getFuzzyTool(toolId: string): Promise<FuzzyTool> {
    const response = await authFetch(`${API_BASE}/tools/${toolId}`)
    return handleResponse<FuzzyTool>(response)
}

export async function updateFuzzyToolConfig(
    toolId: string,
    config: FuzzyToolConfig
): Promise<FuzzyTool> {
    const response = await authFetch(`${API_BASE}/tools/${toolId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
    })
    return handleResponse<FuzzyTool>(response)
}

export async function enableFuzzyTool(toolId: string): Promise<FuzzyTool> {
    const response = await authFetch(`${API_BASE}/tools/${toolId}/enable`, {
        method: 'POST'
    })
    return handleResponse<FuzzyTool>(response)
}

export async function disableFuzzyTool(toolId: string): Promise<FuzzyTool> {
    const response = await authFetch(`${API_BASE}/tools/${toolId}/disable`, {
        method: 'POST'
    })
    return handleResponse<FuzzyTool>(response)
}

export async function testFuzzyTool(
    toolId: string,
    parameters: Record<string, any>
): Promise<FuzzyToolResponse> {
    const response = await authFetch(`${API_BASE}/tools/${toolId}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ parameters })
    })
    return handleResponse<FuzzyToolResponse>(response)
}

// ============== Session Management API ==============

export async function createFuzzySession(
    data: FuzzySessionCreate
): Promise<FuzzySession> {
    const response = await authFetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    return handleResponse<FuzzySession>(response)
}

export async function getFuzzySessions(
    limit: number = 50,
    offset: number = 0
): Promise<{ sessions: FuzzySession[]; total: number }> {
    const params = buildQueryString({ limit, offset })
    const response = await authFetch(`${API_BASE}/sessions${params}`)
    return handleResponse<{ sessions: FuzzySession[]; total: number }>(response)
}

export async function getFuzzySession(sessionId: number): Promise<FuzzySession> {
    const response = await authFetch(`${API_BASE}/sessions/${sessionId}`)
    return handleResponse<FuzzySession>(response)
}

export async function endFuzzySession(sessionId: number): Promise<FuzzySession> {
    const response = await authFetch(`${API_BASE}/sessions/${sessionId}/end`, {
        method: 'POST'
    })
    return handleResponse<FuzzySession>(response)
}

// ============== Action Audit API ==============

export async function getFuzzyActions(
    sessionId?: number,
    actionType?: string,
    status?: string,
    limit: number = 50,
    offset: number = 0
): Promise<FuzzyActionList> {
    const params: Record<string, unknown> = { limit, offset }
    if (sessionId) params.session_id = sessionId
    if (actionType) params.action_type = actionType
    if (status) params.status = status

    const queryString = buildQueryString(params)
    const response = await authFetch(`${API_BASE}/actions${queryString}`)
    return handleResponse<FuzzyActionList>(response)
}

export async function getFuzzyAction(actionId: number): Promise<FuzzyAction> {
    const response = await authFetch(`${API_BASE}/actions/${actionId}`)
    return handleResponse<FuzzyAction>(response)
}

export async function rollbackFuzzyAction(
    actionId: number
): Promise<FuzzyApiResponse> {
    const response = await authFetch(`${API_BASE}/actions/${actionId}/rollback`, {
        method: 'POST'
    })
    return handleResponse<FuzzyApiResponse>(response)
}

// ============== Monitoring API ==============

export async function getFuzzyStatistics(): Promise<FuzzyUsageStatistics> {
    const response = await authFetch(`${API_BASE}/monitoring/statistics`)
    return handleResponse<FuzzyUsageStatistics>(response)
}

export async function getFuzzyPerformance(): Promise<FuzzyPerformanceMetrics> {
    const response = await authFetch(`${API_BASE}/monitoring/performance`)
    return handleResponse<FuzzyPerformanceMetrics>(response)
}

export async function getFuzzyHealth(): Promise<FuzzyHealthStatus> {
    const response = await authFetch(`${API_BASE}/monitoring/health`)
    return handleResponse<FuzzyHealthStatus>(response)
}

export async function getFuzzyDashboard(): Promise<FuzzyDashboardData> {
    const response = await authFetch(`${API_BASE}/monitoring/dashboard`)
    return handleResponse<FuzzyDashboardData>(response)
}

export async function getFuzzyActivityLogs(
    level?: string,
    limit: number = 100,
    offset: number = 0
): Promise<{ logs: FuzzyActivityLog[]; total: number }> {
    const params: Record<string, unknown> = { limit, offset }
    if (level) params.level = level

    const queryString = buildQueryString(params)
    const response = await authFetch(`${API_BASE}/monitoring/logs${queryString}`)
    return handleResponse<{ logs: FuzzyActivityLog[]; total: number }>(response)
}

// ============== Testing API ==============

export async function testFuzzyResponse(
    request: FuzzyTestRequest
): Promise<FuzzyTestResponse> {
    const response = await authFetch(`${API_BASE}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
    })
    return handleResponse<FuzzyTestResponse>(response)
}

export async function simulateFuzzyInteraction(
    scenario: string,
    context?: Record<string, any>
): Promise<FuzzyTestResponse> {
    const response = await authFetch(`${API_BASE}/test/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario, context })
    })
    return handleResponse<FuzzyTestResponse>(response)
}

// ============== Rate Limit API ==============

export async function getFuzzyRateLimitStatus(
    userId?: number
): Promise<FuzzyRateLimitStatus> {
    const params = userId ? buildQueryString({ user_id: userId }) : ''
    const response = await authFetch(`${API_BASE}/rate-limit${params}`)
    return handleResponse<FuzzyRateLimitStatus>(response)
}

export async function resetFuzzyRateLimit(userId: number): Promise<FuzzyApiResponse> {
    const response = await authFetch(`${API_BASE}/rate-limit/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
    })
    return handleResponse<FuzzyApiResponse>(response)
}

// ============== Utility Functions ==============

export async function downloadConfigurationFile(
    config: FuzzyConfigurationExport
): Promise<void> {
    const blob = new Blob([JSON.stringify(config, null, 2)], {
        type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `fuzzy-config-${new Date().toISOString()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
}

export async function uploadConfigurationFile(
    file: File
): Promise<FuzzyConfigurationImport> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => {
            try {
                const config = JSON.parse(e.target?.result as string)
                resolve(config)
            } catch (error) {
                reject(new Error('Invalid configuration file'))
            }
        }
        reader.onerror = () => reject(new Error('Failed to read file'))
        reader.readAsText(file)
    })
}
