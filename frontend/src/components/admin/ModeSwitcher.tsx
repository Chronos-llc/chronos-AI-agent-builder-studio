import { useState } from 'react'
import { AdminMode } from '../../types/admin'
import { Button } from '../ui/button'
import { 
    Users, 
    UserPlus, 
    ShoppingCart, 
    BrainCircuit, 
    Package, 
    MessageSquare, 
    CreditCard, 
    Settings 
} from 'lucide-react'

export const ModeSwitcher = ({ 
    currentMode, 
    onModeChange 
}: { 
    currentMode: AdminMode 
    onModeChange: (mode: AdminMode) => void 
}) => {
    const modes: { 
        mode: AdminMode 
        label: string 
        icon: React.ReactNode 
        description: string 
    }[] = [
        {
            mode: 'meta-agents',
            label: 'Meta Agents',
            icon: <Users className="w-4 h-4" />,
            description: 'Manage meta agents and their configurations'
        },
        {
            mode: 'subagents',
            label: 'Subagents',
            icon: <UserPlus className="w-4 h-4" />,
            description: 'Create and manage subagents'
        },
        {
            mode: 'marketplace',
            label: 'Marketplace',
            icon: <ShoppingCart className="w-4 h-4" />,
            description: 'Administer marketplace listings and categories'
        },
        {
            mode: 'skills',
            label: 'Skills',
            icon: <BrainCircuit className="w-4 h-4" />,
            description: 'Manage agent skills and capabilities'
        },
        {
            mode: 'platform-updates',
            label: 'Platform Updates',
            icon: <Package className="w-4 h-4" />,
            description: 'Handle platform updates and versioning'
        },
        {
            mode: 'support',
            label: 'Support',
            icon: <MessageSquare className="w-4 h-4" />,
            description: 'Manage support tickets and user assistance'
        },
        {
            mode: 'payments',
            label: 'Payments',
            icon: <CreditCard className="w-4 h-4" />,
            description: 'Handle billing, payments, and subscriptions'
        }
    ]

    return (
        <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="text-sm font-medium mb-3 px-2 text-muted-foreground">
                Admin Modes
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {modes.map((mode) => (
                    <Button
                        key={mode.mode}
                        variant={currentMode === mode.mode ? 'default' : 'outline'}
                        size="sm"
                        className={`justify-start gap-2 h-10 ${currentMode === mode.mode ? 'bg-primary text-primary-foreground' : ''}`}
                        onClick={() => onModeChange(mode.mode)}
                        title={mode.description}
                    >
                        {mode.icon}
                        <span className="truncate">{mode.label}</span>
                    </Button>
                ))}
            </div>
        </div>
    )
}