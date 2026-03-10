---
sidebar_position: 1
title: Installation
---

# Installation

This guide covers how to set up your development environment to work with Chronos Studio.

## Prerequisites

Before installing, ensure you have:

- **Node.js** 18.x or higher
- **Python** 3.9 or higher (for SDK usage)
- **npm** or **yarn** package manager
- A Chronos Studio account ([sign up](https://chronos.studio))

## Quick Install

### Using npm (Recommended)
```bash
npm install -g chronos-cli
```

### Using yarn
```bash
yarn global add chronos-cli
```

### Verify Installation
```bash
chronos --version
# Output: chronos/1.0.0
```

## SDK Installation

### Python SDK
```bash
pip install chronos-sdk
```

### Node.js SDK
```bash
npm install chronos-sdk
```

## Project Setup

### Create a New Project
```bash
chronos init my-agent-project
cd my-agent-project
```

### Project Structure
```
my-agent-project/
├── agents/
│   └── config.yaml
├── tools/
│   └── custom_tools.py
├── .env
└── chronos.json
```

## Environment Configuration

### Create .env File
```bash
# .env
CHRONOS_API_KEY=sk_live_...
CHRONOS_ORG_ID=org_...
```

### Using Environment Variables
```python
from chronos import Chronos

client = Chronos(
    api_key=os.getenv("CHRONOS_API_KEY"),
    organization=os.getenv("CHRONOS_ORG_ID")
)
```

## Docker Installation

### Using Docker
```bash
# Pull the Chronos CLI image
docker pull chronos/cli:latest

# Run commands
docker run --rm -it \
  -v $(pwd):/app \
  -e CHRONOS_API_KEY=$CHRONOS_API_KEY \
  chronos_cli agent list
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  chronos:
    image: chronos/cli:latest
    volumes:
      - .:/app
    environment:
      - CHRONOS_API_KEY=${CHRONOS_API_KEY}
```

## Local Development Server

### Start Local Server
```bash
chronos dev
```

This starts:
- Development API server on `http://localhost:3001`
- Dashboard on `http://localhost:3000`

### Configuration
```json
// chronos.config.json
{
  "dev": {
    "port": 3001,
    "dashboard": "http://localhost:3000"
  }
}
```

## System Requirements

### Minimum Requirements
- 2GB RAM
- 1 CPU core
- 1GB disk space

### Recommended Requirements
- 4GB+ RAM
- 2+ CPU cores
- 5GB+ disk space

## Troubleshooting

### Common Issues

**API Key Not Found**
```bash
# Set environment variable
export CHRONOS_API_KEY="sk_live_..."

# Or use CLI flag
chronos agent list --api-key sk_live_...
```

**Permission Denied**
```bash
# Fix npm permissions
sudo chown -R $(whoami) ~/.npm

# Or use nvm for Node version management
```

**Connection Timeout**
- Check firewall settings
- Verify network connectivity
- Ensure correct API endpoint

## Next Steps

- [Quick Start Guide](/docs/getting-started/quickstart)
- [Build Your First Agent](/docs/getting-started/first-agent)
- [Core Concepts](/docs/getting-started/concepts)
