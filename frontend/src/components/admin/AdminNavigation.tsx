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
    FolderPlus,
    ClipboardCheck,
    LayoutList,
    Store,
    Upload,
    BarChart3,
    Package,
    MessageSquare,
    CreditCard,
    Settings
} from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'

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

    const defaultItems: AdminNavigationItem[] = useMemo(() => [
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
            id: 'integrations',
            title: 'Integrations',
            icon: <ClipboardCheck className="w-4 h-4" />,
            path: '/app/admin/integrations-manage',
            subItems: [
                {
                    id: 'integrations-manage',
                    title: 'Manage Integrations',
                    icon: <LayoutList className="w-4 h-4" />,
                    path: '/app/admin/integrations-manage'
                },
                {
                    id: 'integrations-create',
                    title: 'Create Integrations',
                    icon: <FolderPlus className="w-4 h-4" />,
                    path: '/app/admin/integrations-create'
                },
                {
                    id: 'integrations-review',
                    title: 'Review Uploaded Integrations',
                    icon: <ClipboardCheck className="w-4 h-4" />,
                    path: '/app/admin/integrations-review'
                },
            ],
        },
        {
            id: 'skills',
            title: 'Skills',
            icon: <BrainCircuit className="w-4 h-4" />,
            path: '/app/admin/skills-marketplace',
            subItems: [
                {
                    id: 'skills-marketplace',
                    title: 'Skill Marketplace',
                    icon: <Store className="w-4 h-4" />,
                    path: '/app/admin/skills-marketplace'
                },
                {
                    id: 'skills-publish',
                    title: 'Publish Skill',
                    icon: <Upload className="w-4 h-4" />,
                    path: '/app/admin/skills-publish'
                },
                {
                    id: 'skills-review',
                    title: 'Review Uploaded Skill',
                    icon: <ClipboardCheck className="w-4 h-4" />,
                    path: '/app/admin/skills-review'
                },
                {
                    id: 'skills-statistics',
                    title: 'Statistics',
                    icon: <BarChart3 className="w-4 h-4" />,
                    path: '/app/admin/skills-statistics'
                }
            ]
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
    ], [])

    const navigationItems = items.length > 0 ? items : defaultItems

    const collectParentIdsForActive = (nodes: AdminNavigationItem[], targetId?: string, ancestry: string[] = []): string[] => {
        if (!targetId) return []
        for (const node of nodes) {
            const nextAncestry = [...ancestry, node.id]
            if (node.id === targetId) {
                return ancestry
            }
            if (node.subItems?.length) {
                const found = collectParentIdsForActive(node.subItems, targetId, nextAncestry)
                if (found.length) {
                    return found
                }
            }
        }
        return []
    }

    useEffect(() => {
        if (!activeItemId) return
        const parentIds = collectParentIdsForActive(navigationItems, activeItemId)
        if (!parentIds.length) return
        setExpandedItems((prev) => {
            const next = new Set(prev)
            parentIds.forEach((id) => next.add(id))
            return next
        })
    }, [activeItemId, navigationItems])

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
        const isActiveDescendant = Boolean(
            item.subItems?.some((subItem) => subItem.id === activeItemId)
        )
        const isActive = activeItemId === item.id || isActiveDescendant

        return (
            <div key={item.id} className={collapsed ? '' : `${level > 0 ? 'ml-6' : ''}`}>
                <Button
                    variant={isActive ? 'secondary' : 'ghost'}
                    size="sm"
                    data-testid={`admin-nav-${item.id}`}
                    title={collapsed ? item.title : undefined}
                className={`h-10 w-full ${collapsed ? 'justify-center px-2' : 'justify-start gap-2'} text-[15px] ${isActive ? 'bg-accent' : 'hover:bg-accent'}`}
                onClick={() => {
                    if (shouldExpand) {
                        toggleExpand(item.id)
                        if (item.path) {
                            onNavigate(item.path)
                        }
                    } else if (item.path) {
                        onNavigate(item.path)
                    }
                }}
            >
                    {item.icon}
                    {!collapsed && <span className="flex-1 truncate text-left">{item.title}</span>}
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
