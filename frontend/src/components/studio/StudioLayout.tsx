import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { toast } from 'react-hot-toast'
import { ActionsPanel } from './ActionsPanel'
import VersionControlPanel from './VersionControlPanel'
import BotSettingsPanel from './BotSettingsPanel'
import SubAgentConfigPanel from './SubAgentConfigPanel'
import { Loader2, Save, Settings, Users, FileText, Database, Code, MessageSquare, Play, Pause, Stop, Maximize, Minimize, PanelLeftClose, PanelRightClose, PanelLeftOpen, PanelRightOpen, Moon, Sun, Keyboard, Plus, Upload, Trash2, Edit, Search, Filter, MoreVertical, ChevronDown, ChevronUp, ChevronLeft, ChevronRight, X, Check, AlertTriangle, Info, HelpCircle, GitBranch, GitCommit, GitMerge, GitPullRequest, Cloud, CloudOffline, Wifi, WifiOff, User, Users as UsersIcon, MessageCircle, Bell, BarChart2, PieChart, LineChart, File, Folder, Image, Video, Code as CodeIcon, Terminal, Cpu, Server, Globe, Lock, Unlock, Eye, EyeOff, Star, Heart, ThumbsUp, ThumbsDown, Share, Download, Bookmark, Flag, Tag, Hash, Sliders, Grid, List, Layout, LayoutDashboard, LayoutGrid, LayoutList, Palette, Paintbrush, Droplet, Sun as SunIcon, Moon as MoonIcon, Sunrise, Sunset, Wind, CloudRain, Snowflake, Thermometer, Activity, AlertCircle, Archive, Award, BarChart, Battery, BatteryCharging, BellOff, Bluetooth, Bold, Book, BookOpen, Box, Briefcase, Calendar, Camera, CameraOff, Car, Cast, CheckCircle, CheckSquare, ChevronDown as ChevronDownIcon, ChevronUp as ChevronUpIcon, ChevronLeft as ChevronLeftIcon, ChevronRight as ChevronRightIcon, Chrome, Circle, Clipboard, Clock, CloudDrizzle, CloudLightning, CloudSnow, CloudSun, Cloudy, Codepen, Coffee, Command, Compass, Copy, CornerDownLeft, CornerDownRight, CornerLeftDown, CornerLeftUp, CornerRightDown, CornerRightUp, CornerUpLeft, CornerUpRight, Cpu as CpuIcon, CreditCard, Crop, Crosshair, Database as DatabaseIcon, Delete, Disc, Divide, DollarSign, DownloadCloud, Droplet as DropletIcon, Edit2, Edit3, ExternalLink, EyeOff as EyeOffIcon, Facebook, FastForward, Feather, Figma, FileMinus, FilePlus, FileText as FileTextIcon, Film, Filter as FilterIcon, Flag as FlagIcon, FolderMinus, FolderPlus, Frown, Gift, GitBranch as GitBranchIcon, GitCommit as GitCommitIcon, GitMerge as GitMergeIcon, GitPullRequest as GitPullRequestIcon, Github, Gitlab, Globe as GlobeIcon, Grid as GridIcon, HardDrive, Hash as HashIcon, Headphones, Heart as HeartIcon, HelpCircle as HelpCircleIcon, Home, Image as ImageIcon, Inbox, Info as InfoIcon, Instagram, Italic, Key, Layers, Layout as LayoutIcon, LifeBuoy, Link, Link2, Linkedin, List as ListIcon, Loader, Lock as LockIcon, LogIn, LogOut, Mail, Map, MapPin, Maximize2, Meh, Menu, MessageCircle as MessageCircleIcon, MessageSquare as MessageSquareIcon, Mic, MicOff, Minimize2, Minus, MinusCircle, MinusSquare, Monitor, Moon as MoonIcon2, MoreHorizontal, MoreVertical as MoreVerticalIcon, MousePointer, Move, Music, Navigation, Navigation2, Octagon, Package, Paperclip, PauseCircle, PenTool, Percent, Phone, PhoneCall, PhoneForwarded, PhoneIncoming, PhoneMissed, PhoneOff, PhoneOutgoing, PieChart as PieChartIcon, PlayCircle, PlusCircle, PlusSquare, Pocket, Power, Printer, Radio, RefreshCcw, RefreshCw, Repeat, Rewind, RotateCcw, RotateCw, Rss, Save as SaveIcon, Scissors, Search as SearchIcon, Send, Server as ServerIcon, Settings as SettingsIcon, Share2, Shield, ShieldOff, ShoppingBag, ShoppingCart, Shuffle, Sidebar, SkipBack, SkipForward, Slack, Slash, Sliders as SlidersIcon, Smartphone, Smile, Speaker, Square, Star as StarIcon, StopCircle, Sun as SunIcon2, Sunrise as SunriseIcon, Sunset as SunsetIcon, Table, Tablet, Tag as TagIcon, Target, Terminal as TerminalIcon, Thermometer as ThermometerIcon, ThumbsDown as ThumbsDownIcon, ThumbsUp as ThumbsUpIcon, ToggleLeft, ToggleRight, Tool, Trash, Trash2 as Trash2Icon, Trello, TrendingDown, TrendingUp, Triangle, Truck, Tv, Twitch, Twitter, Type, Umbrella, Underline, Unlock as UnlockIcon, UploadCloud, UserCheck, UserMinus, UserPlus, UserX, Users as UsersIcon2, Video as VideoIcon, VideoOff, Voicemail, Volume, Volume1, Volume2, VolumeX, Watch, Wifi as WifiIcon, WifiOff as WifiOffIcon, Wind as WindIcon, XCircle, XOctagon, XSquare, Youtube, Zap, ZapOff, ZoomIn, ZoomOut } from 'lucide-react'

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
    const [collaborators, setCollaborators] = useState<any[]>([])
    const [onlineUsers, setOnlineUsers] = useState<number>(0)

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
        queryFn: async () => {
            if (!id) return []
            // Mock data for now
            return [
                { id: '1', name: 'Getting Started Guide', type: 'text', size: 1024, content: 'Welcome to the AI Agent Studio...', metadata: {}, created_at: new Date().toISOString() },
                { id: '2', name: 'API Documentation', type: 'pdf', size: 2048, content: 'API documentation content...', metadata: {}, created_at: new Date().toISOString() }
            ]
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
                content: `I received your message: "${newMessage}". How can I assist you further?`,
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
            toast.info('Emulator mode activated')
        } else {
            toast.info('Emulator mode deactivated')
        }
    }

    // Handle testing
    const handleStartTesting = () => {
        setIsTesting(true)
        setTestResults([])
        toast.info('Testing started...')
        
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
                        <h1 className="text-xl font-bold">
                            {agentConfig.name || 'AI Agent Studio'}
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
                            className="flex flex-col border-r border-border bg-card overflow-hidden"
                            style={{ width: panelSizes.left }}
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
                        className="flex flex-col border-r border-border bg-card overflow-hidden"
                        style={{ width: showSidebar ? panelSizes.center : `calc(100% - ${showToolsPanel ? panelSizes.right : 0}px)` }}
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
                            className="flex flex-col border-r border-border bg-card overflow-hidden"
                            style={{ width: panelSizes.right }}
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
                                                                >
                                                                    <Info className="w-3 h-3" />
                                                                    <span>Details</span>
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
                                                placeholder='Enter JSON configuration'
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
                                                placeholder='Enter metadata as JSON'
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
                                            <select className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground">
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
                    onClick={() => toast.info('Keyboard shortcuts guide coming soon!')}
                >
                    <Keyboard className="w-4 h-4" />
                    <span>Shortcuts</span>
                </button>
            </div>
        </div>
    )
}