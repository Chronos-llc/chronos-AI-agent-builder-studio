---
sidebar_position: 5
title: Voice API
---

# Voice API

The Voice API provides programmatic access to Chronos Studio's voice agent capabilities, including initiating calls, managing voice configurations, and handling voice events.

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /voice/agents | List voice agents |
| POST | /voice/calls | Initiate a voice call |
| GET | /voice/calls/{id} | Get call details |
| POST | /voice/calls/{id}/transfer | Transfer call |
| POST | /voice/calls/{id}/end | End call |
| GET | /voice/models | List available voice models |

## Voice Agents

### List Voice Agents
```bash
GET /voice/agents
```

### Response
```json
{
  "data": [
    {
      "id": "voice_agent_sales",
      "name": "Sales Voice Agent",
      "agent_id": "agent_abc123",
      "voice_id": "voice_rachel",
      "language": "en-US",
      "config": {
        "emotion_detection": true,
        "interruption_threshold": 0.5,
        "max_duration": 600
      }
    }
  ]
}
```

## Initiate Call

### Outbound Call
```bash
POST /voice/calls
```

### Request Body
```json
{
  "agent_id": "agent_abc123",
  "to": "+1234567890",
  "from": "+0987654321",
  "config": {
    "record": true,
    "transcribe": true,
    "emotion_detection": true,
    "voice_id": "voice_rachel"
  },
  "webhook_url": "https://yourapp.com/webhooks/voice"
}
```

### Response
```json
{
  "id": "call_xyz789",
  "status": "initiated",
  "agent_id": "agent_abc123",
  "to": "+1234567890",
  "from": "+0987654321",
  "created_at": "2024-01-15T14:00:00Z"
}
```

## Call States

| State | Description |
|-------|-------------|
| `initiated` | Call created, dialing |
| `ringing` | Call is ringing |
| `in_progress` | Agent connected, conversation active |
| `on_hold` | Call on hold |
| `transferring` | Call being transferred |
| `completed` | Call ended normally |
| `failed` | Call failed |

## Call Events via Webhook

Configure webhooks to receive call events:

```json
{
  "event": "voice.call.status",
  "timestamp": "2024-01-15T14:05:00Z",
  "call_id": "call_xyz789",
  "data": {
    "status": "in_progress",
    "duration": 30,
    "agent_id": "agent_abc123"
  }
}
```

## Get Call Details

```bash
GET /voice/calls/{id}
```

### Response
```json
{
  "id": "call_xyz789",
  "status": "completed",
  "agent_id": "agent_abc123",
  "to": "+1234567890",
  "from": "+0987654321",
  "duration": 245,
  "recording_url": "https://recordings.chronos.studio/call_xyz789.mp3",
  "transcript": [
    {"time": 0, "speaker": "caller", "text": "Hi, I need help with..."},
    {"time": 3, "speaker": "agent", "text": "I'd be happy to help..."}
  ],
  "emotions": [
    {"time": 0, "speaker": "caller", "emotion": "neutral"},
    {"time": 30, "speaker": "caller", "emotion": "frustrated"},
    {"time": 60, "speaker": "caller", "emotion": "satisfied"}
  ],
  "created_at": "2024-01-15T14:00:00Z",
  "ended_at": "2024-01-15T14:04:05Z"
}
```

## Transfer Call

```bash
POST /voice/calls/{id}/transfer
```

### Request Body
```json
{
  "to": "+1234567890",
  "type": "warm",
  "announcement": "I'm transferring you to a human agent"
}
```

Transfer types:
- `cold` - Direct transfer
- `warm` - Announce transfer before connecting

## End Call

```bash
POST /voice/calls/{id}/end
```

### Request Body
```json
{
  "reason": "customer_requested",
  "message": "Thank you for calling. Goodbye!"
}
```

## Voice Models

### List Available Models
```bash
GET /voice/models
```

### Response
```json
{
  "data": [
    {
      "id": "voice_rachel",
      "name": "Rachel",
      "gender": "female",
      "language": "en-US",
      "style": "professional",
      "preview_url": "https://voices.chronos.studio/preview/rachel.mp3"
    },
    {
      "id": "voice_marcus",
      "name": "Marcus",
      "gender": "male",
      "language": "en-US",
      "style": "friendly",
      "preview_url": "https://voices.chronos.studio/preview/marcus.mp3"
    }
  ]
}
```

## Voice Configuration

### Agent Voice Settings

```json
{
  "voice": {
    "voice_id": "voice_rachel",
    "speed": 1.0,
    "pitch": 0,
    "volume": 0,
    "emotion_detection": true,
    "interruption_timeout": 2.0,
    "silence_timeout": 30.0,
    "max_duration": 600
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| voice_id | string | - | Voice model ID |
| speed | float | 1.0 | Speech rate (0.5-2.0) |
| pitch | float | 0 | Voice pitch adjustment |
| emotion_detection | boolean | false | Enable emotion detection |
| interruption_timeout | float | 2.0 | Max silence before responding |
| silence_timeout | float | 30.0 | Timeout before ending call |
| max_duration | integer | 600 | Maximum call duration (seconds) |

## Real-time Transcription

Enable live transcription via WebSocket:

```javascript
const ws = new WebSocket('wss://api.chronos.studio/v1/voice/transcribe');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.transcript);
  // {"partial": true, "text": "Hello, how can", "speaker": "agent"}
};
```

## DTMF Tones

Handle DTMF input from callers:

```json
{
  "event": "voice.dtmf",
  "call_id": "call_xyz789",
  "digit": "1",
  "timestamp": "2024-01-15T14:02:30Z"
}
```
