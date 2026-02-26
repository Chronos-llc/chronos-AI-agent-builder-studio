import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ProtectedRoute } from '../components/ProtectedRoute'
import { CreateIntegrationWizard } from '../components/integrations/CreateIntegrationWizard'
import {
  integrationSubmissionService,
  type IntegrationSubmission,
  type IntegrationSubmissionEvent,
} from '../services/integrationSubmissionService'

const statusStyles: Record<string, string> = {
  draft: 'bg-slate-500/20 text-slate-200',
  submitted: 'bg-cyan-500/20 text-cyan-200',
  under_review: 'bg-amber-500/20 text-amber-200',
  approved: 'bg-emerald-500/20 text-emerald-200',
  rejected: 'bg-rose-500/20 text-rose-200',
  published: 'bg-purple-500/20 text-purple-200',
}

const IntegrationCreatePage: React.FC = () => {
  const [submissions, setSubmissions] = useState<IntegrationSubmission[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [events, setEvents] = useState<IntegrationSubmissionEvent[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [planType, setPlanType] = useState<string>('free')

  const loadSubmissions = async () => {
    setLoading(true)
    try {
      setSubmissions(await integrationSubmissionService.listMySubmissions())
      setError(null)
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to load submissions')
    } finally {
      setLoading(false)
    }
  }

  const loadEvents = async (integrationId: number) => {
    setSelectedId(integrationId)
    try {
      setEvents(await integrationSubmissionService.getSubmissionEvents(integrationId))
    } catch {
      setEvents([])
    }
  }

  useEffect(() => {
    loadSubmissions()
  }, [])

  useEffect(() => {
    const loadPlan = async () => {
      try {
        const response = await fetch('/api/v1/usage/plan', { credentials: 'include' })
        if (!response.ok) return
        const payload = await response.json()
        setPlanType((payload?.plan_type || 'free').toLowerCase())
      } catch {
        setPlanType('free')
      }
    }
    loadPlan()
  }, [])

  const canPublish = ['team_developer', 'special_service', 'enterprise', 'pro'].includes(planType)

  return (
    <ProtectedRoute>
      <div className="space-y-6">
        {canPublish ? (
          <CreateIntegrationWizard onCreated={async () => { await loadSubmissions() }} />
        ) : (
          <div className="chronos-surface p-6">
            <h2 className="text-xl font-semibold text-white">Create New Integration</h2>
            <p className="mt-2 text-sm text-white/75">
              Publishing integrations is available from the Team/Developer plan and above.
            </p>
            <p className="mt-3 text-xs text-amber-200">Current plan: {planType || 'free'}</p>
            <Link to="/docs#mcp" className="mt-3 inline-block text-xs text-cyan-200 underline underline-offset-4">
              Read developer documentation
            </Link>
          </div>
        )}

        <div className="chronos-surface p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">My Submissions</h2>
            <button onClick={loadSubmissions} className="rounded-md border border-white/20 px-3 py-1 text-sm text-white/80 hover:text-white">
              Refresh
            </button>
          </div>
          {error && <p className="mb-3 text-sm text-red-300">{error}</p>}
          {loading ? (
            <p className="text-sm text-white/70">Loading submissions...</p>
          ) : (
            <div className="space-y-3">
              {submissions.map(item => (
                <button
                  key={item.id}
                  onClick={() => loadEvents(item.id)}
                  className="w-full rounded-lg border border-white/10 bg-black/25 p-4 text-left transition hover:border-white/25"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-white">{item.name}</p>
                      <p className="text-sm text-white/60">{item.integration_type.replace('_', ' ')} | {item.category.replace('_', ' ')}</p>
                    </div>
                    <span className={`rounded-full px-3 py-1 text-xs ${statusStyles[item.status] || 'bg-white/10 text-white/70'}`}>
                      {item.status}
                    </span>
                  </div>
                </button>
              ))}
              {!submissions.length && <p className="text-sm text-white/60">No submissions yet.</p>}
            </div>
          )}
        </div>

        {selectedId && (
          <div className="chronos-surface p-6">
            <h3 className="mb-4 text-lg font-semibold text-white">Submission Timeline #{selectedId}</h3>
            <div className="space-y-2">
              {events.map(event => (
                <div key={event.id} className="rounded-md border border-white/10 bg-black/20 p-3">
                  <p className="text-sm font-medium text-white">{event.action}</p>
                  <p className="text-xs text-white/60">{new Date(event.created_at).toLocaleString()}</p>
                </div>
              ))}
              {!events.length && <p className="text-sm text-white/60">No events available.</p>}
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  )
}

export default IntegrationCreatePage
