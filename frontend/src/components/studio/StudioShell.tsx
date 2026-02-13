import React from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { ChronosLogo } from '../brand/ChronosLogo'
import {
  LayoutDashboard,
  Bot,
  Settings,
  Shield,
  Puzzle,
  Plus,
  Sparkles,
  Radio,
} from 'lucide-react'
import { cn } from '../../lib/utils'

const navItems = [
  { label: 'Dashboard', to: '/app', icon: LayoutDashboard },
  { label: 'Agents', to: '/app/agents', icon: Bot },
  { label: 'Integrations', to: '/app/integrations', icon: Puzzle },
  { label: 'Channels', to: '/app/channels', icon: Radio },
  { label: 'Settings', to: '/app/settings', icon: Settings },
  { label: 'Admin', to: '/app/admin', icon: Shield },
]

export const StudioShell: React.FC = () => {
  const location = useLocation()

  return (
    <div className="dark min-h-screen bg-[#06080D] text-foreground">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.14),_transparent_36%)]" />
      <div className="pointer-events-none fixed -left-24 top-36 h-64 w-64 rounded-full bg-cyan-300/10 blur-3xl" />
      <div className="pointer-events-none fixed -right-20 top-10 h-72 w-72 rounded-full bg-emerald-300/10 blur-3xl" />

      <div className="relative flex min-h-screen">
        <aside className="hidden w-72 flex-col border-r border-white/10 bg-black/35 p-5 md:flex">
          <ChronosLogo className="mb-8" textClassName="text-white" markClassName="text-white" />

          <nav className="flex flex-1 flex-col gap-2">
            {navItems.map(item => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition',
                      isActive
                        ? 'border border-cyan-300/40 bg-cyan-300/15 text-cyan-100 shadow-glow'
                        : 'text-white/70 hover:border hover:border-white/20 hover:bg-white/5 hover:text-white'
                    )
                  }
                  end={item.to === '/app'}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </NavLink>
              )
            })}
          </nav>

          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-xs text-white/70">
            <div className="flex items-center gap-2 text-sm font-semibold text-white">
              <Sparkles className="h-4 w-4 text-cyan-300" />
              Chronos Build Mode
            </div>
            <p className="mt-2">Build voice and chat agents, connect tools, and run orchestration from one workspace.</p>
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-20 border-b border-white/10 bg-[#06080D]/80 px-6 py-4 backdrop-blur">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <ChronosLogo className="md:hidden" showWordmark={false} markClassName="text-white" />
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-white/50">Chronos Studio</p>
                  <h1 className="text-lg font-semibold text-white">
                    {location.pathname.startsWith('/app/agents')
                      ? 'Agent Workspace'
                      : location.pathname.startsWith('/app/integrations')
                        ? 'Integration Hub'
                        : 'Control Center'}
                  </h1>
                </div>
              </div>
              <NavLink
                to="/app/agents/new"
                className="inline-flex items-center gap-2 rounded-full bg-cyan-300 px-4 py-2 text-sm font-semibold text-[#081018] transition hover:bg-cyan-200"
              >
                <Plus className="h-4 w-4" />
                New Agent
              </NavLink>
            </div>
          </header>

          <main className="flex-1 px-6 py-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}
