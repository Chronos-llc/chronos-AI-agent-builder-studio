import { Card } from '../ui/card'
import { Loader2 } from 'lucide-react'
import type { SkillMarketplaceItem } from '../../types/skillMarketplace'
import { SkillCard } from './SkillCard'

interface SkillMarketplaceGridProps {
  skills: SkillMarketplaceItem[]
  loading?: boolean
  error?: string | null
  onOpenSkill: (skillId: number) => void
  emptyLabel?: string
}

export function SkillMarketplaceGrid({
  skills,
  loading,
  error,
  onOpenSkill,
  emptyLabel = 'No skills available yet.',
}: SkillMarketplaceGridProps) {
  if (loading) {
    return (
      <Card className="flex min-h-[220px] items-center justify-center border border-border bg-card" data-testid="skills-grid-loading">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading skills...
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="border border-red-500/45 bg-red-500/10 p-4 text-sm text-red-700 dark:text-red-200" data-testid="skills-grid-error">
        {error}
      </Card>
    )
  }

  if (!skills.length) {
    return (
      <Card className="border border-border bg-card p-6 text-center text-muted-foreground" data-testid="skills-grid-empty">
        {emptyLabel}
      </Card>
    )
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3" data-testid="skills-grid">
      {skills.map((skill) => (
        <SkillCard key={skill.id} skill={skill} onOpen={onOpenSkill} />
      ))}
    </div>
  )
}
