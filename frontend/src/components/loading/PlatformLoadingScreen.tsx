import React, { useEffect, useMemo, useState } from 'react'
import chronosMark from '../../assets/brand/chronos-mark.svg'
import { cn } from '../../lib/utils'
import { useTheme } from '../../hooks/useTheme'

export const DEFAULT_PLATFORM_LOADING_MESSAGES = [
  'Loading Studio',
  'Loading Studio Tools',
  'Loading Bot',
  'Opening Studio',
  'Loading custom components',
  'Initializing Agents',
  'Setting up virtual computers',
] as const

interface PlatformLoadingScreenProps {
  mode?: 'page' | 'overlay'
  messages?: readonly string[]
  stepIntervalMs?: number
  className?: string
}

const resolveMessages = (messages?: readonly string[]) =>
  messages && messages.length > 0 ? [...messages] : [...DEFAULT_PLATFORM_LOADING_MESSAGES]

export const PlatformLoadingScreen: React.FC<PlatformLoadingScreenProps> = ({
  mode = 'page',
  messages,
  stepIntervalMs = 3000,
  className,
}) => {
  const loadingMessages = useMemo(() => resolveMessages(messages), [messages])
  const [stepIndex, setStepIndex] = useState(0)
  const { resolvedTheme } = useTheme()

  useEffect(() => {
    setStepIndex(0)
  }, [loadingMessages])

  useEffect(() => {
    if (loadingMessages.length <= 1) return
    const timerId = window.setInterval(() => {
      setStepIndex(previous => (previous + 1) % loadingMessages.length)
    }, stepIntervalMs)

    return () => window.clearInterval(timerId)
  }, [loadingMessages, stepIntervalMs])

  const activeMessage = loadingMessages[stepIndex] || DEFAULT_PLATFORM_LOADING_MESSAGES[0]

  return (
    <section
      data-testid="platform-loading-screen"
      data-loading-mode={mode}
      className={cn(
        mode === 'overlay' ? 'fixed inset-0 z-[120]' : 'min-h-screen',
        resolvedTheme === 'dark' 
          ? 'overflow-hidden bg-[radial-gradient(circle_at_18%_18%,rgba(56,189,248,0.2),transparent_34%),radial-gradient(circle_at_82%_16%,rgba(34,211,238,0.15),transparent_42%),linear-gradient(165deg,#020409_0%,#050b16_52%,#021121_100%)] text-white'
          : 'overflow-hidden bg-[radial-gradient(circle_at_18%_18%,rgba(56,189,248,0.1),transparent_34%),radial-gradient(circle_at_82%_16%,rgba(34,211,238,0.08),transparent_42%),linear-gradient(165deg,#f8fafc_0%,#e0f2fe_52%,#bae6fd_100%)] text-slate-900',
        className,
      )}
    >
      <div className="relative flex min-h-screen w-full items-center justify-center px-6 py-10">
        <div className={cn(
          'pointer-events-none absolute -left-24 top-20 h-64 w-64 rounded-full blur-3xl',
          resolvedTheme === 'dark' ? 'bg-cyan-400/20' : 'bg-cyan-400/10'
        )} />
        <div className={cn(
          'pointer-events-none absolute -right-20 bottom-16 h-72 w-72 rounded-full blur-3xl',
          resolvedTheme === 'dark' ? 'bg-sky-500/15' : 'bg-sky-500/08'
        )} />

        <div className="relative z-10 flex w-full max-w-xl flex-col items-center gap-8 text-center">
          <div className="relative flex h-44 w-44 items-center justify-center">
            <div className={cn(
              'absolute inset-0 rounded-full border',
              resolvedTheme === 'dark' ? 'border-cyan-200/25' : 'border-cyan-300/35'
            )} />
            <div className={cn(
              'absolute inset-[10px] animate-spin rounded-full border-4 border-t-cyan-200 shadow-[0_0_25px_rgba(56,189,248,0.35)]',
              resolvedTheme === 'dark' ? 'border-cyan-400/20' : 'border-cyan-400/15'
            )} />
            <div className={cn(
              'absolute inset-[25px] rounded-full border bg-slate-950/70 backdrop-blur-md',
              resolvedTheme === 'dark' ? 'border-cyan-100/20' : 'border-cyan-200/30'
            )} />
            <img
              src={chronosMark}
              alt=""
              aria-hidden="true"
              className={cn(
                'relative z-10 h-16 w-16 object-contain drop-shadow-[0_0_20px_rgba(56,189,248,0.5)]'
              )}
            />
          </div>

          <div className="space-y-2">
            <p
              role="status"
              aria-live="polite"
              className={cn(
                'text-2xl font-semibold tracking-tight sm:text-3xl',
                resolvedTheme === 'dark' ? 'text-white' : 'text-slate-900'
              )}
            >
              {activeMessage}
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}

export default PlatformLoadingScreen
