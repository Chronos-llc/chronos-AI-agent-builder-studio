---
sidebar_position: 4
title: Agent Memory & Persistence
---

# Agent Memory & Persistence

Chronos Studio provides sophisticated memory management capabilities that enable agents to maintain context across conversations and store persistent information for long-term knowledge retention.

## Memory Types Overview

| Type | Scope | Use Case | Persistence |
|------|-------|----------|-------------|
| Session Memory | Current conversation | Context within session | Session-only |
| Persistent Memory | Cross-session | User preferences, history | Permanent |
| Key-Value Memory | Structured data | Configuration, cache | Permanent |
| Vector Memory | Semantic search | Knowledge retrieval | Permanent |

## Session Memory

Session memory stores the immediate conversation history for context within the current session. It's automatically managed and cleared when the session ends.

### Configuration

```json
{
  "memory": {
    "type": "session",
    "max_history": 50,
    "summary_mode": true,
    "window_size": 10
  }
}
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| max_history | number | 50 | Maximum messages to retain |
| summary_mode | boolean | false | Use summarization for long conversations |
| window_size | number | 0 | Sliding window for context (0 = unlimited) |
| include_system | boolean | true | Include system prompts in context |

### Using Session Memory

```python
from chronos.memory import SessionMemory

# Initialize session memory
memory = SessionMemory(
    agent_id="agent_abc123",
    max_history=50,
    summary_mode=True
)

# Add message to session
memory.add_message(
    role="user",
    content="I need help with my order"
)

memory.add_message(
    role="assistant",
    content="I'd be happy to help! Can you provide your order number?"
)

# Get conversation context
context = memory.get_context()
```

```javascript
// Node.js
const { SessionMemory } = require('chronos-sdk');

const memory = new SessionMemory({
  agentId: 'agent_abc123',
  maxHistory: 50,
  summaryMode: true
});

// Add message
await memory.addMessage({
  role: 'user',
  content: 'I need help with my order'
});

// Get context
const context = await memory.getContext();
```

### Session Memory Best Practices

- Set appropriate `max_history` based on token limits
- Enable `summary_mode` for long conversations
- Use `window_size` for focused context on recent messages

## Persistent Memory

Persistent memory stores information that persists across sessions, enabling agents to remember user preferences, history, and learned facts.

### Configuration

```json
{
  "memory": {
    "type": "persistent",
    "storage": "database",
    "encryption": true,
    "retention_days": 365
  }
}
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| storage | string | database | Storage backend (database, redis, s3) |
| encryption | boolean | false | Encrypt stored data |
| retention_days | number | -1 | Data retention (-1 = forever) |
| namespace | string | agent_id | Data namespace |

### Use Cases

- User preferences
- Previous interaction history
- Learned facts about users
- Custom knowledge bases
- Conversation summaries

### Using Persistent Memory

```python
from chronos.memory import PersistentMemory

# Initialize persistent memory
memory = PersistentMemory(
    agent_id="agent_abc123",
    storage="database",
    encryption=True
)

# Store user preferences
memory.set(
    key="user:preferences",
    value={
        "theme": "dark",
        "language": "en",
        "notifications": "email"
    }
)

# Retrieve preferences
prefs = memory.get("user:preferences")

# Delete data
memory.delete("user:preferences")
```

```javascript
// Node.js
const { PersistentMemory } = require('chronos-sdk');

const memory = new PersistentMemory({
  agentId: 'agent_abc123',
  storage: 'database',
  encryption: true
});

// Store data
await memory.set('user:preferences', {
  theme: 'dark',
  language: 'en'
});

// Retrieve data
const prefs = await memory.get('user:preferences');
```

### Persistent Memory APIs

```bash
# REST API
GET /agents/{id}/memory/{key}
PUT /agents/{id}/memory/{key}
DELETE /agents/{id}/memory/{key}
```

## Key-Value Memory

Key-value memory provides a simple, fast storage mechanism for structured data using a key-value store pattern.

### Configuration

```json
{
  "memory": {
    "type": "keyvalue",
    "backend": "redis",
    "ttl": 3600,
    "max_size": "100MB"
  }
}
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| backend | string | redis | Storage backend (redis, memcached, dynamodb) |
| ttl | number | 0 | Time-to-live in seconds (0 = no expiry) |
| max_size | string | 100MB | Maximum data size |
| compression | boolean | false | Compress stored values |

### Using Key-Value Memory

```python
from chronos.memory import KeyValueMemory

# Initialize KV memory
kv = KeyValueMemory(
    agent_id="agent_abc123",
    backend="redis"
)

# Store simple values
kv.set("config:theme", "dark")
kv.set("config:language", "en")

# Store complex values
kv.set("user:session_123", {
    "last_active": "2024-01-15T10:30:00Z",
    "page": "/dashboard",
    "items": ["item1", "item2"]
})

# Retrieve with default
theme = kv.get("config:theme", default="light")

# Check existence
if kv.exists("config:theme"):
    theme = kv.get("config:theme")

# Delete
kv.delete("config:theme")

# Batch operations
kv.mset({
    "key1": "value1",
    "key2": "value2"
})
values = kv.mget(["key1", "key2"])
```

### Key-Value Patterns

```python
# Cache pattern with TTL
kv.set("api:users:123", user_data, ttl=300)

# Counter pattern
kv.incr("agent:requests:total")
kv.incr("agent:requests:today")

# Set pattern
kv.sadd("user:tags:123", ["premium", "enterprise"])
tags = kv.smembers("user:tags:123")
```

## Vector Memory

Vector memory enables semantic search capabilities using embeddings for retrieval-augmented generation (RAG).

### Configuration

```json
{
  "memory": {
    "type": "vector",
    "embedding_model": "text-embedding-ada-002",
    "index_name": "knowledge_base",
    "dimension": 1536,
    "metric": "cosine"
  }
}
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| embedding_model | string | text-embedding-ada-002 | Embedding model to use |
| index_name | string | agent_id | Vector index name |
| dimension | number | 1536 | Embedding dimension |
| metric | string | cosine | Similarity metric (cosine, euclidean, dot) |
| namespace | string | default | Index namespace |

### Using Vector Memory

```python
from chronos.memory import VectorMemory

# Initialize vector memory
vector = VectorMemory(
    agent_id="agent_abc123",
    embedding_model="text-embedding-ada-002",
    index_name="knowledge_base"
)

# Add documents to memory
documents = [
    "Our refund policy allows returns within 30 days of purchase.",
    "We offer free shipping on orders over $50.",
    "Customer support is available 24/7 via chat and email."
]

vector.add_documents(documents)

# Search semantic similarity
results = vector.search(
    query="How does your return policy work?",
    top_k=3
)

# Results contain:
# - text: The matched document
# - score: Similarity score (0-1)
# - metadata: Optional metadata

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Text: {result['text']}")
```

```javascript
// Node.js
const { VectorMemory } = require('chronos-sdk');

const vector = new VectorMemory({
  agentId: 'agent_abc123',
  embeddingModel: 'text-embedding-ada-002',
  indexName: 'knowledge_base'
});

// Add documents
await vector.addDocuments([
  'Our refund policy allows returns within 30 days.',
  'Free shipping on orders over $50.',
  'Customer support available 24/7'
]);

// Search
const results = await vector.search({
  query: 'How does return policy work?',
  topK: 3
});
```

### Vector Search with Metadata

```python
from chronos.memory import VectorMemory

vector = VectorMemory(agent_id="agent_abc123")

# Add documents with metadata
vector.add_documents(
    documents=[
        "Troubleshooting guide for login issues",
        "Password reset instructions",
        "Two-factor authentication setup"
    ],
    metadata=[
        {"category": "account", "type": "troubleshooting"},
        {"category": "account", "type": "guide"},
        {"category": "security", "type": "setup"}
    ]
)

# Filtered search
results = vector.search(
    query="How do I reset my password?",
    top_k=5,
    filter={"category": "account"}
)
```

### RAG Integration

```python
from chronos import Agent
from chronos.memory import VectorMemory

# Initialize agent with RAG
agent = Agent.create(
    name="Support Agent",
    config={
        "system_prompt": "Use the knowledge base to answer questions accurately."
    }
)

# Query with retrieval
response = agent.chat(
    message="What's your return policy?",
    retrieval=True,  # Enable RAG
    top_k=3
)
```

## Memory Operations

### Reading Memory

```python
# Retrieve conversation context
context = agent.memory.get_context(session_id="sess_123")

# Get user profile from persistent memory
profile = agent.memory.get(key="user:profile:user_456")

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

# Session context for current interaction
context = SessionContext(
    session_id="sess_123",
    user_id="user_789",
    agent_id="agent_abc123",
    start_time="2024-01-15T10:00:00Z"
)
```

## Memory Management Best Practices

### 1. Define Clear Memory Scope

Determine what information is relevant to store:
- User preferences: Persistent memory
- Conversation context: Session-based
- General knowledge: Vector storage
- Configuration data: Key-value store

### 2. Implement Data Retention Policies

```python
config = {
    "retention": {
        "session": {"hours": 24},
        "persistent": {"days": 365},
        "keyvalue": {"days": 90, "ttl": 3600},
        "vector": {"days": -1}  # Never auto-delete
    }
}
```

### 3. Ensure Privacy Compliance

- Encrypt sensitive data
- Implement access controls
- Support data deletion requests (GDPR)
- Log memory access for auditing

### 4. Optimize for Performance

- Use pagination for large histories
- Implement caching for frequent queries
- Compress old conversations
- Configure appropriate TTLs

## Memory APIs

### REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /agents/{id}/memory | Get agent memory config |
| POST | /agents/{id}/memory | Update memory settings |
| GET | /sessions/{id}/history | Get conversation history |
| POST | /memory/search | Semantic search |
| GET | /memory/kv/{key} | Get key-value pair |
| PUT | /memory/kv/{key} | Set key-value pair |

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
