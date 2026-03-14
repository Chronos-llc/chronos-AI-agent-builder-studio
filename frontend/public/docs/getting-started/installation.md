---
sidebar_position: 2
title: Installation
---

# Installation

Set up Chronos Studio in your development environment.

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Node.js | 18.0+ | 20.0+ |
| Python | 3.10+ | 3.11+ |
| RAM | 4 GB | 8 GB+ |
| OS | macOS, Linux, Windows (WSL2) | macOS / Linux |

## Install via npm (Recommended)

```bash
npm install -g @chronos-studio/cli
```

Verify the installation:

```bash
chronos --version
# chronos-studio/cli v1.0.0
```

## Install via pip

```bash
pip install chronos-studio
```

Or with a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install chronos-studio
```

## Install via Docker

```bash
docker pull chronosstudio/cli:latest
docker run -it chronosstudio/cli chronos --version
```

## Authentication

### Interactive Login

```bash
chronos login
```

Opens your browser for OAuth authentication. Your credentials are stored securely at `~/.chronos/credentials.json`.

### API Key (CI/CD)

For automated environments:

```bash
export CHRONOS_API_KEY=your_api_key_here
```

Generate API keys in the [Dashboard → Settings → API Keys](https://app.mohex.org/settings/api-keys).

## SDK Installation

### Python SDK

```bash
pip install chronos-sdk
```

```python
from chronos import ChronosClient

client = ChronosClient(api_key="your_key")
agent = client.agents.get("my-agent")
response = agent.chat("Hello!")
print(response.message)
```

### JavaScript/TypeScript SDK

```bash
npm install @chronos-studio/sdk
```

```typescript
import { ChronosClient } from '@chronos-studio/sdk';

const client = new ChronosClient({ apiKey: 'your_key' });
const agent = await client.agents.get('my-agent');
const response = await agent.chat('Hello!');
console.log(response.message);
```

## Verify Your Setup

```bash
chronos doctor
```

This checks your environment, authentication, and connectivity:

```
✓ CLI version: 1.0.0
✓ Node.js: v20.11.0
✓ Authentication: Valid (expires in 29 days)
✓ API connectivity: OK (latency: 45ms)
✓ Workspace: chronos-studio (3 agents deployed)
```

---

## Next Steps

- [Quickstart](./quickstart) — Build and deploy your first agent
- [Core Concepts](./concepts) — Understand the Chronos architecture
