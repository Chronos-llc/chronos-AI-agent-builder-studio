---
sidebar_position: 2
title: Voice AI Quick Start
---

# Voice AI Quick Start

Get started with voice agents in minutes.

## Prerequisites

- Chronos Studio account
- Voice-enabled agent (or create one)

## Step 1: Create Voice Agent

```bash
chronos voice agents create \
  --name "Support Voice" \
  --agent existing_agent_id \
  --voice rachel \
  --language en-US
```

## Step 2: Configure Voice Settings

```yaml
voice:
  voice_id: "voice_rachel"
  language: "en-US"
  speed: 1.0
  pitch: 0
  
  # Advanced
  emotion_detection: true
  interruption_threshold: 0.5
  silence_timeout: 30
  max_duration: 300
```

## Step 3: Connect Phone Number

```bash
# Get available numbers
chronos voice numbers search \
  --country US \
  --type toll-free

# Purchase and connect
chronos voice numbers provision \
  --number "+1-800-555-0100" \
  --agent voice_agent_id
```

## Step 4: Test Voice Agent

```bash
# Test with simulated call
chronos voice test \
  --agent voice_agent_id \
  --message "Hello, testing the voice agent"
```

## Making Your First Call

### Outbound

```python
from chronos.voice import VoiceClient

voice = VoiceClient(api_key="sk_live_...")

call = voice.calls.create(
    agent_id="voice_agent_123",
    to="+1234567890"
)

print(f"Call initiated: {call.id}")
```

### Inbound

Configure webhook:
```bash
chronos webhooks create \
  --url https://yourapp.com/webhooks/voice \
  --events voice.call.in_progress
```

Handle incoming calls:
```python
@app.route('/webhooks/voice', methods=['POST'])
def handle_voice(event):
    if event.type == 'voice.call.in_progress':
        # Call is connected, agent is listening
        pass
```

## Voice Pipeline

1. **Speech Recognition**: Caller speech → text
2. **Agent Processing**: Text → AI response
3. **Speech Synthesis**: AI response → audio
4. **Telephony**: Audio → caller

## Testing

### Simulator

Use the dashboard voice simulator to test:
- Single turns
- Full conversations
- Edge cases

### Recording

```python
# Get call recording
call = voice.calls.get("call_123")
recording_url = call.recording_url

# Download
import requests
audio = requests.get(recording_url)
with open('recording.mp3', 'wb') as f:
    f.write(audio.content)
```

## Next Steps

- [Configure Telephony](/docs/voice-ai/telephony)
- [Choose Voice Models](/docs/voice-ai/voice-models)
- [Enable Emotion Detection](/docs/voice-ai/emotion-detection)
