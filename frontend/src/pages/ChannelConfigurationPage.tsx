import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ChannelConfig, TelegramConfig, SlackConfig, WhatsAppConfig, DiscordConfig, WebChatConfig } from '../types/channel';

const ChannelConfigurationPage: React.FC = () => {
    const { channelType } = useParams<{ channelType: string }>();
    const { user } = useAuth();
    const navigate = useNavigate();
    const [config, setConfig] = useState<ChannelConfig | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isSaving, setIsSaving] = useState(false);

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }

        const fetchConfig = async () => {
            try {
                setIsLoading(true);
                const response = await fetch(`/api/communication-channels/config/${channelType}`, {
                    headers: {
                        'Authorization': `Bearer ${user.token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch configuration');
                }

                const data = await response.json();
                setConfig(data);
                setError(null);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load configuration');
                console.error('Error fetching config:', err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchConfig();
    }, [user, channelType, navigate]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;

        if (!config) return;

        if (type === 'checkbox') {
            const checked = (e.target as HTMLInputElement).checked;
            setConfig({ ...config, [name]: checked });
        } else {
            setConfig({ ...config, [name]: value });
        }
    };

    const handleNestedInputChange = (section: string, field: string, value: string | boolean) => {
        if (!config) return;

        setConfig({
            ...config,
            [section]: {
                ...config[section as keyof ChannelConfig] as Record<string, any>,
                [field]: value
            }
        });
    };

    const handleSave = async () => {
        if (!config || !user) return;

        try {
            setIsSaving(true);
            setError(null);

            const response = await fetch(`/api/communication-channels/config/${channelType}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });

            if (!response.ok) {
                throw new Error('Failed to save configuration');
            }

            // Show success message
            setError(null);
            alert('Configuration saved successfully!');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to save configuration');
            console.error('Error saving config:', err);
        } finally {
            setIsSaving(false);
        }
    };

    const renderTelegramConfig = () => {
        if (!config || !('telegram' in config)) return null;
        const telegramConfig = config.telegram as TelegramConfig;

        return (
            <div className="space-y-4">
                <h3 className="text-xl font-semibold text-cyan-300">Telegram Configuration</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label htmlFor="telegram-botToken" className="block text-sm font-medium text-muted-foreground mb-1">Bot Token</label>
                        <input
                            id="telegram-botToken"
                            type="password"
                            name="botToken"
                            value={telegramConfig.botToken || ''}
                            onChange={(e) => handleNestedInputChange('telegram', 'botToken', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter Telegram bot token"
                            aria-describedby="telegram-botToken-help"
                            aria-required="true"
                            required
                            aria-invalid={!telegramConfig.botToken}
                        />
                        <p id="telegram-botToken-help" className="text-xs text-muted-foreground mt-1">Your Telegram bot token from BotFather</p>
                    </div>

                    <div>
                        <label htmlFor="telegram-webhookUrl" className="block text-sm font-medium text-muted-foreground mb-1">Webhook URL</label>
                        <input
                            id="telegram-webhookUrl"
                            type="url"
                            name="webhookUrl"
                            value={telegramConfig.webhookUrl || ''}
                            onChange={(e) => handleNestedInputChange('telegram', 'webhookUrl', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="https://your-domain.com/webhook/telegram"
                            aria-describedby="telegram-webhookUrl-help"
                        />
                        <p id="telegram-webhookUrl-help" className="text-xs text-muted-foreground mt-1">URL where Telegram will send updates</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Welcome Message</label>
                        <textarea
                            name="welcomeMessage"
                            value={telegramConfig.welcomeMessage || ''}
                            onChange={(e) => handleNestedInputChange('telegram', 'welcomeMessage', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 h-20"
                            placeholder="Welcome to our bot! How can I help you?"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Help Command Response</label>
                        <textarea
                            name="helpMessage"
                            value={telegramConfig.helpMessage || ''}
                            onChange={(e) => handleNestedInputChange('telegram', 'helpMessage', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 h-20"
                            placeholder="Available commands: /start, /help, /settings"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Enable Inline Keyboards</label>
                        <select
                            name="enableInlineKeyboards"
                            value={telegramConfig.enableInlineKeyboards ? 'true' : 'false'}
                            onChange={(e) => handleNestedInputChange('telegram', 'enableInlineKeyboards', e.target.value === 'true')}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="true">Yes</option>
                            <option value="false">No</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Enable File Uploads</label>
                        <select
                            name="enableFileUploads"
                            value={telegramConfig.enableFileUploads ? 'true' : 'false'}
                            onChange={(e) => handleNestedInputChange('telegram', 'enableFileUploads', e.target.value === 'true')}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="true">Yes</option>
                            <option value="false">No</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Max File Size (MB)</label>
                        <input
                            type="number"
                            name="maxFileSize"
                            value={telegramConfig.maxFileSize || 20}
                            onChange={(e) => handleNestedInputChange('telegram', 'maxFileSize', parseInt(e.target.value))}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            min="1"
                            max="50"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Allowed File Types</label>
                        <input
                            type="text"
                            name="allowedFileTypes"
                            value={telegramConfig.allowedFileTypes?.join(', ') || 'jpg,png,gif,pdf,doc,docx'}
                            onChange={(e) => handleNestedInputChange('telegram', 'allowedFileTypes', e.target.value.split(',').map(item => item.trim()))}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="jpg,png,gif,pdf,doc,docx"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Rate Limit (messages/min)</label>
                        <input
                            type="number"
                            name="rateLimit"
                            value={telegramConfig.rateLimit || 30}
                            onChange={(e) => handleNestedInputChange('telegram', 'rateLimit', parseInt(e.target.value))}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            min="1"
                            max="100"
                        />
                    </div>
                </div>
            </div>
        );
    };

    const renderSlackConfig = () => {
        if (!config || !('slack' in config)) return null;
        const slackConfig = config.slack as SlackConfig;

        return (
            <div className="space-y-4">
                <h3 className="text-xl font-semibold text-emerald-300">Slack Configuration</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Client ID</label>
                        <input
                            type="text"
                            name="clientId"
                            value={slackConfig.clientId || ''}
                            onChange={(e) => handleNestedInputChange('slack', 'clientId', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                            placeholder="Enter Slack client ID"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Client Secret</label>
                        <input
                            type="password"
                            name="clientSecret"
                            value={slackConfig.clientSecret || ''}
                            onChange={(e) => handleNestedInputChange('slack', 'clientSecret', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                            placeholder="Enter Slack client secret"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Signing Secret</label>
                        <input
                            type="password"
                            name="signingSecret"
                            value={slackConfig.signingSecret || ''}
                            onChange={(e) => handleNestedInputChange('slack', 'signingSecret', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                            placeholder="Enter Slack signing secret"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Redirect URI</label>
                        <input
                            type="url"
                            name="redirectUri"
                            value={slackConfig.redirectUri || ''}
                            onChange={(e) => handleNestedInputChange('slack', 'redirectUri', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                            placeholder="https://your-domain.com/auth/slack/callback"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Default Channel</label>
                        <input
                            type="text"
                            name="defaultChannel"
                            value={slackConfig.defaultChannel || ''}
                            onChange={(e) => handleNestedInputChange('slack', 'defaultChannel', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                            placeholder="#general"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Bot Username</label>
                        <input
                            type="text"
                            name="botUsername"
                            value={slackConfig.botUsername || ''}
                            onChange={(e) => handleNestedInputChange('slack', 'botUsername', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                            placeholder="ChronosBot"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Enable Slash Commands</label>
                        <select
                            name="enableSlashCommands"
                            value={slackConfig.enableSlashCommands ? 'true' : 'false'}
                            onChange={(e) => handleNestedInputChange('slack', 'enableSlashCommands', e.target.value === 'true')}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        >
                            <option value="true">Yes</option>
                            <option value="false">No</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Enable Interactive Messages</label>
                        <select
                            name="enableInteractiveMessages"
                            value={slackConfig.enableInteractiveMessages ? 'true' : 'false'}
                            onChange={(e) => handleNestedInputChange('slack', 'enableInteractiveMessages', e.target.value === 'true')}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        >
                            <option value="true">Yes</option>
                            <option value="false">No</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Enable File Uploads</label>
                        <select
                            name="enableFileUploads"
                            value={slackConfig.enableFileUploads ? 'true' : 'false'}
                            onChange={(e) => handleNestedInputChange('slack', 'enableFileUploads', e.target.value === 'true')}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        >
                            <option value="true">Yes</option>
                            <option value="false">No</option>
                        </select>
                    </div>
                </div>
            </div>
        );
    };

    const renderWhatsAppConfig = () => {
        if (!config || !('whatsapp' in config)) return null;
        const whatsappConfig = config.whatsapp as WhatsAppConfig;

        return (
            <div className="space-y-4">
                <h3 className="text-xl font-semibold text-green-500">WhatsApp Business API Configuration</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Business Account ID</label>
                        <input
                            type="text"
                            name="businessAccountId"
                            value={whatsappConfig.businessAccountId || ''}
                            onChange={(e) => handleNestedInputChange('whatsapp', 'businessAccountId', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                            placeholder="Enter WhatsApp Business Account ID"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">API Key</label>
                        <input
                            type="password"
                            name="apiKey"
                            value={whatsappConfig.apiKey || ''}
                            onChange={(e) => handleNestedInputChange('whatsapp', 'apiKey', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                            placeholder="Enter WhatsApp API Key"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Phone Number ID</label>
                        <input
                            type="text"
                            name="phoneNumberId"
                            value={whatsappConfig.phoneNumberId || ''}
                            onChange={(e) => handleNestedInputChange('whatsapp', 'phoneNumberId', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                            placeholder="Enter Phone Number ID"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Webhook Verify Token</label>
                        <input
                            type="password"
                            name="webhookVerifyToken"
                            value={whatsappConfig.webhookVerifyToken || ''}
                            onChange={(e) => handleNestedInputChange('whatsapp', 'webhookVerifyToken', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                            placeholder="Enter webhook verify token"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Welcome Message Template</label>
                        <textarea
                            name="welcomeTemplate"
                            value={whatsappConfig.welcomeTemplate || ''}
                            onChange={(e) => handleNestedInputChange('whatsapp', 'welcomeTemplate', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 h-20"
                            placeholder="Hello {{1}}! Welcome to our service. How can we help you today?"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Default Template</label>
                        <textarea
                            name="defaultTemplate"
                            value={whatsappConfig.defaultTemplate || ''}
                            onChange={(e) => handleNestedInputChange('whatsapp', 'defaultTemplate', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 h-20"
                            placeholder="Thank you for your message. We'll get back to you soon!"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Enable Template Messages</label>
                        <select
                            name="enableTemplateMessages"
                            value={whatsappConfig.enableTemplateMessages ? 'true' : 'false'}
                            onChange={(e) => handleNestedInputChange('whatsapp', 'enableTemplateMessages', e.target.value === 'true')}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        >
                            <option value="true">Yes</option>
                            <option value="false">No</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Enable Media Messages</label>
                        <select
                            name="enableMediaMessages"
                            value={whatsappConfig.enableMediaMessages ? 'true' : 'false'}
                            onChange={(e) => handleNestedInputChange('whatsapp', 'enableMediaMessages', e.target.value === 'true')}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                        >
                            <option value="true">Yes</option>
                            <option value="false">No</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Max Media Size (MB)</label>
                        <input
                            type="number"
                            name="maxMediaSize"
                            value={whatsappConfig.maxMediaSize || 16}
                            onChange={(e) => handleNestedInputChange('whatsapp', 'maxMediaSize', parseInt(e.target.value))}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                            min="1"
                            max="100"
                        />
                    </div>
                </div>
            </div>
        );
    };

    const renderDiscordConfig = () => {
        if (!config || !('discord' in config)) return null;
        const discordConfig = config.discord as DiscordConfig;

        return (
            <div className="space-y-4">
                <h3 className="text-xl font-semibold text-purple-600">Discord Configuration</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Bot Token</label>
                        <input
                            type="password"
                            name="botToken"
                            value={discordConfig.botToken || ''}
                            onChange={(e) => handleNestedInputChange('discord', 'botToken', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                            placeholder="Enter Discord bot token"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Client ID</label>
                        <input
                            type="text"
                            name="clientId"
                            value={discordConfig.clientId || ''}
                            onChange={(e) => handleNestedInputChange('discord', 'clientId', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                            placeholder="Enter Discord client ID"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Client Secret</label>
                        <input
                            type="password"
                            name="clientSecret"
                            value={discordConfig.clientSecret || ''}
                            onChange={(e) => handleNestedInputChange('discord', 'clientSecret', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                            placeholder="Enter Discord client secret"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Redirect URI</label>
                        <input
                            type="url"
                            name="redirectUri"
                            value={discordConfig.redirectUri || ''}
                            onChange={(e) => handleNestedInputChange('discord', 'redirectUri', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                            placeholder="https://your-domain.com/auth/discord/callback"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Default Command Prefix</label>
                        <input
                            type="text"
                            name="commandPrefix"
                            value={discordConfig.commandPrefix || '!'}
                            onChange={(e) => handleNestedInputChange('discord', 'commandPrefix', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                            placeholder="!"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Bot Status</label>
                        <input
                            type="text"
                            name="botStatus"
                            value={discordConfig.botStatus || 'Online'}
                            onChange={(e) => handleNestedInputChange('discord', 'botStatus', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                            placeholder="Online"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Enable Embed Support</label>
                        <select
                            name="enableEmbedSupport"
                            value={discordConfig.enableEmbedSupport ? 'true' : 'false'}
                            onChange={(e) => handleNestedInputChange('discord', 'enableEmbedSupport', e.target.value === 'true')}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                            <option value="true">Yes</option>
                            <option value="false">No</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Enable File Uploads</label>
                        <select
                            name="enableFileUploads"
                            value={discordConfig.enableFileUploads ? 'true' : 'false'}
                            onChange={(e) => handleNestedInputChange('discord', 'enableFileUploads', e.target.value === 'true')}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                            <option value="true">Yes</option>
                            <option value="false">No</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Max File Size (MB)</label>
                        <input
                            type="number"
                            name="maxFileSize"
                            value={discordConfig.maxFileSize || 8}
                            onChange={(e) => handleNestedInputChange('discord', 'maxFileSize', parseInt(e.target.value))}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                            min="1"
                            max="100"
                        />
                    </div>
                </div>
            </div>
        );
    };

    const renderWebChatConfig = () => {
        if (!config || !('webchat' in config)) return null;
        const webchatConfig = config.webchat as WebChatConfig;

        return (
            <div className="space-y-4">
                <h3 className="text-xl font-semibold text-indigo-600">WebChat Configuration</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Embed Type</label>
                        <select
                            name="embedType"
                            value={webchatConfig.embedType || 'bubble'}
                            onChange={(e) => handleNestedInputChange('webchat', 'embedType', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        >
                            <option value="bubble">Bubble</option>
                            <option value="iframe">Iframe</option>
                            <option value="standalone">Standalone</option>
                            <option value="react">React Component</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Theme</label>
                        <select
                            name="theme"
                            value={webchatConfig.theme || 'light'}
                            onChange={(e) => handleNestedInputChange('webchat', 'theme', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        >
                            <option value="light">Light</option>
                            <option value="dark">Dark</option>
                            <option value="system">System</option>
                        </select>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Primary Color</label>
                        <input
                            type="color"
                            name="primaryColor"
                            value={webchatConfig.primaryColor || '#3B82F6'}
                            onChange={(e) => handleNestedInputChange('webchat', 'primaryColor', e.target.value)}
                            className="w-full h-10 px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Secondary Color</label>
                        <input
                            type="color"
                            name="secondaryColor"
                            value={webchatConfig.secondaryColor || '#1E40AF'}
                            onChange={(e) => handleNestedInputChange('webchat', 'secondaryColor', e.target.value)}
                            className="w-full h-10 px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Welcome Message</label>
                        <textarea
                            name="welcomeMessage"
                            value={webchatConfig.welcomeMessage || 'Hello! How can I help you today?'}
                            onChange={(e) => handleNestedInputChange('webchat', 'welcomeMessage', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 h-20"
                            placeholder="Hello! How can I help you today?"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Placeholder Text</label>
                        <input
                            type="text"
                            name="placeholderText"
                            value={webchatConfig.placeholderText || 'Type your message...'}
                            onChange={(e) => handleNestedInputChange('webchat', 'placeholderText', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            placeholder="Type your message..."
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Enable Voice Input</label>
                        <select
                            name="enableVoiceInput"
                            value={webchatConfig.enableVoiceInput ? 'true' : 'false'}
                            onChange={(e) => handleNestedInputChange('webchat', 'enableVoiceInput', e.target.value === 'true')}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        >
                            <option value="true">Yes</option>
                            <option value="false">No</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Enable Voice Output</label>
                        <select
                            name="enableVoiceOutput"
                            value={webchatConfig.enableVoiceOutput ? 'true' : 'false'}
                            onChange={(e) => handleNestedInputChange('webchat', 'enableVoiceOutput', e.target.value === 'true')}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        >
                            <option value="true">Yes</option>
                            <option value="false">No</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Enable User Feedback</label>
                        <select
                            name="enableUserFeedback"
                            value={webchatConfig.enableUserFeedback ? 'true' : 'false'}
                            onChange={(e) => handleNestedInputChange('webchat', 'enableUserFeedback', e.target.value === 'true')}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        >
                            <option value="true">Yes</option>
                            <option value="false">No</option>
                        </select>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Custom CSS URL</label>
                        <input
                            type="url"
                            name="customCssUrl"
                            value={webchatConfig.customCssUrl || ''}
                            onChange={(e) => handleNestedInputChange('webchat', 'customCssUrl', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            placeholder="https://your-domain.com/webchat.css"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">Custom JS URL</label>
                        <input
                            type="url"
                            name="customJsUrl"
                            value={webchatConfig.customJsUrl || ''}
                            onChange={(e) => handleNestedInputChange('webchat', 'customJsUrl', e.target.value)}
                            className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            placeholder="https://your-domain.com/webchat.js"
                        />
                    </div>
                </div>
            </div>
        );
    };

    const renderConfigForm = () => {
        if (!config) return null;

        switch (channelType) {
            case 'telegram':
                return renderTelegramConfig();
            case 'slack':
                return renderSlackConfig();
            case 'whatsapp':
                return renderWhatsAppConfig();
            case 'discord':
                return renderDiscordConfig();
            case 'webchat':
                return renderWebChatConfig();
            default:
                return <div role="alert" aria-live="assertive">Unknown channel type: {channelType}</div>;
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="max-w-4xl mx-auto p-6">
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                    <strong className="font-bold">Error!</strong>
                    <span className="block sm:inline"> {error}</span>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-foreground capitalize">{channelType} Configuration</h1>
                    <p className="text-muted-foreground">Configure your {channelType} communication channel settings</p>
                </div>

                <div className="flex space-x-2">
                    <button
                        onClick={() => navigate('/app/channels')}
                        className="px-4 py-2 bg-gray-100 text-muted-foreground rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                    >
                        Cancel
                    </button>

                    <button
                        onClick={handleSave}
                        disabled={isSaving}
                        className={`px-4 py-2 text-white rounded-md focus:outline-none focus:ring-2 ${isSaving ? 'bg-blue-400 cursor-not-allowed' : 'bg-cyan-400 hover:bg-cyan-300 focus:ring-blue-500'}`}
                    >
                        {isSaving ? (
                            <>
                                <span className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white inline-block mr-2"></span>
                                Saving...
                            </>
                        ) : (
                            'Save Configuration'
                        )}
                    </button>
                </div>
            </div>

            <div className="bg-card shadow-sm rounded-lg p-6">
                {renderConfigForm()}
            </div>

            <div className="mt-6">
                <div className="bg-cyan-500/10 border-l-4 border-blue-500 p-4">
                    <div className="flex">
                        <div className="flex-shrink-0">
                            <svg className="h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <div className="ml-3">
                            <p className="text-sm text-blue-700">
                                Remember to save your configuration before testing the channel. You can test your configuration on the <a href="/communication-channels/test" className="font-medium underline">test page</a>.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChannelConfigurationPage;
