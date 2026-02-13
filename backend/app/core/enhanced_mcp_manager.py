"""
Enhanced MCP Manager
Advanced MCP integration manager with database persistence, load balancing, and monitoring
"""
import asyncio
import json
import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, select

from app.models.mcp_server import (
    MCPServer, MCPOperationLog, MCPServerMetric, 
    MCPCacheEntry, MCPServerGroup, MCPServerGroupMember
)
from app.schemas.mcp_server import (
    MCPServerCreate, MCPServerUpdate, MCPServerResponse,
    MCPServerGroupCreate, MCPServerGroupUpdate, MCPServerGroupResponse,
    MCPServerGroupMemberCreate, MCPServerGroupMemberResponse,
    OperationType, HealthStatus, LogStatus, LoadBalanceAlgorithm
)
from app.core.advanced_mcp_client import (
    AdvancedMCPClient, LoadBalancer, RequestCache, 
    MCPServerError, RetryPolicy
)
from app.core.database import SessionLocal


logger = logging.getLogger(__name__)


class EnhancedMCPManager:
    """
    Enhanced MCP Integration Manager
    
    Features:
    - Database persistence for server configurations
    - Load balancing across multiple servers
    - Health monitoring and automatic failover
    - Request caching and rate limiting
    - Metrics collection and analytics
    - Circuit breaker pattern
    - Server groups for advanced load balancing
    """
    
    def __init__(self):
        self.clients: Dict[str, AdvancedMCPClient] = {}
        self.load_balancer = LoadBalancer()
        self.server_groups: Dict[str, MCPServerGroup] = {}
        self.health_check_interval = 60  # seconds
        self.health_check_task: Optional[asyncio.Task] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Background tasks control
        self._running = False
    
    async def initialize(self):
        """Initialize the enhanced MCP manager"""
        logger.info("Initializing Enhanced MCP Manager...")
        
        # Load servers from database
        await self._load_servers_from_database()
        
        # Load server groups
        await self._load_server_groups_from_database()
        
        # Start background tasks
        self._running = True
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("Enhanced MCP Manager initialized successfully")
    
    async def shutdown(self):
        """Shutdown the enhanced MCP manager"""
        logger.info("Shutting down Enhanced MCP Manager...")
        
        self._running = False
        
        # Cancel background tasks
        if self.health_check_task:
            self.health_check_task.cancel()
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
        
        # Close all clients
        for client in self.clients.values():
            await client.close()
        
        self.clients.clear()
        logger.info("Enhanced MCP Manager shutdown complete")
    
    async def _load_servers_from_database(self):
        """Load MCP servers from database"""
        try:
            async with SessionLocal() as db:
                servers = (
                    await db.execute(
                        select(MCPServer).where(MCPServer.is_active.is_(True))
                    )
                ).scalars().all()

                for server in servers:
                    await self._add_server_to_client(server)

                logger.info(f"Loaded {len(servers)} MCP servers from database")
        except Exception as e:
            logger.error(f"Failed to load servers from database: {e}")
    
    async def _load_server_groups_from_database(self):
        """Load server groups from database"""
        try:
            async with SessionLocal() as db:
                groups = (
                    await db.execute(
                        select(MCPServerGroup).where(MCPServerGroup.is_active.is_(True))
                    )
                ).scalars().all()

                for group in groups:
                    members = (
                        await db.execute(
                            select(MCPServerGroupMember).where(
                                and_(
                                    MCPServerGroupMember.group_id == group.id,
                                    MCPServerGroupMember.is_active.is_(True),
                                )
                            )
                        )
                    ).scalars().all()

                    self.server_groups[group.name] = group

                    # Add group members to load balancer
                    for member in members:
                        server = await db.get(MCPServer, member.server_id)
                        if server and server.server_id in self.clients:
                            self.load_balancer.add_server(server.server_id, {
                                'weight': member.weight,
                                'is_active': server.is_active,
                                'health_status': server.health_status,
                                'current_connections': server.current_connections
                            })

                logger.info(f"Loaded {len(groups)} server groups from database")
        except Exception as e:
            logger.error(f"Failed to load server groups from database: {e}")
    
    async def _add_server_to_client(self, server: MCPServer):
        """Add server to client and load balancer"""
        try:
            # Create enhanced client configuration
            config_dict = {
                'server_url': server.server_url,
                'api_key': server.api_key,
                'timeout': server.timeout,
                'verify_ssl': server.verify_ssl,
                'max_connections': server.max_connections,
                'rate_limit_per_minute': server.rate_limit_per_minute,
                'retry_config': server.retry_config or {},
                'circuit_breaker_config': server.circuit_breaker_config or {},
                'cache_config': server.cache_config or {},
                'monitoring_config': server.monitoring_config or {}
            }
            
            # Create advanced client
            client = AdvancedMCPClient(
                config=config_dict,
                server_id=server.server_id
            )
            
            # Test connection
            if await client.health_check():
                self.clients[server.server_id] = client
                self.load_balancer.add_server(server.server_id, {
                    'weight': server.weight,
                    'is_active': server.is_active,
                    'health_status': server.health_status,
                    'current_connections': server.current_connections
                })
                logger.info(f"Successfully added MCP server: {server.server_id}")
            else:
                logger.warning(f"Health check failed for MCP server: {server.server_id}")
        
        except Exception as e:
            logger.error(f"Failed to add MCP server {server.server_id}: {e}")
    
    async def add_server(self, server_data: MCPServerCreate, db: Session) -> MCPServerResponse:
        """Add new MCP server"""
        try:
            # Generate server_id if not provided
            server_id = server_data.server_id or f"mcp_server_{int(datetime.utcnow().timestamp())}"
            
            # Create database record
            server = MCPServer(
                server_id=server_id,
                name=server_data.name,
                description=server_data.description,
                server_url=server_data.server_url,
                api_key=server_data.api_key,
                timeout=server_data.timeout,
                verify_ssl=server_data.verify_ssl,
                auth_type=server_data.auth_type.value,
                is_default=server_data.is_default,
                tags=server_data.tags,
                category=server_data.category,
                weight=server_data.weight,
                max_connections=server_data.max_connections,
                rate_limit_per_minute=server_data.rate_limit_per_minute,
                rate_limit_per_hour=server_data.rate_limit_per_hour,
                retry_config=server_data.retry_config,
                circuit_breaker_config=server_data.circuit_breaker_config,
                cache_config=server_data.cache_config,
                monitoring_config=server_data.monitoring_config,
                status="active"
            )
            
            db.add(server)
            db.commit()
            db.refresh(server)
            
            # Add to client if active
            if server.is_active:
                await self._add_server_to_client(server)
            
            # Update default server if needed
            if server_data.is_default:
                await self._update_default_server(server_id, db)
            
            logger.info(f"Added new MCP server: {server_id}")
            return MCPServerResponse.from_orm(server)
        
        except Exception as e:
            logger.error(f"Failed to add MCP server: {e}")
            raise MCPServerError(f"Failed to add MCP server: {str(e)}")
    
    async def update_server(self, server_id: str, server_update: MCPServerUpdate, db: Session) -> MCPServerResponse:
        """Update MCP server configuration"""
        try:
            server = db.query(MCPServer).filter(MCPServer.server_id == server_id).first()
            if not server:
                raise MCPServerError(f"MCP server {server_id} not found")
            
            # Update fields
            update_data = server_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(server, field, value)
            
            server.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(server)
            
            # Update client if exists
            if server_id in self.clients:
                client = self.clients[server_id]
                await client.close()
                del self.clients[server_id]
                
                if server.is_active:
                    await self._add_server_to_client(server)
            
            # Update load balancer
            self.load_balancer.remove_server(server_id)
            if server.is_active and server.health_status == HealthStatus.HEALTHY:
                self.load_balancer.add_server(server_id, {
                    'weight': server.weight,
                    'is_active': server.is_active,
                    'health_status': server.health_status,
                    'current_connections': server.current_connections
                })
            
            logger.info(f"Updated MCP server: {server_id}")
            return MCPServerResponse.from_orm(server)
        
        except Exception as e:
            logger.error(f"Failed to update MCP server {server_id}: {e}")
            raise MCPServerError(f"Failed to update MCP server: {str(e)}")
    
    async def remove_server(self, server_id: str, db: Session):
        """Remove MCP server"""
        try:
            server = db.query(MCPServer).filter(MCPServer.server_id == server_id).first()
            if not server:
                raise MCPServerError(f"MCP server {server_id} not found")
            
            # Remove from client
            if server_id in self.clients:
                await self.clients[server_id].close()
                del self.clients[server_id]
            
            # Remove from load balancer
            self.load_balancer.remove_server(server_id)
            
            # Mark as inactive in database
            server.is_active = False
            server.status = "inactive"
            server.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Removed MCP server: {server_id}")
        
        except Exception as e:
            logger.error(f"Failed to remove MCP server {server_id}: {e}")
            raise MCPServerError(f"Failed to remove MCP server: {str(e)}")
    
    async def get_server(self, server_id: Optional[str] = None, group_name: Optional[str] = None) -> AdvancedMCPClient:
        """Get MCP server client with load balancing"""
        if group_name and group_name in self.server_groups:
            group = self.server_groups[group_name]
            member_servers = self._get_group_member_server_ids(group.id)
            selected_server_id = self.load_balancer.get_server(
                algorithm=group.algorithm.value,
                group_servers=member_servers
            )
            if selected_server_id:
                server_id = selected_server_id
            elif member_servers:
                server_id = member_servers[0]
        
        if not server_id:
            # Get default server or first available
            available_servers = [sid for sid in self.clients.keys() 
                               if self.clients[sid].circuit_breaker.state.value != "open"]
            if not available_servers:
                raise MCPServerError("No available MCP servers")
            server_id = available_servers[0]
        
        if server_id not in self.clients:
            raise MCPServerError(f"MCP server {server_id} not found or not active")
        
        return self.clients[server_id]
    
    async def file_operation(self, operation, server_id: Optional[str] = None, group_name: Optional[str] = None) -> Dict[str, Any]:
        """Perform file operation with advanced features"""
        client = await self.get_server(server_id, group_name)
        
        # Generate cache key if caching is enabled
        cache_key = None
        if operation.operation in ['read', 'list']:
            cache_key = client.request_cache.generate_cache_key(
                "file_operation", operation.dict(), client.server_id
            )
        
        return await client.file_operation(operation, cache_key)
    
    async def database_query(self, query: str, database_type: str, parameters: Optional[Dict[str, Any]] = None, 
                           server_id: Optional[str] = None, group_name: Optional[str] = None) -> Dict[str, Any]:
        """Execute database query with advanced features"""
        from app.schemas.mcp_server import MCPDatabaseQuery
        
        client = await self.get_server(server_id, group_name)
        
        db_query = MCPDatabaseQuery(
            operation="query",
            query=query,
            database_type=database_type,
            parameters=parameters
        )
        
        # Don't cache database queries by default for security
        cache_key = None
        
        return await client.database_query(db_query, cache_key)
    
    async def scrape_website(self, url: str, selectors: Dict[str, str], render_javascript: bool = False,
                           server_id: Optional[str] = None, group_name: Optional[str] = None) -> Dict[str, Any]:
        """Perform web scraping with advanced features"""
        from app.schemas.mcp_server import MCPWebScrapingTask
        
        client = await self.get_server(server_id, group_name)
        
        task = MCPWebScrapingTask(
            url=url,
            selectors=selectors,
            render_javascript=render_javascript
        )
        
        # Cache web scraping results for 5 minutes
        cache_key = client.request_cache.generate_cache_key(
            "web_scraping", task.dict(), client.server_id
        )
        
        return await client.web_scraping(task, cache_key)
    
    async def make_api_request(self, method: str, url: str, headers: Optional[Dict[str, str]] = None,
                             body: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, str]] = None,
                             server_id: Optional[str] = None, group_name: Optional[str] = None) -> Dict[str, Any]:
        """Make API request with advanced features"""
        from app.schemas.mcp_server import MCPApiRequest
        
        client = await self.get_server(server_id, group_name)
        
        request = MCPApiRequest(
            method=method,
            url=url,
            headers=headers,
            body=body,
            params=params
        )
        
        # Cache GET requests for 1 minute
        cache_key = None
        if method.upper() == 'GET':
            cache_key = client.request_cache.generate_cache_key(
                "api_request", request.dict(), client.server_id
            )
        
        return await client.api_request(request, cache_key)
    
    async def health_check(self, server_id: Optional[str] = None) -> Dict[str, Any]:
        """Perform health check on MCP servers"""
        if server_id:
            if server_id in self.clients:
                is_healthy = await self.clients[server_id].health_check()
                return {
                    server_id: {
                        "status": "healthy" if is_healthy else "unhealthy",
                        "connected": is_healthy
                    }
                }
            else:
                raise MCPServerError(f"MCP server {server_id} not found")
        
        # Check all servers
        health_status = {}
        for sid, client in self.clients.items():
            try:
                is_healthy = await client.health_check()
                health_status[sid] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "connected": is_healthy,
                    "metrics": client.get_metrics()
                }
            except Exception as e:
                health_status[sid] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "status": "ok",
            "servers": health_status,
            "total_servers": len(self.clients),
            "healthy_servers": sum(1 for status in health_status.values() if status.get("status") == "healthy")
        }
    
    async def get_server_info(self) -> Dict[str, Any]:
        """Get comprehensive MCP server information"""
        servers_info = []
        
        for server_id, client in self.clients.items():
            metrics = client.get_metrics()
            servers_info.append({
                "server_id": server_id,
                "metrics": metrics,
                "circuit_breaker_state": client.circuit_breaker.state.value,
                "cache_size": len(client.request_cache.cache)
            })
        
        return {
            "servers": list(self.clients.keys()),
            "server_details": servers_info,
            "total_servers": len(self.clients),
            "server_groups": list(self.server_groups.keys()),
            "load_balancing_status": {
                "algorithm": "round_robin",
                "total_servers": len(self.clients),
                "active_servers": len([s for s in self.clients.values() 
                                     if s.circuit_breaker.state.value != "open"])
            }
        }
    
    async def batch_operation(self, operations: List[Dict[str, Any]], parallel: bool = False,
                            server_id: Optional[str] = None, group_name: Optional[str] = None) -> Dict[str, Any]:
        """Execute batch operations"""
        import uuid
        from app.schemas.mcp_server import MCPBatchOperationResult
        
        batch_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        results = []
        errors = []
        successful_count = 0
        failed_count = 0
        
        if parallel:
            # Execute operations in parallel
            tasks = []
            for i, operation in enumerate(operations):
                try:
                    if operation['type'] == 'file_operation':
                        from app.schemas.mcp_server import MCPFileOperation
                        op = MCPFileOperation(**operation['data'])
                        task = self.file_operation(op, server_id, group_name)
                    elif operation['type'] == 'api_request':
                        from app.schemas.mcp_server import MCPApiRequest
                        op = MCPApiRequest(**operation['data'])
                        task = self.make_api_request(**operation['data'], server_id=server_id, group_name=group_name)
                    else:
                        raise ValueError(f"Unsupported operation type: {operation['type']}")
                    
                    tasks.append((i, task))
                except Exception as e:
                    errors.append({"index": i, "error": str(e)})
                    failed_count += 1
            
            # Execute all tasks
            for i, task in tasks:
                try:
                    result = await task
                    results.append({"index": i, "result": result})
                    successful_count += 1
                except Exception as e:
                    errors.append({"index": i, "error": str(e)})
                    failed_count += 1
        
        else:
            # Execute operations sequentially
            for i, operation in enumerate(operations):
                try:
                    if operation['type'] == 'file_operation':
                        from app.schemas.mcp_server import MCPFileOperation
                        op = MCPFileOperation(**operation['data'])
                        result = await self.file_operation(op, server_id, group_name)
                    elif operation['type'] == 'api_request':
                        result = await self.make_api_request(**operation['data'], server_id=server_id, group_name=group_name)
                    else:
                        raise ValueError(f"Unsupported operation type: {operation['type']}")
                    
                    results.append({"index": i, "result": result})
                    successful_count += 1
                except Exception as e:
                    errors.append({"index": i, "error": str(e)})
                    failed_count += 1
        
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return MCPBatchOperationResult(
            batch_id=batch_id,
            total_operations=len(operations),
            successful_operations=successful_count,
            failed_operations=failed_count,
            results=results,
            execution_time_ms=execution_time,
            errors=errors
        ).dict()
    
    async def _health_check_loop(self):
        """Background health check loop"""
        while self._running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self._running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(60)  # Collect metrics every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _perform_health_checks(self):
        """Perform health checks on all servers"""
        for server_id, client in self.clients.items():
            try:
                is_healthy = await client.health_check()
                # Update database with health status
                # This would be implemented with database updates
                logger.debug(f"Health check for {server_id}: {'healthy' if is_healthy else 'unhealthy'}")
            except Exception as e:
                logger.error(f"Health check failed for {server_id}: {e}")
    
    async def _collect_metrics(self):
        """Collect and store metrics"""
        for server_id, client in self.clients.items():
            try:
                metrics = client.get_metrics()
                # Store metrics in database
                # This would be implemented with database inserts
                logger.debug(f"Collected metrics for {server_id}: {metrics}")
            except Exception as e:
                logger.error(f"Failed to collect metrics for {server_id}: {e}")
    
    def _get_group_member_server_ids(self, group_id: int) -> List[str]:
        """Get server IDs for a group"""
        # This would query the database for group members
        # For now, return empty list
        return []
    
    async def _update_default_server(self, server_id: str, db: Session):
        """Update default server"""
        # Remove default flag from other servers
        db.query(MCPServer).filter(MCPServer.server_id != server_id).update({"is_default": False})
        db.commit()


# Global enhanced MCP manager instance
enhanced_mcp_manager = EnhancedMCPManager()


async def initialize_enhanced_mcp():
    """Initialize enhanced MCP manager"""
    await enhanced_mcp_manager.initialize()


async def get_enhanced_mcp_client(server_id: Optional[str] = None) -> AdvancedMCPClient:
    """Get enhanced MCP client"""
    return await enhanced_mcp_manager.get_server(server_id)
