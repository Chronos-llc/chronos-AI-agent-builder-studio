import React, { useMemo, useState } from 'react'
import { integrationSubmissionService, type IntegrationSubmission, type IntegrationSubmissionCreate } from '../../services/integrationSubmissionService'

interface CreateIntegrationWizardProps {
  onCreated?: (submission: IntegrationSubmission) => void | Promise<void>
}

const categories = [
  'data_sources',
  'ai_models',
  'communication',
  'automation',
  'monitoring',
  'storage',
  'utilities',
]

export const CreateIntegrationWizard: React.FC<CreateIntegrationWizardProps> = ({ onCreated }) => {
  const [step, setStep] = useState(1)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [draftId, setDraftId] = useState<number | null>(null)

  const [form, setForm] = useState<IntegrationSubmissionCreate>({
    name: '',
    subtitle: '',
    description: '',
    category: 'automation',
    integration_type: 'mcp_server',
    visibility: 'private',
    submission_notes: '',
    app_icon_url: '',
    app_screenshots: [],
    developer_name: '',
    website_url: '',
    support_url_or_email: '',
    privacy_policy_url: '',
    terms_url: '',
    demo_url: '',
    documentation_url: '',
    config_schema: {},
    credentials_schema: {},
    supported_features: [],
    is_workflow_node_enabled: false,
  })

  const isLastStep = step === 6
  const canContinue = useMemo(() => {
    if (step === 1) return Boolean(form.name.trim() && form.description.trim() && form.category)
    if (step === 2) return Boolean(form.integration_type)
    if (step === 4) return Boolean(form.app_icon_url?.trim())
    return true
  }, [form, step])

  const update = (key: keyof IntegrationSubmissionCreate, value: any) => {
    setForm(prev => ({ ...prev, [key]: value }))
  }

  const parseJsonField = (value: string, field: 'config_schema' | 'credentials_schema') => {
    if (!value.trim()) {
      update(field, {})
      return
    }
    try {
      update(field, JSON.parse(value))
      setError(null)
    } catch {
      setError(`Invalid JSON for ${field.replace('_', ' ')}`)
    }
  }

  const saveDraft = async () => {
    setSaving(true)
    setError(null)
    try {
      if (!draftId) {
        const created = await integrationSubmissionService.createSubmission(form)
        setDraftId(created.id)
        await onCreated?.(created)
      } else {
        const updated = await integrationSubmissionService.updateSubmission(draftId, form)
        await onCreated?.(updated)
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail?.message || err?.response?.data?.detail || err?.message || 'Failed to save draft')
      throw err
    } finally {
      setSaving(false)
    }
  }

  const handleContinue = async () => {
    if (!canContinue || saving) return
    if (step < 6) {
      await saveDraft()
      setStep(prev => prev + 1)
      return
    }

    if (!draftId) {
      await saveDraft()
    }
    const submissionId = draftId || (await integrationSubmissionService.createSubmission(form)).id
    await integrationSubmissionService.submitSubmission(submissionId)
    setStep(7)
  }

  return (
    <div className="chronos-surface p-6">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">Create New Integration</h2>
        <span className="rounded-full border border-white/15 px-3 py-1 text-xs text-white/75">Step {Math.min(step, 6)} of 6</span>
      </div>

      {error && <div className="mb-4 rounded-md border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">{error}</div>}

      {step === 1 && (
        <div className="grid gap-4 md:grid-cols-2">
          <input className="rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white" placeholder="App name" value={form.name} onChange={e => update('name', e.target.value)} />
          <input className="rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white" placeholder="Subtitle" value={form.subtitle} onChange={e => update('subtitle', e.target.value)} />
          <textarea className="md:col-span-2 min-h-[100px] rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white" placeholder="Describe what this integration does" value={form.description} onChange={e => update('description', e.target.value)} />
          <select className="rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white" value={form.category} onChange={e => update('category', e.target.value)}>
            {categories.map(category => (
              <option key={category} value={category}>{category.replace('_', ' ')}</option>
            ))}
          </select>
          <input className="rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white" placeholder="Developer or company name" value={form.developer_name} onChange={e => update('developer_name', e.target.value)} />
        </div>
      )}

      {step === 2 && (
        <div className="space-y-4">
          <select className="w-full rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white" value={form.integration_type} onChange={e => update('integration_type', e.target.value as 'mcp_server' | 'api')}>
            <option value="mcp_server">MCP Server</option>
            <option value="api">API Integration</option>
          </select>
          <textarea
            className="min-h-[180px] w-full rounded-md border border-white/15 bg-black/30 px-3 py-2 font-mono text-sm text-white"
            defaultValue={JSON.stringify(form.config_schema, null, 2)}
            onBlur={e => parseJsonField(e.target.value, 'config_schema')}
            placeholder='{"command":"npx","args":["-y","my-mcp-server"]}'
          />
          <textarea
            className="min-h-[140px] w-full rounded-md border border-white/15 bg-black/30 px-3 py-2 font-mono text-sm text-white"
            defaultValue={JSON.stringify(form.credentials_schema, null, 2)}
            onBlur={e => parseJsonField(e.target.value, 'credentials_schema')}
            placeholder='{"api_key":{"required":true,"sensitive":true}}'
          />
        </div>
      )}

      {step === 3 && (
        <div className="space-y-3 text-sm text-white/80">
          <label className="flex items-center gap-2">
            <input type="checkbox" className="h-4 w-4" checked={form.is_workflow_node_enabled} onChange={e => update('is_workflow_node_enabled', e.target.checked)} />
            Enable as workflow node after approval
          </label>
          <textarea
            className="min-h-[120px] w-full rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white"
            placeholder="Testing checklist and expected behavior"
            value={form.submission_notes}
            onChange={e => update('submission_notes', e.target.value)}
          />
        </div>
      )}

      {step === 4 && (
        <div className="space-y-3">
          <input className="w-full rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white" placeholder="Icon URL" value={form.app_icon_url} onChange={e => update('app_icon_url', e.target.value)} />
          <textarea
            className="min-h-[120px] w-full rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white"
            placeholder="Screenshot URLs (one per line)"
            value={form.app_screenshots.join('\n')}
            onChange={e => update('app_screenshots', e.target.value.split('\n').map(item => item.trim()).filter(Boolean))}
          />
        </div>
      )}

      {step === 5 && (
        <div className="grid gap-3 md:grid-cols-2">
          <select className="rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white" value={form.visibility} onChange={e => update('visibility', e.target.value)}>
            <option value="private">Private</option>
            <option value="team">Team</option>
            <option value="public">Public</option>
          </select>
          <input className="rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white" placeholder="Documentation URL" value={form.documentation_url} onChange={e => update('documentation_url', e.target.value)} />
          <input className="rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white" placeholder="Website URL" value={form.website_url} onChange={e => update('website_url', e.target.value)} />
          <input className="rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white" placeholder="Support URL or email" value={form.support_url_or_email} onChange={e => update('support_url_or_email', e.target.value)} />
          <input className="rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white" placeholder="Privacy policy URL" value={form.privacy_policy_url} onChange={e => update('privacy_policy_url', e.target.value)} />
          <input className="rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white" placeholder="Terms URL" value={form.terms_url} onChange={e => update('terms_url', e.target.value)} />
          <input className="rounded-md border border-white/15 bg-black/30 px-3 py-2 text-white md:col-span-2" placeholder="Demo URL" value={form.demo_url} onChange={e => update('demo_url', e.target.value)} />
        </div>
      )}

      {step === 6 && (
        <div className="space-y-3 text-sm text-white/80">
          <p>Review summary before submitting:</p>
          <div className="rounded-md border border-white/10 bg-black/30 p-4">
            <p><span className="text-white/60">Name:</span> {form.name}</p>
            <p><span className="text-white/60">Type:</span> {form.integration_type}</p>
            <p><span className="text-white/60">Visibility:</span> {form.visibility}</p>
            <p><span className="text-white/60">Workflow node:</span> {form.is_workflow_node_enabled ? 'Enabled' : 'Disabled'}</p>
          </div>
          <p className="text-white/60">After submission, admins review and publish globally after approval.</p>
        </div>
      )}

      {step === 7 && (
        <div className="rounded-md border border-emerald-500/40 bg-emerald-500/10 p-4 text-emerald-200">
          Submission sent. You can track status in My Submissions below.
        </div>
      )}

      <div className="mt-6 flex justify-between">
        <button
          type="button"
          disabled={saving || step <= 1 || step >= 7}
          onClick={() => setStep(prev => prev - 1)}
          className="rounded-md border border-white/20 px-4 py-2 text-sm text-white disabled:opacity-40"
        >
          Back
        </button>
        {step < 7 && (
          <button
            type="button"
            onClick={handleContinue}
            disabled={!canContinue || saving}
            className="rounded-md bg-cyan-300 px-4 py-2 text-sm font-semibold text-[#081018] disabled:opacity-40"
          >
            {isLastStep ? 'Submit for review' : 'Continue'}
          </button>
        )}
      </div>
    </div>
  )
}
