#!/usr/bin/env python3
"""
Comprehensive Integration Setup Test Script

This script tests all the integration components to ensure they're working correctly.
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List


class IntegrationTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
        self.test_results: List[Dict[str, Any]] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Chronos AI Integration Setup Tests...")
        print("=" * 60)
        
        # Run individual test suites
        await self.test_api_health()
        await self.test_integrations_api()
        await self.test_mcp_api()
        await self.test_ai_providers_api()
        await self.test_communication_api()
        await self.test_webchat_api()
        await self.test_monitoring_api()
        
        # Print summary
        self.print_test_summary()
        
        # Return overall status
        failed_tests = [r for r in self.test_results if not r["success"]]
        return len(failed_tests) == 0

    async def test_api_health(self):
        """Test API health endpoints"""
        print("\n🔍 Testing API Health Endpoints...")
        
        tests = [
            {"name": "Root endpoint", "path": "/"},
            {"name": "Health check", "path": "/health"},
        ]
        
        for test in tests:
            try:
                response = await self.client.get(test["path"])
                success = response.status_code == 200
                
                self.test_results.append({
                    "test": f"API Health - {test['name']}",
                    "success": success,
                    "status_code": response.status_code,
                    "response": response.json() if success else response.text
                })
                
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"  {status} {test['name']}: Status {response.status_code}")
                
            except Exception as e:
                self.test_results.append({
                    "test": f"API Health - {test['name']}",
                    "success": False,
                    "error": str(e)
                })
                print(f"  ❌ FAIL {test['name']}: {str(e)}")

    async def test_integrations_api(self):
        """Test integrations API"""
        print("\n🔍 Testing Integrations API...")
        
        try:
            # Test marketplace search
            search_response = await self.client.post(
                "/api/v1/integrations/search/",
                json={"query": "test", "page": 1, "page_size": 10}
            )
            
            success = search_response.status_code == 200
            self.test_results.append({
                "test": "Integrations - Marketplace search",
                "success": success,
                "status_code": search_response.status_code,
                "response": search_response.json() if success else search_response.text
            })
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} Marketplace search: Status {search_response.status_code}")
            
        except Exception as e:
            self.test_results.append({
                "test": "Integrations - Marketplace search",
                "success": False,
                "error": str(e)
            })
            print(f"  ❌ FAIL Marketplace search: {str(e)}")

    async def test_mcp_api(self):
        """Test MCP server API"""
        print("\n🔍 Testing MCP Server API...")
        
        try:
            # Test MCP health
            health_response = await self.client.get("/api/v1/mcp/health/")
            
            success = health_response.status_code == 200
            self.test_results.append({
                "test": "MCP Server - Health check",
                "success": success,
                "status_code": health_response.status_code,
                "response": health_response.json() if success else health_response.text
            })
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} MCP health check: Status {health_response.status_code}")
            
        except Exception as e:
            self.test_results.append({
                "test": "MCP Server - Health check",
                "success": False,
                "error": str(e)
            })
            print(f"  ❌ FAIL MCP health check: {str(e)}")

    async def test_ai_providers_api(self):
        """Test AI providers API"""
        print("\n🔍 Testing AI Providers API...")
        
        try:
            # Test list providers
            providers_response = await self.client.get("/api/v1/ai/providers/")
            
            success = providers_response.status_code == 200
            self.test_results.append({
                "test": "AI Providers - List providers",
                "success": success,
                "status_code": providers_response.status_code,
                "response": providers_response.json() if success else providers_response.text
            })
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} List AI providers: Status {providers_response.status_code}")
            
            # Test list models
            models_response = await self.client.get("/api/v1/ai/models/")
            
            success = models_response.status_code == 200
            self.test_results.append({
                "test": "AI Providers - List models",
                "success": success,
                "status_code": models_response.status_code,
                "response": models_response.json() if success else models_response.text
            })
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} List AI models: Status {models_response.status_code}")
            
        except Exception as e:
            self.test_results.append({
                "test": "AI Providers - API tests",
                "success": False,
                "error": str(e)
            })
            print(f"  ❌ FAIL AI providers tests: {str(e)}")

    async def test_communication_api(self):
        """Test communication channels API"""
        print("\n🔍 Testing Communication Channels API...")
        
        try:
            # Test communication health
            health_response = await self.client.get("/api/v1/communication/health/")
            
            success = health_response.status_code == 200
            self.test_results.append({
                "test": "Communication - Health check",
                "success": success,
                "status_code": health_response.status_code,
                "response": health_response.json() if success else health_response.text
            })
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} Communication health: Status {health_response.status_code}")
            
        except Exception as e:
            self.test_results.append({
                "test": "Communication - Health check",
                "success": False,
                "error": str(e)
            })
            print(f"  ❌ FAIL Communication health: {str(e)}")

    async def test_webchat_api(self):
        """Test WebChat API"""
        print("\n🔍 Testing WebChat API...")
        
        try:
            # Test WebChat health
            health_response = await self.client.get("/api/v1/webchat/health/")
            
            success = health_response.status_code == 200
            self.test_results.append({
                "test": "WebChat - Health check",
                "success": success,
                "status_code": health_response.status_code,
                "response": health_response.json() if success else health_response.text
            })
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} WebChat health: Status {health_response.status_code}")
            
        except Exception as e:
            self.test_results.append({
                "test": "WebChat - Health check",
                "success": False,
                "error": str(e)
            })
            print(f"  ❌ FAIL WebChat health: {str(e)}")

    async def test_monitoring_api(self):
        """Test integration monitoring API"""
        print("\n🔍 Testing Integration Monitoring API...")
        
        try:
            # Test monitoring health
            health_response = await self.client.get("/api/v1/monitoring/health/")
            
            success = health_response.status_code == 200
            self.test_results.append({
                "test": "Monitoring - Health check",
                "success": success,
                "status_code": health_response.status_code,
                "response": health_response.json() if success else health_response.text
            })
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} Monitoring health: Status {health_response.status_code}")
            
        except Exception as e:
            self.test_results.append({
                "test": "Monitoring - Health check",
                "success": False,
                "error": str(e)
            })
            print(f"  ❌ FAIL Monitoring health: {str(e)}")

    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests / total_tests * 100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 60)


async def main():
    """Main test function"""
    async with IntegrationTester() as tester:
        success = await tester.run_all_tests()
        
        if success:
            print("\n🎉 ALL TESTS PASSED! Integration setup is working correctly.")
            return 0
        else:
            print("\n⚠️  SOME TESTS FAILED! Please check the errors above.")
            return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)