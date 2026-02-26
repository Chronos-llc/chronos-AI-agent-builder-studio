import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { X, Search, Filter, Plus, Loader2 } from 'lucide-react'
import { ProviderLogo } from '../brand/ProviderLogo'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Badge } from '../ui/badge'
import { integrationsHubService } from '../../services/integrationsHubService'
import type { HubIntegration } from '../../types/integrationsHub'

type Props = {
  onClose: () => void
}

const CATEGORY_OPTIONS = [
  { label: 'All categories', value: 'all' },
  { label: 'Automation', value: 'automation' },
  { label: 'AI', value: 'ai' },
  { label: 'Communication', value: 'communication' },
  { label: 'Communications', value: 'communications' },
  { label: 'Utilities', value: 'utilities' },
  { label: 'Productivity', value: 'productivity' },
  { label: 'Development', value: 'development' },
  { label: 'Search', value: 'search' },
  { label: 'Geospatial', value: 'geospatial' },
]

const TYPE_OPTIONS = [
  { label: 'All types', value: 'all' },
  { label: 'MCP Server', value: 'mcp_server' },
  { label: 'API', value: 'api' },
  { label: 'AI Model', value: 'ai_model' },
  { label: 'Communication', value: 'communication' },
]

export const ChronosHubModal = ({ onClose }: Props) => {
  const navigate = useNavigate()
  const [items, setItems] = useState<HubIntegration[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('all')
  const [integrationType, setIntegrationType] = useState('all')

  useEffect(() => {
    const timer = window.setTimeout(() => {
      const load = async () => {
        setLoading(true)
        setError(null)
        try {
          const response = await integrationsHubService.getHubIntegrations({
            query: query || undefined,
            category: category !== 'all' ? category : undefined,
            integration_type: integrationType !== 'all' ? integrationType : undefined,
            sort_by: 'popularity',
            page_size: 60,
          })
          setItems(response)
        } catch (err: any) {
          setError(err?.message || 'Failed to load Chronos Hub')
        } finally {
          setLoading(false)
        }
      }
      void load()
    }, 250)

    return () => window.clearTimeout(timer)
  }, [query, category, integrationType])

  const emptyState = useMemo(
    () => (
      <div className="rounded-xl border border-dashed border-border bg-background/60 p-8 text-center">
        <p className="text-base font-medium text-foreground">No integrations matched your filters.</p>
        <p className="mt-1 text-sm text-muted-foreground">Adjust search or clear filters to see more results.</p>
      </div>
    ),
    [],
  )

  return (
    <div className="relative mx-auto flex h-[calc(100vh-8rem)] w-full max-w-7xl flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-2xl">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div>
          <h2 className="text-xl font-semibold text-foreground">Chronos Hub</h2>
          <p className="text-sm text-muted-foreground">Explore and install integrations from the curated marketplace.</p>
        </div>
        <Button variant="outline" onClick={onClose} className="gap-2">
          <X className="h-4 w-4" />
          Close
        </Button>
      </div>

      <div className="border-b border-border px-4 py-3">
        <div className="grid gap-3 md:grid-cols-[2fr,1fr,1fr]">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search integrations..."
              className="pl-9"
            />
          </div>
          <label className="flex items-center gap-2 rounded-md border border-input bg-background px-3">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <select
              value={category}
              onChange={(event) => setCategory(event.target.value)}
              className="h-10 w-full bg-transparent text-sm text-foreground outline-none"
            >
              {CATEGORY_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label className="flex items-center gap-2 rounded-md border border-input bg-background px-3">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <select
              value={integrationType}
              onChange={(event) => setIntegrationType(event.target.value)}
              className="h-10 w-full bg-transparent text-sm text-foreground outline-none"
            >
              {TYPE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {loading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading Chronos Hub integrations...
          </div>
        )}

        {!loading && error && (
          <div className="rounded-lg border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-300">{error}</div>
        )}

        {!loading && !error && items.length === 0 && emptyState}

        {!loading && !error && items.length > 0 && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {items.map((integration) => (
              <article
                key={integration.id}
                className="flex h-full flex-col justify-between rounded-xl border border-border bg-background/60 p-4"
              >
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <ProviderLogo
                      name={integration.name}
                      url={integration.app_icon_url || integration.icon || undefined}
                      size={30}
                      className="border-0 bg-transparent"
                    />
                    <div className="min-w-0 flex-1">
                      <h3 className="truncate text-base font-semibold text-foreground">{integration.name}</h3>
                      <p className="text-xs text-muted-foreground">
                        {integration.integration_type.replace(/_/g, ' ')} | {integration.category.replace(/_/g, ' ')}
                      </p>
                    </div>
                  </div>
                  <p className="line-clamp-3 text-sm text-muted-foreground">
                    {integration.description || 'No description provided.'}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="outline">v{integration.version}</Badge>
                    <Badge variant="outline">{integration.download_count} downloads</Badge>
                    <Badge variant="outline">{integration.review_count} reviews</Badge>
                  </div>
                </div>
                <div className="mt-4 grid grid-cols-2 gap-2">
                  <Button
                    variant="outline"
                    onClick={() => navigate(`/app/integrations/${integration.id}`)}
                  >
                    Open
                  </Button>
                  <Button onClick={() => navigate(`/app/integrations/${integration.id}/install`)}>
                    Install
                  </Button>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>

      <div className="border-t border-border bg-primary/10 px-4 py-3">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-foreground">
            Don’t find what you’re looking for? Create an integration and submit for review to the Chronos team.
            Approval time: 5 working days or less.
          </p>
          <Button
            variant="outline"
            className="gap-2 self-start sm:self-auto"
            onClick={() => navigate('/app/integrations/create')}
          >
            <Plus className="h-4 w-4" />
            Create integration
          </Button>
        </div>
      </div>
    </div>
  )
}

export default ChronosHubModal
