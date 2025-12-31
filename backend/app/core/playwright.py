"""
Playwright Core Services

This module provides core Playwright browser automation functionality including:
- PlaywrightManager: Main coordinator for Playwright operations
- BrowserSessionManager: Browser session lifecycle management
- TaskExecutor: Automation task execution engine
- ArtifactManager: File artifact storage and retrieval
- PoolManager: Browser pool management for high-throughput scenarios
"""

import asyncio
import json
import os
import shutil
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4
import aiofiles
import aiofiles.os

try:
    from playwright.async_api import (
        async_playwright, 
        Browser, 
        BrowserContext, 
        Page, 
        Playwright,
        PlaywrightContextManager
    )
except ImportError:
    Browser = BrowserContext = Page = Playwright = None
    PlaywrightContextManager = None

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.playwright import (
    BrowserType, 
    BrowserSessionStatus, 
    TaskStatus, 
    ArtifactType
)

settings = get_settings()
logger = get_logger(__name__)


class PlaywrightManager:
    """
    Main coordinator for Playwright browser automation operations.
    Manages browser sessions, task execution, and system health.
    """
    
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser_sessions: Dict[str, Dict[str, Any]] = {}
        self.active_browsers: Dict[str, Browser] = {}
        self.health_status = {"status": "healthy", "last_check": datetime.utcnow()}
    
    async def initialize(self):
        """Initialize Playwright browser automation"""
        try:
            self.playwright = await async_playwright().start()
            logger.info("Playwright initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Playwright: {str(e)}")
            self.health_status = {"status": "unhealthy", "error": str(e)}
            return False
    
    async def shutdown(self):
        """Shutdown Playwright and cleanup all resources"""
        try:
            # Close all active browsers
            for browser_id, browser in self.active_browsers.items():
                try:
                    await browser.close()
                except Exception as e:
                    logger.warning(f"Error closing browser {browser_id}: {str(e)}")
            
            # Shutdown Playwright
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            self.active_browsers.clear()
            self.browser_sessions.clear()
            logger.info("Playwright shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during Playwright shutdown: {str(e)}")
    
    async def create_session(
        self, 
        session_id: str, 
        browser_type: str, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new browser session"""
        
        if not self.playwright:
            await self.initialize()
        
        try:
            # Create browser instance
            browser_kwargs = {}
            
            # Handle browser type
            if browser_type.lower() == "chromium":
                browser = await self.playwright.chromium.launch(**browser_kwargs)
            elif browser_type.lower() == "firefox":
                browser = await self.playwright.firefox.launch(**browser_kwargs)
            elif browser_type.lower() == "webkit":
                browser = await self.playwright.webkit.launch(**browser_kwargs)
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
            
            # Create browser context
            context_kwargs = {}
            if config.get("viewport"):
                context_kwargs["viewport"] = config["viewport"]
            if config.get("user_agent"):
                context_kwargs["user_agent"] = config["user_agent"]
            if config.get("ignore_https_errors"):
                context_kwargs["ignore_https_errors"] = config["ignore_https_errors"]
            
            context = await browser.new_context(**context_kwargs)
            
            # Create page
            page = await context.new_page()
            
            # Store session info
            session_info = {
                "session_id": session_id,
                "browser": browser,
                "context": context,
                "page": page,
                "browser_type": browser_type,
                "config": config,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "status": "active"
            }
            
            self.active_browsers[session_id] = browser
            self.browser_sessions[session_id] = session_info
            
            logger.info(f"Created browser session {session_id}")
            
            # Get browser info
            browser_info = {
                "browser_type": browser.browser_type.name,
                "version": await browser.version(),
                "user_agent": await page.evaluate("navigator.userAgent")
            }
            
            return {
                "session_id": session_id,
                "browser_info": browser_info,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Failed to create browser session {session_id}: {str(e)}")
            raise
    
    async def close_session(self, session_id: str):
        """Close a browser session"""
        
        try:
            if session_id in self.browser_sessions:
                session_info = self.browser_sessions[session_id]
                
                # Close page
                if "page" in session_info:
                    await session_info["page"].close()
                
                # Close context
                if "context" in session_info:
                    await session_info["context"].close()
                
                # Close browser
                if "browser" in session_info:
                    await session_info["browser"].close()
                
                # Remove from tracking
                self.browser_sessions.pop(session_id, None)
                self.active_browsers.pop(session_id, None)
                
                logger.info(f"Closed browser session {session_id}")
                
        except Exception as e:
            logger.error(f"Error closing browser session {session_id}: {str(e)}")
            raise
    
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a browser session"""
        
        if session_id not in self.browser_sessions:
            return {"error": "Session not found"}
        
        session_info = self.browser_sessions[session_id]
        
        try:
            # Update last activity
            session_info["last_activity"] = datetime.utcnow()
            
            # Get current page info if available
            page_info = {}
            if "page" in session_info:
                page = session_info["page"]
                try:
                    current_url = await page.url()
                    title = await page.title()
                    page_info = {
                        "current_url": current_url,
                        "title": title
                    }
                except Exception:
                    pass
            
            return {
                "session_id": session_id,
                "browser_type": session_info["browser_type"],
                "status": session_info["status"],
                "created_at": session_info["created_at"],
                "last_activity": session_info["last_activity"],
                "page_info": page_info
            }
            
        except Exception as e:
            logger.error(f"Error getting session info for {session_id}: {str(e)}")
            return {"error": str(e)}
    
    async def execute_javascript(self, session_id: str, script: str, timeout: int = 30) -> Any:
        """Execute JavaScript in a browser session"""
        
        if session_id not in self.browser_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        try:
            result = await page.evaluate(script, timeout=timeout * 1000)
            session_info["last_activity"] = datetime.utcnow()
            return result
        except Exception as e:
            logger.error(f"JavaScript execution failed in session {session_id}: {str(e)}")
            raise
    
    async def navigate_to(self, session_id: str, url: str, wait_until: str = "load", timeout: int = 30) -> Dict[str, Any]:
        """Navigate to a URL in a browser session"""
        
        if session_id not in self.browser_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        try:
            response = await page.goto(url, wait_until=wait_until, timeout=timeout * 1000)
            session_info["last_activity"] = datetime.utcnow()
            
            return {
                "url": await page.url(),
                "title": await page.title(),
                "status": response.status if response else None
            }
        except Exception as e:
            logger.error(f"Navigation failed in session {session_id}: {str(e)}")
            raise
    
    async def take_screenshot(self, session_id: str, full_page: bool = False, path: Optional[str] = None) -> bytes:
        """Take a screenshot in a browser session"""
        
        if session_id not in self.browser_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        try:
            screenshot = await page.screenshot(full_page=full_page, path=path)
            session_info["last_activity"] = datetime.utcnow()
            return screenshot
        except Exception as e:
            logger.error(f"Screenshot failed in session {session_id}: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """Check Playwright service health"""
        
        try:
            # Update health check timestamp
            self.health_status["last_check"] = datetime.utcnow()
            
            # Check if Playwright is initialized
            if not self.playwright:
                return False
            
            # Test basic functionality
            test_session_id = f"health_check_{int(time.time())}"
            try:
                await self.create_session(test_session_id, "chromium", {})
                await self.close_session(test_session_id)
                self.health_status["status"] = "healthy"
                return True
            except Exception as e:
                logger.error(f"Playwright health check failed: {str(e)}")
                self.health_status["status"] = "unhealthy"
                return False
                
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            self.health_status["status"] = "unhealthy"
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Playwright manager statistics"""
        
        return {
            "active_sessions": len(self.browser_sessions),
            "playwright_initialized": self.playwright is not None,
            "health_status": self.health_status,
            "session_ids": list(self.browser_sessions.keys())
        }


class BrowserSessionManager:
    """
    Manages browser session lifecycle including creation, reuse, and cleanup.
    Provides session pooling and intelligent session management.
    """
    
    def __init__(self, playwright_manager: PlaywrightManager):
        self.playwright_manager = playwright_manager
        self.session_pools: Dict[str, List[str]] = {}  # browser_type -> list of session_ids
        self.session_metadata: Dict[str, Dict[str, Any]] = {}
        self.max_idle_time = timedelta(minutes=30)
    
    async def acquire_session(
        self, 
        browser_type: str, 
        config: Dict[str, Any],
        preferred_session_id: Optional[str] = None
    ) -> str:
        """Acquire a browser session, creating new or reusing existing"""
        
        session_id = None
        
        # Try to reuse existing session if preferred_session_id provided
        if preferred_session_id and preferred_session_id in self.playwright_manager.browser_sessions:
            session_info = self.playwright_manager.browser_sessions[preferred_session_id]
            if session_info["browser_type"] == browser_type and session_info["status"] == "active":
                session_id = preferred_session_id
        
        # Try to reuse from pool
        if not session_id and browser_type in self.session_pools:
            pool = self.session_pools[browser_type]
            if pool:
                session_id = pool.pop(0)
                # Verify session is still active
                if session_id in self.playwright_manager.browser_sessions:
                    session_info = self.playwright_manager.browser_sessions[session_id]
                    if session_info["status"] == "active":
                        session_info["last_activity"] = datetime.utcnow()
                    else:
                        session_id = None
        
        # Create new session if none available
        if not session_id:
            session_id = str(uuid4())
            await self.playwright_manager.create_session(session_id, browser_type, config)
        
        # Store metadata
        self.session_metadata[session_id] = {
            "browser_type": browser_type,
            "config": config,
            "acquired_at": datetime.utcnow(),
            "reuse_count": self.session_metadata.get(session_id, {}).get("reuse_count", 0) + 1
        }
        
        return session_id
    
    async def release_session(self, session_id: str, return_to_pool: bool = True):
        """Release a browser session back to pool or close it"""
        
        if session_id not in self.playwright_manager.browser_sessions:
            return
        
        session_info = self.playwright_manager.browser_sessions[session_id]
        browser_type = session_info["browser_type"]
        
        if return_to_pool:
            # Add to pool for reuse
            if browser_type not in self.session_pools:
                self.session_pools[browser_type] = []
            
            # Check if session is still usable
            last_activity = session_info.get("last_activity")
            if last_activity and datetime.utcnow() - last_activity > self.max_idle_time:
                # Session is too old, close it
                await self.playwright_manager.close_session(session_id)
                return
            
            self.session_pools[browser_type].append(session_id)
            logger.info(f"Session {session_id} returned to pool")
        else:
            # Close the session
            await self.playwright_manager.close_session(session_id)
    
    async def cleanup_idle_sessions(self):
        """Clean up idle sessions beyond pool limits"""
        
        current_time = datetime.utcnow()
        
        for browser_type, pool in self.session_pools.items():
            # Keep only the most recent sessions
            if len(pool) > 10:  # Max pool size per browser type
                sessions_to_close = pool[10:]
                for session_id in sessions_to_close:
                    await self.playwright_manager.close_session(session_id)
                self.session_pools[browser_type] = pool[:10]
        
        # Close sessions that have been idle too long
        sessions_to_close = []
        for session_id, session_info in self.playwright_manager.browser_sessions.items():
            if "last_activity" in session_info:
                if current_time - session_info["last_activity"] > self.max_idle_time:
                    sessions_to_close.append(session_id)
        
        for session_id in sessions_to_close:
            await self.playwright_manager.close_session(session_id)
            logger.info(f"Closed idle session {session_id}")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get session pool statistics"""
        
        return {
            "pools": {
                browser_type: {
                    "pool_size": len(sessions),
                    "session_ids": sessions
                }
                for browser_type, sessions in self.session_pools.items()
            },
            "total_active_sessions": len(self.playwright_manager.browser_sessions),
            "max_idle_time_minutes": self.max_idle_time.total_seconds() / 60
        }


class TaskExecutor:
    """
    Executes automation tasks using Playwright browser sessions.
    Handles task queuing, execution, error handling, and result collection.
    """
    
    def __init__(self, playwright_manager: PlaywrightManager, session_manager: BrowserSessionManager):
        self.playwright_manager = playwright_manager
        self.session_manager = session_manager
        self.task_queue: List[Dict[str, Any]] = []
        self.executing_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: Dict[str, Dict[str, Any]] = {}
        self.max_concurrent_tasks = 10
    
    async def execute_task(
        self, 
        task_id: str, 
        browser_session_id: Optional[str] = None,
        override_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute an automation task"""
        
        # For now, this is a placeholder implementation
        # In a real implementation, this would:
        # 1. Get task details from database
        # 2. Acquire browser session
        # 3. Execute task steps
        # 4. Collect results and artifacts
        # 5. Update task status
        
        try:
            # Simulate task execution
            logger.info(f"Executing task {task_id}")
            
            # Get browser session
            if browser_session_id:
                session_id = browser_session_id
            else:
                session_id = await self.session_manager.acquire_session(
                    "chromium", 
                    override_config or {}
                )
            
            # Simulate navigation and interaction
            try:
                # This would be the actual task execution logic
                pass
                
                # Return mock result
                result = {
                    "success": True,
                    "session_id": session_id,
                    "steps_completed": 1,
                    "artifacts": [],
                    "execution_time": 0.0
                }
                
                # Release session if we acquired it
                if not browser_session_id:
                    await self.session_manager.release_session(session_id)
                
                return result
                
            except Exception as e:
                # Release session on error
                if not browser_session_id:
                    await self.session_manager.release_session(session_id)
                raise
            
        except Exception as e:
            logger.error(f"Task execution failed for task {task_id}: {str(e)}")
            raise
    
    async def execute_batch_tasks(
        self, 
        task_ids: List[str], 
        max_concurrent: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Execute multiple tasks in batch"""
        
        max_concurrent = max_concurrent or self.max_concurrent_tasks
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_single_task(task_id: str) -> Dict[str, Any]:
            async with semaphore:
                return await self.execute_task(task_id)
        
        # Execute tasks concurrently
        tasks = [execute_single_task(task_id) for task_id in task_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "task_id": task_ids[i],
                    "success": False,
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def add_to_queue(
        self, 
        task_data: Dict[str, Any], 
        priority: int = 0
    ):
        """Add task to execution queue"""
        
        task_item = {
            "task_id": task_data.get("task_id"),
            "data": task_data,
            "priority": priority,
            "queued_at": datetime.utcnow()
        }
        
        # Insert based on priority (higher priority first)
        inserted = False
        for i, item in enumerate(self.task_queue):
            if priority > item["priority"]:
                self.task_queue.insert(i, task_item)
                inserted = True
                break
        
        if not inserted:
            self.task_queue.append(task_item)
        
        logger.info(f"Task {task_data.get('task_id')} added to queue with priority {priority}")
    
    async def process_queue(self):
        """Process tasks from the queue"""
        
        while self.task_queue and len(self.executing_tasks) < self.max_concurrent_tasks:
            # Get next task from queue
            task_item = self.task_queue.pop(0)
            task_id = task_item["task_id"]
            
            # Start task execution
            self.executing_tasks[task_id] = task_item
            asyncio.create_task(self._execute_queued_task(task_item))
    
    async def _execute_queued_task(self, task_item: Dict[str, Any]):
        """Execute a task from the queue"""
        
        task_id = task_item["task_id"]
        
        try:
            result = await self.execute_task(task_id, task_data=task_item["data"])
            self.completed_tasks[task_id] = result
            
        except Exception as e:
            logger.error(f"Queued task execution failed for {task_id}: {str(e)}")
            self.completed_tasks[task_id] = {
                "success": False,
                "error": str(e)
            }
        
        finally:
            # Remove from executing tasks
            self.executing_tasks.pop(task_id, None)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get task queue statistics"""
        
        return {
            "queue_size": len(self.task_queue),
            "executing_count": len(self.executing_tasks),
            "completed_count": len(self.completed_tasks),
            "max_concurrent": self.max_concurrent_tasks
        }


class ArtifactManager:
    """
    Manages file artifacts generated during automation tasks.
    Handles storage, retrieval, cleanup, and organization of artifacts.
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or settings.PLAYWRIGHT_ARTIFACTS_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.cleanup_days = 30
    
    async def save_artifact(
        self,
        artifact_name: str,
        content: Union[bytes, str],
        artifact_type: ArtifactType,
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save an artifact file"""
        
        # Create task-specific directory
        task_dir = self.base_dir / (task_id or "general")
        task_dir.mkdir(exist_ok=True)
        
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in artifact_name if c.isalnum() or c in ('.', '-', '_')).rstrip()
        filename = f"{timestamp}_{safe_name}"
        
        # Add appropriate extension based on artifact type
        extensions = {
            ArtifactType.SCREENSHOT: ".png",
            ArtifactType.PDF: ".pdf",
            ArtifactType.HTML: ".html",
            ArtifactType.JSON: ".json",
            ArtifactType.CSV: ".csv",
            ArtifactType.LOG: ".log"
        }
        
        filename += extensions.get(artifact_type, "")
        file_path = task_dir / filename
        
        # Save file
        try:
            if isinstance(content, str):
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(content)
            else:
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(content)
            
            # Get file info
            file_stats = await aiofiles.os.stat(file_path)
            
            artifact_info = {
                "artifact_name": artifact_name,
                "file_path": str(file_path),
                "artifact_type": artifact_type,
                "file_size": file_stats.st_size,
                "mime_type": mime_type or self._get_mime_type(artifact_type),
                "task_id": task_id,
                "metadata": metadata or {},
                "created_at": datetime.utcnow()
            }
            
            logger.info(f"Saved artifact {artifact_name} to {file_path}")
            return artifact_info
            
        except Exception as e:
            logger.error(f"Failed to save artifact {artifact_name}: {str(e)}")
            raise
    
    async def get_artifact(self, file_path: str) -> Dict[str, Any]:
        """Get artifact information and file path"""
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Artifact file not found: {file_path}")
        
        file_stats = await aiofiles.os.stat(path)
        
        return {
            "file_path": str(path),
            "file_name": path.name,
            "file_size": file_stats.st_size,
            "created_at": datetime.fromtimestamp(file_stats.st_ctime),
            "modified_at": datetime.fromtimestamp(file_stats.st_mtime)
        }
    
    async def delete_artifact(self, file_path: str):
        """Delete an artifact file"""
        
        try:
            path = Path(file_path)
            if path.exists():
                await aiofiles.os.remove(path)
                logger.info(f"Deleted artifact: {file_path}")
            else:
                logger.warning(f"Artifact file not found for deletion: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete artifact {file_path}: {str(e)}")
            raise
    
    async def list_artifacts(
        self, 
        task_id: Optional[str] = None,
        artifact_type: Optional[ArtifactType] = None
    ) -> List[Dict[str, Any]]:
        """List artifacts, optionally filtered by task or type"""
        
        artifacts = []
        
        # Search in base directory or task-specific directory
        search_dir = self.base_dir / (task_id or "")
        if not search_dir.exists():
            return artifacts
        
        for file_path in search_dir.rglob("*"):
            if file_path.is_file():
                try:
                    artifact_info = await self.get_artifact(str(file_path))
                    
                    # Apply filters
                    if task_id and artifact_info.get("task_id") != task_id:
                        continue
                    
                    # Determine artifact type from extension
                    file_ext = file_path.suffix.lower()
                    detected_type = self._get_artifact_type_from_extension(file_ext)
                    if artifact_type and detected_type != artifact_type:
                        continue
                    
                    artifact_info["artifact_type"] = detected_type
                    artifacts.append(artifact_info)
                    
                except Exception as e:
                    logger.warning(f"Error processing artifact {file_path}: {str(e)}")
        
        # Sort by creation date
        artifacts.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        
        return artifacts
    
    async def cleanup_old_artifacts(self):
        """Clean up old artifacts beyond retention period"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=self.cleanup_days)
        deleted_count = 0
        
        for file_path in self.base_dir.rglob("*"):
            if file_path.is_file():
                try:
                    file_stats = await aiofiles.os.stat(file_path)
                    created_date = datetime.fromtimestamp(file_stats.st_ctime)
                    
                    if created_date < cutoff_date:
                        await aiofiles.os.remove(file_path)
                        deleted_count += 1
                        
                except Exception as e:
                    logger.warning(f"Error cleaning up artifact {file_path}: {str(e)}")
        
        logger.info(f"Cleaned up {deleted_count} old artifacts")
        return deleted_count
    
    def _get_mime_type(self, artifact_type: ArtifactType) -> str:
        """Get MIME type for artifact type"""
        
        mime_types = {
            ArtifactType.SCREENSHOT: "image/png",
            ArtifactType.PDF: "application/pdf",
            ArtifactType.HTML: "text/html",
            ArtifactType.JSON: "application/json",
            ArtifactType.CSV: "text/csv",
            ArtifactType.LOG: "text/plain"
        }
        
        return mime_types.get(artifact_type, "application/octet-stream")
    
    def _get_artifact_type_from_extension(self, extension: str) -> ArtifactType:
        """Determine artifact type from file extension"""
        
        type_mapping = {
            ".png": ArtifactType.SCREENSHOT,
            ".jpg": ArtifactType.SCREENSHOT,
            ".jpeg": ArtifactType.SCREENSHOT,
            ".pdf": ArtifactType.PDF,
            ".html": ArtifactType.HTML,
            ".htm": ArtifactType.HTML,
            ".json": ArtifactType.JSON,
            ".csv": ArtifactType.CSV,
            ".log": ArtifactType.LOG
        }
        
        return type_mapping.get(extension.lower(), ArtifactType.OTHER)
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get artifact storage statistics"""
        
        total_size = 0
        file_count = 0
        type_counts = {artifact_type: 0 for artifact_type in ArtifactType}
        
        for file_path in self.base_dir.rglob("*"):
            if file_path.is_file():
                try:
                    file_stats = file_path.stat()
                    total_size += file_stats.st_size
                    file_count += 1
                    
                    # Count by type
                    extension = file_path.suffix.lower()
                    artifact_type = self._get_artifact_type_from_extension(extension)
                    type_counts[artifact_type] += 1
                    
                except Exception:
                    continue
        
        return {
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "file_count": file_count,
            "type_counts": type_counts,
            "storage_dir": str(self.base_dir)
        }


class PoolManager:
    """
    Manages browser pools for high-throughput automation scenarios.
    Provides scalable browser session management with automatic scaling.
    """
    
    def __init__(self, playwright_manager: PlaywrightManager):
        self.playwright_manager = playwright_manager
        self.browser_pools: Dict[str, Dict[str, Any]] = {}
        self.session_manager = BrowserSessionManager(playwright_manager)
    
    async def create_pool(
        self,
        pool_id: str,
        browser_type: str,
        config: Dict[str, Any],
        max_size: int = 10,
        min_size: int = 0
    ):
        """Create a new browser pool"""
        
        try:
            pool_info = {
                "pool_id": pool_id,
                "browser_type": browser_type,
                "config": config,
                "max_size": max_size,
                "min_size": min_size,
                "current_size": 0,
                "active_sessions": [],
                "idle_sessions": [],
                "created_at": datetime.utcnow(),
                "status": "active"
            }
            
            self.browser_pools[pool_id] = pool_info
            
            # Initialize with minimum sessions
            for _ in range(min_size):
                session_id = await self._create_pool_session(pool_id)
                if session_id:
                    pool_info["idle_sessions"].append(session_id)
                    pool_info["current_size"] += 1
            
            logger.info(f"Created browser pool {pool_id} with {min_size} initial sessions")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create browser pool {pool_id}: {str(e)}")
            raise
    
    async def close_pool(self, pool_id: str):
        """Close a browser pool and all its sessions"""
        
        if pool_id not in self.browser_pools:
            raise ValueError(f"Pool {pool_id} not found")
        
        pool_info = self.browser_pools[pool_id]
        
        try:
            # Close all sessions
            all_sessions = pool_info["active_sessions"] + pool_info["idle_sessions"]
            for session_id in all_sessions:
                try:
                    await self.playwright_manager.close_session(session_id)
                except Exception as e:
                    logger.warning(f"Error closing session {session_id}: {str(e)}")
            
            # Remove pool
            del self.browser_pools[pool_id]
            
            logger.info(f"Closed browser pool {pool_id}")
            
        except Exception as e:
            logger.error(f"Failed to close browser pool {pool_id}: {str(e)}")
            raise
    
    async def get_session(self, pool_id: str, timeout: int = 30) -> str:
        """Get a session from the pool"""
        
        if pool_id not in self.browser_pools:
            raise ValueError(f"Pool {pool_id} not found")
        
        pool_info = self.browser_pools[pool_id]
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Try to get from idle sessions first
            if pool_info["idle_sessions"]:
                session_id = pool_info["idle_sessions"].pop(0)
                pool_info["active_sessions"].append(session_id)
                logger.info(f"Assigned session {session_id} from pool {pool_id}")
                return session_id
            
            # Check if we can create more sessions
            if pool_info["current_size"] < pool_info["max_size"]:
                session_id = await self._create_pool_session(pool_id)
                if session_id:
                    pool_info["active_sessions"].append(session_id)
                    pool_info["current_size"] += 1
                    logger.info(f"Created new session {session_id} in pool {pool_id}")
                    return session_id
            
            # Wait a bit before retrying
            await asyncio.sleep(1)
        
        raise TimeoutError(f"Failed to get session from pool {pool_id} within {timeout} seconds")
    
    async def return_session(self, pool_id: str, session_id: str):
        """Return a session to the pool"""
        
        if pool_id not in self.browser_pools:
            raise ValueError(f"Pool {pool_id} not found")
        
        pool_info = self.browser_pools[pool_id]
        
        # Remove from active sessions
        if session_id in pool_info["active_sessions"]:
            pool_info["active_sessions"].remove(session_id)
            
            # Add to idle sessions if under max idle limit
            if len(pool_info["idle_sessions"]) < 5:  # Max idle sessions to keep
                pool_info["idle_sessions"].append(session_id)
                logger.info(f"Returned session {session_id} to pool {pool_id}")
            else:
                # Close session if too many idle
                await self.playwright_manager.close_session(session_id)
                pool_info["current_size"] -= 1
    
    async def expand_pool(self, pool_id: str, additional_size: int):
        """Expand a browser pool by adding more sessions"""
        
        if pool_id not in self.browser_pools:
            raise ValueError(f"Pool {pool_id} not found")
        
        pool_info = self.browser_pools[pool_id]
        
        try:
            # Add new sessions
            for _ in range(additional_size):
                session_id = await self._create_pool_session(pool_id)
                if session_id:
                    pool_info["idle_sessions"].append(session_id)
                    pool_info["current_size"] += 1
            
            pool_info["max_size"] += additional_size
            
            logger.info(f"Expanded pool {pool_id} by {additional_size} sessions")
            
        except Exception as e:
            logger.error(f"Failed to expand pool {pool_id}: {str(e)}")
            raise
    
    async def shrink_pool(self, pool_id: str, reduce_by: int):
        """Shrink a browser pool by removing sessions"""
        
        if pool_id not in self.browser_pools:
            raise ValueError(f"Pool {pool_id} not found")
        
        pool_info = self.browser_pools[pool_id]
        
        try:
            sessions_to_close = min(reduce_by, len(pool_info["idle_sessions"]))
            
            for _ in range(sessions_to_close):
                if pool_info["idle_sessions"]:
                    session_id = pool_info["idle_sessions"].pop(0)
                    await self.playwright_manager.close_session(session_id)
                    pool_info["current_size"] -= 1
            
            pool_info["max_size"] -= sessions_to_close
            
            logger.info(f"Shrunk pool {pool_id} by {sessions_to_close} sessions")
            
        except Exception as e:
            logger.error(f"Failed to shrink pool {pool_id}: {str(e)}")
            raise
    
    async def _create_pool_session(self, pool_id: str) -> Optional[str]:
        """Create a new session for a pool"""
        
        if pool_id not in self.browser_pools:
            return None
        
        pool_info = self.browser_pools[pool_id]
        session_id = str(uuid4())
        
        try:
            await self.playwright_manager.create_session(
                session_id, 
                pool_info["browser_type"], 
                pool_info["config"]
            )
            return session_id
        except Exception as e:
            logger.error(f"Failed to create pool session {session_id}: {str(e)}")
            return None
    
    async def get_pool_info(self, pool_id: str) -> Dict[str, Any]:
        """Get information about a browser pool"""
        
        if pool_id not in self.browser_pools:
            return {"error": "Pool not found"}
        
        pool_info = self.browser_pools[pool_id]
        
        return {
            "pool_id": pool_id,
            "browser_type": pool_info["browser_type"],
            "max_size": pool_info["max_size"],
            "min_size": pool_info["min_size"],
            "current_size": pool_info["current_size"],
            "active_sessions_count": len(pool_info["active_sessions"]),
            "idle_sessions_count": len(pool_info["idle_sessions"]),
            "status": pool_info["status"],
            "created_at": pool_info["created_at"]
        }
    
    async def health_check(self) -> bool:
        """Check browser pool manager health"""
        
        try:
            # Check if Playwright manager is healthy
            if not await self.playwright_manager.health_check():
                return False
            
            # Test pool functionality
            test_pool_id = f"health_check_pool_{int(time.time())}"
            try:
                await self.create_pool(test_pool_id, "chromium", {}, 1, 0)
                session_id = await self.get_session(test_pool_id, 5)
                await self.return_session(test_pool_id, session_id)
                await self.close_pool(test_pool_id)
                return True
            except Exception as e:
                logger.error(f"Pool health check failed: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"Pool manager health check error: {str(e)}")
            return False
    
    def get_all_pools_stats(self) -> Dict[str, Any]:
        """Get statistics for all browser pools"""
        
        total_pools = len(self.browser_pools)
        total_capacity = sum(pool["max_size"] for pool in self.browser_pools.values())
        total_current = sum(pool["current_size"] for pool in self.browser_pools.values())
        total_active = sum(len(pool["active_sessions"]) for pool in self.browser_pools.values())
        total_idle = sum(len(pool["idle_sessions"]) for pool in self.browser_pools.values())
        
        return {
            "total_pools": total_pools,
            "total_capacity": total_capacity,
            "total_current": total_current,
            "total_active_sessions": total_active,
            "total_idle_sessions": total_idle,
            "utilization_rate": (total_active / total_capacity * 100) if total_capacity > 0 else 0,
            "pool_details": {
                pool_id: {
                    "capacity": pool["max_size"],
                    "current": pool["current_size"],
                    "active": len(pool["active_sessions"]),
                    "idle": len(pool["idle_sessions"]),
                    "utilization": (len(pool["active_sessions"]) / pool["max_size"] * 100) if pool["max_size"] > 0 else 0
                }
                for pool_id, pool in self.browser_pools.items()
            }
        }


# Global instances
_playwright_manager: Optional[PlaywrightManager] = None
_pool_manager: Optional[PoolManager] = None


async def get_playwright_manager() -> PlaywrightManager:
    """Get or create global Playwright manager instance"""
    global _playwright_manager
    
    if _playwright_manager is None:
        _playwright_manager = PlaywrightManager()
        await _playwright_manager.initialize()
    
    return _playwright_manager


async def get_pool_manager() -> PoolManager:
    """Get or create global pool manager instance"""
    global _pool_manager, _playwright_manager
    
    if _pool_manager is None:
        if _playwright_manager is None:
            _playwright_manager = await get_playwright_manager()
        _pool_manager = PoolManager(_playwright_manager)
    
    return _pool_manager


async def cleanup_playwright_resources():
    """Cleanup all Playwright resources"""
    global _playwright_manager, _pool_manager
    
    if _pool_manager:
        # Close all pools
        for pool_id in list(_pool_manager.browser_pools.keys()):
            try:
                await _pool_manager.close_pool(pool_id)
            except Exception as e:
                logger.warning(f"Error closing pool {pool_id}: {str(e)}")
    
    if _playwright_manager:
        await _playwright_manager.shutdown()
    
    _playwright_manager = None
    _pool_manager = None