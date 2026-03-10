---
sidebar_position: 1
title: Customer Support Bot
---

# Build a Customer Support Bot

This guide walks you through building a comprehensive customer support bot using Chronos Studio.

## Overview

We'll create a support agent that can:
- Answer product questions
- Troubleshoot common issues
- Look up order status
- Create support tickets
- Escalate to human agents when needed

## Step 1: Create the Agent

### Agent Configuration

```yaml
name: Customer Support Agent
type: conversational

config:
  system_prompt: |
    You are a friendly and professional customer support agent for Acme Corp.
    
    Your responsibilities:
    - Answer questions about products and services
    - Help troubleshoot technical issues
    - Look up order status
    - Create support tickets when needed
    
    Guidelines:
    - Always be polite and empathetic
    - Ask clarifying questions when needed
    - Provide clear, actionable solutions
    - Know when to escalate to human agents
    
    Escalation triggers:
    - Customer explicitly requests human
    - Complex technical issues beyond scope
    - Billing disputes
    - Account security concerns
```

## Step 2: Add Knowledge Base

### Import Documentation

```bash
# Import from various sources
chronos knowledge import \
  --source docs/ \
  --format markdown

chronos knowledge import \
  --source https://help.example.com \
  --format web
```

### Configure Vector Search

```json
{
  "memory": {
    "type": "vector",
    "embedding_model": "text-embedding-ada-002",
    "index_name": "support_knowledge"
  }
}
```

## Step 3: Create Support Tools

### Order Lookup Tool

```python
from chronos.tools import Tool
import requests

class OrderLookup(Tool):
    name = "get_order_status"
    description = "Look up order status by order ID"
    
    parameters = {
        "order_id": {
            "type": "string",
            "required": True,
            "description": "The order ID (e.g., ORD-12345)"
        }
    }
    
    def execute(self, order_id):
        # Call your order system API
        response = requests.get(
            f"https://api.yourstore.com/orders/{order_id}",
            headers={"Authorization": f"Bearer {os.getenv('ORDER_API_KEY')}"}
        )
        
        if response.status_code == 404:
            return {"error": "Order not found"}
        
        order = response.json()
        return {
            "order_id": order["id"],
            "status": order["status"],
            "items": order["items"],
            "shipping": {
                "carrier": order["shipping"]["carrier"],
                "tracking": order["shipping"]["tracking_number"],
                "eta": order["shipping"]["estimated_delivery"]
            },
            "total": order["total"]
        }
```

### Ticket Creation Tool

```python
class CreateTicket(Tool):
    name = "create_support_ticket"
    description = "Create a support ticket"
    
    parameters = {
        "subject": {"type": "string", "required": True},
        "description": {"type": "string", "required": True},
        "priority": {
            "type": "string",
            "enum": ["low", "medium", "high", "urgent"],
            "default": "medium"
        },
        "category": {
            "type": "string",
            "enum": ["billing", "technical", "general", "account"],
            "required": True
        }
    }
    
    def execute(self, subject, description, priority, category):
        ticket = {
            "subject": subject,
            "description": description,
            "priority": priority,
            "category": category,
            "status": "open",
            "source": "ai_agent"
        }
        
        response = requests.post(
            "https://your-helpdesk.com/api/tickets",
            json=ticket,
            headers={"Authorization": f"Bearer {os.getenv('HELPDESK_KEY')}"}
        )
        
        return {
            "ticket_id": response.json()["id"],
            "status": "created",
            "message": f"Ticket created. Reference: {response.json()['id']}"
        }
```

### Knowledge Search Tool

```python
class SearchKnowledgeBase(Tool):
    name = "search_knowledge"
    description = "Search the knowledge base for solutions"
    
    parameters = {
        "query": {"type": "string", "required": True}
    }
    
    def execute(self, query):
        results = vector_store.search(
            query=query,
            index="support_knowledge",
            limit=5
        )
        
        return {
            "results": [
                {
                    "title": r["title"],
                    "content": r["content"][:500],
                    "url": r["url"],
                    "relevance": r["score"]
                }
                for r in results
            ]
        }
```

## Step 4: Register Tools

```bash
chronos tools register order_lookup.py
chronos tools register create_ticket.py
chronos tools register search_knowledge.py

# Enable tools for agent
chronos agent update agent_123 \
  --tools get_order_status,create_support_ticket,search_knowledge
```

## Step 5: Configure Escalation

### Escalation Flow

```python
class EscalationHandler:
    def __init__(self):
        self.escalation_threshold = 3  # Failed resolutions
    
    def should_escalate(self, context):
        triggers = [
            context.get("user_requested_human"),
            context.get("complex_issue"),
            context.get("security_concern"),
            context.get("failed_resolutions", 0) >= self.escalation_threshold
        ]
        return any(triggers)
    
    def escalate(self, session):
        # Notify human agent
        notify_slack(
            channel="#support-escalations",
            message=f"Escalation needed for session {session.id}"
        )
        
        # Transfer conversation
        return {
            "status": "escalated",
            "agent": "human_agent",
            "summary": session.get_summary()
        }
```

## Step 6: Add Sentiment Analysis

Enable emotion detection to identify frustrated customers:

```json
{
  "emotion_detection": {
    "enabled": true,
    "triggers": {
      "frustrated": {
        "threshold": 0.7,
        "action": "offer_human"
      }
    }
  }
}
```

## Step 7: Test the Agent

### Test Scenarios

```python
# Test order lookup
response = client.chat(
    message="What's the status of order ORD-12345?"
)
# Expected: Order details with shipping info

# Test ticket creation
response = client.chat(
    message="I can't log into my account!"
)
# Expected: Ticket created with priority set

# Test knowledge base
response = client.chat(
    message="How do I reset my password?"
)
# Expected: Knowledge base article returned
```

## Step 8: Deploy

```bash
# Deploy to production
chronos agent deploy agent_123 --env production

# Configure webhook for tickets
chronos webhooks create \
  --url https://yourapp.com/webhooks/tickets \
  --events agent.message.completed
```

## Monitoring

### Dashboard Metrics
- Total conversations
- Resolution rate
- Average response time
- Ticket creation rate
- Escalation rate
- Customer satisfaction

## Complete Code

```python
from chronos import Chronos
from chronos.tools import register_tool

client = Chronos(api_key="sk_live_...")

# Create agent
agent = client.agents.create(
    name="Support Agent",
    type="conversational",
    config={
        "system_prompt": open("prompts/support.txt").read(),
        "temperature": 0.7,
        "tools": [
            "get_order_status",
            "create_support_ticket",
            "search_knowledge"
        ]
    }
)

# Deploy
client.agents.deploy(agent.id)
```

## Next Steps

- [Add Voice Capabilities](/docs/guides/sales-voice-agent)
- [Set Up Multi-Agent Teams](/docs/agents/multi-agent)
- [Configure Analytics](/docs/platform/dashboard)
