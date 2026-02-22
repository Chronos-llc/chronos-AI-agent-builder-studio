import { useEffect, useMemo, useState, type CSSProperties } from 'react'
import { Loader2, RefreshCw } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card } from '../components/ui/card'
import type { AgentUsageResourcesResponse, UsageResourceSnapshot, UsageResourcesResponse } from '../types/usageMetering'
import { usageMeteringService } from '../services/usageMeteringService'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

type AgentOption = {
  id: number
  name: string
}

const RESOURCE_LABELS: Record<string, string> = {
  ai_spend: 'AI Spend',
  file_storage: 'File Storage',
  vector_db_storage: 'Vector DB Storage',
  table_rows: 'Table Rows',
  collaborators: 'Collaborators',
  agents: 'Agents',
}

const formatResourceValue = (resource: UsageResourceSnapshot, value: number | null | undefined) => {
  if (value === null || value === undefined) return 'Unlimited'

  if (resource.unit === 'bytes') {
    if (value >= 1024 * 1024 * 1024) return `${(value / (1024 * 1024 * 1024)).toFixed(2)} GB`
    if (value >= 1024 * 1024) return `${(value / (1024 * 1024)).toFixed(2)} MB`
    if (value >= 1024) return `${(value / 1024).toFixed(2)} KB`
    return `${Math.round(value)} B`
  }
  if (resource.unit === 'usd') {
    return `$${value.toFixed(2)}`
  }
  return value.toLocaleString()
}

const getAccessToken = () => {
  if (typeof globalThis === 'undefined' || !('localStorage' in globalThis)) return null
  return globalThis.localStorage.getItem('chronos_access_token') || globalThis.localStorage.getItem('access_token')
}

const UsagePage = () => {
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [snapshot, setSnapshot] = useState<UsageResourcesResponse | null>(null)
  const [agentSnapshot, setAgentSnapshot] = useState<AgentUsageResourcesResponse | null>(null)
  const [agents, setAgents] = useState<AgentOption[]>([])
  const [selectedAgentId, setSelectedAgentId] = useState<number | null>(null)

  const loadAgents = async () => {
    const token = getAccessToken()
    const response = await fetch(`${API_BASE_URL}/api/v1/agents?limit=100`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      credentials: 'include',
    })
    if (!response.ok) {
      return
    }
    const payload = await response.json()
    setAgents(
      (payload || []).map((item: any) => ({ id: item.id, name: item.name })),
    )
  }

  const loadUsage = async (silent = false) => {
    if (silent) setRefreshing(true)
    else setLoading(true)
    setError(null)
    try {
      const [userUsage] = await Promise.all([usageMeteringService.getUserUsageResources(), loadAgents()])
      setSnapshot(userUsage)
      if (selectedAgentId) {
        const agentUsage = await usageMeteringService.getAgentUsageResources(selectedAgentId)
        setAgentSnapshot(agentUsage)
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load usage metrics')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    void loadUsage()
    const interval = window.setInterval(() => {
      void loadUsage(true)
    }, 10_000)
    return () => window.clearInterval(interval)
  }, [])

  useEffect(() => {
    if (!selectedAgentId) {
      setAgentSnapshot(null)
      return
    }
    void usageMeteringService
      .getAgentUsageResources(selectedAgentId)
      .then(setAgentSnapshot)
      .catch(() => {
        setAgentSnapshot(null)
      })
  }, [selectedAgentId])

  const rows = useMemo(() => snapshot?.resources || [], [snapshot])

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Usage</h1>
          <p className="text-sm text-muted-foreground">
            Live usage metrics across spend, storage, rows, seats, and agents.
          </p>
        </div>
        <Button variant="outline" onClick={() => void loadUsage(true)} disabled={refreshing}>
          {refreshing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
          Refresh
        </Button>
      </div>

      {loading ? (
        <Card className="p-6">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading usage metrics...
          </div>
        </Card>
      ) : error ? (
        <Card className="border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-300">{error}</Card>
      ) : (
        <>
          <Card className="overflow-hidden border border-border bg-card">
            <div className="border-b border-border px-5 py-4">
              <p className="text-sm text-muted-foreground">
                Plan: <span className="font-medium text-foreground">{snapshot?.plan || 'payg'}</span>
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-background/60 text-left text-muted-foreground">
                    <th className="px-5 py-3 font-medium">Resource</th>
                    <th className="px-5 py-3 font-medium">Current</th>
                    <th className="px-5 py-3 font-medium">Base</th>
                    <th className="px-5 py-3 font-medium">Add-on</th>
                    <th className="px-5 py-3 font-medium">Total</th>
                    <th className="px-5 py-3 font-medium">Usage</th>
                    <th className="px-5 py-3 font-medium">Overage Est.</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((resource) => (
                    <tr key={resource.resource_type} className="border-b border-border/60">
                      <td className="px-5 py-3 font-medium text-foreground">
                        {RESOURCE_LABELS[resource.resource_type] || resource.resource_type}
                      </td>
                      <td className="px-5 py-3 text-foreground">{formatResourceValue(resource, resource.current)}</td>
                      <td className="px-5 py-3 text-muted-foreground">{formatResourceValue(resource, resource.base_limit)}</td>
                      <td className="px-5 py-3 text-muted-foreground">{formatResourceValue(resource, resource.addon_limit)}</td>
                      <td className="px-5 py-3 text-muted-foreground">{formatResourceValue(resource, resource.total_limit)}</td>
                      <td className="px-5 py-3">
                        <div className="flex min-w-[160px] items-center gap-2">
                          <div className="h-2 flex-1 rounded-full bg-muted">
                            <div
                              className="usage-progress-bar h-2 rounded-full bg-primary"
                              style={{ '--usage-width': `${Math.min(100, resource.percent_used)}%` } as CSSProperties}
                            />
                          </div>
                          <span className="w-14 text-right text-xs text-muted-foreground">
                            {Number.isFinite(resource.percent_used) ? `${resource.percent_used.toFixed(1)}%` : '0%'}
                          </span>
                        </div>
                      </td>
                      <td className="px-5 py-3 text-muted-foreground">
                        {resource.estimated_overage_monthly_usd > 0
                          ? `$${resource.estimated_overage_monthly_usd.toFixed(2)}/mo`
                          : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          <Card className="border border-border bg-card p-5">
            <div className="flex flex-wrap items-center gap-3">
              <label className="text-sm font-medium text-foreground" htmlFor="usage-agent">
                Agent Drilldown
              </label>
              <select
                id="usage-agent"
                className="h-10 min-w-[220px] rounded-md border border-input bg-background px-3 text-sm text-foreground"
                value={selectedAgentId ?? ''}
                onChange={(event) => setSelectedAgentId(event.target.value ? Number(event.target.value) : null)}
              >
                <option value="">Select an agent</option>
                {agents.map((agent) => (
                  <option key={agent.id} value={agent.id}>
                    {agent.name}
                  </option>
                ))}
              </select>
            </div>

            {selectedAgentId && agentSnapshot && (
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                {agentSnapshot.resources.map((resource) => (
                  <div key={resource.resource_type} className="rounded-lg border border-border bg-background/70 p-4">
                    <p className="text-sm font-semibold text-foreground">
                      {RESOURCE_LABELS[resource.resource_type] || resource.resource_type}
                    </p>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {formatResourceValue(resource, resource.current)} used
                    </p>
                    <p className="text-xs text-muted-foreground">
                      of {formatResourceValue(resource, resource.total_limit)} total
                    </p>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  )
}

export default UsagePage
