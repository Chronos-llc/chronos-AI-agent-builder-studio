export interface InstalledIntegration {
  integration_id: number
  name: string
  description?: string | null
  integration_type: string
  category: string
  icon?: string | null
  app_icon_url?: string | null
  version: string
  status: string
  visibility: string
  download_count: number
  rating: number
  review_count: number
  installed_count: number
  active_installed_count: number
  last_installed_at?: string | null
}

export interface InstalledIntegrationsResponse {
  items: InstalledIntegration[]
  total: number
}

export interface HubIntegration {
  id: number
  name: string
  description?: string | null
  integration_type: string
  category: string
  icon?: string | null
  app_icon_url?: string | null
  version: string
  status: string
  visibility: string
  download_count: number
  rating: number
  review_count: number
  subtitle?: string | null
}

export interface HubIntegrationsQuery {
  query?: string
  category?: string
  integration_type?: string
  sort_by?: 'popularity' | 'rating' | 'newest'
  page?: number
  page_size?: number
}
