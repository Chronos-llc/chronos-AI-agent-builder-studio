import React from 'react'
import { Check, Laptop, Moon, Sun } from 'lucide-react'
import { useTheme } from '../../hooks/useTheme'
import { cn } from '../../lib/utils'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu'

const options = [
  { id: 'light', label: 'Light', icon: Sun },
  { id: 'dark', label: 'Dark', icon: Moon },
  { id: 'system', label: 'System', icon: Laptop },
] as const

export const LandingThemeToggle: React.FC = () => {
  const { theme, resolvedTheme, setTheme } = useTheme()

  const CurrentIcon = resolvedTheme === 'dark' ? Moon : Sun

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          aria-label="Theme settings"
          className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-white/20 bg-white/5 text-white/80 transition hover:border-white/40 hover:text-white"
        >
          <CurrentIcon className="h-4 w-4" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="min-w-[9.5rem] border-white/20 bg-[#0D1421] text-white">
        {options.map((option) => {
          const Icon = option.icon
          const active = theme === option.id
          return (
            <DropdownMenuItem
              key={option.id}
              onClick={() => setTheme(option.id)}
              className={cn('justify-between text-white/90 hover:bg-white/10 hover:text-white', active && 'bg-white/10')}
            >
              <span className="inline-flex items-center gap-2">
                <Icon className="h-4 w-4" />
                {option.label}
              </span>
              {active ? <Check className="h-4 w-4 text-cyan-200" /> : null}
            </DropdownMenuItem>
          )
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
