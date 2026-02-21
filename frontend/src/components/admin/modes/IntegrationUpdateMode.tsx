import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { Card } from '../../ui/card'
import { Button } from '../../ui/button'
import { CreateIntegrationWizard } from '../../integrations/CreateIntegrationWizard'
import { adminIntegrationService } from '../../../services/adminIntegrationService'
import type { IntegrationSubmissionCreate, IntegrationSubmission } from '../../../services/integrationSubmissionService'

interface IntegrationUpdateModeProps {
  integrationId: number
}

const toWizardInitialData = (integration: Record<string, any>): Partial<IntegrationSubmissionCreate> => ({
  name: integration.name || '',
  subtitle: integration.subtitle || '',
  description: integration.description || '',
  category: integration.category || 'automation',
  integration_type: integration.integration_type || 'mcp_server',
  visibility: integration.visibility || 'private',
  submission_notes: integration.submission_notes || '',
  app_icon_url: integration.app_icon_url || '',
  app_screenshots: Array.isArray(integration.app_screenshots) ? integration.app_screenshots : [],
  developer_name: integration.developer_name || '',
  website_url: integration.website_url || '',
  support_url_or_email: integration.support_url_or_email || '',
  privacy_policy_url: integration.privacy_policy_url || '',
  terms_url: integration.terms_url || '',
  demo_url: integration.demo_url || '',
  documentation_url: integration.documentation_url || '',
  config_schema: integration.config_schema || {},
  credentials_schema: integration.credentials_schema || {},
  supported_features: Array.isArray(integration.supported_features) ? integration.supported_features : [],
  is_workflow_node_enabled: Boolean(integration.is_workflow_node_enabled),
  version: integration.version || '1.0.0',
})

export const IntegrationUpdateMode = ({ integrationId }: IntegrationUpdateModeProps) => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [initialData, setInitialData] = useState<Partial<IntegrationSubmissionCreate> | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await adminIntegrationService.getHubIntegration(integrationId)
      setInitialData(toWizardInitialData(response.integration))
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to load integration')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [integrationId])

  if (loading) {
    return (
      <Card className="border border-border bg-card p-6">
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading integration for update...
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

  if (!initialData) return null

  return (
    <div className="space-y-4">
      <Button
        variant="outline"
        className="gap-2"
        onClick={() => navigate(`/app/admin/integrations-manage/${integrationId}`)}
        data-testid="admin-integration-update-back"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Manage
      </Button>

      <CreateIntegrationWizard
        mode="update"
        integrationId={integrationId}
        initialData={initialData}
        onCreated={async (_integration: IntegrationSubmission) => {
          navigate(`/app/admin/integrations-manage/${integrationId}`)
        }}
      />
    </div>
  )
}

export default IntegrationUpdateMode
