import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUserProfile, type UserPersona } from '../hooks/useUserProfile'
import { Checkbox } from '../components/ui/checkbox'

const PERSONAS: Array<{ id: UserPersona; label: string; description: string }> = [
  { id: 'developer', label: 'Developer', description: 'Build custom agents, connect code, and automate technical workflows.' },
  { id: 'power_user', label: 'Power User', description: 'Run daily operations and automate repetitive business tasks.' },
  { id: 'enterprise', label: 'Enterprise', description: 'Scale governance, team productivity, and enterprise orchestration.' },
]

const ProfileOnboardingPage = () => {
  const navigate = useNavigate()
  const {
    profile,
    onboardingStatus,
    onboardingStatusLoading,
    completeProfileOnboarding,
    completingProfileOnboarding,
  } = useUserProfile()

  const [step, setStep] = useState(1)
  const [persona, setPersona] = useState<UserPersona>((profile?.persona as UserPersona) || 'developer')
  const [githubUrl, setGithubUrl] = useState(profile?.github_url || '')
  const [linkedinUrl, setLinkedinUrl] = useState(profile?.linkedin_url || '')
  const [roleTitle, setRoleTitle] = useState(profile?.role_title || '')
  const [companyName, setCompanyName] = useState(profile?.company_name || '')
  const [industry, setIndustry] = useState(profile?.industry || '')
  const [teamSize, setTeamSize] = useState(profile?.team_size || '')
  const [consentAccepted, setConsentAccepted] = useState(false)
  const [consentTouched, setConsentTouched] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const requiresGithub = persona === 'developer'
  const requiresLinkedin = persona !== 'developer'

  const personaTitle = useMemo(() => {
    return PERSONAS.find((item) => item.id === persona)?.label || 'User'
  }, [persona])

  useEffect(() => {
    if (onboardingStatusLoading || !onboardingStatus) return
    if (!onboardingStatus.onboarding_completed) return
    if (onboardingStatus.fuzzy_onboarding_state === 'pending') {
      navigate('/app/onboarding/fuzzy', { replace: true })
      return
    }
    navigate('/app', { replace: true })
  }, [navigate, onboardingStatus, onboardingStatusLoading])

  const onSubmit = async () => {
    setError(null)
    setConsentTouched(true)
    if (!consentAccepted) {
      setError('Please accept the profile context sharing prompt before continuing.')
      return
    }
    try {
      await completeProfileOnboarding({
        persona,
        github_url: githubUrl || undefined,
        linkedin_url: linkedinUrl || undefined,
        role_title: roleTitle || undefined,
        company_name: companyName || undefined,
        industry: industry || undefined,
        team_size: teamSize || undefined,
      })
      navigate('/app/onboarding/fuzzy')
    } catch (submitError: any) {
      setError(submitError?.message || 'Failed to complete profile onboarding')
    }
  }

  return (
    <div className="min-h-screen bg-background px-6 py-10 text-foreground">
      <div className="mx-auto max-w-3xl space-y-6">
        <div className="rounded-2xl border border-border bg-card p-6">
          <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Step 1 of 2</p>
          <h1 className="mt-2 text-2xl font-semibold">Profile onboarding</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Set your profile context first. Fuzzy onboarding comes next and can be skipped.
          </p>
          <div className="mt-5 flex gap-2">
            <div className="h-2 flex-1 rounded-full bg-cyan-300/80" />
            <div className="h-2 flex-1 rounded-full bg-muted" />
          </div>
        </div>

        {step === 1 && (
          <div className="rounded-2xl border border-border bg-card p-6">
            <h2 className="text-lg font-medium">Choose persona</h2>
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              {PERSONAS.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setPersona(item.id)}
                  className={`rounded-xl border p-4 text-left transition ${
                    persona === item.id ? 'border-cyan-300/60 bg-cyan-300/10' : 'border-border bg-background hover:border-cyan-300/40'
                  }`}
                >
                  <div className="font-semibold">{item.label}</div>
                  <div className="mt-2 text-xs text-muted-foreground">{item.description}</div>
                </button>
              ))}
            </div>
            <div className="mt-6 flex justify-end">
              <button className="btn btn-primary" onClick={() => setStep(2)}>
                Continue
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="rounded-2xl border border-border bg-card p-6">
            <h2 className="text-lg font-medium">{personaTitle} profile context</h2>
            <p className="mt-1 text-sm text-muted-foreground">This context improves agent and workflow recommendations.</p>

            <div className="mt-4 space-y-4">
              {requiresGithub && (
                <div>
                  <label className="mb-1 block text-sm font-medium">GitHub URL</label>
                  <input
                    value={githubUrl}
                    onChange={(e) => setGithubUrl(e.target.value)}
                    className="input w-full"
                    placeholder="https://github.com/username"
                  />
                </div>
              )}
              {requiresLinkedin && (
                <div>
                  <label className="mb-1 block text-sm font-medium">LinkedIn URL</label>
                  <input
                    value={linkedinUrl}
                    onChange={(e) => setLinkedinUrl(e.target.value)}
                    className="input w-full"
                    placeholder="https://linkedin.com/in/username"
                  />
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
            </div>

            <div className="mt-5 rounded-xl border border-cyan-300/30 bg-cyan-300/10 px-3 py-2 text-xs text-cyan-900 dark:text-cyan-100">
              Continuing shares your profile context with Fuzzy so it can recommend more personalized agents and workflows.
            </div>
            <div className="mt-3 rounded-xl border border-border bg-muted/30 px-3 py-2">
              <label className="flex items-start gap-2 text-sm">
                <Checkbox
                  checked={consentAccepted}
                  onCheckedChange={(checked) => {
                    setConsentAccepted(checked)
                    setConsentTouched(true)
                  }}
                  className="mt-0.5"
                />
                <span>
                  I agree to share this profile context with Fuzzy for personalized recommendations.
                </span>
              </label>
              {consentTouched && !consentAccepted && (
                <p className="mt-2 text-xs text-red-400">
                  You must accept this prompt before continuing.
                </p>
              )}
            </div>

            {error && <p className="mt-3 text-sm text-red-300">{error}</p>}

            <div className="mt-6 flex justify-between">
              <button className="btn btn-secondary" onClick={() => setStep(1)}>
                Back
              </button>
              <button
                className="btn btn-primary"
                disabled={
                  completingProfileOnboarding ||
                  !consentAccepted ||
                  (requiresGithub && !githubUrl) ||
                  (requiresLinkedin && !linkedinUrl)
                }
                onClick={onSubmit}
              >
                {completingProfileOnboarding ? 'Saving...' : 'Continue to Fuzzy setup'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ProfileOnboardingPage
