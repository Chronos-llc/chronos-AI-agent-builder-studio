# MCP Server Integrations for Chronos Hub Marketplace

This document explains the MCP (Model Context Protocol) server integrations that have been added to the Chronos AI Agent Builder Studio.

## Overview

Two MCP server integrations have been added to the Chronos Hub Marketplace:

1. **Playwright MCP Server** - Advanced web automation and testing capabilities
2. **Memory MCP Server** - Persistent memory and conversation history management

## Installation

The MCP server integrations are automatically initialized when the Chronos backend starts. They will appear as installable integrations in the Chronos Hub Marketplace.

### Manual Initialization

If you need to initialize the MCP integrations manually, you can run:

```bash
cd backend
python scripts/run_initialize_mcp_integrations.py
```

## Playwright MCP Server

### Configuration

The Playwright MCP Server integration includes the following configuration options:

```json
{
  "command": "npx",
  "args": ["@playwright/mcp@latest", "--headless", "--vision"],
  "server_url": "http://localhost:8080",
  "timeout": 30000,
  "headless": true,
  "vision": true
}
```

### Features

- **Web Automation**: Automate web interactions and form submissions
- **Data Extraction**: Extract structured data from web pages
- **Website Testing**: Perform automated testing of web applications
- **Screenshot Capture**: Capture screenshots of web pages
- **PDF Generation**: Generate PDF documents from web pages
- **Performance Testing**: Measure website performance metrics
- **Vision Capabilities**: Advanced visual recognition and processing

### Usage

Once installed, the Playwright MCP Server can be used in your agents for:

- Web scraping and data extraction
- Automated testing workflows
- Browser automation tasks
- Visual content processing
- Performance monitoring

## Memory MCP Server

### Configuration

The Memory MCP Server integration includes the following configuration options:

```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-memory"],
  "server_url": "http://localhost:8081",
  "timeout": 30000,
  "memory_persistence": true
}
```

### Features

- **Persistent Memory**: Long-term storage of conversation context
- **Conversation History**: Complete history tracking for AI interactions
- **Context Management**: Efficient context retrieval and management
- **Memory Retrieval**: Fast access to stored memories
- **Conversation Continuity**: Seamless continuation of conversations

### Usage

Once installed, the Memory MCP Server can be used in your agents for:

- Maintaining conversation context across sessions
- Long-term memory storage for AI agents
- Context-aware decision making
- Personalized user experiences
- Historical data analysis

## Integration with Chronos Studio

Both MCP servers integrate seamlessly with the Chronos AI Agent Builder Studio:

1. **Installation**: Available through the Chronos Hub Marketplace
2. **Configuration**: Configurable via the integration settings interface
3. **Usage**: Accessible through the MCP client interface in your agents
4. **Monitoring**: Integrated with the Chronos monitoring system

## Technical Details

### Database Schema

The MCP server integrations are stored in the `integrations` table with:

- `integration_type`: "mcp_server"
- `category`: "automation" (Playwright) or "utilities" (Memory)
- `config_schema`: JSON schema for configuration
- `credentials_schema`: JSON schema for credentials
- `supported_features`: Array of supported capabilities

### API Endpoints

The integrations are accessible through the standard integrations API:

- `GET /api/v1/integrations/` - List all integrations
- `POST /api/v1/integrations/search/` - Search for MCP server integrations
- `POST /api/v1/integrations/{id}/config/` - Configure an MCP server integration

## Troubleshooting

### No Users Found

If you see the error "No user found in database", you need to create a user first:

```bash
# Create a user through the API or UI
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "securepassword"}'
```

### Integration Already Exists

If integrations already exist, the initialization script will skip them and show a summary of existing integrations.

## Development

### Adding New MCP Servers

To add additional MCP server integrations:

1. Add the integration configuration to `scripts/initialize_mcp_integrations.py`
2. Run the initialization script
3. The new integration will appear in the Chronos Hub Marketplace

### Testing

You can test the MCP integrations using the Chronos API:

```bash
# Search for MCP server integrations
curl -X POST http://localhost:8000/api/v1/integrations/search/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"types": ["mcp_server"]}'
```

## Support

For issues or questions about MCP server integrations:

- Check the Chronos documentation
- Review the MCP protocol specification
- Contact the Chronos support team

## License

The MCP server integrations are provided under the same license as the Chronos AI Agent Builder Studio.