---
sidebar_position: 5
title: Databases
---

# Database Integrations

Give your agents access to structured data through database connections.

## PostgreSQL

```yaml
tools:
  - name: database
    mcp: true
    server:
      command: npx
      args: ["-y", "@modelcontextprotocol/server-postgres"]
      env:
        DATABASE_URL: ${DATABASE_URL}
```

Or with a custom tool:

```python
from chronos.tools import tool
import asyncpg

@tool(name="query_users", description="Look up user data from the database")
async def query_users(email: str = None, user_id: str = None) -> dict:
    conn = await asyncpg.connect(env("DATABASE_URL"))
    try:
        if email:
            row = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
        elif user_id:
            row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        else:
            return {"error": "Provide email or user_id"}
        return dict(row) if row else {"error": "User not found"}
    finally:
        await conn.close()
```

## MongoDB

```python
from chronos.tools import tool
from motor.motor_asyncio import AsyncIOMotorClient

@tool(name="search_products", description="Search the product catalog")
async def search_products(query: str, category: str = None) -> list[dict]:
    client = AsyncIOMotorClient(env("MONGODB_URL"))
    db = client.catalog

    filter_query = {"$text": {"$search": query}}
    if category:
        filter_query["category"] = category

    cursor = db.products.find(filter_query).limit(10)
    return [doc async for doc in cursor]
```

## Redis

```python
from chronos.tools import tool
import redis.asyncio as redis

@tool(name="get_session", description="Retrieve active user session data")
async def get_session(session_id: str) -> dict:
    r = redis.from_url(env("REDIS_URL"))
    data = await r.hgetall(f"session:{session_id}")
    return {k.decode(): v.decode() for k, v in data.items()}
```

## Vector Databases

For RAG (Retrieval-Augmented Generation) workflows:

### Pinecone

```python
from chronos.tools import tool
from pinecone import Pinecone

@tool(name="search_knowledge", description="Semantic search over knowledge base")
async def search_knowledge(query: str, top_k: int = 5) -> list[dict]:
    pc = Pinecone(api_key=env("PINECONE_API_KEY"))
    index = pc.Index("knowledge-base")

    # Chronos auto-generates embeddings
    results = index.query(vector=await embed(query), top_k=top_k)
    return [{"text": m.metadata["text"], "score": m.score} for m in results.matches]
```

## Security Best Practices

1. **Read-only access** — Give agents SELECT-only database credentials
2. **Row-level security** — Limit what data agents can see
3. **Query parameterization** — Always use parameterized queries
4. **Connection pooling** — Use pools for production workloads
5. **Audit logging** — Log all database queries from agents

---

## Next Steps

- [API Reference](../api-reference/overview) — Full REST API documentation
- [Guides](../guides/customer-support-bot) — Build real-world agents
