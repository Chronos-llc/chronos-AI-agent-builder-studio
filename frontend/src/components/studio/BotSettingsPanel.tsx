import React, { useState, useEffect, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    Settings,
    User,
    Shield,
    Zap,
    Key,
    Gauge,
    Brain,
    Info,
    Upload,
    Download,
    Eye,
    EyeOff,
    Plus,
    Trash2,
    Save,
    Globe,
    Mic,
    Cpu
} from 'lucide-react';
import { useModelCatalog } from '../../hooks/useModelCatalog';
import { ModelCatalogPicker } from './ModelCatalogPicker';
import { VoiceConfigurationPanel } from './VoiceConfigurationPanel';
import { useVirtualComputerConfig, VirtualComputerConfig } from '../../hooks/useVirtualComputerConfig';

interface BotSettings {
    // Basic Settings
    name: string;
    description: string;
    avatar_url?: string;
    agent_type: 'text' | 'voice';

    // LLM Configuration
    llm_model: string;
    llm_temperature: number;
    llm_max_tokens: number;
    llm_top_p: number;
    llm_frequency_penalty: number;
    llm_presence_penalty: number;

    // Performance Settings
    max_concurrent_requests: number;
    request_timeout: number;
    rate_limit_per_minute: number;
    rate_limit_per_hour: number;
    cache_enabled: boolean;
    cache_ttl: number;

    // Security & Privacy
    data_retention_days: number;
    allow_public_access: boolean;
    enable_encryption: boolean;
    log_level: 'debug' | 'info' | 'warn' | 'error';

    // Environment Variables
    environment_variables: Record<string, string>;
    api_keys: Record<string, string>;
    database_config: Record<string, any>;

    // Advanced Configuration
    custom_prompts: {
        system_prompt: string;
        user_prompt_template: string;
        error_handling_prompt: string;
    };

    // Monitoring
    enable_analytics: boolean;
    enable_monitoring: boolean;
    alert_email?: string;
    agentic_thinking_enabled: boolean;
}

interface EnvironmentVariable {
    key: string;
    value: string;
    description?: string;
    isSecret: boolean;
}

interface McpServer {
    id: number;
    server_id: string;
    name: string;
    is_active: boolean;
}

interface McpServerGroup {
    id: number;
    name: string;
    description?: string;
    algorithm?: string;
    health_check_interval?: number;
    failover_enabled?: boolean;
    is_active: boolean;
}

interface McpServerGroupMemberInfo {
    server_id: string;
    name: string;
    is_active: boolean;
    server_active?: boolean;
    weight?: number;
    priority?: number;
}

interface McpServerGroupInfo {
    group: McpServerGroup;
    members: McpServerGroupMemberInfo[];
    total_members: number;
    active_members: number;
}

interface VirtualComputerTestResult {
    stdout?: string;
    stderr?: string;
    exit_code?: number;
    duration_ms?: number;
    error?: string;
}

const BotSettingsPanel: React.FC<{ agentId: number }> = ({ agentId }) => {
    const [activeTab, setActiveTab] = useState<'basic' | 'llm' | 'voice' | 'performance' | 'security' | 'integrations' | 'env' | 'advanced'>('basic');
    const [showSecretValues, setShowSecretValues] = useState<Record<string, boolean>>({});
    const [newEnvVar, setNewEnvVar] = useState<EnvironmentVariable>({ key: '', value: '', isSecret: false });
    const [showAddEnvVar, setShowAddEnvVar] = useState(false);

    const queryClient = useQueryClient();
    const { data: modelCatalog } = useModelCatalog();
    const chatModels = modelCatalog?.models?.chat || [];
    const {
        config: virtualComputerConfig,
        isLoading: virtualComputerLoading,
        updateConfig: updateVirtualComputerConfig,
        updating: virtualComputerUpdating
    } = useVirtualComputerConfig(agentId);
    const [virtualComputer, setVirtualComputer] = useState<VirtualComputerConfig | null>(null);
    const [virtualComputerTestResult, setVirtualComputerTestResult] = useState<VirtualComputerTestResult | null>(null);

    const { data: mcpServers } = useQuery({
        queryKey: ['mcp-servers'],
        queryFn: async () => {
            const response = await fetch('/api/v1/enhanced-mcp/servers/?active_only=false');
            if (!response.ok) {
                throw new Error('Failed to fetch MCP servers');
            }
            return response.json() as Promise<McpServer[]>;
        }
    });

    const { data: mcpGroupInfos } = useQuery({
        queryKey: ['mcp-group-infos'],
        queryFn: async () => {
            const groupResponse = await fetch('/api/v1/enhanced-mcp/groups/');
            if (!groupResponse.ok) {
                throw new Error('Failed to fetch MCP groups');
            }
            const groups = await groupResponse.json() as McpServerGroup[];
            const infos = await Promise.all(
                groups.map(async (group) => {
                    const response = await fetch(`/api/v1/enhanced-mcp/groups/${encodeURIComponent(group.name)}/members/`);
                    if (!response.ok) {
                        return {
                            group,
                            members: [],
                            total_members: 0,
                            active_members: 0
                        } as McpServerGroupInfo;
                    }
                    return response.json() as Promise<McpServerGroupInfo>;
                })
            );
            return infos;
        }
    });

    // Fetch current settings
    const { data: settings, isLoading } = useQuery({
        queryKey: ['bot-settings', agentId],
        queryFn: async () => {
            const response = await fetch(`/api/v1/agents/${agentId}`);
            if (!response.ok) throw new Error('Failed to fetch settings');
            const agent = await response.json();
            return {
                name: agent.name,
                description: agent.description || '',
                agent_type: agent.agent_type || 'text',
                llm_model: agent.model_config?.llm_model || 'gpt-4',
                llm_temperature: agent.model_config?.temperature ?? 0.7,
                llm_max_tokens: agent.model_config?.max_tokens ?? 1000,
                custom_prompts: {
                    system_prompt: agent.system_prompt || '',
                    user_prompt_template: agent.user_prompt_template || '',
                    error_handling_prompt: ''
                },
                agentic_thinking_enabled: Boolean(agent.agentic_thinking_enabled)
            };
        }
    });

    // Save settings mutation
    const saveSettingsMutation = useMutation({
        mutationFn: async (settings: BotSettings) => {
            const response = await fetch(`/api/v1/agents/${agentId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: settings.name,
                    description: settings.description,
                    agent_type: settings.agent_type,
                    system_prompt: settings.custom_prompts?.system_prompt || '',
                    user_prompt_template: settings.custom_prompts?.user_prompt_template || '',
                    model_config: {
                        llm_model: settings.llm_model,
                        temperature: settings.llm_temperature,
                        max_tokens: settings.llm_max_tokens,
                        top_p: settings.llm_top_p,
                        frequency_penalty: settings.llm_frequency_penalty,
                        presence_penalty: settings.llm_presence_penalty
                    },
                    agentic_thinking_enabled: settings.agentic_thinking_enabled
                })
            });
            if (!response.ok) throw new Error('Failed to save settings');
            return response.json();
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['bot-settings', agentId] });
        }
    });

    // Initialize default settings if not loaded
    const [botSettings, setBotSettings] = useState<BotSettings>({
        name: '',
        description: '',
        agent_type: 'text',
        llm_model: 'gpt-4',
        llm_temperature: 0.7,
        llm_max_tokens: 1000,
        llm_top_p: 1.0,
        llm_frequency_penalty: 0.0,
        llm_presence_penalty: 0.0,
        max_concurrent_requests: 10,
        request_timeout: 30,
        rate_limit_per_minute: 60,
        rate_limit_per_hour: 1000,
        cache_enabled: true,
        cache_ttl: 300,
        data_retention_days: 30,
        allow_public_access: false,
        enable_encryption: true,
        log_level: 'info',
        api_keys: {},
        database_config: {},
        environment_variables: {},
        custom_prompts: {
            system_prompt: '',
            user_prompt_template: '',
            error_handling_prompt: ''
        },
        enable_analytics: true,
        enable_monitoring: true,
        agentic_thinking_enabled: false
    });

    useEffect(() => {
        if (settings) {
            setBotSettings(prevSettings => ({ ...prevSettings, ...settings }));
        }
    }, [settings]);

    useEffect(() => {
        if (virtualComputerConfig) {
            setVirtualComputer(virtualComputerConfig);
        }
    }, [virtualComputerConfig]);

    const allServerIds = useMemo(
        () => (mcpServers || []).filter(server => server.is_active).map(server => server.server_id),
        [mcpServers]
    );

    const groupInfos = useMemo(
        () => mcpGroupInfos || [],
        [mcpGroupInfos]
    );

    const groupedServerIds = useMemo(() => {
        const ids = new Set<string>();
        groupInfos.forEach(groupInfo => {
            groupInfo.members?.forEach(member => {
                ids.add(member.server_id);
            });
        });
        return ids;
    }, [groupInfos]);

    const ungroupedServers = useMemo(() => {
        return (mcpServers || []).filter(server => !groupedServerIds.has(server.server_id));
    }, [mcpServers, groupedServerIds]);

    const effectiveSelectedServerIds = useMemo(() => {
        if (!virtualComputer) return [];
        const selected = virtualComputer.mcp_server_ids || [];
        if (selected.length === 0) {
            return allServerIds;
        }
        return selected;
    }, [virtualComputer, allServerIds]);

    const updateSetting = (key: keyof BotSettings, value: any) => {
        setBotSettings(prev => ({ ...prev, [key]: value }));
    };

    const addEnvironmentVariable = () => {
        if (!newEnvVar.key) return;

        setBotSettings(prev => ({
            ...prev,
            environment_variables: {
                ...prev.environment_variables,
                [newEnvVar.key]: newEnvVar.value
            }
        }));

        setNewEnvVar({ key: '', value: '', isSecret: false });
        setShowAddEnvVar(false);
    };

    const removeEnvironmentVariable = (key: string) => {
        setBotSettings(prev => {
            const newEnv = { ...prev.environment_variables };
            delete newEnv[key];
            return { ...prev, environment_variables: newEnv };
        });
    };

    const toggleSecretValue = (key: string) => {
        setShowSecretValues(prev => ({ ...prev, [key]: !prev[key] }));
    };

    const updateVirtualComputerField = (field: keyof VirtualComputerConfig, value: any) => {
        setVirtualComputer(prev => (prev ? { ...prev, [field]: value } : prev));
    };

    const toggleMcpServer = (serverId: string) => {
        setVirtualComputer(prev => {
            if (!prev) return prev;
            const current = prev.mcp_server_ids || [];
            if (current.length === 0) {
                const next = allServerIds.filter(id => id !== serverId);
                return { ...prev, mcp_server_ids: next };
            }
            if (current.includes(serverId)) {
                return { ...prev, mcp_server_ids: current.filter(id => id !== serverId) };
            }
            return { ...prev, mcp_server_ids: [...current, serverId] };
        });
    };

    const toggleMcpGroup = (groupServerIds: string[]) => {
        if (!groupServerIds.length) return;
        setVirtualComputer(prev => {
            if (!prev) return prev;
            const current = prev.mcp_server_ids || [];
            if (current.length === 0) {
                const next = allServerIds.filter(id => !groupServerIds.includes(id));
                return { ...prev, mcp_server_ids: next };
            }
            const groupFullySelected = groupServerIds.every(id => current.includes(id));
            if (groupFullySelected) {
                return { ...prev, mcp_server_ids: current.filter(id => !groupServerIds.includes(id)) };
            }
            const next = Array.from(new Set([...current, ...groupServerIds]));
            return { ...prev, mcp_server_ids: next };
        });
    };

    const saveVirtualComputer = async () => {
        if (!virtualComputer) return;
        await updateVirtualComputerConfig({
            enabled: virtualComputer.enabled,
            provider: virtualComputer.provider,
            idle_timeout_seconds: virtualComputer.idle_timeout_seconds,
            max_runtime_seconds: virtualComputer.max_runtime_seconds,
            memory_mb: virtualComputer.memory_mb,
            cpu_cores: virtualComputer.cpu_cores,
            allow_network: virtualComputer.allow_network,
            mcp_enabled: virtualComputer.mcp_enabled,
            mcp_server_ids: virtualComputer.mcp_server_ids
        });
    };

    const testVirtualComputer = async () => {
        setVirtualComputerTestResult(null);
        try {
            const response = await fetch(`/api/v1/agents/${agentId}/virtual-computer/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code: 'print("Hello from Chronos Virtual Computer")',
                    inputs: { message: 'ping' }
                })
            });
            const result = await response.json();
            if (!response.ok) {
                setVirtualComputerTestResult({ error: result.detail || 'Failed to run sandbox test' });
                return;
            }
            setVirtualComputerTestResult({
                stdout: result.stdout,
                stderr: result.stderr,
                exit_code: result.exit_code,
                duration_ms: result.duration_ms
            });
        } catch (error: any) {
            setVirtualComputerTestResult({ error: error?.message || 'Failed to run sandbox test' });
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-2">Loading settings...</span>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col">
            {/* Header */}
            <div className="border-b border-border pb-4 mb-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <Settings className="w-6 h-6 text-primary" />
                        <h2 className="text-xl font-semibold text-foreground">Bot Settings</h2>
                    </div>
                    <button
                        onClick={() => saveSettingsMutation.mutate(botSettings)}
                        disabled={saveSettingsMutation.isPending}
                        className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                    >
                        <Save className="w-4 h-4" />
                        <span>{saveSettingsMutation.isPending ? 'Saving...' : 'Save Settings'}</span>
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex space-x-1 mt-4 overflow-x-auto">
                    {[
                        { id: 'basic', label: 'Basic', icon: User },
                        { id: 'llm', label: 'LLM Model', icon: Brain },
                        { id: 'voice', label: 'Voice', icon: Mic },
                        { id: 'performance', label: 'Performance', icon: Gauge },
                        { id: 'security', label: 'Security', icon: Shield },
                        { id: 'integrations', label: 'Integrations', icon: Globe },
                        { id: 'env', label: 'Environment', icon: Key },
                        { id: 'advanced', label: 'Advanced', icon: Zap }
                    ].map(({ id, label, icon: Icon }) => (
                        <button
                            key={id}
                            onClick={() => setActiveTab(id as any)}
                            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors whitespace-nowrap ${activeTab === id
                                    ? 'bg-primary/15 text-primary'
                                    : 'text-muted-foreground hover:bg-muted/40'
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
                {activeTab === 'basic' && (
                    <div className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Bot Name
                                </label>
                                <input
                                    type="text"
                                    value={botSettings.name}
                                    onChange={(e) => updateSetting('name', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="Enter bot name"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Avatar URL
                                </label>
                                <input
                                    type="url"
                                    value={botSettings.avatar_url || ''}
                                    onChange={(e) => updateSetting('avatar_url', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="https://example.com/avatar.png"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Description
                            </label>
                            <textarea
                                value={botSettings.description}
                                onChange={(e) => updateSetting('description', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                rows={4}
                                placeholder="Describe your bot's purpose and capabilities"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Agent Type
                            </label>
                            <div className="grid grid-cols-2 gap-3">
                                <label className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
                                    <input
                                        type="radio"
                                        value="text"
                                        checked={botSettings.agent_type === 'text'}
                                        onChange={(e) => updateSetting('agent_type', e.target.value)}
                                        className="mr-2 text-blue-600"
                                    />
                                    <span className="font-medium">Text Agent</span>
                                    <p className="text-xs text-gray-500 ml-2">For chat and text-based interactions</p>
                                </label>
                                <label className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:border-purple-500 transition-colors">
                                    <input
                                        type="radio"
                                        value="voice"
                                        checked={botSettings.agent_type === 'voice'}
                                        onChange={(e) => updateSetting('agent_type', e.target.value)}
                                        className="mr-2 text-purple-600"
                                    />
                                    <span className="font-medium">Voice Agent</span>
                                    <p className="text-xs text-gray-500 ml-2">For voice and speech-based interactions</p>
                                </label>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                System Prompt
                            </label>
                            <textarea
                                value={botSettings.custom_prompts.system_prompt}
                                onChange={(e) => updateSetting('custom_prompts', {
                                    ...botSettings.custom_prompts,
                                    system_prompt: e.target.value
                                })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                                rows={6}
                                placeholder="Define the bot's core behavior and personality..."
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                User Prompt Template
                            </label>
                            <textarea
                                value={botSettings.custom_prompts.user_prompt_template}
                                onChange={(e) => updateSetting('custom_prompts', {
                                    ...botSettings.custom_prompts,
                                    user_prompt_template: e.target.value
                                })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                                rows={4}
                                placeholder="Template for user interactions with variables like {{user_input}}"
                            />
                        </div>
                    </div>
                )}

                {activeTab === 'llm' && (
                    <div className="space-y-6">
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-blue-900">LLM Configuration</h3>
                                    <p className="text-sm text-blue-700 mt-1">
                                        Fine-tune the language model behavior. Higher temperature = more creative, lower = more focused.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <ModelCatalogPicker
                            capability="chat"
                            providers={modelCatalog?.providers || []}
                            models={chatModels}
                            value={botSettings.llm_model}
                            onChange={(model) => updateSetting('llm_model', model)}
                            label="Model"
                            helperText="Select a provider to see its available models."
                        />

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label htmlFor="llm-temperature" className="block text-sm font-medium text-gray-700 mb-2">
                                    Temperature: {botSettings.llm_temperature}
                                </label>
                                <input
                                    id="llm-temperature"
                                    type="range"
                                    min="0"
                                    max="2"
                                    step="0.1"
                                    value={botSettings.llm_temperature}
                                    onChange={(e) => updateSetting('llm_temperature', parseFloat(e.target.value))}
                                    className="w-full"
                                    title="Temperature setting"
                                    aria-label="Temperature setting for LLM model"
                                />
                                <div className="flex justify-between text-xs text-gray-500 mt-1">
                                    <span>Focused</span>
                                    <span>Balanced</span>
                                    <span>Creative</span>
                                </div>
                            </div>

                            <div>
                                <label htmlFor="llm-max-tokens" className="block text-sm font-medium text-gray-700 mb-2">
                                    Max Tokens: {botSettings.llm_max_tokens}
                                </label>
                                <input
                                    id="llm-max-tokens"
                                    type="range"
                                    min="100"
                                    max="4000"
                                    step="100"
                                    value={botSettings.llm_max_tokens}
                                    onChange={(e) => updateSetting('llm_max_tokens', parseInt(e.target.value))}
                                    className="w-full"
                                    title="Maximum tokens setting"
                                    aria-label="Maximum tokens setting for LLM model"
                                />
                                <div className="flex justify-between text-xs text-gray-500 mt-1">
                                    <span>100</span>
                                    <span>2000</span>
                                    <span>4000</span>
                                </div>
                            </div>

                            <div>
                                <label htmlFor="llm-top-p" className="block text-sm font-medium text-gray-700 mb-2">
                                    Top P: {botSettings.llm_top_p}
                                </label>
                                <input
                                    id="llm-top-p"
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.1"
                                    value={botSettings.llm_top_p}
                                    onChange={(e) => updateSetting('llm_top_p', parseFloat(e.target.value))}
                                    className="w-full"
                                    title="Top P setting"
                                    aria-label="Top P setting for LLM model"
                                />
                            </div>

                            <div>
                                <label htmlFor="llm-frequency-penalty" className="block text-sm font-medium text-gray-700 mb-2">
                                    Frequency Penalty: {botSettings.llm_frequency_penalty}
                                </label>
                                <input
                                    id="llm-frequency-penalty"
                                    type="range"
                                    min="-2"
                                    max="2"
                                    step="0.1"
                                    value={botSettings.llm_frequency_penalty}
                                    onChange={(e) => updateSetting('llm_frequency_penalty', parseFloat(e.target.value))}
                                    className="w-full"
                                    title="Frequency penalty setting"
                                    aria-label="Frequency penalty setting for LLM model"
                                />
                            </div>

                            <div>
                                <label htmlFor="llm-presence-penalty" className="block text-sm font-medium text-gray-700 mb-2">
                                    Presence Penalty: {botSettings.llm_presence_penalty}
                                </label>
                                <input
                                    id="llm-presence-penalty"
                                    type="range"
                                    min="-2"
                                    max="2"
                                    step="0.1"
                                    value={botSettings.llm_presence_penalty}
                                    onChange={(e) => updateSetting('llm_presence_penalty', parseFloat(e.target.value))}
                                    className="w-full"
                                    title="Presence penalty setting"
                                    aria-label="Presence penalty setting for LLM model"
                                />
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'performance' && (
                    <div className="space-y-6">
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <Gauge className="w-5 h-5 text-green-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-green-900">Performance Tuning</h3>
                                    <p className="text-sm text-green-700 mt-1">
                                        Optimize bot performance, response times, and resource usage.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label htmlFor="max-concurrent-requests" className="block text-sm font-medium text-gray-700 mb-2">
                                    Max Concurrent Requests
                                </label>
                                <input
                                    id="max-concurrent-requests"
                                    type="number"
                                    min="1"
                                    max="100"
                                    value={botSettings.max_concurrent_requests}
                                    onChange={(e) => updateSetting('max_concurrent_requests', parseInt(e.target.value))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="10"
                                    aria-label="Maximum concurrent requests"
                                    title="Maximum number of simultaneous requests"
                                />
                                <p className="text-xs text-gray-500 mt-1">Maximum number of simultaneous requests</p>
                            </div>

                            <div>
                                <label htmlFor="request-timeout" className="block text-sm font-medium text-gray-700 mb-2">
                                    Request Timeout (seconds)
                                </label>
                                <input
                                    id="request-timeout"
                                    type="number"
                                    min="5"
                                    max="300"
                                    value={botSettings.request_timeout}
                                    onChange={(e) => updateSetting('request_timeout', parseInt(e.target.value))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="30"
                                    aria-label="Request timeout in seconds"
                                    title="Timeout for request processing"
                                />
                            </div>

                            <div>
                                <label htmlFor="rate-limit-minute" className="block text-sm font-medium text-gray-700 mb-2">
                                    Rate Limit per Minute
                                </label>
                                <input
                                    id="rate-limit-minute"
                                    type="number"
                                    min="1"
                                    max="1000"
                                    value={botSettings.rate_limit_per_minute}
                                    onChange={(e) => updateSetting('rate_limit_per_minute', parseInt(e.target.value))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="60"
                                    aria-label="Rate limit per minute"
                                    title="Maximum requests per minute"
                                />
                            </div>

                            <div>
                                <label htmlFor="rate-limit-hour" className="block text-sm font-medium text-gray-700 mb-2">
                                    Rate Limit per Hour
                                </label>
                                <input
                                    id="rate-limit-hour"
                                    type="number"
                                    min="10"
                                    max="10000"
                                    value={botSettings.rate_limit_per_hour}
                                    onChange={(e) => updateSetting('rate_limit_per_hour', parseInt(e.target.value))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="1000"
                                    aria-label="Rate limit per hour"
                                    title="Maximum requests per hour"
                                />
                            </div>

                            <div>
                                <label htmlFor="cache-ttl" className="block text-sm font-medium text-gray-700 mb-2">
                                    Cache TTL (seconds)
                                </label>
                                <input
                                    id="cache-ttl"
                                    type="number"
                                    min="60"
                                    max="86400"
                                    value={botSettings.cache_ttl}
                                    onChange={(e) => updateSetting('cache_ttl', parseInt(e.target.value))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="300"
                                    aria-label="Cache TTL in seconds"
                                    title="Cache time-to-live in seconds"
                                />
                            </div>
                        </div>

                        <div className="space-y-4">
                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={botSettings.cache_enabled}
                                    onChange={(e) => updateSetting('cache_enabled', e.target.checked)}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Enable Caching</span>
                                    <p className="text-sm text-gray-500">Cache responses to improve performance</p>
                                </div>
                            </label>
                        </div>
                    </div>
                )}

                {activeTab === 'security' && (
                    <div className="space-y-6">
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <Shield className="w-5 h-5 text-red-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-red-900">Security & Privacy</h3>
                                    <p className="text-sm text-red-700 mt-1">
                                        Configure data protection, access controls, and security settings.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label htmlFor="data-retention" className="block text-sm font-medium text-gray-700 mb-2">
                                    Data Retention (days)
                                </label>
                                <select
                                    id="data-retention"
                                    value={botSettings.data_retention_days}
                                    onChange={(e) => updateSetting('data_retention_days', parseInt(e.target.value))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                >
                                    <option value={7}>7 days</option>
                                    <option value={30}>30 days</option>
                                    <option value={90}>90 days</option>
                                    <option value={365}>1 year</option>
                                    <option value={-1}>Never delete</option>
                                </select>
                            </div>

                            <div>
                                <label htmlFor="log-level" className="block text-sm font-medium text-gray-700 mb-2">
                                    Log Level
                                </label>
                                <select
                                    id="log-level"
                                    value={botSettings.log_level}
                                    onChange={(e) => updateSetting('log_level', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                >
                                    <option value="debug">Debug</option>
                                    <option value="info">Info</option>
                                    <option value="warn">Warning</option>
                                    <option value="error">Error</option>
                                </select>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={botSettings.allow_public_access}
                                    onChange={(e) => updateSetting('allow_public_access', e.target.checked)}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Allow Public Access</span>
                                    <p className="text-sm text-gray-500">Enable public access to this bot</p>
                                </div>
                            </label>

                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={botSettings.enable_encryption}
                                    onChange={(e) => updateSetting('enable_encryption', e.target.checked)}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Enable Encryption</span>
                                    <p className="text-sm text-gray-500">Encrypt sensitive data and communications</p>
                                </div>
                            </label>

                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={botSettings.enable_analytics}
                                    onChange={(e) => updateSetting('enable_analytics', e.target.checked)}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Enable Analytics</span>
                                    <p className="text-sm text-gray-500">Collect usage analytics and performance metrics</p>
                                </div>
                            </label>

                            <label className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    checked={botSettings.enable_monitoring}
                                    onChange={(e) => updateSetting('enable_monitoring', e.target.checked)}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Enable Monitoring</span>
                                    <p className="text-sm text-gray-500">Real-time monitoring and alerting</p>
                                </div>
                            </label>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Alert Email
                            </label>
                            <input
                                type="email"
                                value={botSettings.alert_email || ''}
                                onChange={(e) => updateSetting('alert_email', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                placeholder="alerts@example.com"
                            />
                            <p className="text-xs text-gray-500 mt-1">Email for system alerts and notifications</p>
                        </div>
                    </div>
                )}

                {activeTab === 'integrations' && (
                    <div className="space-y-6">
                        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <Globe className="w-5 h-5 text-gray-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-gray-900">Integrations</h3>
                                    <p className="text-sm text-gray-700 mt-1">
                                        Configure sandboxed execution and tool access for this agent.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="border border-amber-200 bg-amber-50 rounded-lg p-4">
                            <div className="flex items-center justify-between gap-4">
                                <div>
                                    <h3 className="font-medium text-amber-900">Agentic Thinking (Beta / Experimental)</h3>
                                    <p className="text-sm text-amber-700 mt-1">
                                        Enables internal dialogue planning before execution. Available on Pro and Enterprise plans.
                                    </p>
                                </div>
                                <label className="flex items-center space-x-2">
                                    <input
                                        type="checkbox"
                                        checked={botSettings.agentic_thinking_enabled}
                                        onChange={(e) => updateSetting('agentic_thinking_enabled', e.target.checked)}
                                        className="rounded border-amber-300 text-amber-600 focus:ring-amber-500"
                                    />
                                    <span className="text-sm text-amber-900">Enable</span>
                                </label>
                            </div>
                        </div>

                        {virtualComputerLoading && (
                            <div className="text-sm text-gray-500">Loading virtual computer settings...</div>
                        )}

                        {!virtualComputerLoading && !virtualComputer && (
                            <div className="text-sm text-gray-500">Virtual computer configuration is unavailable.</div>
                        )}

                        {virtualComputer && (
                            <div className="border border-gray-200 rounded-lg p-4 space-y-4">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <Cpu className="w-5 h-5 text-blue-600" />
                                        <div>
                                            <h3 className="font-medium text-gray-900">Virtual Computer</h3>
                                            <p className="text-sm text-gray-500">Run Python in an isolated E2B sandbox.</p>
                                        </div>
                                    </div>
                                    <label className="flex items-center space-x-2">
                                        <input
                                            type="checkbox"
                                            checked={virtualComputer.enabled}
                                            onChange={(e) => updateVirtualComputerField('enabled', e.target.checked)}
                                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                        />
                                        <span className="text-sm text-gray-700">Enabled</span>
                                    </label>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label htmlFor="vc-provider" className="block text-sm font-medium text-gray-700 mb-1">Provider</label>
                                        <select
                                            id="vc-provider"
                                            value={virtualComputer.provider}
                                            onChange={(e) => updateVirtualComputerField('provider', e.target.value)}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                            aria-label="Virtual computer provider"
                                            title="Virtual computer provider"
                                        >
                                            <option value="e2b">E2B</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label htmlFor="vc-idle-timeout" className="block text-sm font-medium text-gray-700 mb-1">Idle Timeout (seconds)</label>
                                        <input
                                            id="vc-idle-timeout"
                                            type="number"
                                            min={30}
                                            max={3600}
                                            value={virtualComputer.idle_timeout_seconds}
                                            onChange={(e) => updateVirtualComputerField('idle_timeout_seconds', Number(e.target.value))}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                            placeholder="300"
                                            aria-label="Idle timeout in seconds"
                                            title="Idle timeout in seconds"
                                        />
                                    </div>
                                    <div>
                                        <label htmlFor="vc-max-runtime" className="block text-sm font-medium text-gray-700 mb-1">Max Runtime (seconds)</label>
                                        <input
                                            id="vc-max-runtime"
                                            type="number"
                                            min={60}
                                            max={7200}
                                            value={virtualComputer.max_runtime_seconds}
                                            onChange={(e) => updateVirtualComputerField('max_runtime_seconds', Number(e.target.value))}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                            placeholder="3600"
                                            aria-label="Max runtime in seconds"
                                            title="Max runtime in seconds"
                                        />
                                    </div>
                                    <div>
                                        <label htmlFor="vc-memory" className="block text-sm font-medium text-gray-700 mb-1">Memory (MB)</label>
                                        <input
                                            id="vc-memory"
                                            type="number"
                                            min={128}
                                            max={8192}
                                            value={virtualComputer.memory_mb}
                                            onChange={(e) => updateVirtualComputerField('memory_mb', Number(e.target.value))}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                            placeholder="1024"
                                            aria-label="Memory in MB"
                                            title="Memory in MB"
                                        />
                                    </div>
                                    <div>
                                        <label htmlFor="vc-cpu-cores" className="block text-sm font-medium text-gray-700 mb-1">CPU Cores</label>
                                        <input
                                            id="vc-cpu-cores"
                                            type="number"
                                            min={0.25}
                                            max={8}
                                            step={0.25}
                                            value={virtualComputer.cpu_cores}
                                            onChange={(e) => updateVirtualComputerField('cpu_cores', Number(e.target.value))}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                            placeholder="1"
                                            aria-label="CPU cores"
                                            title="CPU cores"
                                        />
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <label className="flex items-center space-x-3">
                                        <input
                                            type="checkbox"
                                            checked={virtualComputer.allow_network}
                                            onChange={(e) => updateVirtualComputerField('allow_network', e.target.checked)}
                                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                        />
                                        <div>
                                            <span className="font-medium text-gray-900">Allow Network Access</span>
                                            <p className="text-sm text-gray-500">Permit outbound network calls in the sandbox.</p>
                                        </div>
                                    </label>
                                    <label className="flex items-center space-x-3">
                                        <input
                                            type="checkbox"
                                            checked={virtualComputer.mcp_enabled}
                                            onChange={(e) => updateVirtualComputerField('mcp_enabled', e.target.checked)}
                                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                        />
                                        <div>
                                            <span className="font-medium text-gray-900">MCP Tools Enabled</span>
                                            <p className="text-sm text-gray-500">Expose MCP tools through the sandbox proxy.</p>
                                        </div>
                                    </label>
                                </div>

                                {virtualComputer.mcp_enabled && (
                                    <div className="space-y-3">
                                        <div className="border border-gray-200 rounded-lg p-3">
                                            <div className="flex items-center justify-between mb-2">
                                                <div>
                                                    <h4 className="text-sm font-medium text-gray-900">Server Groups</h4>
                                                    <p className="text-xs text-gray-500">Manage access by MCP groups or fine-tune server selection below.</p>
                                                </div>
                                            </div>
                                            <div className="space-y-2 max-h-56 overflow-auto">
                                                {groupInfos.length > 0 ? (
                                                    groupInfos.map(groupInfo => {
                                                        const memberServerIds = (groupInfo.members || []).map(member => member.server_id);
                                                        const activeMemberIds = memberServerIds.filter(id => allServerIds.includes(id));
                                                        const groupSelected = activeMemberIds.length > 0 && activeMemberIds.every(id => effectiveSelectedServerIds.includes(id));
                                                        return (
                                                            <div key={groupInfo.group.id} className="rounded-md border border-gray-200 p-2">
                                                                <label className="flex items-center space-x-2 text-sm font-medium">
                                                                    <input
                                                                        type="checkbox"
                                                                        checked={groupSelected}
                                                                        onChange={() => toggleMcpGroup(activeMemberIds)}
                                                                        disabled={activeMemberIds.length === 0}
                                                                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                                                    />
                                                                    <span className="text-gray-800">{groupInfo.group.name}</span>
                                                                    <span className="text-xs text-gray-500">({groupInfo.active_members}/{groupInfo.total_members})</span>
                                                                </label>
                                                                {groupInfo.group.description && (
                                                                    <div className="text-xs text-gray-500 ml-6">
                                                                        {groupInfo.group.description}
                                                                    </div>
                                                                )}
                                                                <div className="mt-2 space-y-1 ml-6">
                                                                    {groupInfo.members.length > 0 ? (
                                                                        groupInfo.members.map(member => (
                                                                            <label key={`${groupInfo.group.id}-${member.server_id}`} className="flex items-center space-x-2 text-xs">
                                                                                <input
                                                                                    type="checkbox"
                                                                                    checked={effectiveSelectedServerIds.includes(member.server_id)}
                                                                                    onChange={() => toggleMcpServer(member.server_id)}
                                                                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                                                                />
                                                                                <span className="text-gray-800">{member.name}</span>
                                                                                {member.server_active === false && (
                                                                                    <span className="text-xs text-gray-400">(inactive)</span>
                                                                                )}
                                                                            </label>
                                                                        ))
                                                                    ) : (
                                                                        <div className="text-xs text-gray-500">No servers assigned to this group.</div>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        );
                                                    })
                                                ) : (
                                                    <div className="text-xs text-gray-500">No server groups found.</div>
                                                )}
                                            </div>
                                        </div>

                                        <div className="border border-gray-200 rounded-lg p-3">
                                            <div className="flex items-center justify-between mb-2">
                                                <div>
                                                    <h4 className="text-sm font-medium text-gray-900">Allowed MCP Servers</h4>
                                                    <p className="text-xs text-gray-500">Select the MCP servers this sandbox can access. Leave empty to allow all.</p>
                                                </div>
                                                {(virtualComputer.mcp_server_ids || []).length === 0 && (
                                                    <span className="text-xs text-gray-500">All active servers</span>
                                                )}
                                            </div>
                                            <div className="space-y-2 max-h-48 overflow-auto">
                                                {ungroupedServers.map(server => (
                                                    <label key={server.server_id} className="flex items-center space-x-2 text-sm">
                                                        <input
                                                            type="checkbox"
                                                            checked={effectiveSelectedServerIds.includes(server.server_id)}
                                                            onChange={() => toggleMcpServer(server.server_id)}
                                                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                                        />
                                                        <span className="text-gray-800">{server.name}</span>
                                                        {!server.is_active && (
                                                            <span className="text-xs text-gray-400">(inactive)</span>
                                                        )}
                                                    </label>
                                                ))}
                                                {(!mcpServers || mcpServers.length === 0) && (
                                                    <div className="text-xs text-gray-500">No MCP servers found.</div>
                                                )}
                                                {mcpServers && mcpServers.length > 0 && ungroupedServers.length === 0 && (
                                                    <div className="text-xs text-gray-500">All servers are assigned to groups.</div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                )}

                                <div className="flex flex-wrap gap-3">
                                    <button
                                        onClick={saveVirtualComputer}
                                        disabled={virtualComputerUpdating}
                                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                                    >
                                        {virtualComputerUpdating ? 'Saving...' : 'Save Virtual Computer'}
                                    </button>
                                    <button
                                        onClick={testVirtualComputer}
                                        className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                                    >
                                        Test Sandbox
                                    </button>
                                </div>

                                {virtualComputerTestResult && (
                                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm text-gray-700 space-y-2">
                                        {virtualComputerTestResult.error && (
                                            <div className="text-red-600">{virtualComputerTestResult.error}</div>
                                        )}
                                        {virtualComputerTestResult.stdout && (
                                            <div>
                                                <div className="text-xs font-medium uppercase text-gray-500">stdout</div>
                                                <pre className="whitespace-pre-wrap">{virtualComputerTestResult.stdout}</pre>
                                            </div>
                                        )}
                                        {virtualComputerTestResult.stderr && (
                                            <div>
                                                <div className="text-xs font-medium uppercase text-gray-500">stderr</div>
                                                <pre className="whitespace-pre-wrap">{virtualComputerTestResult.stderr}</pre>
                                            </div>
                                        )}
                                        {virtualComputerTestResult.duration_ms !== undefined && (
                                            <div className="text-xs text-gray-500">Duration: {virtualComputerTestResult.duration_ms} ms</div>
                                        )}
                                        {virtualComputerTestResult.exit_code !== undefined && (
                                            <div className="text-xs text-gray-500">Exit code: {virtualComputerTestResult.exit_code}</div>
                                        )}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'voice' && (
                    <VoiceConfigurationPanel agentId={agentId} />
                )}

                {activeTab === 'env' && (
                    <div className="space-y-6">
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <Key className="w-5 h-5 text-yellow-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-yellow-900">Environment Variables</h3>
                                    <p className="text-sm text-yellow-700 mt-1">
                                        Manage environment variables and secrets for your bot.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="border border-gray-200 rounded-lg overflow-hidden">
                            <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
                                <div className="flex items-center justify-between">
                                    <h3 className="font-medium">Environment Variables</h3>
                                    <button
                                        onClick={() => setShowAddEnvVar(true)}
                                        className="flex items-center space-x-2 px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                                    >
                                        <Plus className="w-4 h-4" />
                                        <span>Add Variable</span>
                                    </button>
                                </div>
                            </div>
                            <div className="divide-y divide-gray-200">
                                {Object.entries(botSettings.environment_variables).map(([key, value]) => (
                                    <div key={key} className="px-4 py-3 flex items-center justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center space-x-3">
                                                <span className="font-medium text-sm">{key}</span>
                                                <div className="flex-1 max-w-md">
                                                    <input
                                                        id={`env-var-${key}`}
                                                        type={showSecretValues[key] ? 'text' : 'password'}
                                                        value={value}
                                                        readOnly
                                                        className="w-full px-2 py-1 bg-gray-100 border border-gray-300 rounded text-sm"
                                                        placeholder="Value"
                                                        aria-label={`Environment variable value for ${key}`}
                                                        title={`Value for environment variable ${key}`}
                                                    />
                                                </div>
                                                <button
                                                    onClick={() => toggleSecretValue(key)}
                                                    className="p-1 text-gray-400 hover:text-gray-600"
                                                    title={showSecretValues[key] ? 'Hide value' : 'Show value'}
                                                >
                                                    {showSecretValues[key] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                                </button>
                                                <button
                                                    onClick={() => removeEnvironmentVariable(key)}
                                                    className="p-1 text-red-400 hover:text-red-600"
                                                    title="Remove variable"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                                {Object.keys(botSettings.environment_variables).length === 0 && (
                                    <div className="px-4 py-8 text-center text-gray-500">
                                        No environment variables configured
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Add Environment Variable Modal */}
                        {showAddEnvVar && (
                            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                                <div className="bg-white rounded-lg p-6 w-full max-w-md">
                                    <h3 className="text-lg font-medium mb-4">Add Environment Variable</h3>
                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Key
                                            </label>
                                            <input
                                                type="text"
                                                value={newEnvVar.key}
                                                onChange={(e) => setNewEnvVar(prev => ({ ...prev, key: e.target.value }))}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                                placeholder="VARIABLE_NAME"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Value
                                            </label>
                                            <input
                                                type="text"
                                                value={newEnvVar.value}
                                                onChange={(e) => setNewEnvVar(prev => ({ ...prev, value: e.target.value }))}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                                placeholder="variable value"
                                            />
                                        </div>
                                        <label className="flex items-center space-x-2">
                                            <input
                                                type="checkbox"
                                                checked={newEnvVar.isSecret}
                                                onChange={(e) => setNewEnvVar(prev => ({ ...prev, isSecret: e.target.checked }))}
                                                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                            />
                                            <span className="text-sm text-gray-700">This is a secret value</span>
                                        </label>
                                    </div>
                                    <div className="flex space-x-3 mt-6">
                                        <button
                                            onClick={() => setShowAddEnvVar(false)}
                                            className="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                                        >
                                            Cancel
                                        </button>
                                        <button
                                            onClick={addEnvironmentVariable}
                                            disabled={!newEnvVar.key}
                                            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                                        >
                                            Add Variable
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'advanced' && (
                    <div className="space-y-6">
                        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <Zap className="w-5 h-5 text-gray-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-gray-900">Advanced Configuration</h3>
                                    <p className="text-sm text-gray-700 mt-1">
                                        Expert-level settings for fine-tuning bot behavior and performance.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Error Handling Prompt
                            </label>
                            <textarea
                                value={botSettings.custom_prompts.error_handling_prompt}
                                onChange={(e) => updateSetting('custom_prompts', {
                                    ...botSettings.custom_prompts,
                                    error_handling_prompt: e.target.value
                                })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                                rows={4}
                                placeholder="Instructions for handling errors and edge cases..."
                            />
                        </div>

                        <div className="border border-gray-200 rounded-lg p-4">
                            <h3 className="font-medium mb-4">Configuration Export/Import</h3>
                            <div className="flex space-x-3">
                                <button
                                    onClick={() => {
                                        const dataStr = JSON.stringify(botSettings, null, 2);
                                        const dataBlob = new Blob([dataStr], { type: 'application/json' });
                                        const url = URL.createObjectURL(dataBlob);
                                        const link = document.createElement('a');
                                        link.href = url;
                                        link.download = `bot-settings-${Date.now()}.json`;
                                        link.click();
                                        URL.revokeObjectURL(url);
                                    }}
                                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                                >
                                    <Download className="w-4 h-4" />
                                    <span>Export Settings</span>
                                </button>
                                <label className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors cursor-pointer">
                                    <Upload className="w-4 h-4" />
                                    <span>Import Settings</span>
                                    <input
                                        type="file"
                                        accept=".json"
                                        className="hidden"
                                        onChange={(e) => {
                                            const file = e.target.files?.[0];
                                            if (file) {
                                                const reader = new FileReader();
                                                reader.onload = (event) => {
                                                    try {
                                                        const settings = JSON.parse(event.target?.result as string);
                                                        setBotSettings({ ...botSettings, ...settings });
                                                    } catch (error) {
                                                        alert('Invalid settings file');
                                                    }
                                                };
                                                reader.readAsText(file);
                                            }
                                        }}
                                    />
                                </label>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default BotSettingsPanel;
