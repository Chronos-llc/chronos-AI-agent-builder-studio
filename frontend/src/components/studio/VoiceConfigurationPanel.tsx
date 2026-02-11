import React, { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ChevronDown, RefreshCw, Save } from 'lucide-react'
import { useModelCatalog } from '../../hooks/useModelCatalog'
import { ModelCatalogPicker } from './ModelCatalogPicker'
import { ProviderLogo } from '../brand/ProviderLogo'
import { phoneProviders } from '../../config/iconRegistry'
import { useAgentPhoneNumbers } from '../../hooks/useAgentPhoneNumbers'
import type { PhoneNumberProvider } from '../../services/phoneNumberService'

type VoiceProvider =
  | 'OPENAI'
  | 'ELEVENLABS'
  | 'CARTESIA'
  | 'GOOGLE'
  | 'AZURE'
  | 'AWS'
  | 'DEEPGRAM'
  | 'ASSEMBLYAI'

type VoiceGender = 'MALE' | 'FEMALE' | 'NEUTRAL'
type AudioFormat = 'MP3' | 'WAV' | 'OGG' | 'WEBM' | 'FLAC'
type PhoneProviderType = PhoneNumberProvider

interface VoiceConfig {
  id?: number
  agent_id?: number
  user_id?: number
  voice_enabled: boolean
  stt_provider: VoiceProvider
  stt_model?: string | null
  stt_language: string
  tts_provider: VoiceProvider
  tts_model?: string | null
  tts_voice?: string | null
  tts_voice_gender: VoiceGender
  tts_speed: number
  tts_pitch: number
  audio_format: AudioFormat
  sample_rate: number
  bit_rate: number
  noise_reduction: boolean
  echo_cancellation: boolean
  auto_gain_control: boolean
  voice_activity_detection: boolean
  allow_interruption: boolean
  interruption_threshold: number
  selected_phone_number_id?: number | null
  phone_provider_preference?: PhoneProviderType | null
}

const providerIdFromEnum: Record<VoiceProvider, string> = {
  OPENAI: 'openai',
  ELEVENLABS: 'elevenlabs',
  CARTESIA: 'cartesia',
  GOOGLE: 'google',
  AZURE: 'azure',
  AWS: 'aws',
  DEEPGRAM: 'deepgram',
  ASSEMBLYAI: 'assemblyai',
}

const providerEnumFromId = Object.entries(providerIdFromEnum).reduce(
  (acc, [key, value]) => {
    acc[value] = key as VoiceProvider
    return acc
  },
  {} as Record<string, VoiceProvider>
)

const defaultConfig: VoiceConfig = {
  voice_enabled: true,
  stt_provider: 'OPENAI',
  stt_model: '',
  stt_language: 'en',
  tts_provider: 'OPENAI',
  tts_model: '',
  tts_voice: '',
  tts_voice_gender: 'NEUTRAL',
  tts_speed: 1.0,
  tts_pitch: 1.0,
  audio_format: 'MP3',
  sample_rate: 24000,
  bit_rate: 128,
  noise_reduction: true,
  echo_cancellation: true,
  auto_gain_control: true,
  voice_activity_detection: true,
  allow_interruption: true,
  interruption_threshold: 0.5,
  selected_phone_number_id: null,
  phone_provider_preference: null,
}

const Section: React.FC<{
  title: string
  description?: string
  children: React.ReactNode
}> = ({ title, description, children }) => {
  const [open, setOpen] = useState(true)
  return (
    <div className="rounded-2xl border border-border bg-card/60 backdrop-blur">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-4 text-left"
      >
        <div>
          <h3 className="text-base font-semibold text-foreground">{title}</h3>
          {description && <p className="text-xs text-muted-foreground mt-1">{description}</p>}
        </div>
        <ChevronDown
          className={`h-4 w-4 text-muted-foreground transition-transform ${open ? 'rotate-180' : ''}`}
        />
      </button>
      {open && <div className="px-5 pb-5 space-y-4">{children}</div>}
    </div>
  )
}

export const VoiceConfigurationPanel: React.FC<{ agentId: number }> = ({ agentId }) => {
  const queryClient = useQueryClient()
  const { data: modelCatalog } = useModelCatalog()
  const sttModels = modelCatalog?.models?.stt || []
  const ttsModels = modelCatalog?.models?.tts || []
  const voiceModels = modelCatalog?.models?.voice || []
  const {
    providers: phoneProviderAvailability,
    searchResults,
    ownedNumbers,
    search,
    searching,
    purchase,
    purchasing,
    selectNumber,
    selecting,
  } = useAgentPhoneNumbers(agentId)
  const [phoneProvider, setPhoneProvider] = useState<PhoneProviderType>('twilio')
  const [phoneCountryCode, setPhoneCountryCode] = useState('US')
  const [phoneContains, setPhoneContains] = useState('')
  const [phoneCapabilities, setPhoneCapabilities] = useState<string[]>(['voice'])
  const [confirmPurchase, setConfirmPurchase] = useState(false)
  const [phoneActionError, setPhoneActionError] = useState<string | null>(null)

  const { data, isLoading } = useQuery<VoiceConfig>({
    queryKey: ['voice-config', agentId],
    queryFn: async () => {
      const response = await fetch(`/api/v1/agents/${agentId}/voice-config`)
      if (!response.ok) throw new Error('Failed to load voice configuration')
      return response.json()
    },
  })

  const [config, setConfig] = useState<VoiceConfig>(defaultConfig)

  useEffect(() => {
    if (data) {
      setConfig({ ...defaultConfig, ...data })
      if (data.phone_provider_preference) {
        setPhoneProvider(data.phone_provider_preference)
      }
    }
  }, [data])

  const updateMutation = useMutation({
    mutationFn: async (payload: VoiceConfig) => {
      const response = await fetch(`/api/v1/agents/${agentId}/voice-config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!response.ok) throw new Error('Failed to save voice configuration')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['voice-config', agentId] })
    },
  })

  const resetMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`/api/v1/agents/${agentId}/voice-config/reset`, {
        method: 'POST',
      })
      if (!response.ok) throw new Error('Failed to reset voice configuration')
      return response.json()
    },
    onSuccess: (payload) => {
      setConfig({ ...defaultConfig, ...payload })
      queryClient.invalidateQueries({ queryKey: ['voice-config', agentId] })
    },
  })

  const sttProviderId = providerIdFromEnum[config.stt_provider] || ''
  const ttsProviderId = providerIdFromEnum[config.tts_provider] || ''
  const firstTtsModelForProvider = useMemo(() => {
    return (providerId: string) =>
      ttsModels.find(model => model.provider === providerId)?.model || ''
  }, [ttsModels])
  const firstVoiceForProvider = useMemo(() => {
    return (providerId: string) =>
      voiceModels.find(voice => voice.provider === providerId)?.model || ''
  }, [voiceModels])
  const configuredPhoneProviders = useMemo(
    () =>
      phoneProviderAvailability.reduce<Record<string, { configured: boolean; message?: string | null }>>(
        (acc, item) => {
          acc[item.provider] = { configured: item.configured, message: item.message }
          return acc
        },
        {}
      ),
    [phoneProviderAvailability]
  )

  const togglePhoneCapability = (capability: string) => {
    setPhoneCapabilities(prev =>
      prev.includes(capability) ? prev.filter(item => item !== capability) : [...prev, capability]
    )
  }

  const handleSearchPhoneNumbers = async () => {
    setPhoneActionError(null)
    try {
      await search({
        provider: phoneProvider,
        payload: {
          country_code: phoneCountryCode,
          capabilities: phoneCapabilities.length ? phoneCapabilities : ['voice'],
          limit: 20,
          contains: phoneContains || undefined,
        },
      })
    } catch (error: any) {
      setPhoneActionError(error?.message || 'Failed to search phone numbers')
    }
  }

  const handlePurchasePhoneNumber = async (
    provider: PhoneProviderType,
    phoneNumber: string,
    providerNumberId: string,
    capabilities: string[],
    countryCode?: string | null
  ) => {
    setPhoneActionError(null)
    try {
      const purchased = await purchase({
        provider,
        payload: {
          country_code: (countryCode || phoneCountryCode).toUpperCase(),
          phone_number_e164: phoneNumber,
          provider_number_id: providerNumberId,
          capabilities: capabilities.length ? capabilities : ['voice'],
          confirm_purchase: confirmPurchase,
        },
      })
      setConfig(prev => ({
        ...prev,
        selected_phone_number_id: purchased.id,
        phone_provider_preference: purchased.provider,
      }))
      setConfirmPurchase(false)
    } catch (error: any) {
      setPhoneActionError(error?.message || 'Failed to purchase phone number')
    }
  }

  const handleSelectPhoneNumber = async (numberId: number, provider: PhoneProviderType) => {
    setPhoneActionError(null)
    try {
      const selected = await selectNumber({ numberId })
      setConfig(prev => ({
        ...prev,
        selected_phone_number_id: selected.id,
        phone_provider_preference: provider,
      }))
    } catch (error: any) {
      setPhoneActionError(error?.message || 'Failed to select phone number')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
        <span className="ml-3 text-muted-foreground">Loading voice configuration...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-foreground">Voice Configuration</h2>
          <p className="text-sm text-muted-foreground">
            Configure STT, TTS, and voice settings for your assistant.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => resetMutation.mutate()}
            className="inline-flex items-center gap-2 rounded-full border border-border px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:border-muted-foreground transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            Reset
          </button>
          <button
            type="button"
            onClick={() => updateMutation.mutate(config)}
            className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            <Save className="h-4 w-4" />
            Save Voice Settings
          </button>
        </div>
      </div>

      <div className="grid gap-6">
        <Section
          title="Voice Engine"
          description="Pick your speech output model and voice. Provider icons are placeholders for now."
        >
          <label className="flex items-center gap-3 text-sm text-muted-foreground">
            <input
              type="checkbox"
              checked={config.voice_enabled}
              onChange={(e) => setConfig(prev => ({ ...prev, voice_enabled: e.target.checked }))}
              className="rounded border-border text-primary focus:ring-primary"
            />
            Enable voice features for this agent.
          </label>

          <ModelCatalogPicker
            capability="tts"
            providers={modelCatalog?.providers || []}
            models={ttsModels}
            value={config.tts_model || ''}
            providerId={ttsProviderId}
            onProviderChange={(providerId) => {
              const provider = providerEnumFromId[providerId] || 'OPENAI'
              setConfig(prev => ({
                ...prev,
                tts_provider: provider,
                tts_voice: firstVoiceForProvider(providerId),
              }))
            }}
            onChange={(model) => setConfig(prev => ({ ...prev, tts_model: model }))}
            label="TTS Provider + Model"
          />

          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <ModelCatalogPicker
              capability="voice"
              providers={modelCatalog?.providers || []}
              models={voiceModels}
              value={config.tts_voice || ''}
              providerId={ttsProviderId}
              onProviderChange={(providerId) => {
                const provider = providerEnumFromId[providerId] || 'OPENAI'
                setConfig(prev => ({
                  ...prev,
                  tts_provider: provider,
                  tts_model: firstTtsModelForProvider(providerId),
                }))
              }}
              onChange={(voice) => setConfig(prev => ({ ...prev, tts_voice: voice }))}
              label="Voice Selection"
            />
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Voice Gender</label>
              <select
                value={config.tts_voice_gender}
                onChange={(e) => setConfig(prev => ({ ...prev, tts_voice_gender: e.target.value as VoiceGender }))}
                className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground focus:ring-2 focus:ring-primary/60"
              >
                <option value="NEUTRAL">Neutral</option>
                <option value="FEMALE">Female</option>
                <option value="MALE">Male</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <div>
              <label className="text-sm font-medium text-foreground">Speed: {config.tts_speed.toFixed(1)}x</label>
              <input
                type="range"
                min={0.5}
                max={2}
                step={0.1}
                value={config.tts_speed}
                onChange={(e) => setConfig(prev => ({ ...prev, tts_speed: Number(e.target.value) }))}
                className="w-full"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground">Pitch: {config.tts_pitch.toFixed(1)}x</label>
              <input
                type="range"
                min={0.5}
                max={2}
                step={0.1}
                value={config.tts_pitch}
                onChange={(e) => setConfig(prev => ({ ...prev, tts_pitch: Number(e.target.value) }))}
                className="w-full"
              />
            </div>
          </div>
        </Section>

        <Section
          title="Transcriber"
          description="Configure speech-to-text models and language settings."
        >
          <ModelCatalogPicker
            capability="stt"
            providers={modelCatalog?.providers || []}
            models={sttModels}
            value={config.stt_model || ''}
            providerId={sttProviderId}
            onProviderChange={(providerId) => {
              const provider = providerEnumFromId[providerId] || 'OPENAI'
              setConfig(prev => ({ ...prev, stt_provider: provider }))
            }}
            onChange={(model) => setConfig(prev => ({ ...prev, stt_model: model }))}
            label="STT Provider + Model"
          />

          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Language</label>
              <input
                value={config.stt_language}
                onChange={(e) => setConfig(prev => ({ ...prev, stt_language: e.target.value }))}
                className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground focus:ring-2 focus:ring-primary/60"
                placeholder="en"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Noise Reduction</label>
              <label className="flex items-center gap-3 text-sm text-muted-foreground">
                <input
                  type="checkbox"
                  checked={config.noise_reduction}
                  onChange={(e) => setConfig(prev => ({ ...prev, noise_reduction: e.target.checked }))}
                  className="rounded border-border text-primary focus:ring-primary"
                />
                Background denoising enabled
              </label>
            </div>
          </div>
        </Section>

        <Section
          title="Fallbacks"
          description="Define backup voice or transcriber providers for resilience."
        >
          <div className="rounded-xl border border-dashed border-border px-4 py-6 text-center text-sm text-muted-foreground">
            No fallbacks configured. Add a fallback provider for improved reliability.
          </div>
        </Section>

        <Section
          title="Phone Numbers"
          description="Choose a telephony provider, search available numbers, purchase, and assign one number to this agent."
        >
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Provider</label>
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                {(['twilio', 'vonage'] as PhoneProviderType[]).map(providerId => {
                  const provider = phoneProviders[providerId] || {
                    id: providerId,
                    name: providerId.toUpperCase(),
                    url: '',
                  }
                  const availability = configuredPhoneProviders[providerId]
                  const isActive = phoneProvider === providerId
                  return (
                    <button
                      key={providerId}
                      type="button"
                      onClick={() => {
                        setPhoneProvider(providerId)
                        setConfig(prev => ({ ...prev, phone_provider_preference: providerId }))
                      }}
                      className={`rounded-xl border px-3 py-2 text-left transition ${
                        isActive
                          ? 'border-primary bg-primary/10'
                          : 'border-border bg-card hover:border-muted-foreground/40'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <ProviderLogo name={provider.name} url={provider.url} size={24} />
                        <span className="text-sm font-medium text-foreground">{provider.name}</span>
                      </div>
                      <div
                        className={`mt-1 text-xs ${
                          availability?.configured ? 'text-emerald-400' : 'text-muted-foreground'
                        }`}
                      >
                        {availability?.configured ? 'Configured' : availability?.message || 'Not configured'}
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Search filters</label>
              <div className="grid grid-cols-2 gap-2">
                <input
                  value={phoneCountryCode}
                  onChange={(e) => setPhoneCountryCode(e.target.value.toUpperCase())}
                  maxLength={4}
                  className="rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground focus:ring-2 focus:ring-primary/60"
                  placeholder="Country (US)"
                />
                <input
                  value={phoneContains}
                  onChange={(e) => setPhoneContains(e.target.value)}
                  className="rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground focus:ring-2 focus:ring-primary/60"
                  placeholder="Contains"
                />
              </div>
              <div className="flex flex-wrap gap-2">
                {['voice', 'sms', 'mms'].map(capability => (
                  <button
                    key={capability}
                    type="button"
                    onClick={() => togglePhoneCapability(capability)}
                    className={`rounded-full border px-3 py-1 text-xs uppercase tracking-wide transition ${
                      phoneCapabilities.includes(capability)
                        ? 'border-primary bg-primary/10 text-primary'
                        : 'border-border text-muted-foreground hover:border-muted-foreground/40'
                    }`}
                  >
                    {capability}
                  </button>
                ))}
              </div>
              <button
                type="button"
                onClick={handleSearchPhoneNumbers}
                disabled={searching}
                className="rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-60"
              >
                {searching ? 'Searching...' : 'Search numbers'}
              </button>
            </div>
          </div>

          <label className="flex items-center gap-3 text-sm text-muted-foreground">
            <input
              type="checkbox"
              checked={confirmPurchase}
              onChange={(e) => setConfirmPurchase(e.target.checked)}
              className="rounded border-border text-primary focus:ring-primary"
            />
            Confirm purchase authorization for paid phone number orders.
          </label>

          {phoneActionError && (
            <div className="rounded-xl border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-300">
              {phoneActionError}
            </div>
          )}

          <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-foreground">Search results</h4>
              <div className="max-h-56 space-y-2 overflow-y-auto pr-1">
                {searchResults.length === 0 && (
                  <div className="rounded-lg border border-dashed border-border px-3 py-4 text-xs text-muted-foreground">
                    Run a search to load available numbers from the selected provider.
                  </div>
                )}
                {searchResults.map(result => (
                  <div key={`${result.provider}-${result.provider_number_id}`} className="rounded-lg border border-border bg-card px-3 py-2">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="text-sm font-medium text-foreground">{result.phone_number_e164}</div>
                        <div className="text-xs text-muted-foreground">
                          {(result.capabilities || []).join(', ') || 'voice'}
                          {result.monthly_cost ? ` • ${result.currency || 'USD'} ${result.monthly_cost}` : ''}
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() =>
                          handlePurchasePhoneNumber(
                            result.provider,
                            result.phone_number_e164,
                            result.provider_number_id,
                            result.capabilities || ['voice'],
                            result.country_code
                          )
                        }
                        disabled={!confirmPurchase || purchasing}
                        className="rounded-full border border-primary/40 px-3 py-1 text-xs font-medium text-primary hover:border-primary disabled:opacity-50"
                      >
                        {purchasing ? 'Purchasing...' : 'Purchase'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-foreground">Owned numbers</h4>
              <div className="max-h-56 space-y-2 overflow-y-auto pr-1">
                {ownedNumbers.length === 0 && (
                  <div className="rounded-lg border border-dashed border-border px-3 py-4 text-xs text-muted-foreground">
                    No purchased numbers yet for this agent.
                  </div>
                )}
                {ownedNumbers.map(number => (
                  <div key={number.id} className="rounded-lg border border-border bg-card px-3 py-2">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="text-sm font-medium text-foreground">{number.phone_number_e164}</div>
                        <div className="text-xs text-muted-foreground">
                          {number.provider.toUpperCase()} • {(number.capabilities || []).join(', ') || 'voice'}
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleSelectPhoneNumber(number.id, number.provider)}
                        disabled={selecting || number.is_selected}
                        className={`rounded-full px-3 py-1 text-xs font-medium ${
                          number.is_selected
                            ? 'border border-emerald-500/40 bg-emerald-500/10 text-emerald-300'
                            : 'border border-border text-muted-foreground hover:border-primary hover:text-primary'
                        }`}
                      >
                        {number.is_selected ? 'Selected' : selecting ? 'Selecting...' : 'Select'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Section>

        <Section
          title="Advanced Audio"
          description="Fine-grain control for formats, interruption handling, and audio quality."
        >
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Audio Format</label>
              <select
                value={config.audio_format}
                onChange={(e) => setConfig(prev => ({ ...prev, audio_format: e.target.value as AudioFormat }))}
                className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground focus:ring-2 focus:ring-primary/60"
              >
                {['MP3', 'WAV', 'OGG', 'WEBM', 'FLAC'].map(format => (
                  <option key={format} value={format}>
                    {format}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Sample Rate (Hz)</label>
              <input
                type="number"
                value={config.sample_rate}
                onChange={(e) => setConfig(prev => ({ ...prev, sample_rate: Number(e.target.value) }))}
                className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground focus:ring-2 focus:ring-primary/60"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Bit Rate (kbps)</label>
              <input
                type="number"
                value={config.bit_rate}
                onChange={(e) => setConfig(prev => ({ ...prev, bit_rate: Number(e.target.value) }))}
                className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground focus:ring-2 focus:ring-primary/60"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <label className="flex items-center gap-3 text-sm text-muted-foreground">
              <input
                type="checkbox"
                checked={config.echo_cancellation}
                onChange={(e) => setConfig(prev => ({ ...prev, echo_cancellation: e.target.checked }))}
                className="rounded border-border text-primary focus:ring-primary"
              />
              Echo cancellation
            </label>
            <label className="flex items-center gap-3 text-sm text-muted-foreground">
              <input
                type="checkbox"
                checked={config.auto_gain_control}
                onChange={(e) => setConfig(prev => ({ ...prev, auto_gain_control: e.target.checked }))}
                className="rounded border-border text-primary focus:ring-primary"
              />
              Auto gain control
            </label>
            <label className="flex items-center gap-3 text-sm text-muted-foreground">
              <input
                type="checkbox"
                checked={config.voice_activity_detection}
                onChange={(e) => setConfig(prev => ({ ...prev, voice_activity_detection: e.target.checked }))}
                className="rounded border-border text-primary focus:ring-primary"
              />
              Voice activity detection
            </label>
            <label className="flex items-center gap-3 text-sm text-muted-foreground">
              <input
                type="checkbox"
                checked={config.allow_interruption}
                onChange={(e) => setConfig(prev => ({ ...prev, allow_interruption: e.target.checked }))}
                className="rounded border-border text-primary focus:ring-primary"
              />
              Allow interruption
            </label>
          </div>

          <div>
            <label className="text-sm font-medium text-foreground">
              Interruption Threshold: {config.interruption_threshold.toFixed(2)}
            </label>
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={config.interruption_threshold}
              onChange={(e) => setConfig(prev => ({ ...prev, interruption_threshold: Number(e.target.value) }))}
              className="w-full"
            />
          </div>
        </Section>
      </div>
    </div>
  )
}
