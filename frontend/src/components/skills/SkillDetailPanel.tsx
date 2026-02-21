import { useEffect, useMemo, useState } from 'react'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Card } from '../ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { SkillFilesTab } from './SkillFilesTab'
import { SkillCompareTab } from './SkillCompareTab'
import { SkillVersionsTab } from './SkillVersionsTab'
import { SkillInstallDialog } from './SkillInstallDialog'
import type {
  SkillCompareResponse,
  SkillFileContentResponse,
  SkillMarketplaceDetailResponse,
  SkillVersion,
} from '../../types/skillMarketplace'

interface SkillDetailPanelProps {
  detail: SkillMarketplaceDetailResponse
  versions: SkillVersion[]
  fileContent?: SkillFileContentResponse | null
  compareResult?: SkillCompareResponse | null
  defaultAgentId?: number
  allowFuzzyInstall?: boolean
  onLoadVersionFile: (versionId: number) => void
  onCompareVersions: (baseVersionId: number, headVersionId: number) => void
  onInstall: (payload: { target_type: 'agent' | 'fuzzy'; agent_id?: number }) => Promise<void>
  onDownload: (versionId?: number) => Promise<void>
}

export function SkillDetailPanel({
  detail,
  versions,
  fileContent,
  compareResult,
  defaultAgentId,
  allowFuzzyInstall,
  onLoadVersionFile,
  onCompareVersions,
  onInstall,
  onDownload,
}: SkillDetailPanelProps) {
  const [baseVersionId, setBaseVersionId] = useState<number | undefined>(versions[0]?.id)
  const [headVersionId, setHeadVersionId] = useState<number | undefined>(versions[1]?.id || versions[0]?.id)
  const [installDialogOpen, setInstallDialogOpen] = useState(false)
  const [downloadBusy, setDownloadBusy] = useState(false)

  useEffect(() => {
    setBaseVersionId(versions[0]?.id)
    setHeadVersionId(versions[1]?.id || versions[0]?.id)
  }, [versions])

  const skill = detail.skill
  const publisher = (skill.publisher_username || 'jessenewt').replace(/^@+/, '').trim() || 'jessenewt'
  const scanTone = useMemo(() => {
    if (skill.scan_status === 'benign') return 'border-emerald-500/45 bg-emerald-500/10 text-emerald-700 dark:text-emerald-200'
    if (skill.scan_status === 'suspicious') return 'border-amber-500/45 bg-amber-500/10 text-amber-700 dark:text-amber-200'
    if (skill.scan_status === 'malicious') return 'border-rose-500/45 bg-rose-500/10 text-rose-700 dark:text-rose-200'
    return 'border-slate-500/45 bg-slate-500/10 text-slate-700 dark:text-slate-200'
  }, [skill.scan_status])

  const activeFile = fileContent?.raw_content || ''

  const handleDownload = async () => {
    setDownloadBusy(true)
    try {
      await onDownload(headVersionId)
    } finally {
      setDownloadBusy(false)
    }
  }

  return (
    <Card className="space-y-4 border border-border bg-card p-4 text-card-foreground" data-testid={`skill-detail-${skill.id}`}>
      <div className="space-y-2">
        <h2 className="text-2xl font-semibold">{skill.display_name}</h2>
        <p className="text-muted-foreground">{skill.description || 'No description provided.'}</p>
        <p className="text-sm text-muted-foreground">
          Published by <span className="font-medium text-foreground">@{publisher}</span>
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        <Badge className={scanTone}>{skill.scan_status}</Badge>
        <Badge className="border-border bg-background/70 text-foreground">{skill.submission_status}</Badge>
        {skill.version && <Badge className="border-border bg-background/70 text-foreground">latest v{skill.version}</Badge>}
        <Badge className="border-border bg-background/70 text-foreground">{skill.install_count} installs</Badge>
        <Badge className="border-border bg-background/70 text-foreground">{skill.download_count} downloads</Badge>
      </div>

      <div className="rounded-lg border border-border bg-muted/45 p-3 text-sm">
        <div className="font-semibold uppercase tracking-wide text-muted-foreground">Security Scan</div>
        <p className="mt-2 text-foreground">{skill.scan_summary || 'Scan summary unavailable.'}</p>
        <p className="text-xs text-muted-foreground">Confidence: {skill.scan_confidence}%</p>
      </div>

      <div className="flex flex-wrap gap-2">
        <Button className="bg-primary text-primary-foreground hover:bg-primary/90" onClick={handleDownload} disabled={downloadBusy} data-testid="skill-detail-download-button">
          {downloadBusy ? 'Preparing zip...' : 'Download zip'}
        </Button>
        <Button className="border border-primary/55 bg-primary/15 text-primary hover:bg-primary/25" onClick={() => setInstallDialogOpen(true)} data-testid="skill-detail-install-button">
          Install Skill
        </Button>
      </div>

      <Tabs defaultValue="files" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="files">Files</TabsTrigger>
          <TabsTrigger value="compare">Compare</TabsTrigger>
          <TabsTrigger value="versions">Versions</TabsTrigger>
        </TabsList>

        <TabsContent value="files" className="mt-4">
          <SkillFilesTab fileName={fileContent?.file_name || detail.current_version?.file_name} content={activeFile} />
        </TabsContent>

        <TabsContent value="compare" className="mt-4 space-y-3">
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              data-testid="skill-detail-compare-run-button"
              onClick={() => {
                if (!baseVersionId || !headVersionId) return
                onCompareVersions(baseVersionId, headVersionId)
              }}
              disabled={!baseVersionId || !headVersionId}
            >
              Run compare
            </Button>
          </div>
          <SkillCompareTab compareResult={compareResult} />
        </TabsContent>

        <TabsContent value="versions" className="mt-4">
          <SkillVersionsTab
            versions={versions}
            selectedBaseVersionId={baseVersionId}
            selectedHeadVersionId={headVersionId}
            onPickBase={(versionId) => {
              setBaseVersionId(versionId)
              onLoadVersionFile(versionId)
            }}
            onPickHead={(versionId) => {
              setHeadVersionId(versionId)
              onLoadVersionFile(versionId)
            }}
          />
        </TabsContent>
      </Tabs>

      <SkillInstallDialog
        open={installDialogOpen}
        onOpenChange={setInstallDialogOpen}
        defaultAgentId={defaultAgentId}
        allowFuzzy={allowFuzzyInstall}
        onInstall={onInstall}
      />
    </Card>
  )
}
