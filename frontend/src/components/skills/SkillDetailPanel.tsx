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
  const scanTone = useMemo(() => {
    if (skill.scan_status === 'benign') return 'bg-emerald-600/20 text-emerald-200 border-emerald-400/30'
    if (skill.scan_status === 'suspicious') return 'bg-amber-600/20 text-amber-200 border-amber-400/30'
    if (skill.scan_status === 'malicious') return 'bg-rose-600/20 text-rose-200 border-rose-400/30'
    return 'bg-slate-600/20 text-slate-200 border-slate-400/30'
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
    <Card className="space-y-4 border border-white/10 bg-gradient-to-b from-[#2b1a15] to-[#130d0a] p-4 text-white" data-testid={`skill-detail-${skill.id}`}>
      <div className="space-y-2">
        <h2 className="text-2xl font-semibold">{skill.display_name}</h2>
        <p className="text-white/75">{skill.description || 'No description provided.'}</p>
      </div>

      <div className="flex flex-wrap gap-2">
        <Badge className={scanTone}>{skill.scan_status}</Badge>
        <Badge variant="outline">{skill.submission_status}</Badge>
        {skill.version && <Badge variant="outline">latest v{skill.version}</Badge>}
        <Badge variant="outline">{skill.install_count} installs</Badge>
        <Badge variant="outline">{skill.download_count} downloads</Badge>
      </div>

      <div className="rounded-lg border border-white/10 bg-black/20 p-3 text-sm">
        <div className="font-semibold uppercase tracking-wide text-white/70">Security Scan</div>
        <p className="mt-2 text-white/80">{skill.scan_summary || 'Scan summary unavailable.'}</p>
        <p className="text-xs text-white/60">Confidence: {skill.scan_confidence}%</p>
      </div>

      <div className="flex flex-wrap gap-2">
        <Button className="bg-[#dd5b42] text-white hover:bg-[#ef6b51]" onClick={handleDownload} disabled={downloadBusy} data-testid="skill-detail-download-button">
          {downloadBusy ? 'Preparing zip...' : 'Download zip'}
        </Button>
        <Button variant="outline" onClick={() => setInstallDialogOpen(true)} data-testid="skill-detail-install-button">
          Install skill
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
