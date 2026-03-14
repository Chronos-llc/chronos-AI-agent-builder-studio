---
sidebar_position: 4
title: Voice API
---

# Voice API

Manage voice agents, phone numbers, and call sessions.

## Start Voice Session

```
POST /v1/voice/sessions
```

```bash
curl -X POST https://api.mohex.org/v1/voice/sessions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agt_abc123",
    "mode": "webrtc",
    "config": {
      "language": "en-US",
      "voice_id": "aria"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "vs_def456",
    "webrtc_url": "wss://voice.mohex.org/session/vs_def456",
    "ice_servers": [...],
    "expires_at": "2026-03-09T13:00:00Z"
  }
}
```

## Initiate Outbound Call

```
POST /v1/voice/calls
```

```bash
curl -X POST https://api.mohex.org/v1/voice/calls \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agt_abc123",
    "to": "+1-555-0199",
    "from": "+1-555-0100",
    "context": "Follow up on support ticket #1234"
  }'
```

## List Phone Numbers

```
GET /v1/voice/numbers
```

## Buy Phone Number

```
POST /v1/voice/numbers
```

```bash
curl -X POST https://api.mohex.org/v1/voice/numbers \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "country": "US",
    "type": "local",
    "area_code": "415",
    "agent_id": "agt_abc123"
  }'
```

## Get Call History

```
GET /v1/voice/calls?agent_id=agt_abc123&period=7d
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "call_id": "call_789",
      "direction": "inbound",
      "from": "+1-555-0199",
      "to": "+1-555-0100",
      "agent_id": "agt_abc123",
      "duration_seconds": 245,
      "status": "completed",
      "recording_url": "https://...",
      "transcript_url": "https://...",
      "emotion_summary": {"dominant": "neutral", "frustration_peak": 0.3},
      "started_at": "2026-03-09T10:30:00Z"
    }
  ]
}
```

## Get Call Recording

```
GET /v1/voice/calls/:call_id/recording
```

## Get Call Transcript

```
GET /v1/voice/calls/:call_id/transcript
```

---

## Next Steps

- [Tools API](./tools) — Manage agent tools
- [Webhooks](./webhooks) — Subscribe to voice events
