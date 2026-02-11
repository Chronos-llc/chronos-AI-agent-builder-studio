import React from 'react'
import { cn } from '../../lib/utils'

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
      <svg
        width={size}
        height={size}
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
        className={cn('shrink-0', markClassName)}
      >
        <defs>
          <linearGradient id="chronosOrbit" x1="10" y1="10" x2="56" y2="56" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#2DD4BF" />
            <stop offset="100%" stopColor="#38BDF8" />
          </linearGradient>
          <linearGradient id="chronosCore" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#0EA5E9" />
            <stop offset="100%" stopColor="#22D3EE" />
          </linearGradient>
        </defs>
        <path
          d="M46 17.5C41.9 13.2 36.2 10.5 30 10.5C17.8 10.5 8 20.3 8 32.5C8 44.7 17.8 54.5 30 54.5C36.5 54.5 42.4 51.8 46.6 47.3"
          stroke="url(#chronosOrbit)"
          strokeWidth="6"
          strokeLinecap="round"
        />
        <path
          d="M54 21C50.1 16.1 43.8 12.8 36.7 12.4"
          stroke="url(#chronosCore)"
          strokeWidth="3"
          strokeLinecap="round"
        />
        <circle cx="52" cy="14" r="4" fill="url(#chronosCore)" />
      </svg>

      {showWordmark && (
        <div className="flex items-baseline gap-1">
          <span className={cn('text-lg font-semibold tracking-tight', textClassName || 'text-foreground')}>
            Chronos
          </span>
          <span className="text-lg font-semibold tracking-tight bg-gradient-to-r from-cyan-400 to-sky-400 text-transparent bg-clip-text">
            AI
          </span>
        </div>
      )}
    </div>
  )
}
