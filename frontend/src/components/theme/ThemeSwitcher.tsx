import { cn } from '../../lib/utils'
import { useTheme } from '../../hooks/useTheme'

interface ThemeSwitcherProps {
  compact?: boolean
  className?: string
}

const themeOptions = [
  { id: 'light', label: 'Light' },
  { id: 'dark', label: 'Dark' },
  { id: 'system', label: 'System' },
] as const

const ThemeSwitcher: React.FC<ThemeSwitcherProps> = ({ compact = false, className }) => {
  const { theme, setTheme } = useTheme()

  return (
    <div
      className={cn(
        'inline-flex items-center rounded-lg border border-border bg-background p-1',
        className
      )}
    >
      {themeOptions.map((option) => {
        const active = theme === option.id
        return (
          <button
            key={option.id}
            type="button"
            className={cn(
              'rounded-md px-2 py-1 text-xs font-medium transition-colors',
              compact ? 'min-w-14' : 'min-w-16',
              active ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
            )}
            onClick={() => setTheme(option.id)}
          >
            {option.label}
          </button>
        )
      })}
    </div>
  )
}

export default ThemeSwitcher
