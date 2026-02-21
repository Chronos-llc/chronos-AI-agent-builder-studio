import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import type { SkillVersion } from '../../types/skillMarketplace'

interface SkillVersionsTabProps {
  versions: SkillVersion[]
  selectedBaseVersionId?: number
  selectedHeadVersionId?: number
  onPickBase: (versionId: number) => void
  onPickHead: (versionId: number) => void
}

export function SkillVersionsTab({
  versions,
  selectedBaseVersionId,
  selectedHeadVersionId,
  onPickBase,
  onPickHead,
}: SkillVersionsTabProps) {
  if (!versions.length) {
    return <div className="text-sm text-muted-foreground">No versions yet.</div>
  }

  return (
    <div className="space-y-3">
      {versions.map((version) => (
        <div key={version.id} className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-border bg-muted/40 p-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-medium text-foreground">v{version.version}</span>
              {version.is_current && <Badge className="border-cyan-500/45 bg-cyan-500/10 text-cyan-700 dark:text-cyan-200">Current</Badge>}
              <Badge className="border-border bg-background/80 text-foreground">{version.scan_status}</Badge>
            </div>
            <p className="text-xs text-muted-foreground">{new Date(version.created_at).toLocaleString()}</p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant={selectedBaseVersionId === version.id ? 'default' : 'outline'}
              onClick={() => onPickBase(version.id)}
            >
              Base
            </Button>
            <Button
              size="sm"
              variant={selectedHeadVersionId === version.id ? 'default' : 'outline'}
              onClick={() => onPickHead(version.id)}
            >
              Head
            </Button>
          </div>
        </div>
      ))}
    </div>
  )
}
