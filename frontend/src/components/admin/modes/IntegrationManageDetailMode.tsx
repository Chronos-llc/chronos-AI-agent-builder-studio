import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Loader2, Trash2 } from 'lucide-react'
import { Card } from '../../ui/card'
import { Button } from '../../ui/button'
import { Badge } from '../../ui/badge'
import { ProviderLogo } from '../../brand/ProviderLogo'
import {
  adminIntegrationService,
  type AdminIntegrationHubDetail,
  type AdminIntegrationHubStatistics,
} from '../../../services/adminIntegrationService'

interface IntegrationManageDetailModeProps {
  integrationId: number
}

export const IntegrationManageDetailMode = ({ integrationId }: IntegrationManageDetailModeProps) => {
  const navigate = useNavigate()
  const [detail, setDetail] = useState<AdminIntegrationHubDetail | null>(null)
  const [statistics, setStatistics] = useState<AdminIntegrationHubStatistics | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const [detailPayload, statsPayload] = await Promise.all([
        adminIntegrationService.getHubIntegration(integrationId),
        adminIntegrationService.getHubStatistics(integrationId),
      ])
      setDetail(detailPayload)
      setStatistics(statsPayload)
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to load integration details')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [integrationId])

  const handleDelete = async () => {
    if (!detail?.integration) return
    const confirmed = window.confirm(`Delete integration "${detail.integration.name}" from hub?`)
    if (!confirmed) return
    setDeleting(true)
    try {
      await adminIntegrationService.deleteHubIntegration(integrationId)
      navigate('/app/admin/integrations-manage')
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to delete integration')
    } finally {
      setDeleting(false)
    }
  }

  if (loading) {
    return (
      <Card className="border border-border bg-card p-6">
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading integration details...
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-300">
        {error}
      </Card>
    )
  }

  if (!detail?.integration || !statistics) return null

  const integration = detail.integration

  return (
    <div className="space-y-4" data-testid="admin-integration-manage-detail">
      <Button
        variant="outline"
        className="gap-2"
        onClick={() => navigate('/app/admin/integrations-manage')}
        data-testid="admin-integration-manage-detail-back"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Integrations
      </Button>

      <Card className="border border-border bg-card p-5">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div className="flex items-start gap-3">
            <ProviderLogo
              name={integration.name}
              url={integration.app_icon_url || integration.icon || undefined}
              size={36}
              className="border-0 bg-transparent"
            />
            <div>
              <h2 className="text-2xl font-bold">{integration.name}</h2>
              <p className="text-sm text-muted-foreground">
                {integration.integration_type?.replace(/_/g, ' ')} | {integration.category?.replace(/_/g, ' ')}
              </p>
              <p className="mt-2 text-sm text-muted-foreground">{integration.description || 'No description provided.'}</p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge className="border-border bg-background text-foreground">v{integration.version}</Badge>
            <Badge className="border-border bg-background text-foreground">{integration.status}</Badge>
            <Badge className="border-border bg-background text-foreground">{integration.visibility}</Badge>
          </div>
        </div>

        <div className="mt-5 grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
          <Card className="border border-border bg-background p-3">
            <p className="text-xs text-muted-foreground">Downloads</p>
            <p className="text-xl font-semibold">{statistics.download_count}</p>
          </Card>
          <Card className="border border-border bg-background p-3">
            <p className="text-xs text-muted-foreground">Usage</p>
            <p className="text-xl font-semibold">{statistics.usage_count}</p>
            <p className="text-xs text-muted-foreground">
              {statistics.success_count} success | {statistics.error_count} errors
            </p>
          </Card>
          <Card className="border border-border bg-background p-3">
            <p className="text-xs text-muted-foreground">Configs</p>
            <p className="text-xl font-semibold">{statistics.active_config_count}/{statistics.total_config_count}</p>
            <p className="text-xs text-muted-foreground">active installs</p>
          </Card>
          <Card className="border border-border bg-background p-3">
            <p className="text-xs text-muted-foreground">Rating</p>
            <p className="text-xl font-semibold">{statistics.rating.toFixed(1)}</p>
            <p className="text-xs text-muted-foreground">{statistics.review_count} reviews</p>
          </Card>
        </div>

        <div className="mt-5 flex flex-wrap gap-2">
          <Button
            onClick={() => navigate(`/app/admin/integrations-update/${integration.id}`)}
            data-testid="admin-integration-manage-detail-update"
          >
            Update Integration
          </Button>
          <Button
            variant="destructive"
            className="gap-2"
            disabled={deleting}
            onClick={() => void handleDelete()}
            data-testid="admin-integration-manage-detail-delete"
          >
            <Trash2 className="h-4 w-4" />
            {deleting ? 'Deleting...' : 'Delete Integration'}
          </Button>
        </div>
      </Card>
    </div>
  )
}

export default IntegrationManageDetailMode
