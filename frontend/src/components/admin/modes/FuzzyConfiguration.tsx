import { useState } from 'react'
import { Button } from '../../ui/button'
import { Input } from '../../ui/input'
import { Label } from '../../ui/label'
import { Textarea } from '../../ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card'
import { Alert, AlertDescription } from '../../ui/alert'
import { Switch } from '../../ui/switch'
import { Slider } from '../../ui/slider'
import {
    Save,
    Download,
    Upload,
    AlertCircle,
    CheckCircle2,
    Loader2,
    Info
} from 'lucide-react'
import {
    updateFuzzyConfiguration,
    exportFuzzyConfiguration,
    importFuzzyConfiguration,
    downloadConfigurationFile,
    uploadConfigurationFile
} from '../../../services/fuzzyService'
import { useModelCatalog } from '../../../hooks/useModelCatalog'
import { ModelCatalogPicker } from '../../studio/ModelCatalogPicker'
import type {
    FuzzyConfiguration as FuzzyConfigType,
    FuzzyConfigurationUpdate
} from '../../../types/fuzzy'

interface FuzzyConfigurationProps {
    configuration: FuzzyConfigType
    onUpdate: (config: FuzzyConfigType) => void
}

export const FuzzyConfiguration = ({ configuration, onUpdate }: FuzzyConfigurationProps) => {
    const [formData, setFormData] = useState<FuzzyConfigType>(configuration)
    const [saving, setSaving] = useState(false)
    const [exporting, setExporting] = useState(false)
    const [importing, setImporting] = useState(false)
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
    const { data: modelCatalog } = useModelCatalog()
    const availableProviders = (modelCatalog?.providers || []).filter(provider => provider.available)
    const chatModels = modelCatalog?.models?.chat || []
    const availableProviderIds = new Set(availableProviders.map(provider => provider.id))
    const availableChatModels = chatModels.filter(model => availableProviderIds.has(model.provider))

    const handleInputChange = (field: keyof FuzzyConfigType, value: any) => {
        setFormData(prev => ({ ...prev, [field]: value }))
    }

    const handleSave = async () => {
        try {
            setSaving(true)
            setMessage(null)

            const updateData: FuzzyConfigurationUpdate = {
                system_instructions: formData.system_instructions,
                personality: formData.personality,
                temperature: formData.temperature,
                max_tokens: formData.max_tokens,
                model: formData.model,
                provider: formData.provider,
                rate_limit_hourly: formData.rate_limit_hourly,
                rate_limit_daily: formData.rate_limit_daily,
                enabled_tools: formData.enabled_tools,
                permissions: formData.permissions,
                auto_approve_actions: formData.auto_approve_actions,
                require_confirmation: formData.require_confirmation,
                logging_level: formData.logging_level
            }

            const updated = await updateFuzzyConfiguration(updateData)
            onUpdate(updated)
            setFormData(updated)
            setMessage({ type: 'success', text: 'Configuration saved successfully!' })
        } catch (err) {
            setMessage({
                type: 'error',
                text: err instanceof Error ? err.message : 'Failed to save configuration'
            })
        } finally {
            setSaving(false)
        }
    }

    const handleExport = async () => {
        try {
            setExporting(true)
            const exportData = await exportFuzzyConfiguration()
            await downloadConfigurationFile(exportData)
            setMessage({ type: 'success', text: 'Configuration exported successfully!' })
        } catch (err) {
            setMessage({
                type: 'error',
                text: err instanceof Error ? err.message : 'Failed to export configuration'
            })
        } finally {
            setExporting(false)
        }
    }

    const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0]
        if (!file) return

        try {
            setImporting(true)
            setMessage(null)

            const importData = await uploadConfigurationFile(file)
            const updated = await importFuzzyConfiguration(importData)

            onUpdate(updated)
            setFormData(updated)
            setMessage({ type: 'success', text: 'Configuration imported successfully!' })
        } catch (err) {
            setMessage({
                type: 'error',
                text: err instanceof Error ? err.message : 'Failed to import configuration'
            })
        } finally {
            setImporting(false)
            event.target.value = '' // Reset file input
        }
    }

    return (
        <div className="space-y-6">
            {/* Action Buttons */}
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">FUZZY Configuration</h2>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleExport}
                        disabled={exporting}
                    >
                        {exporting ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                            <Download className="w-4 h-4 mr-2" />
                        )}
                        Export
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => document.getElementById('import-file')?.click()}
                        disabled={importing}
                    >
                        {importing ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                            <Upload className="w-4 h-4 mr-2" />
                        )}
                        Import
                    </Button>
                    <input
                        id="import-file"
                        type="file"
                        accept=".json"
                        className="hidden"
                        onChange={handleImport}
                        aria-label="Import configuration file"
                        title="Import configuration file"
                        role="button"
                        tabIndex={-1}
                    />
                    <Button
                        onClick={handleSave}
                        disabled={saving}
                    >
                        {saving ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                            <Save className="w-4 h-4 mr-2" />
                        )}
                        Save Changes
                    </Button>
                </div>
            </div>

            {/* Status Message */}
            {message && (
                <Alert variant={message.type === 'error' ? 'destructive' : 'default'}>
                    {message.type === 'success' ? (
                        <CheckCircle2 className="h-4 w-4" />
                    ) : (
                        <AlertCircle className="h-4 w-4" />
                    )}
                    <AlertDescription>{message.text}</AlertDescription>
                </Alert>
            )}

            {/* System Instructions */}
            <Card>
                <CardHeader>
                    <CardTitle>System Instructions</CardTitle>
                    <CardDescription>
                        Define FUZZY's core behavior and capabilities
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <Label htmlFor="system-instructions">System Instructions</Label>
                        <Textarea
                            id="system-instructions"
                            value={formData.system_instructions}
                            onChange={(e) => handleInputChange('system_instructions', e.target.value)}
                            rows={6}
                            className="mt-2"
                            placeholder="Enter system instructions for FUZZY..."
                        />
                    </div>
                    <div>
                        <Label htmlFor="personality">Personality</Label>
                        <Textarea
                            id="personality"
                            value={formData.personality}
                            onChange={(e) => handleInputChange('personality', e.target.value)}
                            rows={4}
                            className="mt-2"
                            placeholder="Define FUZZY's personality traits..."
                        />
                    </div>
                </CardContent>
            </Card>

            {/* AI Provider Settings */}
            <Card>
                <CardHeader>
                    <CardTitle>AI Provider Settings</CardTitle>
                    <CardDescription>
                        Configure the underlying AI model and parameters
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <ModelCatalogPicker
                        capability="chat"
                        providers={availableProviders}
                        models={availableChatModels}
                        value={formData.model}
                        providerId={formData.provider}
                        onProviderChange={(providerId) => handleInputChange('provider', providerId)}
                        onChange={(model) => handleInputChange('model', model)}
                        label="Provider + Model"
                        helperText="Select the AI provider and model powering FUZZY."
                    />

                    <div>
                        <Label htmlFor="temperature">
                            Temperature: {formData.temperature.toFixed(2)}
                        </Label>
                        <Slider
                            id="temperature"
                            min={0}
                            max={2}
                            step={0.1}
                            value={[formData.temperature]}
                            onValueChange={([value]) => handleInputChange('temperature', value)}
                            className="mt-2"
                        />
                        <p className="text-xs text-muted-foreground mt-1">
                            Controls randomness in responses (0 = deterministic, 2 = very creative)
                        </p>
                    </div>

                    <div>
                        <Label htmlFor="max-tokens">Max Tokens</Label>
                        <Input
                            id="max-tokens"
                            type="number"
                            value={formData.max_tokens}
                            onChange={(e) => handleInputChange('max_tokens', parseInt(e.target.value))}
                            className="mt-2"
                        />
                    </div>
                </CardContent>
            </Card>

            {/* Rate Limits */}
            <Card>
                <CardHeader>
                    <CardTitle>Rate Limits</CardTitle>
                    <CardDescription>
                        Control how many actions FUZZY can perform
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <Label htmlFor="hourly-limit">Hourly Limit</Label>
                            <Input
                                id="hourly-limit"
                                type="number"
                                value={formData.rate_limit_hourly}
                                onChange={(e) => handleInputChange('rate_limit_hourly', parseInt(e.target.value))}
                                className="mt-2"
                            />
                        </div>
                        <div>
                            <Label htmlFor="daily-limit">Daily Limit</Label>
                            <Input
                                id="daily-limit"
                                type="number"
                                value={formData.rate_limit_daily}
                                onChange={(e) => handleInputChange('rate_limit_daily', parseInt(e.target.value))}
                                className="mt-2"
                            />
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Behavior Settings */}
            <Card>
                <CardHeader>
                    <CardTitle>Behavior Settings</CardTitle>
                    <CardDescription>
                        Configure FUZZY's operational behavior
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                            <Label>Auto-Approve Actions</Label>
                            <p className="text-sm text-muted-foreground">
                                Allow FUZZY to execute actions without confirmation
                            </p>
                        </div>
                        <Switch
                            checked={formData.auto_approve_actions}
                            onCheckedChange={(checked) => handleInputChange('auto_approve_actions', checked)}
                        />
                    </div>

                    <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                            <Label>Require Confirmation</Label>
                            <p className="text-sm text-muted-foreground">
                                Require user confirmation for critical actions
                            </p>
                        </div>
                        <Switch
                            checked={formData.require_confirmation}
                            onCheckedChange={(checked) => handleInputChange('require_confirmation', checked)}
                        />
                    </div>

                    <div>
                        <Label htmlFor="logging-level">Logging Level</Label>
                        <select
                            id="logging-level"
                            value={formData.logging_level}
                            onChange={(e) => handleInputChange('logging_level', e.target.value)}
                            className="mt-2 w-full px-3 py-2 border border-input rounded-md bg-background"
                            aria-label="Logging Level"
                        >
                            <option value="debug">Debug</option>
                            <option value="info">Info</option>
                            <option value="warning">Warning</option>
                            <option value="error">Error</option>
                        </select>
                    </div>
                </CardContent>
            </Card>

            {/* Info Alert */}
            <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                    Changes to FUZZY configuration will take effect immediately. Make sure to test
                    the configuration after making changes.
                </AlertDescription>
            </Alert>
        </div>
    )
}
