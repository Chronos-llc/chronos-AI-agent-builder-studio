---
sidebar_position: 2
title: Sales Voice Agent
---

# Build a Sales Voice Agent

This guide covers creating an AI-powered voice agent for sales and outbound calling campaigns.

## Overview

We'll build a voice agent that can:
- Handle inbound sales inquiries
- Qualify leads through conversation
- Schedule appointments
- Answer product questions
- Transfer to human salespeople

## Step 1: Create Voice Agent

### Configuration

```yaml
name: Sales Voice Agent
type: voice

voice:
  voice_id: "voice_rachel"
  language: "en-US"
  speed: 1.0
  pitch: 0
  
config:
  system_prompt: |
    You are a friendly and enthusiastic sales representative for Acme SaaS.
    
    Your role:
    - Engage prospects in conversation
    - Understand their needs
    - Explain product benefits
    - Handle objections professionally
    - Qualify leads for sales team
    
    Always sound enthusiastic but not pushy.
    Ask open-ended questions to understand pain points.
    
  max_duration: 300
  interruption_threshold: 0.5
  silence_timeout: 15
  emotion_detection: true
```

### Via API

```bash
curl -X POST https://api.chronos.studio/v1/voice/agents \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Voice Agent",
    "agent_id": "agent_sales_123",
    "voice_id": "voice_rachel",
    "language": "en-US",
    "config": {
      "emotion_detection": true,
      "max_duration": 300
    }
  }'
```

## Step 2: Configure Telephony

### Connect Phone Number

```bash
# Purchase and configure number
chronos voice provision \
  --country US \
  --type toll-free

# Or connect existing number
chronos voice connect \
  --number "+1-800-555-1234" \
  --agent agent_voice_123
```

### Supported Providers

| Provider | Setup | Features |
|----------|-------|----------|
| Twilio | Auto-configured | Full feature set |
| Plivo | Auto-configured | Full feature set |
| Vonage | Manual | Basic |
| Custom SIP | Manual | BYOC |

## Step 3: Lead Qualification

### Qualification Logic

```python
class LeadQualifier:
    def __init__(self):
        self.qualification_questions = [
            "What challenge are you looking to solve?",
            "How large is your team?",
            "What's your budget?",
            "When are you looking to implement?"
        ]
    
    def score_lead(self, conversation_data):
        score = 0
        
        # Budget qualification
        if conversation_data.get("has_budget"):
            score += 25
        
        # Timeline qualification
        if conversation_data.get("timeline") in ["immediate", "1-3 months"]:
            score += 25
        
        # Company size
        if conversation_data.get("company_size", 0) >= 10:
            score += 25
        
        # Decision authority
        if conversation_data.get("is_decision_maker"):
            score += 25
        
        return score
    
    def qualify(self, score):
        if score >= 75:
            return "hot"
        elif score >= 50:
            return "warm"
        else:
            return "cold"
```

### Integration with CRM

```python
class CRMIntegration:
    def sync_lead(self, lead_data):
        # Create/update in Salesforce
        response = sf_client.create("Lead", {
            "FirstName": lead_data["first_name"],
            "LastName": lead_data["last_name"],
            "Company": lead_data["company"],
            "Email": lead_data["email"],
            "Phone": lead_data["phone"],
            "LeadSource": "AI Voice Agent",
            "Rating": lead_data["qualification"]
        })
        return response["id"]
```

## Step 4: Appointment Scheduling

### Calendar Integration

```python
class AppointmentScheduler:
    def check_availability(self, rep_id, date):
        events = calendar.get_events(
            calendar_id=rep_id,
            start=date,
            end=date
        )
        return self.find_slots(events)
    
    def book_appointment(self, rep_id, lead, slot):
        event = calendar.create_event(
            calendar_id=rep_id,
            title=f"Sales Discovery - {lead['name']}",
            start=slot["start"],
            end=slot["end"],
            attendees=[lead["email"]]
        )
        
        # Send confirmation
        self.send_confirmation(lead, event)
        
        return event["id"]
    
    def send_confirmation(self, lead, event):
        send_email(
            to=lead["email"],
            subject="Your Appointment Confirmation",
            body=f"Hi {lead['name']}, your appointment is confirmed..."
        )
```

### Appointment Tool

```python
class ScheduleAppointment(Tool):
    name = "schedule_appointment"
    description = "Schedule a meeting with a sales rep"
    
    parameters = {
        "date": {"type": "string", "required": True},
        "time": {"type": "string", "required": True},
        "rep_id": {"type": "string", "required": True},
        "lead_name": {"type": "string", "required": True},
        "lead_email": {"type": "string", "required": True}
    }
    
    def execute(self, date, time, rep_id, lead_name, lead_email):
        slot = find_slot(rep_id, date, time)
        if not slot:
            return {"error": "No availability"}
        
        event = book_appointment(rep_id, {
            "name": lead_name,
            "email": lead_email
        }, slot)
        
        return {
            "status": "confirmed",
            "appointment_id": event["id"],
            "meeting_link": event["meet_link"]
        }
```

## Step 5: Objection Handling

### Common Objections

```yaml
objections:
  - pattern: "too expensive"
    response: |
      I understand budget is a concern. Let me share how other companies 
      have seen ROI within the first 3 months. Would that be helpful?
      
  - pattern: "need to think about it"
    response: |
      Of course, this is an important decision. What specific aspects 
      would you like to discuss further?
      
  - pattern: "competitor better"
    response: |
      What features are most important to you? I'd be happy to show you 
      how we compare in those specific areas.
```

### Implementation

```python
def handle_objection(agent, user_text):
    objection = detect_objection(user_text)
    
    if objection == "price":
        return redirect_to_roi_calculation()
    elif objection == "timing":
        return explore_concerns()
    elif objection == "competitor":
        return feature_comparison()
    
    return None
```

## Step 6: Outbound Campaigns

### Campaign Setup

```bash
# Create campaign
chronos voice campaign create \
  --name "Q1 Sales Outreach" \
  --agent voice_agent_123 \
  --leads-file leads.csv

# Schedule campaign
chronos voice campaign schedule \
  --campaign_id campaign_abc \
  --start "2024-02-01T09:00:00Z" \
  --end "2024-02-28T18:00:00Z"
```

### Lead List Format
```csv
phone,name,company,email,qualification
+1234567890,John Smith,john@acme.com,Acme Inc,high
+1987654321,Jane Doe,jane@tech.co,Tech Corp,medium
```

## Step 7: Analytics & Recording

### Call Recording

```json
{
  "recording": {
    "enabled": true,
    "storage": "s3",
    "retention_days": 90
  }
}
```

### Analytics Dashboard

Track key metrics:
- Conversion rate
- Average call duration
- Qualification rate
- Appointment set rate
- Revenue attribution

### Post-Call Summary

```python
def generate_summary(call_id):
    transcript = get_transcript(call_id)
    emotions = get_emotions(call_id)
    
    summary = {
        "duration": get_duration(call_id),
        "key_points": extract_key_points(transcript),
        "next_steps": extract_next_steps(transcript),
        "lead_score": calculate_score(emotions, transcript),
        "sentiment": analyze_sentiment(emotions)
    }
    
    # Sync to CRM
    crm.update_lead(lead_id, summary)
    
    return summary
```

## Complete Example

```python
from chronos import ChronosVoice

# Initialize voice client
voice = ChronosVoice(api_key="sk_live_...")

# Create voice agent
agent = voice.agents.create(
    name="Sales Agent",
    config={
        "system_prompt": open("prompts/sales.txt").read(),
        "voice_id": "voice_rachel",
        "emotion_detection": True,
        "tools": ["schedule_appointment", "create_lead", "check_pricing"]
    }
)

# Connect phone number
number = voice.numbers.provision(country="US", type="toll-free")

# Point to agent
voice.numbers.assign(number, agent)

# Monitor
voice.events.on("call.completed", lambda call: log_call(call))
```

## Best Practices

1. **Natural conversation flow** - Don't sound robotic
2. **Active listening** - Respond to context
3. **Clear value proposition** - Lead with benefits
4. **Handle objections gracefully** - Practice scenarios
5. **Seamless handoff** - Transfer to humans smoothly
6. **Continuous optimization** - Review and improve
