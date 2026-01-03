#!/usr/bin/env python3
"""
Convenience script to run the MCP integrations initialization
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.initialize_mcp_integrations import initialize_mcp_integrations


async def main():
    print("🚀 Initializing MCP server integrations for Chronos Hub Marketplace...")
    success = await initialize_mcp_integrations()
    
    if success:
        print("\n✅ MCP integrations are ready to use!")
        print("💡 You can now install these MCP servers from the Chronos Hub Marketplace.")
    else:
        print("\n❌ Failed to initialize MCP integrations.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())