import { ScrollArea } from '../ui/scroll-area'

interface SkillFilesTabProps {
  fileName?: string | null
  content: string
}

export function SkillFilesTab({ fileName, content }: SkillFilesTabProps) {
  return (
    <div className="space-y-3">
      <div className="text-sm text-muted-foreground">{fileName || 'SKILL.md'}</div>
      <ScrollArea className="h-[320px] rounded-md border border-border bg-muted/40 p-4">
        <pre className="whitespace-pre-wrap text-xs leading-relaxed text-foreground">{content || 'No file content loaded.'}</pre>
      </ScrollArea>
    </div>
  )
}
