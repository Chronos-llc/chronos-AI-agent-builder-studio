import React, { useEffect, useState } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { ChronosLogo } from '../brand/ChronosLogo'
import {
  LayoutDashboard,
  Bot,
  Settings,
  Puzzle,
  Plus,
  Sparkles,
  Radio,
  Gauge,
  UserCircle2,
  LogOut,
  Repeat2,
  PanelLeftClose,
  PanelLeftOpen,
  Store,
} from 'lucide-react'
import { cn } from '../../lib/utils'
import { useAuth } from '../../contexts/AuthContext'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu'
import ImpersonationBanner from './ImpersonationBanner'
import ThemeSwitcher from '../theme/ThemeSwitcher'
import UsageSidebarWidget from './UsageSidebarWidget'

const API_BASE_URL_RAW = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const API_BASE_URL = API_BASE_URL_RAW.replace(/\/$/, '')
const SIDEBAR_COLLAPSED_KEY = 'chronos_ui_sidebar_collapsed'

const navItems = [
  { label: 'Dashboard', to: '/app', icon: LayoutDashboard },
  { label: 'Agents', to: '/app/agents', icon: Bot },
  { label: 'Integrations', to: '/app/integrations', icon: Puzzle },
  { label: 'Chronos Hub', to: '/app/integrations/hub', icon: Store },
  { label: 'Channels', to: '/app/channels', icon: Radio },
  { label: 'Usage', to: '/app/usage', icon: Gauge },
  { label: 'Settings', to: '/app/settings', icon: Settings },
]

export const StudioShell: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout, sessionContext, setAccessToken, refreshSessionContext } = useAuth()
  const [switchingBack, setSwitchingBack] = useState(false)
  const [isCollapsed, setIsCollapsed] = useState(() => {
    if (typeof window === 'undefined') return false
    return window.localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === 'true'
  })

  useEffect(() => {
    if (typeof window === 'undefined') return
    window.localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(isCollapsed))
  }, [isCollapsed])

  const handleReturnToAdmin = async () => {
    setSwitchingBack(true)
    try {
      const token = localStorage.getItem('chronos_access_token') || localStorage.getItem('access_token')
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/impersonation/exit`, {
        method: 'POST',
        credentials: 'include',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })
      if (!response.ok) {
        throw new Error('Failed to return to admin')
      }
      const payload = await response.json()
      if (payload?.access_token) {
        setAccessToken(payload.access_token)
      }
      await refreshSessionContext()
      navigate('/app/admin')
    } finally {
      setSwitchingBack(false)
    }
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.14),_transparent_36%)]" />
      <div className="pointer-events-none fixed -left-24 top-36 h-64 w-64 rounded-full bg-cyan-300/10 blur-3xl" />
      <div className="pointer-events-none fixed -right-20 top-10 h-72 w-72 rounded-full bg-emerald-300/10 blur-3xl" />

      <div className="relative flex min-h-screen">
        <aside
          className={cn(
            'hidden h-screen flex-col overflow-y-auto border-r border-border bg-card/90 transition-all duration-300 md:sticky md:top-0 md:flex',
            isCollapsed ? 'w-20 p-3' : 'w-72 p-5'
          )}
        >
          <ChronosLogo
            className={cn('mb-8', isCollapsed && 'justify-center')}
            showWordmark={!isCollapsed}
            textClassName="text-foreground"
            markClassName="text-foreground"
          />

          <nav className="flex flex-1 flex-col gap-2">
            {navItems.map(item => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  title={isCollapsed ? item.label : undefined}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center rounded-xl py-2.5 text-sm font-medium transition',
                      isCollapsed ? 'justify-center px-2' : 'gap-3 px-3',
                      isActive
                        ? 'border border-primary/40 bg-primary/15 text-foreground'
                        : 'text-muted-foreground hover:border hover:border-border hover:bg-accent hover:text-foreground'
                    )
                  }
                  end={item.to === '/app'}
                >
                  <Icon className="h-4 w-4" />
                  {!isCollapsed && item.label}
                </NavLink>
              )
            })}
          </nav>

          <UsageSidebarWidget collapsed={isCollapsed} />

          <div
            className={cn(
              'rounded-2xl border border-border bg-background/70 text-xs text-muted-foreground',
              isCollapsed ? 'p-3 text-center' : 'p-4'
            )}
            title={isCollapsed ? 'Chronos Build Mode' : undefined}
          >
            <div className={cn('flex items-center text-sm font-semibold text-foreground', isCollapsed ? 'justify-center' : 'gap-2')}>
              <Sparkles className="h-4 w-4 text-cyan-300" />
              {!isCollapsed && 'Chronos Build Mode'}
            </div>
            {!isCollapsed && <p className="mt-2">Build voice and chat agents, connect tools, and run orchestration from one workspace.</p>}
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-20 border-b border-border bg-background/90 px-6 py-4 backdrop-blur">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  className="hidden rounded-xl border border-border bg-background p-2 text-muted-foreground transition hover:bg-accent hover:text-foreground md:inline-flex"
                  aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                  aria-expanded={!isCollapsed}
                  onClick={() => setIsCollapsed((previous) => !previous)}
                >
                  {isCollapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
                </button>
                <ChronosLogo className="md:hidden" showWordmark={false} markClassName="text-foreground" />
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Chronos Studio</p>
                  <h1 className="text-lg font-semibold text-foreground">
                    {location.pathname.startsWith('/app/agents')
                      ? 'Agent Workspace'
                      : location.pathname.startsWith('/app/integrations')
                        ? 'Integration Hub'
                        : location.pathname.startsWith('/app/usage')
                          ? 'Usage Center'
                        : 'Control Center'}
                  </h1>
                </div>
              </div>
              <NavLink
                to="/app/integrations/hub"
                className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-4 py-2 text-sm font-semibold text-foreground transition hover:bg-accent"
              >
                <Store className="h-4 w-4" />
                Chronos Hub
              </NavLink>
              <NavLink
                to="/app/agents/new"
                className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90"
              >
                <Plus className="h-4 w-4" />
                New Agent
              </NavLink>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-2 text-sm text-foreground hover:bg-accent">
                    <UserCircle2 className="h-4 w-4" />
                    {user?.username || 'Profile'}
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <div className="px-2 py-2">
                    <p className="mb-1 text-xs font-medium text-muted-foreground">Theme</p>
                    <ThemeSwitcher compact className="w-full justify-center" />
                  </div>
                  {sessionContext?.is_impersonating && (
                    <DropdownMenuItem
                      onSelect={(event) => {
                        event.preventDefault()
                        if (!switchingBack) {
                          void handleReturnToAdmin()
                        }
                      }}
                    >
                      <Repeat2 className="mr-2 h-4 w-4" />
                      {switchingBack ? 'Switching...' : 'Return to Admin'}
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuItem
                    onSelect={(event) => {
                      event.preventDefault()
                      navigate('/app/settings')
                    }}
                  >
                    <Settings className="mr-2 h-4 w-4" />
                    Settings
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onSelect={(event) => {
                      event.preventDefault()
                      void handleLogout()
                    }}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    Sign out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </header>

          <main className="flex-1 px-6 py-8">
            <ImpersonationBanner />
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}
