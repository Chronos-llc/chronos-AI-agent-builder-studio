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
    X
} from 'lucide-react';

interface BotSettings {
    // Basic Settings
    name: string;
    description: string;
    avatar_url?: string;

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

    // Integration Settings
    webhook_url?: string;
    api_keys: Record<string, string>;
    database_config: Record<string, any>;

    // Environment Variables
    environment_variables: Record<string, string>;

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
}

interface EnvironmentVariable {
    key: string;
    value: string;
    description?: string;
    isSecret: boolean;
}

interface Integration {
    name: string;
    type: string;
    config: Record<string, any>;
    enabled: boolean;
}

const BotSettingsPanel: React.FC<{ agentId: number }> = ({ agentId }) => {
    const [activeTab, setActiveTab] = useState<'basic' | 'llm' | 'performance' | 'security' | 'integrations' | 'env' | 'advanced'>('basic');
    const [showSecretValues, setShowSecretValues] = useState<Record<string, boolean>>({});
    const [newEnvVar, setNewEnvVar] = useState<EnvironmentVariable>({ key: '', value: '', isSecret: false });
    const [showAddEnvVar, setShowAddEnvVar] = useState(false);

    const queryClient = useQueryClient();

    // Fetch current settings
    const { data: settings, isLoading } = useQuery({
        queryKey: ['bot-settings', agentId],
        queryFn: async () => {
            const response = await fetch(`/api/agents/${agentId}/settings`);
            if (!response.ok) throw new Error('Failed to fetch settings');
            return response.json();
        }
    });

    // Save settings mutation
    const saveSettingsMutation = useMutation({
        mutationFn: async (settings: BotSettings) => {
            const response = await fetch(`/api/agents/${agentId}/settings`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
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
        enable_monitoring: true
    });

    useEffect(() => {
        if (settings) {
            setBotSettings({ ...botSettings, ...settings });
        }
    }, [settings]);

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

    const getLogLevelColor = (level: string) => {
        switch (level) {
            case 'debug': return 'text-blue-600';
            case 'info': return 'text-green-600';
            case 'warn': return 'text-yellow-600';
            case 'error': return 'text-red-600';
            default: return 'text-gray-600';
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
            <div className="border-b border-gray-200 pb-4 mb-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <Settings className="w-6 h-6 text-blue-600" />
                        <h2 className="text-xl font-semibold text-gray-900">Bot Settings</h2>
                    </div>
                    <button
                        onClick={() => saveSettingsMutation.mutate(botSettings)}
                        disabled={saveSettingsMutation.isPending}
                        className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
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

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Model
                            </label>
                            <select
                                value={botSettings.llm_model}
                                onChange={(e) => updateSetting('llm_model', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option value="gpt-4">GPT-4</option>
                                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                <option value="claude-3">Claude 3</option>
                                <option value="gemini-pro">Gemini Pro</option>
                            </select>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Temperature: {botSettings.llm_temperature}
                                </label>
                                <input
                                    type="range"
                                    min="0"
                                    max="2"
                                    step="0.1"
                                    value={botSettings.llm_temperature}
                                    onChange={(e) => updateSetting('llm_temperature', parseFloat(e.target.value))}
                                    className="w-full"
                                />
                                <div className="flex justify-between text-xs text-gray-500 mt-1">
                                    <span>Focused</span>
                                    <span>Balanced</span>
                                    <span>Creative</span>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Max Tokens: {botSettings.llm_max_tokens}
                                </label>
                                <input
                                    type="range"
                                    min="100"
                                    max="4000"
                                    step="100"
                                    value={botSettings.llm_max_tokens}
                                    onChange={(e) => updateSetting('llm_max_tokens', parseInt(e.target.value))}
                                    className="w-full"
                                />
                                <div className="flex justify-between text-xs text-gray-500 mt-1">
                                    <span>100</span>
                                    <span>2000</span>
                                    <span>4000</span>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Top P: {botSettings.llm_top_p}
                                </label>
                                <input
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.1"
                                    value={botSettings.llm_top_p}
                                    onChange={(e) => updateSetting('llm_top_p', parseFloat(e.target.value))}
                                    className="w-full"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Frequency Penalty: {botSettings.llm_frequency_penalty}
                                </label>
                                <input
                                    type="range"
                                    min="-2"
                                    max="2"
                                    step="0.1"
                                    value={botSettings.llm_frequency_penalty}
                                    onChange={(e) => updateSetting('llm_frequency_penalty', parseFloat(e.target.value))}
                                    className="w-full"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Presence Penalty: {botSettings.llm_presence_penalty}
                                </label>
                                <input
                                    type="range"
                                    min="-2"
                                    max="2"
                                    step="0.1"
                                    value={botSettings.llm_presence_penalty}
                                    onChange={(e) => updateSetting('llm_presence_penalty', parseFloat(e.target.value))}
                                    className="w-full"
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
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Max Concurrent Requests
                                </label>
                                <input
                                    type="number"
                                    min="1"
                                    max="100"
                                    value={botSettings.max_concurrent_requests}
                                    onChange={(e) => updateSetting('max_concurrent_requests', parseInt(e.target.value))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                />
                                <p className="text-xs text-gray-500 mt-1">Maximum number of simultaneous requests</p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Request Timeout (seconds)
                                </label>
                                <input
                                    type="number"
                                    min="5"
                                    max="300"
                                    value={botSettings.request_timeout}
                                    onChange={(e) => updateSetting('request_timeout', parseInt(e.target.value))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Rate Limit per Minute
                                </label>
                                <input
                                    type="number"
                                    min="1"
                                    max="1000"
                                    value={botSettings.rate_limit_per_minute}
                                    onChange={(e) => updateSetting('rate_limit_per_minute', parseInt(e.target.value))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Rate Limit per Hour
                                </label>
                                <input
                                    type="number"
                                    min="10"
                                    max="10000"
                                    value={botSettings.rate_limit_per_hour}
                                    onChange={(e) => updateSetting('rate_limit_per_hour', parseInt(e.target.value))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Cache TTL (seconds)
                                </label>
                                <input
                                    type="number"
                                    min="60"
                                    max="86400"
                                    value={botSettings.cache_ttl}
                                    onChange={(e) => updateSetting('cache_ttl', parseInt(e.target.value))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Data Retention (days)
                                </label>
                                <select
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
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Log Level
                                </label>
                                <select
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
                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <Globe className="w-5 h-5 text-purple-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-purple-900">External Integrations</h3>
                                    <p className="text-sm text-purple-700 mt-1">
                                        Configure webhooks, databases, and third-party service integrations.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Webhook URL
                            </label>
                            <input
                                type="url"
                                value={botSettings.webhook_url || ''}
                                onChange={(e) => updateSetting('webhook_url', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                placeholder="https://your-webhook-url.com/webhook"
                            />
                            <p className="text-xs text-gray-500 mt-1">URL to receive bot events and notifications</p>
                        </div>

                        <div className="border border-gray-200 rounded-lg p-4">
                            <h3 className="font-medium mb-4">Database Configuration</h3>
                            <textarea
                                value={JSON.stringify(botSettings.database_config, null, 2)}
                                onChange={(e) => {
                                    try {
                                        updateSetting('database_config', JSON.parse(e.target.value));
                                    } catch (error) {
                                        // Keep previous value if invalid JSON
                                    }
                                }}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                                rows={6}
                                placeholder='{\n  "host": "localhost",\n  "port": 5432,\n  "database": "myapp"\n}'
                            />
                        </div>

                        <div className="border border-gray-200 rounded-lg p-4">
                            <h3 className="font-medium mb-4">API Keys</h3>
                            <p className="text-sm text-gray-600 mb-4">Configure external service API keys</p>
                            {Object.entries(botSettings.api_keys).map(([service, key]) => (
                                <div key={service} className="flex items-center space-x-2 mb-2">
                                    <span className="text-sm font-medium w-24">{service}:</span>
                                    <input
                                        type="password"
                                        value={key}
                                        onChange={(e) => updateSetting('api_keys', {
                                            ...botSettings.api_keys,
                                            [service]: e.target.value
                                        })}
                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>
                            ))}
                            <button className="text-blue-600 text-sm hover:text-blue-700">
                                + Add API Key
                            </button>
                        </div>
                    </div>
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
                                                        type={showSecretValues[key] ? 'text' : 'password'}
                                                        value={value}
                                                        readOnly
                                                        className="w-full px-2 py-1 bg-gray-100 border border-gray-300 rounded text-sm"
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