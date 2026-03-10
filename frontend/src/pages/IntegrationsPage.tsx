import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Box, Loader2, PlugZap } from 'lucide-react'
import { ProviderLogo } from '../components/brand/ProviderLogo'
import { Button } from '../components/ui/button'
import { Card } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { integrationsHubService } from '../services/integrationsHubService'
import type { InstalledIntegration } from '../types/integrationsHub'

const IntegrationsPage = () => {
  const navigate = useNavigate()
  const [items, setItems] = useState<InstalledIntegration[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadInstalled = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await integrationsHubService.getInstalledIntegrations()
        setItems(response.items)
      } catch (err: any) {
        setError(err?.message || 'Failed to load installed integrations')
      } finally {
        setLoading(false)
      }
    }
    void loadInstalled()
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Integrations</p>
        <h1 className="mt-2 text-3xl font-bold text-foreground">My Integrations</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Manage integrations installed in your workspace and open the Chronos Hub for more.
        </p>
      </div>

      {loading && (
        <Card className="border border-border bg-card p-6">
          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading your integrations...
          </div>
        </Card>
      )}

      {!loading && error && (
        <Card className="border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-300">
          {error}
        </Card>
      )}

      {!loading && !error && items.length === 0 && (
        <Card className="border border-border bg-card p-8">
          <div className="mx-auto max-w-xl text-center">
            <Box className="mx-auto h-10 w-10 text-muted-foreground" />
            <h2 className="mt-4 text-xl font-semibold text-foreground">You own no integrations</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Integrations connect Chronos to external services. Choose what to do next.
            </p>
            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              <Button onClick={() => navigate('/app/integrations/hub')}>
                Looking for an integration? Search the Chronos Hub
              </Button>
              <Button variant="outline" onClick={() => navigate('/app/integrations/create')}>
                Build Your Own Integration
              </Button>
            </div>
            <p className="mt-3 text-sm text-muted-foreground">
              <Link className="underline underline-offset-4 hover:text-foreground" to="/docs#mcp">
                Developer documentation
              </Link>
            </p>
          </div>
        </Card>
      )}

      {!loading && !error && items.length > 0 && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3">
          {items.map((integration) => (
            <Card key={integration.integration_id} className="flex h-full flex-col justify-between border border-border bg-card p-4">
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <ProviderLogo
                    name={integration.name}
                    url={integration.app_icon_url || integration.icon || undefined}
                    size={30}
                    className="border-0 bg-transparent"
                  />
                  <div className="min-w-0 flex-1">
                    <h3 className="truncate text-lg font-semibold text-foreground">{integration.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      {integration.integration_type.replace(/_/g, ' ')} | {integration.category.replace(/_/g, ' ')}
                    </p>
                  </div>
                </div>
                <p className="line-clamp-3 text-sm text-muted-foreground">
                  {integration.description || 'No description provided.'}
                </p>
                <div className="flex flex-wrap gap-2 text-xs">
                  <Badge variant="outline">v{integration.version}</Badge>
                  <Badge variant="outline">{integration.active_installed_count}/{integration.installed_count} active</Badge>
                  <Badge variant="outline">{integration.download_count} downloads</Badge>
                </div>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-2">
                <Button
                  variant="outline"
                  onClick={() => navigate(`/app/integrations/${integration.integration_id}`)}
                >
                  Open
                </Button>
                <Button
                  className="gap-2"
                  onClick={() => navigate(`/app/integrations/${integration.integration_id}/configure`)}
                >
                  <PlugZap className="h-4 w-4" />
                  Manage
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

export default IntegrationsPage
