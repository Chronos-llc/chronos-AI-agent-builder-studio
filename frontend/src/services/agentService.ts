/**
 * Agent Service
 * Handles agent-related API calls for the frontend
 */

import type { Agent } from '../types/marketplace'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = `${API_BASE_URL}/api`

// ============== Helper Functions ==============

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

// ============== Agent API ==============

export async function getAgents(
    skip: number = 0,
    limit: number = 100,
    status?: string,
    agent_type?: 'text' | 'voice'
): Promise<Agent[]> {
    const params: Record<string, unknown> = { skip, limit }
    if (status) params.status = status
    if (agent_type) params.agent_type = agent_type

    const queryString = buildQueryString(params)
    const response = await fetch(`${API_BASE}/agents${queryString}`)
    return handleResponse<Agent[]>(response)
}

export async function createAgent(agentData: Omit<Agent, 'id' | 'created_at' | 'updated_at'>): Promise<Agent> {
    const response = await fetch(`${API_BASE}/agents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(agentData)
    })
    return handleResponse<Agent>(response)
}

export async function updateAgent(agentId: number, agentData: Partial<Agent>): Promise<Agent> {
    const response = await fetch(`${API_BASE}/agents/${agentId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(agentData)
    })
    return handleResponse<Agent>(response)
}

export async function deleteAgent(agentId: number): Promise<void> {
    const response = await fetch(`${API_BASE}/agents/${agentId}`, {
        method: 'DELETE'
    })
    if (!response.ok) {
        throw new Error(`Failed to delete agent: ${response.status}`)
    }
}

export async function searchAgents(
    query: string,
    status?: string,
    tags?: string[],
    agent_type?: 'text' | 'voice',
    skip: number = 0,
    limit: number = 50
): Promise<Agent[]> {
    const params: Record<string, unknown> = { q: query, skip, limit }
    if (status) params.status = status
    if (tags) params.tags = tags
    if (agent_type) params.agent_type = agent_type

    const queryString = buildQueryString(params)
    const response = await fetch(`${API_BASE}/agents/search${queryString}`)
    return handleResponse<Agent[]>(response)
}
