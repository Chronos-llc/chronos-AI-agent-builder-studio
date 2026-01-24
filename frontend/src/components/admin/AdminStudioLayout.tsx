import { useState, useEffect } from 'react'
import { AdminHeader } from './AdminHeader'
import { AdminNavigation } from './AdminNavigation'
import { AdminDashboard } from './AdminDashboard'
import { ModeSwitcher } from './ModeSwitcher'
import { MetaAgentMode } from './modes/MetaAgentMode'
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

export const AdminStudioLayout = () => {
    const [currentMode, setCurrentMode] = useState<AdminMode>('meta-agents')
    const [sidebarOpen, setSidebarOpen] = useState(true)
    const [isMobile, setIsMobile] = useState(false)

    // Mock admin user data
    const adminUser: AdminUser = {
        id: 'admin-001',
        name: 'Admin User',
        email: 'admin@example.com',
        role: 'super-admin',
        permissions: ['all'],
        last_login: new Date().toISOString(),
        status: 'active'
    }

    // Mock statistics data
    const statistics: AdminStatistics = {
        total_users: 1248,
        active_agents: 342,
        marketplace_listings: 89,
        pending_support_tickets: 12,
        revenue: 45678.90,
        system_health: 'good'
    }

    // Mock alerts data
    const alerts: AdminAlert[] = [
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
            onClick: () => alert('Create Agent clicked')
        },
        {
            id: 'action-2',
            title: 'Add User',
            icon: <UserPlus className="w-5 h-5" />,
            onClick: () => alert('Add User clicked')
        },
        {
            id: 'action-3',
            title: 'Marketplace',
            icon: <ShoppingCart className="w-5 h-5" />,
            onClick: () => alert('Marketplace clicked')
        },
        {
            id: 'action-4',
            title: 'Skills',
            icon: <BrainCircuit className="w-5 h-5" />,
            onClick: () => alert('Skills clicked')
        },
        {
            id: 'action-5',
            title: 'Updates',
            icon: <Package className="w-5 h-5" />,
            onClick: () => alert('Updates clicked')
        },
        {
            id: 'action-6',
            title: 'Support',
            icon: <MessageSquare className="w-5 h-5" />,
            onClick: () => alert('Support clicked')
        }
    ]

    // Handle responsive design
    useEffect(() => {
        const handleResize = () => {
            setIsMobile(window.innerWidth < 768)
            if (window.innerWidth < 768) {
                setSidebarOpen(false)
            } else {
                setSidebarOpen(true)
            }
        }

        handleResize()
        window.addEventListener('resize', handleResize)
        return () => window.removeEventListener('resize', handleResize)
    }, [])

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen)
    }

    const handleModeChange = (mode: AdminMode) => {
        setCurrentMode(mode)
    }

    const handleNavigate = (path: string) => {
        console.log('Navigate to:', path)
        // In a real app, this would use react-router navigation
    }

    // Mode content components
    const renderModeContent = () => {
        switch (currentMode) {
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
            case 'skills':
                return (
                    <div className="p-6">
                        <h2 className="text-xl font-bold mb-4">Skills Management</h2>
                        <p>Agent skills and capabilities management.</p>
                    </div>
                )
            case 'platform-updates':
                return (
                    <div className="p-6">
                        <h2 className="text-xl font-bold mb-4">Platform Updates</h2>
                        <p>System updates and version management.</p>
                    </div>
                )
            case 'support':
                return (
                    <div className="p-6">
                        <h2 className="text-xl font-bold mb-4">Support System</h2>
                        <p>Support tickets and knowledge base management.</p>
                    </div>
                )
            case 'payments':
                return (
                    <div className="p-6">
                        <h2 className="text-xl font-bold mb-4">Payments & Billing</h2>
                        <p>Billing, transactions, and subscriptions management.</p>
                    </div>
                )
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
            {/* Sidebar */}
            <div className={`transition-all duration-300 ease-in-out ${sidebarOpen ? 'w-64' : 'w-0'} ${!sidebarOpen && !isMobile ? 'hidden md:block' : ''} admin-mobile-sidebar ${sidebarOpen ? 'open' : ''}`}>
                <div className="h-full flex flex-col border-r border-border bg-card admin-navigation">
                    {/* Logo/Brand */}
                    <div className="p-4 border-b border-border flex items-center gap-2">
                        <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
                            <span className="text-primary-foreground font-bold text-sm">ADMIN</span>
                        </div>
                        <span className="font-semibold text-lg">Chronos Admin</span>
                    </div>

                    {/* Navigation */}
                    <div className="flex-1 overflow-hidden">
                        <AdminNavigation
                            items={[]} // Using default items
                            activeItemId={currentMode}
                            onNavigate={handleNavigate}
                        />
                    </div>

                    {/* Sidebar toggle */}
                    <div className="p-2 border-t border-border">
                        <Button
                            variant="ghost"
                            size="sm"
                            className="w-full justify-start gap-2"
                            onClick={toggleSidebar}
                        >
                            {sidebarOpen ?
                                <PanelLeftClose className="w-4 h-4" /> :
                                <PanelLeftOpen className="w-4 h-4" />
                            }
                            <span>{sidebarOpen ? 'Collapse' : 'Expand'}</span>
                        </Button>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className={`flex-1 flex flex-col overflow-hidden transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-0'} admin-main-content ${sidebarOpen ? 'mobile-open' : ''}`}>
                {/* Header */}
                <AdminHeader
                    user={adminUser}
                    alerts={alerts}
                    onSearch={(query: string) => console.log('Search:', query)}
                />

                {/* Mode Switcher */}
                <div className="p-4 border-b border-border bg-card">
                    <ModeSwitcher
                        currentMode={currentMode}
                        onModeChange={handleModeChange}
                    />
                </div>

                {/* Content Area */}
                <main className="flex-1 overflow-auto p-6 mode-content">
                    {renderModeContent()}
                </main>
            </div>
        </div>
    )
}