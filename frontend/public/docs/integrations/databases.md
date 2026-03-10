---
sidebar_position: 3
title: Database Integrations
---

# Database Integrations

Connect Chronos Studio to databases for persistent storage and data retrieval.

## Supported Databases

### Relational Databases

| Database | Status |
|----------|--------|
| PostgreSQL | Supported |
| MySQL | Supported |
| SQLite | Supported |
| SQL Server | Supported |

### NoSQL Databases

| Database | Status |
|----------|--------|
| MongoDB | Supported |
| Redis | Supported |

### Cloud Databases

| Service | Status |
|---------|--------|
| Amazon RDS | Supported |
| Google Cloud SQL | Supported |
| Azure Database | Supported |
| Neon | Supported |
| PlanetScale | Supported |

## Connecting Databases

### Via Dashboard

1. Go to **Integrations** → **Databases**
2. Click **Add Database**
3. Select database type
4. Enter connection details
5. Test connection

### Via Configuration

```yaml
# chronos.yaml
databases:
  - name: production
    type: postgresql
    connection:
      host: db.example.com
      port: 5432
      database: production
      user: chronos_user
      password: "{{ secrets.DB_PASSWORD }}"
    pool_size: 10
    ssl: true
```

### Via API

```bash
curl -X POST https://api.chronos.studio/v1/databases \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production",
    "type": "postgresql",
    "connection": {
      "host": "db.example.com",
      "port": 5432,
      "database": "production",
      "user": "chronos_user"
    }
  }'
```

## Using Databases in Agents

### Query Tool

```python
from chronos.tools import DatabaseTool

tool = DatabaseTool(
    database="production",
    queries={
        "get_user": "SELECT * FROM users WHERE id = :user_id",
        "recent_orders": "SELECT * FROM orders WHERE user_id = :user_id ORDER BY created_at DESC LIMIT :limit"
    }
)
```

### Vector Store for RAG

```python
# Configure vector store
vector_store = client.vector_stores.create(
    name="knowledge_base",
    database="postgres",
    embedding_model="text-embedding-ada-002"
)

# Add documents
vector_store.add(
    documents=[
        {"content": "Our refund policy allows returns within 30 days..."},
        {"content": "We offer 24/7 customer support via chat..."}
    ]
)

# Search
results = vector_store.search("refund policy")
```

## Schema Management

### Auto-Schema Sync

```bash
# Sync database schema
chronos db sync production --watch
```

### Define Tables

```python
from chronos.db import Table, Column

class UserTable(Table):
    name = "users"
    columns = [
        Column("id", "uuid", primary_key=True),
        Column("email", "varchar(255)", unique=True),
        Column("name", "varchar(255)"),
        Column("created_at", "timestamp", default="now()")
    ]
```

## Query Builder

### Python API

```python
# Select
users = db.table("users").select("id", "email").where(
    "created_at >", "2024-01-01"
).execute()

# Insert
db.table("users").insert(
    email="user@example.com",
    name="John Doe"
)

# Update
db.table("users").where(
    "id", "user_123"
).update(status="active")

# Delete
db.table("sessions").where(
    "expires_at <", "now()"
).delete()
```

### Raw SQL

```python
result = db.query("""
    SELECT u.name, COUNT(o.id) as order_count
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE o.created_at > %s
    GROUP BY u.id
""", [start_date])
```

## Connection Pooling

```python
pool = ConnectionPool(
    database="production",
    min_size=5,
    max_size=20,
    timeout=30
)

# Automatically managed
with pool.connect() as conn:
    result = conn.query("SELECT * FROM users")
```

## Data Sync

### Bidirectional Sync

```python
sync = SyncConfiguration(
    source="postgres.production",
    target="mongo.analytics",
    tables=["users", "orders"],
    mode="realtime",  # or "batch"
    schedule="0 * * *"  # hourly for batch
)

sync.start()
```

## Security

### Encryption

- SSL/TLS for connections
- Encrypted at rest
- Secrets management

### Access Control

```python
# Row-level security
db.table("orders").configure(
    row_security=True,
    policy=lambda user: {"user_id": user.id}
)
```

## Performance Optimization

### Indexing

```python
# Create indexes
db.table("orders").create_index(
    columns=["user_id", "created_at"],
    unique=False
)
```

### Caching

```python
# Enable caching for queries
result = db.query(
    "SELECT * FROM products WHERE category = :cat",
    cat="electronics",
    cache=True,
    ttl=3600  # seconds
)
```

## Best Practices

1. **Use connection pools** - Reuse connections
2. **Parameterize queries** - Prevent SQL injection
3. **Index appropriately** - Optimize common queries
4. **Monitor performance** - Track slow queries
5. **Backup regularly** - Protect your data
