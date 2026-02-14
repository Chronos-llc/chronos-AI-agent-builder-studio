import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

const API_BASE_URL_RAW = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const API_BASE_URL = API_BASE_URL_RAW.replace(/\/$/, '')

const ImpersonationBanner = () => {
  const navigate = useNavigate()
  const { sessionContext, setAccessToken, refreshSessionContext } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!sessionContext?.is_impersonating) {
    return null
  }

  const handleReturnToAdmin = async () => {
    setLoading(true)
    setError(null)
    try {
      const token = localStorage.getItem('chronos_access_token') || localStorage.getItem('access_token')
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/impersonation/exit`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      })
      if (!response.ok) {
        const body = await response.json().catch(() => null)
        throw new Error(body?.detail || 'Failed to return to admin')
      }
      const payload = await response.json()
      if (payload?.access_token) {
        setAccessToken(payload.access_token)
      }
      await refreshSessionContext()
      navigate('/app/admin')
    } catch (err: any) {
      setError(err?.message || 'Failed to return to admin')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mb-4 rounded-xl border border-amber-400/40 bg-amber-300/10 px-4 py-3 text-sm text-amber-100">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <strong className="font-semibold">Admin impersonation active.</strong> You are viewing the user side with a switched profile.
          {error && <span className="ml-2 text-red-200">{error}</span>}
        </div>
        <button className="btn btn-secondary !border-amber-300/50 !text-amber-100" onClick={handleReturnToAdmin} disabled={loading}>
          {loading ? 'Switching...' : 'Return to Admin'}
        </button>
      </div>
    </div>
  )
}

export default ImpersonationBanner
