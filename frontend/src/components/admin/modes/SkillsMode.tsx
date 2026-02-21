import { useEffect, useMemo, useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../ui/tabs'
import { Card } from '../../ui/card'
import { Button } from '../../ui/button'
import { Input } from '../../ui/input'
import { Badge } from '../../ui/badge'
import { Alert, AlertDescription } from '../../ui/alert'
import { ArrowLeft, Loader2, RefreshCw, Search } from 'lucide-react'
import toast from 'react-hot-toast'
import { SkillMarketplaceGrid } from '../../skills/SkillMarketplaceGrid'
import { SkillDetailPanel } from '../../skills/SkillDetailPanel'
import { SkillUploadForm } from '../../skills/SkillUploadForm'
import { skillMarketplaceService } from '../../../services/skillMarketplaceService'
import { getSkillsStatistics } from '../../../services/skillsService'
import type {
  SkillCompareResponse,
  SkillFileContentResponse,
  SkillMarketplaceDetailResponse,
  SkillMarketplaceItem,
  SkillSubmissionListResponse,
  SkillVersion,
} from '../../../types/skillMarketplace'
import type { SkillStatistics } from '../../../types/skills'

type SkillsTab = 'marketplace' | 'review' | 'publish' | 'statistics'
interface SkillsModeProps {
  initialTab?: SkillsTab
  hideTabs?: boolean
}

const REVIEW_STATUSES = ['pending_review', 'under_review', 'approved', 'rejected', 'quarantined'] as const

const triggerDownload = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  window.URL.revokeObjectURL(url)
}

export const SkillsMode = ({ initialTab = 'marketplace', hideTabs = false }: SkillsModeProps) => {
  const [activeTab, setActiveTab] = useState<SkillsTab>(initialTab)
  const [searchQuery, setSearchQuery] = useState('')

  const [marketplaceItems, setMarketplaceItems] = useState<SkillMarketplaceItem[]>([])
  const [marketplaceLoading, setMarketplaceLoading] = useState(true)
  const [marketplaceError, setMarketplaceError] = useState<string | null>(null)

  const [submissionItems, setSubmissionItems] = useState<SkillSubmissionListResponse['items']>([])
  const [submissionLoading, setSubmissionLoading] = useState(true)
  const [submissionError, setSubmissionError] = useState<string | null>(null)

  const [selectedSkillId, setSelectedSkillId] = useState<number | null>(null)
  const [selectedDetail, setSelectedDetail] = useState<SkillMarketplaceDetailResponse | null>(null)
  const [selectedVersions, setSelectedVersions] = useState<SkillVersion[]>([])
  const [selectedFileContent, setSelectedFileContent] = useState<SkillFileContentResponse | null>(null)
  const [selectedCompare, setSelectedCompare] = useState<SkillCompareResponse | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)

  const [statistics, setStatistics] = useState<SkillStatistics | null>(null)
  const [statisticsLoading, setStatisticsLoading] = useState(true)
  const [statisticsError, setStatisticsError] = useState<string | null>(null)

  const summaryCounts = useMemo(() => {
    const counts: Record<string, number> = {}
    REVIEW_STATUSES.forEach((status) => {
      counts[status] = submissionItems.filter((item) => item.submission_status === status).length
    })
    return counts
  }, [submissionItems])

  const loadMarketplace = async () => {
    try {
      setMarketplaceLoading(true)
      setMarketplaceError(null)
      const payload = await skillMarketplaceService.listMarketplace({
        page: 1,
        page_size: 40,
        search_query: searchQuery || undefined,
        sort_by: 'created_at',
        sort_order: 'desc',
      })
      setMarketplaceItems(payload.items)
    } catch (error) {
      setMarketplaceError(error instanceof Error ? error.message : 'Failed to load marketplace skills.')
    } finally {
      setMarketplaceLoading(false)
    }
  }

  const loadSubmissions = async () => {
    try {
      setSubmissionLoading(true)
      setSubmissionError(null)
      const payload = await skillMarketplaceService.listSubmissions()
      setSubmissionItems(payload.items)
    } catch (error) {
      setSubmissionError(error instanceof Error ? error.message : 'Failed to load submissions.')
    } finally {
      setSubmissionLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      setStatisticsLoading(true)
      setStatisticsError(null)
      const stats = await getSkillsStatistics()
      setStatistics(stats)
    } catch (error) {
      setStatisticsError(error instanceof Error ? error.message : 'Failed to load skills statistics.')
    } finally {
      setStatisticsLoading(false)
    }
  }

  const openSkillDetail = async (skillId: number) => {
    setActiveTab('marketplace')
    setSelectedSkillId(skillId)
    setDetailLoading(true)
    setSelectedDetail(null)
    setSelectedVersions([])
    setSelectedFileContent(null)
    setSelectedCompare(null)
    try {
      const [detail, versions] = await Promise.all([
        skillMarketplaceService.getSkill(skillId),
        skillMarketplaceService.listVersions(skillId),
      ])
      setSelectedDetail(detail)
      setSelectedVersions(versions.items)
      setSelectedCompare(null)
      if (versions.items.length > 0) {
        const targetVersionId = detail.current_version?.id || versions.items[0].id
        const filePayload = await skillMarketplaceService.getVersionFile(skillId, targetVersionId)
        setSelectedFileContent(filePayload)
      } else {
        setSelectedFileContent(null)
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to open skill.')
    } finally {
      setDetailLoading(false)
    }
  }

  const closeSkillDetail = () => {
    setSelectedSkillId(null)
    setSelectedDetail(null)
    setSelectedVersions([])
    setSelectedFileContent(null)
    setSelectedCompare(null)
    setDetailLoading(false)
  }

  const handleLoadVersionFile = async (versionId: number) => {
    if (!selectedSkillId) return
    try {
      const filePayload = await skillMarketplaceService.getVersionFile(selectedSkillId, versionId)
      setSelectedFileContent(filePayload)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to load file content.')
    }
  }

  const handleCompareVersions = async (baseVersionId: number, headVersionId: number) => {
    if (!selectedSkillId) return
    try {
      const result = await skillMarketplaceService.compareVersions(selectedSkillId, baseVersionId, headVersionId)
      setSelectedCompare(result)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Version comparison failed.')
    }
  }

  const handleInstall = async (payload: { target_type: 'agent' | 'fuzzy'; agent_id?: number }) => {
    if (!selectedSkillId) return
    const response = await skillMarketplaceService.installSkill(selectedSkillId, payload)
    toast.success(response.message)
    await loadMarketplace()
  }

  const handleDownload = async (versionId?: number) => {
    if (!selectedSkillId) return
    const download = await skillMarketplaceService.downloadSkill(selectedSkillId, versionId)
    triggerDownload(download.blob, download.filename)
    await loadMarketplace()
  }

  const runSubmissionAction = async (
    skillId: number,
    action: () => Promise<unknown>,
    successMessage: string,
  ) => {
    try {
      await action()
      toast.success(successMessage)
      await Promise.all([loadSubmissions(), loadMarketplace()])
      if (selectedSkillId === skillId) {
        await openSkillDetail(skillId)
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Action failed.')
    }
  }

  useEffect(() => {
    void loadMarketplace()
  }, [searchQuery])

  useEffect(() => {
    void Promise.all([loadSubmissions(), loadStatistics()])
  }, [])

  useEffect(() => {
    setActiveTab(initialTab)
  }, [initialTab])

  return (
    <div className="space-y-6 text-[15px]" data-testid="admin-skills-mode">
      <div className="space-y-1">
        <h1 className="text-3xl font-bold">Skills Marketplace</h1>
        <p className="text-base text-muted-foreground">
          Publish, review, compare, download, and install SKILL.md packages.
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as SkillsTab)} data-testid="admin-skills-tabs">
        {!hideTabs && (
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="marketplace" data-testid="admin-skills-tab-marketplace">Marketplace</TabsTrigger>
            <TabsTrigger value="review" data-testid="admin-skills-tab-review">Review Uploaded Skills</TabsTrigger>
            <TabsTrigger value="publish" data-testid="admin-skills-tab-publish">Publish Skill</TabsTrigger>
            <TabsTrigger value="statistics" data-testid="admin-skills-tab-statistics">Statistics</TabsTrigger>
          </TabsList>
        )}

        <TabsContent value="marketplace" className="space-y-4">
          {selectedSkillId ? (
            <>
              <Button
                variant="outline"
                onClick={closeSkillDetail}
                className="gap-2"
                data-testid="admin-skill-detail-back"
              >
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

              {selectedDetail && !detailLoading && (
                <SkillDetailPanel
                  detail={selectedDetail}
                  versions={selectedVersions}
                  fileContent={selectedFileContent}
                  compareResult={selectedCompare}
                  allowFuzzyInstall
                  onLoadVersionFile={handleLoadVersionFile}
                  onCompareVersions={handleCompareVersions}
                  onInstall={handleInstall}
                  onDownload={handleDownload}
                />
              )}
            </>
          ) : (
            <>
              <Card className="border border-border bg-card p-4">
                <div className="flex flex-col gap-3 md:flex-row md:items-center">
                  <div className="relative flex-1">
                    <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      className="pl-9"
                      data-testid="admin-skills-search-input"
                      value={searchQuery}
                      onChange={(event) => setSearchQuery(event.target.value)}
                      placeholder="Search marketplace skills..."
                    />
                  </div>
                  <Button variant="outline" onClick={() => loadMarketplace()} className="gap-2" data-testid="admin-skills-refresh-marketplace">
                    <RefreshCw className="h-4 w-4" />
                    Refresh
                  </Button>
                </div>
              </Card>

              <SkillMarketplaceGrid
                skills={marketplaceItems}
                loading={marketplaceLoading}
                error={marketplaceError}
                onOpenSkill={openSkillDetail}
                emptyLabel="No published skills available yet."
              />
            </>
          )}
        </TabsContent>

        <TabsContent value="review" className="space-y-4">
          <Card className="border border-border bg-card p-4">
            <div className="flex flex-wrap gap-2 text-xs">
              {REVIEW_STATUSES.map((status) => (
                <Badge key={status} className="border-border bg-background/80 text-foreground">
                  {status.replace('_', ' ')}: {summaryCounts[status] || 0}
                </Badge>
              ))}
            </div>
          </Card>

          {submissionLoading ? (
            <Card className="border border-border bg-card p-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading submission queue...
              </div>
            </Card>
          ) : submissionError ? (
            <Alert variant="destructive">
              <AlertDescription>{submissionError}</AlertDescription>
            </Alert>
          ) : !submissionItems.length ? (
            <Card className="border border-border bg-card p-4 text-sm text-muted-foreground">
              No pending submissions.
            </Card>
          ) : (
            <div className="space-y-3">
              {submissionItems.map((item) => (
                <Card key={item.id} className="border border-border bg-card p-4" data-testid={`admin-review-row-${item.id}`}>
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="text-lg font-semibold text-foreground" data-testid={`admin-review-title-${item.id}`}>{item.display_name}</p>
                      <p className="text-sm text-muted-foreground">
                        Published by @{(item.publisher_username || 'jessenewt').replace(/^@+/, '') || 'jessenewt'} • {item.scan_status} • {item.submission_status}
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <Button size="sm" variant="outline" onClick={() => openSkillDetail(item.id)} data-testid={`admin-review-open-${item.id}`}>
                        Open
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        data-testid={`admin-review-scan-${item.id}`}
                        onClick={() => runSubmissionAction(item.id, () => skillMarketplaceService.scanSubmission(item.id), 'Scan completed')}
                      >
                        Scan
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        data-testid={`admin-review-approve-${item.id}`}
                        onClick={() =>
                          runSubmissionAction(
                            item.id,
                            () => skillMarketplaceService.reviewSubmission(item.id, 'approve'),
                            'Submission approved',
                          )
                        }
                      >
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        data-testid={`admin-review-reject-${item.id}`}
                        onClick={() =>
                          runSubmissionAction(
                            item.id,
                            () => skillMarketplaceService.reviewSubmission(item.id, 'reject'),
                            'Submission rejected',
                          )
                        }
                      >
                        Reject
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        data-testid={`admin-review-quarantine-${item.id}`}
                        onClick={() =>
                          runSubmissionAction(
                            item.id,
                            () => skillMarketplaceService.reviewSubmission(item.id, 'quarantine'),
                            'Submission quarantined',
                          )
                        }
                      >
                        Quarantine
                      </Button>
                      <Button
                        size="sm"
                        data-testid={`admin-review-publish-${item.id}`}
                        onClick={() => runSubmissionAction(item.id, () => skillMarketplaceService.publishSubmission(item.id), 'Submission published')}
                      >
                        Publish
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="publish" className="space-y-4">
          <SkillUploadForm
            submitLabel="Upload SKILL.md"
            onSubmit={async (formData) => {
              const result = await skillMarketplaceService.uploadSkill(formData)
              await Promise.all([loadMarketplace(), loadSubmissions()])
              return result
            }}
          />
        </TabsContent>

        <TabsContent value="statistics" className="space-y-4">
          {statisticsLoading ? (
            <Card className="border border-border bg-card p-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading statistics...
              </div>
            </Card>
          ) : statisticsError ? (
            <Alert variant="destructive">
              <AlertDescription>{statisticsError}</AlertDescription>
            </Alert>
          ) : statistics ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <Card className="border border-border bg-card p-4">
                <p className="text-sm text-muted-foreground">Total Skills</p>
                <p className="mt-1 text-2xl font-bold">{statistics.total_skills}</p>
              </Card>
              <Card className="border border-border bg-card p-4">
                <p className="text-sm text-muted-foreground">Active Skills</p>
                <p className="mt-1 text-2xl font-bold">{statistics.active_skills}</p>
              </Card>
              <Card className="border border-border bg-card p-4">
                <p className="text-sm text-muted-foreground">Installations</p>
                <p className="mt-1 text-2xl font-bold">{statistics.total_installations}</p>
              </Card>
            </div>
          ) : null}
        </TabsContent>
      </Tabs>
    </div>
  )
}
