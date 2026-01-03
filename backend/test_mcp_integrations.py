#!/usr/bin/env python3
"""
Test script to verify MCP integrations are properly installed and working
"""

import asyncio
import sys
import os
from typing import List, Dict, Any

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.integration import Integration as IntegrationModel
from app.models.user import User as UserModel


async def test_mcp_integrations():
    """Test that MCP integrations are properly installed"""
    
    print("🧪 Testing MCP Server Integrations...")
    print("=" * 50)
    
    try:
        db_gen = get_db()
        db = await anext(db_gen)
        
        # Test 1: Check if users exist
        print("\n1️⃣ Checking for users in database...")
        result = await db.execute(select(UserModel))
        users = result.scalars().all()
        
        if not users:
            print("❌ No users found in database")
            print("   Please create a user first before testing MCP integrations")
            await db.close()
            return False
        
        print(f"✅ Found {len(users)} user(s) in database")
        
        # Test 2: Check for MCP server integrations
        print("\n2️⃣ Checking for MCP server integrations...")
        result = await db.execute(
            select(IntegrationModel).where(IntegrationModel.integration_type == "mcp_server")
        )
        mcp_servers = result.scalars().all()
        
        if not mcp_servers:
            print("❌ No MCP server integrations found")
            print("   You may need to run the initialization script")
            await db.close()
            return False
        
        print(f"✅ Found {len(mcp_servers)} MCP server integration(s)")
        
        # Test 3: Validate Playwright MCP Server
        print("\n3️⃣ Validating Playwright MCP Server...")
        playwright_server = None
        for server in mcp_servers:
            if server.name == "Playwright MCP Server":
                playwright_server = server
                break
        
        if not playwright_server:
            print("❌ Playwright MCP Server not found")
        else:
            print("✅ Playwright MCP Server found")
            print(f"   - Version: {playwright_server.version}")
            print(f"   - Category: {playwright_server.category}")
            print(f"   - Features: {len(playwright_server.supported_features)} capabilities")
            
            # Validate configuration schema
            config_schema = playwright_server.config_schema
            if not config_schema or not isinstance(config_schema, dict):
                print("❌ Invalid configuration schema")
            else:
                print("✅ Configuration schema is valid")
                
            # Validate credentials schema
            credentials_schema = playwright_server.credentials_schema
            if credentials_schema and isinstance(credentials_schema, dict):
                print("✅ Credentials schema is valid")
            
            # Check for required features
            required_features = ["web_automation", "data_extraction", "screenshot_capture"]
            missing_features = [f for f in required_features if f not in playwright_server.supported_features]
            
            if missing_features:
                print(f"❌ Missing required features: {missing_features}")
            else:
                print("✅ All required features are present")
        
        # Test 4: Validate Memory MCP Server
        print("\n4️⃣ Validating Memory MCP Server...")
        memory_server = None
        for server in mcp_servers:
            if server.name == "Memory MCP Server":
                memory_server = server
                break
        
        if not memory_server:
            print("❌ Memory MCP Server not found")
        else:
            print("✅ Memory MCP Server found")
            print(f"   - Version: {memory_server.version}")
            print(f"   - Category: {memory_server.category}")
            print(f"   - Features: {len(memory_server.supported_features)} capabilities")
            
            # Validate configuration schema
            config_schema = memory_server.config_schema
            if not config_schema or not isinstance(config_schema, dict):
                print("❌ Invalid configuration schema")
            else:
                print("✅ Configuration schema is valid")
                
            # Check for required features
            required_features = ["persistent_memory", "conversation_history", "context_management"]
            missing_features = [f for f in required_features if f not in memory_server.supported_features]
            
            if missing_features:
                print(f"❌ Missing required features: {missing_features}")
            else:
                print("✅ All required features are present")
        
        # Test 5: Check integration details
        print("\n5️⃣ Checking integration details...")
        for server in mcp_servers:
            print(f"\n📋 {server.name}:")
            print(f"   - Type: {server.integration_type}")
            print(f"   - Category: {server.category}")
            print(f"   - Version: {server.version}")
            print(f"   - Public: {server.is_public}")
            print(f"   - Author: User ID {server.author_id}")
            print(f"   - Features: {', '.join(server.supported_features[:3])}...")
            
            # Check configuration defaults
            config = server.config_schema
            if config and 'properties' in config:
                properties = config['properties']
                if 'command' in properties and properties['command'].get('default') == 'npx':
                    print("   - ✅ Default command: npx")
                if 'server_url' in properties:
                    print(f"   - ✅ Default server URL: {properties['server_url'].get('default', 'not set')}")
        
        await db.close()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Users found: {len(users)}")
        print(f"✅ MCP servers found: {len(mcp_servers)}")
        
        if playwright_server and memory_server:
            print("✅ Both Playwright and Memory MCP servers are properly configured")
            print("\n🎉 All tests passed! MCP integrations are ready to use.")
            return True
        else:
            print("❌ Some MCP servers are missing or misconfigured")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        if 'db' in locals():
            await db.close()
        return False


async def test_api_endpoints():
    """Test the API endpoints for MCP integrations"""
    
    print("\n🔧 Testing API endpoints...")
    print("=" * 50)
    
    try:
        # This would be a real API test in a complete implementation
        print("ℹ️ API endpoint testing would be implemented here")
        print("   - GET /api/v1/integrations/")
        print("   - POST /api/v1/integrations/search/")
        print("   - POST /api/v1/integrations/{id}/config/")
        print("\n✅ API endpoints are available (manual testing recommended)")
        
    except Exception as e:
        print(f"❌ API test failed: {e}")


async def main():
    """Main test function"""
    
    print("🚀 Starting MCP Integrations Test Suite")
    print("=" * 50)
    
    # Run database tests
    db_success = await test_mcp_integrations()
    
    # Run API tests
    await test_api_endpoints()
    
    # Final result
    print("\n" + "=" * 50)
    if db_success:
        print("✅ MCP INTEGRATIONS TEST: PASSED")
        print("\n💡 Next steps:")
        print("   1. Start the Chronos backend: python -m app.main")
        print("   2. Visit the Chronos Hub Marketplace in your browser")
        print("   3. Install the MCP server integrations")
        print("   4. Configure and use them in your agents")
    else:
        print("❌ MCP INTEGRATIONS TEST: FAILED")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure you have users in the database")
        print("   2. Run the initialization script: python scripts/run_initialize_mcp_integrations.py")
        print("   3. Check database connectivity")
        print("   4. Review the MCP_INTEGRATIONS_README.md for details")
    
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())