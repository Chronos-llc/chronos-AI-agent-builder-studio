import { AdminDashboardCard, AdminStatistics } from '../../types/admin'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import {
    Users,
    ShoppingCart,
    MessageSquare,
    CreditCard,
    AlertTriangle,
    CheckCircle,
    TrendingUp,
    TrendingDown,
    Activity,
    Settings
} from 'lucide-react'

export const AdminDashboard = ({
    statistics,
    recentActivity,
    quickActions
}: {
    statistics: AdminStatistics
    recentActivity?: {
        id: string
        title: string
        description: string
        timestamp: string
        type: 'user' | 'system' | 'payment'
    }[]
    quickActions?: {
        id: string
        title: string
        onClick: () => void
        icon: React.ReactNode
    }[]
}) => {
    // Default dashboard cards
    const dashboardCards: AdminDashboardCard[] = [
        {
            id: 'total-users',
            title: 'Total Users',
            value: statistics.total_users,
            trend: 'up',
            trendValue: 12,
            icon: <Users className="w-6 h-6 text-blue-500" />
        },
        {
            id: 'active-agents',
            title: 'Active Agents',
            value: statistics.active_agents,
            trend: 'up',
            trendValue: 8,
            icon: <Activity className="w-6 h-6 text-green-500" />
        },
        {
            id: 'marketplace-listings',
            title: 'Marketplace Listings',
            value: statistics.marketplace_listings,
            trend: 'stable',
            icon: <ShoppingCart className="w-6 h-6 text-purple-500" />
        },
        {
            id: 'support-tickets',
            title: 'Support Tickets',
            value: statistics.pending_support_tickets,
            trend: 'down',
            trendValue: 5,
            icon: <MessageSquare className="w-6 h-6 text-yellow-500" />
        }
    ]

    const getTrendIcon = (trend?: 'up' | 'down' | 'stable') => {
        switch (trend) {
            case 'up': return <TrendingUp className="w-4 h-4 text-green-500" />
            case 'down': return <TrendingDown className="w-4 h-4 text-red-500" />
            case 'stable': return <TrendingUp className="w-4 h-4 text-gray-500 rotate-90" />
            default: return null
        }
    }

    const getSystemHealthStatus = () => {
        switch (statistics.system_health) {
            case 'good': return {
                text: 'System Healthy',
                icon: <CheckCircle className="w-5 h-5 text-green-500" />,
                bgColor: 'bg-green-100',
                textColor: 'text-green-800'
            }
            case 'warning': return {
                text: 'Warning',
                icon: <AlertTriangle className="w-5 h-5 text-yellow-500" />,
                bgColor: 'bg-yellow-100',
                textColor: 'text-yellow-800'
            }
            case 'critical': return {
                text: 'Critical Issue',
                icon: <AlertTriangle className="w-5 h-5 text-red-500" />,
                bgColor: 'bg-red-100',
                textColor: 'text-red-800'
            }
        }
    }

    const systemHealth = getSystemHealthStatus()

    return (
        <div className="space-y-6">
            {/* Dashboard header */}
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Admin Dashboard</h1>
                <div className="flex items-center gap-2">
                    {systemHealth && (
                        <div className={`px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2 ${systemHealth.bgColor} ${systemHealth.textColor}`}>
                            {systemHealth.icon}
                            <span>{systemHealth.text}</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Quick stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {dashboardCards.map((card) => (
                    <Card key={card.id} className="hover:shadow-md transition-shadow">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
                            {card.icon}
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{card.value}</div>
                            {card.trend && (
                                <p className={`text-xs flex items-center gap-1 mt-1 ${card.trend === 'up' ? 'text-green-500' : card.trend === 'down' ? 'text-red-500' : 'text-gray-500'}`}>
                                    {getTrendIcon(card.trend)}
                                    {card.trend === 'stable' ? 'Stable' : `${card.trend === 'up' ? '+' : '-'}${card.trendValue}%`}
                                </p>
                            )}
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Quick actions */}
            {quickActions && quickActions.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                    {quickActions.map((action) => (
                        <Button
                            key={action.id}
                            variant="outline"
                            size="sm"
                            className="flex flex-col items-center justify-center h-20 gap-2 hover:bg-accent"
                            onClick={action.onClick}
                        >
                            {action.icon}
                            <span className="text-xs font-medium text-center">{action.title}</span>
                        </Button>
                    ))}
                </div>
            )}

            {/* Recent activity */}
            {recentActivity && recentActivity.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">Recent Activity</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {recentActivity.slice(0, 5).map((activity) => (
                                <div key={activity.id} className="flex items-start gap-3 p-3 border border-border rounded-lg">
                                    <div className="mt-1">
                                        {activity.type === 'user' && <Users className="w-5 h-5 text-blue-500" />}
                                        {activity.type === 'system' && <Settings className="w-5 h-5 text-gray-500" />}
                                        {activity.type === 'payment' && <CreditCard className="w-5 h-5 text-green-500" />}
                                    </div>
                                    <div className="flex-1">
                                        <h4 className="font-medium text-sm">{activity.title}</h4>
                                        <p className="text-sm text-muted-foreground truncate">{activity.description}</p>
                                        <p className="text-xs text-muted-foreground mt-1">{activity.timestamp}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* System overview */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">System Overview</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">Total Revenue</span>
                                <span className="text-lg font-bold">${statistics.revenue.toLocaleString()}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">System Health</span>
                                <div className="flex items-center gap-2">
                                    {systemHealth?.icon}
                                    <span className={`font-medium ${systemHealth?.textColor}`}>{systemHealth?.text}</span>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">Quick Stats</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-sm text-muted-foreground">Users</p>
                                <p className="text-xl font-bold">{statistics.total_users}</p>
                            </div>
                            <div>
                                <p className="text-sm text-muted-foreground">Agents</p>
                                <p className="text-xl font-bold">{statistics.active_agents}</p>
                            </div>
                            <div>
                                <p className="text-sm text-muted-foreground">Listings</p>
                                <p className="text-xl font-bold">{statistics.marketplace_listings}</p>
                            </div>
                            <div>
                                <p className="text-sm text-muted-foreground">Tickets</p>
                                <p className="text-xl font-bold">{statistics.pending_support_tickets}</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}