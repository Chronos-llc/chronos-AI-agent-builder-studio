import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Card } from '../ui/card'
import { Download, ShieldCheck, ShieldAlert, ShieldX, Star } from 'lucide-react'
import type { SkillMarketplaceItem } from '../../types/skillMarketplace'

interface SkillCardProps {
  skill: SkillMarketplaceItem
  onOpen: (skillId: number) => void
}

const scanBadge = (status: SkillMarketplaceItem['scan_status']) => {
  if (status === 'benign') return { label: 'Benign', icon: ShieldCheck, className: 'border-emerald-500/45 bg-emerald-500/10 text-emerald-700 dark:text-emerald-200' }
  if (status === 'suspicious') return { label: 'Suspicious', icon: ShieldAlert, className: 'border-amber-500/45 bg-amber-500/10 text-amber-700 dark:text-amber-200' }
  if (status === 'malicious') return { label: 'Malicious', icon: ShieldX, className: 'border-rose-500/45 bg-rose-500/10 text-rose-700 dark:text-rose-200' }
  return { label: 'Pending', icon: ShieldAlert, className: 'border-slate-500/45 bg-slate-500/10 text-slate-700 dark:text-slate-200' }
}

export function SkillCard({ skill, onOpen }: SkillCardProps) {
  const scan = scanBadge(skill.scan_status)
  const ScanIcon = scan.icon
  const publisher = skill.publisher_username ? skill.publisher_username.replace(/^@+/, '').trim() || null : null

  return (
    <Card className="flex h-full flex-col justify-between border border-border bg-card p-4 text-card-foreground shadow-sm" data-testid={`skill-card-${skill.id}`}>
      <div className="space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold">{skill.display_name}</h3>
            <p className="text-sm text-muted-foreground">{skill.description || 'No description provided.'}</p>
          </div>
          <Badge className={scan.className}>
            <ScanIcon className="mr-1 h-3.5 w-3.5" />
            {scan.label}
          </Badge>
        </div>

        <div className="flex flex-wrap gap-2">
          {skill.category && <Badge className="border-border bg-background/70 text-foreground">{skill.category}</Badge>}
          {skill.version && <Badge className="border-border bg-background/70 text-foreground">v{skill.version}</Badge>}
          <Badge className="border-border bg-background/70 text-foreground">
            <Star className="mr-1 h-3 w-3 fill-current" />
            {skill.install_count} installs
          </Badge>
          <Badge className="border-border bg-background/70 text-foreground">
            <Download className="mr-1 h-3 w-3" />
            {skill.download_count} downloads
          </Badge>
        </div>

        {publisher && (
          <p className="text-sm text-muted-foreground">
            Published by <span className="font-medium text-foreground">@{publisher}</span>
          </p>
        )}
      </div>

      <Button className="mt-4 w-full bg-primary text-primary-foreground hover:bg-primary/90" onClick={() => onOpen(skill.id)} data-testid={`skill-card-open-${skill.id}`}>
        Open Skill
      </Button>
    </Card>
  )
}
