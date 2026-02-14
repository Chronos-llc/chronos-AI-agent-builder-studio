import React, { useMemo, useState } from 'react'
import { useNavigate, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { ChronosLogo } from '../components/brand/ChronosLogo'
import { ProviderLogo } from '../components/brand/ProviderLogo'
import { getProviderIcon } from '../config/iconRegistry'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000'

const LoginPage: React.FC = () => {
    const location = useLocation()
    const isSignupMode = location.pathname === '/signup'
    const navigate = useNavigate()
    const { login, register } = useAuth()

    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [username, setUsername] = useState('')
    const [fullName, setFullName] = useState('')
    const [passwordConfirm, setPasswordConfirm] = useState('')
    const [showPassword, setShowPassword] = useState(false)
    const [showPasswordConfirm, setShowPasswordConfirm] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const minPasswordLength = 8
    const passwordTooShort = password.length > 0 && password.length < minPasswordLength
    const passwordConfirmMismatch =
        isSignupMode &&
        passwordConfirm.length > 0 &&
        password !== passwordConfirm

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
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                },
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

    const handleOAuth = (provider: 'google' | 'github') => {
        window.location.href = `${API_BASE_URL}/api/v1/auth/oauth/${provider}/start?return_to=/app`
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        try {
            if (isSignupMode) {
                const resolvedUsername = username.trim() || email.split('@')[0]
                await register({
                    email,
                    username: resolvedUsername,
                    full_name: fullName.trim() || undefined,
                    password,
                    password_confirm: passwordConfirm,
                })
                await login(email, password)
                navigate(await resolvePostLoginRoute())
                return
            }

            await login(email, password)
            navigate(await resolvePostLoginRoute())
        } catch (submitError: any) {
            setError(submitError?.message || 'Authentication failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-[#0B1016] text-white flex items-center justify-center px-6 py-12">
            <div className="w-full max-w-5xl grid gap-10 md:grid-cols-[1.1fr_0.9fr] items-center">
                <div className="space-y-6">
                    <ChronosLogo textClassName="text-white" markClassName="text-white" />
                    <h1 className="text-4xl font-semibold leading-tight">
                        Build, launch, and orchestrate agents with Chronos AI.
                    </h1>
                    <p className="text-white/70">
                        Centralize your model catalog, tools, and voice pipelines in a single studio built for teams.
                    </p>
                    <div className="flex flex-wrap gap-3 text-sm text-white/60">
                        {['Multi-agent orchestration', 'Voice + STT/TTS', 'Enterprise-ready controls'].map(item => (
                            <span key={item} className="rounded-full border border-white/10 px-3 py-1">
                                {item}
                            </span>
                        ))}
                    </div>
                </div>

                <div className="rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/30 backdrop-blur">
                    <div className="mb-4 flex items-center gap-2">
                        <Link
                            to="/login"
                            className={`rounded-full px-4 py-2 text-sm ${!isSignupMode ? 'bg-cyan-400 text-[#0B1016] font-semibold' : 'border border-white/20 text-white/80'}`}
                        >
                            Sign in
                        </Link>
                        <Link
                            to="/signup"
                            className={`rounded-full px-4 py-2 text-sm ${isSignupMode ? 'bg-cyan-400 text-[#0B1016] font-semibold' : 'border border-white/20 text-white/80'}`}
                        >
                            Sign up
                        </Link>
                    </div>

                    <h2 className="text-2xl font-semibold">{isSignupMode ? 'Create account' : 'Sign in'}</h2>
                    <p className="mt-2 text-sm text-white/70">
                        {isSignupMode
                            ? 'Create your Chronos Studio account to start building.'
                            : 'Use your Chronos Studio credentials to continue.'}
                    </p>

                    <div className="mt-6 grid gap-3">
                        <button
                            type="button"
                            onClick={() => handleOAuth('google')}
                            className="inline-flex w-full items-center justify-center gap-2 rounded-full border border-white/20 bg-white/5 px-4 py-2.5 text-sm font-medium text-white hover:bg-white/10"
                        >
                            <ProviderLogo name="Google" url={googleIcon?.url} size={20} className="border-white/30" />
                            Continue with Google
                        </button>
                        <button
                            type="button"
                            onClick={() => handleOAuth('github')}
                            className="inline-flex w-full items-center justify-center gap-2 rounded-full border border-white/20 bg-white/5 px-4 py-2.5 text-sm font-medium text-white hover:bg-white/10"
                        >
                            <ProviderLogo name="GitHub" url={githubIcon?.url} size={20} className="border-white/30" />
                            Continue with GitHub
                        </button>
                    </div>

                    <div className="my-5 flex items-center gap-3">
                        <div className="h-px flex-1 bg-white/15" />
                        <span className="text-xs uppercase tracking-[0.2em] text-white/50">or</span>
                        <div className="h-px flex-1 bg-white/15" />
                    </div>

                    <form className="space-y-5" onSubmit={handleSubmit}>
                        {isSignupMode && (
                            <>
                                <div>
                                    <label htmlFor="username" className="text-sm text-white/70">
                                        Username
                                    </label>
                                    <input
                                        id="username"
                                        name="username"
                                        type="text"
                                        className="mt-2 w-full rounded-lg border border-white/10 bg-[#101720] px-3 py-2 text-sm text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-400/60"
                                        placeholder="chronos_builder"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                    />
                                </div>
                                <div>
                                    <label htmlFor="full-name" className="text-sm text-white/70">
                                        Full name (optional)
                                    </label>
                                    <input
                                        id="full-name"
                                        name="fullName"
                                        type="text"
                                        className="mt-2 w-full rounded-lg border border-white/10 bg-[#101720] px-3 py-2 text-sm text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-400/60"
                                        placeholder="Jane Doe"
                                        value={fullName}
                                        onChange={(e) => setFullName(e.target.value)}
                                    />
                                </div>
                            </>
                        )}

                        <div>
                            <label htmlFor="email-address" className="text-sm text-white/70">
                                Email address
                            </label>
                            <input
                                id="email-address"
                                name="email"
                                type="email"
                                autoComplete="email"
                                required
                                className="mt-2 w-full rounded-lg border border-white/10 bg-[#101720] px-3 py-2 text-sm text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-400/60"
                                placeholder="you@chronos.ai"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                        <div>
                            <label htmlFor="password" className="text-sm text-white/70">
                                Password
                            </label>
                            <div className="relative mt-2">
                                <input
                                    id="password"
                                    name="password"
                                    type={showPassword ? 'text' : 'password'}
                                    autoComplete={isSignupMode ? 'new-password' : 'current-password'}
                                    required
                                    className="w-full rounded-lg border border-white/10 bg-[#101720] px-3 py-2 pr-16 text-sm text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-400/60"
                                    placeholder="********"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword((prev) => !prev)}
                                    className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md border border-white/20 px-2 py-1 text-xs text-white/80 hover:bg-white/10"
                                >
                                    {showPassword ? 'Hide' : 'Show'}
                                </button>
                            </div>
                            {passwordTooShort && (
                                <p className="mt-2 text-xs text-amber-300">
                                    Password should be at least {minPasswordLength} characters.
                                </p>
                            )}
                        </div>

                        {isSignupMode && (
                            <div>
                                <label htmlFor="password-confirm" className="text-sm text-white/70">
                                    Confirm password
                                </label>
                                <div className="relative mt-2">
                                    <input
                                        id="password-confirm"
                                        name="passwordConfirm"
                                        type={showPasswordConfirm ? 'text' : 'password'}
                                        autoComplete="new-password"
                                        required
                                        className="w-full rounded-lg border border-white/10 bg-[#101720] px-3 py-2 pr-16 text-sm text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-400/60"
                                        placeholder="********"
                                        value={passwordConfirm}
                                        onChange={(e) => setPasswordConfirm(e.target.value)}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPasswordConfirm((prev) => !prev)}
                                        className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md border border-white/20 px-2 py-1 text-xs text-white/80 hover:bg-white/10"
                                    >
                                        {showPasswordConfirm ? 'Hide' : 'Show'}
                                    </button>
                                </div>
                                {passwordConfirmMismatch && (
                                    <p className="mt-2 text-xs text-amber-300">
                                        Passwords do not match yet.
                                    </p>
                                )}
                            </div>
                        )}

                        {error && <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">{error}</div>}

                        <button
                            type="submit"
                            disabled={loading}
                            className="flex w-full items-center justify-center rounded-full bg-cyan-400 px-4 py-2 text-sm font-semibold text-[#0B1016] transition hover:bg-cyan-300 disabled:opacity-50"
                        >
                            {loading ? <div className="loading-spinner border-[#0B1016]"></div> : isSignupMode ? 'Create account' : 'Sign in to Studio'}
                        </button>

                        <div className="text-center text-sm text-white/60">
                            {isSignupMode ? 'Already have an account? ' : 'Need an account? '}
                            <Link to={isSignupMode ? '/login' : '/signup'} className="text-cyan-300 hover:text-cyan-200">
                                {isSignupMode ? 'Sign in' : 'Create one'}
                            </Link>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    )
}

export default LoginPage

