import { useState } from 'react'
import { CreateIntegrationWizard } from '../../integrations/CreateIntegrationWizard'
import type { IntegrationSubmission } from '../../../services/integrationSubmissionService'
import { Card } from '../../ui/card'
import { Badge } from '../../ui/badge'

export const IntegrationCreateMode = () => {
  const [lastPublished, setLastPublished] = useState<IntegrationSubmission | null>(null)

  return (
    <div className="space-y-4">
      <div className="space-y-1">
        <h2 className="text-2xl font-bold">Create Integrations</h2>
        <p className="text-sm text-muted-foreground">
          Build and publish integrations directly to the user integrations hub.
        </p>
      </div>

      {lastPublished && (
        <Card className="border border-emerald-500/30 bg-emerald-500/10 p-4">
          <div className="flex flex-wrap items-center gap-3 text-sm">
            <Badge className="bg-emerald-600 text-white">Published</Badge>
            <span className="font-medium text-foreground">{lastPublished.name}</span>
            <span className="text-muted-foreground">
              {lastPublished.category.replace(/_/g, ' ')} | {lastPublished.integration_type.replace(/_/g, ' ')}
            </span>
          </div>
        </Card>
      )}

      <CreateIntegrationWizard
        adminPublish
        onCreated={async (integration) => {
          setLastPublished(integration)
        }}
      />
    </div>
  )
}

export default IntegrationCreateMode
