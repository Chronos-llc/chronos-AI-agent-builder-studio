import { useQuery } from '@tanstack/react-query'

export type ModelCapability = 'chat' | 'translation' | 'image' | 'video' | 'stt' | 'tts' | 'voice'

export interface ModelCatalogEntry {
  provider: string
  model: string
  label: string
}

export interface ModelCatalogProvider {
  id: string
  name: string
  installed: boolean
  available: boolean
  default_env_key?: string
  has_default_key?: boolean
  capabilities: string[]
}

export interface ModelCatalogResponse {
  providers: ModelCatalogProvider[]
  models: Record<ModelCapability, ModelCatalogEntry[]>
}

export interface ModelGroup {
  provider: string
  label: string
  models: ModelCatalogEntry[]
}

export const groupModelsByProvider = (
  models: ModelCatalogEntry[],
  providers: ModelCatalogProvider[]
): ModelGroup[] => {
  const providerNames = new Map(providers.map(provider => [provider.id, provider.name]))
  const grouped = new Map<string, ModelCatalogEntry[]>()

  models.forEach(model => {
    if (!grouped.has(model.provider)) {
      grouped.set(model.provider, [])
    }
    grouped.get(model.provider)?.push(model)
  })

  return Array.from(grouped.entries())
    .map(([provider, entries]) => ({
      provider,
      label: providerNames.get(provider) || provider,
      models: entries.sort((a, b) => a.label.localeCompare(b.label))
    }))
    .sort((a, b) => a.label.localeCompare(b.label))
}

export const useModelCatalog = () => {
  return useQuery<ModelCatalogResponse>({
    queryKey: ['model-catalog'],
    queryFn: async () => {
      const response = await fetch('/api/v1/ai/catalog')
      if (!response.ok) {
        throw new Error('Failed to fetch model catalog')
      }
      return response.json()
    }
  })
}
