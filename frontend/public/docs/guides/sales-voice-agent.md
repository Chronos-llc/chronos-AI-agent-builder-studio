---
sidebar_position: 2
title: "Guide: Sales Voice Agent"
---

# Guide: Build a Sales Voice Agent

Build an AI-powered outbound sales agent that qualifies leads, books meetings, and handles objections — all via phone.

## What We'll Build

A voice agent that:
- Makes outbound calls to leads
- Qualifies prospects with discovery questions
- Handles common objections naturally
- Books meetings on your calendar
- Logs call outcomes to your CRM

## Agent Configuration

```yaml
name: sales-caller
model: gemini-2.0-pro            # Pro model for nuanced conversation
temperature: 0.6

system_prompt: |
  You are a sales development representative for {{company_name}}.
  You're calling leads who expressed interest in {{product_name}}.

  Call structure:
  1. Introduce yourself warmly (first name only)
  2. Reference how they found you (lead source)
  3. Ask 2-3 discovery questions about their needs
  4. Present a brief value proposition based on their answers
  5. Offer to book a demo with a solutions engineer
  6. Handle objections naturally — never be pushy

  Qualification criteria (BANT):
  - Budget: Can they invest $X/month?
  - Authority: Are they a decision maker?
  - Need: Do they have a real problem we solve?
  - Timeline: Are they looking to implement soon?

  Rules:
  - Keep the call under 5 minutes
  - If they're busy, offer to call back
  - Never lie or exaggerate capabilities
  - If they say no, thank them and end gracefully
  - Log every call outcome to CRM

voice:
  stt_provider: deepgram
  tts_provider: elevenlabs
  voice_id: josh-professional      # Warm, confident male voice
  language: en-US
  speed: 1.0
  interruption: true
  emotion_detection: true
  end_of_turn_silence: 2s

telephony:
  recording: true
  transcription: true

tools:
  - name: get_lead_info
    path: ./tools/lead_info.py
  - name: book_meeting
    path: ./tools/book_meeting.py
  - name: log_call_outcome
    path: ./tools/log_outcome.py
  - name: schedule_callback
    path: ./tools/callback.py
```

## Example Call Flow

```
Agent: "Hi Sarah, this is Alex from Chronos Studio. You signed up
        for our waitlist last week — thanks for your interest!
        Do you have a couple minutes to chat about what brought
        you to us?"

Lead:  "Yeah, sure. We're looking at voice AI for our support line."

Agent: "Great! Just so I can point you in the right direction —
        roughly how many support calls does your team handle per month?"

Lead:  "About 2,000, and it's growing."

Agent: "That's significant. And are most of those common questions
        that could be handled by AI, or more complex issues?"

Lead:  "Probably 60-70% are repetitive — password resets, order
        status, basic troubleshooting."

Agent: "That's exactly what our voice agents excel at. Our clients
        typically automate 60-80% of those calls with sub-second
        response times — no hold music. Would it be helpful to see
        a 15-minute demo tailored to your support use case?"

Lead:  "Yeah, that sounds good."

Agent: [tool:book_meeting] "Perfect! I have Thursday at 2 PM or
        Friday at 10 AM available. Which works better?"
```

## Tools

### Book Meeting

```python
@tool(name="book_meeting", description="Book a demo on the calendar")
async def book_meeting(
    lead_email: str,
    date: str,
    time: str,
    meeting_type: str = "demo"
) -> str:
    event = await calendar.create_event(
        title=f"Chronos Demo — {lead_email}",
        date=date,
        time=time,
        duration=15,
        attendees=[lead_email, "sales@mohex.org"],
        description=f"Product demo for {lead_email}"
    )
    return f"Meeting booked: {date} at {time}. Calendar invite sent."
```

### Log Call Outcome

```python
@tool(name="log_call_outcome", description="Log the call result to CRM")
async def log_call_outcome(
    lead_id: str,
    outcome: str,        # "meeting_booked", "callback", "not_interested", "no_answer"
    notes: str,
    qualification: dict   # {"budget": bool, "authority": bool, "need": bool, "timeline": bool}
) -> str:
    await crm.update_lead(
        id=lead_id,
        status=outcome,
        notes=notes,
        qualification_score=sum(qualification.values()),
        last_contact=datetime.now()
    )
    return f"CRM updated: {outcome}"
```

## Launch an Outbound Campaign

```python
from chronos import ChronosClient

client = ChronosClient(api_key="your_key")

# Get uncontacted leads
leads = await crm.get_leads(status="new", limit=50)

for lead in leads:
    await client.voice.call(
        agent_id="sales-caller",
        to=lead.phone,
        context={
            "lead_name": lead.name,
            "lead_source": lead.source,
            "lead_company": lead.company
        }
    )
```

---

## Next Steps

- [Workflow Automation](./workflow-automation) — Automate follow-ups
- [Emotion Detection](../voice-ai/emotion-detection) — Handle objections better
