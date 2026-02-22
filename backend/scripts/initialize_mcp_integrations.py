#!/usr/bin/env python3
"""
Script to initialize MCP server integrations in the Chronos Hub Marketplace
This script can be run standalone or imported during application startup
"""

import asyncio
import sys
import os
import secrets
from typing import Optional
from datetime import datetime, UTC

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.integration import Integration as IntegrationModel
from app.models.integration import IntegrationStatus, IntegrationVisibility
from app.models.user import User as UserModel


SEED_AUTHOR_EMAIL = os.getenv("CHRONOS_SEED_AUTHOR_EMAIL", "integrations.seed@chronos.local")
SEED_AUTHOR_USERNAME = os.getenv("CHRONOS_SEED_AUTHOR_USERNAME", "chronos_integrations_seed")


async def _get_or_create_seed_author(db: AsyncSession) -> UserModel:
    existing = (
        await db.execute(
            select(UserModel).where(
                (UserModel.email == SEED_AUTHOR_EMAIL) | (UserModel.username == SEED_AUTHOR_USERNAME)
            )
        )
    ).scalar_one_or_none()
    if existing:
        return existing

    seed_user = UserModel(
        email=SEED_AUTHOR_EMAIL,
        username=SEED_AUTHOR_USERNAME,
        full_name="Chronos Integrations Seed",
        hashed_password=get_password_hash(secrets.token_urlsafe(32)),
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )
    db.add(seed_user)
    await db.flush()
    return seed_user


async def create_mcp_integrations(
    db: AsyncSession,
    default_user_id: int,
    integrations_data: Optional[list[dict]] = None,
) -> tuple[int, int]:
    """Create the MCP server integrations in the database"""
    
    # Define the MCP integrations
    mcp_integrations = [
        {
            "name": "Web Browser MCP Server",
            "description": "Web Browser MCP Server provides browser automation capabilities using the Model Context Protocol. Enables web browsing, form interaction, content extraction, and web-based task automation.",
            "integration_type": "mcp_server",
            "category": "automation",
            "icon": "🌐",
            "documentation_url": "https://modelcontextprotocol.io/",
            "version": "1.0.0",
            "is_public": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "default": "uv",
                        "description": "Command to run the MCP server"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["tool", "run", "web-browser-mcp-server"],
                        "description": "Arguments for the MCP server command"
                    },
                    "env": {
                        "type": "object",
                        "properties": {
                            "REQUEST_TIMEOUT": {
                                "type": "string",
                                "default": "30",
                                "description": "Request timeout in seconds"
                            }
                        },
                        "default": {
                            "REQUEST_TIMEOUT": "30"
                        }
                    },
                    "server_url": {
                        "type": "string",
                        "default": "http://localhost:8080",
                        "description": "Server URL for the Web Browser MCP server"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30000,
                        "description": "Request timeout in milliseconds"
                    }
                },
                "required": ["command", "args"]
            },
            "credentials_schema": {
                "type": "object",
                "properties": {
                    "api_key": {
                        "type": "string",
                        "description": "API key for authentication",
                        "sensitive": True
                    }
                }
            },
            "supported_features": [
                "web_browsing",
                "form_interaction",
                "content_extraction",
                "web_automation",
                "browser_control",
                "web_content_processing"
            ]
        },
        {
            "name": "Time MCP Server",
            "description": "MCP server providing time and timezone conversion tools for AI assistants to handle localized time data and calculations.",
            "integration_type": "mcp_server",
            "category": "utilities",
            "icon": "⏰",
            "documentation_url": "https://github.com/modelcontextprotocol/servers",
            "version": "0.0.0",
            "is_public": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "server_url": {
                        "type": "string",
                        "default": "http://localhost:8081",
                        "description": "Server URL for the Time MCP server"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30000,
                        "description": "Request timeout in milliseconds"
                    },
                    "default_timezone": {
                        "type": "string",
                        "default": "UTC",
                        "description": "Default timezone for time operations"
                    },
                    "enable_timezone_conversion": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable timezone conversion features"
                    }
                },
                "required": ["server_url"]
            },
            "credentials_schema": {
                "type": "object",
                "properties": {
                    "api_key": {
                        "type": "string",
                        "description": "API key for authentication",
                        "sensitive": True
                    }
                }
            },
            "supported_features": [
                "current_time",
                "timezone_conversion",
                "time_calculations",
                "time_formatting",
                "timezone_listing",
                "localized_time_handling"
            ],
            "repository": {
                "source": "github",
                "subfolder": "src/time",
                "url": "https://github.com/modelcontextprotocol/servers"
            }
        },
        {
            "name": "Notion MCP Server",
            "description": "Official Notion MCP server for integrating with Notion's Model Context Protocol services. Provides access to Notion databases, pages, and workspace management through MCP.",
            "integration_type": "mcp_server",
            "category": "productivity",
            "icon": "📚",
            "documentation_url": "https://developers.notion.com/",
            "version": "1.0.1",
            "is_public": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "remotes": {
                        "type": "array",
                        "default": [
                            {
                                "type": "streamable-http",
                                "url": "https://mcp.notion.com/mcp"
                            },
                            {
                                "type": "sse",
                                "url": "https://mcp.notion.com/sse"
                            }
                        ],
                        "description": "Remote connection endpoints for Notion MCP server"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30000,
                        "description": "Request timeout in milliseconds"
                    },
                    "enable_streaming": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable streaming connections to Notion"
                    }
                },
                "required": ["remotes"]
            },
            "credentials_schema": {
                "type": "object",
                "properties": {
                    "notion_api_key": {
                        "type": "string",
                        "description": "Notion API key for authentication",
                        "sensitive": True
                    },
                    "integration_token": {
                        "type": "string",
                        "description": "Notion integration token",
                        "sensitive": True
                    }
                },
                "required": ["notion_api_key"]
            },
            "supported_features": [
                "database_access",
                "page_management",
                "workspace_management",
                "real_time_updates",
                "content_search",
                "collaboration_features",
                "notion_blocks",
                "rich_text_editing"
            ],
            "repository": {}
        },
        {
            "name": "GitHub MCP Server",
            "description": "GitHub MCP server for managing repositories, issues, and searching code via GitHub API. Provides comprehensive GitHub integration through the Model Context Protocol.",
            "integration_type": "mcp_server",
            "category": "development",
            "icon": "🐙",
            "documentation_url": "https://docs.github.com/en/rest",
            "version": "0.0.0",
            "is_public": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "server_url": {
                        "type": "string",
                        "default": "http://localhost:8082",
                        "description": "Server URL for the GitHub MCP server"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30000,
                        "description": "Request timeout in milliseconds"
                    },
                    "api_base_url": {
                        "type": "string",
                        "default": "https://api.github.com",
                        "description": "GitHub API base URL"
                    },
                    "enable_webhooks": {
                        "type": "boolean",
                        "default": False,
                        "description": "Enable GitHub webhook integration"
                    },
                    "webhook_secret": {
                        "type": "string",
                        "default": "",
                        "description": "Webhook secret for verification"
                    }
                },
                "required": ["server_url"]
            },
            "credentials_schema": {
                "type": "object",
                "properties": {
                    "github_token": {
                        "type": "string",
                        "description": "GitHub personal access token",
                        "sensitive": True
                    },
                    "app_id": {
                        "type": "string",
                        "description": "GitHub App ID (optional)",
                        "sensitive": False
                    },
                    "app_private_key": {
                        "type": "string",
                        "description": "GitHub App private key (optional)",
                        "sensitive": True
                    }
                },
                "required": ["github_token"]
            },
            "supported_features": [
                "repository_management",
                "issue_tracking",
                "code_search",
                "pull_requests",
                "webhook_integration",
                "user_management",
                "organization_management",
                "github_actions"
            ],
            "repository": {
                "source": "github",
                "subfolder": "src/github",
                "url": "https://github.com/modelcontextprotocol/servers-archived"
            }
        },
        {
            "name": "ElevenLabs MCP Server",
            "description": "ElevenLabs MCP server for AI voice generation and text-to-speech capabilities. Provides high-quality voice synthesis through the ElevenLabs API using the Model Context Protocol.",
            "integration_type": "mcp_server",
            "category": "ai",
            "icon": "🎙️",
            "documentation_url": "https://elevenlabs.io/docs",
            "version": "1.0.0",
            "is_public": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "default": "uvx",
                        "description": "Command to run the MCP server"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["elevenlabs-mcp"],
                        "description": "Arguments for the MCP server command"
                    },
                    "server_url": {
                        "type": "string",
                        "default": "http://localhost:8083",
                        "description": "Server URL for the ElevenLabs MCP server"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 60000,
                        "description": "Request timeout in milliseconds (longer for voice generation)"
                    },
                    "default_voice": {
                        "type": "string",
                        "default": "Rachel",
                        "description": "Default voice for text-to-speech"
                    },
                    "enable_streaming": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable streaming voice generation"
                    }
                },
                "required": ["command", "args"]
            },
            "credentials_schema": {
                "type": "object",
                "properties": {
                    "elevenlabs_api_key": {
                        "type": "string",
                        "description": "ElevenLabs API key for authentication",
                        "sensitive": True
                    }
                },
                "required": ["elevenlabs_api_key"]
            },
            "supported_features": [
                "text_to_speech",
                "voice_generation",
                "voice_cloning",
                "audio_streaming",
                "multi_language_support",
                "emotional_voices",
                "voice_customization",
                "audio_quality_control"
            ],
            "env": {
                "ELEVENLABS_API_KEY": "<insert-your-api-key-here>"
            }
        },
        {
            "name": "HowToCook MCP Server",
            "description": "HowToCook MCP server for cooking-related capabilities and recipe management. Provides access to cooking instructions, recipe databases, and culinary knowledge through the Model Context Protocol.",
            "integration_type": "mcp_server",
            "category": "lifestyle",
            "icon": "👨‍🍳",
            "documentation_url": "https://howtocook.io/docs",
            "version": "1.0.0",
            "is_public": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "default": "npx",
                        "description": "Command to run the MCP server"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["-y", "howtocook-mcp"],
                        "description": "Arguments for the MCP server command"
                    },
                    "server_url": {
                        "type": "string",
                        "default": "http://localhost:8084",
                        "description": "Server URL for the HowToCook MCP server"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30000,
                        "description": "Request timeout in milliseconds"
                    },
                    "default_cuisine": {
                        "type": "string",
                        "default": "international",
                        "description": "Default cuisine type for recipes"
                    },
                    "enable_nutrition_info": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable nutritional information in responses"
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 10,
                        "description": "Maximum number of results to return"
                    }
                },
                "required": ["command", "args"]
            },
            "credentials_schema": {
                "type": "object",
                "properties": {
                    "api_key": {
                        "type": "string",
                        "description": "API key for HowToCook service",
                        "sensitive": True
                    }
                }
            },
            "supported_features": [
                "recipe_search",
                "cooking_instructions",
                "ingredient_analysis",
                "meal_planning",
                "nutritional_information",
                "cuisine_specialization",
                "cooking_techniques",
                "dietary_restrictions",
                "food_pairing_suggestions"
            ]
        },
        {
            "name": "MiniMax MCP Server",
            "description": "MiniMax MCP server for AI capabilities through the MiniMax API. Provides advanced AI features including text generation, audio processing, and multimedia capabilities using the Model Context Protocol.",
            "integration_type": "mcp_server",
            "category": "ai",
            "icon": "🤖",
            "documentation_url": "https://api.minimaxi.chat/docs",
            "version": "1.0.0",
            "is_public": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "default": "uvx",
                        "description": "Command to run the MCP server"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["minimax-mcp"],
                        "description": "Arguments for the MCP server command"
                    },
                    "server_url": {
                        "type": "string",
                        "default": "http://localhost:8085",
                        "description": "Server URL for the MiniMax MCP server"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 60000,
                        "description": "Request timeout in milliseconds"
                    },
                    "api_host": {
                        "type": "string",
                        "default": "https://api.minimaxi.chat",
                        "description": "MiniMax API host URL"
                    },
                    "resource_mode": {
                        "type": "string",
                        "default": "url",
                        "enum": ["url", "local"],
                        "description": "Resource mode for audio/image/video (url or local)"
                    },
                    "local_output_dir": {
                        "type": "string",
                        "default": "./minimax_output",
                        "description": "Local directory for downloaded resources"
                    },
                    "enable_streaming": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable streaming responses"
                    }
                },
                "required": ["command", "args"]
            },
            "credentials_schema": {
                "type": "object",
                "properties": {
                    "minimax_api_key": {
                        "type": "string",
                        "description": "MiniMax API key for authentication",
                        "sensitive": True
                    }
                },
                "required": ["minimax_api_key"]
            },
            "supported_features": [
                "text_generation",
                "ai_chat",
                "audio_processing",
                "image_generation",
                "video_processing",
                "multimedia_analysis",
                "content_creation",
                "language_translation",
                "code_generation"
            ],
            "env": {
                "MINIMAX_API_KEY": "<insert-your-api-key-here>",
                "MINIMAX_MCP_BASE_PATH": "./minimax_output",
                "MINIMAX_API_HOST": "https://api.minimaxi.chat",
                "MINIMAX_API_RESOURCE_MODE": "url"
            }
        },
        {
            "name": "Chrome MCP Server",
            "description": "Chrome Browser MCP Server providing browser automation capabilities via streamable HTTP. Enables web browsing, form interaction, and content extraction using a remote Chrome instance.",
            "integration_type": "mcp_server",
            "category": "automation",
            "icon": "🌐",
            "documentation_url": "https://github.com/modelcontextprotocol/servers",
            "version": "1.0.0",
            "is_public": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "server_url": {
                        "type": "string",
                        "default": "http://127.0.0.1:12306/mcp",
                        "description": "Server URL for the Chrome MCP server"
                    },
                    "connection_type": {
                        "type": "string",
                        "default": "streamableHttp",
                        "enum": ["streamableHttp", "sse", "stdio"],
                        "description": "Connection type"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30000,
                        "description": "Request timeout in milliseconds"
                    }
                },
                "required": ["server_url"]
            },
            "credentials_schema": {
                "type": "object",
                "properties": {
                    "api_key": {
                        "type": "string",
                        "description": "API key for authentication (optional)",
                        "sensitive": True
                    }
                }
            },
            "supported_features": [
                "web_browsing",
                "browser_automation",
                "dom_manipulation",
                "content_extraction",
                "screenshot_capture"
            ]
        },
        {
            "name": "Serper MCP Server",
            "description": "Serper MCP Server for web search capabilities using the Serper API. Provides Google search results, knowledge graph data, and web content through the Model Context Protocol.",
            "integration_type": "mcp_server",
            "category": "search",
            "icon": "🔍",
            "documentation_url": "https://serper.dev/docs",
            "version": "1.0.0",
            "is_public": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "default": "uvx",
                        "description": "Command to run the MCP server"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["serper-mcp-server"],
                        "description": "Arguments for the MCP server command"
                    },
                    "server_url": {
                        "type": "string",
                        "default": "http://localhost:8086",
                        "description": "Server URL for the Serper MCP server"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30000,
                        "description": "Request timeout in milliseconds"
                    }
                },
                "required": ["command", "args"]
            },
            "credentials_schema": {
                "type": "object",
                "properties": {
                    "serper_api_key": {
                        "type": "string",
                        "description": "Serper API key for authentication",
                        "sensitive": True
                    }
                },
                "required": ["serper_api_key"]
            },
            "supported_features": [
                "web_search",
                "google_search",
                "knowledge_graph",
                "web_content",
                "search_results"
            ],
            "env": {
                "SERPER_API_KEY": "<Your Serper API key>"
            }
        },
        {
            "name": "Ask UI MCP Server",
            "description": "Ask UI MCP Server for AI-powered user interface interactions and automation. Provides UI testing, interaction automation, and visual regression capabilities through the Model Context Protocol.",
            "integration_type": "mcp_server",
            "category": "ai",
            "icon": "🤖",
            "documentation_url": "https://github.com/ask-ui/ask-ui",
            "version": "1.0.0",
            "is_public": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "default": "npx",
                        "description": "Command to run the MCP server"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["-y", "mcp-ask-ui"],
                        "description": "Arguments for the MCP server command"
                    },
                    "server_url": {
                        "type": "string",
                        "default": "http://localhost:8087",
                        "description": "Server URL for the Ask UI MCP server"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 60000,
                        "description": "Request timeout in milliseconds"
                    }
                },
                "required": ["command", "args"]
            },
            "credentials_schema": {
                "type": "object",
                "properties": {
                    "moonshot_api_key": {
                        "type": "string",
                        "description": "Moonshot API key for authentication (optional)",
                        "sensitive": True
                    },
                    "ppio_api_key": {
                        "type": "string",
                        "description": "PPIO API key for authentication (optional)",
                        "sensitive": True
                    },
                    "minimax_api_key": {
                        "type": "string",
                        "description": "MiniMax API key for authentication (optional)",
                        "sensitive": True
                    }
                }
            },
            "supported_features": [
                "ui_automation",
                "visual_testing",
                "interaction_automation",
                "ui_content_extraction",
                "visual_regression"
            ],
            "env": {
                "MOONSHOT_API_KEY": "all keys are optional",
                "PPIO_API_KEY": "all keys are optional",
                "MINIMAX_API_KEY": "all keys are optional"
            }
        },
        {
            "name": "302AI Sandbox MCP Server",
            "description": "302AI Sandbox MCP Server for AI model testing and experimentation. Provides a sandbox environment for testing AI models and APIs through the Model Context Protocol.",
            "integration_type": "mcp_server",
            "category": "ai",
            "icon": "🧪",
            "documentation_url": "https://302.ai/docs",
            "version": "1.0.0",
            "is_public": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "default": "npx",
                        "description": "Command to run the MCP server"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["-y", "@302ai/sandbox-mcp"],
                        "description": "Arguments for the MCP server command"
                    },
                    "server_url": {
                        "type": "string",
                        "default": "http://localhost:8088",
                        "description": "Server URL for the 302AI Sandbox MCP server"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 60000,
                        "description": "Request timeout in milliseconds"
                    }
                },
                "required": ["command", "args"]
            },
            "credentials_schema": {
                "type": "object",
                "properties": {
                    "302ai_api_key": {
                        "type": "string",
                        "description": "302AI API key for authentication",
                        "sensitive": True
                    }
                },
                "required": ["302ai_api_key"]
            },
            "supported_features": [
                "ai_model_testing",
                "sandbox_environment",
                "model_experimentation",
                "api_testing",
                "ai_development"
            ],
            "env": {
                "302AI_API_KEY": "YOUR_API_KEY_HERE"
            }
        },
        {
            "name": "Slack MCP Server",
            "description": "Slack MCP Server for communication and collaboration through Slack. Provides messaging, file sharing, and team collaboration capabilities via the Model Context Protocol.",
            "integration_type": "mcp_server",
            "category": "communication",
            "icon": "💬",
            "documentation_url": "https://api.slack.com/",
            "version": "1.0.0",
            "is_public": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "default": "npx",
                        "description": "Command to run the MCP server"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["-y", "@modelcontextprotocol/server-slack"],
                        "description": "Arguments for the MCP server command"
                    },
                    "server_url": {
                        "type": "string",
                        "default": "http://localhost:8089",
                        "description": "Server URL for the Slack MCP server"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30000,
                        "description": "Request timeout in milliseconds"
                    }
                },
                "required": ["command", "args"]
            },
            "credentials_schema": {
                "type": "object",
                "properties": {
                    "slack_bot_token": {
                        "type": "string",
                        "description": "Slack bot token for authentication",
                        "sensitive": True
                    },
                    "slack_team_id": {
                        "type": "string",
                        "description": "Slack team ID",
                        "sensitive": False
                    },
                    "slack_channel_ids": {
                        "type": "string",
                        "description": "Comma-separated Slack channel IDs",
                        "sensitive": False
                    }
                },
                "required": ["slack_bot_token", "slack_team_id"]
            },
            "supported_features": [
                "messaging",
                "file_sharing",
                "team_collaboration",
                "channel_management",
                "real_time_communication"
            ],
            "env": {
                "SLACK_BOT_TOKEN": "xoxb-your-bot-token",
                "SLACK_TEAM_ID": "T01234567",
                "SLACK_CHANNEL_IDS": "C01234567, C76543210"
            }
        },
        {
            "name": "Playwright MCP Server",
            "description": "Playwright MCP server for browser automation tasks including navigation, interaction, extraction, and end-to-end web workflows.",
            "integration_type": "mcp_server",
            "category": "automation",
            "icon": "https://playwright.dev/img/playwright-logo.svg",
            "documentation_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/playwright",
            "version": "1.0.0",
            "is_public": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "default": "npx",
                        "description": "Command to run the Playwright MCP server"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["-y", "@modelcontextprotocol/server-playwright"],
                        "description": "Arguments for the Playwright MCP server command"
                    },
                    "server_url": {
                        "type": "string",
                        "default": "http://localhost:8091",
                        "description": "Server URL for the Playwright MCP server"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 45000,
                        "description": "Request timeout in milliseconds"
                    }
                },
                "required": ["command", "args"]
            },
            "credentials_schema": {
                "type": "object",
                "properties": {}
            },
            "supported_features": [
                "browser_navigation",
                "form_interaction",
                "web_extraction",
                "screenshot_capture",
                "ui_testing"
            ]
        },
        {
            "name": "Twilio MCP Server",
            "description": "Twilio MCP server for telephony workflows including messaging, voice routing, and programmable communications via Twilio Labs MCP.",
            "integration_type": "mcp_server",
            "category": "communications",
            "icon": "https://i.postimg.cc/c45jzmKM/download_16.png",
            "documentation_url": "https://www.npmjs.com/package/@twilio-alpha/mcp",
            "version": "1.0.0",
            "is_public": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "default": "npx",
                        "description": "Command to run the Twilio MCP server"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["-y", "@twilio-alpha/mcp", "{account_sid}/{api_key}:{api_secret}"],
                        "description": "Arguments for the Twilio MCP server command"
                    },
                    "server_url": {
                        "type": "string",
                        "default": "http://localhost:8090",
                        "description": "Server URL for the Twilio MCP server"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30000,
                        "description": "Request timeout in milliseconds"
                    }
                },
                "required": ["command", "args"]
            },
            "credentials_schema": {
                "type": "object",
                "properties": {
                    "account_sid": {
                        "type": "string",
                        "description": "Twilio Account SID",
                        "sensitive": True
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Twilio API Key",
                        "sensitive": True
                    },
                    "api_secret": {
                        "type": "string",
                        "description": "Twilio API Secret",
                        "sensitive": True
                    }
                },
                "required": ["account_sid", "api_key", "api_secret"]
            },
            "supported_features": [
                "sms",
                "voice",
                "phone_numbers",
                "call_automation",
                "telephony_workflows"
            ],
            "env": {
                "TWILIO_ACCOUNT_SID": "<YOUR_ACCOUNT_SID>",
                "TWILIO_API_KEY": "<YOUR_API_KEY>",
                "TWILIO_API_SECRET": "<YOUR_API_SECRET>"
            }
        },
        {
            "name": "Google Maps MCP Server",
            "description": "Google Maps MCP Server for location services and mapping capabilities. Provides geocoding, directions, place search, and map visualization through the Model Context Protocol.",
            "integration_type": "mcp_server",
            "category": "geospatial",
            "icon": "🗺️",
            "documentation_url": "https://developers.google.com/maps",
            "version": "1.0.0",
            "is_public": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "default": "docker",
                        "description": "Command to run the MCP server"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["run", "-i", "--rm", "-e", "GOOGLE_MAPS_API_KEY", "mcp/google-maps"],
                        "description": "Arguments for the MCP server command"
                    },
                    "server_url": {
                        "type": "string",
                        "default": "http://localhost:8090",
                        "description": "Server URL for the Google Maps MCP server"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30000,
                        "description": "Request timeout in milliseconds"
                    }
                },
                "required": ["command", "args"]
            },
            "credentials_schema": {
                "type": "object",
                "properties": {
                    "google_maps_api_key": {
                        "type": "string",
                        "description": "Google Maps API key for authentication",
                        "sensitive": True
                    }
                },
                "required": ["google_maps_api_key"]
            },
            "supported_features": [
                "geocoding",
                "directions",
                "place_search",
                "map_visualization",
                "distance_matrix",
                "location_services"
            ],
            "env": {
                "GOOGLE_MAPS_API_KEY": "<YOUR_API_KEY>"
            }
        }
    ]
    
    if integrations_data is not None:
        mcp_integrations = integrations_data

    created_count = 0
    updated_count = 0
    
    # Create integrations
    for integration_data in mcp_integrations:
        # Check if integration already exists
        result = await db.execute(
            select(IntegrationModel).where(IntegrationModel.name == integration_data["name"])
        )
        existing = result.scalars().first()
        
        # Upsert and normalize to published/public for curated seed catalog
        allowed_fields = set(IntegrationModel.__table__.columns.keys())
        payload = {k: v for k, v in integration_data.items() if k in allowed_fields}
        payload.update(
            {
                "status": IntegrationStatus.PUBLISHED.value,
                "visibility": IntegrationVisibility.PUBLIC.value,
                "is_public": True,
                "author_id": default_user_id,
                "submitted_at": datetime.now(UTC),
                "reviewed_at": datetime.now(UTC),
                "published_at": datetime.now(UTC),
            }
        )

        if existing:
            for key, value in payload.items():
                if key in allowed_fields or key == "author_id":
                    setattr(existing, key, value)
            updated_count += 1
            print(f"[UPSERT] Updated integration: {integration_data['name']}")
            continue

        integration = IntegrationModel(**payload)
        db.add(integration)
        created_count += 1
        print(f"[OK] Created integration: {integration_data['name']}")

    return created_count, updated_count


async def initialize_mcp_integrations() -> bool:
    """Initialize MCP integrations - can be called during app startup"""
    
    try:
        db_gen = get_db()
        db = await anext(db_gen)
        
        # Find or create a default user for integrations
        result = await db.execute(select(UserModel).limit(1))
        default_user = result.scalars().first()

        if not default_user:
            default_user = await _get_or_create_seed_author(db)
            print(f"[INFO] Created seed author user: {default_user.email} (ID: {default_user.id})")

        print(f"[INFO] Using user: {default_user.email} (ID: {default_user.id})")
        
        # Create MCP integrations
        created_count, updated_count = await create_mcp_integrations(db, default_user.id)
        
        if created_count > 0 or updated_count > 0:
            await db.commit()
            print(
                f"[OK] Seed sync complete. Created {created_count}, updated {updated_count} "
                "MCP integrations for the Chronos Hub Marketplace."
            )
        else:
            print("[INFO] All MCP server integrations already exist in the database.")
            
        # Show summary
        result = await db.execute(
            select(IntegrationModel).where(IntegrationModel.integration_type == "mcp_server")
        )
        mcp_servers = result.scalars().all()
        
        print(f"\n[INFO] Summary: {len(mcp_servers)} MCP server integrations available:")
        for server in mcp_servers:
            print(f"  - {server.name} v{server.version} ({server.category})")
            
        await db.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error initializing MCP integrations: {e}")
        if 'db' in locals():
            await db.rollback()
            await db.close()
        return False


async def get_default_user_id() -> Optional[int]:
    """Get the ID of the first user in the database"""
    try:
        db_gen = get_db()
        db = await anext(db_gen)
        
        result = await db.execute(select(UserModel).limit(1))
        default_user = result.scalars().first()
        
        await db.close()
        return default_user.id if default_user else None
        
    except Exception as e:
        print(f"[ERROR] Error getting default user: {e}")
        return None


if __name__ == "__main__":
    print("[INFO] Initializing MCP server integrations for Chronos Hub Marketplace...")
    success = asyncio.run(initialize_mcp_integrations())
    
    if success:
        print("\n[OK] MCP integrations are ready to use.")
        print("[INFO] You can now install these MCP servers from the Chronos Hub Marketplace.")
    else:
        print("\n[ERROR] Failed to initialize MCP integrations.")
        sys.exit(1)
