import httpx
import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import logging

from app.core.config import settings


logger = logging.getLogger(__name__)


class MCPServerConfig(BaseModel):
    server_url: str = Field(..., description="MCP Server URL")
    api_key: Optional[str] = Field(None, description="API Key for authentication")
    timeout: int = Field(30, description="Request timeout in seconds")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")


class MCPFileOperation(BaseModel):
    operation: str = Field(..., description="Operation type: read, write, list, delete")
    path: str = Field(..., description="File path")
    content: Optional[str] = Field(None, description="File content for write operations")
    recursive: bool = Field(False, description="Recursive operation for list/delete")


class MCPDatabaseQuery(BaseModel):
    operation: str = Field(..., description="Database operation: query, execute, fetch")
    query: str = Field(..., description="SQL query or database command")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Query parameters")
    database_type: str = Field(..., description="Database type: postgres, mysql, sqlite, etc.")


class MCPWebScrapingTask(BaseModel):
    url: str = Field(..., description="URL to scrape")
    selectors: Dict[str, str] = Field(..., description="CSS selectors for data extraction")
    render_javascript: bool = Field(False, description="Render JavaScript before scraping")
    wait_for_selector: Optional[str] = Field(None, description="Wait for specific selector")


class MCPApiRequest(BaseModel):
    method: str = Field(..., description="HTTP method: GET, POST, PUT, DELETE, etc.")
    url: str = Field(..., description="API endpoint URL")
    headers: Optional[Dict[str, str]] = Field(None, description="Request headers")
    body: Optional[Dict[str, Any]] = Field(None, description="Request body")
    params: Optional[Dict[str, str]] = Field(None, description="Query parameters")


class MCPClient:
    """
    MCP (Multi-Protocol Connectivity) Server Client
    
    This client provides a unified interface for interacting with MCP servers
    that support file operations, database access, web scraping, and API calls.
    """

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.base_url = config.server_url.rstrip('/')
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=config.timeout,
            verify=config.verify_ssl,
            headers=self._get_default_headers()
        )

    def _get_default_headers(self) -> Dict[str, str]:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Chronos-AI-Agent-Builder/MCP-Client-1.0'
        }
        
        if self.config.api_key:
            headers['Authorization'] = f'Bearer {self.config.api_key}'
        
        return headers

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self.client.aclose()

    async def file_operation(self, operation: MCPFileOperation) -> Dict[str, Any]:
        """Perform file operations on the MCP server"""
        try:
            endpoint = "/api/v1/files"
            
            response = await self.client.post(
                endpoint,
                json=operation.dict()
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"MCP File Operation failed: {e}")
            raise MCPServerError(f"File operation failed: {e.response.text}")
        except Exception as e:
            logger.error(f"MCP File Operation error: {e}")
            raise MCPServerError(f"File operation error: {str(e)}")

    async def database_query(self, query: MCPDatabaseQuery) -> Dict[str, Any]:
        """Execute database queries through the MCP server"""
        try:
            endpoint = "/api/v1/database"
            
            response = await self.client.post(
                endpoint,
                json=query.dict()
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"MCP Database Query failed: {e}")
            raise MCPServerError(f"Database query failed: {e.response.text}")
        except Exception as e:
            logger.error(f"MCP Database Query error: {e}")
            raise MCPServerError(f"Database query error: {str(e)}")

    async def web_scraping(self, task: MCPWebScrapingTask) -> Dict[str, Any]:
        """Perform web scraping through the MCP server"""
        try:
            endpoint = "/api/v1/scraping"
            
            response = await self.client.post(
                endpoint,
                json=task.dict()
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"MCP Web Scraping failed: {e}")
            raise MCPServerError(f"Web scraping failed: {e.response.text}")
        except Exception as e:
            logger.error(f"MCP Web Scraping error: {e}")
            raise MCPServerError(f"Web scraping error: {str(e)}")

    async def api_request(self, request: MCPApiRequest) -> Dict[str, Any]:
        """Make API requests through the MCP server"""
        try:
            endpoint = "/api/v1/proxy"
            
            response = await self.client.post(
                endpoint,
                json=request.dict()
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"MCP API Request failed: {e}")
            raise MCPServerError(f"API request failed: {e.response.text}")
        except Exception as e:
            logger.error(f"MCP API Request error: {e}")
            raise MCPServerError(f"API request error: {str(e)}")

    async def health_check(self) -> bool:
        """Check MCP server health"""
        try:
            response = await self.client.get("/health")
            return response.status_code == 200
        except Exception:
            return False

    async def get_server_info(self) -> Dict[str, Any]:
        """Get MCP server information"""
        try:
            response = await self.client.get("/api/v1/info")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get MCP server info: {e}")
            raise MCPServerError(f"Failed to get server info: {str(e)}")


class MCPServerError(Exception):
    """Custom exception for MCP server errors"""
    pass


class MCPIntegrationManager:
    """
    Manager for MCP server integrations
    
    Handles multiple MCP server connections and provides a unified interface
    for agent operations.
    """

    def __init__(self):
        self.servers: Dict[str, MCPClient] = {}
        self.default_server: Optional[str] = None

    async def add_server(self, server_id: str, config: MCPServerConfig):
        """Add a new MCP server connection"""
        client = MCPClient(config)
        
        # Test the connection
        if not await client.health_check():
            raise MCPServerError(f"MCP server {server_id} health check failed")
        
        self.servers[server_id] = client
        
        # Set as default if it's the first server
        if not self.default_server:
            self.default_server = server_id

    async def remove_server(self, server_id: str):
        """Remove an MCP server connection"""
        if server_id in self.servers:
            await self.servers[server_id].close()
            del self.servers[server_id]
            
            # Update default server if needed
            if self.default_server === server_id:
                self.default_server = next(iter(self.servers.keys()), None)

    async def get_server(self, server_id: Optional[str] = None) -> MCPClient:
        """Get an MCP server client"""
        if not server_id:
            if not self.default_server:
                raise MCPServerError("No default MCP server configured")
            return self.servers[self.default_server]
        
        if server_id not in self.servers:
            raise MCPServerError(f"MCP server {server_id} not found")
        
        return self.servers[server_id]

    async def list_files(
        self, 
        path: str = "/", 
        server_id: Optional[str] = None,
        recursive: bool = False
    ) -> List[Dict[str, Any]]:
        """List files on an MCP server"""
        client = await self.get_server(server_id)
        operation = MCPFileOperation(
            operation="list",
            path=path,
            recursive=recursive
        )
        result = await client.file_operation(operation)
        return result.get("files", [])

    async def read_file(
        self, 
        path: str, 
        server_id: Optional[str] = None
    ) -> str:
        """Read file content from an MCP server"""
        client = await self.get_server(server_id)
        operation = MCPFileOperation(
            operation="read",
            path=path
        )
        result = await client.file_operation(operation)
        return result.get("content", "")

    async def write_file(
        self, 
        path: str, 
        content: str, 
        server_id: Optional[str] = None
    ) -> bool:
        """Write file content to an MCP server"""
        client = await self.get_server(server_id)
        operation = MCPFileOperation(
            operation="write",
            path=path,
            content=content
        )
        result = await client.file_operation(operation)
        return result.get("success", False)

    async def delete_file(
        self, 
        path: str, 
        server_id: Optional[str] = None
    ) -> bool:
        """Delete file from an MCP server"""
        client = await self.get_server(server_id)
        operation = MCPFileOperation(
            operation="delete",
            path=path
        )
        result = await client.file_operation(operation)
        return result.get("success", False)

    async def query_database(
        self, 
        query: str, 
        database_type: str, 
        parameters: Optional[Dict[str, Any]] = None, 
        server_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute database query through MCP server"""
        client = await self.get_server(server_id)
        db_query = MCPDatabaseQuery(
            operation="query",
            query=query,
            database_type=database_type,
            parameters=parameters
        )
        return await client.database_query(db_query)

    async def scrape_website(
        self, 
        url: str, 
        selectors: Dict[str, str], 
        render_javascript: bool = False, 
        server_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform web scraping through MCP server"""
        client = await self.get_server(server_id)
        task = MCPWebScrapingTask(
            url=url,
            selectors=selectors,
            render_javascript=render_javascript
        )
        return await client.web_scraping(task)

    async def make_api_request(
        self, 
        method: str, 
        url: str, 
        headers: Optional[Dict[str, str]] = None, 
        body: Optional[Dict[str, Any]] = None, 
        params: Optional[Dict[str, str]] = None, 
        server_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make API request through MCP server"""
        client = await self.get_server(server_id)
        request = MCPApiRequest(
            method=method,
            url=url,
            headers=headers,
            body=body,
            params=params
        )
        return await client.api_request(request)

    async def close_all(self):
        """Close all MCP server connections"""
        for client in self.servers.values():
            await client.close()
        self.servers.clear()
        self.default_server = None


# Global MCP integration manager instance
mcp_manager = MCPIntegrationManager()


async def initialize_mcp_integrations():
    """Initialize MCP integrations from configuration"""
    try:
        # In a real implementation, this would load from database/config
        if settings.MCP_SERVER_URL:
            config = MCPServerConfig(
                server_url=settings.MCP_SERVER_URL,
                api_key=settings.MCP_SERVER_API_KEY,
                timeout=settings.MCP_SERVER_TIMEOUT
            )
            await mcp_manager.add_server("default", config)
            logger.info("MCP server integration initialized")
    except Exception as e:
        logger.error(f"Failed to initialize MCP integrations: {e}")


async def get_mcp_client() -> MCPClient:
    """Get the default MCP client"""
    return await mcp_manager.get_server()