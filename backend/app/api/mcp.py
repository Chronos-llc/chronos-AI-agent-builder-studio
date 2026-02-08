from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from app.core.mcp_client import (
    MCPServerConfig, 
    MCPFileOperation, 
    MCPDatabaseQuery, 
    MCPWebScrapingTask, 
    MCPApiRequest,
    mcp_manager, 
    MCPServerError
)
from app.api.auth import get_current_user
from app.models.user import User as UserModel


router = APIRouter()


class MCPServerCreate(BaseModel):
    server_id: str
    config: MCPServerConfig


class MCPServerResponse(BaseModel):
    server_id: str
    status: str
    config: Dict[str, Any]


class MCPFileRequest(BaseModel):
    server_id: Optional[str] = None
    operation: str
    path: str
    content: Optional[str] = None
    recursive: bool = False


class MCPFileResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MCPDatabaseRequest(BaseModel):
    server_id: Optional[str] = None
    operation: str
    query: str
    database_type: str
    parameters: Optional[Dict[str, Any]] = None


class MCPWebScrapingRequest(BaseModel):
    server_id: Optional[str] = None
    url: str
    selectors: Dict[str, str]
    render_javascript: bool = False
    wait_for_selector: Optional[str] = None


class MCPApiProxyRequest(BaseModel):
    server_id: Optional[str] = None
    method: str
    url: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, str]] = None


@router.post("/mcp/servers/", response_model=MCPServerResponse)
async def add_mcp_server(
    server_data: MCPServerCreate,
    current_user: UserModel = Depends(get_current_user)
):
    """Add a new MCP server connection"""
    try:
        await mcp_manager.add_server(server_data.server_id, server_data.config)
        return MCPServerResponse(
            server_id=server_data.server_id,
            status="active",
            config=server_data.config.dict()
        )
    except MCPServerError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add MCP server: {str(e)}")


@router.delete("/mcp/servers/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_mcp_server(
    server_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Remove an MCP server connection"""
    try:
        await mcp_manager.remove_server(server_id)
    except MCPServerError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove MCP server: {str(e)}")


@router.get("/mcp/servers/", response_model=List[str])
async def list_mcp_servers(
    current_user: UserModel = Depends(get_current_user)
):
    """List all configured MCP servers"""
    return list(mcp_manager.servers.keys())


@router.post("/mcp/files/", response_model=MCPFileResponse)
async def mcp_file_operation(
    file_request: MCPFileRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """Perform file operations through MCP server"""
    try:
        operation = MCPFileOperation(
            operation=file_request.operation,
            path=file_request.path,
            content=file_request.content,
            recursive=file_request.recursive
        )
        
        result = await mcp_manager.file_operation(
            operation,
            file_request.server_id
        )
        
        return MCPFileResponse(
            success=True,
            data=result
        )
    except MCPServerError as e:
        return MCPFileResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        return MCPFileResponse(
            success=False,
            error=f"File operation failed: {str(e)}"
        )


@router.post("/mcp/database/", response_model=MCPFileResponse)
async def mcp_database_query(
    db_request: MCPDatabaseRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """Execute database queries through MCP server"""
    try:
        query = MCPDatabaseQuery(
            operation=db_request.operation,
            query=db_request.query,
            database_type=db_request.database_type,
            parameters=db_request.parameters
        )
        
        result = await mcp_manager.query_database(
            db_request.query,
            db_request.database_type,
            db_request.parameters,
            db_request.server_id
        )
        
        return MCPFileResponse(
            success=True,
            data=result
        )
    except MCPServerError as e:
        return MCPFileResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        return MCPFileResponse(
            success=False,
            error=f"Database query failed: {str(e)}"
        )


@router.post("/mcp/scraping/", response_model=MCPFileResponse)
async def mcp_web_scraping(
    scraping_request: MCPWebScrapingRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """Perform web scraping through MCP server"""
    try:
        task = MCPWebScrapingTask(
            url=scraping_request.url,
            selectors=scraping_request.selectors,
            render_javascript=scraping_request.render_javascript,
            wait_for_selector=scraping_request.wait_for_selector
        )
        
        result = await mcp_manager.scrape_website(
            scraping_request.url,
            scraping_request.selectors,
            scraping_request.render_javascript,
            scraping_request.server_id
        )
        
        return MCPFileResponse(
            success=True,
            data=result
        )
    except MCPServerError as e:
        return MCPFileResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        return MCPFileResponse(
            success=False,
            error=f"Web scraping failed: {str(e)}"
        )


@router.post("/mcp/proxy/", response_model=MCPFileResponse)
async def mcp_api_proxy(
    proxy_request: MCPApiProxyRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """Make API requests through MCP server proxy"""
    try:
        request = MCPApiRequest(
            method=proxy_request.method,
            url=proxy_request.url,
            headers=proxy_request.headers,
            body=proxy_request.body,
            params=proxy_request.params
        )
        
        result = await mcp_manager.make_api_request(
            proxy_request.method,
            proxy_request.url,
            proxy_request.headers,
            proxy_request.body,
            proxy_request.params,
            proxy_request.server_id
        )
        
        return MCPFileResponse(
            success=True,
            data=result
        )
    except MCPServerError as e:
        return MCPFileResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        return MCPFileResponse(
            success=False,
            error=f"API proxy request failed: {str(e)}"
        )


@router.get("/mcp/health/", response_model=Dict[str, Any])
async def mcp_health_check(
    current_user: UserModel = Depends(get_current_user)
):
    """Check MCP server health status"""
    health_status = {}
    
    for server_id, client in mcp_manager.servers.items():
        try:
            is_healthy = await client.health_check()
            health_status[server_id] = {
                "status": "healthy" if is_healthy else "unhealthy",
                "connected": is_healthy
            }
        except Exception as e:
            health_status[server_id] = {
                "status": "error",
                "error": str(e)
            }
    
    return {
        "status": "ok",
        "servers": health_status,
        "default_server": mcp_manager.default_server
    }


@router.get("/mcp/info/", response_model=Dict[str, Any])
async def mcp_server_info(
    current_user: UserModel = Depends(get_current_user)
):
    """Get MCP server information"""
    info = {
        "servers": list(mcp_manager.servers.keys()),
        "default_server": mcp_manager.default_server,
        "total_servers": len(mcp_manager.servers)
    }
    
    return info