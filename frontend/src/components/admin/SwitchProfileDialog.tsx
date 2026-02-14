import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog'

const API_BASE_URL_RAW = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const API_BASE_URL = API_BASE_URL_RAW.replace(/\/$/, '')

interface SwitchProfileDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const SwitchProfileDialog: React.FC<SwitchProfileDialogProps> = ({ open, onOpenChange }) => {
  const navigate = useNavigate()
  const { setAccessToken, refreshSessionContext } = useAuth()
  const [identifier, setIdentifier] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async () => {
    const trimmed = identifier.trim()
    if (!trimmed) {
      setError('Enter a username or email')
      return
    }

    setSubmitting(true)
    setError(null)
    try {
      const token = localStorage.getItem('chronos_access_token') || localStorage.getItem('access_token')
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/switch-profile/start`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ identifier: trimmed }),
      })
      if (!response.ok) {
        const body = await response.json().catch(() => null)
        throw new Error(body?.detail || 'Failed to switch profile')
      }

      const payload = await response.json()
      if (payload?.access_token) {
        setAccessToken(payload.access_token)
      }
      await refreshSessionContext()
      onOpenChange(false)
      setIdentifier('')
      navigate('/app')
    } catch (err: any) {
      setError(err?.message || 'Failed to switch profile')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Switch profile</DialogTitle>
          <DialogDescription>
            Enter a non-admin username or email to switch into that user view.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-2">
          <Input
            value={identifier}
            onChange={(event) => setIdentifier(event.target.value)}
            placeholder="username or email"
            autoFocus
          />
          {error && <p className="text-sm text-red-400">{error}</p>}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={submitting}>
            Cancel
          </Button>
          <Button onClick={onSubmit} disabled={submitting}>
            {submitting ? 'Switching...' : 'Switch profile'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default SwitchProfileDialog
