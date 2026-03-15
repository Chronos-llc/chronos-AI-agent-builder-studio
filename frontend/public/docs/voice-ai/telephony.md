---
sidebar_position: 4
title: Telephony
---

# Telephony

Connect your voice agents to real phone systems — PSTN numbers, SIP trunks, and WebRTC endpoints.

## Phone Numbers

### Get a Number

```bash
# List available numbers
chronos voice numbers list --country US --area-code 415

# Buy a number
chronos voice numbers buy +1-415-555-0199

# Assign to an agent
chronos voice assign +1-415-555-0199 my-voice-agent
```

### Number Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Local** | City/region number | Local business presence |
| **Toll-Free** | 800/888/877 numbers | Customer support lines |
| **International** | Numbers in 40+ countries | Global operations |

### Number Management

```bash
# List your numbers
chronos voice numbers mine

# Transfer a number between agents
chronos voice assign +1-415-555-0199 different-agent

# Release a number
chronos voice numbers release +1-415-555-0199
```

## SIP Integration

Connect to existing PBX/phone systems via SIP:

```yaml
telephony:
  sip:
    domain: sip.yourcompany.com
    username: ${SIP_USERNAME}
    password: ${SIP_PASSWORD}
    transport: tls                # tls, tcp, udp
    codecs: [opus, g711_ulaw]
    registration: true
```

### SIP Trunk Configuration

```yaml
telephony:
  sip_trunk:
    provider: twilio              # twilio, vonage, telnyx
    trunk_id: ${SIP_TRUNK_ID}
    inbound: true
    outbound: true
    concurrent_calls: 50
```

## WebRTC

For browser-based voice interactions:

```yaml
channels:
  - type: voice
    config:
      mode: webrtc
      stun_server: stun:stun.l.google.com:19302
```

### Embed in Your Website

```html
<script src="https://cdn.mohex.org/voice-widget.js"></script>
<chronos-voice
  agent="my-voice-agent"
  api-key="your_public_key"
  theme="dark"
></chronos-voice>
```

## Call Features

### Call Transfer

```yaml
tools:
  - name: transfer_call
    builtin: true
    config:
      destinations:
        sales: "+1-555-0100"
        support: "+1-555-0200"
        billing: "+1-555-0300"
```

```
Caller: "I need to speak with someone in billing"
Agent: "I'll transfer you to our billing department right now. One moment."
[Agent transfers call to +1-555-0200]
```

### Call Recording

```yaml
telephony:
  recording:
    enabled: true
    format: mp3
    storage: 90d                 # Retain for 90 days
    transcription: true          # Auto-transcribe recordings
    pii_redaction: true          # Redact PII from transcripts
```

### IVR / Call Routing

```yaml
telephony:
  ivr:
    greeting: "Welcome to Acme Corp."
    menu:
      - key: 1
        label: "Sales"
        agent: sales-voice-agent
      - key: 2
        label: "Support"
        agent: support-voice-agent
      - key: 0
        label: "Operator"
        transfer: "+1-555-0000"
    default_agent: general-voice-agent
```

## Enterprise SLA

For enterprise telephony:

| Metric | Guarantee |
|--------|-----------|
| Uptime | 99.9% |
| Call Setup Time | < 2 seconds |
| Audio Latency | < 200ms |
| Concurrent Calls | Unlimited (with enterprise plan) |
| Failover | Automatic regional failover |

---

## Next Steps

- [Emotion Detection](./emotion-detection) — Detect and respond to caller sentiment
- [Guides: Sales Voice Agent](../guides/sales-voice-agent) — Build a complete sales agent
