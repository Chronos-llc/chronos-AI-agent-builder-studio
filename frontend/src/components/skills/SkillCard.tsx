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
  if (status === 'benign') return { label: 'Benign', icon: ShieldCheck, className: 'bg-emerald-600/20 text-emerald-300 border-emerald-500/40' }
  if (status === 'suspicious') return { label: 'Suspicious', icon: ShieldAlert, className: 'bg-amber-600/20 text-amber-300 border-amber-500/40' }
  if (status === 'malicious') return { label: 'Malicious', icon: ShieldX, className: 'bg-rose-600/20 text-rose-300 border-rose-500/40' }
  return { label: 'Pending', icon: ShieldAlert, className: 'bg-slate-600/20 text-slate-200 border-slate-500/40' }
}

export function SkillCard({ skill, onOpen }: SkillCardProps) {
  const scan = scanBadge(skill.scan_status)
  const ScanIcon = scan.icon

  return (
    <Card className="flex h-full flex-col justify-between border border-white/10 bg-gradient-to-b from-[#2a1712] to-[#160f0c] p-4 text-white shadow-xl" data-testid={`skill-card-${skill.id}`}>
      <div className="space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold">{skill.display_name}</h3>
            <p className="text-sm text-white/60">{skill.description || 'No description provided.'}</p>
          </div>
          <Badge className={scan.className}>
            <ScanIcon className="mr-1 h-3.5 w-3.5" />
            {scan.label}
          </Badge>
        </div>

        <div className="flex flex-wrap gap-2">
          {skill.category && <Badge variant="outline">{skill.category}</Badge>}
          {skill.version && <Badge variant="outline">v{skill.version}</Badge>}
          <Badge variant="outline">
            <Star className="mr-1 h-3 w-3 fill-current" />
            {skill.install_count} installs
          </Badge>
          <Badge variant="outline">
            <Download className="mr-1 h-3 w-3" />
            {skill.download_count} downloads
          </Badge>
        </div>

        <p className="text-sm text-white/70">
          by <span className="font-medium text-white">{skill.publisher_username || 'unknown'}</span>
        </p>
      </div>

      <Button className="mt-4 w-full bg-[#dd5b42] text-white hover:bg-[#ef6b51]" onClick={() => onOpen(skill.id)} data-testid={`skill-card-open-${skill.id}`}>
        Open Skill
      </Button>
    </Card>
  )
}
