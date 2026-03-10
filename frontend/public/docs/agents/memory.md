---
sidebar_position: 4
title: Agent Memory & Persistence
---

# Agent Memory & Persistence

Chronos Studio provides sophisticated memory management capabilities that enable agents to maintain context across conversations and store persistent information for long-term knowledge retention.

## Memory Types

### Conversation Memory
Stores the immediate conversation history for context within the current session.

**Configuration Options**:
- `max_history`: Maximum number of messages to retain
- `summary_mode`: Use summarization for long conversations
- `window_size`: Sliding window for context

```json
{
  "memory": {
    "type": "conversation",
    "max_history": 50,
    "summary_mode": true
  }
}
```

### Persistent Memory
Long-term storage for information that should persist across sessions.

**Use Cases**:
- User preferences
- Previous interaction history
- Learned facts about users
- Custom knowledge bases

```json
{
  "memory": {
    "type": "persistent",
    "storage": "database",
    "encryption": true
  }
}
```

### Vector Memory
Semantic search capabilities using embeddings for retrieval-augmented generation.

```json
{
  "memory": {
    "type": "vector",
    "embedding_model": "text-embedding-ada-002",
    "index_name": "knowledge_base"
  }
}
```

## Memory Operations

### Reading Memory
```python
# Retrieve conversation context
context = agent.memory.get_context(session_id="sess_123")

# Semantic search in vector memory
results = agent.memory.search(
    query="user's preferred payment method",
    limit=3
)
```

### Writing Memory
```python
# Store information in persistent memory
agent.memory.set(
    key="user:user_456:preferences",
    value={"theme": "dark", "language": "en"}
)

# Add to conversation history
agent.memory.add_message(
    session_id="sess_123",
    role="user",
    content="I prefer email notifications"
)
```

### Memory Templates
```python
# Predefined memory structures
from chronos.memory import UserProfile, SessionContext

# User profile persists across sessions
profile = UserProfile(
    user_id="user_789",
    name="John",
    preferences={"notifications": "email"},
    history=[]
)
```

## Memory Management Best Practices

### 1. Define Clear Memory Scope
Determine what information is relevant to store:
- User preferences: Store persistently
- Conversation context: Session-based
- General knowledge: Vector storage

### 2. Implement Data Retention Policies
```python
# Automatic cleanup configuration
config = {
    "retention": {
        "conversation": {"days": 30},
        "persistent": {"days": 365},
        "vector": {"days": -1}  # Never auto-delete
    }
}
```

### 3. Ensure Privacy Compliance
- Encrypt sensitive data
- Implement access controls
- Support data deletion requests
- Log memory access for auditing

### 4. Optimize for Performance
- Use pagination for large histories
- Implement caching for frequent queries
- Compress old conversations

## Memory APIs

### REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /agents/{id}/memory | Get agent memory config |
| POST | /agents/{id}/memory | Update memory settings |
| GET | /sessions/{id}/history | Get conversation history |
| POST | /memory/search | Semantic search |

### Example: Search Memory
```bash
curl -X POST https://api.chronos.studio/v1/memory/search \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent_abc123",
    "query": "customer previous orders",
    "limit": 5
  }'
```

## Memory Visualization

The dashboard provides memory visualization tools:
- Conversation timeline
- Key facts extracted
- User profile summary
- Search analytics

## Troubleshooting

### Common Issues

**Memory Not Persisting**
- Check storage configuration
- Verify database connectivity
- Review retention policies

**Slow Search Performance**
- Optimize embedding indexes
- Increase cache size
- Reduce search scope

**Memory Size Limits**
- Implement archival strategies
- Use summarization for old data
- Configure automatic cleanup

## Next Steps

- Explore [Multi-Agent Memory Sharing](/docs/agents/multi-agent)
- Configure [Vector Search](/docs/integrations/databases)
- Set up [Data Retention Policies](/docs/platform/dashboard)
