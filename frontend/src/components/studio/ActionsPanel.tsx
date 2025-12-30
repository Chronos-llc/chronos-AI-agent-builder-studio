import React, { useState, useEffect } from 'react'
import { Zap, GitBranch, Terminal, Plus, Edit, Trash2, Play, Save, X, Search, Filter, Code, Globe, CheckCircle, AlertTriangle, Clock, GitMerge, Cpu, Database, Loader2 } from 'lucide-react'

// Types
interface Action {
    id: number
    name: string
    description: string
    action_type: string
    status: string
    parameters?: any
    config?: any
    code?: string
    dependencies?: string[]
    timeout?: number
    created_at: string
    updated_at: string
}

interface Hook {
    id: number
    name: string
    description: string
    hook_type: string
    trigger: string
    status: string
    action_config: any
    priority: number
    is_global: boolean
    timeout: number
    created_at: string
    updated_at: string
}

export const ActionsPanel: React.FC<{ agentId: number }> = ({ agentId }) => {
    const [actions, setActions] = useState<Action[]>([])
    const [hooks, setHooks] = useState<Hook[]>([])
    const [activeTab, setActiveTab] = useState<'actions' | 'hooks'>('actions')
    const [isLoading, setIsLoading] = useState(true)
    const [showActionForm, setShowActionForm] = useState(false)
    const [showHookForm, setShowHookForm] = useState(false)

    // Mock data for development
    useEffect(() => {
        const mockActions: Action[] = [
            {
                id: 1,
                name: 'Web Search',
                description: 'Search the web for information',
                action_type: 'api_call',
                status: 'active',
                parameters: { search_engine: 'google' },
                config: { api_key: 'mock_key' },
                code: 'def web_search(query): return results',
                dependencies: ['requests'],
                timeout: 30,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            },
            {
                id: 2,
                name: 'Data Processing',
                description: 'Process and transform data',
                action_type: 'code_execution',
                status: 'draft',
                parameters: { format: 'json' },
                config: { memory_limit: '512MB' },
                code: 'def process_data(data): return processed_data',
                dependencies: ['pandas'],
                timeout: 60,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            }
        ]
        
        const mockHooks: Hook[] = [
            {
                id: 1,
                name: 'Input Validator',
                description: 'Validate input before execution',
                hook_type: 'validation',
                trigger: 'before_action',
                status: 'active',
                action_config: { required_fields: ['query'] },
                priority: 10,
                is_global: false,
                timeout: 5,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            },
            {
                id: 2,
                name: 'Error Logger',
                description: 'Log errors to monitoring system',
                hook_type: 'logging',
                trigger: 'on_error',
                status: 'active',
                action_config: { log_level: 'error' },
                priority: 5,
                is_global: true,
                timeout: 3,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            }
        ]
        
        setActions(mockActions)
        setHooks(mockHooks)
        setIsLoading(false)
    }, [agentId])

    const getActionTypeIcon = (type: string) => {
        switch (type) {
            case 'api_call': return <Globe className="w-4 h-4 text-blue-500" />
            case 'code_execution': return <Terminal className="w-4 h-4 text-green-500" />
            default: return <Code className="w-4 h-4 text-yellow-500" />
        }
    }

    const getHookTypeIcon = (type: string) => {
        switch (type) {
            case 'validation': return <CheckCircle className="w-4 h-4 text-green-500" />
            case 'logging': return <AlertTriangle className="w-4 h-4 text-red-500" />
            default: return <GitBranch className="w-4 h-4 text-purple-500" />
        }
    }

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'active': return <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">Active</span>
            case 'draft': return <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">Draft</span>
            default: return <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded-full">{status}</span>
        }
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="flex flex-col items-center gap-4">
                    <Loader2 className="w-8 h-8 animate-spin" />
                    <span>Loading Actions & Hooks...</span>
                </div>
            </div>
        )
    }

    return (
        <div className="flex flex-col h-full bg-card">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border">
                <div className="flex items-center gap-4">
                    <button
                        className={`flex items-center gap-2 px-3 py-1 rounded-md ${activeTab === 'actions' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        onClick={() => setActiveTab('actions')}
                    >
                        <Zap className="w-4 h-4" />
                        <span>Actions</span>
                        <span className="bg-secondary text-secondary-foreground text-xs px-2 py-1 rounded-full ml-1">{actions.length}</span>
                    </button>
                    <button
                        className={`flex items-center gap-2 px-3 py-1 rounded-md ${activeTab === 'hooks' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        onClick={() => setActiveTab('hooks')}
                    >
                        <GitBranch className="w-4 h-4" />
                        <span>Hooks</span>
                        <span className="bg-secondary text-secondary-foreground text-xs px-2 py-1 rounded-full ml-1">{hooks.length}</span>
                    </button>
                </div>
                <div className="flex items-center gap-2">
                    {activeTab === 'actions' && (
                        <button
                            onClick={() => setShowActionForm(true)}
                            className="flex items-center gap-2 px-3 py-1 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                        >
                            <Plus className="w-4 h-4" />
                            <span>New Action</span>
                        </button>
                    )}
                    {activeTab === 'hooks' && (
                        <button
                            onClick={() => setShowHookForm(true)}
                            className="flex items-center gap-2 px-3 py-1 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                        >
                            <Plus className="w-4 h-4" />
                            <span>New Hook</span>
                        </button>
                    )}
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-hidden">
                {activeTab === 'actions' && (
                    <div className="flex flex-col h-full">
                        <div className="p-4 border-b border-border">
                            <div className="flex items-center gap-2 mb-3">
                                <Search className="w-4 h-4 text-muted-foreground" />
                                <input
                                    type="text"
                                    placeholder="Search actions..."
                                    className="flex-1 px-3 py-2 border border-input rounded-md bg-background text-foreground text-sm"
                                />
                            </div>
                        </div>

                        <div className="flex-1 overflow-auto p-4">
                            {actions.length === 0 ? (
                                <div className="text-center py-8 text-muted-foreground">
                                    <Zap className="w-8 h-8 mx-auto mb-2" />
                                    <p>No actions created yet</p>
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {actions.map(action => (
                                        <div key={action.id} className="border border-border rounded-lg p-4 hover:shadow-md transition-shadow">
                                            <div className="flex items-center justify-between mb-2">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-8 h-8 flex items-center justify-center bg-secondary rounded-md">
                                                        {getActionTypeIcon(action.action_type)}
                                                    </div>
                                                    <div>
                                                        <h4 className="font-medium">{action.name}</h4>
                                                        <p className="text-xs text-muted-foreground">{action.action_type.replace('_', ' ')}</p>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    {getStatusBadge(action.status)}
                                                    <button className="p-1 rounded-md hover:bg-accent text-muted-foreground">
                                                        <Play className="w-4 h-4" />
                                                    </button>
                                                    <button className="p-1 rounded-md hover:bg-accent text-muted-foreground">
                                                        <Edit className="w-4 h-4" />
                                                    </button>
                                                    <button className="p-1 rounded-md hover:bg-accent text-muted-foreground">
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            </div>
                                            <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                                                {action.description}
                                            </p>
                                            <div className="flex items-center justify-between text-xs text-muted-foreground">
                                                <div className="flex items-center gap-2">
                                                    <Clock className="w-3 h-3" />
                                                    <span>{action.timeout}s timeout</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <Code className="w-3 h-3" />
                                                    <span>{action.dependencies?.length || 0} dependencies</span>
                                                </div>
                                            </div>
                                            {action.code && (
                                                <div className="mt-3 p-2 bg-secondary rounded-md text-xs font-mono line-clamp-3">
                                                    {action.code}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {activeTab === 'hooks' && (
                    <div className="flex flex-col h-full">
                        <div className="p-4 border-b border-border">
                            <div className="flex items-center gap-2 mb-3">
                                <Search className="w-4 h-4 text-muted-foreground" />
                                <input
                                    type="text"
                                    placeholder="Search hooks..."
                                    className="flex-1 px-3 py-2 border border-input rounded-md bg-background text-foreground text-sm"
                                />
                            </div>
                        </div>

                        <div className="flex-1 overflow-auto p-4">
                            {hooks.length === 0 ? (
                                <div className="text-center py-8 text-muted-foreground">
                                    <GitBranch className="w-8 h-8 mx-auto mb-2" />
                                    <p>No hooks created yet</p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {hooks.map(hook => (
                                        <div key={hook.id} className="border border-border rounded-lg p-4 hover:shadow-md transition-shadow">
                                            <div className="flex items-center justify-between mb-2">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-8 h-8 flex items-center justify-center bg-secondary rounded-md">
                                                        {getHookTypeIcon(hook.hook_type)}
                                                    </div>
                                                    <div>
                                                        <h4 className="font-medium">{hook.name}</h4>
                                                        <p className="text-xs text-muted-foreground">{hook.hook_type} • {hook.trigger}</p>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    {getStatusBadge(hook.status)}
                                                    {hook.is_global && (
                                                        <span className="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">Global</span>
                                                    )}
                                                    <button className="p-1 rounded-md hover:bg-accent text-muted-foreground">
                                                        <Play className="w-4 h-4" />
                                                    </button>
                                                    <button className="p-1 rounded-md hover:bg-accent text-muted-foreground">
                                                        <Edit className="w-4 h-4" />
                                                    </button>
                                                    <button className="p-1 rounded-md hover:bg-accent text-muted-foreground">
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            </div>
                                            <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                                                {hook.description}
                                            </p>
                                            <div className="flex items-center justify-between text-xs text-muted-foreground">
                                                <div className="flex items-center gap-2">
                                                    <GitMerge className="w-3 h-3" />
                                                    <span>Priority: {hook.priority}</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <Clock className="w-3 h-3" />
                                                    <span>{hook.timeout}s timeout</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* Action Form Modal */}
            {showActionForm && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-card border border-border rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
                        <div className="flex items-center justify-between p-4 border-b border-border">
                            <h2 className="font-semibold flex items-center gap-2">
                                <Zap className="w-4 h-4" />
                                <span>Create New Action</span>
                            </h2>
                            <button
                                onClick={() => setShowActionForm(false)}
                                className="p-1 rounded-md hover:bg-accent"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-auto p-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Name</label>
                                    <input
                                        type="text"
                                        className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
                                        placeholder="Action name"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Type</label>
                                    <select className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground">
                                        <option value="function">Function</option>
                                        <option value="api_call">API Call</option>
                                        <option value="code_execution">Code Execution</option>
                                    </select>
                                </div>
                            </div>

                            <div className="mb-4">
                                <label className="block text-sm font-medium mb-1">Description</label>
                                <textarea
                                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground min-h-[60px]"
                                    placeholder="Describe what this action does"
                                />
                            </div>

                            <div className="mb-4">
                                <label className="block text-sm font-medium mb-1">Code</label>
                                <textarea
                                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground min-h-[150px] font-mono text-sm"
                                    placeholder="def my_function():
    # Write your code here
    return result"
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Timeout (seconds)</label>
                                    <input
                                        type="number"
                                        defaultValue={30}
                                        className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Dependencies</label>
                                    <input
                                        type="text"
                                        className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
                                        placeholder="Comma-separated dependencies"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="border-t border-border p-4 flex justify-end gap-2">
                            <button
                                onClick={() => setShowActionForm(false)}
                                className="px-4 py-2 bg-secondary rounded-md hover:bg-secondary/80"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => setShowActionForm(false)}
                                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                            >
                                <Save className="w-4 h-4 inline-block mr-1" />
                                Save Action
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Hook Form Modal */}
            {showHookForm && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-card border border-border rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
                        <div className="flex items-center justify-between p-4 border-b border-border">
                            <h2 className="font-semibold flex items-center gap-2">
                                <GitBranch className="w-4 h-4" />
                                <span>Create New Hook</span>
                            </h2>
                            <button
                                onClick={() => setShowHookForm(false)}
                                className="p-1 rounded-md hover:bg-accent"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-auto p-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Name</label>
                                    <input
                                        type="text"
                                        className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
                                        placeholder="Hook name"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Type</label>
                                    <select className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground">
                                        <option value="validation">Validation</option>
                                        <option value="logging">Logging</option>
                                        <option value="error_handler">Error Handler</option>
                                    </select>
                                </div>
                            </div>

                            <div className="mb-4">
                                <label className="block text-sm font-medium mb-1">Description</label>
                                <textarea
                                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground min-h-[60px]"
                                    placeholder="Describe what this hook does"
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Trigger</label>
                                    <select className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground">
                                        <option value="before_action">Before Action</option>
                                        <option value="after_action">After Action</option>
                                        <option value="on_error">On Error</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Priority</label>
                                    <input
                                        type="number"
                                        defaultValue={0}
                                        className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
                                    />
                                </div>
                            </div>

                            <div className="mb-4">
                                <label className="block text-sm font-medium mb-1">Configuration</label>
                                <textarea
                                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground min-h-[100px] font-mono text-sm"
                                    placeholder="Hook configuration JSON"
                                />
                            </div>

                            <div className="flex items-center gap-2 mb-4">
                                <input type="checkbox" id="isGlobal" className="rounded" />
                                <label htmlFor="isGlobal" className="text-sm">Is Global Hook</label>
                            </div>
                        </div>

                        <div className="border-t border-border p-4 flex justify-end gap-2">
                            <button
                                onClick={() => setShowHookForm(false)}
                                className="px-4 py-2 bg-secondary rounded-md hover:bg-secondary/80"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => setShowHookForm(false)}
                                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                            >
                                <Save className="w-4 h-4 inline-block mr-1" />
                                Save Hook
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}