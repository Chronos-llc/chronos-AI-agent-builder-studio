---
sidebar_position: 2
title: Voice AI Getting Started
---

# Voice AI — Getting Started

Build and deploy your first voice agent in 10 minutes.

## Prerequisites

- Chronos Studio account
- CLI installed (`npm install -g @chronos-studio/cli`)

## Step 1: Create a Voice Agent

```bash
chronos init my-voice-agent --template voice-assistant
cd my-voice-agent
```

## Step 2: Configure Voice Settings

Edit `agent.yaml`:

```yaml
name: my-voice-agent
model: gemini-2.0-flash
temperature: 0.6

system_prompt: |
  You are a friendly AI assistant available via phone.
  Keep responses concise — aim for 1-2 sentences per turn.
  Ask clarifying questions when needed.
  Be natural and conversational.

voice:
  stt_provider: deepgram
  tts_provider: elevenlabs
  voice_id: aria                # Friendly, natural voice
  language: en-US
  speed: 1.0                    # 0.5 (slow) to 2.0 (fast)
  interruption: true            # Allow caller to interrupt
  end_of_turn_silence: 1.5s    # How long to wait for more input
  emotion_detection: true

channels:
  - type: voice
    config:
      mode: webrtc              # Start with browser testing
  - type: api                   # Also available via API
```

## Step 3: Test Locally

```bash
chronos dev --voice
```

This opens a browser-based voice interface for testing:

```
🎙️ Voice agent "my-voice-agent" is running
   Open: http://localhost:3000/voice-test

   [Press space to talk, release to send]

You: "Hi, what can you help me with?"
Agent: "Hey there! I can help with just about anything — questions,
        research, reminders, or just a good conversation. What's
        on your mind?"
```

## Step 4: Get a Phone Number

```bash
# List available phone numbers
chronos voice numbers list --country US

# Provision a number
chronos voice numbers buy +1-555-0199

# Assign to your agent
chronos voice assign +1-555-0199 my-voice-agent
```

## Step 5: Deploy

```bash
chronos deploy
```

Your voice agent is now:
- **Answering calls** at your assigned phone number
- **Available via WebRTC** at your agent's dashboard
- **Accessible via API** for programmatic voice sessions

## Step 6: Test with a Real Call

Call your assigned phone number. Your agent picks up and starts the conversation.

## Voice-Specific Tips

### Keep It Short
Voice responses should be 1-3 sentences. Long responses feel unnatural in conversation.

```yaml
# Good system prompt for voice
system_prompt: |
  Keep responses to 1-2 sentences. Be conversational.
  Ask one question at a time. Confirm before taking actions.
```

### Handle Interruptions
Users will interrupt. Design for it:

```yaml
voice:
  interruption: true
  interruption_sensitivity: medium  # low, medium, high
```

### Manage Silence
Configure what happens when the user stops talking:

```yaml
voice:
  end_of_turn_silence: 1.5s    # Wait before responding
  max_silence: 10s              # Prompt user after silence
  silence_prompt: "Are you still there? I'm here if you need anything."
  hang_up_silence: 30s          # End call after extended silence
```

### Error Recovery
Voice agents need graceful error handling:

```yaml
system_prompt: |
  If you don't understand something, say "I didn't quite catch that,
  could you repeat?" rather than guessing.
  If there's a technical issue, say "Let me try that again"
  and retry the operation.
```

---

## Next Steps

- [Voice Models](./voice-models) — Choose the perfect voice
- [Telephony](./telephony) — Advanced phone system setup
- [Emotion Detection](./emotion-detection) — Build empathetic voice agents
