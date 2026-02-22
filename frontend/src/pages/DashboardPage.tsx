import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { AlertTriangle, Bot, MessageSquare, Search } from 'lucide-react'
import { ProviderLogo } from '../components/brand/ProviderLogo'
import { getProviderIcon } from '../config/iconRegistry'
import { dashboardService } from '../services/dashboardService'
import { useAuth } from '../contexts/AuthContext'
import type { AgentHomeCard, AgentHomeCardsResponse } from '../types/dashboard'

const formatPlanLabel = (plan: string) =>
  plan
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())

const statusBadgeClasses: Record<string, string> = {
  active: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  draft: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  inactive: 'bg-slate-500/15 text-slate-300 border-slate-500/30',
  archived: 'bg-zinc-500/15 text-zinc-300 border-zinc-500/30',
}

const formatRelativeDate = (dateString: string | null) => {
  if (!dateString) return 'No activity yet'
  const date = new Date(dateString)
  if (Number.isNaN(date.getTime())) return 'No activity yet'
  return `Last activity ${date.toLocaleString()}`
}

const DashboardPage = () => {
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [snapshot, setSnapshot] = useState<AgentHomeCardsResponse | null>(null)

  const loadHomeCards = async (silent = false) => {
    if (!silent) setLoading(true)
    try {
      const response = await dashboardService.getAgentHomeCards()
      setSnapshot(response)
      setError(null)
    } catch (loadError: any) {
      setError(loadError?.message || 'Failed to load workspace cards')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadHomeCards()
    const interval = window.setInterval(() => {
      void loadHomeCards(true)
    }, 10_000)
    return () => window.clearInterval(interval)
  }, [])

  const filteredAgents = useMemo(() => {
    const cards = snapshot?.agents || []
    const query = search.trim().toLowerCase()
    if (!query) return cards
    return cards.filter((agent) => {
      const channelText = agent.deployed_channels.join(' ')
      return (
        agent.name.toLowerCase().includes(query) ||
        agent.status.toLowerCase().includes(query) ||
        channelText.toLowerCase().includes(query)
      )
    })
  }, [search, snapshot])

  const workspaceName = snapshot?.workspace_name || `${user?.full_name || user?.username || 'My'}'s Workspace`
  const planLabel = formatPlanLabel(snapshot?.plan || 'pay as you go')

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Home</p>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-3xl font-bold text-foreground">{workspaceName}</h1>
          <span className="rounded-full border border-border bg-card px-3 py-1 text-xs font-semibold text-muted-foreground">
            {planLabel}
          </span>
        </div>
      </div>

      <div className="chronos-surface rounded-xl p-4">
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search agents or channels..."
            className="w-full rounded-lg border border-input bg-background px-10 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none"
          />
        </div>
      </div>

      {loading ? (
        <div className="chronos-surface rounded-xl p-6">
          <p className="text-sm text-muted-foreground">Loading workspace agents...</p>
        </div>
      ) : error ? (
        <div className="chronos-surface rounded-xl border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-300">
          {error}
        </div>
      ) : filteredAgents.length === 0 ? (
        <div className="chronos-surface rounded-xl p-8 text-center">
          <Bot className="mx-auto h-8 w-8 text-muted-foreground" />
          <h2 className="mt-3 text-lg font-semibold text-foreground">
            {snapshot?.agents?.length ? 'No matching agents' : 'No agents created yet'}
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {snapshot?.agents?.length
              ? 'Try a different search query.'
              : 'Create your first agent to see live usage and deployment metrics here.'}
          </p>
          {!snapshot?.agents?.length && (
            <Link
              to="/app/agents/new"
              className="mt-4 inline-flex rounded-full bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90"
            >
              Create Agent
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
          {filteredAgents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      )}
    </div>
  )
}

type AgentCardProps = {
  agent: AgentHomeCard
}

const AgentCard = ({ agent }: AgentCardProps) => {
  const normalizedStatus = agent.status.toLowerCase()
  const statusClass = statusBadgeClasses[normalizedStatus] || 'bg-muted text-muted-foreground border-border'

  return (
    <div className="chronos-surface rounded-xl border border-border p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-xl font-semibold text-foreground">{agent.name}</h3>
          <p className="mt-1 text-xs text-muted-foreground">{formatRelativeDate(agent.last_message_at)}</p>
        </div>
        <span className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${statusClass}`}>
          {normalizedStatus.charAt(0).toUpperCase() + normalizedStatus.slice(1)}
        </span>
      </div>

      <div className="mt-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Deployed on</p>
        {agent.deployed_channels.length ? (
          <div className="mt-2 flex flex-wrap items-center gap-2">
            {agent.deployed_channels.map((channel) => {
              const icon = getProviderIcon(channel)
              const label = channel.charAt(0).toUpperCase() + channel.slice(1)
              return (
                <div
                  key={`${agent.id}-${channel}`}
                  className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-2 py-1"
                  title={label}
                >
                  {icon?.url ? (
                    <ProviderLogo name={label} url={icon.url} size={18} className="border-white/20" />
                  ) : (
                    <span className="flex h-[18px] w-[18px] items-center justify-center rounded-full bg-muted text-[10px] text-muted-foreground">
                      {channel.slice(0, 1).toUpperCase()}
                    </span>
                  )}
                  <span className="text-xs text-foreground">{label}</span>
                </div>
              )
            })}
          </div>
        ) : (
          <p className="mt-2 text-sm text-muted-foreground">Not deployed yet</p>
        )}
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3">
        <div className="rounded-lg border border-border bg-background p-3">
          <div className="flex items-center gap-2 text-muted-foreground">
            <MessageSquare className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wide">Messages</span>
          </div>
          <p className="mt-2 text-2xl font-semibold text-foreground">{agent.messages_received.toLocaleString()}</p>
        </div>
        <div className="rounded-lg border border-border bg-background p-3">
          <div className="flex items-center gap-2 text-muted-foreground">
            <AlertTriangle className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wide">Errors</span>
          </div>
          <p className="mt-2 text-2xl font-semibold text-foreground">{agent.errors_encountered.toLocaleString()}</p>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        <Link
          to={`/app/agents/${agent.id}/edit`}
          className="inline-flex flex-1 items-center justify-center rounded-lg border border-border bg-background px-3 py-2 text-sm font-semibold text-foreground hover:bg-accent"
        >
          Edit in Studio
        </Link>
        <Link
          to={`/app/agents/${agent.id}/edit?tab=fuzzy`}
          className="inline-flex flex-1 items-center justify-center rounded-lg border border-border bg-background px-3 py-2 text-sm font-semibold text-foreground hover:bg-accent"
        >
          Edit with Fuzzy
        </Link>
        <Link
          to={`/app/agents/${agent.id}/suite`}
          className="inline-flex flex-1 items-center justify-center rounded-lg bg-primary px-3 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90"
        >
          Open Agent
        </Link>
      </div>
    </div>
  )
}

export default DashboardPage

