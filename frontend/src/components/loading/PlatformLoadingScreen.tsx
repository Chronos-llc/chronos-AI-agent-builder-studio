import React, { useEffect, useMemo, useState } from 'react'
import chronosMark from '../../assets/brand/chronos-mark.svg'
import { cn } from '../../lib/utils'

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
  /** Single static message to display (overrides rotating messages when provided) */
  message?: string
  messages?: readonly string[]
  stepIntervalMs?: number
  className?: string
}

const resolveMessages = (messages?: readonly string[]) =>
  messages && messages.length > 0 ? [...messages] : [...DEFAULT_PLATFORM_LOADING_MESSAGES]

export const PlatformLoadingScreen: React.FC<PlatformLoadingScreenProps> = ({
  mode = 'page',
  message,
  messages,
  stepIntervalMs = 1600,
  className,
}) => {
  const loadingMessages = useMemo(() => resolveMessages(messages), [messages])
  const [stepIndex, setStepIndex] = useState(0)

  useEffect(() => {
    setStepIndex(0)
  }, [loadingMessages])

  useEffect(() => {
    if (message || loadingMessages.length <= 1) return
    const timerId = window.setInterval(() => {
      setStepIndex(previous => (previous + 1) % loadingMessages.length)
    }, stepIntervalMs)

    return () => window.clearInterval(timerId)
  }, [message, loadingMessages, stepIntervalMs])

  const activeMessage = message || loadingMessages[stepIndex] || DEFAULT_PLATFORM_LOADING_MESSAGES[0]

  return (
    <section
      data-testid="platform-loading-screen"
      data-loading-mode={mode}
      className={cn(
        mode === 'overlay' ? 'fixed inset-0 z-[120]' : 'min-h-screen',
        'overflow-hidden bg-[radial-gradient(circle_at_18%_18%,rgba(56,189,248,0.2),transparent_34%),radial-gradient(circle_at_82%_16%,rgba(34,211,238,0.15),transparent_42%),linear-gradient(165deg,#020409_0%,#050b16_52%,#021121_100%)] text-white',
        className,
      )}
    >
      <div className="relative flex min-h-screen w-full items-center justify-center px-6 py-10">
        <div className="pointer-events-none absolute -left-24 top-20 h-64 w-64 rounded-full bg-cyan-400/20 blur-3xl" />
        <div className="pointer-events-none absolute -right-20 bottom-16 h-72 w-72 rounded-full bg-sky-500/15 blur-3xl" />

        <div className="relative z-10 flex w-full max-w-xl flex-col items-center gap-8 text-center">
          <div className="relative flex h-44 w-44 items-center justify-center">
            <div className="absolute inset-0 rounded-full border border-cyan-200/25" />
            <div className="absolute inset-[10px] animate-spin rounded-full border-4 border-cyan-400/20 border-t-cyan-200 shadow-[0_0_25px_rgba(56,189,248,0.35)]" />
            <div className="absolute inset-[25px] rounded-full border border-cyan-100/20 bg-slate-950/70 backdrop-blur-md" />
            <img
              src={chronosMark}
              alt=""
              aria-hidden="true"
              className="relative z-10 h-16 w-16 object-contain drop-shadow-[0_0_20px_rgba(56,189,248,0.5)]"
            />
          </div>

          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.32em] text-cyan-100/70">Chronos Studio</p>
            <p
              role="status"
              aria-live="polite"
              className="text-2xl font-semibold tracking-tight text-white sm:text-3xl"
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
