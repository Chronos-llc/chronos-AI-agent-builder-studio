import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUserProfile, type UserPersona } from '../hooks/useUserProfile'

const PERSONAS: Array<{ id: UserPersona; label: string; description: string }> = [
  { id: 'developer', label: 'Developer', description: 'Build custom agents, connect code, and automate technical workflows.' },
  { id: 'power_user', label: 'Power User', description: 'Run daily operations and automate repetitive business tasks.' },
  { id: 'enterprise', label: 'Enterprise', description: 'Scale governance, team productivity, and enterprise orchestration.' },
]

const OnboardingPage = () => {
  const navigate = useNavigate()
  const { profile, completeOnboarding, completingOnboarding } = useUserProfile()

  const [step, setStep] = useState(1)
  const [persona, setPersona] = useState<UserPersona>('developer')
  const [githubUrl, setGithubUrl] = useState('')
  const [linkedinUrl, setLinkedinUrl] = useState('')
  const [roleTitle, setRoleTitle] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [industry, setIndustry] = useState('')
  const [teamSize, setTeamSize] = useState('')
  const [useCases, setUseCases] = useState('')
  const [toolsStack, setToolsStack] = useState('')
  const [primaryGoal, setPrimaryGoal] = useState('')
  const [error, setError] = useState<string | null>(null)

  const requiresGithub = persona === 'developer'
  const requiresLinkedin = persona !== 'developer'

  const personaTitle = useMemo(() => {
    return PERSONAS.find(item => item.id === persona)?.label || 'User'
  }, [persona])

  const onSubmit = async () => {
    setError(null)
    try {
      await completeOnboarding({
        persona,
        github_url: githubUrl || undefined,
        linkedin_url: linkedinUrl || undefined,
        role_title: roleTitle || undefined,
        company_name: companyName || undefined,
        industry: industry || undefined,
        team_size: teamSize || undefined,
        use_cases: useCases ? useCases.split(',').map(item => item.trim()).filter(Boolean) : undefined,
        tools_stack: toolsStack ? toolsStack.split(',').map(item => item.trim()).filter(Boolean) : undefined,
        primary_goal: primaryGoal,
      })
      navigate('/app')
    } catch (submitError: any) {
      setError(submitError?.message || 'Failed to complete onboarding')
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="card p-6">
        <h1 className="text-2xl font-semibold">Let&apos;s personalize your studio</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Share your role and goals so Fuzzy can recommend the right agents and workflows.
        </p>
        {profile?.onboarding_completed && (
          <p className="mt-3 text-sm text-emerald-400">Onboarding is complete. You can update your profile anytime.</p>
        )}
      </div>

      {step === 1 && (
        <div className="card space-y-4 p-6">
          <h2 className="text-lg font-medium">Step 1: Choose persona</h2>
          <div className="grid gap-3 md:grid-cols-3">
            {PERSONAS.map(item => (
              <button
                key={item.id}
                onClick={() => setPersona(item.id)}
                className={`rounded-xl border p-4 text-left transition ${
                  persona === item.id ? 'border-primary bg-primary/10' : 'border-border bg-card hover:border-primary/60'
                }`}
              >
                <div className="font-semibold">{item.label}</div>
                <div className="mt-2 text-xs text-muted-foreground">{item.description}</div>
              </button>
            ))}
          </div>
          <div className="flex justify-end">
            <button className="btn btn-primary" onClick={() => setStep(2)}>
              Continue
            </button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="card space-y-4 p-6">
          <h2 className="text-lg font-medium">Step 2: {personaTitle} profile context</h2>
          {requiresGithub && (
            <div>
              <label className="mb-1 block text-sm font-medium">GitHub URL</label>
              <input value={githubUrl} onChange={(e) => setGithubUrl(e.target.value)} className="input w-full" placeholder="https://github.com/username" />
            </div>
          )}
          {requiresLinkedin && (
            <div>
              <label className="mb-1 block text-sm font-medium">LinkedIn URL</label>
              <input value={linkedinUrl} onChange={(e) => setLinkedinUrl(e.target.value)} className="input w-full" placeholder="https://linkedin.com/in/username" />
            </div>
          )}
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium">Role title</label>
              <input value={roleTitle} onChange={(e) => setRoleTitle(e.target.value)} className="input w-full" placeholder="Engineering Manager" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Company</label>
              <input value={companyName} onChange={(e) => setCompanyName(e.target.value)} className="input w-full" placeholder="Chronos AI" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Industry</label>
              <input value={industry} onChange={(e) => setIndustry(e.target.value)} className="input w-full" placeholder="Software" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Team size</label>
              <input value={teamSize} onChange={(e) => setTeamSize(e.target.value)} className="input w-full" placeholder="11-50" />
            </div>
          </div>
          <div className="flex justify-between">
            <button className="btn btn-secondary" onClick={() => setStep(1)}>
              Back
            </button>
            <button className="btn btn-primary" onClick={() => setStep(3)}>
              Continue
            </button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="card space-y-4 p-6">
          <h2 className="text-lg font-medium">Step 3: Goals and use cases</h2>
          <div>
            <label className="mb-1 block text-sm font-medium">Primary goal</label>
            <textarea
              value={primaryGoal}
              onChange={(e) => setPrimaryGoal(e.target.value)}
              className="input min-h-28 w-full"
              placeholder="Describe what you want your agents to do daily."
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Use cases (comma separated)</label>
            <input
              value={useCases}
              onChange={(e) => setUseCases(e.target.value)}
              className="input w-full"
              placeholder="customer support, report automation, lead routing"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Tools stack (comma separated)</label>
            <input
              value={toolsStack}
              onChange={(e) => setToolsStack(e.target.value)}
              className="input w-full"
              placeholder="Slack, Notion, HubSpot"
            />
          </div>
          {error && <p className="text-sm text-red-400">{error}</p>}
          <div className="flex justify-between">
            <button className="btn btn-secondary" onClick={() => setStep(2)}>
              Back
            </button>
            <button
              className="btn btn-primary"
              disabled={completingOnboarding || !primaryGoal || (requiresGithub && !githubUrl) || (requiresLinkedin && !linkedinUrl)}
              onClick={onSubmit}
            >
              {completingOnboarding ? 'Saving...' : 'Complete Onboarding'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default OnboardingPage

