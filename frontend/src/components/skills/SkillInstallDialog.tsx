import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Label } from '../ui/label'

interface SkillInstallDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  defaultAgentId?: number
  allowFuzzy?: boolean
  onInstall: (payload: { target_type: 'agent' | 'fuzzy'; agent_id?: number }) => Promise<void>
}

export function SkillInstallDialog({
  open,
  onOpenChange,
  defaultAgentId,
  allowFuzzy = false,
  onInstall,
}: SkillInstallDialogProps) {
  const [targetType, setTargetType] = useState<'agent' | 'fuzzy'>(defaultAgentId ? 'agent' : (allowFuzzy ? 'fuzzy' : 'agent'))
  const [agentIdValue, setAgentIdValue] = useState(defaultAgentId ? String(defaultAgentId) : '')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async () => {
    setError(null)
    if (targetType === 'agent' && !agentIdValue.trim()) {
      setError('Agent ID is required for agent installs.')
      return
    }

    try {
      setSubmitting(true)
      await onInstall({
        target_type: targetType,
        agent_id: targetType === 'agent' ? Number(agentIdValue) : undefined,
      })
      onOpenChange(false)
    } catch (installError) {
      setError(installError instanceof Error ? installError.message : 'Install failed.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent data-testid="skill-install-dialog">
        <DialogHeader>
          <DialogTitle>Install Skill</DialogTitle>
          <DialogDescription>Select where this skill should be installed.</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="flex items-center gap-4 text-sm">
            <label className="flex items-center gap-2">
              <input
                type="radio"
                data-testid="skill-install-target-agent"
                checked={targetType === 'agent'}
                onChange={() => setTargetType('agent')}
              />
              Current agent
            </label>
            {allowFuzzy && (
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  data-testid="skill-install-target-fuzzy"
                  checked={targetType === 'fuzzy'}
                  onChange={() => setTargetType('fuzzy')}
                />
                Fuzzy knowledge base
              </label>
            )}
          </div>

          {targetType === 'agent' && (
            <div className="space-y-2">
              <Label htmlFor="install-agent-id">Agent ID</Label>
              <Input
                id="install-agent-id"
                data-testid="skill-install-agent-id-input"
                inputMode="numeric"
                value={agentIdValue}
                onChange={(event) => setAgentIdValue(event.target.value)}
              />
            </div>
          )}

          {error && <p className="text-sm text-red-500">{error}</p>}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={submitting} data-testid="skill-install-cancel-button">
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={submitting} data-testid="skill-install-confirm-button">
            {submitting ? 'Installing...' : 'Install Skill'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
