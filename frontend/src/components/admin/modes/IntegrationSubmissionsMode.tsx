import React, { useEffect, useState } from 'react'
import axios from 'axios'

type ModerationAction = 'approve' | 'reject' | 'request_changes'

interface Submission {
  id: number
  name: string
  integration_type: string
  category: string
  status: string
  visibility: string
  updated_at: string
  moderation_notes?: string
}

export const IntegrationSubmissionsMode: React.FC = () => {
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [selected, setSelected] = useState<Submission | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [moderationNotes, setModerationNotes] = useState('')

  const fetchSubmissions = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.get<Submission[]>('/api/v1/admin/integrations/submissions')
      setSubmissions(response.data)
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to fetch submissions')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSubmissions()
  }, [])

  const runModeration = async (action: ModerationAction) => {
    if (!selected) return
    try {
      await axios.post(`/api/v1/admin/integrations/submissions/${selected.id}/review`, {
        action,
        moderation_notes: moderationNotes,
      })
      await fetchSubmissions()
      const updated = submissions.find(item => item.id === selected.id)
      if (updated) setSelected(updated)
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || `Failed to ${action}`)
    }
  }

  const publish = async () => {
    if (!selected) return
    try {
      await axios.post(`/api/v1/admin/integrations/submissions/${selected.id}/publish`)
      await fetchSubmissions()
      setSelected(null)
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to publish')
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Integration Submissions</h2>
        <button onClick={fetchSubmissions} className="rounded border border-border px-3 py-1 text-sm">Refresh</button>
      </div>
      {error && <p className="text-sm text-red-500">{error}</p>}

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-border p-4">
          {loading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : (
            <div className="space-y-2">
              {submissions.map(item => (
                <button
                  key={item.id}
                  onClick={() => {
                    setSelected(item)
                    setModerationNotes(item.moderation_notes || '')
                  }}
                  className={`w-full rounded border p-3 text-left ${selected?.id === item.id ? 'border-primary bg-primary/5' : 'border-border'}`}
                >
                  <p className="font-medium">{item.name}</p>
                  <p className="text-xs text-muted-foreground">{item.integration_type} | {item.category}</p>
                  <p className="text-xs text-muted-foreground">Status: {item.status}</p>
                </button>
              ))}
              {!submissions.length && <p className="text-sm text-muted-foreground">No pending submissions.</p>}
            </div>
          )}
        </div>

        <div className="rounded-lg border border-border p-4">
          {selected ? (
            <div className="space-y-3">
              <h3 className="font-semibold">{selected.name}</h3>
              <p className="text-sm text-muted-foreground">Visibility: {selected.visibility}</p>
              <p className="text-sm text-muted-foreground">Status: {selected.status}</p>
              <textarea
                className="min-h-[120px] w-full rounded border border-border bg-background px-3 py-2"
                placeholder="Moderation notes"
                value={moderationNotes}
                onChange={e => setModerationNotes(e.target.value)}
              />
              <div className="flex flex-wrap gap-2">
                <button className="rounded bg-emerald-600 px-3 py-1 text-sm text-white" onClick={() => runModeration('approve')}>Approve</button>
                <button className="rounded bg-amber-600 px-3 py-1 text-sm text-white" onClick={() => runModeration('request_changes')}>Request changes</button>
                <button className="rounded bg-rose-600 px-3 py-1 text-sm text-white" onClick={() => runModeration('reject')}>Reject</button>
                <button className="rounded bg-cyan-600 px-3 py-1 text-sm text-white" onClick={publish}>Publish</button>
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Select a submission to review.</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default IntegrationSubmissionsMode
