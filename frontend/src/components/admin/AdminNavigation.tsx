import { AdminNavigationItem } from '../../types/admin'
import { Button } from '../ui/button'
import { ScrollArea } from '../ui/scroll-area'
import {
    ChevronDown,
    ChevronRight,
    Home,
    Users,
    UserPlus,
    ShoppingCart,
    BrainCircuit,
    Package,
    MessageSquare,
    CreditCard,
    Settings,
    ClipboardCheck
} from 'lucide-react'
import { useState } from 'react'

export const AdminNavigation = ({
    items,
    activeItemId,
    onNavigate,
    collapsed = false,
}: {
    items: AdminNavigationItem[]
    activeItemId?: string
    onNavigate: (path: string) => void
    collapsed?: boolean
}) => {
    const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())

    const toggleExpand = (itemId: string) => {
        setExpandedItems(prev => {
            const newSet = new Set(prev)
            if (newSet.has(itemId)) {
                newSet.delete(itemId)
            } else {
                newSet.add(itemId)
            }
            return newSet
        })
    }

    const renderNavigationItem = (item: AdminNavigationItem, level = 0) => {
        if (collapsed && level > 0) {
            return null
        }

        const hasSubItems = item.subItems && item.subItems.length > 0
        const shouldExpand = hasSubItems && !collapsed
        const isExpanded = expandedItems.has(item.id)
        const isActive = activeItemId === item.id

        return (
            <div key={item.id} className={collapsed ? '' : `${level > 0 ? 'ml-6' : ''}`}>
                <Button
                    variant={isActive ? 'secondary' : 'ghost'}
                    size="sm"
                    title={collapsed ? item.title : undefined}
                    className={`w-full h-9 ${collapsed ? 'justify-center px-2' : 'justify-start gap-2'} ${isActive ? 'bg-accent' : 'hover:bg-accent'}`}
                    onClick={() => {
                        if (shouldExpand) {
                            toggleExpand(item.id)
                        } else if (item.path) {
                            onNavigate(item.path)
                        }
                    }}
                >
                    {item.icon}
                    {!collapsed && <span className="flex-1 text-left truncate">{item.title}</span>}
                    {shouldExpand && (
                        isExpanded ?
                            <ChevronDown className="w-4 h-4" /> :
                            <ChevronRight className="w-4 h-4" />
                    )}
                </Button>

                {shouldExpand && isExpanded && (
                    <div className="mt-1 space-y-1">
                        {(item.subItems || []).map(subItem => renderNavigationItem(subItem, level + 1))}
                    </div>
                )}
            </div>
        )
    }

    // Default navigation items if none provided
    const defaultItems: AdminNavigationItem[] = [
        {
            id: 'dashboard',
            title: 'Dashboard',
            icon: <Home className="w-4 h-4" />,
            path: '/app/admin/dashboard'
        },
        {
            id: 'meta-agents',
            title: 'Meta Agents',
            icon: <Users className="w-4 h-4" />,
            path: '/app/admin/meta-agents'
        },
        {
            id: 'subagents',
            title: 'Subagents',
            icon: <UserPlus className="w-4 h-4" />,
            path: '/app/admin/subagents'
        },
        {
            id: 'marketplace',
            title: 'Marketplace',
            icon: <ShoppingCart className="w-4 h-4" />,
            path: '/app/admin/marketplace'
        },
        {
            id: 'integration-submissions',
            title: 'Integrations',
            icon: <ClipboardCheck className="w-4 h-4" />,
            path: '/app/admin/integration-submissions'
        },
        {
            id: 'skills',
            title: 'Skills',
            icon: <BrainCircuit className="w-4 h-4" />,
            path: '/app/admin/skills'
        },
        {
            id: 'platform-updates',
            title: 'Platform Updates',
            icon: <Package className="w-4 h-4" />,
            path: '/app/admin/platform-updates'
        },
        {
            id: 'support',
            title: 'Support',
            icon: <MessageSquare className="w-4 h-4" />,
            path: '/app/admin/support'
        },
        {
            id: 'payments',
            title: 'Payments',
            icon: <CreditCard className="w-4 h-4" />,
            path: '/app/admin/payments'
        },
        {
            id: 'settings',
            title: 'System',
            icon: <Settings className="w-4 h-4" />,
            path: '/app/admin/settings'
        }
    ]

    const navigationItems = items.length > 0 ? items : defaultItems

    return (
        <ScrollArea className="w-full h-full">
            <nav className="w-full h-full">
                <div className="p-2 space-y-1">
                    {navigationItems.map(item => renderNavigationItem(item))}
                </div>
            </nav>
        </ScrollArea>
    )
}
