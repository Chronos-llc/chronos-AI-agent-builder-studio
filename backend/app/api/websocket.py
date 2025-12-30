from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
import json
import uuid
import time
from datetime import datetime
import logging

from app.core.security import verify_token
from app.models.user import User
from app.models.agent import AgentModel
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

router = APIRouter()
logger = logging.getLogger(__name__)


# WebSocket connection manager for collaboration
class CollaborationWebSocketManager:
    def __init__(self):
        # Map of connection_id to connection info
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        # Map of agent_id to list of connection_ids
        self.agent_connections: Dict[int, List[str]] = {}
        # Map of user_id to connection_ids
        self.user_connections: Dict[int, List[str]] = {}
        
    async def connect(self, websocket: WebSocket, agent_id: int, user_id: int, user_info: Dict[str, Any]) -> str:
        """Accept WebSocket connection and register it"""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        
        # Store connection info
        self.active_connections[connection_id] = {
            "websocket": websocket,
            "agent_id": agent_id,
            "user_id": user_id,
            "user_info": user_info,
            "connected_at": time.time()
        }
        
        # Register in agent connections
        if agent_id not in self.agent_connections:
            self.agent_connections[agent_id] = []
        self.agent_connections[agent_id].append(connection_id)
        
        # Register in user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)
        
        # Send connection confirmation with current users
        current_users = await self.get_agent_users(agent_id)
        await self.send_message({
            "type": "connection_established",
            "data": {
                "connection_id": connection_id,
                "current_users": current_users,
                "timestamp": datetime.utcnow().isoformat()
            }
        }, connection_id)
        
        # Notify other users in the agent about new user
        await self.broadcast_to_agent({
            "type": "user_joined",
            "data": {
                "user": user_info,
                "timestamp": datetime.utcnow().isoformat()
            }
        }, agent_id, exclude_connection=connection_id)
        
        return connection_id
        
    def disconnect(self, connection_id: str):
        """Handle WebSocket disconnection"""
        if connection_id not in self.active_connections:
            return
            
        connection_info = self.active_connections[connection_id]
        agent_id = connection_info["agent_id"]
        user_id = connection_info["user_id"]
        user_info = connection_info["user_info"]
        
        # Remove from active connections
        del self.active_connections[connection_id]
        
        # Remove from agent connections
        if agent_id in self.agent_connections:
            if connection_id in self.agent_connections[agent_id]:
                self.agent_connections[agent_id].remove(connection_id)
            if not self.agent_connections[agent_id]:
                del self.agent_connections[agent_id]
        
        # Remove from user connections
        if user_id in self.user_connections:
            if connection_id in self.user_connections[user_id]:
                self.user_connections[user_id].remove(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Notify other users about departure
        import asyncio
        asyncio.create_task(self.broadcast_to_agent({
            "type": "user_left",
            "data": {
                "user": user_info,
                "timestamp": datetime.utcnow().isoformat()
            }
        }, agent_id))
        
    async def send_message(self, message: Dict[str, Any], connection_id: str):
        """Send message to specific connection"""
        if connection_id not in self.active_connections:
            return
            
        try:
            websocket = self.active_connections[connection_id]["websocket"]
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            self.disconnect(connection_id)
            
    async def broadcast_to_agent(self, message: Dict[str, Any], agent_id: int, exclude_connection: Optional[str] = None):
        """Broadcast message to all users in an agent"""
        if agent_id not in self.agent_connections:
            return
            
        for connection_id in self.agent_connections[agent_id]:
            if connection_id != exclude_connection:
                await self.send_message(message, connection_id)
                
    async def broadcast_to_user(self, message: Dict[str, Any], user_id: int):
        """Broadcast message to all connections for a user"""
        if user_id not in self.user_connections:
            return
            
        for connection_id in self.user_connections[user_id]:
            await self.send_message(message, connection_id)
            
    async def get_agent_users(self, agent_id: int) -> List[Dict[str, Any]]:
        """Get list of currently connected users for an agent"""
        if agent_id not in self.agent_connections:
            return []
            
        users = []
        for connection_id in self.agent_connections[agent_id]:
            if connection_id in self.active_connections:
                conn_info = self.active_connections[connection_id]
                users.append({
                    "user_id": conn_info["user_id"],
                    "user_info": conn_info["user_info"],
                    "connected_at": conn_info["connected_at"]
                })
        return users


# Global WebSocket manager instance
websocket_manager = CollaborationWebSocketManager()


async def get_current_user_from_token(token: str, db: AsyncSession) -> User:
    """Get current user from WebSocket token"""
    try:
        payload = verify_token(token)
        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


@router.websocket("/ws/collaboration/{agent_id}")
async def collaboration_websocket_endpoint(
    websocket: WebSocket,
    agent_id: int,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time collaboration in Studio"""
    
    # Authenticate user
    try:
        user = await get_current_user_from_token(token, db)
    except HTTPException as e:
        await websocket.close(code=4001, reason=str(e.detail))
        return
    
    # Verify agent ownership or access
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        await websocket.close(code=4004, reason="Agent not found or access denied")
        return
    
    # Prepare user info for collaboration
    user_info = {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email
    }
    
    # Connect WebSocket
    connection_id = await websocket_manager.connect(websocket, agent_id, user.id, user_info)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"Received collaboration message: {message}")
            
            # Handle different collaboration message types
            message_type = message.get("type")
            message_data = message.get("data", {})
            
            if message_type == "cursor_position":
                # Broadcast cursor position to other users
                await websocket_manager.broadcast_to_agent({
                    "type": "cursor_position",
                    "data": {
                        "user_id": user.id,
                        "user_info": user_info,
                        "position": message_data.get("position"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, agent_id, exclude_connection=connection_id)
                
            elif message_type == "text_selection":
                # Broadcast text selection to other users
                await websocket_manager.broadcast_to_agent({
                    "type": "text_selection",
                    "data": {
                        "user_id": user.id,
                        "user_info": user_info,
                        "selection": message_data.get("selection"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, agent_id, exclude_connection=connection_id)
                
            elif message_type == "editor_change":
                # Broadcast editor changes to other users (for real-time collaboration)
                await websocket_manager.broadcast_to_agent({
                    "type": "editor_change",
                    "data": {
                        "user_id": user.id,
                        "user_info": user_info,
                        "changes": message_data.get("changes"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, agent_id, exclude_connection=connection_id)
                
            elif message_type == "knowledge_upload_progress":
                # Broadcast file upload progress
                await websocket_manager.broadcast_to_agent({
                    "type": "knowledge_upload_progress",
                    "data": {
                        "user_id": user.id,
                        "user_info": user_info,
                        "file_info": message_data.get("file_info"),
                        "progress": message_data.get("progress"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, agent_id, exclude_connection=connection_id)
                
            elif message_type == "agent_configuration_change":
                # Broadcast agent configuration changes
                await websocket_manager.broadcast_to_agent({
                    "type": "agent_configuration_change",
                    "data": {
                        "user_id": user.id,
                        "user_info": user_info,
                        "changes": message_data.get("changes"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, agent_id, exclude_connection=connection_id)
                
            elif message_type == "chat_message":
                # Broadcast chat messages to all users
                await websocket_manager.broadcast_to_agent({
                    "type": "chat_message",
                    "data": {
                        "user_id": user.id,
                        "user_info": user_info,
                        "message": message_data.get("message"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, agent_id)
                
            elif message_type == "request_sync":
                # Send current state to requesting user
                current_state = await get_agent_current_state(agent_id, db)
                await websocket_manager.send_message({
                    "type": "sync_response",
                    "data": {
                        "agent_state": current_state,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, connection_id)
                
            elif message_type == "ping":
                # Respond to ping with pong
                await websocket_manager.send_message({
                    "type": "pong",
                    "data": {
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, connection_id)
                
    except WebSocketDisconnect:
        logger.info(f"Collaboration WebSocket disconnected: {connection_id}")
        websocket_manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"Collaboration WebSocket error: {e}")
        websocket_manager.disconnect(connection_id)


async def get_agent_current_state(agent_id: int, db: AsyncSession) -> Dict[str, Any]:
    """Get current state of agent for synchronization"""
    result = await db.execute(select(AgentModel).where(AgentModel.id == agent_id))
    agent = result.scalar_one_or_none()
    
    if not agent:
        return {}
    
    return {
        "agent": {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "status": agent.status.value,
            "system_prompt": agent.system_prompt,
            "user_prompt_template": agent.user_prompt_template,
            "model_config": agent.model_config,
            "tags": agent.tags,
            "metadata": agent.metadata,
            "updated_at": agent.updated_at.isoformat()
        },
        "collaborators": await websocket_manager.get_agent_users(agent_id)
    }


# Helper functions for broadcasting events
async def broadcast_agent_update(agent_id: int, update_data: Dict[str, Any]):
    """Broadcast agent update to all collaborators"""
    await websocket_manager.broadcast_to_agent({
        "type": "agent_updated",
        "data": {
            "agent_id": agent_id,
            "update": update_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    }, agent_id)


async def broadcast_knowledge_update(agent_id: int, file_data: Dict[str, Any]):
    """Broadcast knowledge base update to all collaborators"""
    await websocket_manager.broadcast_to_agent({
        "type": "knowledge_updated",
        "data": {
            "agent_id": agent_id,
            "file": file_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    }, agent_id)


async def broadcast_agent_status_change(agent_id: int, old_status: str, new_status: str, user_id: int):
    """Broadcast agent status change to all collaborators"""
    await websocket_manager.broadcast_to_agent({
        "type": "agent_status_changed",
        "data": {
            "agent_id": agent_id,
            "old_status": old_status,
            "new_status": new_status,
            "changed_by": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    }, agent_id)