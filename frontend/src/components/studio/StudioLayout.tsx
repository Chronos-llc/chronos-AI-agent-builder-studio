import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { toast } from 'react-hot-toast'
import VersionControlPanel from './VersionControlPanel'
import BotSettingsPanel from './BotSettingsPanel'
import SubAgentConfigPanel from './SubAgentConfigPanel'
import { Loader2, Save, Settings, Users, FileText, Database, Code, MessageSquare, Play, Maximize, Minimize, PanelLeftClose, PanelRightClose, Moon, Sun, Keyboard, Plus, Upload, Trash2, Edit, X, AlertTriangle, Info, GitBranch, Image, Video, Cpu, Eye, Send, Zap } from 'lucide-react'

// Types
interface AgentConfig {
    id?: number
    name: string
    description: string
    system_prompt: string
    user_prompt_template: string
    model_config: any
    status: string
    tags: string[]
    metadata: any
}

interface KnowledgeItem {
    id: string
    name: string
    type: 'text' | 'pdf' | 'image' | 'video' | 'code'
    size: number
    content: string
    metadata: any
    created_at: string
}

interface ToolIntegration {
    id: string
    name: string
    description: string
    type: string
    icon: string
    is_installed: boolean
    config: any
}

interface ChatMessage {
    id: string
    role: 'user' | 'agent' | 'system'
    content: string
    timestamp: string
    status: 'sent' | 'delivered' | 'read' | 'error'
    metadata?: any
}

export const StudioLayout: React.FC = () => {
    const { id } = useParams()
    const [agentConfig, setAgentConfig] = useState<AgentConfig>({
        name: '',
        description: '',
        system_prompt: '',
        user_prompt_template: '',
        model_config: {},
        status: 'draft',
        tags: [],
        metadata: {}
    })
    const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([])
    const [tools, setTools] = useState<ToolIntegration[]>([])
    const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
    const [newMessage, setNewMessage] = useState('')
    const [isLoading, setIsLoading] = useState(true)
    const [isSaving, setIsSaving] = useState(false)
    const [activeTab, setActiveTab] = useState<'instructions' | 'knowledge' | 'tools' | 'chat' | 'config' | 'actions' | 'versions' | 'settings' | 'sub-agents'>('instructions')
    const [panelSizes, setPanelSizes] = useState({
        left: 300,
        center: 500,
        right: 300
    })
    const [isFullScreen, setIsFullScreen] = useState(false)
    const [darkMode, setDarkMode] = useState(false)
    const [isDragging, setIsDragging] = useState(false)
    const [draggingPanel, setDraggingPanel] = useState<'left' | 'right' | null>(null)
    const [showSidebar, setShowSidebar] = useState(true)
    const [showToolsPanel, setShowToolsPanel] = useState(true)
    const [showConfigPanel, setShowConfigPanel] = useState(false)
    const [emulatorMode, setEmulatorMode] = useState(false)
    const [isTesting, setIsTesting] = useState(false)
    const [testResults, setTestResults] = useState<any[]>([])
    const [onlineUsers, setOnlineUsers] = useState<number>(0)

    // Simulate online users count (in production, this would come from WebSocket or API)
    useEffect(() => {
        const interval = setInterval(() => {
            // Simulate random online users between 1-5
            setOnlineUsers(Math.floor(Math.random() * 5) + 1)
        }, 30000) // Update every 30 seconds

        // Initial count
        setOnlineUsers(Math.floor(Math.random() * 5) + 1)

        return () => clearInterval(interval)
    }, [])

    // Fetch agent data
    const { data: agentData, isLoading: isAgentLoading } = useQuery({
        queryKey: ['agent', id],
        queryFn: async () => {
            if (!id) return null
            const response = await axios.get(`/api/agents/${id}`)
            return response.data
        },
        enabled: !!id
    })

    // Fetch knowledge base
    const { data: knowledgeData } = useQuery({
        queryKey: ['knowledge', id],
        queryFn: async (): Promise<KnowledgeItem[]> => {
            if (!id) return []
            // Mock data for now
            return [
                { id: '1', name: 'Getting Started Guide', type: 'text', size: 1024, content: 'Welcome to the AI Agent Studio...', metadata: {}, created_at: new Date().toISOString() },
                { id: '2', name: 'API Documentation', type: 'pdf', size: 2048, content: 'API documentation content...', metadata: {}, created_at: new Date().toISOString() }
            ] as KnowledgeItem[]
        },
        enabled: !!id
    })

    // Fetch tools
    const { data: toolsData } = useQuery({
        queryKey: ['tools'],
        queryFn: async () => {
            // Mock data for now
            return [
                { id: '1', name: 'Web Search', description: 'Search the web for information', type: 'search', icon: '🌐', is_installed: true, config: {} },
                { id: '2', name: 'Code Interpreter', description: 'Execute Python code', type: 'code', icon: '🐍', is_installed: true, config: {} },
                { id: '3', name: 'Database Query', description: 'Query databases', type: 'database', icon: '🗃️', is_installed: false, config: {} }
            ]
        }
    })

    // Save agent configuration
    const saveAgentMutation = useMutation({
        mutationFn: async (config: AgentConfig) => {
            if (id) {
                await axios.put(`/api/agents/${id}`, config)
            } else {
                const response = await axios.post('/api/agents', config)
                return response.data
            }
        },
        onSuccess: (data) => {
            toast.success('Agent saved successfully')
            if (data && !id) {
                // Redirect to edit page if new agent
                window.location.href = `/agents/${data.id}/edit`
            }
        },
        onError: (error) => {
            toast.error('Failed to save agent')
            console.error('Save error:', error)
        }
    })

    // Handle agent data
    useEffect(() => {
        if (agentData) {
            setAgentConfig({
                ...agentData,
                model_config: agentData.model_config || {},
                tags: agentData.tags || [],
                metadata: agentData.metadata || {}
            })
        } else if (!id) {
            setAgentConfig({
                name: 'New Agent',
                description: 'A new AI agent',
                system_prompt: 'You are a helpful AI assistant.',
                user_prompt_template: '{{user_input}}',
                model_config: {},
                status: 'draft',
                tags: [],
                metadata: {}
            })
        }
        setIsLoading(false)
    }, [agentData, id])

    useEffect(() => {
        if (knowledgeData) {
            setKnowledgeItems(knowledgeData)
        }
    }, [knowledgeData])

    useEffect(() => {
        if (toolsData) {
            setTools(toolsData)
        }
    }, [toolsData])

    // Handle saving
    const handleSave = async () => {
        setIsSaving(true)
        try {
            await saveAgentMutation.mutateAsync(agentConfig)
        } finally {
            setIsSaving(false)
        }
    }

    // Handle configuration changes
    const handleConfigChange = (field: keyof AgentConfig, value: any) => {
        setAgentConfig(prev => ({
            ...prev,
            [field]: value
        }))
    }

    // Handle knowledge base changes
    const handleKnowledgeChange = (items: KnowledgeItem[]) => {
        setKnowledgeItems(items)
    }

    // Handle tools changes
    const handleToolsChange = (updatedTools: ToolIntegration[]) => {
        setTools(updatedTools)
    }

    // Handle chat message send
    const handleSendMessage = () => {
        if (!newMessage.trim()) return

        const userMessage: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: newMessage,
            timestamp: new Date().toISOString(),
            status: 'sent'
        }

        setChatMessages(prev => [...prev, userMessage])
        setNewMessage('')

        // Simulate agent response
        setTimeout(() => {
            const agentMessage: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: 'agent',
                content: `I received your message: "${userMessage.content}". How can I assist you further?`,
                timestamp: new Date().toISOString(),
                status: 'delivered'
            }
            setChatMessages(prev => [...prev, agentMessage])
        }, 1000)
    }

    // Handle panel resizing
    const handleMouseDown = (panel: 'left' | 'right') => (e: React.MouseEvent) => {
        setDraggingPanel(panel)
        setIsDragging(true)
        e.preventDefault()
    }

    const handleMouseMove = (e: MouseEvent) => {
        if (!isDragging || !draggingPanel) return

        if (draggingPanel === 'left') {
            const newLeftSize = e.clientX
            if (newLeftSize > 100 && newLeftSize < window.innerWidth - 200) {
                setPanelSizes(prev => ({
                    ...prev,
                    left: newLeftSize,
                    center: prev.center + prev.left - newLeftSize
                }))
            }
        } else if (draggingPanel === 'right') {
            const newRightSize = window.innerWidth - e.clientX
            if (newRightSize > 100 && newRightSize < window.innerWidth - 200) {
                setPanelSizes(prev => ({
                    ...prev,
                    right: newRightSize,
                    center: prev.center + prev.right - newRightSize
                }))
            }
        }
    }

    const handleMouseUp = () => {
        setIsDragging(false)
        setDraggingPanel(null)
    }

    useEffect(() => {
        window.addEventListener('mousemove', handleMouseMove)
        window.addEventListener('mouseup', handleMouseUp)
        return () => {
            window.removeEventListener('mousemove', handleMouseMove)
            window.removeEventListener('mouseup', handleMouseUp)
        }
    }, [isDragging, draggingPanel])

    // Toggle panels
    const toggleLeftPanel = () => setShowSidebar(!showSidebar)
    const toggleRightPanel = () => setShowToolsPanel(!showToolsPanel)
    const toggleConfigPanel = () => setShowConfigPanel(!showConfigPanel)

    // Toggle full screen
    const toggleFullScreen = () => {
        setIsFullScreen(!isFullScreen)
        if (!isFullScreen) {
            document.documentElement.requestFullscreen()
        } else {
            document.exitFullscreen()
        }
    }

    // Toggle dark mode
    const toggleDarkMode = () => {
        setDarkMode(!darkMode)
        document.documentElement.classList.toggle('dark')
    }

    // Handle file upload (mock)
    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files
        if (!files) return

        const newItems: KnowledgeItem[] = []
        for (let i = 0; i < files.length; i++) {
            const file = files[i]
            const fileType = file.type.startsWith('image/') ? 'image' :
                file.type.startsWith('video/') ? 'video' :
                    file.type === 'application/pdf' ? 'pdf' :
                        file.type.startsWith('text/') ? 'text' : 'code'

            newItems.push({
                id: Date.now() + i + '',
                name: file.name,
                type: fileType,
                size: file.size,
                content: `Content of ${file.name}`,
                metadata: { fileType: file.type },
                created_at: new Date().toISOString()
            })
        }
        handleKnowledgeChange([...knowledgeItems, ...newItems])
    }

    // Handle tool installation
    const handleInstallTool = (toolId: string) => {
        setTools(prev => prev.map(tool =>
            tool.id === toolId ? { ...tool, is_installed: true } : tool
        ))
    }

    // Handle emulator mode
    const handleEmulatorToggle = () => {
        setEmulatorMode(!emulatorMode)
        if (!emulatorMode) {
            toast('Emulator mode activated', { icon: '🔧' })
        } else {
            toast('Emulator mode deactivated', { icon: '🔧' })
        }
    }

    // Handle testing
    const handleStartTesting = () => {
        setIsTesting(true)
        setTestResults([])
        toast('Testing started...', { icon: '🧪' })

        // Simulate test results
        setTimeout(() => {
            const mockResults = [
                { id: '1', test: 'System Prompt Validation', status: 'pass', message: 'System prompt is valid', timestamp: new Date().toISOString() },
                { id: '2', test: 'Knowledge Base Integration', status: 'pass', message: 'Knowledge base connected successfully', timestamp: new Date().toISOString() },
                { id: '3', test: 'Tool Configuration', status: 'warn', message: 'Some tools need configuration', timestamp: new Date().toISOString() }
            ]
            setTestResults(mockResults)
            setIsTesting(false)
            toast.success('Testing completed')
        }, 3000)
    }

    // CSS custom properties for panel widths - updated dynamically via JavaScript
    useEffect(() => {
        const root = document.documentElement;
        root.style.setProperty('--studio-sidebar-width', `${panelSizes.left}px`);
        root.style.setProperty('--studio-center-width', `${showSidebar ? panelSizes.center : showToolsPanel ? window.innerWidth - panelSizes.left - panelSizes.right : window.innerWidth - panelSizes.left}px`);
        root.style.setProperty('--studio-tools-width', `${panelSizes.right}px`);
    }, [panelSizes.left, panelSizes.center, panelSizes.right, showSidebar, showToolsPanel]);

    if (isLoading || isAgentLoading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="flex flex-col items-center gap-4">
                    <Loader2 className="w-8 h-8 animate-spin" />
                    <span>Loading Studio...</span>
                </div>
            </div>
        )
    }

    return (
        <div className={`studio-layout ${isFullScreen ? 'fullscreen' : ''} ${darkMode ? 'dark' : ''}`}>
            <div className="flex flex-col h-screen bg-background text-foreground">
                {/* Header */}
                <header className="flex items-center justify-between p-4 border-b border-border bg-card">
                    <div className="flex items-center gap-4">
                        <img 
                            src="https://i.postimg.cc/FRyC2G1k/IMG-20260103-192235-443.webp" 
                            alt="Chronos Studio Logo" 
                            className="h-8 w-auto"
                        />
                        <h1 className="text-xl font-bold">
                            {agentConfig.name || 'Chronos Studio'}
                        </h1>
                        <span className="text-sm text-muted-foreground">
                            {agentConfig.status.toUpperCase()}
                        </span>
                        <button
                            onClick={handleSave}
                            disabled={isSaving}
                            className="flex items-center gap-2 px-3 py-1 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
                        >
                            {isSaving ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    <span>Saving...</span>
                                </>
                            ) : (
                                <>
                                    <Save className="w-4 h-4" />
                                    <span>Save</span>
                                </>
                            )}
                        </button>
                    </div>

                    <div className="flex items-center gap-2">
                        {/* Collaboration indicators */}
                        <div className="flex items-center gap-1 mr-4">
                            <Users className="w-4 h-4 text-muted-foreground" />
                            <span className="text-sm text-muted-foreground">{onlineUsers} online</span>
                        </div>

                        {/* Theme toggle */}
                        <button
                            onClick={toggleDarkMode}
                            className="p-2 rounded-md hover:bg-accent"
                            title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                        >
                            {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                        </button>

                        {/* Fullscreen toggle */}
                        <button
                            onClick={toggleFullScreen}
                            className="p-2 rounded-md hover:bg-accent"
                            title={isFullScreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}
                        >
                            {isFullScreen ? <Minimize className="w-5 h-5" /> : <Maximize className="w-5 h-5" />}
                        </button>

                        {/* Emulator mode toggle */}
                        <button
                            onClick={handleEmulatorToggle}
                            className={`p-2 rounded-md ${emulatorMode ? 'bg-blue-500 text-white' : 'hover:bg-accent'}`}
                            title={emulatorMode ? 'Deactivate Emulator Mode' : 'Activate Emulator Mode'}
                        >
                            <Cpu className="w-5 h-5" />
                        </button>

                        {/* Settings */}
                        <button
                            onClick={toggleConfigPanel}
                            className="p-2 rounded-md hover:bg-accent"
                            title="Configuration"
                        >
                            <Settings className="w-5 h-5" />
                        </button>
                    </div>
                </header>

                <div className="flex flex-1 overflow-hidden">
                    {/* Left Sidebar - Instructions */}
                    {showSidebar && (
                        <div
                            className="flex flex-col border-r border-border bg-card overflow-hidden studio-sidebar"
                        >
                            <div className="flex items-center justify-between p-3 border-b border-border">
                                <h2 className="font-semibold flex items-center gap-2">
                                    <FileText className="w-4 h-4" />
                                    <span>Instructions</span>
                                </h2>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={toggleLeftPanel}
                                        className="p-1 rounded-md hover:bg-accent"
                                        title="Collapse Panel"
                                    >
                                        <PanelLeftClose className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            <div className="flex-1 overflow-auto p-4">
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Agent Name</label>
                                        <input
                                            type="text"
                                            value={agentConfig.name}
                                            onChange={(e) => handleConfigChange('name', e.target.value)}
                                            className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
                                            placeholder="Enter agent name"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium mb-1">Description</label>
                                        <textarea
                                            value={agentConfig.description}
                                            onChange={(e) => handleConfigChange('description', e.target.value)}
                                            className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground min-h-[60px]"
                                            placeholder="Describe your agent"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium mb-1">System Prompt</label>
                                        <textarea
                                            value={agentConfig.system_prompt}
                                            onChange={(e) => handleConfigChange('system_prompt', e.target.value)}
                                            className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground min-h-[150px] font-mono text-sm"
                                            placeholder="Define the agent's system instructions..."
                                        />
                                        <div className="text-xs text-muted-foreground mt-1 flex justify-between">
                                            <span>Characters: {agentConfig.system_prompt.length}</span>
                                            <span>Tokens: ~{Math.ceil(agentConfig.system_prompt.length / 4)}</span>
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium mb-1">User Prompt Template</label>
                                        <textarea
                                            value={agentConfig.user_prompt_template}
                                            onChange={(e) => handleConfigChange('user_prompt_template', e.target.value)}
                                            className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground min-h-[80px] font-mono text-sm"
                                            placeholder="Template for user prompts with variables..."
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium mb-1">Tags</label>
                                        <div className="flex flex-wrap gap-2 mb-2">
                                            {agentConfig.tags.map((tag, index) => (
                                                <span key={index} className="flex items-center gap-1 px-2 py-1 bg-secondary text-secondary-foreground rounded-md text-sm">
                                                    <span>{tag}</span>
                                                    <button
                                                        onClick={() => handleConfigChange('tags', agentConfig.tags.filter((_, i) => i !== index))}
                                                        className="text-xs"
                                                        aria-label={`Remove tag ${tag}`}
                                                    >
                                                        <X className="w-3 h-3" />
                                                    </button>
                                                </span>
                                            ))}
                                        </div>
                                        <div className="flex gap-2">
                                            <input
                                                type="text"
                                                placeholder="Add tag"
                                                className="flex-1 px-3 py-2 border border-input rounded-md bg-background text-foreground text-sm"
                                                onKeyPress={(e) => {
                                                    if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                                                        handleConfigChange('tags', [...agentConfig.tags, e.currentTarget.value.trim()])
                                                        e.currentTarget.value = ''
                                                    }
                                                }}
                                            />
                                            <button
                                                className="px-3 py-2 bg-primary text-primary-foreground rounded-md"
                                                onClick={() => {
                                                    const input = document.querySelector('input[placeholder="Add tag"]') as HTMLInputElement
                                                    if (input && input.value.trim()) {
                                                        handleConfigChange('tags', [...agentConfig.tags, input.value.trim()])
                                                        input.value = ''
                                                    }
                                                }}
                                                aria-label="Add tag"
                                            >
                                                <Plus className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Resizer between left and center */}
                    {showSidebar && (
                        <div
                            className="w-2 bg-border cursor-col-resize hover:bg-primary"
                            onMouseDown={handleMouseDown('left')}
                        />
                    )}

                    {/* Center Panel - Knowledge Base */}
                    <div
                        className="flex flex-col border-r border-border bg-card overflow-hidden studio-center"
                    >
                        <div className="flex items-center justify-between p-3 border-b border-border">
                            <h2 className="font-semibold flex items-center gap-2">
                                <Database className="w-4 h-4" />
                                <span>Knowledge Base</span>
                            </h2>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={handleStartTesting}
                                    disabled={isTesting}
                                    className="flex items-center gap-2 px-3 py-1 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50"
                                >
                                    {isTesting ? (
                                        <>
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                            <span>Testing...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Play className="w-4 h-4" />
                                            <span>Test</span>
                                        </>
                                    )}
                                </button>
                                <label className="flex items-center gap-2 px-3 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600 cursor-pointer">
                                    <Upload className="w-4 h-4" />
                                    <span>Upload</span>
                                    <input
                                        type="file"
                                        multiple
                                        className="hidden"
                                        onChange={handleFileUpload}
                                    />
                                </label>
                            </div>
                        </div>

                        <div className="flex-1 overflow-auto p-4">
                            {/* Test Results */}
                            {testResults.length > 0 && (
                                <div className="mb-6">
                                    <h3 className="font-medium mb-3 flex items-center gap-2">
                                        <AlertTriangle className="w-4 h-4" />
                                        <span>Test Results</span>
                                    </h3>
                                    <div className="space-y-2">
                                        {testResults.map(result => (
                                            <div
                                                key={result.id}
                                                className={`p-3 rounded-md flex items-center gap-3 ${result.status === 'pass' ? 'bg-green-50 border border-green-200' :
                                                        result.status === 'warn' ? 'bg-yellow-50 border border-yellow-200' :
                                                            'bg-red-50 border border-red-200'
                                                    }`}
                                            >
                                                <div className="flex-1">
                                                    <div className="font-medium">{result.test}</div>
                                                    <div className="text-sm text-muted-foreground">{result.message}</div>
                                                </div>
                                                <div className="text-sm font-medium">
                                                    {result.status.toUpperCase()}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Knowledge Items */}
                            <div className="space-y-4">
                                {knowledgeItems.length === 0 ? (
                                    <div className="text-center py-8 text-muted-foreground">
                                        <Upload className="w-8 h-8 mx-auto mb-2" />
                                        <p>No knowledge items uploaded yet</p>
                                        <p className="text-sm mt-1">Upload files to build your agent's knowledge base</p>
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                        {knowledgeItems.map(item => (
                                            <div key={item.id} className="border border-border rounded-lg p-4 hover:shadow-md transition-shadow">
                                                <div className="flex items-center justify-between mb-2">
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-6 h-6 flex items-center justify-center">
                                                            {item.type === 'text' && <FileText className="w-4 h-4" />}
                                                            {item.type === 'pdf' && <FileText className="w-4 h-4 text-red-500" />}
                                                            {item.type === 'image' && <Image className="w-4 h-4 text-blue-500" />}
                                                            {item.type === 'video' && <Video className="w-4 h-4 text-green-500" />}
                                                            {item.type === 'code' && <Code className="w-4 h-4 text-purple-500" />}
                                                        </div>
                                                        <span className="font-medium truncate max-w-[150px]">{item.name}</span>
                                                    </div>
                                                    <button
                                                        className="text-muted-foreground hover:text-foreground"
                                                        onClick={() => handleKnowledgeChange(knowledgeItems.filter(i => i.id !== item.id))}
                                                        aria-label={`Delete ${item.name}`}
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>
                                                <div className="text-sm text-muted-foreground mb-2">
                                                    {item.type.toUpperCase()} • {(item.size / 1024).toFixed(1)} KB
                                                </div>
                                                <div className="text-sm text-muted-foreground line-clamp-3">
                                                    {item.content}
                                                </div>
                                                <div className="mt-3 flex gap-2">
                                                    <button className="flex items-center gap-1 px-2 py-1 text-xs bg-secondary rounded-md hover:bg-secondary/80">
                                                        <Edit className="w-3 h-3" />
                                                        <span>Edit</span>
                                                    </button>
                                                    <button className="flex items-center gap-1 px-2 py-1 text-xs bg-secondary rounded-md hover:bg-secondary/80">
                                                        <Eye className="w-3 h-3" />
                                                        <span>Preview</span>
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Resizer between center and right */}
                    {showToolsPanel && (
                        <div
                            className="w-2 bg-border cursor-col-resize hover:bg-primary"
                            onMouseDown={handleMouseDown('right')}
                        />
                    )}

                    {/* Right Panel - Tools & Chat */}
                    {showToolsPanel && (
                        <div
                            className="flex flex-col border-r border-border bg-card overflow-hidden studio-tools"
                        >
                            <div className="flex items-center justify-between p-3 border-b border-border">
                                <div className="flex items-center gap-4">
                                    <button
                                        className={`flex items-center gap-2 px-3 py-1 rounded-md ${activeTab === 'tools' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                                        onClick={() => setActiveTab('tools')}
                                    >
                                        <Code className="w-4 h-4" />
                                        <span>Tools</span>
                                    </button>
                                    <button
                                        className={`flex items-center gap-2 px-3 py-1 rounded-md ${activeTab === 'actions' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                                        onClick={() => setActiveTab('actions')}
                                    >
                                        <Zap className="w-4 h-4" />
                                        <span>Actions</span>
                                    </button>
                                    <button
                                        className={`flex items-center gap-2 px-3 py-1 rounded-md ${activeTab === 'versions' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                                        onClick={() => setActiveTab('versions')}
                                    >
                                        <GitBranch className="w-4 h-4" />
                                        <span>Versions</span>
                                    </button>
                                    <button
                                        className={`flex items-center gap-2 px-3 py-1 rounded-md ${activeTab === 'settings' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                                        onClick={() => setActiveTab('settings')}
                                    >
                                        <Settings className="w-4 h-4" />
                                        <span>Settings</span>
                                    </button>
                                    <button
                                        className={`flex items-center gap-2 px-3 py-1 rounded-md ${activeTab === 'chat' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                                        onClick={() => setActiveTab('chat')}
                                    >
                                        <MessageSquare className="w-4 h-4" />
                                        <span>Chat</span>
                                    </button>
                                </div>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={toggleRightPanel}
                                        className="p-1 rounded-md hover:bg-accent"
                                        title="Collapse Panel"
                                    >
                                        <PanelRightClose className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            <div className="flex-1 overflow-auto">
                                {activeTab === 'tools' ? (
                                    <div className="p-4 space-y-4">
                                        <div className="flex items-center justify-between">
                                            <h3 className="font-medium">Available Tools</h3>
                                            <span className="text-sm text-muted-foreground">{tools.filter(t => t.is_installed).length}/{tools.length} installed</span>
                                        </div>

                                        <div className="space-y-3">
                                            {tools.map(tool => (
                                                <div key={tool.id} className="border border-border rounded-lg p-3">
                                                    <div className="flex items-start gap-3">
                                                        <div className="w-8 h-8 flex items-center justify-center bg-secondary rounded-md">
                                                            <span className="text-lg">{tool.icon}</span>
                                                        </div>
                                                        <div className="flex-1">
                                                            <div className="flex items-center justify-between mb-1">
                                                                <h4 className="font-medium">{tool.name}</h4>
                                                                <span className={`text-xs px-2 py-1 rounded-full ${tool.is_installed ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                                                                    {tool.is_installed ? 'Installed' : 'Available'}
                                                                </span>
                                                            </div>
                                                            <p className="text-sm text-muted-foreground mb-2">{tool.description}</p>
                                                            <div className="flex gap-2">
                                                                {!tool.is_installed ? (
                                                                    <button
                                                                        className="flex items-center gap-1 px-3 py-1 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                                                                        onClick={() => handleInstallTool(tool.id)}
                                                                    >
                                                                        <Plus className="w-3 h-3" />
                                                                        <span>Install</span>
                                                                    </button>
                                                                ) : (
                                                                    <button
                                                                        className="flex items-center gap-1 px-3 py-1 text-sm bg-secondary rounded-md hover:bg-secondary/80"
                                                                    >
                                                                        <Settings className="w-3 h-3" />
                                                                        <span>Configure</span>
                                                                    </button>
                                                                )}
                                                                <button
                                                                    className="flex items-center gap-1 px-3 py-1 text-sm bg-secondary rounded-md hover:bg-secondary/80"
                                                                    onClick={() => handleToolsChange(tools.filter(t => t.id !== tool.id))}
                                                                    aria-label={`Remove ${tool.name}`}
                                                                >
                                                                    <Trash2 className="w-3 h-3" />
                                                                    <span>Remove</span>
                                                                </button>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>

                                        <div className="mt-6">
                                            <h3 className="font-medium mb-3">Tool Marketplace</h3>
                                            <div className="grid grid-cols-2 gap-2">
                                                {['🌐 Web Tools', '📊 Analytics', '🔧 Utilities', '💬 Communication'].map((category, index) => (
                                                    <button
                                                        key={index}
                                                        className="flex items-center justify-center gap-2 px-3 py-2 border border-border rounded-md hover:bg-accent text-sm"
                                                    >
                                                        <span>{category.split(' ')[0]}</span>
                                                        <span>{category.split(' ')[1]}</span>
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                ) : activeTab === 'versions' ? (
                                    <VersionControlPanel agentId={parseInt(id || '0')} />
                                ) : activeTab === 'settings' ? (
                                    <BotSettingsPanel agentId={parseInt(id || '0')} />
                                ) : activeTab === 'sub-agents' ? (
                                    <SubAgentConfigPanel agentId={parseInt(id || '0')} />
                                ) : (
                                    <div className="flex flex-col h-full">
                                        <div className="flex-1 overflow-auto p-4 space-y-4">
                                            {chatMessages.length === 0 ? (
                                                <div className="text-center py-8 text-muted-foreground">
                                                    <MessageSquare className="w-8 h-8 mx-auto mb-2" />
                                                    <p>No messages yet</p>
                                                    <p className="text-sm mt-1">Start a conversation to test your agent</p>
                                                </div>
                                            ) : (
                                                <div className="space-y-4">
                                                    {chatMessages.map(message => (
                                                        <div
                                                            key={message.id}
                                                            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                                        >
                                                            <div
                                                                className={`max-w-[80%] p-3 rounded-lg ${message.role === 'user' ? 'bg-primary text-primary-foreground rounded-br-none' :
                                                                        message.role === 'agent' ? 'bg-secondary rounded-bl-none' :
                                                                            'bg-muted rounded-lg'
                                                                    }`}
                                                            >
                                                                <div className="mb-1">
                                                                    <span className="font-medium capitalize text-xs">
                                                                        {message.role}
                                                                    </span>
                                                                    <span className="text-xs text-muted-foreground ml-2">
                                                                        {new Date(message.timestamp).toLocaleTimeString()}
                                                                    </span>
                                                                </div>
                                                                <div className="whitespace-pre-wrap">
                                                                    {message.content}
                                                                </div>
                                                                {message.metadata && (
                                                                    <div className="mt-2 text-xs text-muted-foreground">
                                                                        {JSON.stringify(message.metadata, null, 2)}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>

                                        <div className="border-t border-border p-4">
                                            <div className="flex gap-2">
                                                <input
                                                    type="text"
                                                    value={newMessage}
                                                    onChange={(e) => setNewMessage(e.target.value)}
                                                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                                                    placeholder="Type your message..."
                                                    className="flex-1 px-3 py-2 border border-input rounded-md bg-background text-foreground"
                                                    disabled={isTesting}
                                                />
                                                <button
                                                    onClick={handleSendMessage}
                                                    disabled={!newMessage.trim() || isTesting}
                                                    className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
                                                    aria-label="Send message"
                                                >
                                                    <Send className="w-4 h-4" />
                                                </button>
                                            </div>
                                            <div className="text-xs text-muted-foreground mt-1">
                                                Press Enter to send message
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Configuration Panel */}
            {showConfigPanel && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-card border border-border rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
                        <div className="flex items-center justify-between p-4 border-b border-border">
                            <h2 className="font-semibold flex items-center gap-2">
                                <Settings className="w-4 h-4" />
                                <span>Agent Configuration</span>
                            </h2>
                            <button
                                onClick={toggleConfigPanel}
                                className="p-1 rounded-md hover:bg-accent"
                                aria-label="Close configuration panel"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-auto p-4">
                            <div className="space-y-6">
                                <div>
                                    <h3 className="font-medium mb-3">Basic Settings</h3>
                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium mb-1">Agent Status</label>
                                            <select
                                                value={agentConfig.status}
                                                onChange={(e) => handleConfigChange('status', e.target.value)}
                                                className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
                                                aria-label="Agent Status"
                                            >
                                                <option value="draft">Draft</option>
                                                <option value="active">Active</option>
                                                <option value="inactive">Inactive</option>
                                                <option value="archived">Archived</option>
                                            </select>
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium mb-1">Model Configuration</label>
                                            <textarea
                                                value={JSON.stringify(agentConfig.model_config, null, 2)}
                                                onChange={(e) => {
                                                    try {
                                                        handleConfigChange('model_config', JSON.parse(e.target.value))
                                                    } catch {
                                                        // Keep previous value if invalid JSON
                                                    }
                                                }}
                                                className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground min-h-[100px] font-mono text-sm"
                                                placeholder="Enter JSON configuration"
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div>
                                    <h3 className="font-medium mb-3">Advanced Settings</h3>
                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium mb-1">Metadata</label>
                                            <textarea
                                                value={JSON.stringify(agentConfig.metadata, null, 2)}
                                                onChange={(e) => {
                                                    try {
                                                        handleConfigChange('metadata', JSON.parse(e.target.value))
                                                    } catch {
                                                        // Keep previous value if invalid JSON
                                                    }
                                                }}
                                                className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground min-h-[80px] font-mono text-sm"
                                                placeholder="Enter metadata as JSON"
                                            />
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium mb-1">Performance Settings</label>
                                            <div className="space-y-2">
                                                <label className="flex items-center gap-2">
                                                    <input type="checkbox" className="rounded" />
                                                    <span className="text-sm">Enable caching</span>
                                                </label>
                                                <label className="flex items-center gap-2">
                                                    <input type="checkbox" className="rounded" />
                                                    <span className="text-sm">Enable parallel processing</span>
                                                </label>
                                                <label className="flex items-center gap-2">
                                                    <input type="checkbox" className="rounded" />
                                                    <span className="text-sm">Enable real-time updates</span>
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div>
                                    <h3 className="font-medium mb-3">Security & Privacy</h3>
                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium mb-1">Data Retention</label>
                                            <select
                                                className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
                                                aria-label="Data Retention"
                                            >
                                                <option>30 days</option>
                                                <option>60 days</option>
                                                <option>90 days</option>
                                                <option>Never</option>
                                            </select>
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium mb-1">Access Control</label>
                                            <div className="space-y-2">
                                                <label className="flex items-center gap-2">
                                                    <input type="checkbox" className="rounded" />
                                                    <span className="text-sm">Public access</span>
                                                </label>
                                                <label className="flex items-center gap-2">
                                                    <input type="checkbox" className="rounded" />
                                                    <span className="text-sm">Team access only</span>
                                                </label>
                                                <label className="flex items-center gap-2">
                                                    <input type="checkbox" className="rounded" />
                                                    <span className="text-sm">Private (owner only)</span>
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="border-t border-border p-4 flex justify-end gap-2">
                            <button
                                onClick={toggleConfigPanel}
                                className="px-4 py-2 bg-secondary rounded-md hover:bg-secondary/80"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => {
                                    handleSave()
                                    toggleConfigPanel()
                                }}
                                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                            >
                                Save Configuration
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Keyboard Shortcuts Guide */}
            <div className="fixed bottom-4 right-4">
                <button
                    className="flex items-center gap-2 px-3 py-2 bg-secondary rounded-md hover:bg-secondary/80 text-sm"
                    onClick={() => toast('Keyboard shortcuts guide coming soon!', { icon: '⌨️' })}
                >
                    <Keyboard className="w-4 h-4" />
                    <span>Shortcuts</span>
                </button>
            </div>
        </div>
    )
}