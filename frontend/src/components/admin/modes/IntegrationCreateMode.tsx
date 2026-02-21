import React, { useState } from 'react'
import { CreateIntegrationWizard } from '../../integrations/CreateIntegrationWizard'
import type { IntegrationSubmission, IntegrationSubmissionCreate } from '../../../services/integrationSubmissionService'

export const IntegrationCreateMode: React.FC = () => {
  const [lastPublished, setLastPublished] = useState<IntegrationSubmission | null>(null)

  const initialData: Partial<IntegrationSubmissionCreate> = {
    config_schema: {},
    credentials_schema: {},
    supported_features: [],
    app_screenshots: [],
    is_workflow_node_enabled: false,
  }

  return (
    <div className="space-y-4">
      <div className="space-y-1">
        <h2 className="text-2xl font-bold">Create Integrations</h2>
        <p className="text-sm text-muted-foreground">
          Build and publish integrations directly to the user integrations hub.
        </p>
      </div>

      <CreateIntegrationWizard
        adminPublish
        initialData={initialData}
        onCreated={async (integration) => {
          setLastPublished(integration)
        }}
      />

      {lastPublished && (
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-200">
          Published <span className="font-semibold">{lastPublished.name}</span> ({lastPublished.integration_type}) to the integrations hub.
        </div>
      )}
    </div>
  )
}

export default IntegrationCreateMode
