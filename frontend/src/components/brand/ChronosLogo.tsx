import React from 'react'
import { cn } from '../../lib/utils'
import chronosMark from '../../assets/brand/chronos-mark.svg'

interface ChronosLogoProps {
  className?: string
  markClassName?: string
  textClassName?: string
  size?: number
  showWordmark?: boolean
}

export const ChronosLogo: React.FC<ChronosLogoProps> = ({
  className,
  markClassName,
  textClassName,
  size = 36,
  showWordmark = true,
}) => {
  return (
    <div className={cn('flex items-center gap-3', className)}>
      <img
        src={chronosMark}
        alt=""
        aria-hidden="true"
        width={size}
        height={size}
        className={cn('chronos-logo-mark shrink-0 object-contain', markClassName)}
      />

      {showWordmark && (
        <div className="flex items-baseline gap-1">
          <span className={cn('text-lg font-semibold tracking-tight', textClassName || 'text-foreground')}>
            Chronos
          </span>
          <span className="bg-gradient-to-r from-cyan-400 to-sky-400 bg-clip-text text-lg font-semibold tracking-tight text-transparent">
            AI
          </span>
        </div>
      )}
    </div>
  )
}
