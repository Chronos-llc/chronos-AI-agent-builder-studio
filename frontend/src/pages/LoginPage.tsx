import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { ChronosLogo } from '../components/brand/ChronosLogo'

const LoginPage: React.FC = () => {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const { login } = useAuth()
    const navigate = useNavigate()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)

        try {
            await login(email, password)
            navigate('/app')
        } catch (error) {
            console.error('Login failed:', error)
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
                    <h2 className="text-2xl font-semibold">Sign in</h2>
                    <p className="mt-2 text-sm text-white/70">
                        Use your Chronos Studio credentials to continue.
                    </p>

                    <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
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
                            <input
                                id="password"
                                name="password"
                                type="password"
                                autoComplete="current-password"
                                required
                                className="mt-2 w-full rounded-lg border border-white/10 bg-[#101720] px-3 py-2 text-sm text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-400/60"
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="flex w-full items-center justify-center rounded-full bg-cyan-400 px-4 py-2 text-sm font-semibold text-[#0B1016] transition hover:bg-cyan-300 disabled:opacity-50"
                        >
                            {loading ? (
                                <div className="loading-spinner border-[#0B1016]"></div>
                            ) : (
                                'Sign in to Studio'
                            )}
                        </button>

                        <div className="text-center text-sm text-white/60">
                            Need access?{' '}
                            <Link to="/" className="text-cyan-300 hover:text-cyan-200">
                                Request an invite
                            </Link>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    )
}

export default LoginPage
