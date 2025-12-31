"""
Enhanced MCP API Endpoints
Advanced MCP server management and operation endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import asyncio
import json
import logging
from datetime import datetime, timedelta

from app.core.enhanced_mcp_manager import enhanced_mcp_manager
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User as UserModel
from app.models.mcp_server import (
    MCPServer, MCPOperationLog, MCPServerMetric, 
    MCPCacheEntry, MCPServerGroup, MCPServerGroupMember
)

from app.schemas.mcp_server import (
    # Server management schemas
    MCPServerCreate, MCPServerUpdate, MCPServerResponse,
    MCPServerInfo, MCPHealthCheck, MCPHealthDashboard,
    
    # Operation schemas
    MCPOperationLogResponse, MCPServerMetricResponse,
    MCPCacheEntryResponse, MCPBatchOperation, MCPBatchOperationResult,
    
    # Group management schemas
    MCPServerGroupCreate, MCPServerGroupUpdate, MCPServerGroupResponse,
    MCPServerGroupMemberCreate, MCPServerGroupMemberResponse,
    MCPServerGroupInfo,
    
    # Analytics schemas
    MCPAnalyticsRequest, MCPAnalyticsResponse,
    
    # File operation schemas
    MCPFileRequest, MCPFileResponse,
    
    # Database operation schemas
    MCPDatabaseRequest,
    
    # Web scraping schemas
    MCPWebScrapingRequest,
    
    # API proxy schemas
    MCPApiProxyRequest
)

from app.core.mcp_client import (
    MCPFileOperation, MCPDatabaseQuery, 
    MCPWebScrapingTask, MCPApiRequest,
    MCPServerError
)


router = APIRouter()
logger = logging.getLogger(__name__)


# =============================================================================
# MCP Server Management Endpoints
# =============================================================================

@router.post("/enhanced-mcp/servers/", response_model=MCPServerResponse)
async def create_mcp_server(
    server_data: MCPServerCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new enhanced MCP server with advanced configuration"""
    try:
        return await enhanced_mcp_manager.add_server(server_data, db)
    except MCPServerError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create MCP server: {str(e)}")


@router.put("/enhanced-mcp/servers/{server_id}", response_model=MCPServerResponse)
async def update_mcp_server(
    server_id: str,
    server_update: MCPServerUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update existing MCP server configuration"""
    try:
        return await enhanced_mcp_manager.update_server(server_id, server_update, db)
    except MCPServerError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update MCP server: {str(e)}")


@router.delete("/enhanced-mcp/servers/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcp_server(
    server_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete MCP server"""
    try:
        await enhanced_mcp_manager.remove_server(server_id, db)
    except MCPServerError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete MCP server: {str(e)}")


@router.get("/enhanced-mcp/servers/", response_model=List[MCPServerResponse])
async def list_mcp_servers(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    active_only: bool = True
):
    """List all MCP servers with filtering options"""
    try:
        query = db.query(MCPServer)
        if active_only:
            query = query.filter(MCPServer.is_active == True)
        
        servers = query.all()
        return [MCPServerResponse.from_orm(server) for server in servers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list MCP servers: {str(e)}")


@router.get("/enhanced-mcp/servers/{server_id}", response_model=MCPServerResponse)
async def get_mcp_server(
    server_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific MCP server details"""
    try:
        server = db.query(MCPServer).filter(MCPServer.server_id == server_id).first()
        if not server:
            raise HTTPException(status_code=404, detail="MCP server not found")
        
        return MCPServerResponse.from_orm(server)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get MCP server: {str(e)}")


@router.get("/enhanced-mcp/info/", response_model=MCPServerInfo)
async def get_mcp_info(
    current_user: UserModel = Depends(get_current_user)
):
    """Get comprehensive MCP system information"""
    try:
        return await enhanced_mcp_manager.get_server_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get MCP info: {str(e)}")


# =============================================================================
# Health and Monitoring Endpoints
# =============================================================================

@router.get("/enhanced-mcp/health/", response_model=MCPHealthDashboard)
async def mcp_health_dashboard(
    current_user: UserModel = Depends(get_current_user)
):
    """Get comprehensive MCP health dashboard"""
    try:
        health_status = await enhanced_mcp_manager.health_check()
        
        # Calculate summary statistics
        servers = health_status.get("servers", {})
        healthy_count = sum(1 for status in servers.values() if status.get("status") == "healthy")
        unhealthy_count = sum(1 for status in servers.values() if status.get("status") == "unhealthy")
        error_count = sum(1 for status in servers.values() if status.get("status") == "error")
        
        # Determine overall status
        overall_status = "healthy" if healthy_count > 0 else "unhealthy" if unhealthy_count > 0 else "unknown"
        
        return MCPHealthDashboard(
            overall_status=overall_status,
            total_servers=len(servers),
            healthy_servers=healthy_count,
            unhealthy_servers=unhealthy_count,
            unknown_servers=error_count,
            servers=[
                MCPHealthCheck(
                    server_id=server_id,
                    status=status.get("status", "unknown"),
                    response_time_ms=status.get("metrics", {}).get("average_response_time", 0) * 1000,
                    last_check=datetime.utcnow(),
                    error_message=status.get("error"),
                    uptime_percentage=100.0 if status.get("status") == "healthy" else 0.0,
                    error_rate=status.get("metrics", {}).get("error_rate", 0)
                )
                for server_id, status in servers.items()
            ],
            cluster_metrics={
                "total_requests": sum(s.get("metrics", {}).get("total_requests", 0) for s in servers.values()),
                "success_rate": sum(s.get("metrics", {}).get("success_rate", 0) for s in servers.values()) / max(len(servers), 1),
                "average_response_time": sum(s.get("metrics", {}).get("average_response_time", 0) for s in servers.values()) / max(len(servers), 1)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get health dashboard: {str(e)}")


@router.get("/enhanced-mcp/health/{server_id}")
async def mcp_server_health(
    server_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Get health status for specific MCP server"""
    try:
        return await enhanced_mcp_manager.health_check(server_id)
    except MCPServerError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get server health: {str(e)}")


@router.get("/enhanced-mcp/metrics/{server_id}")
async def get_server_metrics(
    server_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """Get detailed metrics for MCP server"""
    try:
        # Get metrics from database
        query = db.query(MCPServerMetric).filter(MCPServerMetric.server_id == server_id)
        
        if start_time:
            query = query.filter(MCPServerMetric.timestamp >= start_time)
        if end_time:
            query = query.filter(MCPServerMetric.timestamp <= end_time)
        
        metrics = query.order_by(desc(MCPServerMetric.timestamp)).limit(100).all()
        
        return {
            "server_id": server_id,
            "metrics": [MCPServerMetricResponse.from_orm(metric) for metric in metrics],
            "total_metrics": len(metrics)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get server metrics: {str(e)}")


@router.get("/enhanced-mcp/analytics/", response_model=MCPAnalyticsResponse)
async def get_mcp_analytics(
    request: MCPAnalyticsRequest = None,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive MCP analytics"""
    try:
        # Default time range: last 24 hours
        end_time = request.end_date or datetime.utcnow()
        start_time = request.start_date or end_time - timedelta(hours=24)
        
        # Build query
        query = db.query(MCPServerMetric)
        
        if request.server_id:
            server = db.query(MCPServer).filter(MCPServer.server_id == request.server_id).first()
            if server:
                query = query.filter(MCPServerMetric.server_id == server.id)
        
        query = query.filter(
            MCPServerMetric.timestamp >= start_time,
            MCPServerMetric.timestamp <= end_time
        )
        
        if request.metrics:
            query = query.filter(MCPServerMetric.metric_name.in_(request.metrics))
        
        metrics_data = query.all()
        
        # Process analytics data
        analytics = {}
        for metric in metrics_data:
            metric_name = metric.metric_name
            if metric_name not in analytics:
                analytics[metric_name] = []
            analytics[metric_name].append({
                "timestamp": metric.timestamp,
                "value": metric.metric_value,
                "unit": metric.metric_unit
            })
        
        # Calculate summary statistics
        summary = {}
        for metric_name, values in analytics.items():
            if values:
                summary[metric_name] = {
                    "count": len(values),
                    "min": min(v["value"] for v in values),
                    "max": max(v["value"] for v in values),
                    "avg": sum(v["value"] for v in values) / len(values)
                }
        
        return MCPAnalyticsResponse(
            server_id=request.server_id,
            time_range={"start": start_time, "end": end_time},
            metrics=analytics,
            summary=summary,
            trends={}  # Would implement trend analysis
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


# =============================================================================
# Enhanced Operation Endpoints
# =============================================================================

@router.post("/enhanced-mcp/files/", response_model=MCPFileResponse)
async def enhanced_file_operation(
    file_request: MCPFileRequest,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user)
):
    """Enhanced file operation with caching, rate limiting, and monitoring"""
    try:
        operation = MCPFileOperation(
            operation=file_request.operation,
            path=file_request.path,
            content=file_request.content,
            recursive=file_request.recursive
        )
        
        result = await enhanced_mcp_manager.file_operation(
            operation,
            file_request.server_id
        )
        
        # Log operation in background
        background_tasks.add_task(
            _log_operation,
            OperationType.FILE_OPERATION,
            file_request.operation,
            file_request.dict(),
            result,
            current_user.id
        )
        
        return MCPFileResponse(success=True, data=result)
    except MCPServerError as e:
        return MCPFileResponse(success=False, error=str(e))
    except Exception as e:
        return MCPFileResponse(success=False, error=f"File operation failed: {str(e)}")


@router.post("/enhanced-mcp/database/", response_model=MCPFileResponse)
async def enhanced_database_query(
    db_request: MCPDatabaseRequest,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user)
):
    """Enhanced database query with advanced features"""
    try:
        result = await enhanced_mcp_manager.database_query(
            db_request.query,
            db_request.database_type,
            db_request.parameters,
            db_request.server_id
        )
        
        # Log operation in background
        background_tasks.add_task(
            _log_operation,
            OperationType.DATABASE_QUERY,
            "query",
            db_request.dict(),
            result,
            current_user.id
        )
        
        return MCPFileResponse(success=True, data=result)
    except MCPServerError as e:
        return MCPFileResponse(success=False, error=str(e))
    except Exception as e:
        return MCPFileResponse(success=False, error=f"Database query failed: {str(e)}")


@router.post("/enhanced-mcp/scraping/", response_model=MCPFileResponse)
async def enhanced_web_scraping(
    scraping_request: MCPWebScrapingRequest,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user)
):
    """Enhanced web scraping with advanced features"""
    try:
        result = await enhanced_mcp_manager.scrape_website(
            scraping_request.url,
            scraping_request.selectors,
            scraping_request.render_javascript,
            scraping_request.server_id
        )
        
        # Log operation in background
        background_tasks.add_task(
            _log_operation,
            OperationType.WEB_SCRAPING,
            "scrape",
            scraping_request.dict(),
            result,
            current_user.id
        )
        
        return MCPFileResponse(success=True, data=result)
    except MCPServerError as e:
        return MCPFileResponse(success=False, error=str(e))
    except Exception as e:
        return MCPFileResponse(success=False, error=f"Web scraping failed: {str(e)}")


@router.post("/enhanced-mcp/proxy/", response_model=MCPFileResponse)
async def enhanced_api_proxy(
    proxy_request: MCPApiProxyRequest,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user)
):
    """Enhanced API proxy with advanced features"""
    try:
        result = await enhanced_mcp_manager.make_api_request(
            proxy_request.method,
            proxy_request.url,
            proxy_request.headers,
            proxy_request.body,
            proxy_request.params,
            proxy_request.server_id
        )
        
        # Log operation in background
        background_tasks.add_task(
            _log_operation,
            OperationType.API_PROXY,
            proxy_request.method,
            proxy_request.dict(),
            result,
            current_user.id
        )
        
        return MCPFileResponse(success=True, data=result)
    except MCPServerError as e:
        return MCPFileResponse(success=False, error=str(e))
    except Exception as e:
        return MCPFileResponse(success=False, error=f"API proxy request failed: {str(e)}")


# =============================================================================
# Batch Operations Endpoints
# =============================================================================

@router.post("/enhanced-mcp/batch/", response_model=MCPBatchOperationResult)
async def execute_batch_operation(
    batch_request: MCPBatchOperation,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user)
):
    """Execute batch operations with enhanced features"""
    try:
        result = await enhanced_mcp_manager.batch_operation(
            batch_request.operations,
            batch_request.parallel,
            batch_request.server_id
        )
        
        # Log batch operation in background
        background_tasks.add_task(
            _log_batch_operation,
            batch_request.operations,
            result,
            current_user.id
        )
        
        return result
    except MCPServerError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch operation failed: {str(e)}")


# =============================================================================
# Server Groups Management Endpoints
# =============================================================================

@router.post("/enhanced-mcp/groups/", response_model=MCPServerGroupResponse)
async def create_server_group(
    group_data: MCPServerGroupCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new MCP server group"""
    try:
        group = MCPServerGroup(
            name=group_data.name,
            description=group_data.description,
            algorithm=group_data.algorithm.value,
            health_check_interval=group_data.health_check_interval,
            failover_enabled=group_data.failover_enabled
        )
        
        db.add(group)
        db.commit()
        db.refresh(group)
        
        return MCPServerGroupResponse.from_orm(group)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create server group: {str(e)}")


@router.get("/enhanced-mcp/groups/", response_model=List[MCPServerGroupResponse])
async def list_server_groups(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all server groups"""
    try:
        groups = db.query(MCPServerGroup).filter(MCPServerGroup.is_active == True).all()
        return [MCPServerGroupResponse.from_orm(group) for group in groups]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list server groups: {str(e)}")


@router.post("/enhanced-mcp/groups/{group_name}/members/")
async def add_server_to_group(
    group_name: str,
    member_data: MCPServerGroupMemberCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add server to group"""
    try:
        group = db.query(MCPServerGroup).filter(MCPServerGroup.name == group_name).first()
        if not group:
            raise HTTPException(status_code=404, detail="Server group not found")
        
        server = db.query(MCPServer).filter(MCPServer.id == member_data.server_id).first()
        if not server:
            raise HTTPException(status_code=404, detail="Server not found")
        
        # Check if already member
        existing_member = db.query(MCPServerGroupMember).filter(
            and_(
                MCPServerGroupMember.group_id == group.id,
                MCPServerGroupMember.server_id == server.id
            )
        ).first()
        
        if existing_member:
            raise HTTPException(status_code=400, detail="Server already in group")
        
        member = MCPServerGroupMember(
            group_id=group.id,
            server_id=server.id,
            weight=member_data.weight,
            priority=member_data.priority
        )
        
        db.add(member)
        db.commit()
        
        return {"message": f"Server {server.server_id} added to group {group_name}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add server to group: {str(e)}")


# =============================================================================
# Operation Logs and Cache Management
# =============================================================================

@router.get("/enhanced-mcp/logs/")
async def get_operation_logs(
    server_id: Optional[str] = None,
    operation_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get operation logs with filtering"""
    try:
        query = db.query(MCPOperationLog)
        
        if server_id:
            server = db.query(MCPServer).filter(MCPServer.server_id == server_id).first()
            if server:
                query = query.filter(MCPOperationLog.server_id == server.id)
        
        if operation_type:
            query = query.filter(MCPOperationLog.operation_type == operation_type)
        
        if status:
            query = query.filter(MCPOperationLog.status == status)
        
        logs = query.order_by(desc(MCPOperationLog.started_at)).limit(limit).all()
        
        return {
            "logs": [MCPOperationLogResponse.from_orm(log) for log in logs],
            "total": len(logs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get operation logs: {str(e)}")


@router.get("/enhanced-mcp/cache/")
async def get_cache_entries(
    server_id: Optional[str] = None,
    operation_type: Optional[str] = None,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get cache entries"""
    try:
        query = db.query(MCPCacheEntry)
        
        if server_id:
            server = db.query(MCPServer).filter(MCPServer.server_id == server_id).first()
            if server:
                query = query.filter(MCPCacheEntry.server_id == server.id)
        
        if operation_type:
            query = query.filter(MCPCacheEntry.operation_type == operation_type)
        
        entries = query.order_by(desc(MCPCacheEntry.created_at)).limit(limit).all()
        
        return {
            "entries": [MCPCacheEntryResponse.from_orm(entry) for entry in entries],
            "total": len(entries)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache entries: {str(e)}")


@router.delete("/enhanced-mcp/cache/{cache_key}")
async def clear_cache_entry(
    cache_key: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear specific cache entry"""
    try:
        entry = db.query(MCPCacheEntry).filter(MCPCacheEntry.cache_key == cache_key).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Cache entry not found")
        
        db.delete(entry)
        db.commit()
        
        return {"message": f"Cache entry {cache_key} cleared"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache entry: {str(e)}")


# =============================================================================
# WebSocket Support for Real-time Communication
# =============================================================================

@router.websocket("/enhanced-mcp/ws/{server_id}")
async def websocket_endpoint(websocket: WebSocket, server_id: str):
    """WebSocket endpoint for real-time MCP communication"""
    await websocket.accept()
    
    try:
        # Get MCP client
        client = await enhanced_mcp_manager.get_server(server_id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message
            if message_data.get("type") == "operation":
                result = await _process_websocket_operation(client, message_data)
                await websocket.send_text(json.dumps(result))
            else:
                await websocket.send_text(json.dumps({
                    "error": "Unknown message type",
                    "type": "error"
                }))
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for server {server_id}")
    except Exception as e:
        logger.error(f"WebSocket error for server {server_id}: {e}")
        await websocket.send_text(json.dumps({
            "error": str(e),
            "type": "error"
        }))


# =============================================================================
# Helper Functions
# =============================================================================

async def _log_operation(operation_type: str, operation_name: str, request_data: Dict[str, Any],
                       response_data: Dict[str, Any], user_id: str, db: Session = None):
    """Log operation to database"""
    try:
        # This would log to the database
        logger.info(f"Operation logged: {operation_type} - {operation_name}")
    except Exception as e:
        logger.error(f"Failed to log operation: {e}")


async def _log_batch_operation(operations: List[Dict[str, Any]], result: Dict[str, Any], user_id: str):
    """Log batch operation"""
    try:
        logger.info(f"Batch operation completed: {len(operations)} operations, "
                   f"{result.get('successful_operations', 0)} successful")
    except Exception as e:
        logger.error(f"Failed to log batch operation: {e}")


async def _process_websocket_operation(client, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process operation received via WebSocket"""
    try:
        operation_type = message_data.get("operation_type")
        data = message_data.get("data", {})
        
        if operation_type == "file_operation":
            operation = MCPFileOperation(**data)
            result = await client.file_operation(operation)
        elif operation_type == "api_request":
            operation = MCPApiRequest(**data)
            result = await client.api_request(operation)
        else:
            return {"error": f"Unsupported operation type: {operation_type}", "type": "error"}
        
        return {"result": result, "type": "success"}
    except Exception as e:
        return {"error": str(e), "type": "error"}