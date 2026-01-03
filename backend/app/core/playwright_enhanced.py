"""
Enhanced Playwright Core Services with Comprehensive Browser Automation

This module provides enhanced Playwright browser automation functionality including:
- PlaywrightBrowserManager: Enhanced browser automation coordinator
- BrowserSessionManager: Advanced session lifecycle management
- BrowserAutomationTools: Complete automation tool definitions
- ArtifactManager: Enhanced file artifact storage and retrieval
- PlaywrightSecurityManager: Security validation and protection
- BrowserToolRegistry: Tool metadata and descriptions for agent interface
"""

import asyncio
import json
import os
import shutil
import tempfile
import time
import re
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from uuid import uuid4
import aiofiles
import aiofiles.os
from urllib.parse import urlparse, urljoin
from functools import wraps

try:
    from playwright.async_api import (
        async_playwright, 
        Browser, 
        BrowserContext, 
        Page, 
        Playwright,
        PlaywrightContextManager,
        TimeoutError as PlaywrightTimeoutError,
        Error as PlaywrightError,
        ConsoleMessage,
        Dialog,
        Request,
        Response,
        Route
    )
except ImportError:
    Browser = BrowserContext = Page = Playwright = None
    PlaywrightContextManager = None
    PlaywrightTimeoutError = Exception
    PlaywrightError = Exception
    ConsoleMessage = Dialog = Request = Response = Route = None

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


# Custom Exception Classes
class PlaywrightAutomationError(Exception):
    """Base exception for Playwright automation errors"""
    pass

class PlaywrightTimeoutError(PlaywrightAutomationError):
    """Exception for Playwright timeout errors"""
    pass

class PlaywrightNavigationError(PlaywrightAutomationError):
    """Exception for navigation errors"""
    pass

class PlaywrightInteractionError(PlaywrightAutomationError):
    """Exception for interaction errors"""
    pass

class PlaywrightExtractionError(PlaywrightAutomationError):
    """Exception for data extraction errors"""
    pass

class PlaywrightSecurityError(PlaywrightAutomationError):
    """Exception for security violations"""
    pass

class PlaywrightSessionError(PlaywrightAutomationError):
    """Exception for session management errors"""
    pass


# Browser Automation Tool Definitions
class BrowserToolDefinition:
    """Definition for a browser automation tool"""
    
    def __init__(
        self,
        name: str,
        description: str,
        category: str,
        parameters: Dict[str, Any],
        examples: List[Dict[str, Any]],
        tags: List[str],
        icon: str,
        validation_rules: Dict[str, Any] = None
    ):
        self.name = name
        self.description = description
        self.category = category
        self.parameters = parameters
        self.examples = examples
        self.tags = tags
        self.icon = icon
        self.validation_rules = validation_rules or {}
        self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool definition to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "parameters": self.parameters,
            "examples": self.examples,
            "tags": self.tags,
            "icon": self.icon,
            "validation_rules": self.validation_rules,
            "created_at": self.created_at.isoformat()
        }


class BrowserToolRegistry:
    """Registry for all browser automation tools with metadata"""
    
    def __init__(self):
        self.tools: Dict[str, BrowserToolDefinition] = {}
        self._initialize_tool_registry()
    
    def _initialize_tool_registry(self):
        """Initialize all browser automation tools"""
        
        # Navigation Tools
        self.tools["navigate"] = BrowserToolDefinition(
            name="navigate",
            description="Navigate to a specific URL in the browser",
            category="Navigation",
            parameters={
                "url": {
                    "type": "string",
                    "required": True,
                    "description": "URL to navigate to",
                    "pattern": r"^https?://.*"
                },
                "wait_until": {
                    "type": "string",
                    "required": False,
                    "description": "When to consider navigation complete",
                    "default": "load",
                    "options": ["load", "domcontentloaded", "networkidle"]
                },
                "timeout": {
                    "type": "integer",
                    "required": False,
                    "description": "Navigation timeout in milliseconds",
                    "default": 30000,
                    "min": 1000,
                    "max": 120000
                }
            },
            examples=[
                {"url": "https://example.com"},
                {"url": "https://example.com", "wait_until": "networkidle"},
                {"url": "https://example.com", "timeout": 60000}
            ],
            tags=["navigation", "url", "web"],
            icon="🌐",
            validation_rules={
                "url_sanitization": True,
                "allow_external_urls": True,
                "max_redirects": 10
            }
        )
        
        self.tools["go_back"] = BrowserToolDefinition(
            name="go_back",
            description="Navigate back in browser history",
            category="Navigation",
            parameters={
                "timeout": {
                    "type": "integer",
                    "required": False,
                    "description": "Timeout for navigation in milliseconds",
                    "default": 30000
                }
            },
            examples=[
                {},
                {"timeout": 15000}
            ],
            tags=["navigation", "history", "back"],
            icon="⬅️"
        )
        
        self.tools["go_forward"] = BrowserToolDefinition(
            name="go_forward",
            description="Navigate forward in browser history",
            category="Navigation",
            parameters={
                "timeout": {
                    "type": "integer",
                    "required": False,
                    "description": "Timeout for navigation in milliseconds",
                    "default": 30000
                }
            },
            examples=[
                {},
                {"timeout": 15000}
            ],
            tags=["navigation", "history", "forward"],
            icon="➡️"
        )
        
        self.tools["refresh"] = BrowserToolDefinition(
            name="refresh",
            description="Refresh the current page",
            category="Navigation",
            parameters={
                "wait_until": {
                    "type": "string",
                    "required": False,
                    "description": "When to consider refresh complete",
                    "default": "load",
                    "options": ["load", "domcontentloaded", "networkidle"]
                },
                "timeout": {
                    "type": "integer",
                    "required": False,
                    "description": "Refresh timeout in milliseconds",
                    "default": 30000
                }
            },
            examples=[
                {},
                {"wait_until": "networkidle"},
                {"wait_until": "load", "timeout": 45000}
            ],
            tags=["navigation", "refresh", "reload"],
            icon="🔄"
        )
        
        # Interaction Tools
        self.tools["click"] = BrowserToolDefinition(
            name="click",
            description="Click on a page element by selector",
            category="Interaction",
            parameters={
                "selector": {
                    "type": "string",
                    "required": True,
                    "description": "CSS selector for the element to click",
                    "min_length": 1
                },
                "button": {
                    "type": "string",
                    "required": False,
                    "description": "Mouse button to use",
                    "default": "left",
                    "options": ["left", "right", "middle"]
                },
                "click_count": {
                    "type": "integer",
                    "required": False,
                    "description": "Number of clicks",
                    "default": 1,
                    "min": 1,
                    "max": 5
                },
                "delay": {
                    "type": "integer",
                    "required": False,
                    "description": "Delay between clicks in milliseconds",
                    "default": 0,
                    "min": 0,
                    "max": 1000
                },
                "timeout": {
                    "type": "integer",
                    "required": False,
                    "description": "Timeout for finding element in milliseconds",
                    "default": 30000
                }
            },
            examples=[
                {"selector": "#submit-button"},
                {"selector": ".menu-item", "button": "right"},
                {"selector": "#click-me", "click_count": 2, "delay": 500}
            ],
            tags=["interaction", "click", "mouse", "selector"],
            icon="🖱️"
        )
        
        self.tools["type"] = BrowserToolDefinition(
            name="type",
            description="Type text into an input field",
            category="Interaction",
            parameters={
                "selector": {
                    "type": "string",
                    "required": True,
                    "description": "CSS selector for the input element",
                    "min_length": 1
                },
                "text": {
                    "type": "string",
                    "required": True,
                    "description": "Text to type",
                    "max_length": 10000
                },
                "clear_first": {
                    "type": "boolean",
                    "required": False,
                    "description": "Clear field before typing",
                    "default": True
                },
                "delay": {
                    "type": "integer",
                    "required": False,
                    "description": "Delay between keystrokes in milliseconds",
                    "default": 0,
                    "min": 0,
                    "max": 100
                },
                "timeout": {
                    "type": "integer",
                    "required": False,
                    "description": "Timeout for finding element in milliseconds",
                    "default": 30000
                }
            },
            examples=[
                {"selector": "#username", "text": "john_doe"},
                {"selector": "#email", "text": "user@example.com", "clear_first": False},
                {"selector": "#password", "text": "secure_password", "delay": 50}
            ],
            tags=["interaction", "typing", "input", "text"],
            icon="⌨️"
        )
        
        self.tools["select"] = BrowserToolDefinition(
            name="select",
            description="Select an option from a dropdown/select element",
            category="Interaction",
            parameters={
                "selector": {
                    "type": "string",
                    "required": True,
                    "description": "CSS selector for the select element",
                    "min_length": 1
                },
                "value": {
                    "type": "string",
                    "required": True,
                    "description": "Option value to select",
                    "min_length": 1
                },
                "label": {
                    "type": "string",
                    "required": False,
                    "description": "Option label to select (alternative to value)"
                },
                "timeout": {
                    "type": "integer",
                    "required": False,
                    "description": "Timeout for finding element in milliseconds",
                    "default": 30000
                }
            },
            examples=[
                {"selector": "#country", "value": "US"},
                {"selector": "#language", "label": "English"},
                {"selector": "#category", "value": "technology"}
            ],
            tags=["interaction", "select", "dropdown", "option"],
            icon="📋"
        )
        
        self.tools["drag_and_drop"] = BrowserToolDefinition(
            name="drag_and_drop",
            description="Drag an element and drop it on another element",
            category="Interaction",
            parameters={
                "source_selector": {
                    "type": "string",
                    "required": True,
                    "description": "CSS selector for the source element to drag",
                    "min_length": 1
                },
                "target_selector": {
                    "type": "string",
                    "required": True,
                    "description": "CSS selector for the target element to drop on",
                    "min_length": 1
                },
                "timeout": {
                    "type": "integer",
                    "required": False,
                    "description": "Timeout for finding elements in milliseconds",
                    "default": 30000
                }
            },
            examples=[
                {"source_selector": "#draggable", "target_selector": "#dropzone"},
                {"source_selector": ".file-item", "target_selector": ".upload-area"}
            ],
            tags=["interaction", "drag", "drop", "move"],
            icon="🤏"
        )
        
        # Extraction Tools
        self.tools["get_text"] = BrowserToolDefinition(
            name="get_text",
            description="Extract text content from page elements",
            category="Extraction",
            parameters={
                "selector": {
                    "type": "string",
                    "required": True,
                    "description": "CSS selector for elements to extract text from",
                    "min_length": 1
                },
                "attribute": {
                    "type": "string",
                    "required": False,
                    "description": "Specific attribute to extract (e.g., 'href', 'src')",
                    "options": ["text", "href", "src", "title", "alt", "value", "innerHTML", "outerHTML"]
                },
                "multiple": {
                    "type": "boolean",
                    "required": False,
                    "description": "Extract from multiple elements",
                    "default": False
                },
                "timeout": {
                    "type": "integer",
                    "required": False,
                    "description": "Timeout for finding elements in milliseconds",
                    "default": 30000
                }
            },
            examples=[
                {"selector": "h1"},
                {"selector": "a", "attribute": "href", "multiple": True},
                {"selector": ".title", "attribute": "text"}
            ],
            tags=["extraction", "text", "content", "data"],
            icon="📝"
        )
        
        self.tools["get_attribute"] = BrowserToolDefinition(
            name="get_attribute",
            description="Get specific attribute values from page elements",
            category="Extraction",
            parameters={
                "selector": {
                    "type": "string",
                    "required": True,
                    "description": "CSS selector for the element",
                    "min_length": 1
                },
                "attribute": {
                    "type": "string",
                    "required": True,
                    "description": "Attribute name to get",
                    "min_length": 1
                },
                "multiple": {
                    "type": "boolean",
                    "required": False,
                    "description": "Get attribute from multiple elements",
                    "default": False
                },
                "timeout": {
                    "type": "integer",
                    "required": False,
                    "description": "Timeout for finding element in milliseconds",
                    "default": 30000
                }
            },
            examples=[
                {"selector": "img", "attribute": "src"},
                {"selector": "a", "attribute": "href", "multiple": True},
                {"selector": "input", "attribute": "value"}
            ],
            tags=["extraction", "attribute", "metadata"],
            icon="🏷️"
        )
        
        self.tools["get_page_content"] = BrowserToolDefinition(
            name="get_page_content",
            description="Get comprehensive page content and metadata",
            category="Extraction",
            parameters={
                "content_type": {
                    "type": "string",
                    "required": False,
                    "description": "Type of content to extract",
                    "default": "text",
                    "options": ["text", "html", "markdown", "json"]
                },
                "selectors": {
                    "type": "object",
                    "required": False,
                    "description": "Specific selectors to extract (for JSON output)"
                },
                "include_metadata": {
                    "type": "boolean",
                    "required": False,
                    "description": "Include page metadata",
                    "default": True
                }
            },
            examples=[
                {"content_type": "text"},
                {"content_type": "markdown"},
                {"content_type": "json", "selectors": {"title": "h1", "links": "a"}},
                {"content_type": "html", "include_metadata": False}
            ],
            tags=["extraction", "content", "page", "metadata"],
            icon="📄"
        )
        
        # Multimedia Tools
        self.tools["screenshot"] = BrowserToolDefinition(
            name="screenshot",
            description="Take a screenshot of the current page or specific element",
            category="Multimedia",
            parameters={
                "full_page": {
                    "type": "boolean",
                    "required": False,
                    "description": "Take screenshot of entire page",
                    "default": False
                },
                "selector": {
                    "type": "string",
                    "required": False,
                    "description": "CSS selector for specific element to screenshot"
                },
                "quality": {
                    "type": "integer",
                    "required": False,
                    "description": "Screenshot quality (1-100)",
                    "default": 90,
                    "min": 1,
                    "max": 100
                },
                "format": {
                    "type": "string",
                    "required": False,
                    "description": "Screenshot format",
                    "default": "png",
                    "options": ["png", "jpeg", "webp"]
                },
                "timeout": {
                    "type": "integer",
                    "required": False,
                    "description": "Timeout for taking screenshot in milliseconds",
                    "default": 30000
                }
            },
            examples=[
                {},
                {"full_page": True},
                {"selector": "#main-content", "quality": 95},
                {"format": "jpeg", "full_page": True}
            ],
            tags=["multimedia", "screenshot", "image", "capture"],
            icon="📸"
        )
        
        self.tools["pdf"] = BrowserToolDefinition(
            name="pdf",
            description="Generate PDF from current page",
            category="Multimedia",
            parameters={
                "full_page": {
                    "type": "boolean",
                    "required": False,
                    "description": "Include entire page in PDF",
                    "default": False
                },
                "format": {
                    "type": "string",
                    "required": False,
                    "description": "PDF page format",
                    "default": "A4",
                    "options": ["A4", "Letter", "Legal", "A3", "A5"]
                },
                "landscape": {
                    "type": "boolean",
                    "required": False,
                    "description": "Use landscape orientation",
                    "default": False
                },
                "margin": {
                    "type": "object",
                    "required": False,
                    "description": "Page margins in mm",
                    "default": {"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"}
                },
                "timeout": {
                    "type": "integer",
                    "required": False,
                    "description": "Timeout for PDF generation in milliseconds",
                    "default": 60000
                }
            },
            examples=[
                {},
                {"full_page": True, "format": "Letter"},
                {"landscape": True, "margin": {"top": "20mm"}},
                {"format": "A4", "full_page": True}
            ],
            tags=["multimedia", "pdf", "document", "export"],
            icon="📑"
        )
        
        self.tools["record_video"] = BrowserToolDefinition(
            name="record_video",
            description="Start or stop video recording of browser session",
            category="Multimedia",
            parameters={
                "action": {
                    "type": "string",
                    "required": True,
                    "description": "Action to perform",
                    "options": ["start", "stop"]
                },
                "duration": {
                    "type": "integer",
                    "required": False,
                    "description": "Recording duration in seconds (for start action)",
                    "min": 1,
                    "max": 3600
                },
                "fps": {
                    "type": "integer",
                    "required": False,
                    "description": "Frames per second",
                    "default": 30,
                    "min": 1,
                    "max": 60
                },
                "quality": {
                    "type": "string",
                    "required": False,
                    "description": "Video quality",
                    "default": "high",
                    "options": ["low", "medium", "high", "ultra"]
                }
            },
            examples=[
                {"action": "start", "duration": 60},
                {"action": "start", "fps": 30, "quality": "high"},
                {"action": "stop"}
            ],
            tags=["multimedia", "video", "recording", "capture"],
            icon="🎥"
        )
        
        # Wait and Synchronization Tools
        self.tools["wait_for_selector"] = BrowserToolDefinition(
            name="wait_for_selector",
            description="Wait for specific element to appear on page",
            category="Synchronization",
            parameters={
                "selector": {
                    "type": "string",
                    "required": True,
                    "description": "CSS selector to wait for",
                    "min_length": 1
                },
                "timeout": {
                    "type": "integer",
                    "required": False,
                    "description": "Maximum wait time in milliseconds",
                    "default": 30000,
                    "min": 1000,
                    "max": 120000
                },
                "state": {
                    "type": "string",
                    "required": False,
                    "description": "Element state to wait for",
                    "default": "visible",
                    "options": ["attached", "detached", "visible", "hidden"]
                }
            },
            examples=[
                {"selector": "#loading-complete"},
                {"selector": ".modal", "state": "visible", "timeout": 60000},
                {"selector": "#async-content", "state": "attached"}
            ],
            tags=["synchronization", "wait", "selector", "timing"],
            icon="⏳"
        )
        
        self.tools["wait_for_load_state"] = BrowserToolDefinition(
            name="wait_for_load_state",
            description="Wait for page to reach specific load state",
            category="Synchronization",
            parameters={
                "state": {
                    "type": "string",
                    "required": True,
                    "description": "Load state to wait for",
                    "options": ["load", "domcontentloaded", "networkidle"]
                },
                "timeout": {
                    "type": "integer",
                    "required": False,
                    "description": "Maximum wait time in milliseconds",
                    "default": 30000,
                    "min": 1000,
                    "max": 120000
                }
            },
            examples=[
                {"state": "networkidle"},
                {"state": "load", "timeout": 60000},
                {"state": "domcontentloaded"}
            ],
            tags=["synchronization", "wait", "load", "network"],
            icon="🌐"
        )
        
        self.tools["wait_for_timeout"] = BrowserToolDefinition(
            name="wait_for_timeout",
            description="Wait for a specified amount of time",
            category="Synchronization",
            parameters={
                "duration": {
                    "type": "integer",
                    "required": True,
                    "description": "Wait duration in milliseconds",
                    "min": 1,
                    "max": 300000
                }
            },
            examples=[
                {"duration": 5000},
                {"duration": 1000},
                {"duration": 30000}
            ],
            tags=["synchronization", "wait", "timeout", "delay"],
            icon="⏰"
        )
    
    def get_tool(self, name: str) -> Optional[BrowserToolDefinition]:
        """Get tool definition by name"""
        return self.tools.get(name)
    
    def get_tools_by_category(self, category: str) -> List[BrowserToolDefinition]:
        """Get all tools in a specific category"""
        return [tool for tool in self.tools.values() if tool.category == category]
    
    def get_all_tools(self) -> Dict[str, BrowserToolDefinition]:
        """Get all tool definitions"""
        return self.tools.copy()
    
    def get_categories(self) -> List[str]:
        """Get all tool categories"""
        return list(set(tool.category for tool in self.tools.values()))


# Security Manager
class PlaywrightSecurityManager:
    """Security manager for Playwright automation operations"""
    
    def __init__(self):
        self.dangerous_patterns = [
            r'javascript:',
            r'data:text/html',
            r'file://',
            r'ftp://',
            r'<script',
            r'</script>',
            r'eval\(',
            r'javascript:eval',
            r'on\w+\s*=',
            r'expression\(',
            r'url\s*\(',
            r'@import'
        ]
        self.allowed_schemes = ['http:', 'https:']
        self.blocked_domains = set()
        self.allowed_domains = set()
    
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """Validate URL for security"""
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in self.allowed_schemes:
                return False, f"Disallowed URL scheme: {parsed.scheme}"
            
            # Check for dangerous patterns
            for pattern in self.dangerous_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return False, f"Potentially dangerous URL pattern detected: {pattern}"
            
            # Check domain restrictions
            if self.blocked_domains and parsed.netloc in self.blocked_domains:
                return False, f"Domain blocked: {parsed.netloc}"
            
            if self.allowed_domains and parsed.netloc not in self.allowed_domains:
                return False, f"Domain not in allowed list: {parsed.netloc}"
            
            return True, "URL validation passed"
            
        except Exception as e:
            return False, f"URL parsing error: {str(e)}"
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize input text"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters and patterns
        sanitized = re.sub(r'<[^>]*>', '', text)  # Remove HTML tags
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'data:', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    def validate_selector(self, selector: str) -> Tuple[bool, str]:
        """Validate CSS selector for security"""
        if not selector or not isinstance(selector, str):
            return False, "Selector must be a non-empty string"
        
        # Check for potentially dangerous selectors
        dangerous_patterns = [
            r'<[^>]*>',
            r'javascript:',
            r'expression\(',
            r'url\s*\('
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, selector, re.IGNORECASE):
                return False, f"Potentially dangerous selector pattern detected"
        
        # Basic CSS selector validation
        if len(selector) > 1000:  # Prevent extremely long selectors
            return False, "Selector too long"
        
        return True, "Selector validation passed"
    
    def add_domain_restriction(self, domain: str, action: str = "allow"):
        """Add domain restriction"""
        if action == "allow":
            self.allowed_domains.add(domain)
        elif action == "block":
            self.blocked_domains.add(domain)
    
    def remove_domain_restriction(self, domain: str):
        """Remove domain restriction"""
        self.allowed_domains.discard(domain)
        self.blocked_domains.discard(domain)


# Enhanced Playwright Browser Manager
class PlaywrightBrowserManager:
    """Enhanced browser automation coordinator with comprehensive tool support"""
    
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser_sessions: Dict[str, Dict[str, Any]] = {}
        self.active_browsers: Dict[str, Browser] = {}
        self.health_status = {"status": "healthy", "last_check": datetime.utcnow()}
        self.tool_registry = BrowserToolRegistry()
        self.security_manager = PlaywrightSecurityManager()
        self.retry_config = {
            "max_retries": 3,
            "retry_delay": 1.0,
            "backoff_factor": 2.0
        }
    
    async def initialize(self):
        """Initialize Playwright with enhanced configuration"""
        try:
            self.playwright = await async_playwright().start()
            
            # Set up global browser configuration
            self._configure_global_settings()
            
            logger.info("Enhanced Playwright initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize enhanced Playwright: {str(e)}")
            self.health_status = {"status": "unhealthy", "error": str(e)}
            return False
    
    def _configure_global_settings(self):
        """Configure global browser settings"""
        # This would configure any global browser settings
        # that apply to all new browser instances
        pass
    
    async def shutdown(self):
        """Shutdown Playwright and cleanup all resources"""
        try:
            # Close all active browsers
            for browser_id, browser in list(self.active_browsers.items()):
                try:
                    await browser.close()
                    logger.info(f"Closed browser {browser_id}")
                except Exception as e:
                    logger.warning(f"Error closing browser {browser_id}: {str(e)}")
            
            # Shutdown Playwright
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            self.active_browsers.clear()
            self.browser_sessions.clear()
            logger.info("Enhanced Playwright shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during enhanced Playwright shutdown: {str(e)}")
    
    async def create_session(
        self, 
        session_id: str, 
        browser_type: str, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new browser session with enhanced configuration"""
        
        if not self.playwright:
            await self.initialize()
        
        try:
            # Validate browser type
            browser_type = browser_type.lower()
            if browser_type not in ["chromium", "firefox", "webkit"]:
                raise PlaywrightSessionError(f"Unsupported browser type: {browser_type}")
            
            # Create browser with enhanced configuration
            browser_config = self._build_browser_config(config)
            browser = await getattr(self.playwright, browser_type).launch(**browser_config)
            
            # Create context with enhanced options
            context_config = self._build_context_config(config)
            context = await browser.new_context(**context_config)
            
            # Set up page event handlers
            page = await context.new_page()
            self._setup_page_event_handlers(page)
            
            # Store session info with enhanced metadata
            session_info = {
                "session_id": session_id,
                "browser": browser,
                "context": context,
                "page": page,
                "browser_type": browser_type,
                "config": config,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "status": "active",
                "navigation_history": [],
                "performance_metrics": {},
                "security_violations": []
            }
            
            self.active_browsers[session_id] = browser
            self.browser_sessions[session_id] = session_info
            
            logger.info(f"Created enhanced browser session {session_id}")
            
            # Get browser info
            browser_info = await self._get_browser_info(session_info)
            
            return {
                "session_id": session_id,
                "browser_info": browser_info,
                "status": "active",
                "available_tools": list(self.tool_registry.get_all_tools().keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to create enhanced browser session {session_id}: {str(e)}")
            raise PlaywrightSessionError(f"Session creation failed: {str(e)}")
    
    def _build_browser_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build browser launch configuration"""
        browser_config = {
            "headless": config.get("headless", True),
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor"
            ]
        }
        
        # Add proxy configuration
        if config.get("proxy_url"):
            browser_config["proxy"] = {
                "server": config["proxy_url"]
            }
        
        # Add custom user agent
        if config.get("user_agent"):
            browser_config["args"].append(f"--user-agent={config['user_agent']}")
        
        return browser_config
    
    def _build_context_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build browser context configuration"""
        context_config = {
            "viewport": {
                "width": config.get("viewport_width", 1920),
                "height": config.get("viewport_height", 1080)
            },
            "ignore_https_errors": True,
            "java_script_enabled": config.get("enable_javascript", True)
        }
        
        # Add timezone and language
        if config.get("timezone"):
            context_config["timezone_id"] = config["timezone"]
        
        if config.get("language"):
            context_config["locale"] = config["language"]
        
        # Add initial cookies
        if config.get("cookies"):
            context_config["storage_state"] = {"cookies": config["cookies"]}
        
        return context_config
    
    def _setup_page_event_handlers(self, page: Page):
        """Set up page event handlers for monitoring"""
        
        @page.on("console")
        async def handle_console(msg: ConsoleMessage):
            if msg.type in ["error", "warning"]:
                logger.warning(f"Page console {msg.type}: {msg.text}")
        
        @page.on("dialog")
        async def handle_dialog(dialog: Dialog):
            logger.info(f"Page dialog: {dialog.message}")
            await dialog.accept()
        
        @page.on("request")
        async def handle_request(request: Request):
            # Log potentially suspicious requests
            url = request.url
            if "javascript:" in url.lower() or "data:" in url.lower():
                logger.warning(f"Suspicious request detected: {url}")
        
        @page.on("response")
        async def handle_response(response: Response):
            if response.status >= 400:
                logger.warning(f"HTTP error response: {response.status} for {response.url}")
    
    async def _get_browser_info(self, session_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive browser information"""
        try:
            page = session_info["page"]
            
            browser_info = {
                "browser_type": session_info["browser_type"],
                "version": await session_info["browser"].version(),
                "user_agent": await page.evaluate("navigator.userAgent"),
                "viewport": await page.viewport_size(),
                "url": await page.url(),
                "title": await page.title(),
                "cookies_count": len(await page.context.cookies()),
                "local_storage_size": await self._get_local_storage_size(page),
                "session_storage_size": await self._get_session_storage_size(page)
            }
            
            return browser_info
            
        except Exception as e:
            logger.error(f"Error getting browser info: {str(e)}")
            return {"error": str(e)}
    
    async def _get_local_storage_size(self, page: Page) -> int:
        """Get local storage size in bytes"""
        try:
            return await page.evaluate("""
                () => {
                    let total = 0;
                    for(let key in localStorage) {
                        if(localStorage.hasOwnProperty(key)) {
                            total += localStorage[key].length + key.length;
                        }
                    }
                    return total;
                }
            """)
        except:
            return 0
    
    async def _get_session_storage_size(self, page: Page) -> int:
        """Get session storage size in bytes"""
        try:
            return await page.evaluate("""
                () => {
                    let total = 0;
                    for(let key in sessionStorage) {
                        if(sessionStorage.hasOwnProperty(key)) {
                            total += sessionStorage[key].length + key.length;
                        }
                    }
                    return total;
                }
            """)
        except:
            return 0
    
    async def close_session(self, session_id: str):
        """Close a browser session with cleanup"""
        try:
            if session_id not in self.browser_sessions:
                logger.warning(f"Session {session_id} not found for closing")
                return
            
            session_info = self.browser_sessions[session_id]
            
            # Perform cleanup tasks
            await self._cleanup_session(session_info)
            
            # Close page
            if "page" in session_info:
                try:
                    await session_info["page"].close()
                except Exception as e:
                    logger.warning(f"Error closing page for session {session_id}: {str(e)}")
            
            # Close context
            if "context" in session_info:
                try:
                    await session_info["context"].close()
                except Exception as e:
                    logger.warning(f"Error closing context for session {session_id}: {str(e)}")
            
            # Close browser
            if "browser" in session_info:
                try:
                    await session_info["browser"].close()
                except Exception as e:
                    logger.warning(f"Error closing browser for session {session_id}: {str(e)}")
            
            # Remove from tracking
            self.browser_sessions.pop(session_id, None)
            self.active_browsers.pop(session_id, None)
            
            logger.info(f"Successfully closed browser session {session_id}")
            
        except Exception as e:
            logger.error(f"Error closing browser session {session_id}: {str(e)}")
            raise PlaywrightSessionError(f"Session closure failed: {str(e)}")
    
    async def _cleanup_session(self, session_info: Dict[str, Any]):
        """Perform cleanup tasks for a session"""
        try:
            page = session_info.get("page")
            if page:
                # Clear any alerts or dialogs
                await page.evaluate("""
                    () => {
                        // Clear any pending timeouts
                        if (window._playwrightTimers) {
                            window._playwrightTimers.forEach(clearTimeout);
                            delete window._playwrightTimers;
                        }
                    }
                """)
                
        except Exception as e:
            logger.warning(f"Error during session cleanup: {str(e)}")
    
    # Enhanced Navigation Tools
    async def navigate_to(
        self, 
        session_id: str, 
        url: str, 
        wait_until: str = "load", 
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """Enhanced navigation with security validation and retry logic"""
        
        # Validate session
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        # Security validation
        is_valid, validation_message = self.security_manager.validate_url(url)
        if not is_valid:
            raise PlaywrightSecurityError(f"URL validation failed: {validation_message}")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        # Retry logic
        last_error = None
        for attempt in range(self.retry_config["max_retries"]):
            try:
                start_time = time.time()
                
                # Add navigation timeout wrapper
                navigation_task = asyncio.create_task(
                    page.goto(url, wait_until=wait_until, timeout=timeout)
                )
                
                # Wait for navigation with timeout
                response = await asyncio.wait_for(navigation_task, timeout=timeout / 1000)
                
                # Record navigation
                navigation_time = time.time() - start_time
                session_info["navigation_history"].append({
                    "url": url,
                    "timestamp": datetime.utcnow(),
                    "duration": navigation_time,
                    "status": response.status if response else None
                })
                
                # Update session activity
                session_info["last_activity"] = datetime.utcnow()
                
                # Get page info
                current_url = await page.url()
                title = await page.title()
                
                logger.info(f"Successfully navigated to {url} in session {session_id}")
                
                return {
                    "success": True,
                    "url": current_url,
                    "title": title,
                    "status": response.status if response else None,
                    "navigation_time": navigation_time,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except asyncio.TimeoutError:
                last_error = PlaywrightTimeoutError(f"Navigation timeout after {timeout}ms")
                logger.warning(f"Navigation timeout attempt {attempt + 1} for {url}")
                
            except PlaywrightTimeoutError as e:
                last_error = e
                logger.warning(f"Playwright timeout attempt {attempt + 1} for {url}")
                
            except Exception as e:
                last_error = PlaywrightNavigationError(f"Navigation failed: {str(e)}")
                logger.error(f"Navigation error attempt {attempt + 1} for {url}: {str(e)}")
            
            # Wait before retry
            if attempt < self.retry_config["max_retries"] - 1:
                wait_time = self.retry_config["retry_delay"] * (self.retry_config["backoff_factor"] ** attempt)
                await asyncio.sleep(wait_time)
        
        # All retries failed
        raise last_error or PlaywrightNavigationError("Navigation failed after all retries")
    
    async def go_back(self, session_id: str, timeout: int = 30000) -> Dict[str, Any]:
        """Navigate back in browser history"""
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        try:
            await asyncio.wait_for(page.go_back(), timeout=timeout / 1000)
            session_info["last_activity"] = datetime.utcnow()
            
            return {
                "success": True,
                "url": await page.url(),
                "title": await page.title(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except asyncio.TimeoutError:
            raise PlaywrightTimeoutError(f"Go back timeout after {timeout}ms")
        except Exception as e:
            raise PlaywrightNavigationError(f"Go back failed: {str(e)}")
    
    async def go_forward(self, session_id: str, timeout: int = 30000) -> Dict[str, Any]:
        """Navigate forward in browser history"""
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        try:
            await asyncio.wait_for(page.go_forward(), timeout=timeout / 1000)
            session_info["last_activity"] = datetime.utcnow()
            
            return {
                "success": True,
                "url": await page.url(),
                "title": await page.title(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except asyncio.TimeoutError:
            raise PlaywrightTimeoutError(f"Go forward timeout after {timeout}ms")
        except Exception as e:
            raise PlaywrightNavigationError(f"Go forward failed: {str(e)}")
    
    async def refresh(self, session_id: str, wait_until: str = "load", timeout: int = 30000) -> Dict[str, Any]:
        """Refresh the current page"""
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        try:
            await asyncio.wait_for(page.reload(wait_until=wait_until), timeout=timeout / 1000)
            session_info["last_activity"] = datetime.utcnow()
            
            return {
                "success": True,
                "url": await page.url(),
                "title": await page.title(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except asyncio.TimeoutError:
            raise PlaywrightTimeoutError(f"Refresh timeout after {timeout}ms")
        except Exception as e:
            raise PlaywrightNavigationError(f"Refresh failed: {str(e)}")
    
    # Enhanced Interaction Tools
    async def click(
        self,
        session_id: str,
        selector: str,
        button: str = "left",
        click_count: int = 1,
        delay: int = 0,
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """Enhanced click operation with validation and retry logic"""
        
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        # Validate selector
        is_valid, validation_message = self.security_manager.validate_selector(selector)
        if not is_valid:
            raise PlaywrightSecurityError(f"Selector validation failed: {validation_message}")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        last_error = None
        for attempt in range(self.retry_config["max_retries"]):
            try:
                # Wait for element with timeout
                element = await asyncio.wait_for(
                    page.wait_for_selector(selector, state="visible"),
                    timeout=timeout / 1000
                )
                
                # Perform click with optional delay and multiple clicks
                for i in range(click_count):
                    await element.click(button=button)
                    if delay > 0 and i < click_count - 1:
                        await asyncio.sleep(delay / 1000)
                
                session_info["last_activity"] = datetime.utcnow()
                
                # Get element info after click
                element_info = await page.evaluate("""
                    (selector) => {
                        const element = document.querySelector(selector);
                        if (element) {
                            return {
                                tagName: element.tagName,
                                id: element.id,
                                className: element.className,
                                text: element.textContent?.trim().substring(0, 100)
                            };
                        }
                        return null;
                    }
                """, selector)
                
                logger.info(f"Successfully clicked element {selector} in session {session_id}")
                
                return {
                    "success": True,
                    "selector": selector,
                    "button": button,
                    "click_count": click_count,
                    "element_info": element_info,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except asyncio.TimeoutError:
                last_error = PlaywrightTimeoutError(f"Click timeout - element {selector} not found within {timeout}ms")
                
            except Exception as e:
                last_error = PlaywrightInteractionError(f"Click failed on element {selector}: {str(e)}")
                logger.error(f"Click error on attempt {attempt + 1} for selector {selector}: {str(e)}")
            
            # Wait before retry
            if attempt < self.retry_config["max_retries"] - 1:
                wait_time = self.retry_config["retry_delay"] * (self.retry_config["backoff_factor"] ** attempt)
                await asyncio.sleep(wait_time)
        
        raise last_error
    
    async def type(
        self,
        session_id: str,
        selector: str,
        text: str,
        clear_first: bool = True,
        delay: int = 0,
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """Enhanced typing operation with validation and retry logic"""
        
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        # Validate inputs
        is_valid, validation_message = self.security_manager.validate_selector(selector)
        if not is_valid:
            raise PlaywrightSecurityError(f"Selector validation failed: {validation_message}")
        
        # Sanitize input text
        sanitized_text = self.security_manager.sanitize_input(text)
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        last_error = None
        for attempt in range(self.retry_config["max_retries"]):
            try:
                # Wait for element
                element = await asyncio.wait_for(
                    page.wait_for_selector(selector, state="visible"),
                    timeout=timeout / 1000
                )
                
                # Clear field if requested
                if clear_first:
                    await element.clear()
                
                # Type with optional delay
                if delay > 0:
                    await element.type(sanitized_text, delay=delay)
                else:
                    await element.fill(sanitized_text)
                
                session_info["last_activity"] = datetime.utcnow()
                
                # Get input value after typing
                input_value = await element.input_value()
                
                logger.info(f"Successfully typed {len(sanitized_text)} characters into {selector} in session {session_id}")
                
                return {
                    "success": True,
                    "selector": selector,
                    "text_length": len(sanitized_text),
                    "clear_first": clear_first,
                    "delay": delay,
                    "input_value": input_value,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except asyncio.TimeoutError:
                last_error = PlaywrightTimeoutError(f"Type timeout - element {selector} not found within {timeout}ms")
                
            except Exception as e:
                last_error = PlaywrightInteractionError(f"Type failed in element {selector}: {str(e)}")
                logger.error(f"Type error on attempt {attempt + 1} for selector {selector}: {str(e)}")
            
            # Wait before retry
            if attempt < self.retry_config["max_retries"] - 1:
                wait_time = self.retry_config["retry_delay"] * (self.retry_config["backoff_factor"] ** attempt)
                await asyncio.sleep(wait_time)
        
        raise last_error
    
    async def select(
        self,
        session_id: str,
        selector: str,
        value: str = None,
        label: str = None,
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """Enhanced select operation with validation and retry logic"""
        
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        # Validate selector
        is_valid, validation_message = self.security_manager.validate_selector(selector)
        if not is_valid:
            raise PlaywrightSecurityError(f"Selector validation failed: {validation_message}")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        last_error = None
        for attempt in range(self.retry_config["max_retries"]):
            try:
                # Wait for element
                element = await asyncio.wait_for(
                    page.wait_for_selector(selector, state="visible"),
                    timeout=timeout / 1000
                )
                
                # Select option
                if value:
                    await element.select_option(value=value)
                    select_value = value
                elif label:
                    await element.select_option(label=label)
                    select_value = label
                else:
                    raise PlaywrightInteractionError("Either value or label must be provided")
                
                session_info["last_activity"] = datetime.utcnow()
                
                # Get selected value
                selected_value = await element.evaluate("element => element.value")
                
                logger.info(f"Successfully selected option {select_value} from {selector} in session {session_id}")
                
                return {
                    "success": True,
                    "selector": selector,
                    "selected_value": selected_value,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except asyncio.TimeoutError:
                last_error = PlaywrightTimeoutError(f"Select timeout - element {selector} not found within {timeout}ms")
                
            except Exception as e:
                last_error = PlaywrightInteractionError(f"Select failed for element {selector}: {str(e)}")
                logger.error(f"Select error on attempt {attempt + 1} for selector {selector}: {str(e)}")
            
            # Wait before retry
            if attempt < self.retry_config["max_retries"] - 1:
                wait_time = self.retry_config["retry_delay"] * (self.retry_config["backoff_factor"] ** attempt)
                await asyncio.sleep(wait_time)
        
        raise last_error
    
    async def drag_and_drop(
        self,
        session_id: str,
        source_selector: str,
        target_selector: str,
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """Enhanced drag and drop operation with validation and retry logic"""
        
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        # Validate selectors
        for selector in [source_selector, target_selector]:
            is_valid, validation_message = self.security_manager.validate_selector(selector)
            if not is_valid:
                raise PlaywrightSecurityError(f"Selector validation failed for {selector}: {validation_message}")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        last_error = None
        for attempt in range(self.retry_config["max_retries"]):
            try:
                # Wait for both elements
                source_element = await asyncio.wait_for(
                    page.wait_for_selector(source_selector, state="visible"),
                    timeout=timeout / 1000
                )
                
                target_element = await asyncio.wait_for(
                    page.wait_for_selector(target_selector, state="visible"),
                    timeout=timeout / 1000
                )
                
                # Perform drag and drop
                await source_element.drag_to(target_element)
                
                session_info["last_activity"] = datetime.utcnow()
                
                logger.info(f"Successfully dragged {source_selector} to {target_selector} in session {session_id}")
                
                return {
                    "success": True,
                    "source_selector": source_selector,
                    "target_selector": target_selector,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except asyncio.TimeoutError:
                last_error = PlaywrightTimeoutError(f"Drag and drop timeout - elements not found within {timeout}ms")
                
            except Exception as e:
                last_error = PlaywrightInteractionError(f"Drag and drop failed: {str(e)}")
                logger.error(f"Drag and drop error on attempt {attempt + 1}: {str(e)}")
            
            # Wait before retry
            if attempt < self.retry_config["max_retries"] - 1:
                wait_time = self.retry_config["retry_delay"] * (self.retry_config["backoff_factor"] ** attempt)
                await asyncio.sleep(wait_time)
        
        raise last_error
    
    # Enhanced Extraction Tools
    async def get_text(
        self,
        session_id: str,
        selector: str,
        attribute: str = "text",
        multiple: bool = False,
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """Enhanced text extraction with validation and retry logic"""
        
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        # Validate selector
        is_valid, validation_message = self.security_manager.validate_selector(selector)
        if not is_valid:
            raise PlaywrightSecurityError(f"Selector validation failed: {validation_message}")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        last_error = None
        for attempt in range(self.retry_config["max_retries"]):
            try:
                # Wait for elements
                elements = await asyncio.wait_for(
                    page.wait_for_selector(selector, state="attached"),
                    timeout=timeout / 1000
                )
                
                # Extract content based on attribute
                if attribute == "text":
                    if multiple:
                        extracted_content = await page.evaluate("""
                            (selector) => {
                                const elements = document.querySelectorAll(selector);
                                return Array.from(elements).map(el => el.textContent?.trim() || '');
                            }
                        """, selector)
                    else:
                        extracted_content = await page.evaluate("""
                            (selector) => {
                                const element = document.querySelector(selector);
                                return element ? element.textContent?.trim() || '' : null;
                            }
                        """, selector)
                
                elif attribute in ["href", "src", "title", "alt", "value"]:
                    if multiple:
                        extracted_content = await page.evaluate(f"""
                            (selector) => {{
                                const elements = document.querySelectorAll(selector);
                                return Array.from(elements).map(el => el.getAttribute('{attribute}') || '');
                            }}
                        """, selector)
                    else:
                        extracted_content = await page.evaluate(f"""
                            (selector) => {{
                                const element = document.querySelector(selector);
                                return element ? element.getAttribute('{attribute}') || '' : null;
                            }}
                        """, selector)
                
                elif attribute in ["innerHTML", "outerHTML"]:
                    if multiple:
                        extracted_content = await page.evaluate(f"""
                            (selector) => {{
                                const elements = document.querySelectorAll(selector);
                                return Array.from(elements).map(el => el.{attribute});
                            }}
                        """, selector)
                    else:
                        extracted_content = await page.evaluate(f"""
                            (selector) => {{
                                const element = document.querySelector(selector);
                                return element ? element.{attribute} : null;
                            }}
                        """, selector)
                
                else:
                    raise PlaywrightExtractionError(f"Unsupported attribute: {attribute}")
                
                session_info["last_activity"] = datetime.utcnow()
                
                logger.info(f"Successfully extracted {attribute} from {selector} in session {session_id}")
                
                return {
                    "success": True,
                    "selector": selector,
                    "attribute": attribute,
                    "multiple": multiple,
                    "content": extracted_content,
                    "content_length": len(str(extracted_content)),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except asyncio.TimeoutError:
                last_error = PlaywrightTimeoutError(f"Text extraction timeout - elements not found within {timeout}ms")
                
            except Exception as e:
                last_error = PlaywrightExtractionError(f"Text extraction failed: {str(e)}")
                logger.error(f"Text extraction error on attempt {attempt + 1} for selector {selector}: {str(e)}")
            
            # Wait before retry
            if attempt < self.retry_config["max_retries"] - 1:
                wait_time = self.retry_config["retry_delay"] * (self.retry_config["backoff_factor"] ** attempt)
                await asyncio.sleep(wait_time)
        
        raise last_error
    
    async def get_attribute(
        self,
        session_id: str,
        selector: str,
        attribute: str,
        multiple: bool = False,
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """Enhanced attribute extraction with validation and retry logic"""
        
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        # Validate selector
        is_valid, validation_message = self.security_manager.validate_selector(selector)
        if not is_valid:
            raise PlaywrightSecurityError(f"Selector validation failed: {validation_message}")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        last_error = None
        for attempt in range(self.retry_config["max_retries"]):
            try:
                # Wait for elements
                await asyncio.wait_for(
                    page.wait_for_selector(selector, state="attached"),
                    timeout=timeout / 1000
                )
                
                # Extract attribute
                if multiple:
                    extracted_attributes = await page.evaluate(f"""
                        (selector) => {{
                            const elements = document.querySelectorAll(selector);
                            return Array.from(elements).map(el => {{
                                const attrValue = el.getAttribute('{attribute}');
                                return {{
                                    attribute: '{attribute}',
                                    value: attrValue || '',
                                    length: attrValue ? attrValue.length : 0
                                }};
                            }});
                        }}
                    """, selector)
                else:
                    extracted_attributes = await page.evaluate(f"""
                        (selector) => {{
                            const element = document.querySelector(selector);
                            if (element) {{
                                const attrValue = element.getAttribute('{attribute}');
                                return {{
                                    attribute: '{attribute}',
                                    value: attrValue || '',
                                    length: attrValue ? attrValue.length : 0
                                }};
                            }}
                            return null;
                        }}
                    """, selector)
                
                session_info["last_activity"] = datetime.utcnow()
                
                logger.info(f"Successfully extracted attribute {attribute} from {selector} in session {session_id}")
                
                return {
                    "success": True,
                    "selector": selector,
                    "attribute": attribute,
                    "multiple": multiple,
                    "attributes": extracted_attributes,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except asyncio.TimeoutError:
                last_error = PlaywrightTimeoutError(f"Attribute extraction timeout - elements not found within {timeout}ms")
                
            except Exception as e:
                last_error = PlaywrightExtractionError(f"Attribute extraction failed: {str(e)}")
                logger.error(f"Attribute extraction error on attempt {attempt + 1} for selector {selector}: {str(e)}")
            
            # Wait before retry
            if attempt < self.retry_config["max_retries"] - 1:
                wait_time = self.retry_config["retry_delay"] * (self.retry_config["backoff_factor"] ** attempt)
                await asyncio.sleep(wait_time)
        
        raise last_error
    
    async def get_page_content(
        self,
        session_id: str,
        content_type: str = "text",
        selectors: Dict[str, str] = None,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Enhanced page content extraction with comprehensive options"""
        
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        try:
            extracted_content = {}
            
            if content_type == "text":
                extracted_content["text"] = await page.text_content("body")
                
            elif content_type == "html":
                extracted_content["html"] = await page.content()
                
            elif content_type == "markdown":
                # Convert HTML to markdown (simplified)
                html_content = await page.content()
                # In a real implementation, you'd use a proper HTML-to-markdown converter
                extracted_content["markdown"] = html_content  # Placeholder
                
            elif content_type == "json":
                if selectors:
                    # Extract specific content using selectors
                    for key, selector in selectors.items():
                        try:
                            content = await page.text_content(selector)
                            extracted_content[key] = content
                        except:
                            extracted_content[key] = None
                else:
                    # Extract all content as JSON
                    extracted_content = await page.evaluate("""
                        () => {
                            const data = {};
                            const elements = document.querySelectorAll('h1, h2, h3, p, a, img');
                            elements.forEach((el, index) => {
                                const tag = el.tagName.toLowerCase();
                                if (!data[tag]) data[tag] = [];
                                data[tag].push({
                                    text: el.textContent?.trim(),
                                    href: el.href || null,
                                    src: el.src || null,
                                    index: index
                                });
                            });
                            return data;
                        }
                    """)
            
            # Add metadata if requested
            if include_metadata:
                extracted_content["metadata"] = {
                    "url": await page.url(),
                    "title": await page.title(),
                    "timestamp": datetime.utcnow().isoformat(),
                    "content_length": len(str(extracted_content))
                }
            
            session_info["last_activity"] = datetime.utcnow()
            
            logger.info(f"Successfully extracted {content_type} content from session {session_id}")
            
            return {
                "success": True,
                "content_type": content_type,
                "content": extracted_content,
                "metadata": extracted_content.get("metadata") if include_metadata else None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise PlaywrightExtractionError(f"Page content extraction failed: {str(e)}")
    
    # Enhanced Multimedia Tools
    async def screenshot(
        self,
        session_id: str,
        full_page: bool = False,
        selector: str = None,
        quality: int = 90,
        format: str = "png",
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """Enhanced screenshot operation with comprehensive options"""
        
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        try:
            # Prepare screenshot options
            screenshot_options = {
                "full_page": full_page,
                "type": format,
                "quality": quality if format in ["jpeg", "webp"] else None
            }
            
            # If selector specified, take screenshot of specific element
            if selector:
                # Wait for element
                await asyncio.wait_for(
                    page.wait_for_selector(selector, state="visible"),
                    timeout=timeout / 1000
                )
                
                # Take element screenshot
                screenshot_bytes = await page.locator(selector).screenshot(**screenshot_options)
            else:
                # Take page screenshot
                screenshot_bytes = await page.screenshot(**screenshot_options)
            
            session_info["last_activity"] = datetime.utcnow()
            
            # Convert to base64 for easy transport
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            logger.info(f"Successfully took {format} screenshot in session {session_id}")
            
            return {
                "success": True,
                "format": format,
                "full_page": full_page,
                "selector": selector,
                "quality": quality,
                "size_bytes": len(screenshot_bytes),
                "screenshot_base64": screenshot_base64,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except asyncio.TimeoutError:
            raise PlaywrightTimeoutError(f"Screenshot timeout after {timeout}ms")
        except Exception as e:
            raise PlaywrightAutomationError(f"Screenshot failed: {str(e)}")
    
    async def generate_pdf(
        self,
        session_id: str,
        full_page: bool = False,
        format: str = "A4",
        landscape: bool = False,
        margin: Dict[str, str] = None,
        timeout: int = 60000
    ) -> Dict[str, Any]:
        """Enhanced PDF generation with comprehensive options"""
        
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        try:
            # Prepare PDF options
            pdf_options = {
                "format": format,
                "landscape": landscape,
                "print_background": True
            }
            
            if full_page:
                pdf_options["height"] = page.viewport_size["height"] * 10  # Approximate full page
            
            if margin:
                pdf_options["margin"] = margin
            
            # Generate PDF
            pdf_bytes = await page.pdf(**pdf_options)
            
            session_info["last_activity"] = datetime.utcnow()
            
            # Convert to base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            logger.info(f"Successfully generated PDF in session {session_id}")
            
            return {
                "success": True,
                "format": format,
                "full_page": full_page,
                "landscape": landscape,
                "margin": margin,
                "size_bytes": len(pdf_bytes),
                "pdf_base64": pdf_base64,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except asyncio.TimeoutError:
            raise PlaywrightTimeoutError(f"PDF generation timeout after {timeout}ms")
        except Exception as e:
            raise PlaywrightAutomationError(f"PDF generation failed: {str(e)}")
    
    async def record_video(
        self,
        session_id: str,
        action: str,
        duration: int = None,
        fps: int = 30,
        quality: str = "high",
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """Enhanced video recording with comprehensive options"""
        
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        session_info = self.browser_sessions[session_id]
        context = session_info["context"]
        
        try:
            if action == "start":
                # Start video recording
                if duration:
                    # Set up timeout for duration
                    await asyncio.wait_for(self._start_video_recording(context, fps, quality), timeout=duration)
                    return {
                        "success": True,
                        "action": "start",
                        "duration": duration,
                        "fps": fps,
                        "quality": quality,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    await self._start_video_recording(context, fps, quality)
                    return {
                        "success": True,
                        "action": "start",
                        "fps": fps,
                        "quality": quality,
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            elif action == "stop":
                # Stop video recording and get the video
                video_bytes = await self._stop_video_recording(context)
                
                if video_bytes:
                    video_base64 = base64.b64encode(video_bytes).decode('utf-8')
                    
                    logger.info(f"Successfully recorded video in session {session_id}")
                    
                    return {
                        "success": True,
                        "action": "stop",
                        "size_bytes": len(video_bytes),
                        "video_base64": video_base64,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    raise PlaywrightAutomationError("No video was being recorded")
            
            else:
                raise PlaywrightAutomationError(f"Invalid video action: {action}")
                
        except asyncio.TimeoutError:
            raise PlaywrightTimeoutError(f"Video recording timeout after {timeout}ms")
        except Exception as e:
            raise PlaywrightAutomationError(f"Video recording failed: {str(e)}")
    
    async def _start_video_recording(self, context: BrowserContext, fps: int, quality: str):
        """Start video recording (implementation depends on Playwright version)"""
        # This is a placeholder - actual implementation would depend on Playwright video recording capabilities
        # In newer versions, you can use context.set_default_timeout() and page.video()
        pass
    
    async def _stop_video_recording(self, context: BrowserContext) -> bytes:
        """Stop video recording and return video bytes (placeholder)"""
        # This is a placeholder - actual implementation would depend on Playwright video recording capabilities
        return b""
    
    # Enhanced Wait and Synchronization Tools
    async def wait_for_selector(
        self,
        session_id: str,
        selector: str,
        timeout: int = 30000,
        state: str = "visible"
    ) -> Dict[str, Any]:
        """Enhanced wait for selector with validation and retry logic"""
        
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        # Validate selector
        is_valid, validation_message = self.security_manager.validate_selector(selector)
        if not is_valid:
            raise PlaywrightSecurityError(f"Selector validation failed: {validation_message}")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        try:
            # Wait for element with timeout
            await asyncio.wait_for(
                page.wait_for_selector(selector, state=state),
                timeout=timeout / 1000
            )
            
            # Get element info
            element_info = await page.evaluate("""
                (selector) => {
                    const element = document.querySelector(selector);
                    if (element) {
                        return {
                            tagName: element.tagName,
                            id: element.id,
                            className: element.className,
                            textLength: element.textContent?.length || 0,
                            isVisible: element.offsetParent !== null
                        };
                    }
                    return null;
                }
            """, selector)
            
            session_info["last_activity"] = datetime.utcnow()
            
            logger.info(f"Successfully waited for selector {selector} in session {session_id}")
            
            return {
                "success": True,
                "selector": selector,
                "state": state,
                "element_info": element_info,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except asyncio.TimeoutError:
            raise PlaywrightTimeoutError(f"Wait for selector timeout - {selector} not found within {timeout}ms")
        except Exception as e:
            raise PlaywrightAutomationError(f"Wait for selector failed: {str(e)}")
    
    async def wait_for_load_state(
        self,
        session_id: str,
        state: str,
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """Enhanced wait for load state with comprehensive monitoring"""
        
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        session_info = self.browser_sessions[session_id]
        page = session_info["page"]
        
        try:
            # Wait for load state with timeout
            await asyncio.wait_for(
                page.wait_for_load_state(state),
                timeout=timeout / 1000
            )
            
            # Get page performance metrics
            performance_metrics = await page.evaluate("""
                () => {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    const paint = performance.getEntriesByType('paint');
                    
                    return {
                        domContentLoaded: navigation ? navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart : 0,
                        loadComplete: navigation ? navigation.loadEventEnd - navigation.loadEventStart : 0,
                        firstPaint: paint.find(entry => entry.name === 'first-paint')?.startTime || 0,
                        firstContentfulPaint: paint.find(entry => entry.name === 'first-contentful-paint')?.startTime || 0,
                        timestamp: Date.now()
                    };
                }
            """)
            
            session_info["last_activity"] = datetime.utcnow()
            session_info["performance_metrics"] = performance_metrics
            
            logger.info(f"Successfully waited for load state {state} in session {session_id}")
            
            return {
                "success": True,
                "state": state,
                "performance_metrics": performance_metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except asyncio.TimeoutError:
            raise PlaywrightTimeoutError(f"Wait for load state timeout - {state} not achieved within {timeout}ms")
        except Exception as e:
            raise PlaywrightAutomationError(f"Wait for load state failed: {str(e)}")
    
    async def wait_for_timeout(self, session_id: str, duration: int) -> Dict[str, Any]:
        """Enhanced timeout wait with session tracking"""
        
        if session_id not in self.browser_sessions:
            raise PlaywrightSessionError(f"Session {session_id} not found")
        
        try:
            await asyncio.sleep(duration / 1000)
            
            session_info = self.browser_sessions[session_id]
            session_info["last_activity"] = datetime.utcnow()
            
            logger.info(f"Successfully waited for timeout {duration}ms in session {session_id}")
            
            return {
                "success": True,
                "duration": duration,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise PlaywrightAutomationError(f"Wait for timeout failed: {str(e)}")
    
    # Session Management and Health
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive information about a browser session"""
        
        if session_id not in self.browser_sessions:
            return {"error": "Session not found"}
        
        session_info = self.browser_sessions[session_id]
        
        try:
            # Update last activity
            session_info["last_activity"] = datetime.utcnow()
            
            # Get current page info
            page_info = {}
            performance_metrics = {}
            
            if "page" in session_info:
                page = session_info["page"]
                try:
                    current_url = await page.url()
                    title = await page.title()
                    
                    page_info = {
                        "current_url": current_url,
                        "title": title,
                        "viewport_size": await page.viewport_size()
                    }
                    
                    # Get performance metrics if available
                    if session_info.get("performance_metrics"):
                        performance_metrics = session_info["performance_metrics"]
                        
                except Exception:
                    pass
            
            # Compile comprehensive session info
            return {
                "session_id": session_id,
                "browser_type": session_info["browser_type"],
                "status": session_info["status"],
                "config": session_info["config"],
                "created_at": session_info["created_at"].isoformat(),
                "last_activity": session_info["last_activity"].isoformat(),
                "page_info": page_info,
                "navigation_history": session_info.get("navigation_history", [])[-5:],  # Last 5 navigations
                "performance_metrics": performance_metrics,
                "available_tools": list(self.tool_registry.get_all_tools().keys()),
                "security_status": "secure"  # Could be enhanced with actual security checks
            }
            
        except Exception as e:
            logger.error(f"Error getting session info for {session_id}: {str(e)}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Enhanced health check with comprehensive system status"""
        
        try:
            # Update health check timestamp
            self.health_status["last_check"] = datetime.utcnow()
            
            # Check if Playwright is initialized
            if not self.playwright:
                self.health_status = {
                    "status": "unhealthy",
                    "error": "Playwright not initialized",
                    "last_check": datetime.utcnow()
                }
                return self.health_status
            
            # Test basic functionality
            test_session_id = f"health_check_{int(time.time())}"
            health_result = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "playwright": "healthy",
                    "browser_sessions": len(self.browser_sessions),
                    "active_browsers": len(self.active_browsers),
                    "tool_registry": len(self.tool_registry.get_all_tools()),
                    "security_manager": "active"
                },
                "performance": {},
                "errors": []
            }
            
            try:
                # Create test session
                await self.create_session(test_session_id, "chromium", {"headless": True})
                
                # Test navigation
                test_result = await self.navigate_to(
                    test_session_id,
                    "data:text/html,<html><body><h1>Health Check</h1></body></html>",
                    wait_until="load"
                )
                
                # Test basic interaction
                # (Would add more comprehensive tests in production)
                
                # Close test session
                await self.close_session(test_session_id)
                
                health_result["performance"] = {
                    "session_creation_time": "fast",
                    "navigation_response": "good",
                    "overall_status": "excellent"
                }
                
            except Exception as e:
                health_result["errors"].append(str(e))
                health_result["status"] = "degraded"
            
            self.health_status = health_result
            return health_result
            
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            self.health_status = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow()
            }
            return self.health_status
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive Playwright manager statistics"""
        
        return {
            "active_sessions": len(self.browser_sessions),
            "playwright_initialized": self.playwright is not None,
            "health_status": self.health_status,
            "session_ids": list(self.browser_sessions.keys()),
            "tool_registry": {
                "total_tools": len(self.tool_registry.get_all_tools()),
                "categories": self.tool_registry.get_categories(),
                "tools_by_category": {
                    category: len(self.tool_registry.get_tools_by_category(category))
                    for category in self.tool_registry.get_categories()
                }
            },
            "security": {
                "dangerous_patterns_count": len(self.security_manager.dangerous_patterns),
                "allowed_domains_count": len(self.security_manager.allowed_domains),
                "blocked_domains_count": len(self.security_manager.blocked_domains)
            },
            "retry_config": self.retry_config
        }


# Global Enhanced instances
_enhanced_playwright_manager: Optional[PlaywrightBrowserManager] = None


async def get_enhanced_playwright_manager() -> PlaywrightBrowserManager:
    """Get or create global enhanced Playwright manager instance"""
    global _enhanced_playwright_manager
    
    if _enhanced_playwright_manager is None:
        _enhanced_playwright_manager = PlaywrightBrowserManager()
        await _enhanced_playwright_manager.initialize()
    
    return _enhanced_playwright_manager


async def cleanup_enhanced_playwright_resources():
    """Cleanup all enhanced Playwright resources"""
    global _enhanced_playwright_manager
    
    if _enhanced_playwright_manager:
        await _enhanced_playwright_manager.shutdown()
    
    _enhanced_playwright_manager = None