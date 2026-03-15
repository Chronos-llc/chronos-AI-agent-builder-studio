---
sidebar_position: 5
title: Emotion Detection
---

# Emotion Detection

Build empathetic voice agents that detect and respond to caller emotions in real time.

## How It Works

Chronos analyzes vocal patterns — pitch, speed, volume, pauses — to detect emotional states during conversation:

```
Caller: [speaking quickly, rising pitch]
        "I've been on hold for an hour and nobody can help me!"

Detected: frustration (0.87), urgency (0.72)

Agent: [slows pace, empathetic tone]
       "I completely understand your frustration, and I'm sorry about
        the wait. You have my full attention now — let's get this
        resolved for you right away."
```

## Enable Emotion Detection

```yaml
voice:
  emotion_detection: true
  emotion_model: default           # default, advanced
  emotion_response: adaptive       # adaptive, aware, off
```

## Detected Emotions

| Emotion | Indicators | Agent Response |
|---------|-----------|----------------|
| **Frustration** | Fast speech, raised pitch, sighs | Empathize, take ownership |
| **Confusion** | Hesitation, repetition, questions | Simplify, clarify |
| **Urgency** | Fast speech, short sentences | Prioritize, act quickly |
| **Satisfaction** | Relaxed pace, positive words | Reinforce, upsell |
| **Sadness** | Slow speech, low volume | Be gentle, supportive |
| **Anger** | Loud, sharp tone, interruptions | Deescalate, validate |
| **Neutral** | Normal pace and tone | Standard interaction |

## Emotion-Aware System Prompts

```yaml
system_prompt: |
  You are a customer support agent. Adjust your approach based
  on the caller's emotional state:

  - If frustrated: Acknowledge their frustration first, then solve
  - If confused: Break things into simple steps, check understanding
  - If angry: Stay calm, validate feelings, escalate if needed
  - If satisfied: Be warm, ask if there's anything else
  - If urgent: Be efficient, skip pleasantries, act fast
```

## Accessing Emotion Data in Tools

```python
from chronos.tools import tool
from chronos.voice import current_call

@tool(name="escalate_call")
async def escalate_if_frustrated(reason: str) -> str:
    """Escalate to human agent if caller is frustrated."""
    call = current_call()

    if call.emotion.frustration > 0.8 or call.emotion.anger > 0.7:
        await call.transfer("+1-555-0100", priority="high")
        return "Transferred to senior agent (high frustration detected)"

    return "Frustration level normal — continuing conversation"
```

## Emotion Analytics

Track emotional patterns in the dashboard:

- **Call Sentiment Over Time** — Trend of caller emotions
- **Resolution by Emotion** — How well agents handle frustrated callers
- **Escalation Triggers** — What emotions lead to human handoff
- **Agent Performance** — Which agent configs best handle difficult calls

## Best Practices

1. **Always acknowledge** — Never ignore detected frustration
2. **Adapt, don't mimic** — Don't match anger; counter it with calm
3. **Set escalation thresholds** — Auto-transfer at high frustration scores
4. **Monitor patterns** — Use analytics to improve system prompts
5. **Test with scenarios** — Simulate emotional callers in development

---

## Next Steps

- [Guides: Customer Support Bot](../guides/customer-support-bot) — Build a full support agent
- [Guides: Sales Voice Agent](../guides/sales-voice-agent) — Emotion-aware sales calling
