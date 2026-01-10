export type AdminMode =
    'meta-agents' |
    'subagents' |
    'marketplace' |
    'skills' |
    'platform-updates' |
    'support' |
    'payments'

export interface AdminUser {
    id: string
    name: string
    email: string
    role: 'admin' | 'super-admin' | 'moderator'
    permissions: string[]
    last_login: string
    status: 'active' | 'inactive' | 'suspended'
}

export interface AdminStatistics {
    total_users: number
    active_agents: number
    marketplace_listings: number
    pending_support_tickets: number
    revenue: number
    system_health: 'good' | 'warning' | 'critical'
}

export interface AdminNavigationItem {
    id: string
    title: string
    icon: React.ReactNode
    path: string
    mode?: AdminMode
    subItems?: AdminNavigationItem[]
}

export interface AdminDashboardCard {
    id: string
    title: string
    value: string | number
    trend?: 'up' | 'down' | 'stable'
    trendValue?: number
    icon: React.ReactNode
}

export interface AdminModeConfig {
    mode: AdminMode
    title: string
    description: string
    icon: React.ReactNode
    component: React.ReactNode
}

export interface AdminAlert {
    id: string
    type: 'info' | 'warning' | 'error' | 'success'
    title: string
    message: string
    timestamp: string
    isRead: boolean
}

export interface AdminQuickAction {
    id: string
    title: string
    icon: React.ReactNode
    onClick: () => void
    color?: string
}