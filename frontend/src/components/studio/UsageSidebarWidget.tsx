import { useEffect, useMemo, useState, type CSSProperties } from 'react'
import { ChevronDown, ChevronUp, Loader2 } from 'lucide-react'
import { usageMeteringService } from '../../services/usageMeteringService'
import type { UsageResourcesResponse } from '../../types/usageMetering'
import { cn } from '../../lib/utils'

const METRIC_ORDER = ['ai_spend', 'file_storage', 'vector_db_storage', 'table_rows', 'collaborators', 'agents']

const METRIC_LABELS: Record<string, string> = {
  ai_spend: 'AI Spend',
  file_storage: 'Files',
  vector_db_storage: 'Vector DB',
  table_rows: 'Rows',
  collaborators: 'Seats',
  agents: 'Agents',
}

const USAGE_WIDGET_EXPANDED_KEY = 'chronos_ui_usage_widget_expanded'

const formatCompact = (unit: string, value: number) => {
  if (unit === 'usd') return `$${value.toFixed(2)}`
  if (unit === 'bytes') {
    const gb = value / (1024 * 1024 * 1024)
    const mb = value / (1024 * 1024)
    if (gb >= 1) return `${gb.toFixed(1)} GB`
    return `${mb.toFixed(1)} MB`
  }
  return value.toLocaleString()
}

type UsageSidebarWidgetProps = {
  collapsed: boolean
}

const UsageSidebarWidget = ({ collapsed }: UsageSidebarWidgetProps) => {
  const [loading, setLoading] = useState(true)
  const [snapshot, setSnapshot] = useState<UsageResourcesResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [widgetExpanded, setWidgetExpanded] = useState(() => {
    if (typeof window === 'undefined') return true
    return window.localStorage.getItem(USAGE_WIDGET_EXPANDED_KEY) !== 'false'
  })

  const load = async () => {
    try {
      const usage = await usageMeteringService.getUserUsageResources()
      setSnapshot(usage)
      setError(null)
    } catch (err: any) {
      setError(err?.message || 'Failed to load usage')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
    const interval = window.setInterval(() => {
      void load()
    }, 10_000)
    return () => window.clearInterval(interval)
  }, [])

  useEffect(() => {
    if (typeof window === 'undefined') return
    window.localStorage.setItem(USAGE_WIDGET_EXPANDED_KEY, String(widgetExpanded))
  }, [widgetExpanded])

  const metrics = useMemo(() => {
    if (!snapshot) return []
    return METRIC_ORDER
      .map((resourceType) => snapshot.resources.find((item) => item.resource_type === resourceType))
      .filter((item): item is NonNullable<typeof item> => Boolean(item))
  }, [snapshot])

  if (collapsed) {
    const spend = metrics.find((item) => item.resource_type === 'ai_spend')
    return (
      <div className="mt-3 rounded-xl border border-border bg-background/60 p-3 text-center" title="Usage">
        {loading ? <Loader2 className="mx-auto h-4 w-4 animate-spin text-muted-foreground" /> : <span className="text-[11px] text-muted-foreground">Usage</span>}
        {spend && !loading && <p className="mt-1 text-[11px] font-semibold text-foreground">{formatCompact(spend.unit, spend.current)}</p>}
      </div>
    )
  }

  const spend = metrics.find((item) => item.resource_type === 'ai_spend')

  return (
    <div className="mt-4 rounded-2xl border border-border bg-background/70 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-foreground">Usage</h3>
        <div className="flex items-center gap-2">
          {loading && <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />}
          <button
            type="button"
            onClick={() => setWidgetExpanded((previous) => !previous)}
            className="rounded-md border border-border bg-background px-1.5 py-1 text-muted-foreground hover:bg-accent hover:text-foreground"
            aria-expanded={widgetExpanded}
            aria-label={widgetExpanded ? 'Collapse usage meters' : 'Expand usage meters'}
          >
            {widgetExpanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
          </button>
        </div>
      </div>

      {error ? (
        <p className="text-xs text-rose-400">{error}</p>
      ) : !widgetExpanded ? (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">AI Spend</span>
            <span className="text-foreground">
              {spend ? `${formatCompact(spend.unit, spend.current)}${spend.total_limit !== null ? ` / ${formatCompact(spend.unit, spend.total_limit)}` : ''}` : '$0.00'}
            </span>
          </div>
          <div className="h-1.5 rounded-full bg-muted">
            <div
              className={cn(
                'usage-progress-bar h-1.5 rounded-full',
                spend && spend.percent_used >= 90 ? 'bg-rose-500' : spend && spend.percent_used >= 75 ? 'bg-amber-500' : 'bg-primary',
              )}
              style={{ '--usage-width': `${Math.min(100, spend?.percent_used ?? 0)}%` } as CSSProperties}
            />
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {metrics.map((metric) => (
            <div key={metric.resource_type}>
              <div className="mb-1 flex items-center justify-between text-xs">
                <span className="text-muted-foreground">{METRIC_LABELS[metric.resource_type]}</span>
                <span className="text-foreground">
                  {formatCompact(metric.unit, metric.current)}
                  {metric.total_limit !== null ? ` / ${formatCompact(metric.unit, metric.total_limit)}` : ''}
                </span>
              </div>
              <div className="h-1.5 rounded-full bg-muted">
                <div
                  className={cn(
                    'usage-progress-bar h-1.5 rounded-full',
                    metric.percent_used >= 90 ? 'bg-rose-500' : metric.percent_used >= 75 ? 'bg-amber-500' : 'bg-primary',
                  )}
                  style={{ '--usage-width': `${Math.min(100, metric.percent_used)}%` } as CSSProperties}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default UsageSidebarWidget
