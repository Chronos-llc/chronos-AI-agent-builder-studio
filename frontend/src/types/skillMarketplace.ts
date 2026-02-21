export type SkillSubmissionStatus =
  | 'draft'
  | 'pending_review'
  | 'under_review'
  | 'approved'
  | 'rejected'
  | 'quarantined'
  | 'published'

export type SkillScanStatus = 'pending' | 'benign' | 'suspicious' | 'malicious' | 'error'

export interface SkillMarketplaceItem {
  id: number
  name: string
  display_name: string
  description?: string | null
  category?: string | null
  icon?: string | null
  version?: string | null
  is_active: boolean
  is_premium: boolean
  install_count: number
  download_count: number
  submission_status: SkillSubmissionStatus
  visibility: string
  scan_status: SkillScanStatus
  scan_confidence: number
  scan_summary?: string | null
  publisher_username?: string | null
  published_at?: string | null
  created_at: string
  updated_at: string
}

export interface SkillMarketplaceListResponse {
  items: SkillMarketplaceItem[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

export interface SkillVersion {
  id: number
  skill_id: number
  version: string
  file_name: string
  file_path: string
  file_sha256: string
  is_current: boolean
  scan_status: SkillScanStatus
  scan_report_json?: Record<string, unknown> | null
  manifest_json?: Record<string, unknown> | null
  created_by?: number | null
  created_at: string
  updated_at: string
}

export interface SkillVersionListResponse {
  items: SkillVersion[]
  total: number
}

export interface SkillReviewEvent {
  id: number
  skill_id: number
  version_id?: number | null
  action: string
  actor_user_id?: number | null
  actor_username?: string | null
  payload: Record<string, unknown>
  created_at: string
}

export interface SkillMarketplaceDetailResponse {
  skill: SkillMarketplaceItem
  current_version?: SkillVersion | null
  events: SkillReviewEvent[]
}

export interface SkillFileContentResponse {
  skill_id: number
  version_id: number
  file_name: string
  raw_content: string
}

export interface SkillCompareResponse {
  skill_id: number
  base_version_id: number
  head_version_id: number
  diff_text: string
  added_lines: number
  removed_lines: number
}

export interface SkillUploadResponse {
  skill_id: number
  version_id: number
  submission_status: SkillSubmissionStatus
  scan_status: SkillScanStatus
  scan_confidence: number
  scan_summary: string
  published: boolean
}

export interface SkillScanResponse {
  skill_id: number
  version_id?: number | null
  scan_status: SkillScanStatus
  scan_confidence: number
  scan_summary: string
  scan_report: Record<string, unknown>
}

export interface SkillSubmissionDetailResponse {
  submission: SkillMarketplaceItem
  current_version?: SkillVersion | null
  events: SkillReviewEvent[]
}

export interface SkillSubmissionListResponse {
  items: SkillMarketplaceItem[]
  total: number
}

export interface SkillInstallRequest {
  target_type: 'agent' | 'fuzzy'
  agent_id?: number
  version_id?: number
}

export interface SkillInstallResponse {
  success: boolean
  message: string
  target_type: 'agent' | 'fuzzy'
  target_id?: number | null
  installation_id?: number | null
}
