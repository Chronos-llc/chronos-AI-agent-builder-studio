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
    BarChart3,
    Shield,
    FileText
} from 'lucide-react'
import { useState } from 'react'

export const AdminNavigation = ({
    items,
    activeItemId,
    onNavigate
}: {
    items: AdminNavigationItem[]
    activeItemId?: string
    onNavigate: (path: string) => void
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
        const hasSubItems = item.subItems && item.subItems.length > 0
        const isExpanded = expandedItems.has(item.id)
        const isActive = activeItemId === item.id

        return (
            <div key={item.id} className={`${level > 0 ? 'ml-6' : ''}`}>
                <Button
                    variant={isActive ? 'secondary' : 'ghost'}
                    size="sm"
                    className={`w-full justify-start gap-2 h-9 ${isActive ? 'bg-accent' : 'hover:bg-accent'}`}
                    onClick={() => {
                        if (hasSubItems) {
                            toggleExpand(item.id)
                        } else if (item.path) {
                            onNavigate(item.path)
                        }
                    }}
                >
                    {item.icon}
                    <span className="flex-1 text-left truncate">{item.title}</span>
                    {hasSubItems && (
                        isExpanded ?
                            <ChevronDown className="w-4 h-4" /> :
                            <ChevronRight className="w-4 h-4" />
                    )}
                </Button>

                {hasSubItems && isExpanded && (
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
            path: '/admin'
        },
        {
            id: 'meta-agents',
            title: 'Meta Agents',
            icon: <Users className="w-4 h-4" />,
            path: '/admin/meta-agents',
            subItems: [
                {
                    id: 'meta-agents-list',
                    title: 'All Meta Agents',
                    icon: <Users className="w-4 h-4" />,
                    path: '/admin/meta-agents/list'
                },
                {
                    id: 'meta-agents-create',
                    title: 'Create Meta Agent',
                    icon: <UserPlus className="w-4 h-4" />,
                    path: '/admin/meta-agents/create'
                }
            ]
        },
        {
            id: 'subagents',
            title: 'Subagents',
            icon: <UserPlus className="w-4 h-4" />,
            path: '/admin/subagents',
            subItems: [
                {
                    id: 'subagents-list',
                    title: 'All Subagents',
                    icon: <UserPlus className="w-4 h-4" />,
                    path: '/admin/subagents/list'
                },
                {
                    id: 'subagents-create',
                    title: 'Create Subagent',
                    icon: <UserPlus className="w-4 h-4" />,
                    path: '/admin/subagents/create'
                }
            ]
        },
        {
            id: 'marketplace',
            title: 'Marketplace',
            icon: <ShoppingCart className="w-4 h-4" />,
            path: '/admin/marketplace',
            subItems: [
                {
                    id: 'marketplace-listings',
                    title: 'Listings',
                    icon: <ShoppingCart className="w-4 h-4" />,
                    path: '/admin/marketplace/listings'
                },
                {
                    id: 'marketplace-categories',
                    title: 'Categories',
                    icon: <FileText className="w-4 h-4" />,
                    path: '/admin/marketplace/categories'
                }
            ]
        },
        {
            id: 'skills',
            title: 'Skills',
            icon: <BrainCircuit className="w-4 h-4" />,
            path: '/admin/skills',
            subItems: [
                {
                    id: 'skills-library',
                    title: 'Skills Library',
                    icon: <BrainCircuit className="w-4 h-4" />,
                    path: '/admin/skills/library'
                },
                {
                    id: 'skills-create',
                    title: 'Create Skill',
                    icon: <BrainCircuit className="w-4 h-4" />,
                    path: '/admin/skills/create'
                }
            ]
        },
        {
            id: 'platform-updates',
            title: 'Platform Updates',
            icon: <Package className="w-4 h-4" />,
            path: '/admin/platform-updates',
            subItems: [
                {
                    id: 'updates-releases',
                    title: 'Releases',
                    icon: <Package className="w-4 h-4" />,
                    path: '/admin/platform-updates/releases'
                },
                {
                    id: 'updates-changelog',
                    title: 'Changelog',
                    icon: <FileText className="w-4 h-4" />,
                    path: '/admin/platform-updates/changelog'
                }
            ]
        },
        {
            id: 'support',
            title: 'Support',
            icon: <MessageSquare className="w-4 h-4" />,
            path: '/admin/support',
            subItems: [
                {
                    id: 'support-tickets',
                    title: 'Tickets',
                    icon: <MessageSquare className="w-4 h-4" />,
                    path: '/admin/support/tickets'
                },
                {
                    id: 'support-knowledge-base',
                    title: 'Knowledge Base',
                    icon: <FileText className="w-4 h-4" />,
                    path: '/admin/support/knowledge-base'
                }
            ]
        },
        {
            id: 'payments',
            title: 'Payments',
            icon: <CreditCard className="w-4 h-4" />,
            path: '/admin/payments',
            subItems: [
                {
                    id: 'payments-transactions',
                    title: 'Transactions',
                    icon: <CreditCard className="w-4 h-4" />,
                    path: '/admin/payments/transactions'
                },
                {
                    id: 'payments-subscriptions',
                    title: 'Subscriptions',
                    icon: <CreditCard className="w-4 h-4" />,
                    path: '/admin/payments/subscriptions'
                }
            ]
        },
        {
            id: 'system',
            title: 'System',
            icon: <Settings className="w-4 h-4" />,
            path: '/admin/system',
            subItems: [
                {
                    id: 'system-statistics',
                    title: 'Statistics',
                    icon: <BarChart3 className="w-4 h-4" />,
                    path: '/admin/system/statistics'
                },
                {
                    id: 'system-security',
                    title: 'Security',
                    icon: <Shield className="w-4 h-4" />,
                    path: '/admin/system/security'
                }
            ]
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