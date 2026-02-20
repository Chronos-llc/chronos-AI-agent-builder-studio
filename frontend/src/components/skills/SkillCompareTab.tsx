import { useMemo } from 'react'
import { ScrollArea } from '../ui/scroll-area'
import type { SkillCompareResponse } from '../../types/skillMarketplace'

interface SkillCompareTabProps {
  compareResult?: SkillCompareResponse | null
}

export function SkillCompareTab({ compareResult }: SkillCompareTabProps) {
  const summary = useMemo(() => {
    if (!compareResult) return null
    return `+${compareResult.added_lines} / -${compareResult.removed_lines}`
  }, [compareResult])

  if (!compareResult) {
    return <div className="text-sm text-white/70">Select two versions to compare.</div>
  }

  return (
    <div className="space-y-3">
      <div className="text-sm text-white/70">Diff summary: {summary}</div>
      <ScrollArea className="h-[320px] rounded-md border border-white/10 bg-[#120c09] p-4">
        <pre className="whitespace-pre-wrap text-xs leading-relaxed text-white/90">{compareResult.diff_text || 'No textual diff.'}</pre>
      </ScrollArea>
    </div>
  )
}
