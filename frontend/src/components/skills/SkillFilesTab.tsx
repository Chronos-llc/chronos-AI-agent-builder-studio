import { ScrollArea } from '../ui/scroll-area'

interface SkillFilesTabProps {
  fileName?: string | null
  content: string
}

export function SkillFilesTab({ fileName, content }: SkillFilesTabProps) {
  return (
    <div className="space-y-3">
      <div className="text-sm text-white/70">{fileName || 'SKILL.md'}</div>
      <ScrollArea className="h-[320px] rounded-md border border-white/10 bg-[#120c09] p-4">
        <pre className="whitespace-pre-wrap text-xs leading-relaxed text-white/90">{content || 'No file content loaded.'}</pre>
      </ScrollArea>
    </div>
  )
}
