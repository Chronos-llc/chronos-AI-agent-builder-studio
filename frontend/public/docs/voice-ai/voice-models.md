---
sidebar_position: 3
title: Voice Models
---

# Voice Models

Choose and customize the voice your agent uses. Chronos integrates with leading TTS providers for human-like speech.

## Choosing a Voice

### Browse Available Voices

```bash
# List all available voices
chronos voice list

# Filter by provider
chronos voice list --provider elevenlabs

# Filter by characteristics
chronos voice list --gender female --language en --tone professional
```

### Preview Voices

```bash
chronos voice preview aria "Hello, welcome to our support line."
```

Or preview in the Dashboard under **Voice → Voice Library**.

## Voice Configuration

```yaml
voice:
  tts_provider: elevenlabs
  voice_id: aria
  language: en-US
  speed: 1.0                    # 0.5x to 2.0x
  pitch: 0                      # -20 to +20 semitones
  stability: 0.5                # 0.0 (varied) to 1.0 (stable)
  clarity: 0.75                 # 0.0 (warm) to 1.0 (clear)
  style_exaggeration: 0.0       # 0.0 to 1.0
```

## Voice Providers

### ElevenLabs
Premium quality with 1000+ voices. Best for human-like fidelity.

```yaml
voice:
  tts_provider: elevenlabs
  voice_id: rachel
  model: eleven_turbo_v2        # Fastest model
```

### PlayHT
Highly customizable with 800+ voices.

```yaml
voice:
  tts_provider: playht
  voice_id: jennifer
  quality: premium
  speed: 1.0
```

### Google Cloud TTS
Best language coverage with 400+ voices in 50+ languages.

```yaml
voice:
  tts_provider: google
  voice_id: en-US-Neural2-F
  speaking_rate: 1.0
```

## Voice Cloning

Create a custom voice from audio samples:

```bash
# Upload voice samples (minimum 3 minutes of clear speech)
chronos voice clone create \
  --name "Company Voice" \
  --samples audio1.wav audio2.wav audio3.wav \
  --description "Professional female voice for our brand"
```

```yaml
# Use your cloned voice
voice:
  tts_provider: elevenlabs
  voice_id: cloned:company-voice
```

**Requirements:**
- Minimum 3 minutes of clean audio
- Single speaker
- Minimal background noise
- WAV or MP3 format

## Multilingual Voices

Many voices support multiple languages:

```yaml
voice:
  tts_provider: elevenlabs
  voice_id: aria
  language: auto                 # Auto-detect language
  supported_languages:
    - en-US
    - es-ES
    - fr-FR
    - de-DE
```

The agent automatically speaks in the language the caller uses.

## Voice Presets

Quick configurations for common use cases:

| Preset | Voice | Tone | Speed | Use Case |
|--------|-------|------|-------|----------|
| `professional` | Clear, neutral | Formal | 1.0x | Business calls |
| `friendly` | Warm, approachable | Casual | 1.05x | Customer service |
| `energetic` | Upbeat, dynamic | Enthusiastic | 1.1x | Sales |
| `calm` | Soft, measured | Soothing | 0.95x | Healthcare, support |

```yaml
voice:
  preset: friendly              # Apply preset defaults
  voice_id: aria                # Override specific settings
```

---

## Next Steps

- [Telephony](./telephony) — Connect phone systems
- [Emotion Detection](./emotion-detection) — Respond to caller sentiment
