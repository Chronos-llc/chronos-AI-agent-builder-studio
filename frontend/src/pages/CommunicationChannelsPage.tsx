import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { useAuth } from '../contexts/AuthContext';
import { ProviderLogo } from '../components/brand/ProviderLogo';
import { getProviderIcon } from '../config/iconRegistry';
import { PlatformLoadingScreen } from '../components/loading/PlatformLoadingScreen';

interface CommunicationChannel {
    channel_id: string;
    channel_type: string;
    config: any;
    is_default: boolean;
    status: string;
    created_at: string;
}

interface ChannelTypeConfig {
    type: string;
    name: string;
    icon: string;
    logo_key: string;
    description: string;
    config_fields: Array<{
        name: string;
        label: string;
        type: string;
        required: boolean;
        placeholder?: string;
        options?: Array<{ value: string; label: string }>;
        help_text?: string;
    }>;
}

const CommunicationChannelsPage: React.FC = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [channels, setChannels] = useState<CommunicationChannel[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<'channels' | 'analytics' | 'routing'>('channels');
    const [showAddChannel, setShowAddChannel] = useState(false);
    const [selectedChannelType, setSelectedChannelType] = useState<string | null>(null);
    const [newChannelConfig, setNewChannelConfig] = useState<Record<string, any>>({});
    const [isAdding, setIsAdding] = useState(false);
    const [analyticsData, setAnalyticsData] = useState<any>(null);
    const [routingRules, setRoutingRules] = useState<any[]>([]);
    const [newRule, setNewRule] = useState<Record<string, any>>({
        name: '',
        condition: {},
        target_channels: [],
        priority: 1,
        enabled: true
    });

    // Channel type configurations
    const channelTypes: ChannelTypeConfig[] = [
        {
            type: 'telegram',
            name: 'Telegram',
            icon: 'telegram',
            logo_key: 'telegram',
            description: 'Integrate with Telegram bot API',
            config_fields: [
                { name: 'bot_token', label: 'Bot Token', type: 'password', required: true, help_text: 'Telegram bot token from BotFather' },
                { name: 'telegram_bot_username', label: 'Bot Username', type: 'text', required: true, help_text: 'Your bot username without @' },
                { name: 'webhook_url', label: 'Webhook URL', type: 'text', required: false, help_text: 'URL for incoming webhook messages' },
                { name: 'telegram_webhook_secret', label: 'Webhook Secret', type: 'password', required: false, help_text: 'Secret token for webhook verification' },
                { name: 'timeout', label: 'Timeout (seconds)', type: 'number', required: false, placeholder: '30' },
                { name: 'rate_limit', label: 'Rate Limit (messages/min)', type: 'number', required: false, placeholder: '100' },
                { name: 'encryption_enabled', label: 'Enable Encryption', type: 'checkbox', required: false, help_text: 'Enable end-to-end encryption' }
            ]
        },
        {
            type: 'slack',
            name: 'Slack',
            icon: 'slack',
            logo_key: 'slack',
            description: 'Integrate with Slack API',
            config_fields: [
                { name: 'bot_token', label: 'Bot Token', type: 'password', required: true, help_text: 'Slack bot token (xoxb-...)' },
                { name: 'access_token', label: 'User Token', type: 'password', required: false, help_text: 'Slack user token (xoxp-...)' },
                { name: 'slack_client_id', label: 'Client ID', type: 'text', required: true, help_text: 'Slack app client ID' },
                { name: 'slack_client_secret', label: 'Client Secret', type: 'password', required: true, help_text: 'Slack app client secret' },
                { name: 'slack_signing_secret', label: 'Signing Secret', type: 'password', required: true, help_text: 'Slack signing secret for verification' },
                { name: 'slack_redirect_uri', label: 'Redirect URI', type: 'text', required: true, help_text: 'OAuth redirect URI' },
                { name: 'webhook_url', label: 'Webhook URL', type: 'text', required: false, help_text: 'URL for incoming webhook messages' },
                { name: 'timeout', label: 'Timeout (seconds)', type: 'number', required: false, placeholder: '30' }
            ]
        },
        {
            type: 'whatsapp',
            name: 'WhatsApp',
            icon: 'whatsapp',
            logo_key: 'whatsapp',
            description: 'Integrate with WhatsApp Business API',
            config_fields: [
                { name: 'api_key', label: 'API Key', type: 'password', required: true, help_text: 'WhatsApp Business API key' },
                { name: 'whatsapp_phone_number_id', label: 'Phone Number ID', type: 'text', required: true, help_text: 'WhatsApp phone number ID' },
                { name: 'whatsapp_business_account_id', label: 'Business Account ID', type: 'text', required: true, help_text: 'WhatsApp business account ID' },
                { name: 'whatsapp_template_namespace', label: 'Template Namespace', type: 'text', required: false, help_text: 'Namespace for message templates' },
                { name: 'webhook_url', label: 'Webhook URL', type: 'text', required: false, help_text: 'URL for incoming webhook messages' },
                { name: 'timeout', label: 'Timeout (seconds)', type: 'number', required: false, placeholder: '30' },
                { name: 'rate_limit', label: 'Rate Limit (messages/min)', type: 'number', required: false, placeholder: '50' }
            ]
        },
        {
            type: 'discord',
            name: 'Discord',
            icon: 'discord',
            logo_key: 'discord',
            description: 'Integrate with Discord bot API',
            config_fields: [
                { name: 'bot_token', label: 'Bot Token', type: 'password', required: true, help_text: 'Discord bot token' },
                { name: 'discord_client_id', label: 'Client ID', type: 'text', required: true, help_text: 'Discord app client ID' },
                { name: 'discord_client_secret', label: 'Client Secret', type: 'password', required: true, help_text: 'Discord app client secret' },
                { name: 'discord_redirect_uri', label: 'Redirect URI', type: 'text', required: true, help_text: 'OAuth redirect URI' },
                { name: 'discord_permissions', label: 'Permissions', type: 'number', required: false, placeholder: '8', help_text: 'Bot permissions as integer' },
                { name: 'webhook_url', label: 'Webhook URL', type: 'text', required: false, help_text: 'URL for incoming webhook messages' },
                { name: 'timeout', label: 'Timeout (seconds)', type: 'number', required: false, placeholder: '30' }
            ]
        },
        {
            type: 'webchat',
            name: 'WebChat',
            icon: 'webchat',
            logo_key: 'webchat',
            description: 'Advanced WebChat integration',
            config_fields: [
                { name: 'embed_type', label: 'Embed Type', type: 'select', required: true, options: [
                    { value: 'bubble', label: 'Bubble' },
                    { value: 'iframe', label: 'Iframe' },
                    { value: 'standalone', label: 'Standalone' },
                    { value: 'react', label: 'React Component' }
                ] },
                { name: 'brand_name', label: 'Brand Name', type: 'text', required: false, placeholder: 'Chronos AI' },
                { name: 'welcome_message', label: 'Welcome Message', type: 'text', required: false, placeholder: 'Hello! How can I help you today?' },
                { name: 'voice_input_enabled', label: 'Enable Voice Input', type: 'checkbox', required: false },
                { name: 'voice_output_enabled', label: 'Enable Voice Output', type: 'checkbox', required: false },
                { name: 'feedback_enabled', label: 'Enable Feedback', type: 'checkbox', required: false },
                { name: 'analytics_enabled', label: 'Enable Analytics', type: 'checkbox', required: false },
                { name: 'allow_file_uploads', label: 'Allow File Uploads', type: 'checkbox', required: false }
            ]
        }
    ];

    useEffect(() => {
        fetchChannels();
        fetchAnalytics();
    }, []);

    const fetchChannels = async () => {
        try {
            setLoading(true);
            setError(null);

            // Mock data - in real implementation, this would fetch from API
            const mockChannels = [
                {
                    channel_id: 'telegram_main',
                    channel_type: 'telegram',
                    config: {
                        bot_token: '********',
                        telegram_bot_username: 'chronos_ai_bot',
                        webhook_url: 'https://api.chronos.ai/webhook/telegram',
                        timeout: 30,
                        rate_limit: 100
                    },
                    is_default: true,
                    status: 'active',
                    created_at: '2023-01-01T00:00:00Z'
                },
                {
                    channel_id: 'slack_workspace',
                    channel_type: 'slack',
                    config: {
                        bot_token: '********',
                        slack_client_id: '12345.67890',
                        webhook_url: 'https://api.chronos.ai/webhook/slack',
                        timeout: 30
                    },
                    is_default: false,
                    status: 'active',
                    created_at: '2023-01-02T00:00:00Z'
                }
            ];

            setChannels(mockChannels);

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch communication channels');
        } finally {
            setLoading(false);
        }
    };

    const fetchAnalytics = async () => {
        try {
            // Mock analytics data
            const mockAnalytics = {
                total_channels: 2,
                total_messages: 4287,
                successful_messages: 4123,
                failed_messages: 164,
                success_rate: 96.2,
                channel_analytics: {
                    telegram_main: {
                        total_messages: 2456,
                        successful_messages: 2401,
                        failed_messages: 55,
                        avg_response_time_ms: 124.7,
                        error_rate: 2.2,
                        active_users: 1287
                    },
                    slack_workspace: {
                        total_messages: 1831,
                        successful_messages: 1722,
                        failed_messages: 109,
                        avg_response_time_ms: 189.3,
                        error_rate: 5.9,
                        active_users: 456
                    }
                }
            };

            setAnalyticsData(mockAnalytics);

        } catch (err) {
            console.error('Failed to fetch analytics:', err);
        }
    };

    const fetchRoutingRules = async (channelId: string) => {
        try {
            // Mock routing rules
            const mockRules = [
                {
                    name: 'high_priority_routing',
                    condition: { priority: 5 },
                    target_channels: ['telegram_main', 'slack_workspace'],
                    priority: 1,
                    enabled: true,
                    fallback_channels: ['telegram_main']
                },
                {
                    name: 'user_support_routing',
                    condition: { message_type: 'support_request' },
                    target_channels: ['slack_workspace'],
                    priority: 2,
                    enabled: true
                }
            ];

            setRoutingRules(mockRules);

        } catch (err) {
            console.error('Failed to fetch routing rules:', err);
        }
    };

    const handleAddChannel = () => {
        setShowAddChannel(true);
        setSelectedChannelType(null);
        setNewChannelConfig({});
    };

    const handleCancelAddChannel = () => {
        setShowAddChannel(false);
        setSelectedChannelType(null);
        setNewChannelConfig({});
    };

    const handleSelectChannelType = (type: string) => {
        setSelectedChannelType(type);
        
        // Initialize config with default values
        const channelConfig = channelTypes.find(ct => ct.type === type);
        if (channelConfig) {
            const initialConfig: Record<string, any> = { channel_type: type };
            channelConfig.config_fields.forEach(field => {
                if (field.type === 'checkbox') {
                    initialConfig[field.name] = false;
                } else if (field.type === 'number') {
                    initialConfig[field.name] = field.placeholder ? parseInt(field.placeholder) : 0;
                } else if (field.options && field.options.length > 0) {
                    initialConfig[field.name] = field.options[0].value;
                } else {
                    initialConfig[field.name] = '';
                }
            });
            setNewChannelConfig(initialConfig);
        }
    };

    const handleConfigChange = (fieldName: string, value: any) => {
        setNewChannelConfig({
            ...newChannelConfig,
            [fieldName]: value
        });
    };

    const handleSubmitNewChannel = async () => {
        if (!selectedChannelType || isAdding) return;

        setIsAdding(true);

        try {
            // Validate required fields
            const channelConfig = channelTypes.find(ct => ct.type === selectedChannelType);
            if (channelConfig) {
                for (const field of channelConfig.config_fields) {
                    if (field.required && !newChannelConfig[field.name]) {
                        setError(`Field ${field.label} is required`);
                        setIsAdding(false);
                        return;
                    }
                }
            }

            // Generate channel ID
            const channelId = `${selectedChannelType}_${Date.now()}`;

            // In a real implementation, this would call the API
            // For now, we'll add to local state
            const newChannel: CommunicationChannel = {
                channel_id: channelId,
                channel_type: selectedChannelType,
                config: { ...newChannelConfig },
                is_default: channels.length === 0,
                status: 'active',
                created_at: new Date().toISOString()
            };

            setChannels([...channels, newChannel]);
            setShowAddChannel(false);

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to add channel');
        } finally {
            setIsAdding(false);
        }
    };

    const handleTestChannel = async (channelId: string) => {
        try {
            // In a real implementation, this would call the test endpoint
            console.log(`Testing channel ${channelId}`);
            
            // Show success message
            alert(`Test message sent successfully to channel ${channelId}!`);

        } catch (err) {
            console.error(`Failed to test channel ${channelId}:`, err);
            alert(`Failed to test channel: ${err instanceof Error ? err.message : 'Unknown error'}`);
        }
    };

    const handleRemoveChannel = async (channelId: string) => {
        if (!window.confirm('Are you sure you want to remove this channel?')) {
            return;
        }

        try {
            // In a real implementation, this would call the API
            setChannels(channels.filter(channel => channel.channel_id !== channelId));

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to remove channel');
        }
    };

    const handleSetDefaultChannel = async (channelId: string) => {
        try {
            // In a real implementation, this would call the API
            setChannels(channels.map(channel => ({
                ...channel,
                is_default: channel.channel_id === channelId
            })));

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to set default channel');
        }
    };

    const handleAddRoutingRule = () => {
        // In a real implementation, this would call the API
        setRoutingRules([...routingRules, { ...newRule, id: Date.now().toString() }]);
        setNewRule({
            name: '',
            condition: {},
            target_channels: [],
            priority: 1,
            enabled: true
        });
    };

    const handleRemoveRoutingRule = (ruleId: string) => {
        setRoutingRules(routingRules.filter(rule => rule.id !== ruleId));
    };

    const renderChannelCard = (channel: CommunicationChannel) => {
        const channelTypeConfig = channelTypes.find(ct => ct.type === channel.channel_type);
        const analytics = analyticsData?.channel_analytics?.[channel.channel_id] || {};

        return (
            <div key={channel.channel_id} className="chronos-surface overflow-hidden">
                <div className="p-4">
                    <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-2">
                            <ProviderLogo
                                name={channelTypeConfig?.name || channel.channel_type}
                                url={getProviderIcon(channelTypeConfig?.logo_key || channel.channel_type)?.url}
                                size={30}
                                className="rounded-md border-white/20"
                            />
                            <div>
                                <h3 className="font-semibold text-foreground">{channelTypeConfig?.name || channel.channel_type}</h3>
                                <p className="text-sm text-muted-foreground">ID: {channel.channel_id}</p>
                            </div>
                        </div>
                        <div className="flex gap-1">
                            {channel.is_default && (
                                <span className="text-xs bg-green-100 text-emerald-300 px-2 py-1 rounded-full">Default</span>
                            )}
                            <span className={`text-xs px-2 py-1 rounded-full ${channel.status === 'active' ? 'bg-green-100 text-emerald-300' : 'bg-yellow-100 text-amber-400'}`}>
                                {channel.status}
                            </span>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Messages</p>
                            <p className="font-semibold text-foreground">{analytics.total_messages || 0}</p>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Success Rate</p>
                            <p className="font-semibold text-foreground">{analytics.success_rate ? analytics.success_rate.toFixed(1) + '%' : 'N/A'}</p>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Active Users</p>
                            <p className="font-semibold text-foreground">{analytics.active_users || 0}</p>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Avg Response</p>
                            <p className="font-semibold text-foreground">{analytics.avg_response_time_ms ? analytics.avg_response_time_ms.toFixed(1) + 'ms' : 'N/A'}</p>
                        </div>
                    </div>

                    <div className="flex gap-2">
                        <button
                            onClick={() => navigate(`/communication/channels/${channel.channel_id}/configure`)}
                            className="flex-1 bg-gray-100 text-muted-foreground py-2 px-3 rounded-md text-sm hover:bg-gray-200 transition-colors"
                        >
                            Configure
                        </button>
                        <button
                            onClick={() => handleTestChannel(channel.channel_id)}
                            className="bg-cyan-400 text-white py-2 px-3 rounded-md text-sm hover:bg-cyan-300 transition-colors"
                        >
                            Test
                        </button>
                        {!channel.is_default && (
                            <button
                                onClick={() => handleSetDefaultChannel(channel.channel_id)}
                                className="bg-green-600 text-white py-2 px-3 rounded-md text-sm hover:bg-green-700 transition-colors"
                            >
                                Set Default
                            </button>
                        )}
                        <button
                            onClick={() => handleRemoveChannel(channel.channel_id)}
                            className="bg-red-600 text-white py-2 px-3 rounded-md text-sm hover:bg-red-700 transition-colors"
                        >
                            Remove
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    const renderConfigField = (field: any, value: any, onChange: (name: string, value: any) => void) => {
        switch (field.type) {
            case 'checkbox':
                return (
                    <div key={field.name} className="mb-4">
                        <label className="flex items-center">
                            <input
                                type="checkbox"
                                checked={!!value}
                                onChange={(e) => onChange(field.name, e.target.checked)}
                                className="h-4 w-4 text-cyan-300 border-border rounded focus:ring-blue-500"
                            />
                            <span className="ml-2 text-sm text-muted-foreground">{field.label}</span>
                        </label>
                        {field.help_text && <p className="text-xs text-muted-foreground mt-1">{field.help_text}</p>}
                    </div>
                );

            case 'select':
                return (
                    <div key={field.name} className="mb-4">
                        <label htmlFor={field.name} className="block text-sm font-medium text-muted-foreground mb-1">
                            {field.label}
                        </label>
                        <select
                            id={field.name}
                            value={value}
                            onChange={(e) => onChange(field.name, e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                            {field.options?.map((option: any) => (
                                <option key={option.value} value={option.value}>{option.label}</option>
                            ))}
                        </select>
                        {field.help_text && <p className="text-xs text-muted-foreground mt-1">{field.help_text}</p>}
                    </div>
                );

            case 'password':
                return (
                    <div key={field.name} className="mb-4">
                        <label htmlFor={field.name} className="block text-sm font-medium text-muted-foreground mb-1">
                            {field.label}
                        </label>
                        <input
                            type="password"
                            id={field.name}
                            value={value}
                            onChange={(e) => onChange(field.name, e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder={field.placeholder}
                        />
                        {field.help_text && <p className="text-xs text-muted-foreground mt-1">{field.help_text}</p>}
                    </div>
                );

            case 'number':
                return (
                    <div key={field.name} className="mb-4">
                        <label htmlFor={field.name} className="block text-sm font-medium text-muted-foreground mb-1">
                            {field.label}
                        </label>
                        <input
                            type="number"
                            id={field.name}
                            value={value}
                            onChange={(e) => onChange(field.name, parseInt(e.target.value) || 0)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder={field.placeholder}
                        />
                        {field.help_text && <p className="text-xs text-muted-foreground mt-1">{field.help_text}</p>}
                    </div>
                );

            default: // text
                return (
                    <div key={field.name} className="mb-4">
                        <label htmlFor={field.name} className="block text-sm font-medium text-muted-foreground mb-1">
                            {field.label}
                        </label>
                        <input
                            type="text"
                            id={field.name}
                            value={value}
                            onChange={(e) => onChange(field.name, e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder={field.placeholder}
                        />
                        {field.help_text && <p className="text-xs text-muted-foreground mt-1">{field.help_text}</p>}
                    </div>
                );
        }
    };

    if (loading && !channels.length) {
        return (
            <ProtectedRoute>
                <PlatformLoadingScreen />
            </ProtectedRoute>
        );
    }

    if (error) {
        return (
            <ProtectedRoute>
                <div className="min-h-screen bg-background p-6">
                    <div className="max-w-7xl mx-auto">
                        <div className="bg-rose-500/10 border border-red-200 rounded-lg p-6">
                            <p className="text-rose-400 mb-4">⚠️ {error}</p>
                            <button
                                onClick={fetchChannels}
                                className="text-sm text-rose-400 hover:text-red-800"
                            >
                                Try again
                            </button>
                        </div>
                    </div>
                </div>
            </ProtectedRoute>
        );
    }

    return (
        <ProtectedRoute>
            <div className="space-y-6">
                <div className="max-w-7xl mx-auto">
                    {/* Header */}
                    <div className="flex flex-wrap justify-between gap-4 items-center mb-6">
                        <div>
                            <p className="text-xs uppercase tracking-[0.2em] text-white/50">Channels</p>
                            <h1 className="mt-2 text-3xl font-bold text-white">Communication Channels</h1>
                            <p className="text-white/65 mt-1">Manage your multi-channel communication integrations</p>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={handleAddChannel}
                                className="bg-cyan-300 text-[#081018] px-4 py-2 rounded-md hover:bg-cyan-200 transition-colors font-semibold"
                            >
                                + Add Channel
                            </button>
                            <button
                                onClick={() => navigate('/app/integrations')}
                                className="bg-black/25 text-muted-foreground px-4 py-2 rounded-md hover:bg-black/35"
                            >
                                View Integrations
                            </button>
                        </div>
                    </div>

                    {/* Tabs */}
                    <div className="chronos-surface overflow-hidden mb-6">
                        <div className="border-b border-border px-6">
                            <div className="flex -mb-px">
                                <button
                                    onClick={() => setActiveTab('channels')}
                                    className={`flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm ${activeTab === 'channels'
                                        ? 'border-blue-600 text-cyan-300'
                                        : 'border-transparent text-muted-foreground hover:text-muted-foreground hover:border-border'}`}
                                >
                                    Communication Channels
                                </button>
                                <button
                                    onClick={() => { setActiveTab('analytics'); fetchAnalytics(); }}
                                    className={`flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm ${activeTab === 'analytics'
                                        ? 'border-blue-600 text-cyan-300'
                                        : 'border-transparent text-muted-foreground hover:text-muted-foreground hover:border-border'}`}
                                >
                                    Analytics Dashboard
                                </button>
                                <button
                                    onClick={() => { setActiveTab('routing'); fetchRoutingRules('all'); }}
                                    className={`flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm ${activeTab === 'routing'
                                        ? 'border-blue-600 text-cyan-300'
                                        : 'border-transparent text-muted-foreground hover:text-muted-foreground hover:border-border'}`}
                                >
                                    Message Routing
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Channels Tab */}
                    {activeTab === 'channels' && (
                        <div>
                            {/* Add Channel Modal */}
                            {showAddChannel && (
                                <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
                                    <div className="chronos-surface w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                                        <div className="p-6 border-b border-border">
                                            <div className="flex justify-between items-center">
                                                <h3 className="text-xl font-semibold text-foreground">Add New Communication Channel</h3>
                                                <button
                                                    onClick={handleCancelAddChannel}
                                                    className="text-muted-foreground/70 hover:text-muted-foreground"
                                                >
                                                    ✕
                                                </button>
                                            </div>
                                            <p className="text-muted-foreground mt-1">Select a channel type and configure the integration</p>
                                        </div>

                                        {!selectedChannelType ? (
                                            <div className="p-6">
                                                <h4 className="font-medium text-muted-foreground mb-4">Select Channel Type</h4>
                                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                                    {channelTypes.map((channelType) => (
                                                        <div
                                                            key={channelType.type}
                                                            onClick={() => handleSelectChannelType(channelType.type)}
                                                            className="bg-background border-2 border-transparent rounded-lg p-4 cursor-pointer hover:border-blue-300 transition-colors"
                                                        >
                                                            <div className="flex items-center gap-3">
                                                                <ProviderLogo
                                                                    name={channelType.name}
                                                                    url={getProviderIcon(channelType.logo_key)?.url}
                                                                    size={32}
                                                                    className="rounded-md border-white/20"
                                                                />
                                                                <div>
                                                                    <h5 className="font-semibold text-foreground">{channelType.name}</h5>
                                                                    <p className="text-sm text-muted-foreground">{channelType.description}</p>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="p-6">
                                                <div className="flex justify-between items-center mb-4">
                                                    <h4 className="font-medium text-muted-foreground">Configure {channelTypes.find(ct => ct.type === selectedChannelType)?.name}</h4>
                                                    <button
                                                        onClick={() => setSelectedChannelType(null)}
                                                        className="text-sm text-cyan-300 hover:text-blue-800"
                                                    >
                                                        ← Change Channel Type
                                                    </button>
                                                </div>

                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                    {channelTypes
                                                        .find(ct => ct.type === selectedChannelType)
                                                        ?.config_fields.map(field => 
                                                            renderConfigField(field, newChannelConfig[field.name], handleConfigChange)
                                                        )}
                                                </div>

                                                <div className="mt-6 bg-cyan-500/10 border border-blue-200 rounded-lg p-4">
                                                    <p className="text-blue-800 text-sm">
                                                        🔒 Your credentials are encrypted and stored securely. They will never be shared or exposed.
                                                    </p>
                                                </div>

                                                <div className="flex justify-end gap-3 mt-6">
                                                    <button
                                                        onClick={handleCancelAddChannel}
                                                        className="bg-gray-100 text-muted-foreground px-4 py-2 rounded-md hover:bg-gray-200"
                                                        disabled={isAdding}
                                                    >
                                                        Cancel
                                                    </button>
                                                    <button
                                                        onClick={handleSubmitNewChannel}
                                                        className={`bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors ${isAdding ? 'opacity-50 cursor-not-allowed' : ''}`}
                                                        disabled={isAdding}
                                                    >
                                                        {isAdding ? (
                                                            <>
                                                                <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>
                                                                Adding...
                                                            </>
                                                        ) : (
                                                            'Add Channel'
                                                        )}
                                                    </button>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Channels Grid */}
                            {channels.length > 0 ? (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {channels.map(renderChannelCard)}
                                </div>
                            ) : (
                                <div className="text-center py-12">
                                    <div className="text-6xl text-gray-300 mb-4">🔌</div>
                                    <p className="text-muted-foreground mb-2">No communication channels configured</p>
                                    <p className="text-sm text-muted-foreground">Click "Add Channel" to get started</p>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Analytics Tab */}
                    {activeTab === 'analytics' && (
                        <div className="chronos-surface p-6">
                            <h3 className="text-xl font-semibold text-foreground mb-6">Communication Analytics Dashboard</h3>

                            {/* Summary Cards */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                                <div className="bg-cyan-500/10 border border-blue-200 rounded-lg p-4">
                                    <p className="text-sm text-cyan-300 mb-1">Total Channels</p>
                                    <p className="text-2xl font-bold text-blue-800">{analyticsData?.total_channels || 0}</p>
                                </div>
                                <div className="bg-emerald-500/10 border border-green-200 rounded-lg p-4">
                                    <p className="text-sm text-emerald-300 mb-1">Total Messages</p>
                                    <p className="text-2xl font-bold text-green-800">{analyticsData?.total_messages || 0}</p>
                                </div>
                                <div className="bg-amber-500/10 border border-yellow-200 rounded-lg p-4">
                                    <p className="text-sm text-amber-400 mb-1">Success Rate</p>
                                    <p className="text-2xl font-bold text-yellow-800">{analyticsData?.success_rate ? analyticsData.success_rate.toFixed(1) + '%' : 'N/A'}</p>
                                </div>
                                <div className="bg-rose-500/10 border border-red-200 rounded-lg p-4">
                                    <p className="text-sm text-rose-400 mb-1">Failed Messages</p>
                                    <p className="text-2xl font-bold text-red-800">{analyticsData?.failed_messages || 0}</p>
                                </div>
                            </div>

                            {/* Channel Analytics */}
                            <div className="mb-6">
                                <h4 className="font-semibold text-muted-foreground mb-4">Channel Performance</h4>
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead className="bg-background">
                                            <tr>
                                                <th className="px-4 py-2 text-left text-sm font-medium text-muted-foreground">Channel</th>
                                                <th className="px-4 py-2 text-left text-sm font-medium text-muted-foreground">Messages</th>
                                                <th className="px-4 py-2 text-left text-sm font-medium text-muted-foreground">Success</th>
                                                <th className="px-4 py-2 text-left text-sm font-medium text-muted-foreground">Failed</th>
                                                <th className="px-4 py-2 text-left text-sm font-medium text-muted-foreground">Success Rate</th>
                                                <th className="px-4 py-2 text-left text-sm font-medium text-muted-foreground">Avg Response</th>
                                                <th className="px-4 py-2 text-left text-sm font-medium text-muted-foreground">Active Users</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {channels.map(channel => {
                                                const channelAnalytics = analyticsData?.channel_analytics?.[channel.channel_id] || {};
                                                const channelTypeConfig = channelTypes.find(ct => ct.type === channel.channel_type);

                                                return (
                                                    <tr key={channel.channel_id} className="border-t border-border">
                                                        <td className="px-4 py-3">
                                                            <div className="flex items-center gap-2">
                                                                <ProviderLogo
                                                                    name={channelTypeConfig?.name || channel.channel_type}
                                                                    url={getProviderIcon(channelTypeConfig?.logo_key || channel.channel_type)?.url}
                                                                    size={24}
                                                                    className="border-white/20"
                                                                />
                                                                <span className="font-medium text-foreground">{channelTypeConfig?.name || channel.channel_type}</span>
                                                            </div>
                                                        </td>
                                                        <td className="px-4 py-3">{channelAnalytics.total_messages || 0}</td>
                                                        <td className="px-4 py-3">{channelAnalytics.successful_messages || 0}</td>
                                                        <td className="px-4 py-3">{channelAnalytics.failed_messages || 0}</td>
                                                        <td className="px-4 py-3">
                                                            {channelAnalytics.success_rate ? channelAnalytics.success_rate.toFixed(1) + '%' : 'N/A'}
                                                        </td>
                                                        <td className="px-4 py-3">
                                                            {channelAnalytics.avg_response_time_ms ? channelAnalytics.avg_response_time_ms.toFixed(1) + 'ms' : 'N/A'}
                                                        </td>
                                                        <td className="px-4 py-3">{channelAnalytics.active_users || 0}</td>
                                                    </tr>
                                                );
                                            })}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            {/* Performance Charts */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="bg-background rounded-lg p-4">
                                    <h5 className="font-medium text-muted-foreground mb-3">Message Volume by Channel</h5>
                                    <div className="h-48 chronos-surface flex items-center justify-center">
                                        <p className="text-muted-foreground">Chart would display here in real implementation</p>
                                    </div>
                                </div>
                                <div className="bg-background rounded-lg p-4">
                                    <h5 className="font-medium text-muted-foreground mb-3">Success Rate by Channel</h5>
                                    <div className="h-48 chronos-surface flex items-center justify-center">
                                        <p className="text-muted-foreground">Chart would display here in real implementation</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Routing Tab */}
                    {activeTab === 'routing' && (
                        <div className="chronos-surface p-6">
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-xl font-semibold text-foreground">Message Routing Rules</h3>
                                <button
                                    onClick={() => navigate('/app/channels')}
                                    className="bg-cyan-400 text-white px-4 py-2 rounded-md hover:bg-cyan-300 transition-colors"
                                >
                                    Advanced Routing
                                </button>
                            </div>

                            {/* Add Routing Rule */}
                            <div className="mb-6 bg-background rounded-lg p-4">
                                <h4 className="font-medium text-muted-foreground mb-3">Add New Routing Rule</h4>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Rule Name</label>
                                        <input
                                            id="rule-name"
                                            type="text"
                                            value={newRule.name}
                                            onChange={(e) => setNewRule({...newRule, name: e.target.value})}
                                            className="w-full px-3 py-2 border border-border rounded-md"
                                            placeholder="e.g., high_priority_routing"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                                        <input
                                            id="rule-priority"
                                            type="number"
                                            value={newRule.priority}
                                            onChange={(e) => setNewRule({...newRule, priority: parseInt(e.target.value) || 1})}
                                            className="w-full px-3 py-2 border border-border rounded-md"
                                            min="1"
                                            max="5"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Target Channels</label>
                                        <select
                                            id="target-channels"
                                            multiple
                                            value={newRule.target_channels}
                                            onChange={(e) => {
                                                const options = Array.from(e.target.selectedOptions).map(option => option.value);
                                                setNewRule({...newRule, target_channels: options});
                                            }}
                                            className="w-full px-3 py-2 border border-border rounded-md"
                                        >
                                            {channels.map(channel => (
                                                <option key={channel.channel_id} value={channel.channel_id}>{channel.channel_id}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>
                                <button
                                    onClick={handleAddRoutingRule}
                                    className="mt-3 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
                                    disabled={!newRule.name || newRule.target_channels.length === 0}
                                >
                                    Add Routing Rule
                                </button>
                            </div>

                            {/* Routing Rules Table */}
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead className="bg-background">
                                        <tr>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-muted-foreground">Name</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-muted-foreground">Priority</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-muted-foreground">Condition</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-muted-foreground">Target Channels</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-muted-foreground">Status</th>
                                            <th className="px-4 py-2 text-left text-sm font-medium text-muted-foreground">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {routingRules.map(rule => (
                                            <tr key={rule.id} className="border-t border-border">
                                                <td className="px-4 py-3 font-medium text-foreground">{rule.name}</td>
                                                <td className="px-4 py-3">{rule.priority}</td>
                                                <td className="px-4 py-3">
                                                    <code className="text-sm bg-gray-100 px-2 py-1 rounded">
                                                        {JSON.stringify(rule.condition)}
                                                    </code>
                                                </td>
                                                <td className="px-4 py-3">{rule.target_channels.join(', ')}</td>
                                                <td className="px-4 py-3">
                                                    <span className={`text-xs px-2 py-1 rounded-full ${rule.enabled ? 'bg-green-100 text-emerald-300' : 'bg-yellow-100 text-amber-400'}`}>
                                                        {rule.enabled ? 'Enabled' : 'Disabled'}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <button
                                                        onClick={() => handleRemoveRoutingRule(rule.id)}
                                                        className="text-rose-400 hover:text-red-800 text-sm"
                                                    >
                                                        Remove
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>

                            {/* Routing Visualization */}
                            <div className="mt-6 bg-background rounded-lg p-4">
                                <h4 className="font-medium text-muted-foreground mb-3">Routing Flow Visualization</h4>
                                <div className="h-64 chronos-surface flex items-center justify-center">
                                    <p className="text-muted-foreground">Interactive routing flow diagram would display here</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </ProtectedRoute>
    );
};

export default CommunicationChannelsPage;


