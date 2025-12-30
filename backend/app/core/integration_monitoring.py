import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel
import httpx

from app.core.database import get_db
from app.models.integration import IntegrationConfig as IntegrationConfigModel


logger = logging.getLogger(__name__)


class IntegrationTestResult(BaseModel):
    success: bool
    message: str
    timestamp: str
    response_time: float
    details: Optional[Dict[str, Any]] = None


class IntegrationMonitor:
    """
    Integration Monitoring System
    
    Provides testing, monitoring, and health checking for integrations.
    """

    def __init__(self):
        self.test_history: Dict[str, List[IntegrationTestResult]] = {}
        self.performance_metrics: Dict[str, Dict[str, Any]] = {}

    async def test_integration(self, config_id: int) -> IntegrationTestResult:
        """Test an integration configuration"""
        start_time = time.time()
        
        try:
            # Get integration config from database
            async with get_db() as db:
                result = await db.execute(
                    select(IntegrationConfigModel).where(IntegrationConfigModel.id == config_id)
                )
                config = result.scalars().first()
                
                if not config:
                    return IntegrationTestResult(
                        success=False,
                        message="Integration configuration not found",
                        timestamp=datetime.now().isoformat(),
                        response_time=0.0
                    )
                
                # Perform different tests based on integration type
                integration_type = config.integration.integration_type
                
                if integration_type == "api":
                    return await self._test_api_integration(config)
                elif integration_type == "webhook":
                    return await self._test_webhook_integration(config)
                elif integration_type == "database":
                    return await self._test_database_integration(config)
                elif integration_type == "file_system":
                    return await self._test_filesystem_integration(config)
                elif integration_type == "mcp_server":
                    return await self._test_mcp_integration(config)
                elif integration_type == "ai_model":
                    return await self._test_ai_integration(config)
                elif integration_type == "communication":
                    return await self._test_communication_integration(config)
                elif integration_type == "webchat":
                    return await self._test_webchat_integration(config)
                else:
                    return IntegrationTestResult(
                        success=False,
                        message=f"Unsupported integration type: {integration_type}",
                        timestamp=datetime.now().isoformat(),
                        response_time=0.0
                    )
        
        except Exception as e:
            return IntegrationTestResult(
                success=False,
                message=f"Integration test failed: {str(e)}",
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time,
                details={"error": str(e)}
            )
        finally:
            response_time = time.time() - start_time
            result = IntegrationTestResult(
                success=True,
                message="Integration test completed",
                timestamp=datetime.now().isoformat(),
                response_time=response_time
            )
            
            # Store test result
            self._store_test_result(config_id, result)

    async def _test_api_integration(self, config: IntegrationConfigModel) -> IntegrationTestResult:
        """Test API integration"""
        start_time = time.time()
        
        try:
            # Extract API configuration
            api_url = config.config.get("api_url")
            test_endpoint = config.config.get("test_endpoint", "/health")
            
            if not api_url:
                return IntegrationTestResult(
                    success=False,
                    message="API URL not configured",
                    timestamp=datetime.now().isoformat(),
                    response_time=0.0
                )
            
            # Make test request
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{api_url}{test_endpoint}")
                
                if response.status_code == 200:
                    return IntegrationTestResult(
                        success=True,
                        message="API integration test successful",
                        timestamp=datetime.now().isoformat(),
                        response_time=time.time() - start_time,
                        details={
                            "status_code": response.status_code,
                            "response": response.text
                        }
                    )
                else:
                    return IntegrationTestResult(
                        success=False,
                        message=f"API test failed with status {response.status_code}",
                        timestamp=datetime.now().isoformat(),
                        response_time=time.time() - start_time,
                        details={
                            "status_code": response.status_code,
                            "response": response.text
                        }
                    )
        
        except Exception as e:
            return IntegrationTestResult(
                success=False,
                message=f"API test failed: {str(e)}",
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time,
                details={"error": str(e)}
            )

    async def _test_webhook_integration(self, config: IntegrationConfigModel) -> IntegrationTestResult:
        """Test webhook integration"""
        start_time = time.time()
        
        try:
            # Extract webhook configuration
            webhook_url = config.config.get("webhook_url")
            
            if not webhook_url:
                return IntegrationTestResult(
                    success=False,
                    message="Webhook URL not configured",
                    timestamp=datetime.now().isoformat(),
                    response_time=0.0
                )
            
            # Send test webhook payload
            test_payload = {
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "message": "This is a test webhook from Chronos AI Agent Builder"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(webhook_url, json=test_payload)
                
                if response.status_code == 200:
                    return IntegrationTestResult(
                        success=True,
                        message="Webhook integration test successful",
                        timestamp=datetime.now().isoformat(),
                        response_time=time.time() - start_time,
                        details={
                            "status_code": response.status_code,
                            "response": response.text
                        }
                    )
                else:
                    return IntegrationTestResult(
                        success=False,
                        message=f"Webhook test failed with status {response.status_code}",
                        timestamp=datetime.now().isoformat(),
                        response_time=time.time() - start_time,
                        details={
                            "status_code": response.status_code,
                            "response": response.text
                        }
                    )
        
        except Exception as e:
            return IntegrationTestResult(
                success=False,
                message=f"Webhook test failed: {str(e)}",
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time,
                details={"error": str(e)}
            )

    async def _test_database_integration(self, config: IntegrationConfigModel) -> IntegrationTestResult:
        """Test database integration"""
        start_time = time.time()
        
        try:
            # Extract database configuration
            db_type = config.config.get("database_type")
            connection_string = config.config.get("connection_string")
            
            if not db_type or not connection_string:
                return IntegrationTestResult(
                    success=False,
                    message="Database configuration incomplete",
                    timestamp=datetime.now().isoformat(),
                    response_time=0.0
                )
            
            # Test database connection
            if db_type == "postgresql":
                # Test PostgreSQL connection
                import asyncpg
                conn = await asyncpg.connect(connection_string)
                await conn.execute("SELECT 1")
                await conn.close()
            elif db_type == "mysql":
                # Test MySQL connection
                import aiomysql
                conn = await aiomysql.connect(**self._parse_mysql_connection_string(connection_string))
                await conn.ping()
                await conn.close()
            elif db_type == "sqlite":
                # Test SQLite connection
                import aiosqlite
                async with aiosqlite.connect(connection_string) as db:
                    await db.execute("SELECT 1")
            else:
                return IntegrationTestResult(
                    success=False,
                    message=f"Unsupported database type: {db_type}",
                    timestamp=datetime.now().isoformat(),
                    response_time=time.time() - start_time
                )
            
            return IntegrationTestResult(
                success=True,
                message="Database integration test successful",
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time,
                details={"database_type": db_type}
            )
        
        except Exception as e:
            return IntegrationTestResult(
                success=False,
                message=f"Database test failed: {str(e)}",
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time,
                details={"error": str(e)}
            )

    async def _test_filesystem_integration(self, config: IntegrationConfigModel) -> IntegrationTestResult:
        """Test filesystem integration"""
        start_time = time.time()
        
        try:
            # Extract filesystem configuration
            base_path = config.config.get("base_path", ".")
            
            # Test filesystem operations
            import os
            
            # Test directory existence
            if not os.path.isdir(base_path):
                return IntegrationTestResult(
                    success=False,
                    message=f"Base path does not exist: {base_path}",
                    timestamp=datetime.now().isoformat(),
                    response_time=time.time() - start_time
                )
            
            # Test file creation and deletion
            test_file = os.path.join(base_path, "chronos_test_file.txt")
            
            # Write test file
            with open(test_file, "w") as f:
                f.write("Test file for Chronos integration")
            
            # Read test file
            with open(test_file, "r") as f:
                content = f.read()
            
            # Delete test file
            os.remove(test_file)
            
            if content == "Test file for Chronos integration":
                return IntegrationTestResult(
                    success=True,
                    message="Filesystem integration test successful",
                    timestamp=datetime.now().isoformat(),
                    response_time=time.time() - start_time,
                    details={"base_path": base_path}
                )
            else:
                return IntegrationTestResult(
                    success=False,
                    message="Filesystem test failed - content mismatch",
                    timestamp=datetime.now().isoformat(),
                    response_time=time.time() - start_time
                )
        
        except Exception as e:
            return IntegrationTestResult(
                success=False,
                message=f"Filesystem test failed: {str(e)}",
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time,
                details={"error": str(e)}
            )

    async def _test_mcp_integration(self, config: IntegrationConfigModel) -> IntegrationTestResult:
        """Test MCP server integration"""
        start_time = time.time()
        
        try:
            from app.core.mcp_client import MCPClient, MCPServerConfig
            
            # Extract MCP configuration
            server_url = config.config.get("server_url")
            api_key = config.credentials.get("api_key")
            
            if not server_url:
                return IntegrationTestResult(
                    success=False,
                    message="MCP server URL not configured",
                    timestamp=datetime.now().isoformat(),
                    response_time=0.0
                )
            
            # Create MCP client and test connection
            mcp_config = MCPServerConfig(
                server_url=server_url,
                api_key=api_key,
                timeout=30
            )
            
            client = MCPClient(mcp_config)
            is_healthy = await client.health_check()
            
            if is_healthy:
                return IntegrationTestResult(
                    success=True,
                    message="MCP server integration test successful",
                    timestamp=datetime.now().isoformat(),
                    response_time=time.time() - start_time,
                    details={"server_url": server_url}
                )
            else:
                return IntegrationTestResult(
                    success=False,
                    message="MCP server health check failed",
                    timestamp=datetime.now().isoformat(),
                    response_time=time.time() - start_time
                )
        
        except Exception as e:
            return IntegrationTestResult(
                success=False,
                message=f"MCP server test failed: {str(e)}",
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time,
                details={"error": str(e)}
            )

    async def _test_ai_integration(self, config: IntegrationConfigModel) -> IntegrationTestResult:
        """Test AI model integration"""
        start_time = time.time()
        
        try:
            from app.core.ai_providers import AIModelConfig, AIProviderType
            
            # Extract AI configuration
            provider_type = config.config.get("provider_type")
            model_name = config.config.get("model_name")
            api_key = config.credentials.get("api_key")
            
            if not provider_type or not model_name:
                return IntegrationTestResult(
                    success=False,
                    message="AI provider configuration incomplete",
                    timestamp=datetime.now().isoformat(),
                    response_time=0.0
                )
            
            # Create AI model config
            ai_config = AIModelConfig(
                provider_type=provider_type,
                model_name=model_name,
                api_key=api_key,
                max_tokens=10,
                temperature=0.7
            )
            
            # Test with a simple prompt
            test_prompt = "Hello, this is a test."
            result = await ai_provider_manager.generate_text(test_prompt, config_id=str(config.id))
            
            if result and len(result) > 0:
                return IntegrationTestResult(
                    success=True,
                    message="AI model integration test successful",
                    timestamp=datetime.now().isoformat(),
                    response_time=time.time() - start_time,
                    details={
                        "provider": provider_type,
                        "model": model_name,
                        "response_length": len(result)
                    }
                )
            else:
                return IntegrationTestResult(
                    success=False,
                    message="AI model test failed - no response",
                    timestamp=datetime.now().isoformat(),
                    response_time=time.time() - start_time
                )
        
        except Exception as e:
            return IntegrationTestResult(
                success=False,
                message=f"AI model test failed: {str(e)}",
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time,
                details={"error": str(e)}
            )

    async def _test_communication_integration(self, config: IntegrationConfigModel) -> IntegrationTestResult:
        """Test communication channel integration"""
        start_time = time.time()
        
        try:
            # Extract communication configuration
            channel_type = config.config.get("channel_type")
            
            if not channel_type:
                return IntegrationTestResult(
                    success=False,
                    message="Communication channel type not configured",
                    timestamp=datetime.now().isoformat(),
                    response_time=0.0
                )
            
            # Test different channel types
            if channel_type == "telegram":
                return await self._test_telegram_integration(config)
            elif channel_type == "slack":
                return await self._test_slack_integration(config)
            elif channel_type == "whatsapp":
                return await self._test_whatsapp_integration(config)
            elif channel_type == "discord":
                return await self._test_discord_integration(config)
            else:
                return IntegrationTestResult(
                    success=False,
                    message=f"Unsupported communication channel: {channel_type}",
                    timestamp=datetime.now().isoformat(),
                    response_time=time.time() - start_time
                )
        
        except Exception as e:
            return IntegrationTestResult(
                success=False,
                message=f"Communication channel test failed: {str(e)}",
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time,
                details={"error": str(e)}
            )

    async def _test_webchat_integration(self, config: IntegrationConfigModel) -> IntegrationTestResult:
        """Test webchat integration"""
        start_time = time.time()
        
        try:
            # Extract webchat configuration
            embed_type = config.config.get("embed_type")
            
            if not embed_type:
                return IntegrationTestResult(
                    success=False,
                    message="WebChat embed type not configured",
                    timestamp=datetime.now().isoformat(),
                    response_time=0.0
                )
            
            # Test webchat configuration
            return IntegrationTestResult(
                success=True,
                message="WebChat integration test successful",
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time,
                details={"embed_type": embed_type}
            )
        
        except Exception as e:
            return IntegrationTestResult(
                success=False,
                message=f"WebChat test failed: {str(e)}",
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time,
                details={"error": str(e)}
            )

    async def _test_telegram_integration(self, config: IntegrationConfigModel) -> IntegrationTestResult:
        """Test Telegram integration"""
        start_time = time.time()
        
        try:
            bot_token = config.credentials.get("bot_token")
            chat_id = config.config.get("test_chat_id")
            
            if not bot_token:
                return IntegrationTestResult(
                    success=False,
                    message="Telegram bot token not configured",
                    timestamp=datetime.now().isoformat(),
                    response_time=0.0
                )
            
            # Test Telegram API
            async with httpx.AsyncClient(timeout=10.0) as client:
                test_url = f"https://api.telegram.org/bot{bot_token}/getMe"
                response = await client.get(test_url)
                
                if response.status_code == 200:
                    return IntegrationTestResult(
                        success=True,
                        message="Telegram integration test successful",
                        timestamp=datetime.now().isoformat(),
                        response_time=time.time() - start_time,
                        details={"bot_info": response.json()}
                    )
                else:
                    return IntegrationTestResult(
                        success=False,
                        message=f"Telegram test failed with status {response.status_code}",
                        timestamp=datetime.now().isoformat(),
                        response_time=time.time() - start_time
                    )
        
        except Exception as e:
            return IntegrationTestResult(
                success=False,
                message=f"Telegram test failed: {str(e)}",
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time,
                details={"error": str(e)}
            )

    async def _test_slack_integration(self, config: IntegrationConfigModel) -> IntegrationTestResult:
        """Test Slack integration"""
        start_time = time.time()
        
        try:
            access_token = config.credentials.get("access_token")
            
            if not access_token:
                return IntegrationTestResult(
                    success=False,
                    message="Slack access token not configured",
                    timestamp=datetime.now().isoformat(),
                    response_time=0.0
                )
            
            # Test Slack API
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://slack.com/api/auth.test", headers={
                    "Authorization": f"Bearer {access_token}"
                })
                
                if response.status_code == 200:
                    return IntegrationTestResult(
                        success=True,
                        message="Slack integration test successful",
                        timestamp=datetime.now().isoformat(),
                        response_time=time.time() - start_time,
                        details={"auth_info": response.json()}
                    )
                else:
                    return IntegrationTestResult(
                        success=False,
                        message=f"Slack test failed with status {response.status_code}",
                        timestamp=datetime.now().isoformat(),
                        response_time=time.time() - start_time
                    )
        
        except Exception as e:
            return IntegrationTestResult(
                success=False,
                message=f"Slack test failed: {str(e)}",
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time,
                details={"error": str(e)}
            )

    def _store_test_result(self, config_id: int, result: IntegrationTestResult):
        """Store test result in history"""
        if config_id not in self.test_history:
            self.test_history[config_id] = []
        
        self.test_history[config_id].append(result)
        
        # Keep only the last 10 test results
        if len(self.test_history[config_id]) > 10:
            self.test_history[config_id] = self.test_history[config_id][-10:]

    def get_test_history(self, config_id: int) -> List[IntegrationTestResult]:
        """Get test history for an integration"""
        return self.test_history.get(config_id, [])

    def get_performance_metrics(self, config_id: int) -> Dict[str, Any]:
        """Get performance metrics for an integration"""
        if config_id not in self.performance_metrics:
            return {
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "total_tests": 0,
                "successful_tests": 0
            }
        
        return self.performance_metrics[config_id]

    def update_performance_metrics(self, config_id: int, result: IntegrationTestResult):
        """Update performance metrics based on test result"""
        if config_id not in self.performance_metrics:
            self.performance_metrics[config_id] = {
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "total_tests": 0,
                "successful_tests": 0
            }
        
        metrics = self.performance_metrics[config_id]
        metrics["total_tests"] += 1
        
        if result.success:
            metrics["successful_tests"] += 1
        
        # Update success rate
        metrics["success_rate"] = metrics["successful_tests"] / metrics["total_tests"]
        
        # Update average response time (simple moving average)
        if metrics["total_tests"] == 1:
            metrics["avg_response_time"] = result.response_time
        else:
            metrics["avg_response_time"] = (
                metrics["avg_response_time"] * (metrics["total_tests"] - 1) + result.response_time
            ) / metrics["total_tests"]


# Global integration monitor instance
integration_monitor = IntegrationMonitor()


async def initialize_integration_monitoring():
    """Initialize integration monitoring system"""
    logger.info("Integration monitoring system initialized")


async def get_integration_monitor() -> IntegrationMonitor:
    """Get the integration monitor instance"""
    return integration_monitor