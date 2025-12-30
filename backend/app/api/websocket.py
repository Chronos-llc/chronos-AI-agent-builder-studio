from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List, Any
import json
import uuid
from datetime import datetime
import logging

from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.models.agent import Agent
from backend.app.schemas.debugging import (
    DebugEvent, LogEntry, ExecutionTrace, BreakpointHit, 
    WatchExpressionResult, DebugCommand, DebugResponse
)


router = APIRouter()

logger = logging.getLogger(__name__)


# WebSocket connection manager
class DebugWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, List[str]] = {}
        self.user_connections: Dict[int, List[str]] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str, user_id: int):
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        
        self.active_connections[connection_id] = websocket
        
        if session_id not in self.session_connections:
            self.session_connections[session_id] = []
        self.session_connections[session_id].append(connection_id)
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)
        
        return connection_id
        
    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            del self.active_connections[connection_id]
            
            # Clean up session and user connections
            for session_id, connections in self.session_connections.items():
                if connection_id in connections:
                    connections.remove(connection_id)
                    if not connections:
                        del self.session_connections[session_id]
                    break
            
            for user_id, connections in self.user_connections.items():
                if connection_id in connections:
                    connections.remove(connection_id)
                    if not connections:
                        del self.user_connections[user_id]
                    break
        
    async def send_message(self, message: Dict[str, Any], connection_id: str):
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                self.disconnect(connection_id)
                
    async def broadcast_to_session(self, message: Dict[str, Any], session_id: str):
        if session_id in self.session_connections:
            for connection_id in self.session_connections[session_id]:
                await self.send_message(message, connection_id)
                
    async def broadcast_to_user(self, message: Dict[str, Any], user_id: int):
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id]:
                await self.send_message(message, connection_id)


websocket_manager = DebugWebSocketManager()


@router.websocket("/ws/debug/{session_id}")
async def debug_websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    user: User = Depends(get_current_user)
):
    """WebSocket endpoint for real-time debugging"""
    
    # Verify session exists and belongs to user
    # In a real implementation, you would check the session database
    # For now, we'll just verify the user is authenticated
    
    connection_id = await websocket_manager.connect(websocket, session_id, user.id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"Received debug message: {message}")
            
            # Handle different message types
            if message.get("type") == "command":
                command = DebugCommand(**message.get("data", {}))
                
                # Execute command and send response
                response = DebugResponse(
                    success=True,
                    message=f"Command '{command.command}' executed",
                    data={"result": "success"}
                )
                
                await websocket_manager.send_message({
                    "type": "command_response",
                    "data": response.dict()
                }, connection_id)
                
            elif message.get("type") == "log":
                log_entry = LogEntry(**message.get("data", {}))
                
                # Store log entry and broadcast to session
                await websocket_manager.broadcast_to_session({
                    "type": "log_entry",
                    "data": log_entry.dict()
                }, session_id)
                
            elif message.get("type") == "breakpoint_hit":
                breakpoint_hit = BreakpointHit(**message.get("data", {}))
                
                # Broadcast breakpoint hit to session
                await websocket_manager.broadcast_to_session({
                    "type": "breakpoint_hit",
                    "data": breakpoint_hit.dict()
                }, session_id)
                
            elif message.get("type") == "watch_result":
                watch_result = WatchExpressionResult(**message.get("data", {}))
                
                # Broadcast watch result to session
                await websocket_manager.broadcast_to_session({
                    "type": "watch_result",
                    "data": watch_result.dict()
                }, session_id)
                
            elif message.get("type") == "execution_trace":
                trace = ExecutionTrace(**message.get("data", {}))
                
                # Broadcast execution trace to session
                await websocket_manager.broadcast_to_session({
                    "type": "execution_trace",
                    "data": trace.dict()
                }, session_id)
                
    except WebSocketDisconnect:
        logger.info(f"Debug WebSocket disconnected: {connection_id}")
        websocket_manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"Debug WebSocket error: {e}")
        websocket_manager.disconnect(connection_id)


@router.websocket("/ws/logs/{agent_id}")
async def logs_websocket_endpoint(
    websocket: WebSocket,
    agent_id: int,
    user: User = Depends(get_current_user)
):
    """WebSocket endpoint for real-time log streaming"""
    
    # Verify agent exists and belongs to user
    # In a real implementation, you would check the agent database
    
    connection_id = await websocket_manager.connect(websocket, f"logs_{agent_id}", user.id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"Received log message: {message}")
            
            # Handle log subscription
            if message.get("type") == "subscribe":
                # In a real implementation, you would start streaming logs
                # For now, just acknowledge the subscription
                await websocket_manager.send_message({
                    "type": "subscription_ack",
                    "data": {"status": "subscribed", "agent_id": agent_id}
                }, connection_id)
                
            elif message.get("type") == "unsubscribe":
                # In a real implementation, you would stop streaming logs
                await websocket_manager.send_message({
                    "type": "subscription_ack",
                    "data": {"status": "unsubscribed", "agent_id": agent_id}
                }, connection_id)
                break
                
    except WebSocketDisconnect:
        logger.info(f"Logs WebSocket disconnected: {connection_id}")
        websocket_manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"Logs WebSocket error: {e}")
        websocket_manager.disconnect(connection_id)


@router.websocket("/ws/performance/{session_id}")
async def performance_websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    user: User = Depends(get_current_user)
):
    """WebSocket endpoint for real-time performance monitoring"""
    
    connection_id = await websocket_manager.connect(websocket, session_id, user.id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"Received performance message: {message}")
            
            # Handle performance monitoring
            if message.get("type") == "monitor_start":
                # In a real implementation, you would start monitoring
                await websocket_manager.send_message({
                    "type": "monitor_status",
                    "data": {"status": "monitoring_started", "session_id": session_id}
                }, connection_id)
                
            elif message.get("type") == "monitor_stop":
                # In a real implementation, you would stop monitoring
                await websocket_manager.send_message({
                    "type": "monitor_status",
                    "data": {"status": "monitoring_stopped", "session_id": session_id}
                }, connection_id)
                break
                
    except WebSocketDisconnect:
        logger.info(f"Performance WebSocket disconnected: {connection_id}")
        websocket_manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"Performance WebSocket error: {e}")
        websocket_manager.disconnect(connection_id)


# Helper function to broadcast debug events
async def broadcast_debug_event(event: DebugEvent):
    """Broadcast a debug event to all connections in the session"""
    await websocket_manager.broadcast_to_session({
        "type": "debug_event",
        "data": event.dict()
    }, event.session_id)


# Helper function to broadcast log entries
async def broadcast_log_entry(log_entry: LogEntry):
    """Broadcast a log entry to all connections in the session"""
    await websocket_manager.broadcast_to_session({
        "type": "log_entry",
        "data": log_entry.dict()
    }, log_entry.session_id)