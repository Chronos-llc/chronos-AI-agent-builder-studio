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
    return <div className="text-sm text-white/70">No versions yet.</div>
  }

  return (
    <div className="space-y-3">
      {versions.map((version) => (
        <div key={version.id} className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-white/10 bg-[#120c09] p-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-medium text-white">v{version.version}</span>
              {version.is_current && <Badge className="bg-cyan-600/20 text-cyan-200 border-cyan-400/30">Current</Badge>}
              <Badge variant="outline">{version.scan_status}</Badge>
            </div>
            <p className="text-xs text-white/60">{new Date(version.created_at).toLocaleString()}</p>
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
