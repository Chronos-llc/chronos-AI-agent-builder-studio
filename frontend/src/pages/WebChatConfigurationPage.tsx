import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { useAuth } from '../contexts/AuthContext';

interface WebChatConfig {
    embed_type: string;
    theme: {
        primary_color: string;
        secondary_color: string;
        text_color: string;
        background_color: string;
    };
    position: string;
    mobile_responsive: boolean;
    accessibility_features: {
        high_contrast: boolean;
        screen_reader_support: boolean;
        keyboard_navigation: boolean;
    };
    custom_css?: string;
    custom_js?: string;
    voice_input_enabled: boolean;
    voice_output_enabled: boolean;
    voice_language: string;
    voice_rate: number;
    voice_pitch: number;
    feedback_enabled: boolean;
    feedback_types: string[];
    analytics_enabled: boolean;
    analytics_tracking_id?: string;
    auto_open: boolean;
    auto_open_delay: number;
    persistent_menu: boolean;
    welcome_message: string;
    placeholder_text: string;
    brand_name: string;
    brand_logo?: string;
    show_typing_indicator: boolean;
    show_message_timestamps: boolean;
    show_user_avatars: boolean;
    allow_file_uploads: boolean;
    allowed_file_types: string[];
    max_file_size_mb: number;
}

interface WebChatSession {
    session_id: string;
    user_id: string;
    status: string;
    created_at: string;
    message_count: number;
}

const WebChatConfigurationPage: React.FC = () => {
    const { session_id } = useParams<{ session_id: string }>();
    const { user } = useAuth();
    const navigate = useNavigate();
    const [config, setConfig] = useState<WebChatConfig>({
        embed_type: 'bubble',
        theme: {
            primary_color: '#4F46E5',
            secondary_color: '#1F2937',
            text_color: '#FFFFFF',
            background_color: '#FFFFFF'
        },
        position: 'bottom_right',
        mobile_responsive: true,
        accessibility_features: {
            high_contrast: false,
            screen_reader_support: true,
            keyboard_navigation: true
        },
        voice_input_enabled: false,
        voice_output_enabled: false,
        voice_language: 'en-US',
        voice_rate: 1.0,
        voice_pitch: 1.0,
        feedback_enabled: true,
        feedback_types: ['thumbs_up', 'thumbs_down', 'text'],
        analytics_enabled: true,
        auto_open: false,
        auto_open_delay: 3000,
        persistent_menu: true,
        welcome_message: 'Hello! How can I help you today?',
        placeholder_text: 'Type your message...',
        brand_name: 'Chronos AI',
        show_typing_indicator: true,
        show_message_timestamps: true,
        show_user_avatars: true,
        allow_file_uploads: true,
        allowed_file_types: ['image/*', 'application/pdf', 'text/*'],
        max_file_size_mb: 10
    });
    const [sessions, setSessions] = useState<WebChatSession[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<'design' | 'features' | 'analytics' | 'sessions' | 'embed'>('design');
    const [isSaving, setIsSaving] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [embedCode, setEmbedCode] = useState<string>('');
    const [analyticsData, setAnalyticsData] = useState<any>(null);

    useEffect(() => {
        if (session_id) {
            fetchWebChatConfig(session_id);
            fetchSessions(session_id);
            fetchAnalytics(session_id);
        } else {
            // New configuration
            setLoading(false);
        }
    }, [session_id]);

    const fetchWebChatConfig = async (sessionId: string) => {
        try {
            setLoading(true);
            setError(null);

            // Mock data - in real implementation, this would fetch from API
            const mockConfig: WebChatConfig = {
                embed_type: 'bubble',
                theme: {
                    primary_color: '#4F46E5',
                    secondary_color: '#1F2937',
                    text_color: '#FFFFFF',
                    background_color: '#FFFFFF'
                },
                position: 'bottom_right',
                mobile_responsive: true,
                accessibility_features: {
                    high_contrast: false,
                    screen_reader_support: true,
                    keyboard_navigation: true
                },
                voice_input_enabled: false,
                voice_output_enabled: false,
                voice_language: 'en-US',
                voice_rate: 1.0,
                voice_pitch: 1.0,
                feedback_enabled: true,
                feedback_types: ['thumbs_up', 'thumbs_down', 'text'],
                analytics_enabled: true,
                analytics_tracking_id: 'UA-XXXXXX-X',
                auto_open: false,
                auto_open_delay: 3000,
                persistent_menu: true,
                welcome_message: 'Hello! How can I help you today?',
                placeholder_text: 'Type your message...',
                brand_name: 'Chronos AI',
                brand_logo: 'https://chronos.ai/logo.png',
                show_typing_indicator: true,
                show_message_timestamps: true,
                show_user_avatars: true,
                allow_file_uploads: true,
                allowed_file_types: ['image/*', 'application/pdf', 'text/*'],
                max_file_size_mb: 10
            };

            setConfig(mockConfig);

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch WebChat configuration');
        } finally {
            setLoading(false);
        }
    };

    const fetchSessions = async (sessionId: string) => {
        try {
            // Mock sessions data
            const mockSessions: WebChatSession[] = [
                {
                    session_id: 'webchat_12345',
                    user_id: 'user_abc123',
                    status: 'active',
                    created_at: '2023-01-01T10:30:00Z',
                    message_count: 42
                },
                {
                    session_id: 'webchat_67890',
                    user_id: 'user_def456',
                    status: 'ended',
                    created_at: '2023-01-02T14:15:00Z',
                    message_count: 18
                }
            ];

            setSessions(mockSessions);

        } catch (err) {
            console.error('Failed to fetch sessions:', err);
        }
    };

    const fetchAnalytics = async (sessionId: string) => {
        try {
            // Mock analytics data
            const mockAnalytics = {
                total_sessions: 42,
                active_sessions: 8,
                total_messages: 1245,
                avg_session_duration: 345.2,
                user_satisfaction: 87.5,
                daily_active_users: 128,
                weekly_active_users: 456,
                monthly_active_users: 1245
            };

            setAnalyticsData(mockAnalytics);

        } catch (err) {
            console.error('Failed to fetch analytics:', err);
        }
    };

    const handleConfigChange = (section: string, field: string, value: any) => {
        if (section === 'theme') {
            setConfig({
                ...config,
                theme: {
                    ...config.theme,
                    [field]: value
                }
            });
        } else if (section === 'accessibility') {
            setConfig({
                ...config,
                accessibility_features: {
                    ...config.accessibility_features,
                    [field]: value
                }
            });
        } else {
            setConfig({
                ...config,
                [field]: value
            });
        }
    };

    const handleSave = async () => {
        if (!config || isSaving) return;

        setIsSaving(true);
        setError(null);

        try {
            // In a real implementation, this would call the API
            console.log('Saving WebChat configuration:', config);

            // Show success message
            alert('WebChat configuration saved successfully!');

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to save WebChat configuration');
        } finally {
            setIsSaving(false);
        }
    };

    const handleGenerateEmbedCode = async () => {
        if (!config || isGenerating) return;

        setIsGenerating(true);
        setError(null);

        try {
            // In a real implementation, this would call the API
            // For now, we'll generate a simple embed code
            const sessionId = session_id || 'webchat_' + Date.now();

            let embedCode = '';

            if (config.embed_type === 'bubble') {
                embedCode = `<!-- Chronos AI WebChat Bubble Embed -->
<div id="chronos-webchat-bubble">
    <script>
        (function() {
            var script = document.createElement('script');
            script.src = 'https://cdn.chronos.ai/webchat/bubble.js';
            script.async = true;
            script.onload = function() {
                window.ChronosWebChat.init({
                    sessionId: '${sessionId}',
                    config: ${JSON.stringify(config, null, 2)}
                });
            };
            document.head.appendChild(script);
        })();
    </script>
</div>`;
            } else if (config.embed_type === 'iframe') {
                embedCode = `<!-- Chronos AI WebChat Iframe Embed -->
<iframe
    src="https://chat.chronos.ai/embed/${sessionId}"
    width="100%"
    height="600"
    frameborder="0"
    style="border: none; border-radius: 8px;"
    allow="microphone; camera"
></iframe>`;
            } else if (config.embed_type === 'standalone') {
                embedCode = `<!-- Chronos AI WebChat Standalone Embed -->
<div id="chronos-webchat-standalone">
    <iframe
        src="https://chat.chronos.ai/standalone/${sessionId}"
        width="100%"
        height="700"
        frameborder="0"
        style="border: none; border-radius: 12px;"
        allow="microphone; camera"
    ></iframe>
</div>`;
            } else if (config.embed_type === 'react') {
                embedCode = `// Chronos AI WebChat React Component
import React from 'react';
import { ChronosWebChat } from '@chronos-ai/webchat-react';

const MyWebChat = () => {
    return (
        <ChronosWebChat
            sessionId="${sessionId}"
            config=${JSON.stringify(config, null, 2)}
        />
    );
};

export default MyWebChat;`;
            }

            setEmbedCode(embedCode);

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to generate embed code');
        } finally {
            setIsGenerating(false);
        }
    };

    const handleCopyEmbedCode = () => {
        navigator.clipboard.writeText(embedCode);
        alert('Embed code copied to clipboard!');
    };

    const handleAddFeedbackType = (type: string) => {
        if (!config.feedback_types.includes(type)) {
            setConfig({
                ...config,
                feedback_types: [...config.feedback_types, type]
            });
        }
    };

    const handleRemoveFeedbackType = (type: string) => {
        setConfig({
            ...config,
            feedback_types: config.feedback_types.filter(t => t !== type)
        });
    };

    const handleAddFileType = () => {
        const newType = prompt('Enter MIME type (e.g., application/pdf):');
        if (newType && !config.allowed_file_types.includes(newType)) {
            setConfig({
                ...config,
                allowed_file_types: [...config.allowed_file_types, newType]
            });
        }
    };

    const handleRemoveFileType = (type: string) => {
        setConfig({
            ...config,
            allowed_file_types: config.allowed_file_types.filter(t => t !== type)
        });
    };

    if (loading && !config) {
        return (
            <ProtectedRoute>
                <div className="min-h-screen bg-gray-50 p-6">
                    <div className="max-w-4xl mx-auto">
                        <div className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
                            <div className="h-8 bg-gray-200 rounded mb-4 w-1/3"></div>
                            <div className="h-4 bg-gray-200 rounded mb-2 w-full"></div>
                            <div className="h-4 bg-gray-200 rounded mb-4 w-2/3"></div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="h-4 bg-gray-200 rounded"></div>
                                <div className="h-4 bg-gray-200 rounded"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </ProtectedRoute>
        );
    }

    if (error) {
        return (
            <ProtectedRoute>
                <div className="min-h-screen bg-gray-50 p-6">
                    <div className="max-w-4xl mx-auto">
                        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                            <p className="text-red-600 mb-4">⚠️ {error}</p>
                            <button
                                onClick={() => session_id && fetchWebChatConfig(session_id)}
                                className="text-sm text-red-600 hover:text-red-800"
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
            <div className="min-h-screen bg-gray-50 p-6">
                <div className="max-w-4xl mx-auto">
                    {/* Header */}
                    <div className="flex justify-between items-center mb-6">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">WebChat Configuration</h1>
                            <p className="text-gray-600 mt-1">Customize your advanced WebChat integration</p>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => navigate('/communication/channels')}
                                className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200"
                            >
                                ← Back to Channels
                            </button>
                            <button
                                onClick={() => navigate('/integrations')}
                                className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200"
                            >
                                View Integrations
                            </button>
                        </div>
                    </div>

                    {/* WebChat Preview */}
                    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">WebChat Preview</h3>
                        <div className="bg-gray-100 rounded-lg p-8 text-center">
                            <div className="text-6xl mb-4">💬</div>
                            <p className="text-gray-600 mb-2">WebChat preview would appear here</p>
                            <p className="text-sm text-gray-500">Configure your settings and generate embed code to see the live preview</p>
                        </div>
                    </div>

                    {/* Configuration Tabs */}
                    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                        <div className="border-b border-gray-200 px-6">
                            <div className="flex -mb-px">
                                <button
                                    onClick={() => setActiveTab('design')}
                                    className={`flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm ${activeTab === 'design'
                                        ? 'border-blue-600 text-blue-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
                                >
                                    Design & Branding
                                </button>
                                <button
                                    onClick={() => setActiveTab('features')}
                                    className={`flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm ${activeTab === 'features'
                                        ? 'border-blue-600 text-blue-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
                                >
                                    Features
                                </button>
                                <button
                                    onClick={() => setActiveTab('analytics')}
                                    className={`flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm ${activeTab === 'analytics'
                                        ? 'border-blue-600 text-blue-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
                                >
                                    Analytics
                                </button>
                                <button
                                    onClick={() => setActiveTab('sessions')}
                                    className={`flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm ${activeTab === 'sessions'
                                        ? 'border-blue-600 text-blue-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
                                >
                                    Sessions
                                </button>
                                <button
                                    onClick={() => setActiveTab('embed')}
                                    className={`flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm ${activeTab === 'embed'
                                        ? 'border-blue-600 text-blue-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
                                >
                                    Embed Code
                                </button>
                            </div>
                        </div>

                        <div className="p-6">
                            {activeTab === 'design' && (
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Design & Branding</h3>
                                    <p className="text-gray-600 mb-6">Customize the appearance and branding of your WebChat</p>

                                    {/* Embed Type */}
                                    <div className="mb-6">
                                        <h4 className="font-medium text-gray-700 mb-3">Embed Type</h4>
                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                            {['bubble', 'iframe', 'standalone', 'react'].map(type => (
                                                <label key={type} className="flex items-center">
                                                    <input
                                                        type="radio"
                                                        name="embed_type"
                                                        value={type}
                                                        checked={config.embed_type === type}
                                                        onChange={() => handleConfigChange('', 'embed_type', type)}
                                                        className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                    />
                                                    <span className="ml-2 text-sm text-gray-700 capitalize">{type}</span>
                                                </label>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Theme Configuration */}
                                    <div className="mb-6">
                                        <h4 className="font-medium text-gray-700 mb-3">Theme Configuration</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Primary Color</label>
                                                <div className="flex items-center gap-2">
                                                    <input
                                                        type="color"
                                                        value={config.theme.primary_color}
                                                        onChange={(e) => handleConfigChange('theme', 'primary_color', e.target.value)}
                                                        className="w-10 h-10 rounded border border-gray-300"
                                                        aria-label="Primary color picker"
                                                        title="Primary color picker"
                                                    />
                                                    <input
                                                        type="text"
                                                        value={config.theme.primary_color}
                                                        onChange={(e) => handleConfigChange('theme', 'primary_color', e.target.value)}
                                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                                                        aria-label="Primary color hex value"
                                                        placeholder="#RRGGBB"
                                                        title="Primary color hex value"
                                                    />
                                                </div>
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Secondary Color</label>
                                                <div className="flex items-center gap-2">
                                                    <input
                                                        type="color"
                                                        value={config.theme.secondary_color}
                                                        onChange={(e) => handleConfigChange('theme', 'secondary_color', e.target.value)}
                                                        className="w-10 h-10 rounded border border-gray-300"
                                                        aria-label="Secondary color picker"
                                                        title="Secondary color picker"
                                                    />
                                                    <input
                                                        type="text"
                                                        value={config.theme.secondary_color}
                                                        onChange={(e) => handleConfigChange('theme', 'secondary_color', e.target.value)}
                                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                                                        aria-label="Secondary color hex value"
                                                        placeholder="#RRGGBB"
                                                        title="Secondary color hex value"
                                                    />
                                                </div>
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Text Color</label>
                                                <div className="flex items-center gap-2">
                                                    <input
                                                        type="color"
                                                        value={config.theme.text_color}
                                                        onChange={(e) => handleConfigChange('theme', 'text_color', e.target.value)}
                                                        className="w-10 h-10 rounded border border-gray-300"
                                                    />
                                                    <input
                                                        type="text"
                                                        value={config.theme.text_color}
                                                        onChange={(e) => handleConfigChange('theme', 'text_color', e.target.value)}
                                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                                                    />
                                                </div>
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Background Color</label>
                                                <div className="flex items-center gap-2">
                                                    <input
                                                        type="color"
                                                        value={config.theme.background_color}
                                                        onChange={(e) => handleConfigChange('theme', 'background_color', e.target.value)}
                                                        className="w-10 h-10 rounded border border-gray-300"
                                                    />
                                                    <input
                                                        type="text"
                                                        value={config.theme.background_color}
                                                        onChange={(e) => handleConfigChange('theme', 'background_color', e.target.value)}
                                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Position & Layout */}
                                    <div className="mb-6">
                                        <h4 className="font-medium text-gray-700 mb-3">Position & Layout</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Position</label>
                                                <select
                                                    value={config.position}
                                                    onChange={(e) => handleConfigChange('', 'position', e.target.value)}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                                >
                                                    <option value="bottom_right">Bottom Right</option>
                                                    <option value="bottom_left">Bottom Left</option>
                                                    <option value="top_right">Top Right</option>
                                                    <option value="top_left">Top Left</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Mobile Responsive</label>
                                                <div className="flex items-center">
                                                    <input
                                                        type="checkbox"
                                                        checked={config.mobile_responsive}
                                                        onChange={(e) => handleConfigChange('', 'mobile_responsive', e.target.checked)}
                                                        className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                    />
                                                    <span className="ml-2 text-sm text-gray-700">Enable mobile responsiveness</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Branding */}
                                    <div className="mb-6">
                                        <h4 className="font-medium text-gray-700 mb-3">Branding</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Brand Name</label>
                                                <input
                                                    type="text"
                                                    value={config.brand_name}
                                                    onChange={(e) => handleConfigChange('', 'brand_name', e.target.value)}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                                    placeholder="Your Brand Name"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Brand Logo URL</label>
                                                <input
                                                    type="text"
                                                    value={config.brand_logo || ''}
                                                    onChange={(e) => handleConfigChange('', 'brand_logo', e.target.value)}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                                    placeholder="https://yourdomain.com/logo.png"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Welcome Message</label>
                                                <input
                                                    type="text"
                                                    value={config.welcome_message}
                                                    onChange={(e) => handleConfigChange('', 'welcome_message', e.target.value)}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                                    placeholder="Hello! How can I help you today?"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Input Placeholder</label>
                                                <input
                                                    type="text"
                                                    value={config.placeholder_text}
                                                    onChange={(e) => handleConfigChange('', 'placeholder_text', e.target.value)}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                                    placeholder="Type your message..."
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Accessibility */}
                                    <div className="mb-6">
                                        <h4 className="font-medium text-gray-700 mb-3">Accessibility Features</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div className="flex items-center">
                                                <input
                                                    type="checkbox"
                                                    checked={config.accessibility_features.high_contrast}
                                                    onChange={(e) => handleConfigChange('accessibility', 'high_contrast', e.target.checked)}
                                                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                />
                                                <span className="ml-2 text-sm text-gray-700">High Contrast Mode</span>
                                            </div>
                                            <div className="flex items-center">
                                                <input
                                                    type="checkbox"
                                                    checked={config.accessibility_features.screen_reader_support}
                                                    onChange={(e) => handleConfigChange('accessibility', 'screen_reader_support', e.target.checked)}
                                                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                />
                                                <span className="ml-2 text-sm text-gray-700">Screen Reader Support</span>
                                            </div>
                                            <div className="flex items-center">
                                                <input
                                                    type="checkbox"
                                                    checked={config.accessibility_features.keyboard_navigation}
                                                    onChange={(e) => handleConfigChange('accessibility', 'keyboard_navigation', e.target.checked)}
                                                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                />
                                                <span className="ml-2 text-sm text-gray-700">Keyboard Navigation</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'features' && (
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Advanced Features</h3>
                                    <p className="text-gray-600 mb-6">Enable and configure advanced WebChat features</p>

                                    {/* Voice Features */}
                                    <div className="mb-6 bg-gray-50 rounded-lg p-4">
                                        <h4 className="font-medium text-gray-700 mb-3">🎤 Voice Input/Output</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div className="flex items-center">
                                                <input
                                                    type="checkbox"
                                                    checked={config.voice_input_enabled}
                                                    onChange={(e) => handleConfigChange('', 'voice_input_enabled', e.target.checked)}
                                                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                />
                                                <span className="ml-2 text-sm text-gray-700">Enable Voice Input</span>
                                            </div>
                                            <div className="flex items-center">
                                                <input
                                                    type="checkbox"
                                                    checked={config.voice_output_enabled}
                                                    onChange={(e) => handleConfigChange('', 'voice_output_enabled', e.target.checked)}
                                                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                />
                                                <span className="ml-2 text-sm text-gray-700">Enable Voice Output</span>
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Voice Language</label>
                                                <select
                                                    value={config.voice_language}
                                                    onChange={(e) => handleConfigChange('', 'voice_language', e.target.value)}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                                >
                                                    <option value="en-US">English (US)</option>
                                                    <option value="en-GB">English (UK)</option>
                                                    <option value="es-ES">Spanish</option>
                                                    <option value="fr-FR">French</option>
                                                    <option value="de-DE">German</option>
                                                    <option value="ja-JP">Japanese</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Voice Rate</label>
                                                <input
                                                    type="range"
                                                    min="0.5"
                                                    max="2.0"
                                                    step="0.1"
                                                    value={config.voice_rate}
                                                    onChange={(e) => handleConfigChange('', 'voice_rate', parseFloat(e.target.value))}
                                                    className="w-full"
                                                />
                                                <span className="text-sm text-gray-600">{config.voice_rate}x</span>
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Voice Pitch</label>
                                                <input
                                                    type="range"
                                                    min="0.5"
                                                    max="2.0"
                                                    step="0.1"
                                                    value={config.voice_pitch}
                                                    onChange={(e) => handleConfigChange('', 'voice_pitch', parseFloat(e.target.value))}
                                                    className="w-full"
                                                />
                                                <span className="text-sm text-gray-600">{config.voice_pitch}x</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* User Feedback */}
                                    <div className="mb-6 bg-gray-50 rounded-lg p-4">
                                        <h4 className="font-medium text-gray-700 mb-3">❤️ User Feedback</h4>
                                        <div className="flex items-center mb-3">
                                            <input
                                                type="checkbox"
                                                checked={config.feedback_enabled}
                                                onChange={(e) => handleConfigChange('', 'feedback_enabled', e.target.checked)}
                                                className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">Enable User Feedback Collection</span>
                                        </div>

                                        {config.feedback_enabled && (
                                            <div className="ml-6">
                                                <label className="block text-sm font-medium text-gray-700 mb-2">Feedback Types</label>
                                                <div className="flex flex-wrap gap-2 mb-3">
                                                    {config.feedback_types.map(type => (
                                                        <span key={type} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center">
                                                            {type === 'thumbs_up' ? '👍' : type === 'thumbs_down' ? '👎' : '💬'}
                                                            <button
                                                                onClick={() => handleRemoveFeedbackType(type)}
                                                                className="ml-2 text-blue-600 hover:text-blue-800"
                                                            >
                                                                ✕
                                                            </button>
                                                        </span>
                                                    ))}
                                                </div>
                                                <div className="flex flex-wrap gap-2">
                                                    {!config.feedback_types.includes('thumbs_up') && (
                                                        <button
                                                            onClick={() => handleAddFeedbackType('thumbs_up')}
                                                            className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm hover:bg-gray-200"
                                                        >
                                                            👍 Thumbs Up
                                                        </button>
                                                    )}
                                                    {!config.feedback_types.includes('thumbs_down') && (
                                                        <button
                                                            onClick={() => handleAddFeedbackType('thumbs_down')}
                                                            className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm hover:bg-gray-200"
                                                        >
                                                            👎 Thumbs Down
                                                        </button>
                                                    )}
                                                    {!config.feedback_types.includes('text') && (
                                                        <button
                                                            onClick={() => handleAddFeedbackType('text')}
                                                            className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm hover:bg-gray-200"
                                                        >
                                                            💬 Text Feedback
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {/* File Uploads */}
                                    <div className="mb-6 bg-gray-50 rounded-lg p-4">
                                        <h4 className="font-medium text-gray-700 mb-3">📎 File Uploads</h4>
                                        <div className="flex items-center mb-3">
                                            <input
                                                type="checkbox"
                                                checked={config.allow_file_uploads}
                                                onChange={(e) => handleConfigChange('', 'allow_file_uploads', e.target.checked)}
                                                className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">Allow File Uploads</span>
                                        </div>

                                        {config.allow_file_uploads && (
                                            <div className="ml-6">
                                                <div className="mb-3">
                                                    <label className="block text-sm font-medium text-gray-700 mb-1">Max File Size</label>
                                                    <div className="flex items-center gap-2">
                                                        <input
                                                            type="number"
                                                            value={config.max_file_size_mb}
                                                            onChange={(e) => handleConfigChange('', 'max_file_size_mb', parseInt(e.target.value) || 1)}
                                                            className="w-20 px-3 py-2 border border-gray-300 rounded-md"
                                                            min="1"
                                                            max="100"
                                                        />
                                                        <span className="text-sm text-gray-600">MB</span>
                                                    </div>
                                                </div>

                                                <label className="block text-sm font-medium text-gray-700 mb-2">Allowed File Types</label>
                                                <div className="flex flex-wrap gap-2 mb-3">
                                                    {config.allowed_file_types.map(type => (
                                                        <span key={type} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm flex items-center">
                                                            {type}
                                                            <button
                                                                onClick={() => handleRemoveFileType(type)}
                                                                className="ml-2 text-green-600 hover:text-green-800"
                                                            >
                                                                ✕
                                                            </button>
                                                        </span>
                                                    ))}
                                                </div>
                                                <button
                                                    onClick={handleAddFileType}
                                                    className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm hover:bg-gray-200"
                                                >
                                                    + Add File Type
                                                </button>
                                            </div>
                                        )}
                                    </div>

                                    {/* Behavior Settings */}
                                    <div className="mb-6 bg-gray-50 rounded-lg p-4">
                                        <h4 className="font-medium text-gray-700 mb-3">⚙️ Behavior Settings</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div className="flex items-center">
                                                <input
                                                    type="checkbox"
                                                    checked={config.auto_open}
                                                    onChange={(e) => handleConfigChange('', 'auto_open', e.target.checked)}
                                                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                />
                                                <span className="ml-2 text-sm text-gray-700">Auto-open on Page Load</span>
                                            </div>
                                            <div className="flex items-center">
                                                <input
                                                    type="checkbox"
                                                    checked={config.persistent_menu}
                                                    onChange={(e) => handleConfigChange('', 'persistent_menu', e.target.checked)}
                                                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                />
                                                <span className="ml-2 text-sm text-gray-700">Show Persistent Menu</span>
                                            </div>
                                            <div className="flex items-center">
                                                <input
                                                    type="checkbox"
                                                    checked={config.show_typing_indicator}
                                                    onChange={(e) => handleConfigChange('', 'show_typing_indicator', e.target.checked)}
                                                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                />
                                                <span className="ml-2 text-sm text-gray-700">Show Typing Indicator</span>
                                            </div>
                                            <div className="flex items-center">
                                                <input
                                                    type="checkbox"
                                                    checked={config.show_message_timestamps}
                                                    onChange={(e) => handleConfigChange('', 'show_message_timestamps', e.target.checked)}
                                                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                />
                                                <span className="ml-2 text-sm text-gray-700">Show Message Timestamps</span>
                                            </div>
                                            <div className="flex items-center">
                                                <input
                                                    type="checkbox"
                                                    checked={config.show_user_avatars}
                                                    onChange={(e) => handleConfigChange('', 'show_user_avatars', e.target.checked)}
                                                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                />
                                                <span className="ml-2 text-sm text-gray-700">Show User Avatars</span>
                                            </div>
                                        </div>

                                        {config.auto_open && (
                                            <div className="mt-3">
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Auto-open Delay</label>
                                                <div className="flex items-center gap-2">
                                                    <input
                                                        type="number"
                                                        value={config.auto_open_delay}
                                                        onChange={(e) => handleConfigChange('', 'auto_open_delay', parseInt(e.target.value) || 1000)}
                                                        className="w-20 px-3 py-2 border border-gray-300 rounded-md"
                                                        min="500"
                                                        max="10000"
                                                    />
                                                    <span className="text-sm text-gray-600">milliseconds</span>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            {activeTab === 'analytics' && (
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Analytics & Tracking</h3>
                                    <p className="text-gray-600 mb-6">Configure analytics and user tracking for your WebChat</p>

                                    <div className="mb-6">
                                        <div className="flex items-center mb-4">
                                            <input
                                                type="checkbox"
                                                checked={config.analytics_enabled}
                                                onChange={(e) => handleConfigChange('', 'analytics_enabled', e.target.checked)}
                                                className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                            />
                                            <span className="ml-2 text-sm text-gray-700">Enable Analytics Tracking</span>
                                        </div>

                                        {config.analytics_enabled && (
                                            <div className="ml-6">
                                                <div className="mb-4">
                                                    <label className="block text-sm font-medium text-gray-700 mb-1">Analytics Tracking ID</label>
                                                    <input
                                                        type="text"
                                                        value={config.analytics_tracking_id || ''}
                                                        onChange={(e) => handleConfigChange('', 'analytics_tracking_id', e.target.value)}
                                                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                                        placeholder="UA-XXXXXX-X or G-XXXXXXXXXX"
                                                    />
                                                    <p className="text-xs text-gray-500 mt-1">Google Analytics or other tracking ID</p>
                                                </div>

                                                {/* Analytics Dashboard */}
                                                <div className="bg-gray-50 rounded-lg p-4">
                                                    <h4 className="font-medium text-gray-700 mb-3">Analytics Dashboard</h4>

                                                    {/* Summary Cards */}
                                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
                                                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                                                            <p className="text-sm text-blue-600 mb-1">Total Sessions</p>
                                                            <p className="text-xl font-bold text-blue-800">{analyticsData?.total_sessions || 0}</p>
                                                        </div>
                                                        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                                            <p className="text-sm text-green-600 mb-1">Active Sessions</p>
                                                            <p className="text-xl font-bold text-green-800">{analyticsData?.active_sessions || 0}</p>
                                                        </div>
                                                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                                                            <p className="text-sm text-purple-600 mb-1">Total Messages</p>
                                                            <p className="text-xl font-bold text-purple-800">{analyticsData?.total_messages || 0}</p>
                                                        </div>
                                                    </div>

                                                    {/* Detailed Metrics */}
                                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                        <div className="bg-white rounded-lg p-3">
                                                            <p className="text-sm text-gray-600 mb-1">Avg Session Duration</p>
                                                            <p className="font-medium text-gray-900">{analyticsData?.avg_session_duration ? analyticsData.avg_session_duration.toFixed(1) + ' seconds' : 'N/A'}</p>
                                                        </div>
                                                        <div className="bg-white rounded-lg p-3">
                                                            <p className="text-sm text-gray-600 mb-1">User Satisfaction</p>
                                                            <p className="font-medium text-gray-900">{analyticsData?.user_satisfaction ? analyticsData.user_satisfaction.toFixed(1) + '%' : 'N/A'}</p>
                                                        </div>
                                                        <div className="bg-white rounded-lg p-3">
                                                            <p className="text-sm text-gray-600 mb-1">Daily Active Users</p>
                                                            <p className="font-medium text-gray-900">{analyticsData?.daily_active_users || 0}</p>
                                                        </div>
                                                        <div className="bg-white rounded-lg p-3">
                                                            <p className="text-sm text-gray-600 mb-1">Weekly Active Users</p>
                                                            <p className="font-medium text-gray-900">{analyticsData?.weekly_active_users || 0}</p>
                                                        </div>
                                                    </div>

                                                    {/* Usage Trends */}
                                                    <div className="mt-4 bg-white rounded-lg p-3">
                                                        <h5 className="font-medium text-gray-700 mb-2">Usage Trends</h5>
                                                        <div className="h-32 bg-gray-50 rounded border border-gray-200 flex items-center justify-center">
                                                            <p className="text-gray-500 text-sm">Usage chart would display here</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {/* Custom Code */}
                                    <div className="mb-6">
                                        <h4 className="font-medium text-gray-700 mb-3">Custom Code</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Custom CSS</label>
                                                <textarea
                                                    value={config.custom_css || ''}
                                                    onChange={(e) => handleConfigChange('', 'custom_css', e.target.value)}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md font-mono text-sm"
                                                    rows={4}
                                                    placeholder=".chronos-webchat { /* your custom CSS */ }"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Custom JavaScript</label>
                                                <textarea
                                                    value={config.custom_js || ''}
                                                    onChange={(e) => handleConfigChange('', 'custom_js', e.target.value)}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md font-mono text-sm"
                                                    rows={4}
                                                    placeholder="// your custom JavaScript"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'sessions' && (
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Sessions</h3>
                                    <p className="text-gray-600 mb-6">Manage and monitor active WebChat sessions</p>

                                    {/* Sessions Table */}
                                    <div className="overflow-x-auto">
                                        <table className="w-full">
                                            <thead className="bg-gray-50">
                                                <tr>
                                                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Session ID</th>
                                                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">User ID</th>
                                                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Status</th>
                                                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Created</th>
                                                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Messages</th>
                                                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {sessions.map(session => (
                                                    <tr key={session.session_id} className="border-t border-gray-100">
                                                        <td className="px-4 py-3 font-medium text-gray-900">{session.session_id}</td>
                                                        <td className="px-4 py-3">{session.user_id}</td>
                                                        <td className="px-4 py-3">
                                                            <span className={`text-xs px-2 py-1 rounded-full ${session.status === 'active' ? 'bg-green-100 text-green-600' : 'bg-yellow-100 text-yellow-600'}`}>
                                                                {session.status}
                                                            </span>
                                                        </td>
                                                        <td className="px-4 py-3">{new Date(session.created_at).toLocaleString()}</td>
                                                        <td className="px-4 py-3">{session.message_count}</td>
                                                        <td className="px-4 py-3">
                                                            <button
                                                                onClick={() => navigate(`/webchat/sessions/${session.session_id}`)}
                                                                className="text-blue-600 hover:text-blue-800 text-sm mr-2"
                                                            >
                                                                View
                                                            </button>
                                                            <button
                                                                onClick={() => alert('Session management functionality would be implemented here')}
                                                                className="text-red-600 hover:text-red-800 text-sm"
                                                            >
                                                                End
                                                            </button>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>

                                    {/* Session Analytics */}
                                    <div className="mt-6 bg-gray-50 rounded-lg p-4">
                                        <h4 className="font-medium text-gray-700 mb-3">Session Analytics</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div className="bg-white rounded-lg p-3">
                                                <p className="text-sm text-gray-600 mb-1">Total Active Sessions</p>
                                                <p className="text-2xl font-bold text-gray-900">{sessions.filter(s => s.status === 'active').length}</p>
                                            </div>
                                            <div className="bg-white rounded-lg p-3">
                                                <p className="text-sm text-gray-600 mb-1">Total Messages</p>
                                                <p className="text-2xl font-bold text-gray-900">{sessions.reduce((sum, session) => sum + session.message_count, 0)}</p>
                                            </div>
                                            <div className="bg-white rounded-lg p-3">
                                                <p className="text-sm text-gray-600 mb-1">Avg Messages per Session</p>
                                                <p className="text-2xl font-bold text-gray-900">
                                                    {(sessions.reduce((sum, session) => sum + session.message_count, 0) / Math.max(sessions.length, 1)).toFixed(1)}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'embed' && (
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Embed Code Generator</h3>
                                    <p className="text-gray-600 mb-6">Generate embed code for your WebChat configuration</p>

                                    {/* Embed Options */}
                                    <div className="mb-6 bg-gray-50 rounded-lg p-4">
                                        <h4 className="font-medium text-gray-700 mb-3">Embed Options</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Embed Type</label>
                                                <select
                                                    value={config.embed_type}
                                                    onChange={(e) => handleConfigChange('', 'embed_type', e.target.value)}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                                >
                                                    <option value="bubble">Bubble</option>
                                                    <option value="iframe">Iframe</option>
                                                    <option value="standalone">Standalone</option>
                                                    <option value="react">React Component</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Session ID</label>
                                                <input
                                                    type="text"
                                                    value={session_id || 'your_session_id'}
                                                    readOnly
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100"
                                                />
                                            </div>
                                        </div>

                                        <button
                                            onClick={handleGenerateEmbedCode}
                                            disabled={isGenerating}
                                            className={`mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors ${isGenerating ? 'opacity-50 cursor-not-allowed' : ''}`}
                                        >
                                            {isGenerating ? (
                                                <>
                                                    <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>
                                                    Generating...
                                                </>
                                            ) : (
                                                'Generate Embed Code'
                                            )}
                                        </button>
                                    </div>

                                    {/* Embed Code Display */}
                                    {embedCode && (
                                        <div className="mb-4">
                                            <h4 className="font-medium text-gray-700 mb-3">Generated Embed Code</h4>
                                            <div className="bg-gray-900 rounded-lg p-4 text-green-400 font-mono text-sm overflow-x-auto">
                                                <pre>{embedCode}</pre>
                                            </div>
                                            <button
                                                onClick={handleCopyEmbedCode}
                                                className="mt-3 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
                                            >
                                                Copy to Clipboard
                                            </button>
                                        </div>
                                    )}

                                    {/* Implementation Instructions */}
                                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                        <h4 className="font-medium text-blue-700 mb-3">Implementation Instructions</h4>
                                        <p className="text-blue-800 text-sm mb-2">
                                            {config.embed_type === 'bubble' && (
                                                <>Add the embed code to your website's HTML, just before the closing <code>{'<body>'}</code> tag.</>
                                            )}
                                            {config.embed_type === 'iframe' && (
                                                <>Add the iframe code to any page where you want the WebChat to appear.</>
                                            )}
                                            {config.embed_type === 'standalone' && (
                                                <>Use this iframe for a full-page WebChat experience.</>
                                            )}
                                            {config.embed_type === 'react' && (
                                                <>Install the React component package and use it in your React application.</>
                                            )}
                                        </p>
                                        <p className="text-blue-800 text-sm">
                                            The WebChat will automatically connect to your Chronos AI agent and use the configured settings.
                                        </p>
                                    </div>

                                    {/* Preview */}
                                    <div className="mt-6 bg-gray-50 rounded-lg p-4">
                                        <h4 className="font-medium text-gray-700 mb-3">Live Preview</h4>
                                        <div className="bg-white rounded border border-gray-200 p-8 text-center">
                                            <div className="text-4xl mb-2">💬</div>
                                            <p className="text-gray-600">WebChat preview based on your configuration</p>
                                            <p className="text-sm text-gray-500 mt-2">
                                                This preview shows how your WebChat will look with the current settings.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Action Buttons */}
                        <div className="border-t border-gray-200 px-6 py-4">
                            <div className="flex justify-end gap-3">
                                <button
                                    onClick={() => navigate('/communication/channels')}
                                    className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleSave}
                                    disabled={isSaving}
                                    className={`bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors ${isSaving ? 'opacity-50 cursor-not-allowed' : ''}`}
                                >
                                    {isSaving ? (
                                        <>
                                            <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>
                                            Saving...
                                        </>
                                    ) : (
                                        'Save Configuration'
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ProtectedRoute>
    );
};

export default WebChatConfigurationPage;