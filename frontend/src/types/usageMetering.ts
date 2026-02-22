export type UsageResourceType =
  | 'ai_spend'
  | 'file_storage'
  | 'vector_db_storage'
  | 'table_rows'
  | 'collaborators'
  | 'agents'

export interface UsageResourceSnapshot {
  resource_type: UsageResourceType
  unit: string
  current: number
  base_limit: number | null
  addon_limit: number
  total_limit: number | null
  percent_used: number
  overage_units: number
  estimated_overage_monthly_usd: number
}

export interface UsageResourcesResponse {
  plan: string
  resources: UsageResourceSnapshot[]
  updated_at: string
}

export interface AgentUsageResourcesResponse {
  agent_id: number
  plan: string
  resources: UsageResourceSnapshot[]
  updated_at: string
}

export interface AddonAllocation {
  id: number
  user_id: number
  resource_type: UsageResourceType
  units: number
  unit_price_usd: number
  currency: string
  is_active: boolean
  effective_from: string
  effective_to?: string | null
  metadata?: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface AddonAllocationCreateRequest {
  user_id: number
  resource_type: UsageResourceType
  units: number
  unit_price_usd: number
  currency: string
  effective_from?: string
  effective_to?: string
  metadata?: Record<string, unknown>
}

