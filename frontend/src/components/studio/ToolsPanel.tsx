import React, { useState, useEffect } from 'react'
import { Code, Search, Plus, Settings, Trash2, Download, Check, X, AlertTriangle, Info, HelpCircle, Star, MoreVertical, ChevronDown, Grid, List, Globe, MessageSquare, Book, Box, Database, File, Mail, Loader2, Plug, Power } from 'lucide-react'

interface ToolIntegration {
    id: string
    name: string
    description: string
    type: string
    category: string
    icon: string
    is_installed: boolean
    is_enabled: boolean
    config: any
    version: string
    author: string
    rating: number
    download_count: number
    last_updated: string
    documentation_url: string
    support_url: string
}

interface ToolsPanelProps {
    tools: ToolIntegration[]
    onToolsChange: (tools: ToolIntegration[]) => void
    onToolInstall: (toolId: string) => void
    onToolUninstall: (toolId: string) => void
}

export const ToolsPanel: React.FC<ToolsPanelProps> = ({
    tools: initialTools,
    onToolsChange,
    onToolInstall,
    onToolUninstall
}) => {
    const [tools, setTools] = useState<ToolIntegration[]>(initialTools)
    const [searchQuery, setSearchQuery] = useState('')
    const [filterCategory, setFilterCategory] = useState('all')
    const [filterType, setFilterType] = useState('all')
    const [sortBy, setSortBy] = useState<'name' | 'rating' | 'downloads' | 'updated'>('name')
    const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc')
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
    const [showToolDetails, setShowToolDetails] = useState<string | null>(null)
    const [showInstallDialog, setShowInstallDialog] = useState<string | null>(null)
    const [showConfigDialog, setShowConfigDialog] = useState<string | null>(null)
    const [showMarketplace, setShowMarketplace] = useState(false)
    const [marketplaceTools, setMarketplaceTools] = useState<ToolIntegration[]>([])
    const [isLoadingMarketplace, setIsLoadingMarketplace] = useState(false)

    // Form state for configuration dialog
    const [formConfig, setFormConfig] = useState({
        apiEndpoint: '',
        apiKey: '',
        timeout: 5000,
        maxRetries: 3,
        customHeaders: '',
        rateLimitingEnabled: false,
        rateLimitingMaxRequests: 100,
        rateLimitingTimeWindow: 60,
        debugLogging: true,
        logRequests: false,
        logErrorsOnly: false
    })

    // Update tools when props change
    useEffect(() => {
        setTools(initialTools)
    }, [initialTools])

    // Initialize form state when config dialog opens
    useEffect(() => {
        if (showConfigDialog) {
            const tool = tools.find(t => t.id === showConfigDialog)
            if (tool) {
                setFormConfig({
                    apiEndpoint: tool.config.apiEndpoint || '',
                    apiKey: tool.config.apiKey || '',
                    timeout: tool.config.timeout || 5000,
                    maxRetries: tool.config.maxRetries || 3,
                    customHeaders: tool.config.customHeaders ? JSON.stringify(tool.config.customHeaders, null, 2) : '',
                    rateLimitingEnabled: tool.config.rateLimiting?.enabled || false,
                    rateLimitingMaxRequests: tool.config.rateLimiting?.maxRequests || 100,
                    rateLimitingTimeWindow: tool.config.rateLimiting?.timeWindow || 60,
                    debugLogging: tool.config.logging?.debug || true,
                    logRequests: tool.config.logging?.requests || false,
                    logErrorsOnly: tool.config.logging?.errorsOnly || false
                })
            }
        }
    }, [showConfigDialog, tools])

    // Filter and sort tools
    const filteredTools = tools.filter(tool => {
        const matchesSearch = tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            tool.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
            tool.author.toLowerCase().includes(searchQuery.toLowerCase())
        const matchesCategory = filterCategory === 'all' || tool.category === filterCategory
        const matchesType = filterType === 'all' || tool.type === filterType
        return matchesSearch && matchesCategory && matchesType
    }).sort((a, b) => {
        let comparison = 0

        switch (sortBy) {
            case 'name':
                comparison = a.name.localeCompare(b.name)
                break
            case 'rating':
                comparison = b.rating - a.rating
                break
            case 'downloads':
                comparison = b.download_count - a.download_count
                break
            case 'updated':
                comparison = new Date(b.last_updated).getTime() - new Date(a.last_updated).getTime()
                break
        }

        return sortDirection === 'asc' ? comparison : -comparison
    })

    // Handle tool installation
    const handleInstallTool = (toolId: string) => {
        setTools(prev => prev.map(tool =>
            tool.id === toolId ? { ...tool, is_installed: true, is_enabled: true } : tool
        ))
        onToolsChange(tools.map(tool =>
            tool.id === toolId ? { ...tool, is_installed: true, is_enabled: true } : tool
        ))
        onToolInstall(toolId)
        setShowInstallDialog(null)
    }

    // Handle tool uninstall
    const handleUninstallTool = (toolId: string) => {
        setTools(prev => prev.map(tool =>
            tool.id === toolId ? { ...tool, is_installed: false, is_enabled: false } : tool
        ))
        onToolsChange(tools.map(tool =>
            tool.id === toolId ? { ...tool, is_installed: false, is_enabled: false } : tool
        ))
        onToolUninstall(toolId)
    }

    // Handle tool enable/disable
    const handleToggleTool = (toolId: string) => {
        setTools(prev => prev.map(tool =>
            tool.id === toolId ? { ...tool, is_enabled: !tool.is_enabled } : tool
        ))
        onToolsChange(tools.map(tool =>
            tool.id === toolId ? { ...tool, is_enabled: !tool.is_enabled } : tool
        ))
    }

    // Handle tool configuration
    const handleConfigureTool = (toolId: string, config: any) => {
        setTools(prev => prev.map(tool =>
            tool.id === toolId ? { ...tool, config } : tool
        ))
        onToolsChange(tools.map(tool =>
            tool.id === toolId ? { ...tool, config } : tool
        ))
        setShowConfigDialog(null)
    }

    // Load marketplace tools (simulated)
    const loadMarketplaceTools = () => {
        setIsLoadingMarketplace(true)
        setShowMarketplace(true)

        // Simulate API call
        setTimeout(() => {
            const mockMarketplaceTools: ToolIntegration[] = [
                {
                    id: 'market-1',
                    name: 'Advanced Web Search',
                    description: 'Enhanced web search with semantic understanding and multi-source aggregation',
                    type: 'search',
                    category: 'information',
                    icon: '🌐',
                    is_installed: false,
                    is_enabled: false,
                    config: {},
                    version: '2.1.0',
                    author: 'SearchTech Inc.',
                    rating: 4.8,
                    download_count: 12543,
                    last_updated: '2023-11-15T10:30:00Z',
                    documentation_url: 'https://searchtech.com/docs',
                    support_url: 'https://searchtech.com/support'
                },
                {
                    id: 'market-2',
                    name: 'Code Interpreter Pro',
                    description: 'Advanced Python code execution with sandboxed environment and library support',
                    type: 'code',
                    category: 'development',
                    icon: '🐍',
                    is_installed: false,
                    is_enabled: false,
                    config: {},
                    version: '1.5.2',
                    author: 'DevTools Co.',
                    rating: 4.9,
                    download_count: 8721,
                    last_updated: '2023-12-05T14:20:00Z',
                    documentation_url: 'https://devtools.com/docs',
                    support_url: 'https://devtools.com/support'
                },
                {
                    id: 'market-3',
                    name: 'Database Connector',
                    description: 'Universal database connector with SQL and NoSQL support',
                    type: 'database',
                    category: 'data',
                    icon: '🗃️',
                    is_installed: false,
                    is_enabled: false,
                    config: {},
                    version: '3.0.1',
                    author: 'DataSystems Ltd.',
                    rating: 4.5,
                    download_count: 5432,
                    last_updated: '2023-10-28T09:15:00Z',
                    documentation_url: 'https://datasystems.com/docs',
                    support_url: 'https://datasystems.com/support'
                },
                {
                    id: 'market-4',
                    name: 'API Gateway',
                    description: 'REST and GraphQL API integration with authentication support',
                    type: 'api',
                    category: 'integration',
                    icon: '🔌',
                    is_installed: false,
                    is_enabled: false,
                    config: {},
                    version: '1.2.3',
                    author: 'API Solutions',
                    rating: 4.7,
                    download_count: 7654,
                    last_updated: '2023-11-30T16:45:00Z',
                    documentation_url: 'https://apisolutions.com/docs',
                    support_url: 'https://apisolutions.com/support'
                },
                {
                    id: 'market-5',
                    name: 'Email Processor',
                    description: 'Email parsing, composition, and sending with attachment support',
                    type: 'email',
                    category: 'communication',
                    icon: '✉️',
                    is_installed: false,
                    is_enabled: false,
                    config: {},
                    version: '2.3.0',
                    author: 'MailTech',
                    rating: 4.6,
                    download_count: 4321,
                    last_updated: '2023-09-18T11:25:00Z',
                    documentation_url: 'https://mailtech.com/docs',
                    support_url: 'https://mailtech.com/support'
                }
            ]
            setMarketplaceTools(mockMarketplaceTools)
            setIsLoadingMarketplace(false)
        }, 1000)
    }

    // Get tool icon
    const getToolIcon = (type: string) => {
        switch (type) {
            case 'search': return <Search className="w-4 h-4 text-blue-500" />
            case 'code': return <Code className="w-4 h-4 text-green-500" />
            case 'database': return <Database className="w-4 h-4 text-purple-500" />
            case 'api': return <Plug className="w-4 h-4 text-yellow-500" />
            case 'email': return <Mail className="w-4 h-4 text-red-500" />
            case 'file': return <File className="w-4 h-4 text-indigo-500" />
            case 'web': return <Globe className="w-4 h-4 text-orange-500" />
            default: return <Code className="w-4 h-4" />
        }
    }

    // Get category icon
    const getCategoryIcon = (category: string) => {
        switch (category) {
            case 'information': return <Info className="w-4 h-4 text-blue-500" />
            case 'development': return <Code className="w-4 h-4 text-green-500" />
            case 'data': return <Database className="w-4 h-4 text-purple-500" />
            case 'integration': return <Plug className="w-4 h-4 text-yellow-500" />
            case 'communication': return <MessageSquare className="w-4 h-4 text-red-500" />
            case 'utility': return <Settings className="w-4 h-4 text-gray-500" />
            default: return <Box className="w-4 h-4" />
        }
    }

    // Get available categories
    const availableCategories = Array.from(new Set([
        'all',
        ...tools.map(tool => tool.category),
        ...marketplaceTools.map(tool => tool.category)
    ]))

    // Get available types
    const availableTypes = Array.from(new Set([
        'all',
        ...tools.map(tool => tool.type),
        ...marketplaceTools.map(tool => tool.type)
    ]))

    return (
        <div className="tools-panel h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-3 border-b border-border bg-card">
                <h2 className="font-semibold flex items-center gap-2">
                    <Code className="w-4 h-4" />
                    <span>Tools & Integrations</span>
                </h2>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                        className="p-1 rounded-md hover:bg-accent"
                        title={viewMode === 'grid' ? 'Switch to list view' : 'Switch to grid view'}
                    >
                        {viewMode === 'grid' ? <List className="w-4 h-4" /> : <Grid className="w-4 h-4" />}
                    </button>
                    <button
                        onClick={loadMarketplaceTools}
                        className="flex items-center gap-2 px-3 py-1 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                    >
                        <Plus className="w-4 h-4" />
                        <span>Browse Marketplace</span>
                    </button>
                </div>
            </div>

            {/* Search and Filters */}
            <div className="p-3 border-b border-border">
                <div className="flex items-center gap-2 mb-3">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <input
                            type="text"
                            placeholder="Search tools..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-9 pr-3 py-2 border border-input rounded-md bg-background text-foreground text-sm"
                        />
                    </div>

                    <div className="relative">
                        <select
                            title="Filter by category"
                            value={filterCategory}
                            onChange={(e) => setFilterCategory(e.target.value)}
                            className="pl-3 pr-8 py-2 border border-input rounded-md bg-background text-foreground text-sm appearance-none"
                        >
                            {availableCategories.map(category => (
                                <option key={category} value={category}>
                                    {category === 'all' ? 'All Categories' : category.charAt(0).toUpperCase() + category.slice(1)}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
                    </div>

                    <div className="relative">
                        <select
                            title="Filter by type"
                            value={filterType}
                            onChange={(e) => setFilterType(e.target.value)}
                            className="pl-3 pr-8 py-2 border border-input rounded-md bg-background text-foreground text-sm appearance-none"
                        >
                            {availableTypes.map(type => (
                                <option key={type} value={type}>
                                    {type === 'all' ? 'All Types' : type.charAt(0).toUpperCase() + type.slice(1)}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
                    </div>

                    <div className="relative">
                        <select
                            title="Sort tools by"
                            value={`${sortBy}-${sortDirection}`}
                            onChange={(e) => {
                                const [newSortBy, newSortDirection] = e.target.value.split('-')
                                setSortBy(newSortBy as any)
                                setSortDirection(newSortDirection as any)
                            }}
                            className="pl-3 pr-8 py-2 border border-input rounded-md bg-background text-foreground text-sm appearance-none"
                        >
                            <option value="name-asc">Name (A-Z)</option>
                            <option value="name-desc">Name (Z-A)</option>
                            <option value="rating-desc">Rating (High-Low)</option>
                            <option value="rating-asc">Rating (Low-High)</option>
                            <option value="downloads-desc">Downloads (High-Low)</option>
                            <option value="downloads-asc">Downloads (Low-High)</option>
                            <option value="updated-desc">Recently Updated</option>
                            <option value="updated-asc">Oldest Updated</option>
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
                    </div>
                </div>

                <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-2">
                        <span className="text-muted-foreground">View:</span>
                        <button
                            onClick={() => setViewMode('grid')}
                            className={`p-1 rounded-md ${viewMode === 'grid' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                            title="Grid view"
                        >
                            <Grid className="w-4 h-4" />
                        </button>
                        <button
                            onClick={() => setViewMode('list')}
                            className={`p-1 rounded-md ${viewMode === 'list' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                            title="List view"
                        >
                            <List className="w-4 h-4" />
                        </button>
                    </div>

                    <div className="flex items-center gap-2">
                        <span className="text-muted-foreground">Show:</span>
                        <button
                            onClick={() => setFilterCategory('all')}
                            className={`px-2 py-1 rounded-md text-sm ${filterCategory === 'all' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            All ({filteredTools.length})
                        </button>
                        <button
                            onClick={() => setFilterCategory('installed')}
                            className={`px-2 py-1 rounded-md text-sm ${filterCategory === 'installed' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            Installed ({tools.filter(t => t.is_installed).length})
                        </button>
                        <button
                            onClick={() => setFilterCategory('enabled')}
                            className={`px-2 py-1 rounded-md text-sm ${filterCategory === 'enabled' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            Enabled ({tools.filter(t => t.is_enabled).length})
                        </button>
                    </div>
                </div>
            </div>

            {/* Tools Content */}
            <div className="flex-1 overflow-auto p-3">
                {filteredTools.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                        <Code className="w-8 h-8 mx-auto mb-2" />
                        <p>No tools found</p>
                        <p className="text-sm mt-1">Try adjusting your search or filters</p>
                        <button
                            onClick={loadMarketplaceTools}
                            className="mt-4 flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                        >
                            <Plus className="w-4 h-4" />
                            <span>Browse Marketplace</span>
                        </button>
                    </div>
                ) : viewMode === 'grid' ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {filteredTools.map(tool => (
                            <div key={tool.id} className="border border-border rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                                <div className="p-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center gap-2">
                                            <div className="w-8 h-8 flex items-center justify-center bg-secondary rounded-md">
                                                <span className="text-lg">{tool.icon}</span>
                                            </div>
                                            <div>
                                                <h3 className="font-medium">{tool.name}</h3>
                                                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                                    <span>{tool.version}</span>
                                                    <span>•</span>
                                                    <span>{tool.author}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            {tool.is_installed && (
                                                <button
                                                    onClick={() => handleToggleTool(tool.id)}
                                                    className={`p-1 rounded-md ${tool.is_enabled ? 'bg-green-500 text-white' : 'bg-gray-500 text-white'}`}
                                                    title={tool.is_enabled ? 'Disable tool' : 'Enable tool'}
                                                >
                                                    <Power className="w-3 h-3" />
                                                </button>
                                            )}
                                            <button
                                                onClick={() => setShowToolDetails(tool.id)}
                                                className="p-1 rounded-md hover:bg-accent"
                                                title="View details"
                                            >
                                                <MoreVertical className="w-3 h-3" />
                                            </button>
                                        </div>
                                    </div>

                                    <p className="text-sm text-muted-foreground mb-3 line-clamp-3">
                                        {tool.description}
                                    </p>

                                    <div className="flex items-center justify-between mb-3">
                                        <div className="flex items-center gap-2">
                                            <div className="flex items-center gap-1">
                                                <Star className="w-3 h-3 text-yellow-500" />
                                                <span className="text-xs font-medium">{tool.rating}</span>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <Download className="w-3 h-3 text-blue-500" />
                                                <span className="text-xs text-muted-foreground">{tool.download_count.toLocaleString()}</span>
                                            </div>
                                        </div>
                                        <span className="text-xs text-muted-foreground">
                                            Updated {new Date(tool.last_updated).toLocaleDateString()}
                                        </span>
                                    </div>

                                    <div className="flex gap-2">
                                        {tool.is_installed ? (
                                            <>
                                                <button
                                                    onClick={() => setShowConfigDialog(tool.id)}
                                                    className="flex-1 flex items-center justify-center gap-1 px-3 py-1 text-sm bg-secondary rounded-md hover:bg-secondary/80"
                                                >
                                                    <Settings className="w-3 h-3" />
                                                    <span>Configure</span>
                                                </button>
                                                <button
                                                    onClick={() => handleUninstallTool(tool.id)}
                                                    className="flex-1 flex items-center justify-center gap-1 px-3 py-1 text-sm bg-destructive text-destructive-foreground rounded-md hover:bg-destructive/90"
                                                >
                                                    <Trash2 className="w-3 h-3" />
                                                    <span>Uninstall</span>
                                                </button>
                                            </>
                                        ) : (
                                            <button
                                                onClick={() => setShowInstallDialog(tool.id)}
                                                className="flex-1 flex items-center justify-center gap-1 px-3 py-1 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                                            >
                                                <Plus className="w-3 h-3" />
                                                <span>Install</span>
                                            </button>
                                        )}
                                    </div>

                                    {tool.is_installed && tool.is_enabled && (
                                        <div className="mt-3 p-2 bg-green-50 border border-green-200 rounded-md text-xs text-green-800 flex items-center gap-2">
                                            <Check className="w-3 h-3" />
                                            <span>Tool is enabled and active</span>
                                        </div>
                                    )}

                                    {tool.is_installed && !tool.is_enabled && (
                                        <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded-md text-xs text-yellow-800 flex items-center gap-2">
                                            <AlertTriangle className="w-3 h-3" />
                                            <span>Tool is installed but disabled</span>
                                        </div>
                                    )}
                                </div>

                                <div className="px-4 py-2 bg-secondary border-t border-border flex items-center justify-between text-xs">
                                    <div className="flex items-center gap-2">
                                        {getCategoryIcon(tool.category)}
                                        <span>{tool.category}</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {getToolIcon(tool.type)}
                                        <span>{tool.type}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="space-y-2">
                        {filteredTools.map(tool => (
                            <div key={tool.id} className="border border-border rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                                <div className="p-4">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3 flex-1">
                                            <div className="w-8 h-8 flex items-center justify-center bg-secondary rounded-md">
                                                <span className="text-lg">{tool.icon}</span>
                                            </div>
                                            <div className="flex-1">
                                                <h3 className="font-medium">{tool.name}</h3>
                                                <p className="text-sm text-muted-foreground line-clamp-1">
                                                    {tool.description}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <div className="flex items-center gap-1">
                                                <Star className="w-3 h-3 text-yellow-500" />
                                                <span className="text-xs font-medium">{tool.rating}</span>
                                            </div>
                                            {tool.is_installed && (
                                                <button
                                                    onClick={() => handleToggleTool(tool.id)}
                                                    className={`p-1 rounded-md ${tool.is_enabled ? 'bg-green-500 text-white' : 'bg-gray-500 text-white'}`}
                                                    title={tool.is_enabled ? 'Disable tool' : 'Enable tool'}
                                                >
                                                    <Power className="w-3 h-3" />
                                                </button>
                                            )}
                                            <button
                                                onClick={() => setShowToolDetails(tool.id)}
                                                className="p-1 rounded-md hover:bg-accent"
                                                title="View details"
                                            >
                                                <MoreVertical className="w-3 h-3" />
                                            </button>
                                        </div>
                                    </div>

                                    <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
                                        <div className="flex items-center gap-4">
                                            <span>{tool.version} • {tool.author}</span>
                                            <span>Updated {new Date(tool.last_updated).toLocaleDateString()}</span>
                                            <div className="flex items-center gap-1">
                                                <Download className="w-3 h-3" />
                                                <span>{tool.download_count.toLocaleString()} downloads</span>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            {getCategoryIcon(tool.category)}
                                            <span>{tool.category}</span>
                                            <span>•</span>
                                            {getToolIcon(tool.type)}
                                            <span>{tool.type}</span>
                                        </div>
                                    </div>

                                    <div className="mt-3 flex gap-2">
                                        {tool.is_installed ? (
                                            <>
                                                <button
                                                    onClick={() => setShowConfigDialog(tool.id)}
                                                    className="flex-1 flex items-center justify-center gap-1 px-3 py-1 text-sm bg-secondary rounded-md hover:bg-secondary/80"
                                                >
                                                    <Settings className="w-3 h-3" />
                                                    <span>Configure</span>
                                                </button>
                                                <button
                                                    onClick={() => handleUninstallTool(tool.id)}
                                                    className="flex-1 flex items-center justify-center gap-1 px-3 py-1 text-sm bg-destructive text-destructive-foreground rounded-md hover:bg-destructive/90"
                                                >
                                                    <Trash2 className="w-3 h-3" />
                                                    <span>Uninstall</span>
                                                </button>
                                            </>
                                        ) : (
                                            <button
                                                onClick={() => setShowInstallDialog(tool.id)}
                                                className="flex-1 flex items-center justify-center gap-1 px-3 py-1 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                                            >
                                                <Plus className="w-3 h-3" />
                                                <span>Install</span>
                                            </button>
                                        )}
                                    </div>

                                    {tool.is_installed && tool.is_enabled && (
                                        <div className="mt-3 p-2 bg-green-50 border border-green-200 rounded-md text-xs text-green-800 flex items-center gap-2">
                                            <Check className="w-3 h-3" />
                                            <span>Tool is enabled and active</span>
                                        </div>
                                    )}

                                    {tool.is_installed && !tool.is_enabled && (
                                        <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded-md text-xs text-yellow-800 flex items-center gap-2">
                                            <AlertTriangle className="w-3 h-3" />
                                            <span>Tool is installed but disabled</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Tool Details Dialog */}
            {showToolDetails && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-card border border-border rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
                        <div className="flex items-center justify-between p-4 border-b border-border">
                            <h3 className="font-semibold flex items-center gap-2">
                                <Info className="w-4 h-4" />
                                <span>Tool Details</span>
                            </h3>
                            <button
                                onClick={() => setShowToolDetails(null)}
                                className="p-1 rounded-md hover:bg-accent"
                                title="Close"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-auto p-4">
                            {tools.find(tool => tool.id === showToolDetails) && (
                                <div className="space-y-6">
                                    <div className="flex items-start gap-4">
                                        <div className="w-12 h-12 flex items-center justify-center bg-secondary rounded-lg">
                                            <span className="text-2xl">{tools.find(tool => tool.id === showToolDetails)!.icon}</span>
                                        </div>
                                        <div>
                                            <h4 className="text-xl font-bold mb-1">
                                                {tools.find(tool => tool.id === showToolDetails)!.name}
                                            </h4>
                                            <p className="text-sm text-muted-foreground mb-2">
                                                {tools.find(tool => tool.id === showToolDetails)!.description}
                                            </p>
                                            <div className="flex items-center gap-4 text-sm">
                                                <div className="flex items-center gap-1">
                                                    <Star className="w-3 h-3 text-yellow-500" />
                                                    <span>{tools.find(tool => tool.id === showToolDetails)!.rating} (Excellent)</span>
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    <Download className="w-3 h-3 text-blue-500" />
                                                    <span>{tools.find(tool => tool.id === showToolDetails)!.download_count.toLocaleString()} downloads</span>
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    <span>Version {tools.find(tool => tool.id === showToolDetails)!.version}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <h5 className="font-medium mb-2">Category</h5>
                                            <div className="flex items-center gap-2">
                                                {getCategoryIcon(tools.find(tool => tool.id === showToolDetails)!.category)}
                                                <span>{tools.find(tool => tool.id === showToolDetails)!.category}</span>
                                            </div>
                                        </div>
                                        <div>
                                            <h5 className="font-medium mb-2">Type</h5>
                                            <div className="flex items-center gap-2">
                                                {getToolIcon(tools.find(tool => tool.id === showToolDetails)!.type)}
                                                <span>{tools.find(tool => tool.id === showToolDetails)!.type}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <h5 className="font-medium mb-2">Author</h5>
                                        <p>{tools.find(tool => tool.id === showToolDetails)!.author}</p>
                                    </div>

                                    <div>
                                        <h5 className="font-medium mb-2">Last Updated</h5>
                                        <p>{new Date(tools.find(tool => tool.id === showToolDetails)!.last_updated).toLocaleString()}</p>
                                    </div>

                                    <div>
                                        <h5 className="font-medium mb-2">Links</h5>
                                        <div className="space-y-2">
                                            <a 
                                                href={tools.find(tool => tool.id === showToolDetails)!.documentation_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="flex items-center gap-2 text-blue-500 hover:underline"
                                            >
                                                <Book className="w-4 h-4" />
                                                <span>Documentation</span>
                                            </a>
                                            <a 
                                                href={tools.find(tool => tool.id === showToolDetails)!.support_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="flex items-center gap-2 text-green-500 hover:underline"
                                            >
                                                <HelpCircle className="w-4 h-4" />
                                                <span>Support</span>
                                            </a>
                                        </div>
                                    </div>

                                    <div>
                                        <h5 className="font-medium mb-2">Configuration</h5>
                                        <pre className="bg-secondary p-3 rounded-md text-sm overflow-x-auto">
                                            {JSON.stringify(tools.find(tool => tool.id === showToolDetails)!.config, null, 2)}
                                        </pre>
                                    </div>

                                    <div>
                                        <h5 className="font-medium mb-2">Status</h5>
                                        <div className="flex items-center gap-2">
                                            {tools.find(tool => tool.id === showToolDetails)!.is_installed ? (
                                                <Check className="w-4 h-4 text-green-500" />
                                            ) : (
                                                <X className="w-4 h-4 text-red-500" />
                                            )}
                                            <span>
                                                {tools.find(tool => tool.id === showToolDetails)!.is_installed ? 'Installed' : 'Not Installed'}
                                            </span>
                                            {tools.find(tool => tool.id === showToolDetails)!.is_installed && (
                                                <>
                                                    <span>•</span>
                                                    {tools.find(tool => tool.id === showToolDetails)!.is_enabled ? (
                                                        <Check className="w-4 h-4 text-green-500" />
                                                    ) : (
                                                        <X className="w-4 h-4 text-red-500" />
                                                    )}
                                                    <span>
                                                        {tools.find(tool => tool.id === showToolDetails)!.is_enabled ? 'Enabled' : 'Disabled'}
                                                    </span>
                                                </>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="border-t border-border p-4 flex justify-end gap-2">
                            <button
                                onClick={() => setShowToolDetails(null)}
                                className="px-4 py-2 bg-secondary rounded-md hover:bg-secondary/80"
                            >
                                Close
                            </button>
                            {tools.find(tool => tool.id === showToolDetails)!.is_installed ? (
                                <button
                                    onClick={() => setShowConfigDialog(showToolDetails)}
                                    className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                                >
                                    Configure
                                </button>
                            ) : (
                                <button
                                    onClick={() => setShowInstallDialog(showToolDetails)}
                                    className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                                >
                                    Install
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Install Tool Dialog */}
            {showInstallDialog && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-card border border-border rounded-lg w-full max-w-md">
                        <div className="flex items-center justify-between p-4 border-b border-border">
                            <h3 className="font-semibold flex items-center gap-2">
                                <Plus className="w-4 h-4" />
                                <span>Install Tool</span>
                            </h3>
                            <button
                                onClick={() => setShowInstallDialog(null)}
                                className="p-1 rounded-md hover:bg-accent"
                                title="Close"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="p-4 space-y-4">
                            {tools.find(tool => tool.id === showInstallDialog) && (
                                <div className="space-y-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 flex items-center justify-center bg-secondary rounded-md">
                                            <span className="text-xl">{tools.find(tool => tool.id === showInstallDialog)!.icon}</span>
                                        </div>
                                        <div>
                                            <h4 className="font-medium">{tools.find(tool => tool.id === showInstallDialog)!.name}</h4>
                                            <p className="text-sm text-muted-foreground">
                                                {tools.find(tool => tool.id === showInstallDialog)!.description}
                                            </p>
                                        </div>
                                    </div>

                                    <div>
                                        <h5 className="font-medium mb-2">Installation Options</h5>
                                        <div className="space-y-2">
                                            <label className="flex items-center gap-2">
                                                <input type="checkbox" defaultChecked className="rounded" />
                                                <span className="text-sm">Enable after installation</span>
                                            </label>
                                            <label className="flex items-center gap-2">
                                                <input type="checkbox" defaultChecked className="rounded" />
                                                <span className="text-sm">Load default configuration</span>
                                            </label>
                                            <label className="flex items-center gap-2">
                                                <input type="checkbox" className="rounded" />
                                                <span className="text-sm">Install dependencies automatically</span>
                                            </label>
                                        </div>
                                    </div>

                                    <div>
                                        <h5 className="font-medium mb-2">Version</h5>
                                        <select title="Select version" className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground">
                                            <option>Latest ({tools.find(tool => tool.id === showInstallDialog)!.version})</option>
                                            <option>Stable (1.0.0)</option>
                                            <option>Beta (2.0.0-beta)</option>
                                        </select>
                                    </div>

                                    <div className="p-3 bg-secondary rounded-md">
                                        <h5 className="font-medium mb-2">Requirements</h5>
                                        <ul className="text-sm space-y-1">
                                            <li className="flex items-center gap-2">
                                                <Check className="w-3 h-3 text-green-500" />
                                                <span>Minimum agent version: 1.0.0</span>
                                            </li>
                                            <li className="flex items-center gap-2">
                                                <Check className="w-3 h-3 text-green-500" />
                                                <span>Memory: 512MB</span>
                                            </li>
                                            <li className="flex items-center gap-2">
                                                <Check className="w-3 h-3 text-green-500" />
                                                <span>Network access required</span>
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="border-t border-border p-4 flex justify-end gap-2">
                            <button
                                onClick={() => setShowInstallDialog(null)}
                                className="px-4 py-2 bg-secondary rounded-md hover:bg-secondary/80"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => handleInstallTool(showInstallDialog!)}
                                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                            >
                                Install Tool
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Configure Tool Dialog */}
            {showConfigDialog && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-card border border-border rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
                        <div className="flex items-center justify-between p-4 border-b border-border">
                            <h3 className="font-semibold flex items-center gap-2">
                                <Settings className="w-4 h-4" />
                                <span>Configure Tool</span>
                            </h3>
                            <button
                                onClick={() => setShowConfigDialog(null)}
                                className="p-1 rounded-md hover:bg-accent"
                                title="Close"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-auto p-4">
                            {tools.find(tool => tool.id === showConfigDialog) && (
                                <div className="space-y-6">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 flex items-center justify-center bg-secondary rounded-md">
                                            <span className="text-xl">{tools.find(tool => tool.id === showConfigDialog)!.icon}</span>
                                        </div>
                                        <div>
                                            <h4 className="font-medium">{tools.find(tool => tool.id === showConfigDialog)!.name}</h4>
                                            <p className="text-sm text-muted-foreground">
                                                Configure the tool settings and parameters
                                            </p>
                                        </div>
                                    </div>

                                    <div>
                                        <h5 className="font-medium mb-2">Basic Configuration</h5>
                                        <div className="space-y-4">
                                            <div>
                                                <label className="block text-sm font-medium mb-1">API Endpoint</label>
                                                <input
                                                    type="text"
                                                    value={formConfig.apiEndpoint}
                                                    onChange={(e) => setFormConfig({ ...formConfig, apiEndpoint: e.target.value })}
                                                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
                                                    placeholder="https://api.example.com/v1"
                                                />
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium mb-1">API Key</label>
                                                <input
                                                    type="password"
                                                    value={formConfig.apiKey}
                                                    onChange={(e) => setFormConfig({ ...formConfig, apiKey: e.target.value })}
                                                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
                                                    placeholder="Enter your API key"
                                                />
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium mb-1">Timeout (ms)</label>
                                                <input
                                                    type="number"
                                                    title="Timeout in milliseconds"
                                                    value={formConfig.timeout}
                                                    onChange={(e) => setFormConfig({ ...formConfig, timeout: parseInt(e.target.value) || 5000 })}
                                                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground text-sm"
                                                    min="1000"
                                                    max="30000"
                                                />
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium mb-1">Max Retries</label>
                                                <input
                                                    type="number"
                                                    title="Maximum retry attempts"
                                                    value={formConfig.maxRetries}
                                                    onChange={(e) => setFormConfig({ ...formConfig, maxRetries: parseInt(e.target.value) || 3 })}
                                                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground text-sm"
                                                    min="0"
                                                    max="10"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <h5 className="font-medium mb-2">Advanced Settings</h5>
                                        <div className="space-y-4">
                                            <div>
                                                <label className="block text-sm font-medium mb-1">Custom Headers</label>
                                                <textarea
                                                    value={formConfig.customHeaders}
                                                    onChange={(e) => setFormConfig({ ...formConfig, customHeaders: e.target.value })}
                                                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground min-h-[80px] font-mono text-sm"
                                                    placeholder={`{
  "Authorization": "Bearer token",
  "X-Custom-Header": "value"
}`}
                                                />
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium mb-1">Rate Limiting</label>
                                                <div className="space-y-2">
                                                    <label className="flex items-center gap-2">
                                                        <input
                                                            type="checkbox"
                                                            checked={formConfig.rateLimitingEnabled}
                                                            onChange={(e) => setFormConfig({ ...formConfig, rateLimitingEnabled: e.target.checked })}
                                                            className="rounded"
                                                        />
                                                        <span className="text-sm">Enable rate limiting</span>
                                                    </label>
                                                    <div className="flex gap-2">
                                                        <input
                                                            type="number"
                                                            value={formConfig.rateLimitingMaxRequests}
                                                            onChange={(e) => setFormConfig({ ...formConfig, rateLimitingMaxRequests: parseInt(e.target.value) || 100 })}
                                                            className="flex-1 px-3 py-2 border border-input rounded-md bg-background text-foreground text-sm"
                                                            placeholder="Max requests"
                                                            min="1"
                                                            max="1000"
                                                        />
                                                        <input
                                                            type="number"
                                                            value={formConfig.rateLimitingTimeWindow}
                                                            onChange={(e) => setFormConfig({ ...formConfig, rateLimitingTimeWindow: parseInt(e.target.value) || 60 })}
                                                            className="flex-1 px-3 py-2 border border-input rounded-md bg-background text-foreground text-sm"
                                                            placeholder="Time window (seconds)"
                                                            min="1"
                                                            max="3600"
                                                        />
                                                    </div>
                                                </div>
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium mb-1">Logging</label>
                                                <div className="space-y-2">
                                                    <label className="flex items-center gap-2">
                                                        <input
                                                            type="checkbox"
                                                            checked={formConfig.debugLogging}
                                                            onChange={(e) => setFormConfig({ ...formConfig, debugLogging: e.target.checked })}
                                                            className="rounded"
                                                        />
                                                        <span className="text-sm">Enable debug logging</span>
                                                    </label>
                                                    <label className="flex items-center gap-2">
                                                        <input
                                                            type="checkbox"
                                                            checked={formConfig.logRequests}
                                                            onChange={(e) => setFormConfig({ ...formConfig, logRequests: e.target.checked })}
                                                            className="rounded"
                                                        />
                                                        <span className="text-sm">Log requests and responses</span>
                                                    </label>
                                                    <label className="flex items-center gap-2">
                                                        <input
                                                            type="checkbox"
                                                            checked={formConfig.logErrorsOnly}
                                                            onChange={(e) => setFormConfig({ ...formConfig, logErrorsOnly: e.target.checked })}
                                                            className="rounded"
                                                        />
                                                        <span className="text-sm">Log errors only</span>
                                                    </label>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <h5 className="font-medium mb-2">Configuration Preview</h5>
                                        <pre className="bg-secondary p-3 rounded-md text-sm overflow-x-auto">
                                            {JSON.stringify({
                                                apiEndpoint: formConfig.apiEndpoint,
                                                timeout: formConfig.timeout,
                                                maxRetries: formConfig.maxRetries,
                                                customHeaders: formConfig.customHeaders ? (() => {
                                                    try { return JSON.parse(formConfig.customHeaders); } catch { return undefined; }
                                                })() : undefined,
                                                rateLimiting: formConfig.rateLimitingEnabled ? {
                                                    enabled: true,
                                                    maxRequests: formConfig.rateLimitingMaxRequests,
                                                    timeWindow: formConfig.rateLimitingTimeWindow
                                                } : undefined,
                                                logging: {
                                                    debug: formConfig.debugLogging,
                                                    requests: formConfig.logRequests,
                                                    errorsOnly: formConfig.logErrorsOnly
                                                }
                                            }, null, 2)}
                                        </pre>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="border-t border-border p-4 flex justify-end gap-2">
                            <button
                                onClick={() => setShowConfigDialog(null)}
                                className="px-4 py-2 bg-secondary rounded-md hover:bg-secondary/80"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => {
                                    // Build the updated configuration from form state
                                    let parsedHeaders = undefined
                                    if (formConfig.customHeaders.trim()) {
                                        try {
                                            parsedHeaders = JSON.parse(formConfig.customHeaders)
                                        } catch (e) {
                                            // Keep as string if parsing fails
                                            parsedHeaders = formConfig.customHeaders
                                        }
                                    }

                                    const updatedConfig = {
                                        apiEndpoint: formConfig.apiEndpoint,
                                        apiKey: formConfig.apiKey,
                                        timeout: formConfig.timeout,
                                        maxRetries: formConfig.maxRetries,
                                        customHeaders: parsedHeaders,
                                        rateLimiting: formConfig.rateLimitingEnabled ? {
                                            enabled: true,
                                            maxRequests: formConfig.rateLimitingMaxRequests,
                                            timeWindow: formConfig.rateLimitingTimeWindow
                                        } : undefined,
                                        logging: {
                                            debug: formConfig.debugLogging,
                                            requests: formConfig.logRequests,
                                            errorsOnly: formConfig.logErrorsOnly
                                        }
                                    }
                                    handleConfigureTool(showConfigDialog!, updatedConfig)
                                }}
                                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                            >
                                Save Configuration
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Marketplace */}
            {showMarketplace && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-card border border-border rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
                        <div className="flex items-center justify-between p-4 border-b border-border">
                            <h3 className="font-semibold flex items-center gap-2">
                                <Plug className="w-4 h-4" />
                                <span>Tool Marketplace</span>
                            </h3>
                            <button
                                onClick={() => setShowMarketplace(false)}
                                className="p-1 rounded-md hover:bg-accent"
                                title="Close"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-auto p-4">
                            {isLoadingMarketplace ? (
                                <div className="text-center py-12">
                                    <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                                    <p>Loading marketplace tools...</p>
                                </div>
                            ) : (
                                <div className="space-y-6">
                                    <div className="flex items-center gap-4 mb-4">
                                        <div className="relative flex-1">
                                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                                            <input
                                                type="text"
                                                placeholder="Search marketplace..."
                                                className="w-full pl-9 pr-3 py-2 border border-input rounded-md bg-background text-foreground"
                                            />
                                        </div>

                                        <div className="relative">
                                            <select title="Filter by category" className="pl-3 pr-8 py-2 border border-input rounded-md bg-background text-foreground appearance-none">
                                                <option>All Categories</option>
                                                <option>Information</option>
                                                <option>Development</option>
                                                <option>Data</option>
                                                <option>Integration</option>
                                                <option>Communication</option>
                                            </select>
                                            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
                                        </div>

                                        <div className="relative">
                                            <select title="Sort by" className="pl-3 pr-8 py-2 border border-input rounded-md bg-background text-foreground appearance-none">
                                                <option>Sort: Popular</option>
                                                <option>Sort: Rating</option>
                                                <option>Sort: Newest</option>
                                                <option>Sort: Name</option>
                                            </select>
                                            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                        {marketplaceTools.map(tool => (
                                            <div key={tool.id} className="border border-border rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                                                <div className="p-4">
                                                    <div className="flex items-center justify-between mb-2">
                                                        <div className="flex items-center gap-2">
                                                            <div className="w-8 h-8 flex items-center justify-center bg-secondary rounded-md">
                                                                <span className="text-lg">{tool.icon}</span>
                                                            </div>
                                                            <div>
                                                                <h4 className="font-medium">{tool.name}</h4>
                                                                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                                                    <span>{tool.version}</span>
                                                                    <span>•</span>
                                                                    <span>{tool.author}</span>
                                                                </div>
                                                            </div>
                                                        </div>
                                                        <button
                                                            onClick={() => setShowInstallDialog(tool.id)}
                                                            className="flex items-center gap-1 px-3 py-1 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                                                        >
                                                            <Plus className="w-3 h-3" />
                                                            <span>Install</span>
                                                        </button>
                                                    </div>

                                                    <p className="text-sm text-muted-foreground mb-3 line-clamp-3">
                                                        {tool.description}
                                                    </p>

                                                    <div className="flex items-center justify-between mb-3">
                                                        <div className="flex items-center gap-2">
                                                            <div className="flex items-center gap-1">
                                                                <Star className="w-3 h-3 text-yellow-500" />
                                                                <span className="text-xs font-medium">{tool.rating}</span>
                                                            </div>
                                                            <div className="flex items-center gap-1">
                                                                <Download className="w-3 h-3 text-blue-500" />
                                                                <span className="text-xs text-muted-foreground">{tool.download_count.toLocaleString()}</span>
                                                            </div>
                                                        </div>
                                                        <span className="text-xs text-muted-foreground">
                                                            Updated {new Date(tool.last_updated).toLocaleDateString()}
                                                        </span>
                                                    </div>

                                                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                                                        <div className="flex items-center gap-2">
                                                            {getCategoryIcon(tool.category)}
                                                            <span>{tool.category}</span>
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            {getToolIcon(tool.type)}
                                                            <span>{tool.type}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>

                                    <div className="mt-6 p-4 bg-secondary rounded-md">
                                        <h4 className="font-medium mb-2">Marketplace Information</h4>
                                        <p className="text-sm text-muted-foreground mb-2">
                                            Browse and install tools from the official Chronos AI Tool Marketplace.
                                        </p>
                                        <ul className="text-sm space-y-1">
                                            <li className="flex items-center gap-2">
                                                <Check className="w-3 h-3 text-green-500" />
                                                <span>All tools are verified and secure</span>
                                            </li>
                                            <li className="flex items-center gap-2">
                                                <Check className="w-3 h-3 text-green-500" />
                                                <span>Regular updates and maintenance</span>
                                            </li>
                                            <li className="flex items-center gap-2">
                                                <Check className="w-3 h-3 text-green-500" />
                                                <span>Community ratings and reviews</span>
                                            </li>
                                            <li className="flex items-center gap-2">
                                                <Check className="w-3 h-3 text-green-500" />
                                                <span>Detailed documentation and support</span>
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="border-t border-border p-4 flex justify-end gap-2">
                            <button
                                onClick={() => setShowMarketplace(false)}
                                className="px-4 py-2 bg-secondary rounded-md hover:bg-secondary/80"
                            >
                                Close Marketplace
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}