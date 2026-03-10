---
sidebar_position: 3
title: Telephony Integration
---

# Telephony Integration

Connect voice agents to the public telephone network.

## Supported Providers

| Provider | Type | Features |
|----------|------|----------|
| Twilio | SIP Trunking | Full PSTN |
| Plivo | SIP Trunking | Full PSTN |
| Vonage | SIP Trunking | Full PSTN |
| Direct SIP | BYOC | Custom |

## Setup

### Twilio

```bash
chronos voice provider add twilio \
  --account-sid AC... \
  --auth-token ... \
  --phone-number-sid PN...
```

### BYOC (Bring Your Own Carrier)

```yaml
# Custom SIP configuration
telephony:
  protocol: sip
  sip_domain: voice.yourcompany.com
  
  codecs:
    - opus
    - g711
    
  dtmf_mode: rfc2833
  
  redundancy:
    enabled: true
    failover: 100ms
```

## Phone Numbers

### Provision Numbers

```bash
# Search available numbers
chronos voice numbers search \
  --country US \
  --type toll-free \
  --area-code 800

# Purchase number
chronos voice numbers buy \
  --number "+1-800-555-0100"

# Connect to agent
chronos voice numbers connect \
  --number "+1-800-555-0100" \
  --agent voice_agent_id
```

### Number Types

| Type | Description | Cost |
|------|-------------|------|
| Toll-free | 800, 888, etc. | Higher |
| Local | Geographic | Lower |
| Mobile | Cell numbers | Varies |
| Vanity | Custom words | Premium |

## Call Handling

### Inbound Calls

```python
@webhook.on("voice.call.inbound")
def handle_inbound(call):
    # Route based on DID
    if call.to == "+1-800-555-0100":
        return voice_agent.sales
    elif call.to == "+1-800-555-0200":
        return voice_agent.support
```

### Outbound Calls

```python
call = voice.calls.create(
    agent_id="voice_agent_123",
    from_number="+1-800-555-0100",
    to="+1234567890",
    config={
        "record": True,
        "transcribe": True
    }
)
```

## Call Flows

### IVR (Interactive Voice Response)

```python
def ivr_menu(call):
    response = voice.speak("Press 1 for sales, 2 for support, 3 for billing")
    
    digit = wait_for_digit(timeout=5)
    
    if digit == "1":
        transfer_to_agent("sales")
    elif digit == "2":
        transfer_to_agent("support")
    elif digit == "3":
        transfer_to_agent("billing")
    else:
        voice.speak("Invalid choice")
        ivr_menu(call)
```

### Call Transfer

```python
# Warm transfer
voice.transfer(
    call_id="call_123",
    to="+1234567890",
    type="warm",
    announcement="I'll transfer you to an agent"
)

# Cold transfer
voice.transfer(
    call_id="call_123",
    to="+1234567890",
    type="cold"
)
```

## Call Recording

### Configuration

```yaml
recording:
  enabled: true
  channels: mono
  format: mp3
  quality: 64kbps
  storage: s3://your-bucket/recordings/
```

### Access

```python
# Get recording
call = voice.calls.get("call_123")
url = call.recording_url

# Get transcript
transcript = call.transcript
```

## Quality

### Metrics

- **MOS Score**: 4.0+ (good)
- **Latency**: <300ms
- **Jitter**: <50ms
- **Packet Loss**: <1%

### Monitoring

```bash
# View call quality
chronos voice quality call_123

# Real-time metrics
chronos voice metrics --live
```

## Best Practices

1. **Number selection**: Choose appropriate number type
2. **Recording consent**: Comply with regulations
3. **Fallback**: Plan for provider outages
4. **Quality monitoring**: Track continuously
