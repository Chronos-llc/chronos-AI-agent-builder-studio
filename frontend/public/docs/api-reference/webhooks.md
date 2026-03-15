---
sidebar_position: 6
title: Webhooks
---

# Webhooks

Receive real-time notifications when events happen in your Chronos workspace.

## Create Webhook

```
POST /v1/webhooks
```

```bash
curl -X POST https://api.mohex.org/v1/webhooks \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-api.com/webhooks/chronos",
    "events": [
      "conversation.started",
      "conversation.completed",
      "agent.error",
      "voice.call.started",
      "voice.call.ended"
    ],
    "secret": "whsec_your_signing_secret"
  }'
```

## Events

### Conversation Events
| Event | Description |
|-------|-------------|
| `conversation.started` | New conversation initiated |
| `conversation.message` | New message in conversation |
| `conversation.completed` | Conversation ended |
| `conversation.escalated` | Escalated to human agent |

### Agent Events
| Event | Description |
|-------|-------------|
| `agent.deployed` | Agent deployed to production |
| `agent.updated` | Agent configuration changed |
| `agent.error` | Agent encountered an error |
| `agent.tool.failed` | Tool execution failed |

### Voice Events
| Event | Description |
|-------|-------------|
| `voice.call.started` | Incoming/outgoing call started |
| `voice.call.ended` | Call ended |
| `voice.call.transferred` | Call transferred to human/agent |
| `voice.recording.ready` | Call recording processed |

## Webhook Payload

```json
{
  "id": "evt_abc123",
  "type": "conversation.message",
  "timestamp": "2026-03-09T12:00:00Z",
  "data": {
    "agent_id": "agt_abc123",
    "conversation_id": "conv_xyz789",
    "message": {
      "role": "assistant",
      "content": "Your order has been shipped!",
      "tools_used": ["track_order"]
    }
  }
}
```

## Webhook Verification

Verify webhooks using the signing secret:

```python
import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

The signature is in the `X-Chronos-Signature` header.

## Retry Policy

Failed webhook deliveries are retried:
- **Attempt 1**: Immediate
- **Attempt 2**: 1 minute
- **Attempt 3**: 5 minutes
- **Attempt 4**: 30 minutes
- **Attempt 5**: 2 hours

After 5 failures, the webhook is paused. Reactivate in the dashboard.

## List Webhooks

```
GET /v1/webhooks
```

## Delete Webhook

```
DELETE /v1/webhooks/:webhook_id
```

---

## Next Steps

- [Guides](../guides/customer-support-bot) — Build real-world agents
- [Resources](../resources/faq) — FAQ and support
