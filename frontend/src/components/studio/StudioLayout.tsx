import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import VersionControlPanel from './VersionControlPanel'
import BotSettingsPanel from './BotSettingsPanel'
import SubAgentConfigPanel from './SubAgentConfigPanel'
import FuzzyPanel from './FuzzyPanel'
import WorkflowBuilder from './WorkflowBuilder'
import AIWorkflowGenerator from './AIWorkflowGenerator'
import PatternVisualizer from './PatternVisualizer'
import ConfigManager from './ConfigManager'
import OptimizationDashboard from './OptimizationDashboard'
import { ActionsPanel } from './ActionsPanel'
import { ToolsPanel, ToolIntegration } from './ToolsPanel'
import { Loader2, Save, Settings, Users, FileText, Database, Code, MessageSquare, Keyboard, Plus, GitBranch, Send, Zap, Workflow, Settings2, BarChart3, ShoppingCart, Copy } from 'lucide-react'
import { PublishButton } from './PublishButton'
import CopiedAgentsManager from './CopiedAgentsManager'

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

interface ChatMessage {
    id: string
    role: 'user' | 'agent' | 'system'
    content: string
    timestamp: string
    status: 'sent' | 'delivered' | 'read' | 'error'
    metadata?: any
}

export const StudioLayout = () => {
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
    const [activeTab, setActiveTab] = useState<'instructions' | 'knowledge' | 'tools' | 'chat' | 'config' | 'actions' | 'versions' | 'settings' | 'sub-agents' | 'fuzzy' | 'workflow' | 'optimization' | 'marketplace'>('instructions')
    const [workflowSubTab, setWorkflowSubTab] = useState<'builder' | 'generator' | 'patterns'>('builder')
    const [marketplaceSubTab, setMarketplaceSubTab] = useState<'copied-agents' | 'browse'>('copied-agents')

    // Note: Resizable panel functionality would require implementing panel drag handling
    // and using panelSizes in the component's JSX for width/height styling

    // State for agent data fetching
    useEffect(() => {
        const fetchAgentData = async () => {
            if (!id) return
            try {
                setIsLoading(true)
                // In a real app, this would be an API call
                // const response = await axios.get(`/api/agents/${id}`)
                // setAgentConfig(response.data)
            } catch (error) {
                console.error('Error fetching agent data:', error)
                toast.error('Failed to load agent data')
            } finally {
                setIsLoading(false)
            }
        }
        fetchAgentData()
    }, [id])

    const handleSave = async () => {
        try {
            setIsSaving(true)
            // In a real app, this would be an API call
            // await axios.put(`/api/agents/${id}`, agentConfig)
            toast.success('Agent configuration saved successfully')
        } catch (error) {
            console.error('Error saving agent:', error)
            toast.error('Failed to save agent configuration')
        } finally {
            setIsSaving(false)
        }
    }

    const handleSendMessage = () => {
        if (!newMessage.trim()) return
        const newMessageObj: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: newMessage,
            timestamp: new Date().toISOString(),
            status: 'sent'
        }
        setChatMessages(prev => [...prev, newMessageObj])
        setNewMessage('')
    }
    const handleAddKnowledgeItem = () => {
        const newItem: KnowledgeItem = {
            id: Date.now().toString(),
            name: `Knowledge Item ${knowledgeItems.length + 1}`,
            type: 'text',
            size: 0,
            content: '',
            metadata: {},
            created_at: new Date().toISOString()
        }
        setKnowledgeItems(prev => [...prev, newItem])
        toast.success('Knowledge item added!')
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-full">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        )
    }

    return (
        <div className="flex h-screen bg-background overflow-hidden">
            {/* Sidebar - Fixed position with independent scrolling */}
            <div className="fixed inset-y-0 left-0 w-64 border-r border-border bg-card z-30">
                <div className="h-full flex flex-col">
                    <div className="p-4 border-b border-border shrink-0">
                        <h2 className="font-semibold text-lg">Agent Studio</h2>
                    </div>
                    <div className="flex-1 overflow-y-auto p-2 space-y-1">
                        <button
                            onClick={() => setActiveTab('instructions')}
                            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeTab === 'instructions' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            <FileText className="w-4 h-4" />
                            <span>Instructions</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('knowledge')}
                            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeTab === 'knowledge' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            <Database className="w-4 h-4" />
                            <span>Knowledge</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('tools')}
                            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeTab === 'tools' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            <Code className="w-4 h-4" />
                            <span>Tools</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('chat')}
                            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeTab === 'chat' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            <MessageSquare className="w-4 h-4" />
                            <span>Chat</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('config')}
                            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeTab === 'config' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            <Settings className="w-4 h-4" />
                            <span>Configuration</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('actions')}
                            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeTab === 'actions' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            <Zap className="w-4 h-4" />
                            <span>Actions</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('versions')}
                            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeTab === 'versions' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            <GitBranch className="w-4 h-4" />
                            <span>Versions</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('settings')}
                            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeTab === 'settings' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            <Settings2 className="w-4 h-4" />
                            <span>Settings</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('sub-agents')}
                            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeTab === 'sub-agents' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            <Users className="w-4 h-4" />
                            <span>Sub-Agents</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('fuzzy')}
                            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeTab === 'fuzzy' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            <Keyboard className="w-4 h-4" />
                            <span>Fuzzy Commands</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('workflow')}
                            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeTab === 'workflow' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            <Workflow className="w-4 h-4" />
                            <span>Workflow</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('optimization')}
                            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeTab === 'optimization' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            <BarChart3 className="w-4 h-4" />
                            <span>Optimization</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('marketplace')}
                            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeTab === 'marketplace' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        >
                            <ShoppingCart className="w-4 h-4" />
                            <span>Marketplace</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content - Add margin-left to account for fixed sidebar */}
            <div className="flex-1 flex flex-col overflow-hidden ml-64">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-border bg-card">
                    <div className="flex items-center gap-4">
                        <input
                            type="text"
                            value={agentConfig.name}
                            onChange={(e) => setAgentConfig({ ...agentConfig, name: e.target.value })}
                            className="text-xl font-semibold bg-transparent border-none focus:outline-none"
                            placeholder="Untitled Agent"
                        />
                        <span className="px-2 py-1 text-xs rounded-full bg-secondary text-secondary-foreground">
                            {agentConfig.status}
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={handleSave}
                            disabled={isSaving}
                            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
                        >
                            <Save className="w-4 h-4" />
                            <span>{isSaving ? 'Saving...' : 'Save'}</span>
                        </button>
                        <PublishButton
                            agentId={parseInt(id || '0')}
                            agentName={agentConfig.name || 'Untitled Agent'}
                            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-600/90 disabled:opacity-50"
                        />
                    </div>
                </div>

                {/* Content Area */}
                <div className="flex-1 overflow-auto p-6">
                    {activeTab === 'instructions' && (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Description</label>
                                <input
                                    type="text"
                                    value={agentConfig.description}
                                    onChange={(e) => setAgentConfig({ ...agentConfig, description: e.target.value })}
                                    className="w-full px-3 py-2 border border-input rounded-md bg-background"
                                    placeholder="Describe your agent..."
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">System Prompt</label>
                                <textarea
                                    value={agentConfig.system_prompt}
                                    onChange={(e) => setAgentConfig({ ...agentConfig, system_prompt: e.target.value })}
                                    className="w-full px-3 py-2 border border-input rounded-md bg-background min-h-[200px]"
                                    placeholder="You are a helpful AI assistant..."
                                />
                            </div>
                        </div>
                    )}
                    {activeTab === 'knowledge' && (
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <h3 className="text-lg font-medium">Knowledge Base</h3>
                                <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90" onClick={handleAddKnowledgeItem}>
                                    <Plus className="w-4 h-4" />
                                    <span>Add Knowledge</span>
                                </button>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                {knowledgeItems.map((item) => (
                                    <div key={item.id} className="p-4 border border-border rounded-lg">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="font-medium">{item.name}</span>
                                            <span className="px-2 py-0.5 text-xs rounded-full bg-secondary">{item.type}</span>
                                        </div>
                                        <p className="text-sm text-muted-foreground">{item.size} bytes</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                    {activeTab === 'config' && (
                        <ConfigManager configId={id || ''} />
                    )}
                    {activeTab === 'actions' && (
                        <ActionsPanel agentId={parseInt(id || '0')} />
                    )}
                    {activeTab === 'versions' && (
                        <VersionControlPanel agentId={parseInt(id || '0')} />
                    )}
                    {activeTab === 'settings' && (
                        <BotSettingsPanel agentId={parseInt(id || '0')} />
                    )}
                    {activeTab === 'sub-agents' && (
                        <SubAgentConfigPanel agentId={parseInt(id || '0')} />
                    )}
                    {activeTab === 'fuzzy' && (
                        <FuzzyPanel agentId={parseInt(id || '0')} />
                    )}
                    {activeTab === 'workflow' && (
                        <div className="space-y-4">
                            <div className="flex items-center gap-4 mb-4">
                                <button
                                    onClick={() => setWorkflowSubTab('builder')}
                                    className={`px-4 py-2 rounded-md ${workflowSubTab === 'builder' ? 'bg-primary text-primary-foreground' : 'bg-secondary'}`}
                                >
                                    Builder
                                </button>
                                <button
                                    onClick={() => setWorkflowSubTab('generator')}
                                    className={`px-4 py-2 rounded-md ${workflowSubTab === 'generator' ? 'bg-primary text-primary-foreground' : 'bg-secondary'}`}
                                >
                                    AI Generator
                                </button>
                                <button
                                    onClick={() => setWorkflowSubTab('patterns')}
                                    className={`px-4 py-2 rounded-md ${workflowSubTab === 'patterns' ? 'bg-primary text-primary-foreground' : 'bg-secondary'}`}
                                >
                                    Patterns
                                </button>
                            </div>
                            {workflowSubTab === 'builder' && <WorkflowBuilder />}
                            {workflowSubTab === 'generator' && <AIWorkflowGenerator />}
                            {workflowSubTab === 'patterns' && <PatternVisualizer />}
                        </div>
                    )}
                    {activeTab === 'optimization' && (
                        <OptimizationDashboard />
                    )}
                    {activeTab === 'tools' && (
                        <ToolsPanel
                            tools={tools}
                            onToolsChange={setTools}
                            onToolInstall={(toolId) => setTools(prev => prev.map(t => t.id === toolId ? { ...t, is_installed: true } : t))}
                            onToolUninstall={(toolId) => setTools(prev => prev.map(t => t.id === toolId ? { ...t, is_installed: false } : t))}
                        />
                    )}
                    {activeTab === 'chat' && (
                        <div className="space-y-4">
                            <div className="flex-1 overflow-auto space-y-4 p-4 border border-border rounded-lg h-[400px}">
                                {chatMessages.map((message) => (
                                    <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                        <div className={`max-w-[80%] p-3 rounded-lg ${message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-secondary'}`}>
                                            {message.content}
                                        </div>
                                    </div>
                                ))}
                            </div>
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={newMessage}
                                    onChange={(e) => setNewMessage(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                                    className="flex-1 px-3 py-2 border border-input rounded-md bg-background"
                                    placeholder="Type a message..."
                                />
                                <button
                                    onClick={handleSendMessage}
                                    className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                                >
                                    <Send className="w-4 h-4" />
                                    <span>Send</span>
                                </button>
                            </div>
                        </div>
                    )}
                    {activeTab === 'marketplace' && (
                        <div className="space-y-4">
                            <div className="flex items-center gap-4 mb-4">
                                <button
                                    onClick={() => setMarketplaceSubTab('copied-agents')}
                                    className={`px-4 py-2 rounded-md ${marketplaceSubTab === 'copied-agents' ? 'bg-primary text-primary-foreground' : 'bg-secondary'}`}
                                >
                                    <Copy className="w-4 h-4 mr-2" />
                                    My Copied Agents
                                </button>
                                <button
                                    onClick={() => setMarketplaceSubTab('browse')}
                                    className={`px-4 py-2 rounded-md ${marketplaceSubTab === 'browse' ? 'bg-primary text-primary-foreground' : 'bg-secondary'}`}
                                >
                                    <ShoppingCart className="w-4 h-4 mr-2" />
                                    Browse Marketplace
                                </button>
                            </div>
                            {marketplaceSubTab === 'copied-agents' && <CopiedAgentsManager />}
                            {marketplaceSubTab === 'browse' && (
                                <div className="space-y-4">
                                    <div className="bg-muted p-6 rounded-lg text-center">
                                        <h3 className="text-xl font-semibold mb-2">Marketplace Browser</h3>
                                        <p className="text-muted-foreground mb-4">
                                            Browse and discover agents from the Chronos AI Marketplace
                                        </p>
                                        <button
                                            onClick={() => window.open('/marketplace', '_blank')}
                                            className="px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                                        >
                                            Open Marketplace
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
