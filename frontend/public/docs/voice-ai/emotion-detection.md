---
sidebar_position: 5
title: Emotion Detection
---

# Emotion Detection

Chronos Studio's emotion detection enables voice agents to understand and respond to caller emotional state.

## Overview

Emotion detection analyzes:
- Speech patterns
- Voice tone
- Speaking pace
- Volume changes

## Supported Emotions

| Emotion | Description |
|---------|-------------|
| Happy | Positive, satisfied |
| Sad | Disappointed, frustrated |
| Angry | Frustrated, upset |
| Fearful | Anxious, concerned |
| Surprised | Unexpected |
| Neutral | Calm, normal |

## Enabling Emotion Detection

### Configuration

```yaml
voice:
  emotion_detection:
    enabled: true
    sensitivity: medium  # low, medium, high
    
    # Triggers
    triggers:
      angry:
        threshold: 0.7
        action: offer_escalation
      fearful:
        threshold: 0.6
        action: reassure
```

### API

```python
call = voice.calls.create(
    agent_id="voice_agent_123",
    to="+1234567890",
    config={
        "emotion_detection": True
    }
)
```

## Using Emotion Data

### Webhook Events

```json
{
  "event": "voice.emotion",
  "timestamp": "2024-01-15T14:05:00Z",
  "call_id": "call_xyz789",
  "emotion": {
    "speaker": "caller",
    "primary": "frustrated",
    "confidence": 0.85,
    "secondary": "angry",
    "score": {
      "happy": 0.05,
      "sad": 0.10,
      "angry": 0.85,
      "neutral": 0.00
    }
  }
}
```

### In Conversation

```python
# Access emotion in agent context
def handle_message(event):
    emotions = event.emotions
    
    if emotions.primary == "angry" and emotions.confidence > 0.7:
        # Empathize before responding
        return f"I understand you're frustrated. Let me help."
    
    elif emotions.primary == "happy":
        # Match enthusiasm
        return f"Wonderful! I'm glad to hear that!"
    
    return process_normal_response(event)
```

## Emotion Responses

### Pre-defined Responses

```python
EMOTION_RESPONSES = {
    "angry": [
        "I completely understand your frustration.",
        "I'm sorry you're having this experience.",
        "Let me make this right for you."
    ],
    "frustrated": [
        "I can hear this is frustrating.",
        "Let's work through this together."
    ],
    "happy": [
        "That's great to hear!",
        "I'm so glad I could help!"
    ]
}
```

### Custom Responses

```yaml
emotion_responses:
  angry:
    - response: "I completely understand. This is important to us."
      min_confidence: 0.6
    - response: "I'm so sorry for the inconvenience."
      min_confidence: 0.8
      
  happy:
    - response: "Thank you! It's our pleasure!"
```

## Analytics

### Emotion Tracking

```bash
# View emotion distribution
chronos voice analytics emotions \
  --agent voice_agent_123 \
  --date_range "last_30_days"
```

### Response Metrics

- Emotion accuracy
- Response effectiveness
- Escalation rates by emotion

## Privacy

### Consent

- Notify callers about emotion analysis
- Allow opt-out
- Store emotion data securely

### Data Usage

- Improve agent responses
- Quality assurance
- Analytics (aggregated)
