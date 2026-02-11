import React, { useMemo, useState } from 'react'
import { cn } from '../../lib/utils'

export interface ProviderLogoProps {
  name: string
  url?: string | null
  size?: number
  className?: string
  imageClassName?: string
}

const initialsFromName = (name: string) =>
  name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map(part => part[0]?.toUpperCase() || '')
    .join('')

const isRemoteUrl = (value?: string | null) => Boolean(value && /^https?:\/\//i.test(value))

export const ProviderLogo: React.FC<ProviderLogoProps> = ({
  name,
  url,
  size = 28,
  className,
  imageClassName,
}) => {
  const [failed, setFailed] = useState(false)
  const initials = useMemo(() => initialsFromName(name), [name])
  const shouldRenderImage = isRemoteUrl(url) && !failed

  return (
    <div
      className={cn(
        'inline-flex items-center justify-center overflow-hidden rounded-full border border-white/20 bg-white/10 text-xs font-semibold text-white/90',
        className
      )}
      style={{ width: size, height: size, minWidth: size, minHeight: size }}
      title={name}
      aria-label={name}
    >
      {shouldRenderImage ? (
        <img
          src={url || ''}
          alt={name}
          loading="lazy"
          onError={() => setFailed(true)}
          className={cn('h-full w-full object-cover', imageClassName)}
        />
      ) : (
        <span>{initials || 'AI'}</span>
      )}
    </div>
  )
}
