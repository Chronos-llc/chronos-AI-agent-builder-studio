import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    Settings,
    User,
    Shield,
    Zap,
    Database,
    Key,
    Gauge,
    Brain,
    Globe,
    Clock,
    AlertTriangle,
    CheckCircle,
    Info,
    Upload,
    Download,
    Copy,
    Eye,
    EyeOff,
    Plus,
    Trash2,
    Edit,
    Save,
    X,
    ResetIcon,
    Sliders,
    BookOpen,
    Image as ImageIcon,
    Video as VideoIcon,
    Camera,
    Mic,
    Volume2,
    Smile,
    GitBranch,
    GitCommit,
    GitMerge,
    GitPullRequest
} from 'lucide-react';

interface SubAgentConfig {
    summary_agent: {
        enabled: boolean;
        summary_max_tokens: number;
        transcript_max_lines: number;
        model: string;
        exposed_variables: Record<string, string>;
    };
    translator_agent: {
        enabled: boolean;
        detect_initial_language: boolean;
        detect_language_change: boolean;
        model: string;
        exposed_variables: Record<string, string>;
    };
    knowledge_agent: {
        enabled: boolean;
        answer_manually: boolean;
        additional_context: boolean;
        model_strategy: string;
        fastest_model: string;
        best_model: string;
        question_extractor_model: string;
        chunks_count: number;
        exposed_variables: Record<string, string>;
    };
    vision_agent: {
        enabled: boolean;
        extract_from_incoming_images: boolean;
        exposed_variables: Record<string, string>;
    };
    image_generation_agent: {
        enabled: boolean;
        generate_image: boolean;
        edit_images: boolean;
        exposed_variables: Record<string, string>;
    };
    video_agent: {
        enabled: boolean;
        generate_video: boolean;
        analyze_incoming_videos: boolean;
        exposed_variables: Record<string, string>;
    };
    personality_agent: {
        enabled: boolean;
        personality_traits: Record<string, number>;
        tone_style: string;
    };
    policy_agent: {
        enabled: boolean;
        compliance_rules: string[];
        content_filters: string[];
    };
}

const SubAgentConfigPanel: React.FC<{ agentId: number }> = ({ agentId }) => {
    const [activeTab, setActiveTab] = useState<'summary' | 'translator' | 'knowledge' | 'vision' | 'image' | 'video' | 'personality' | 'policy'>('summary');
    const [config, setConfig] = useState<SubAgentConfig | null>(null);
    const [showConfirmReset, setShowConfirmReset] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    const queryClient = useQueryClient();

    // Fetch current sub-agent configuration
    const { data: subAgentConfig, isLoading: isConfigLoading } = useQuery({
        queryKey: ['sub-agent-config', agentId],
        queryFn: async () => {
            const response = await fetch(`/api/agents/${agentId}/sub-agent-config`);
            if (!response.ok) throw new Error('Failed to fetch sub-agent configuration');
            return response.json();
        },
        enabled: !!agentId
    });

    // Fetch default configuration
    const { data: defaultConfig } = useQuery({
        queryKey: ['default-sub-agent-config', agentId],
        queryFn: async () => {
            const response = await fetch(`/api/agents/${agentId}/sub-agent-config/defaults`);
            if (!response.ok) throw new Error('Failed to fetch default configuration');
            return response.json();
        },
        enabled: !!agentId
    });

    // Save configuration mutation
    const saveConfigMutation = useMutation({
        mutationFn: async (config: SubAgentConfig) => {
            const response = await fetch(`/api/agents/${agentId}/sub-agent-config`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sub_agent_config: config })
            });
            if (!response.ok) throw new Error('Failed to save sub-agent configuration');
            return response.json();
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['sub-agent-config', agentId] });
        }
    });

    // Reset configuration mutation
    const resetConfigMutation = useMutation({
        mutationFn: async () => {
            const response = await fetch(`/api/agents/${agentId}/sub-agent-config/reset`, {
                method: 'POST'
            });
            if (!response.ok) throw new Error('Failed to reset configuration');
            return response.json();
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['sub-agent-config', agentId] });
        }
    });

    // Initialize configuration
    useEffect(() => {
        if (subAgentConfig) {
            setConfig(subAgentConfig);
        } else if (defaultConfig) {
            setConfig(defaultConfig);
        }
        setIsLoading(false);
    }, [subAgentConfig, defaultConfig]);

    const updateConfig = (agentType: keyof SubAgentConfig, updates: Partial<SubAgentConfig[keyof SubAgentConfig]>) => {
        if (!config) return;
        setConfig(prev => prev ? {
            ...prev,
            [agentType]: {
                ...prev[agentType],
                ...updates
            }
        } : null);
    };

    const handleSave = () => {
        if (config) {
            saveConfigMutation.mutate(config);
        }
    };

    const handleReset = () => {
        setShowConfirmReset(true);
    };

    const confirmReset = () => {
        resetConfigMutation.mutate();
        setShowConfirmReset(false);
    };

    if (isLoading || isConfigLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-2">Loading sub-agent configuration...</span>
            </div>
        );
    }

    if (!config) {
        return (
            <div className="text-center py-8 text-gray-500">
                <AlertTriangle className="w-8 h-8 mx-auto mb-2" />
                <p>Configuration not available</p>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col">
            {/* Header */}
            <div className="border-b border-gray-200 pb-4 mb-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <Sliders className="w-6 h-6 text-blue-600" />
                        <h2 className="text-xl font-semibold text-gray-900">Sub-Agent Configuration</h2>
                    </div>
                    <div className="flex items-center space-x-2">
                        <button
                            onClick={handleReset}
                            disabled={resetConfigMutation.isPending}
                            className="flex items-center space-x-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors disabled:opacity-50"
                        >
                            <ResetIcon className="w-4 h-4" />
                            <span>{resetConfigMutation.isPending ? 'Resetting...' : 'Reset to Defaults'}</span>
                        </button>
                        <button
                            onClick={handleSave}
                            disabled={saveConfigMutation.isPending}
                            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                        >
                            <Save className="w-4 h-4" />
                            <span>{saveConfigMutation.isPending ? 'Saving...' : 'Save Configuration'}</span>
                        </button>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex space-x-1 mt-4 overflow-x-auto">
                    {[ 
                        { id: 'summary', label: 'Summary Agent', icon: BookOpen },
                        { id: 'translator', label: 'Translator Agent', icon: Globe },
                        { id: 'knowledge', label: 'Knowledge Agent', icon: Brain },
                        { id: 'vision', label: 'Vision Agent', icon: Eye },
                        { id: 'image', label: 'Image Generation', icon: ImageIcon },
                        { id: 'video', label: 'Video Agent', icon: VideoIcon },
                        { id: 'personality', label: 'Personality Agent', icon: Smile },
                        { id: 'policy', label: 'Policy Agent', icon: Shield }
                    ].map(({ id, label, icon: Icon }) => (
                        <button
                            key={id}
                            onClick={() => setActiveTab(id as any)}
                            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors whitespace-nowrap ${activeTab === id
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'text-gray-600 hover:bg-gray-100'
                                }`}
                        >
                            <Icon className="w-4 h-4" />
                            <span>{label}</span>
                        </button>
                    ))}
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-auto">
                {activeTab === 'summary' && (
                    <div className="space-y-6">
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-blue-900">Summary Agent Configuration</h3>
                                    <p className="text-sm text-blue-700 mt-1">
                                        Configure automatic conversation summarization and transcript management.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.summary_agent.enabled}
                                    onChange={(e) => updateConfig('summary_agent', { enabled: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Enable Summary Agent</span>
                                    <p className="text-sm text-gray-500">Enable automatic conversation summarization</p>
                                </div>
                            </label>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Summary Max Tokens: {config.summary_agent.summary_max_tokens}
                                </label>
                                <input
                                    type="range"
                                    min="50"
                                    max="500"
                                    step="10"
                                    value={config.summary_agent.summary_max_tokens}
                                    onChange={(e) => updateConfig('summary_agent', { summary_max_tokens: parseInt(e.target.value) })}
                                    className="w-full"
                                />
                                <div className="flex justify-between text-xs text-gray-500 mt-1">
                                    <span>50</span>
                                    <span>275</span>
                                    <span>500</span>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Transcript Max Lines: {config.summary_agent.transcript_max_lines}
                                </label>
                                <input
                                    type="range"
                                    min="5"
                                    max="50"
                                    step="1"
                                    value={config.summary_agent.transcript_max_lines}
                                    onChange={(e) => updateConfig('summary_agent', { transcript_max_lines: parseInt(e.target.value) })}
                                    className="w-full"
                                />
                                <div className="flex justify-between text-xs text-gray-500 mt-1">
                                    <span>5</span>
                                    <span>27</span>
                                    <span>50</span>
                                </div>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Summary Generation Model
                            </label>
                            <select
                                value={config.summary_agent.model}
                                onChange={(e) => updateConfig('summary_agent', { model: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                <option value="gpt-4">GPT-4</option>
                                <option value="claude-3">Claude 3</option>
                                <option value="gemini-pro">Gemini Pro</option>
                            </select>
                        </div>

                        <div className="border border-gray-200 rounded-lg p-4">
                            <h3 className="font-medium mb-4">Exposed Variables</h3>
                            <div className="space-y-2 text-sm">
                                {Object.entries(config.summary_agent.exposed_variables).map(([key, value]) => (
                                    <div key={key} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                        <code className="text-blue-600">{key}</code>
                                        <span className="text-gray-600">{value}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'translator' && (
                    <div className="space-y-6">
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <Info className="w-5 h-5 text-green-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-green-900">Translator Agent Configuration</h3>
                                    <p className="text-sm text-green-700 mt-1">
                                        Configure automatic language detection and translation capabilities.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.translator_agent.enabled}
                                    onChange={(e) => updateConfig('translator_agent', { enabled: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Enable Translator Agent</span>
                                    <p className="text-sm text-gray-500">Enable automatic language translation</p>
                                </div>
                            </label>

                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.translator_agent.detect_initial_language}
                                    onChange={(e) => updateConfig('translator_agent', { detect_initial_language: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Detect Initial User Language</span>
                                    <p className="text-sm text-gray-500">Automatically detect the user's initial language</p>
                                </div>
                            </label>

                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.translator_agent.detect_language_change}
                                    onChange={(e) => updateConfig('translator_agent', { detect_language_change: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Detect Language Changes</span>
                                    <p className="text-sm text-gray-500">Detect when user changes language during conversation</p>
                                </div>
                            </label>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Translation Model
                            </label>
                            <select
                                value={config.translator_agent.model}
                                onChange={(e) => updateConfig('translator_agent', { model: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                <option value="gpt-4">GPT-4</option>
                                <option value="claude-3">Claude 3</option>
                                <option value="gemini-pro">Gemini Pro</option>
                            </select>
                        </div>

                        <div className="border border-gray-200 rounded-lg p-4">
                            <h3 className="font-medium mb-4">Exposed Variables</h3>
                            <div className="space-y-2 text-sm">
                                {Object.entries(config.translator_agent.exposed_variables).map(([key, value]) => (
                                    <div key={key} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                        <code className="text-green-600">{key}</code>
                                        <span className="text-gray-600">{value}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'knowledge' && (
                    <div className="space-y-6">
                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <Info className="w-5 h-5 text-purple-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-purple-900">Knowledge Agent Configuration</h3>
                                    <p className="text-sm text-purple-700 mt-1">
                                        Configure knowledge retrieval and question answering capabilities.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.knowledge_agent.enabled}
                                    onChange={(e) => updateConfig('knowledge_agent', { enabled: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Enable Knowledge Agent</span>
                                    <p className="text-sm text-gray-500">Enable knowledge-based question answering</p>
                                </div>
                            </label>

                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.knowledge_agent.answer_manually}
                                    onChange={(e) => updateConfig('knowledge_agent', { answer_manually: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Allow Manual Answers</span>
                                    <p className="text-sm text-gray-500">Allow manual intervention for complex questions</p>
                                </div>
                            </label>

                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.knowledge_agent.additional_context}
                                    onChange={(e) => updateConfig('knowledge_agent', { additional_context: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Use Additional Context</span>
                                    <p className="text-sm text-gray-500">Include additional context from conversation history</p>
                                </div>
                            </label>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Model Strategy
                            </label>
                            <select
                                value={config.knowledge_agent.model_strategy}
                                onChange={(e) => updateConfig('knowledge_agent', { model_strategy: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option value="Fastest">Fastest</option>
                                <option value="Hybrid">Hybrid</option>
                                <option value="Best">Best</option>
                            </select>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Fastest Model
                                </label>
                                <select
                                    value={config.knowledge_agent.fastest_model}
                                    onChange={(e) => updateConfig('knowledge_agent', { fastest_model: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                >
                                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                    <option value="gpt-4">GPT-4</option>
                                    <option value="claude-3">Claude 3</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Best Model
                                </label>
                                <select
                                    value={config.knowledge_agent.best_model}
                                    onChange={(e) => updateConfig('knowledge_agent', { best_model: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                >
                                    <option value="gpt-4">GPT-4</option>
                                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                    <option value="claude-3">Claude 3</option>
                                </select>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Question Extractor Model
                            </label>
                            <select
                                value={config.knowledge_agent.question_extractor_model}
                                onChange={(e) => updateConfig('knowledge_agent', { question_extractor_model: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                <option value="gpt-4">GPT-4</option>
                                <option value="claude-3">Claude 3</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Chunks Count: {config.knowledge_agent.chunks_count}
                            </label>
                            <input
                                type="range"
                                min="5"
                                max="50"
                                step="1"
                                value={config.knowledge_agent.chunks_count}
                                onChange={(e) => updateConfig('knowledge_agent', { chunks_count: parseFloat(e.target.value) })}
                                className="w-full"
                            />
                            <div className="flex justify-between text-xs text-gray-500 mt-1">
                                <span>5</span>
                                <span>27</span>
                                <span>50</span>
                            </div>
                        </div>

                        <div className="border border-gray-200 rounded-lg p-4">
                            <h3 className="font-medium mb-4">Exposed Variables</h3>
                            <div className="space-y-2 text-sm">
                                {Object.entries(config.knowledge_agent.exposed_variables).map(([key, value]) => (
                                    <div key={key} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                        <code className="text-purple-600">{key}</code>
                                        <span className="text-gray-600">{value}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'vision' && (
                    <div className="space-y-6">
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-blue-900">Vision Agent Configuration</h3>
                                    <p className="text-sm text-blue-700 mt-1">
                                        Configure image analysis and content extraction capabilities.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.vision_agent.enabled}
                                    onChange={(e) => updateConfig('vision_agent', { enabled: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Enable Vision Agent</span>
                                    <p className="text-sm text-gray-500">Enable image content analysis</p>
                                </div>
                            </label>

                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.vision_agent.extract_from_incoming_images}
                                    onChange={(e) => updateConfig('vision_agent', { extract_from_incoming_images: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Extract from Incoming Images</span>
                                    <p className="text-sm text-gray-500">Automatically extract content from uploaded images</p>
                                </div>
                            </label>
                        </div>

                        <div className="border border-gray-200 rounded-lg p-4">
                            <h3 className="font-medium mb-4">Exposed Variables</h3>
                            <div className="space-y-2 text-sm">
                                {Object.entries(config.vision_agent.exposed_variables).map(([key, value]) => (
                                    <div key={key} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                        <code className="text-blue-600">{key}</code>
                                        <span className="text-gray-600">{value}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'image' && (
                    <div className="space-y-6">
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <Info className="w-5 h-5 text-green-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-green-900">Image Generation Agent Configuration</h3>
                                    <p className="text-sm text-green-700 mt-1">
                                        Configure automatic image generation and editing capabilities.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.image_generation_agent.enabled}
                                    onChange={(e) => updateConfig('image_generation_agent', { enabled: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Enable Image Generation Agent</span>
                                    <p className="text-sm text-gray-500">Enable automatic image generation</p>
                                </div>
                            </label>

                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.image_generation_agent.generate_image}
                                    onChange={(e) => updateConfig('image_generation_agent', { generate_image: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Generate Images</span>
                                    <p className="text-sm text-gray-500">Generate new images based on prompts</p>
                                </div>
                            </label>

                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.image_generation_agent.edit_images}
                                    onChange={(e) => updateConfig('image_generation_agent', { edit_images: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Edit Images</span>
                                    <p className="text-sm text-gray-500">Enable image editing capabilities</p>
                                </div>
                            </label>
                        </div>

                        <div className="border border-gray-200 rounded-lg p-4">
                            <h3 className="font-medium mb-4">Exposed Variables</h3>
                            <div className="space-y-2 text-sm">
                                {Object.entries(config.image_generation_agent.exposed_variables).map(([key, value]) => (
                                    <div key={key} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                        <code className="text-green-600">{key}</code>
                                        <span className="text-gray-600">{value}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'video' && (
                    <div className="space-y-6">
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <Info className="w-5 h-5 text-red-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-red-900">Video Agent Configuration</h3>
                                    <p className="text-sm text-red-700 mt-1">
                                        Configure video generation and analysis capabilities.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.video_agent.enabled}
                                    onChange={(e) => updateConfig('video_agent', { enabled: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Enable Video Agent</span>
                                    <p className="text-sm text-gray-500">Enable video processing capabilities</p>
                                </div>
                            </label>

                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.video_agent.generate_video}
                                    onChange={(e) => updateConfig('video_agent', { generate_video: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Generate Videos</span>
                                    <p className="text-sm text-gray-500">Enable video generation from prompts</p>
                                </div>
                            </label>

                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.video_agent.analyze_incoming_videos}
                                    onChange={(e) => updateConfig('video_agent', { analyze_incoming_videos: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Analyze Incoming Videos</span>
                                    <p className="text-sm text-gray-500">Automatically analyze uploaded videos</p>
                                </div>
                            </label>
                        </div>

                        <div className="border border-gray-200 rounded-lg p-4">
                            <h3 className="font-medium mb-4">Exposed Variables</h3>
                            <div className="space-y-2 text-sm">
                                {Object.entries(config.video_agent.exposed_variables).map(([key, value]) => (
                                    <div key={key} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                        <code className="text-red-600">{key}</code>
                                        <span className="text-gray-600">{value}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'personality' && (
                    <div className="space-y-6">
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <Info className="w-5 h-5 text-yellow-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-yellow-900">Personality Agent Configuration</h3>
                                    <p className="text-sm text-yellow-700 mt-1">
                                        Configure the agent's personality traits and communication style.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.personality_agent.enabled}
                                    onChange={(e) => updateConfig('personality_agent', { enabled: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Enable Personality Agent</span>
                                    <p className="text-sm text-gray-500">Enable personality-based response generation</p>
                                </div>
                            </label>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Tone Style
                            </label>
                            <select
                                value={config.personality_agent.tone_style}
                                onChange={(e) => updateConfig('personality_agent', { tone_style: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option value="balanced">Balanced</option>
                                <option value="friendly">Friendly</option>
                                <option value="professional">Professional</option>
                                <option value="casual">Casual</option>
                                <option value="formal">Formal</option>
                            </select>
                        </div>

                        <div className="border border-gray-200 rounded-lg p-4">
                            <h3 className="font-medium mb-4">Personality Traits</h3>
                            <div className="space-y-4">
                                {Object.entries(config.personality_agent.personality_traits).map(([trait, value]) => (
                                    <div key={trait} className="space-y-2">
                                        <label className="block text-sm font-medium text-gray-700 capitalize">
                                            {trait}: {value}
                                        </label>
                                        <input
                                            type="range"
                                            min="0"
                                            max="1"
                                            step="0.1"
                                            value={value}
                                            onChange={(e) => updateConfig('personality_agent', {
                                                personality_traits: {
                                                    ...config.personality_agent.personality_traits,
                                                    [trait]: parseFloat(e.target.value)
                                                }
                                            })}
                                            className="w-full"
                                        />
                                        <div className="flex justify-between text-xs text-gray-500">
                                            <span>0.0</span>
                                            <span>0.5</span>
                                            <span>1.0</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'policy' && (
                    <div className="space-y-6">
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <Info className="w-5 h-5 text-red-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-red-900">Policy Agent Configuration</h3>
                                    <p className="text-sm text-red-700 mt-1">
                                        Configure content policies, compliance rules, and safety filters.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={config.policy_agent.enabled}
                                    onChange={(e) => updateConfig('policy_agent', { enabled: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Enable Policy Agent</span>
                                    <p className="text-sm text-gray-500">Enable content policy enforcement</p>
                                </div>
                            </label>
                        </div>

                        <div className="border border-gray-200 rounded-lg p-4">
                            <h3 className="font-medium mb-4">Compliance Rules</h3>
                            <div className="space-y-2">
                                {config.policy_agent.compliance_rules.map((rule, index) => (
                                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                        <span className="text-sm">{rule}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="border border-gray-200 rounded-lg p-4">
                            <h3 className="font-medium mb-4">Content Filters</h3>
                            <div className="space-y-2">
                                {config.policy_agent.content_filters.map((filter, index) => (
                                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                        <span className="text-sm">{filter}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Reset Confirmation Dialog */}
            {showConfirmReset && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-md">
                        <h3 className="text-lg font-medium mb-4">Reset Configuration</h3>
                        <p className="text-gray-600 mb-6">
                            Are you sure you want to reset all sub-agent configurations to their default values?
                            This action cannot be undone.
                        </p>
                        <div className="flex space-x-3">
                            <button
                                onClick={() => setShowConfirmReset(false)}
                                disabled={resetConfigMutation.isPending}
                                className="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={confirmReset}
                                disabled={resetConfigMutation.isPending}
                                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                            >
                                {resetConfigMutation.isPending ? 'Resetting...' : 'Reset Configuration'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SubAgentConfigPanel;