import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUserProfile } from '../hooks/useUserProfile'

const API_BASE_URL_RAW = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const API_BASE_URL = API_BASE_URL_RAW.replace(/\/$/, '')

const POWER_PLANS = new Set(['lotus', 'team_developer', 'special_service', 'enterprise', 'pro'])

const getAccessToken = () => localStorage.getItem('chronos_access_token') || localStorage.getItem('access_token')

const buildHeaders = (withJsonContentType = false): HeadersInit => {
  const token = getAccessToken()
  const headers: Record<string, string> = {}
  if (withJsonContentType) {
    headers['Content-Type'] = 'application/json'
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }
  return headers
}

const FuzzyOnboardingPage = () => {
  const navigate = useNavigate()
  const {
    profile,
    onboardingStatus,
    onboardingStatusLoading,
    completeFuzzyOnboarding,
    completingFuzzyOnboarding,
    skipFuzzyOnboarding,
    skippingFuzzyOnboarding,
  } = useUserProfile()

  const [primaryGoal, setPrimaryGoal] = useState(profile?.primary_goal || '')
  const [useCases, setUseCases] = useState((profile?.use_cases || []).join(', '))
  const [toolsStack, setToolsStack] = useState((profile?.tools_stack || []).join(', '))
  const [error, setError] = useState<string | null>(null)

  const persona = useMemo(() => profile?.persona || onboardingStatus?.profile?.persona || null, [onboardingStatus, profile?.persona])

  useEffect(() => {
    if (onboardingStatusLoading || !onboardingStatus) return
    if (!onboardingStatus.onboarding_completed) {
      navigate('/app/onboarding/profile', { replace: true })
      return
    }
    if (onboardingStatus.fuzzy_onboarding_state === 'completed' || onboardingStatus.fuzzy_onboarding_state === 'skipped') {
      navigate('/app', { replace: true })
    }
  }, [navigate, onboardingStatus, onboardingStatusLoading])

  const resolvePostFuzzyRoute = async () => {
    const isPowerPersona = persona === 'power_user'
    let isPowerPlan = false
    try {
      const planResponse = await fetch(`${API_BASE_URL}/api/v1/usage/plan`, {
        credentials: 'include',
        headers: buildHeaders(),
      })
      if (planResponse.ok) {
        const planPayload = await planResponse.json()
        isPowerPlan = POWER_PLANS.has((planPayload?.plan_type || '').toLowerCase())
      }
    } catch {
      // no-op, fallback route below
    }

    if (isPowerPersona || isPowerPlan) {
      try {
        const agentsResponse = await fetch(`${API_BASE_URL}/api/v1/agents/?limit=1`, {
          credentials: 'include',
          headers: buildHeaders(),
        })
        if (agentsResponse.ok) {
          const agents = await agentsResponse.json()
          if (Array.isArray(agents) && agents.length > 0 && agents[0]?.id) {
            return `/app/agents/${agents[0].id}/suite`
          }
        }
      } catch {
        // no-op
      }
      return '/app/agents/new'
    }

    return '/app/agents'
  }

  const onComplete = async () => {
    setError(null)
    try {
      await completeFuzzyOnboarding({
        primary_goal: primaryGoal,
        use_cases: useCases ? useCases.split(',').map((item) => item.trim()).filter(Boolean) : undefined,
        tools_stack: toolsStack ? toolsStack.split(',').map((item) => item.trim()).filter(Boolean) : undefined,
      })
      navigate(await resolvePostFuzzyRoute())
    } catch (submitError: any) {
      setError(submitError?.message || 'Failed to complete fuzzy onboarding')
    }
  }

  const onSkip = async () => {
    setError(null)
    try {
      await skipFuzzyOnboarding()
      navigate(await resolvePostFuzzyRoute())
    } catch (submitError: any) {
      setError(submitError?.message || 'Failed to skip fuzzy onboarding')
    }
  }

  return (
    <div className="min-h-screen bg-[#06080D] px-6 py-10 text-white">
      <div className="mx-auto max-w-3xl space-y-6">
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <p className="text-xs uppercase tracking-[0.2em] text-white/50">Step 2 of 2</p>
          <h1 className="mt-2 text-2xl font-semibold">Fuzzy onboarding</h1>
          <p className="mt-2 text-sm text-white/70">
            Goals and use-cases help Fuzzy suggest agents and workflows. You can skip this for now.
          </p>
          <p className="mt-2 text-xs text-cyan-100/80">
            Routing after this step: power users go to Agent Suite; other users go to the main agent workspace.
          </p>
          <div className="mt-5 flex gap-2">
            <div className="h-2 flex-1 rounded-full bg-cyan-300/80" />
            <div className="h-2 flex-1 rounded-full bg-cyan-300/80" />
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <h2 className="text-lg font-medium">Goals and use cases</h2>
          <div className="mt-4 space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium">Primary goal</label>
              <textarea
                value={primaryGoal}
                onChange={(e) => setPrimaryGoal(e.target.value)}
                className="input min-h-28 w-full bg-black/30"
                placeholder="Describe what you want your agents to do daily."
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Use cases (comma separated)</label>
              <input
                value={useCases}
                onChange={(e) => setUseCases(e.target.value)}
                className="input w-full bg-black/30"
                placeholder="customer support, report automation, lead routing"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Tools stack (comma separated)</label>
              <input
                value={toolsStack}
                onChange={(e) => setToolsStack(e.target.value)}
                className="input w-full bg-black/30"
                placeholder="Slack, Notion, HubSpot"
              />
            </div>
          </div>

          {error && <p className="mt-3 text-sm text-red-300">{error}</p>}

          <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
            <button className="btn btn-secondary" disabled={skippingFuzzyOnboarding || completingFuzzyOnboarding} onClick={onSkip}>
              {skippingFuzzyOnboarding ? 'Skipping...' : 'Skip for now'}
            </button>
            <button
              className="btn btn-primary"
              disabled={completingFuzzyOnboarding || !primaryGoal}
              onClick={onComplete}
            >
              {completingFuzzyOnboarding ? 'Saving...' : 'Complete Fuzzy onboarding'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FuzzyOnboardingPage
