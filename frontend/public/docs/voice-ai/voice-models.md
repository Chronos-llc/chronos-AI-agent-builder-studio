---
sidebar_position: 4
title: Voice Models
---

# Voice Models

Chronos Studio offers a variety of voice models for different use cases.

## Available Voices

### English (US)

| Voice ID | Name | Gender | Style |
|----------|------|--------|-------|
| voice_rachel | Rachel | Female | Professional |
| voice_marcus | Marcus | Male | Friendly |
| voice_sarah | Sarah | Female | Energetic |
| voice_david | David | Male | Authoritative |
| voice_emily | Emily | Female | Warm |

### Other Languages

| Language | Voices |
|----------|--------|
| Spanish (ES) | Carlos, Maria |
| French | Pierre, Sophie |
| German | Hans, Greta |
| Japanese | Yuki, Kenji |

## Custom Voices

### Voice Cloning

```bash
# Upload voice samples
chronos voice clone upload \
  --samples ./voice_samples/ \
  --name "Company Voice"

# Create custom voice
chronos voice clone create \
  --name "Company Voice" \
  --samples voice_sample_1,voice_sample_2
```

### Requirements
- 30+ minutes of audio
- Multiple speakers
- Clear audio quality
- Diverse content

## Voice Settings

### Configuration

```yaml
voice:
  voice_id: "voice_rachel"
  
  # Synthesis settings
  speed: 1.0        # 0.5 - 2.0
  pitch: 0          # -12 to +12 semitones
  volume: 0         # -6dB to +6dB
  
  # Advanced
  emphasis: normal  # strong, normal, reduced
  rate: normal       # x-slow, slow, normal, fast, x-fast
```

### SSML Support

```xml
<speak>
  <prosody rate="90%">
    This is spoken at 90% speed.
  </prosody>
  
  <emphasis level="strong">
    This is emphasized.
  </emphasis>
  
  <break time="500ms"/>
  
  <voice name="voice_marcus">
    Switching to a different voice.
  </voice>
</speak>
```

## Selection Guide

### Use Case Recommendations

| Use Case | Recommended Voice |
|----------|-------------------|
| Customer Support | Rachel, David |
| Sales | Sarah, Marcus |
| Technical Support | David, Rachel |
| Hospitality | Emily, Sarah |
| Entertainment | Custom |

### Factors to Consider

1. **Audience**: Age, demographics
2. **Content**: Formal, casual
3. **Duration**: Short vs. long-form
4. **Brand**: Consistency with brand voice

## Voice API

### List Available Voices

```bash
GET /voice/models
```

### Get Voice Details

```bash
GET /voice/models/{voice_id}
```

### Preview Voice

```bash
# Test voice
chronos voice preview voice_rachel \
  --text "Hello, this is a test."
```

## Best Practices

1. **Consistency**: Use same voice across touchpoints
2. **Testing**: Test with actual use cases
3. **Accessibility**: Consider screen reader compatibility
4. **Cultural**: Match voice to audience
