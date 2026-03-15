---
sidebar_position: 1
title: Voice AI Overview
---

# Voice AI Overview

Chronos Studio's Voice AI lets you build and deploy real-time voice agents — from personal assistants to enterprise phone systems — all within the same platform you use for text-based agents.

## Why Voice AI?

By 2026, the majority of businesses will integrate AI-driven voice technology into operations. Voice agents handle:

- **Customer Support** — 24/7 phone support without hold times
- **Sales** — Outbound calls, qualification, appointment setting
- **Receptionists** — Business phone lines, call routing, message taking
- **Personal Assistants** — Voice-first interaction with your AI

## Key Capabilities

### Sub-Second Latency
Natural conversation requires speed. Chronos voice agents respond in under 1 second — fast enough that conversations feel natural, not robotic.

### Emotional Awareness
Agents detect and respond to user sentiment — frustration, urgency, satisfaction — and adapt their tone accordingly.

### Human-Like Vocal Fidelity
Access to premier AI voice model providers delivers voices that transcend robotic interaction. Choose from hundreds of voice profiles or clone your own.

### Enterprise Telephony
Production-grade phone infrastructure:
- **99.9% SLA** uptime guarantee
- **SIP trunking** for enterprise PBX integration
- **PSTN connectivity** — real phone numbers worldwide
- **WebRTC** for browser-based voice
- **Call recording** with transcription

## Voice Agent Architecture

```
┌──────────────────────────────────────────────┐
│                Voice Agent                    │
│                                              │
│  Caller → STT → LLM Agent → TTS → Caller   │
│           ↑                   ↑              │
│     Speech-to-    Agent     Text-to-         │
│     Text Engine   Runtime   Speech Engine    │
│                                              │
│  ┌──────────┐  ┌─────────┐  ┌────────────┐  │
│  │ Whisper  │  │ Tools   │  │ ElevenLabs │  │
│  │ Deepgram │  │ Memory  │  │ PlayHT     │  │
│  │ Google   │  │ Logic   │  │ Google     │  │
│  └──────────┘  └─────────┘  └────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │         Telephony Layer               │    │
│  │  PSTN │ SIP │ WebRTC │ Phone Numbers  │    │
│  └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

## Quick Example

```yaml
# voice-agent.yaml
name: support-line
model: gemini-2.0-flash
temperature: 0.5

system_prompt: |
  You are a customer support agent for Acme Corp.
  Be professional, empathetic, and efficient.
  If you can't resolve an issue, offer to transfer
  to a human agent.

voice:
  stt_provider: deepgram          # Speech-to-text
  tts_provider: elevenlabs        # Text-to-speech
  voice_id: rachel-professional   # Voice profile
  language: en-US
  interruption: true              # Allow user to interrupt
  silence_timeout: 5s             # Hang up after 5s silence
  emotion_detection: true

telephony:
  phone_number: +1-555-0123      # Assigned number
  sip_domain: sip.acme.com       # SIP integration
  recording: true                 # Record all calls
  transcription: true             # Transcribe recordings

tools:
  - name: lookup_account
    builtin: true
  - name: create_ticket
    builtin: true
  - name: transfer_to_human
    builtin: true
```

## Supported Providers

### Speech-to-Text (STT)
| Provider | Latency | Languages | Best For |
|----------|---------|-----------|----------|
| Deepgram | ~100ms | 30+ | Real-time, low latency |
| Google STT | ~200ms | 125+ | Language variety |
| Whisper | ~300ms | 100+ | Accuracy |
| Assembly AI | ~150ms | 20+ | Sentiment analysis |

### Text-to-Speech (TTS)
| Provider | Quality | Voices | Best For |
|----------|---------|--------|----------|
| ElevenLabs | Premium | 1000+ | Human-like quality |
| PlayHT | High | 800+ | Customization |
| Google TTS | Good | 400+ | Language variety |
| LMNT | Premium | Custom | Voice cloning |

---

## Next Steps

- [Voice AI Getting Started](./getting-started) — Build your first voice agent
- [Voice Models](./voice-models) — Choose and customize voices
- [Telephony](./telephony) — Phone numbers, SIP, and infrastructure
- [Emotion Detection](./emotion-detection) — Build empathetic agents
