import React, { useMemo, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Building2, Mail } from 'lucide-react'
import { ChronosLogo } from '../components/brand/ChronosLogo'
import { useAuth } from '../contexts/AuthContext'
import { getProviderIcon } from '../config/iconRegistry'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000'

type AuthMethod = 'email' | 'enterprise'

const LoginPage: React.FC = () => {
  const location = useLocation()
  const isSignupMode = location.pathname === '/signup'
  const navigate = useNavigate()
  const { login, register } = useAuth()

  const [method, setMethod] = useState<AuthMethod>('email')
  const [email, setEmail] = useState('')
  const [enterpriseEmail, setEnterpriseEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false)
  const [acceptedPolicies, setAcceptedPolicies] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const minPasswordLength = 8
  const passwordTooShort = password.length > 0 && password.length < minPasswordLength
  const passwordConfirmMismatch =
    isSignupMode && passwordConfirm.length > 0 && password !== passwordConfirm

  const googleIcon = useMemo(() => getProviderIcon('google'), [])
  const githubIcon = useMemo(() => getProviderIcon('github'), [])

  const resolvePostLoginRoute = async (): Promise<string> => {
    const accessToken =
      localStorage.getItem('chronos_access_token') || localStorage.getItem('access_token')
    if (!accessToken) {
      return '/app'
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/session-context`, {
        headers: { Authorization: `Bearer ${accessToken}` },
        credentials: 'include',
      })
      if (!response.ok) {
        return '/app'
      }
      const payload = await response.json()
      if (payload?.is_admin && !payload?.is_impersonating) {
        return '/app/admin'
      }
      return '/app'
    } catch {
      return '/app'
    }
  }

  const requirePolicyAcceptance = (): boolean => {
    if (acceptedPolicies) return true
    setError('Please accept the Terms of Service and Privacy Policy to continue.')
    return false
  }

  const handleOAuth = (provider: 'google' | 'github') => {
    if (!requirePolicyAcceptance()) return
    window.location.href = `${API_BASE_URL}/api/v1/auth/oauth/${provider}/start?return_to=/app`
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!requirePolicyAcceptance()) return

    setLoading(true)
    setError(null)

    try {
      const selectedEmail = method === 'enterprise' ? enterpriseEmail.trim() : email.trim()

      if (!selectedEmail) {
        throw new Error('Email is required')
      }

      if (isSignupMode) {
        const resolvedUsername = selectedEmail.split('@')[0]
        await register({
          email: selectedEmail,
          username: resolvedUsername,
          password,
          password_confirm: passwordConfirm,
        })
        await login(selectedEmail, password)
      } else {
        await login(selectedEmail, password)
      }

      navigate(await resolvePostLoginRoute())
    } catch (submitError: any) {
      setError(submitError?.message || 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0d13] text-white">
      <div className="mx-auto flex min-h-screen w-full max-w-md flex-col px-5 py-6 sm:px-7">
        <header className="flex items-center gap-3">
          <ChronosLogo showWordmark={false} size={28} />
          <div className="text-base font-semibold">Chronos Studio</div>
        </header>

        <main className="flex flex-1 flex-col justify-center">
          <div className="space-y-2 text-center">
            <h1 className="text-3xl font-semibold tracking-tight">
              {isSignupMode ? 'Create an account' : 'Sign in'}
            </h1>
            <p className="text-sm text-white/60">
              {isSignupMode
                ? 'Get your AI workspace started in minutes.'
                : 'Sign in or create an account to get started.'}
            </p>
          </div>

          <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.02] p-2">
            <div className="grid grid-cols-2 gap-2">
              <Link
                to="/login"
                className={`rounded-xl px-3 py-2 text-center text-sm font-medium transition ${
                  !isSignupMode ? 'bg-cyan-300 text-[#081018]' : 'text-white/75 hover:bg-white/5'
                }`}
              >
                Sign in
              </Link>
              <Link
                to="/signup"
                className={`rounded-xl px-3 py-2 text-center text-sm font-medium transition ${
                  isSignupMode ? 'bg-cyan-300 text-[#081018]' : 'text-white/75 hover:bg-white/5'
                }`}
              >
                Sign up
              </Link>
            </div>
          </div>

          <div className="mt-5 space-y-2">
            <button
              type="button"
              onClick={() => handleOAuth('google')}
              data-testid="auth-oauth-google"
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 bg-black/50 px-4 py-3 text-sm text-white transition hover:bg-black/70"
            >
              {googleIcon?.url ? (
                <img src={googleIcon.url} alt="" aria-hidden="true" className="h-4 w-4 object-contain" />
              ) : (
                <span className="inline-flex h-4 w-4 items-center justify-center rounded-full bg-white text-[10px] font-semibold text-black">G</span>
              )}
              Continue with Google
            </button>

            <button
              type="button"
              onClick={() => handleOAuth('github')}
              data-testid="auth-oauth-github"
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 bg-black/50 px-4 py-3 text-sm text-white transition hover:bg-black/70"
            >
              {githubIcon?.url ? (
                <img src={githubIcon.url} alt="" aria-hidden="true" className="h-4 w-4 object-contain" />
              ) : (
                <span className="inline-flex h-4 w-4 items-center justify-center rounded-full bg-white text-[10px] font-semibold text-black">GH</span>
              )}
              Continue with GitHub
            </button>

            <button
              type="button"
              onClick={() => setMethod('email')}
              data-testid="auth-method-email"
              className={`flex w-full items-center justify-center gap-2 rounded-xl border px-4 py-3 text-sm transition ${
                method === 'email'
                  ? 'border-cyan-300/50 bg-cyan-300/10 text-cyan-100'
                  : 'border-white/10 bg-black/50 text-white hover:bg-black/70'
              }`}
            >
              <Mail className="h-4 w-4" />
              Continue with Email
            </button>
          </div>

          <div className="my-4 flex items-center gap-4">
            <div className="h-px flex-1 bg-white/10" />
            <span className="text-xs text-white/40">or</span>
            <div className="h-px flex-1 bg-white/10" />
          </div>

          <button
            type="button"
            onClick={() => setMethod('enterprise')}
            data-testid="auth-method-enterprise"
            className={`flex w-full items-center justify-center gap-2 rounded-xl border px-4 py-3 text-sm transition ${
              method === 'enterprise'
                ? 'border-cyan-300/50 bg-cyan-300/10 text-cyan-100'
                : 'border-white/10 bg-black/50 text-white hover:bg-black/70'
            }`}
          >
            <Building2 className="h-4 w-4" />
            Enterprise SSO
          </button>

          <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
            {method === 'enterprise' ? (
              <div>
                <label htmlFor="enterprise-email" className="text-sm text-white/75">
                  Enterprise email
                </label>
                <input
                  id="enterprise-email"
                  name="enterpriseEmail"
                  type="email"
                  data-testid="auth-enterprise-email"
                  required
                  className="mt-2 w-full rounded-xl border border-white/10 bg-[#121721] px-4 py-3 text-sm text-white placeholder-white/35 focus:outline-none focus:ring-2 focus:ring-cyan-400/60"
                  placeholder="name@company.com"
                  value={enterpriseEmail}
                  onChange={(e) => setEnterpriseEmail(e.target.value)}
                />
              </div>
            ) : (
              <div>
                <label htmlFor="email" className="text-sm text-white/75">
                  Email
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  data-testid="auth-email-input"
                  required
                  className="mt-2 w-full rounded-xl border border-white/10 bg-[#121721] px-4 py-3 text-sm text-white placeholder-white/35 focus:outline-none focus:ring-2 focus:ring-cyan-400/60"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            )}

            <div>
              <label htmlFor="password" className="text-sm text-white/75">
                Password
              </label>
              <div className="relative mt-2">
                <input
                  id="password"
                  name="password"
                  data-testid="auth-password-input"
                  type={showPassword ? 'text' : 'password'}
                  required
                  autoComplete={isSignupMode ? 'new-password' : 'current-password'}
                  className="w-full rounded-xl border border-white/10 bg-[#121721] px-4 py-3 pr-20 text-sm text-white placeholder-white/35 focus:outline-none focus:ring-2 focus:ring-cyan-400/60"
                  placeholder="********"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md border border-white/20 px-2 py-1 text-xs text-white/75 hover:bg-white/10"
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
              {passwordTooShort && (
                <p className="mt-1 text-xs text-amber-300">
                  Password should be at least {minPasswordLength} characters.
                </p>
              )}
            </div>

            {isSignupMode && (
              <div>
                <label htmlFor="password-confirm" className="text-sm text-white/75">
                  Confirm password
                </label>
                <div className="relative mt-2">
                  <input
                    id="password-confirm"
                    name="passwordConfirm"
                    data-testid="auth-password-confirm-input"
                    type={showPasswordConfirm ? 'text' : 'password'}
                    required
                    autoComplete="new-password"
                    className="w-full rounded-xl border border-white/10 bg-[#121721] px-4 py-3 pr-20 text-sm text-white placeholder-white/35 focus:outline-none focus:ring-2 focus:ring-cyan-400/60"
                    placeholder="********"
                    value={passwordConfirm}
                    onChange={(e) => setPasswordConfirm(e.target.value)}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPasswordConfirm((prev) => !prev)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md border border-white/20 px-2 py-1 text-xs text-white/75 hover:bg-white/10"
                  >
                    {showPasswordConfirm ? 'Hide' : 'Show'}
                  </button>
                </div>
                {passwordConfirmMismatch && (
                  <p className="mt-1 text-xs text-amber-300">Passwords do not match yet.</p>
                )}
              </div>
            )}

            <label className="flex items-start gap-2 text-xs text-white/60">
              <input
                type="checkbox"
                data-testid="auth-terms-checkbox"
                className="mt-0.5 h-3.5 w-3.5 rounded border-white/25 bg-transparent accent-cyan-400"
                checked={acceptedPolicies}
                onChange={(e) => {
                  setAcceptedPolicies(e.target.checked)
                  if (e.target.checked) setError(null)
                }}
              />
              <span>
                By checking this box, I agree to the{' '}
                <Link to="/terms" className="text-cyan-200 underline underline-offset-2 hover:text-cyan-100">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link to="/privacy" className="text-cyan-200 underline underline-offset-2 hover:text-cyan-100">
                  Privacy Policy
                </Link>
                .
              </span>
            </label>

            {error && (
              <div className="rounded-lg border border-rose-500/35 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">
                {error}
              </div>
            )}

            <button
              type="submit"
              data-testid="auth-submit-button"
              disabled={loading}
              className="w-full rounded-xl bg-cyan-300 px-4 py-3 text-sm font-semibold text-[#081018] transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading
                ? 'Please wait...'
                : isSignupMode
                  ? method === 'enterprise'
                    ? 'Create enterprise account'
                    : 'Create account'
                  : method === 'enterprise'
                    ? 'Sign in with Enterprise SSO'
                    : 'Sign in with Email'}
            </button>
          </form>
        </main>
      </div>
    </div>
  )
}

export default LoginPage
