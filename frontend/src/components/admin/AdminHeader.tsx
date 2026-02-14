import { useState } from 'react'
import { AdminUser, AdminAlert } from '../../types/admin'
import { Button } from '../ui/button'
import { 
    Bell, 
    User, 
    Settings, 
    LogOut, 
    Search, 
    Menu,
    Repeat2,
    Check,
    X,
} from 'lucide-react'
import { Input } from '../ui/input'
import { 
    DropdownMenu, 
    DropdownMenuContent, 
    DropdownMenuItem, 
    DropdownMenuTrigger 
} from '../ui/dropdown-menu'
import ThemeSwitcher from '../theme/ThemeSwitcher'

export const AdminHeader = ({ 
    user, 
    alerts, 
    onSearch,
    onProfile,
    onSettings,
    onSwitchProfile,
    onMarkAlertRead,
    onDismissAlert,
    onClearAlerts,
    onLogout,
    onToggleSidebar,
}: { 
    user: AdminUser 
    alerts?: AdminAlert[] 
    onSearch?: (query: string) => void 
    onProfile?: () => void
    onSettings?: () => void
    onSwitchProfile?: () => void
    onMarkAlertRead?: (alertId: string) => void
    onDismissAlert?: (alertId: string) => void
    onClearAlerts?: () => void
    onLogout?: () => void
    onToggleSidebar?: () => void
}) => {
    const [searchQuery, setSearchQuery] = useState('')

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault()
        if (onSearch && searchQuery.trim()) {
            onSearch(searchQuery.trim())
        }
    }

    const unreadAlerts = alerts?.filter(alert => !alert.isRead).length || 0

    return (
        <header className="bg-card border-b border-border flex items-center justify-between px-4 py-3 h-16">
            {/* Mobile menu button */}
            <div className="md:hidden">
                <Button 
                    variant="ghost" 
                    size="icon" 
                    onClick={onToggleSidebar}
                    aria-label="Toggle sidebar"
                >
                    <Menu className="w-5 h-5" />
                </Button>
            </div>

            {/* Search bar */}
            <div className="flex-1 max-w-md mx-4">
                <form onSubmit={handleSearch} className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                        type="search"
                        placeholder="Search admin functions..."
                        className="pl-10 pr-4 w-full bg-background"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </form>
            </div>

            {/* User actions */}
            <div className="flex items-center gap-3">
                {/* Alerts */}
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="relative">
                            <Bell className="w-5 h-5" />
                            {unreadAlerts > 0 && (
                                <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center">
                                    {unreadAlerts}
                                </span>
                            )}
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-80">
                        <div className="p-2">
                            <div className="mb-2 flex items-center justify-between">
                                <h4 className="font-medium">Alerts</h4>
                                {alerts && alerts.length > 0 && (
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className="h-7 px-2 text-xs"
                                        onClick={onClearAlerts}
                                    >
                                        Clear all
                                    </Button>
                                )}
                            </div>
                            {alerts && alerts.length > 0 ? (
                                <div className="space-y-2 max-h-64 overflow-auto">
                                    {alerts.slice(0, 5).map((alert) => (
                                        <div
                                            key={alert.id}
                                            className={`rounded-md border px-2 py-2 ${alert.isRead ? 'opacity-70' : ''}`}
                                        >
                                            <div className="flex items-start gap-2">
                                            <div className={`w-2 h-2 rounded-full mt-1 ${alert.type === 'error' ? 'bg-red-500' : alert.type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'}`} />
                                            <div className="flex-1">
                                                <p className="font-medium text-sm">{alert.title}</p>
                                                <p className="text-xs text-muted-foreground truncate">{alert.message}</p>
                                            </div>
                                                <div className="flex items-center gap-1">
                                                    {!alert.isRead && (
                                                        <Button
                                                            variant="ghost"
                                                            size="icon"
                                                            className="h-6 w-6"
                                                            title="Mark as read"
                                                            onClick={() => onMarkAlertRead?.(alert.id)}
                                                        >
                                                            <Check className="h-3.5 w-3.5" />
                                                        </Button>
                                                    )}
                                                    <Button
                                                        variant="ghost"
                                                        size="icon"
                                                        className="h-6 w-6"
                                                        title="Dismiss alert"
                                                        onClick={() => onDismissAlert?.(alert.id)}
                                                    >
                                                        <X className="h-3.5 w-3.5" />
                                                    </Button>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-sm text-muted-foreground py-2">No alerts</p>
                            )}
                        </div>
                    </DropdownMenuContent>
                </DropdownMenu>

                {/* User menu */}
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="flex items-center gap-2">
                            <User className="w-5 h-5" />
                            <span className="font-medium text-sm">{user.name}</span>
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-48">
                        <DropdownMenuItem onClick={onProfile}>
                            <User className="w-4 h-4 mr-2" />
                            Profile
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={onSettings}>
                            <Settings className="w-4 h-4 mr-2" />
                            Settings
                        </DropdownMenuItem>
                        <div className="px-2 py-2">
                            <p className="mb-1 text-xs font-medium text-muted-foreground">Theme</p>
                            <ThemeSwitcher compact className="w-full justify-center" />
                        </div>
                        <DropdownMenuItem onSelect={(event) => {
                            event.preventDefault()
                            onSwitchProfile?.()
                        }}>
                            <Repeat2 className="w-4 h-4 mr-2" />
                            Switch profile
                        </DropdownMenuItem>
                        <DropdownMenuItem
                            className="text-red-600 focus:text-red-600"
                            onSelect={(event) => {
                                event.preventDefault()
                                onLogout?.()
                            }}
                        >
                            <LogOut className="w-4 h-4 mr-2" />
                            Logout
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </header>
    )
}
