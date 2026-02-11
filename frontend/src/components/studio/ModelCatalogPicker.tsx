import React, { useMemo, useState, useEffect } from 'react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { cn } from '../../lib/utils'
import type { ModelCatalogEntry, ModelCatalogProvider, ModelCapability } from '../../hooks/useModelCatalog'

interface ModelCatalogPickerProps {
  capability: ModelCapability
  providers: ModelCatalogProvider[]
  models: ModelCatalogEntry[]
  value?: string
  onChange: (model: string) => void
  providerId?: string
  onProviderChange?: (providerId: string) => void
  label?: string
  helperText?: string
  className?: string
  disabled?: boolean
}

const getProviderInitials = (name: string) => {
  const parts = name.split(' ').filter(Boolean)
  if (!parts.length) return name.slice(0, 2).toUpperCase()
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
}

const ProviderBadge: React.FC<{
  provider?: ModelCatalogProvider
  className?: string
}> = ({ provider, className }) => {
  if (!provider) {
    return (
      <div className={cn('h-6 w-6 rounded-full bg-muted/60 border border-border', className)} />
    )
  }

  if (provider.icon_url) {
    return (
      <img
        src={provider.icon_url}
        alt={provider.name}
        className={cn('h-6 w-6 rounded-full object-cover border border-border', className)}
      />
    )
  }

  return (
    <div
      className={cn(
        'h-6 w-6 rounded-full bg-muted/60 border border-border flex items-center justify-center text-[10px] font-semibold text-muted-foreground',
        className
      )}
    >
      {getProviderInitials(provider.name)}
    </div>
  )
}

export const ModelCatalogPicker: React.FC<ModelCatalogPickerProps> = ({
  capability,
  providers,
  models,
  value,
  onChange,
  providerId,
  onProviderChange,
  label,
  helperText,
  className,
  disabled,
}) => {
  const providerOptions = useMemo(() => {
    const providerMap = new Map(providers.map(p => [p.id, p]))
    const grouped = new Map<string, ModelCatalogEntry[]>()

    models.forEach(model => {
      if (!grouped.has(model.provider)) {
        grouped.set(model.provider, [])
      }
      grouped.get(model.provider)?.push(model)
    })

    return Array.from(grouped.entries()).map(([providerId, modelEntries]) => ({
      provider: providerMap.get(providerId),
      providerId,
      models: modelEntries.sort((a, b) => a.label.localeCompare(b.label)),
    }))
  }, [models, providers])

  const inferredProviderId = useMemo(() => {
    if (!value) return ''
    const match = models.find(model => model.model === value)
    return match?.provider || ''
  }, [models, value])

  const [selectedProviderId, setSelectedProviderId] = useState<string>(inferredProviderId)

  const resolvedProviderId = providerId ?? selectedProviderId

  useEffect(() => {
    if (!providerId && inferredProviderId && inferredProviderId !== selectedProviderId) {
      setSelectedProviderId(inferredProviderId)
    }
  }, [inferredProviderId, providerId, selectedProviderId])

  useEffect(() => {
    if (!resolvedProviderId && providerOptions.length) {
      const fallback = providerOptions[0].providerId
      if (providerId) {
        onProviderChange?.(fallback)
      } else {
        setSelectedProviderId(fallback)
      }
    }
  }, [providerOptions, resolvedProviderId, providerId, onProviderChange])

  const activeProvider = providers.find(p => p.id === resolvedProviderId)
  const activeModels = providerOptions.find(p => p.providerId === resolvedProviderId)?.models || []

  const showCurrent = value && !models.some(model => model.model === value)

  return (
    <div className={cn('space-y-2', className)}>
      {label && <label className="text-sm font-medium text-foreground">{label}</label>}

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <div className="space-y-1">
          <span className="text-xs uppercase tracking-wide text-muted-foreground">Provider</span>
          <Select
            disabled={disabled || !providerOptions.length}
            value={resolvedProviderId}
            onValueChange={(providerId) => {
              if (providerId) {
                if (providerId && onProviderChange) {
                  onProviderChange(providerId)
                } else {
                  setSelectedProviderId(providerId)
                }
              }
              const firstModel = providerOptions.find(p => p.providerId === providerId)?.models?.[0]
              if (firstModel) {
                onChange(firstModel.model)
              } else {
                onChange('')
              }
            }}
          >
            <SelectTrigger className="bg-card border-border text-foreground">
              <SelectValue placeholder={`Select ${capability} provider`}>
                <div className="flex items-center gap-2">
                  <ProviderBadge provider={activeProvider} />
                  <span className="truncate">{activeProvider?.name || 'Select provider'}</span>
                </div>
              </SelectValue>
            </SelectTrigger>
            <SelectContent className="bg-popover border-border text-foreground">
              {!providerOptions.length && (
                <SelectItem value="none" disabled>
                  Install a provider to see options
                </SelectItem>
              )}
              {providerOptions.map(option => (
                <SelectItem key={option.providerId} value={option.providerId}>
                  <div className="flex items-center gap-2">
                    <ProviderBadge provider={option.provider} />
                    <span>{option.provider?.name || option.providerId}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1">
          <span className="text-xs uppercase tracking-wide text-muted-foreground">Model</span>
          <Select
            disabled={disabled || !activeModels.length}
            value={value || ''}
            onValueChange={(modelId) => onChange(modelId)}
          >
            <SelectTrigger className="bg-card border-border text-foreground">
              <SelectValue placeholder={`Select ${capability} model`} />
            </SelectTrigger>
            <SelectContent className="bg-popover border-border text-foreground">
              {showCurrent && (
                <SelectItem value={value || ''}>
                  Current: {value}
                </SelectItem>
              )}
              {!activeModels.length && (
                <SelectItem value="none" disabled>
                  Install a provider to see models
                </SelectItem>
              )}
              {activeModels.map(model => (
                <SelectItem key={`${model.provider}-${model.model}`} value={model.model}>
                  {model.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {helperText && <p className="text-xs text-muted-foreground">{helperText}</p>}
    </div>
  )
}
