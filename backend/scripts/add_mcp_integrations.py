#!/usr/bin/env python3
"""
Script to add Playwright and Memory MCP servers to the Chronos Hub Marketplace
"""

import asyncio
import sys
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import get_db
from app.models.integration import Integration as IntegrationModel
from app.models.user import User as UserModel
from app.schemas.integration import IntegrationCreate, IntegrationCategory, IntegrationType


async def create_mcp_integrations():
    """Create the MCP server integrations in the database"""
    
    # Get database session
    db_gen = get_db()
    db = await anext(db_gen)
    
    try:
        # Find or create a default user for integrations
        result = await db.execute(select(UserModel).limit(1))
        default_user = result.scalars().first()
        
        if not default_user:
            print("No user found in database. Please ensure there's at least one user.")
            return
            
        print(f"Using user: {default_user.email} (ID: {default_user.id})")
        
        # Define the MCP integrations
        mcp_integrations = [
            {
                "name": "Playwright MCP Server",
                "description": "Advanced web automation and testing server using Playwright with headless and vision capabilities. Enables browser automation, form filling, data extraction, website testing, screenshot capture, and PDF generation.",
                "integration_type": "mcp_server",
                "category": "automation",
                "icon": "🎭",
                "documentation_url": "https://playwright.dev/",
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
                            "default": ["@playwright/mcp@latest", "--headless", "--vision"],
                            "description": "Arguments for the MCP server command"
                        },
                        "server_url": {
                            "type": "string",
                            "default": "http://localhost:8080",
                            "description": "Server URL for the Playwright MCP server"
                        },
                        "timeout": {
                            "type": "integer",
                            "default": 30000,
                            "description": "Request timeout in milliseconds"
                        },
                        "headless": {
                            "type": "boolean",
                            "default": True,
                            "description": "Run browser in headless mode"
                        },
                        "vision": {
                            "type": "boolean", 
                            "default": True,
                            "description": "Enable vision capabilities"
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
                    "web_automation",
                    "form_filling", 
                    "data_extraction",
                    "website_testing",
                    "screenshot_capture",
                    "pdf_generation",
                    "performance_testing",
                    "vision_capabilities"
                ]
            },
            {
                "name": "Memory MCP Server",
                "description": "Model Context Protocol server for persistent memory and conversation history management. Provides long-term memory storage and retrieval capabilities for AI agents.",
                "integration_type": "mcp_server", 
                "category": "utilities",
                "icon": "🧠",
                "documentation_url": "https://modelcontextprotocol.io/",
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
                            "default": ["-y", "@modelcontextprotocol/server-memory"],
                            "description": "Arguments for the MCP server command"
                        },
                        "server_url": {
                            "type": "string",
                            "default": "http://localhost:8081",
                            "description": "Server URL for the Memory MCP server"
                        },
                        "timeout": {
                            "type": "integer",
                            "default": 30000,
                            "description": "Request timeout in milliseconds"
                        },
                        "memory_persistence": {
                            "type": "boolean",
                            "default": True,
                            "description": "Enable persistent memory storage"
                        }
                    },
                    "required": ["command", "args"]
                },
                "credentials_schema": {
                    "type": "object",
                    "properties": {
                        "database_url": {
                            "type": "string",
                            "description": "Database URL for memory storage",
                            "sensitive": True
                        }
                    }
                },
                "supported_features": [
                    "persistent_memory",
                    "conversation_history",
                    "context_management",
                    "memory_retrieval",
                    "conversation_continuity"
                ]
            }
        ]
        
        # Create integrations
        for integration_data in mcp_integrations:
            # Check if integration already exists
            result = await db.execute(
                select(IntegrationModel).where(IntegrationModel.name == integration_data["name"])
            )
            existing = result.scalars().first()
            
            if existing:
                print(f"Integration '{integration_data['name']}' already exists, skipping...")
                continue
                
            # Create new integration
            integration = IntegrationModel(
                **integration_data,
                author_id=default_user.id
            )
            db.add(integration)
            
            print(f"Created integration: {integration_data['name']}")
        
        # Commit all changes
        await db.commit()
        print("✅ Successfully added MCP server integrations to the Chronos Hub Marketplace!")
        
        # Show summary
        result = await db.execute(
            select(IntegrationModel).where(IntegrationModel.integration_type == "mcp_server")
        )
        mcp_servers = result.scalars().all()
        
        print(f"\n📊 Summary: {len(mcp_servers)} MCP server integrations available:")
        for server in mcp_servers:
            print(f"  - {server.name} v{server.version} ({server.category})")
            
    except Exception as e:
        print(f"❌ Error creating integrations: {e}")
        await db.rollback()
    finally:
        await db.close()


if __name__ == "__main__":
    print("🚀 Adding MCP server integrations to Chronos Hub Marketplace...")
    asyncio.run(create_mcp_integrations())