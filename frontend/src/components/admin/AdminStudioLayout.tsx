import { useState, useEffect, useMemo } from 'react'
import { AdminHeader } from './AdminHeader'
import { AdminNavigation } from './AdminNavigation'
import { AdminDashboard } from './AdminDashboard'
import { MetaAgentMode } from './modes/MetaAgentMode'
import { IntegrationSubmissionsMode } from './modes/IntegrationSubmissionsMode'
import { SkillsMode } from './modes/SkillsMode'
import { PlatformUpdatesMode } from './modes/PlatformUpdatesMode'
import { SupportMode } from './modes/SupportMode'
import { PaymentMode } from './modes/PaymentMode'
import { AdminMode, AdminUser, AdminStatistics, AdminAlert } from '../../types/admin'
import { Button } from '../ui/button'
import {
    PanelLeftClose,
    PanelLeftOpen,
    Users,
    UserPlus,
    ShoppingCart,
    BrainCircuit,
    Package,
    MessageSquare} from 'lucide-react'
import '../../components/admin/AdminStudio.css'
import { useAuth } from '../../contexts/AuthContext'
import { useNavigate, useParams } from 'react-router-dom'
import SwitchProfileDialog from './SwitchProfileDialog'
import { cn } from '../../lib/utils'
import { adminService } from '../../services/adminService'
import { ChronosLogo } from '../brand/ChronosLogo'

const ADMIN_SIDEBAR_COLLAPSED_KEY = 'chronos_admin_sidebar_collapsed'
const ADMIN_ALERTS_STORAGE_KEY = 'chronos_admin_alerts_state'
const ADMIN_ROUTE_MODES: AdminMode[] = [
    'dashboard',
    'meta-agents',
    'subagents',
    'marketplace',
    'integration-submissions',
    'skills',
    'platform-updates',
    'support',
    'payments',
    'settings',
]

export const AdminStudioLayout = () => {
    const navigate = useNavigate()
    const { mode: routeMode } = useParams<{ mode?: string }>()
    const { sessionContext, logout } = useAuth()
    const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
        if (typeof window === 'undefined') return false
        return window.localStorage.getItem(ADMIN_SIDEBAR_COLLAPSED_KEY) === 'true'
    })
    const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
    const [isMobile, setIsMobile] = useState(false)
    const [switchProfileOpen, setSwitchProfileOpen] = useState(false)
    const [alerts, setAlerts] = useState<AdminAlert[]>(() => {
        if (typeof window === 'undefined') {
            return []
        }
        const saved = window.localStorage.getItem(ADMIN_ALERTS_STORAGE_KEY)
        if (saved) {
            try {
                const parsed = JSON.parse(saved) as AdminAlert[]
                if (Array.isArray(parsed)) {
                    return parsed
                }
            } catch {
                // ignore invalid local cache
            }
        }
        return [
            {
                id: 'alert-1',
                type: 'info',
                title: 'System Update Available',
                message: 'Version 2.1.0 is ready to install',
                timestamp: new Date(Date.now() - 86400000).toISOString(),
                isRead: false
            },
            {
                id: 'alert-2',
                type: 'warning',
                title: 'High Memory Usage',
                message: 'Server memory usage is at 85%',
                timestamp: new Date(Date.now() - 3600000).toISOString(),
                isRead: false
            }
        ]
    })
    const currentMode = useMemo<AdminMode>(() => {
        if (!routeMode) return 'dashboard'
        return (ADMIN_ROUTE_MODES.includes(routeMode as AdminMode) ? routeMode : 'dashboard') as AdminMode
    }, [routeMode])

    // Display-ready admin user data
    const adminUser: AdminUser = {
        id: String(sessionContext?.user?.id || 'admin'),
        name: sessionContext?.user?.full_name || sessionContext?.user?.username || 'Admin User',
        email: sessionContext?.user?.email || 'admin@example.com',
        role: 'super-admin',
        permissions: ['all'],
        last_login: new Date().toISOString(),
        status: 'active'
    }

    // Fetch real statistics data
    const [statistics, setStatistics] = useState<AdminStatistics>({
        total_users: 0,
        active_agents: 0,
        marketplace_listings: 0,
        pending_support_tickets: 0,
        revenue: 0,
        system_health: 'good'
    })

    useEffect(() => {
        const fetchStatistics = async () => {
            try {
                const data = await adminService.getAdminStats()
                // Validate system_health value to match the union type
                const validHealthStatuses = ['warning', 'critical', 'good'] as const
                const systemHealth = validHealthStatuses.includes(data.system_health as typeof validHealthStatuses[number])
                    ? data.system_health as 'warning' | 'critical' | 'good'
                    : 'good'
                setStatistics({
                    ...data,
                    system_health: systemHealth
                })
            } catch (error) {
                console.error('Failed to fetch admin statistics:', error)
            }
        }

        fetchStatistics()
    }, [])

    // Mock recent activity data
    const recentActivity = [
        {
            id: 'activity-1',
            title: 'New user registered',
            description: 'john.doe@example.com signed up',
            timestamp: '2 hours ago',
            type: 'user' as const
        },
        {
            id: 'activity-2',
            title: 'Agent published',
            description: 'Customer Support Agent v1.2',
            timestamp: '5 hours ago',
            type: 'system' as const
        },
        {
            id: 'activity-3',
            title: 'Payment processed',
            description: 'Subscription renewal for Pro Plan',
            timestamp: '1 day ago',
            type: 'payment' as const
        }
    ]

    // Mock quick actions
    const quickActions = [
        {
            id: 'action-1',
            title: 'Create Agent',
            icon: <Users className="w-5 h-5" />,
            onClick: () => navigate('/app/admin/meta-agents')
        },
        {
            id: 'action-2',
            title: 'Add User',
            icon: <UserPlus className="w-5 h-5" />,
            onClick: () => navigate('/app/admin/subagents')
        },
        {
            id: 'action-3',
            title: 'Marketplace',
            icon: <ShoppingCart className="w-5 h-5" />,
            onClick: () => navigate('/app/admin/marketplace')
        },
        {
            id: 'action-4',
            title: 'Skills',
            icon: <BrainCircuit className="w-5 h-5" />,
            onClick: () => navigate('/app/admin/skills')
        },
        {
            id: 'action-5',
            title: 'Updates',
            icon: <Package className="w-5 h-5" />,
            onClick: () => navigate('/app/admin/platform-updates')
        },
        {
            id: 'action-6',
            title: 'Support',
            icon: <MessageSquare className="w-5 h-5" />,
            onClick: () => navigate('/app/admin/support')
        }
    ]

    // Handle responsive design
    useEffect(() => {
        const handleResize = () => {
            setIsMobile(window.innerWidth < 768)
            if (window.innerWidth >= 768) {
                setMobileSidebarOpen(false)
            }
        }

        handleResize()
        window.addEventListener('resize', handleResize)
        return () => window.removeEventListener('resize', handleResize)
    }, [])

    useEffect(() => {
        if (typeof window === 'undefined') return
        window.localStorage.setItem(ADMIN_SIDEBAR_COLLAPSED_KEY, String(sidebarCollapsed))
    }, [sidebarCollapsed])

    useEffect(() => {
        if (typeof window === 'undefined') return
        window.localStorage.setItem(ADMIN_ALERTS_STORAGE_KEY, JSON.stringify(alerts))
    }, [alerts])

    useEffect(() => {
        if (!routeMode) {
            navigate('/app/admin/dashboard', { replace: true })
            return
        }
        if (!ADMIN_ROUTE_MODES.includes(routeMode as AdminMode)) {
            navigate('/app/admin/dashboard', { replace: true })
        }
    }, [navigate, routeMode])

    const toggleSidebar = () => {
        if (isMobile) {
            setMobileSidebarOpen((previous) => !previous)
            return
        }
        setSidebarCollapsed((previous) => !previous)
    }

    const handleModeChange = (mode: AdminMode) => {
        navigate(`/app/admin/${mode}`)
        if (isMobile) {
            setMobileSidebarOpen(false)
        }
    }

    const handleLogout = async () => {
        await logout()
        navigate('/login')
    }

    const handleNavigate = (path: string) => {
        let resolvedPath = path
        if (path.startsWith('/admin/')) {
            const modeFromLegacyPath = path.split('/').filter(Boolean)[1]
            resolvedPath = `/app/admin/${modeFromLegacyPath || 'dashboard'}`
        } else if (path === '/admin') {
            resolvedPath = '/app/admin/dashboard'
        }

        if (resolvedPath === '/app/admin') {
            resolvedPath = '/app/admin/dashboard'
        }

        navigate(resolvedPath)
        if (isMobile) {
            setMobileSidebarOpen(false)
        }
    }

    const handleMarkAlertRead = (alertId: string) => {
        setAlerts((previous) =>
            previous.map((alert) => (alert.id === alertId ? { ...alert, isRead: true } : alert))
        )
    }

    const handleDismissAlert = (alertId: string) => {
        setAlerts((previous) => previous.filter((alert) => alert.id !== alertId))
    }

    const handleClearAlerts = () => {
        setAlerts([])
    }

    // Mode content components
    const renderModeContent = () => {
        switch (currentMode) {
            case 'dashboard':
                return <AdminDashboard
                    statistics={statistics}
                    recentActivity={recentActivity}
                    quickActions={quickActions}
                />
            case 'meta-agents':
                return <MetaAgentMode />
            case 'subagents':
                return (
                    <div className="p-6">
                        <h2 className="text-xl font-bold mb-4">Subagents Management</h2>
                        <p>Subagents creation and management interface.</p>
                    </div>
                )
            case 'marketplace':
                return (
                    <div className="p-6">
                        <h2 className="text-xl font-bold mb-4">Marketplace Administration</h2>
                        <p>Marketplace listings and categories management.</p>
                    </div>
                )
            case 'integration-submissions':
                return <IntegrationSubmissionsMode />
            case 'skills':
                return <SkillsMode />
            case 'platform-updates':
                return <PlatformUpdatesMode />
            case 'support':
                return <SupportMode />
            case 'payments':
                return <PaymentMode />
            case 'settings':
                return (
                    <div className="p-6">
                        <h2 className="text-xl font-bold mb-4">System Settings</h2>
                        <p>Configure system-wide settings and preferences.</p>
                    </div>
                )
            default:
                return <AdminDashboard
                    statistics={statistics}
                    recentActivity={recentActivity}
                    quickActions={quickActions}
                />
        }
    }

    return (
        <div className="flex h-screen bg-background overflow-hidden admin-studio-layout">
            {isMobile && mobileSidebarOpen && (
                <button
                    type="button"
                    aria-label="Close sidebar"
                    className="fixed inset-0 z-30 bg-black/50"
                    onClick={() => setMobileSidebarOpen(false)}
                />
            )}

            {/* Sidebar - Fixed position with independent scrolling */}
            <div
                className={cn(
                    'fixed inset-y-0 left-0 z-40 transition-all duration-300 ease-in-out',
                    isMobile
                        ? cn(
                            'w-64 transform',
                            mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full'
                        )
                        : sidebarCollapsed
                            ? 'w-20'
                            : 'w-64'
                )}
            >
                <div className="h-full flex flex-col border-r border-border bg-card admin-navigation">
                    {/* Logo/Brand */}
                    <div className={cn('border-b border-border flex items-center shrink-0', sidebarCollapsed && !isMobile ? 'justify-center p-3' : 'gap-2 p-4')}>
                        <ChronosLogo showWordmark={false} size={32} />
                        {(!sidebarCollapsed || isMobile) && <span className="font-semibold text-lg">Chronos Admin</span>}
                    </div>

                    {/* Navigation - Independent scroll container */}
                    <div className="flex-1 overflow-y-auto">
                        <AdminNavigation
                            items={[]} // Using default items
                            activeItemId={currentMode}
                            onNavigate={handleNavigate}
                            collapsed={sidebarCollapsed && !isMobile}
                        />
                    </div>

                    {/* Sidebar toggle */}
                    <div className="shrink-0 p-2 border-t border-border">
                        <Button
                            variant="ghost"
                            size="sm"
                            className={cn('w-full', sidebarCollapsed && !isMobile ? 'justify-center px-2' : 'justify-start gap-2')}
                            onClick={toggleSidebar}
                            title={isMobile ? 'Close sidebar' : sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                        >
                            {(sidebarCollapsed && !isMobile) ?
                                <PanelLeftOpen className="w-4 h-4" /> :
                                <PanelLeftClose className="w-4 h-4" />
                            }
                            {(!sidebarCollapsed || isMobile) && (
                                <span>{isMobile ? 'Close' : 'Collapse'}</span>
                            )}
                        </Button>
                    </div>
                </div>
            </div>

            {/* Main Content - Add margin-left to account for fixed sidebar */}
            <div
                className={cn(
                    'flex-1 min-w-0 flex flex-col overflow-hidden transition-all duration-300 admin-main-content',
                    isMobile ? 'ml-0' : sidebarCollapsed ? 'ml-20' : 'ml-64'
                )}
            >
                {/* Header */}
                <AdminHeader
                    user={adminUser}
                    alerts={alerts}
                    onSearch={(query: string) => console.log('Search:', query)}
                    onProfile={() => navigate('/app/admin/settings')}
                    onSettings={() => navigate('/app/admin/settings')}
                    onSwitchProfile={() => setSwitchProfileOpen(true)}
                    onMarkAlertRead={handleMarkAlertRead}
                    onDismissAlert={handleDismissAlert}
                    onClearAlerts={handleClearAlerts}
                    onLogout={handleLogout}
                    onToggleSidebar={toggleSidebar}
                />

                {/* Content Area */}
                <main className="flex-1 overflow-auto p-6 mode-content">
                    {renderModeContent()}
                </main>
            </div>

            <SwitchProfileDialog open={switchProfileOpen} onOpenChange={setSwitchProfileOpen} />
        </div>
    )
}
