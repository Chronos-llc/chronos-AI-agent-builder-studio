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
} from 'lucide-react'
import { cn } from '../../lib/utils'

const navItems = [
  { label: 'Dashboard', to: '/app', icon: LayoutDashboard },
  { label: 'Agents', to: '/app/agents', icon: Bot },
  { label: 'Integrations', to: '/app/integrations', icon: Puzzle },
  { label: 'Settings', to: '/app/settings', icon: Settings },
  { label: 'Admin', to: '/app/admin', icon: Shield },
]

export const StudioShell: React.FC = () => {
  const location = useLocation()

  return (
    <div className="dark min-h-screen bg-background text-foreground">
      <div className="flex min-h-screen">
        <aside className="hidden w-64 flex-col border-r border-border bg-card/70 p-5 md:flex">
          <ChronosLogo className="mb-8" textClassName="text-foreground" markClassName="text-foreground" />

          <nav className="flex flex-1 flex-col gap-2">
            {navItems.map(item => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition',
                      isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-accent hover:text-foreground'
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

          <div className="rounded-2xl border border-border bg-card p-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
              <Sparkles className="h-4 w-4 text-cyan-300" />
              Studio Pro
            </div>
            <p className="mt-2">Unlock premium orchestration, voice routing, and advanced observability.</p>
          </div>
        </aside>

        <div className="flex flex-1 flex-col">
          <header className="flex items-center justify-between border-b border-border bg-card/60 px-6 py-4">
            <div className="flex items-center gap-3">
              <ChronosLogo
                className="md:hidden"
                showWordmark={false}
                markClassName="text-foreground"
              />
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                  Chronos Studio
                </p>
                <h1 className="text-lg font-semibold text-foreground">
                  {location.pathname.startsWith('/app/agents') ? 'Agent Workspace' : 'Control Center'}
                </h1>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <NavLink
                to="/app/agents/new"
                className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90"
              >
                <Plus className="h-4 w-4" />
                New Agent
              </NavLink>
            </div>
          </header>

          <main className="flex-1 bg-background px-6 py-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}
