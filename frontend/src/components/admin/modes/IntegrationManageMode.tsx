import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '../../ui/badge'
import { Button } from '../../ui/button'
import { Card } from '../../ui/card'
import { Input } from '../../ui/input'
import { ProviderLogo } from '../../brand/ProviderLogo'
import { Download, Gauge, Loader2, Search } from 'lucide-react'
import { adminIntegrationService, type AdminIntegrationHubItem } from '../../../services/adminIntegrationService'

const statusBadgeClass: Record<string, string> = {
  draft: 'border-slate-500/45 bg-slate-500/10 text-slate-700 dark:text-slate-200',
  submitted: 'border-cyan-500/45 bg-cyan-500/10 text-cyan-700 dark:text-cyan-200',
  under_review: 'border-amber-500/45 bg-amber-500/10 text-amber-700 dark:text-amber-200',
  approved: 'border-emerald-500/45 bg-emerald-500/10 text-emerald-700 dark:text-emerald-200',
  rejected: 'border-rose-500/45 bg-rose-500/10 text-rose-700 dark:text-rose-200',
  published: 'border-violet-500/45 bg-violet-500/10 text-violet-700 dark:text-violet-200',
}

export const IntegrationManageMode = () => {
  const navigate = useNavigate()
  const [items, setItems] = useState<AdminIntegrationHubItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await adminIntegrationService.listHub({
        query: query || undefined,
        status: statusFilter || undefined,
        page: 1,
        page_size: 50,
      })
      setItems(response.items)
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to load hub integrations')
    } finally {
      setLoading(false)
    }
  }, [query, statusFilter])

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void load()
    }, 250)
    return () => window.clearTimeout(timer)
  }, [load])

  return (
    <div className="space-y-4" data-testid="admin-integrations-manage-mode">
      <div className="space-y-1">
        <h2 className="text-2xl font-bold">Manage Integrations</h2>
        <p className="text-sm text-muted-foreground">
          Manage all integrations currently on the user integrations hub.
        </p>
      </div>

      <Card className="border border-border bg-card p-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search hub integrations..."
              className="pl-9"
              data-testid="admin-integrations-manage-search"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
            className="h-10 rounded-md border border-input bg-background px-3 text-sm text-foreground"
            data-testid="admin-integrations-manage-status"
          >
            <option value="all">All</option>
            <option value="published">Published</option>
            <option value="draft">Draft</option>
            <option value="submitted">Submitted</option>
            <option value="under_review">Under review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
          <Button variant="outline" onClick={() => void load()} data-testid="admin-integrations-manage-refresh">
            Refresh
          </Button>
          <Button onClick={() => navigate('/app/admin/integrations-create')} data-testid="admin-integrations-manage-create">
            Create Integration
          </Button>
        </div>
      </Card>

      {loading && (
        <Card className="border border-border bg-card p-6">
          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading integrations...
          </div>
        </Card>
      )}

      {!loading && error && (
        <Card className="border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-300">
          {error}
        </Card>
      )}

      {!loading && !error && !items.length && (
        <Card className="border border-border bg-card p-6 text-sm text-muted-foreground">
          No integrations found for the selected filters.
        </Card>
      )}

      {!loading && !error && items.length > 0 && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {items.map((integration) => (
            <Card
              key={integration.id}
              className="flex h-full flex-col justify-between border border-border bg-card p-4"
              data-testid={`admin-integration-card-${integration.id}`}
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <ProviderLogo
                      name={integration.name}
                      url={integration.app_icon_url || integration.icon || undefined}
                      size={28}
                      className="border-0 bg-transparent"
                    />
                    <div>
                      <h3 className="text-lg font-semibold">{integration.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        {integration.integration_type.replace(/_/g, ' ')} | {integration.category.replace(/_/g, ' ')}
                      </p>
                    </div>
                  </div>
                  <Badge className={statusBadgeClass[integration.status] || 'border-border bg-background text-foreground'}>
                    {integration.status}
                  </Badge>
                </div>

                <p className="line-clamp-3 text-sm text-muted-foreground">
                  {integration.description || 'No description provided.'}
                </p>

                <div className="flex flex-wrap gap-2 text-xs">
                  <Badge className="border-border bg-background text-foreground">v{integration.version}</Badge>
                  <Badge className="border-border bg-background text-foreground gap-1">
                    <Download className="h-3 w-3" />
                    {integration.download_count} downloads
                  </Badge>
                  <Badge className="border-border bg-background text-foreground gap-1">
                    <Gauge className="h-3 w-3" />
                    {integration.usage_count} usage
                  </Badge>
                  <Badge className="border-border bg-background text-foreground">
                    {integration.active_config_count}/{integration.total_config_count} active installs
                  </Badge>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-2">
                <Button
                  variant="outline"
                  onClick={() => navigate(`/app/admin/integrations-manage/${integration.id}`)}
                  data-testid={`admin-integration-manage-${integration.id}`}
                >
                  Manage
                </Button>
                <Button
                  onClick={() => navigate(`/app/admin/integrations-update/${integration.id}`)}
                  data-testid={`admin-integration-update-${integration.id}`}
                >
                  Update
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

export default IntegrationManageMode
