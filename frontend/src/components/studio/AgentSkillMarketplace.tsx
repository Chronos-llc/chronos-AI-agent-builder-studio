import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { Button } from '../ui/button'
import { Card } from '../ui/card'
import { Input } from '../ui/input'
import { ArrowLeft, Loader2, Search } from 'lucide-react'
import { SkillMarketplaceGrid } from '../skills/SkillMarketplaceGrid'
import { SkillDetailPanel } from '../skills/SkillDetailPanel'
import { SkillUploadForm } from '../skills/SkillUploadForm'
import { skillMarketplaceService } from '../../services/skillMarketplaceService'
import type {
  SkillCompareResponse,
  SkillFileContentResponse,
  SkillMarketplaceDetailResponse,
  SkillMarketplaceItem,
  SkillVersion,
} from '../../types/skillMarketplace'

interface AgentSkillMarketplaceProps {
  currentAgentId?: number
}

export function AgentSkillMarketplace({ currentAgentId }: AgentSkillMarketplaceProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [skills, setSkills] = useState<SkillMarketplaceItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [detail, setDetail] = useState<SkillMarketplaceDetailResponse | null>(null)
  const [versions, setVersions] = useState<SkillVersion[]>([])
  const [fileContent, setFileContent] = useState<SkillFileContentResponse | null>(null)
  const [compareResult, setCompareResult] = useState<SkillCompareResponse | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)

  const loadMarketplace = async () => {
    try {
      setLoading(true)
      setError(null)
      const payload = await skillMarketplaceService.listMarketplace({
        page: 1,
        page_size: 40,
        search_query: searchQuery || undefined,
        sort_by: 'install_count',
        sort_order: 'desc',
      })
      setSkills(payload.items)
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Failed to load skills.')
    } finally {
      setLoading(false)
    }
  }

  const openSkill = async (skillId: number) => {
    try {
      setDetailLoading(true)
      setDetail(null)
      setVersions([])
      setFileContent(null)
      setCompareResult(null)
      const [detailPayload, versionsPayload] = await Promise.all([
        skillMarketplaceService.getSkill(skillId),
        skillMarketplaceService.listVersions(skillId),
      ])
      setDetail(detailPayload)
      setVersions(versionsPayload.items)
      setCompareResult(null)
      if (versionsPayload.items.length > 0) {
        const selectedVersionId = detailPayload.current_version?.id || versionsPayload.items[0].id
        const filePayload = await skillMarketplaceService.getVersionFile(skillId, selectedVersionId)
        setFileContent(filePayload)
      } else {
        setFileContent(null)
      }
    } catch (openError) {
      toast.error(openError instanceof Error ? openError.message : 'Unable to open skill.')
    } finally {
      setDetailLoading(false)
    }
  }

  const closeSkillDetail = () => {
    setDetail(null)
    setVersions([])
    setFileContent(null)
    setCompareResult(null)
    setDetailLoading(false)
  }

  const onLoadVersionFile = async (versionId: number) => {
    if (!detail) return
    const payload = await skillMarketplaceService.getVersionFile(detail.skill.id, versionId)
    setFileContent(payload)
  }

  const onCompareVersions = async (baseVersionId: number, headVersionId: number) => {
    if (!detail) return
    const payload = await skillMarketplaceService.compareVersions(detail.skill.id, baseVersionId, headVersionId)
    setCompareResult(payload)
  }

  const onInstall = async (payload: { target_type: 'agent' | 'fuzzy'; agent_id?: number }) => {
    if (!detail) return
    const installPayload = {
      ...payload,
      agent_id: payload.target_type === 'agent' ? (payload.agent_id || currentAgentId) : undefined,
    }
    const response = await skillMarketplaceService.installSkill(detail.skill.id, installPayload)
    toast.success(response.message)
    await loadMarketplace()
  }

  const onDownload = async (versionId?: number) => {
    if (!detail) return
    const payload = await skillMarketplaceService.downloadSkill(detail.skill.id, versionId)
    const url = URL.createObjectURL(payload.blob)
    const link = document.createElement('a')
    link.href = url
    link.download = payload.filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
    await loadMarketplace()
  }

  useEffect(() => {
    void loadMarketplace()
  }, [searchQuery])

  return (
    <div className="space-y-4" data-testid="user-agent-skill-marketplace">
      {detail || detailLoading ? (
        <>
          <Button variant="outline" onClick={closeSkillDetail} className="gap-2" data-testid="user-skill-detail-back">
            <ArrowLeft className="h-4 w-4" />
            Back to Marketplace
          </Button>

          {detailLoading && (
            <Card className="border border-border bg-card p-6">
              <div className="flex items-center gap-3 text-base text-muted-foreground">
                <Loader2 className="h-5 w-5 animate-spin" />
                Loading skill...
              </div>
            </Card>
          )}

          {detail && !detailLoading && (
            <SkillDetailPanel
              detail={detail}
              versions={versions}
              fileContent={fileContent}
              compareResult={compareResult}
              defaultAgentId={currentAgentId}
              onLoadVersionFile={onLoadVersionFile}
              onCompareVersions={onCompareVersions}
              onInstall={onInstall}
              onDownload={onDownload}
            />
          )}
        </>
      ) : (
        <>
          <Card className="border border-border bg-card p-4">
            <div className="flex flex-col gap-3 md:flex-row">
              <div className="relative flex-1">
                <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  data-testid="user-skills-search-input"
                  className="pl-9"
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value)}
                  placeholder="Search skills..."
                />
              </div>
              <Button variant="outline" onClick={() => loadMarketplace()} data-testid="user-skills-refresh-button">
                Refresh
              </Button>
            </div>
          </Card>

          <SkillMarketplaceGrid skills={skills} loading={loading} error={error} onOpenSkill={openSkill} />

          <SkillUploadForm
            submitLabel="Upload SKILL.md for review"
            onSubmit={async (formData) => {
              const response = await skillMarketplaceService.uploadSkill(formData)
              await loadMarketplace()
              toast.success(
                response.published
                  ? 'Skill published.'
                  : 'Skill submitted. It will appear after admin review.',
              )
              return response
            }}
          />
        </>
      )}
    </div>
  )
}
