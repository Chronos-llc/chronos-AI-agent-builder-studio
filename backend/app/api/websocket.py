from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websocket import WebSocket
from typing import Dict, List
import json
from datetime import datetime
from backend.app.core.security import verify_jwt_token
from backend.app.models.user import User
from backend.app.core.database import get_db

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, agent_id: str):
        await websocket.accept()
        if agent_id not in self.active_connections:
            self.active_connections[agent_id] = []
        self.active_connections[agent_id].append(websocket)
        
    def disconnect(self, websocket: WebSocket, agent_id: str):
        if agent_id in self.active_connections:
            self.active_connections[agent_id].remove(websocket)
            if not self.active_connections[agent_id]:
                del self.active_connections[agent_id]
                
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
        
    async def broadcast(self, message: str, agent_id: str, exclude_websocket: WebSocket = None):
        if agent_id in self.active_connections:
            for connection in self.active_connections[agent_id]:
                if connection != exclude_websocket:
                    await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/agent/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str, token: str):
    """
    WebSocket endpoint for real-time collaboration on agent development
    
    Handles:
    - Real-time chat messages
    - Agent configuration updates
    - Knowledge base changes
    - System instructions edits
    - Presence detection
    """
    try:
        # Authenticate user
        user_data = verify_jwt_token(token)
        if not user_data:
            await websocket.close(code=1008, reason="Unauthorized")
            return
            
        user_id = user_data.get("sub")
        username = user_data.get("username", "Unknown")
        
        # Connect to WebSocket
        await manager.connect(websocket, agent_id)
        
        # Send welcome message with current collaborators
        collaborators = [{"user_id": user_id, "username": username, "timestamp": datetime.now().isoformat()}]
        welcome_message = {
            "type": "welcome",
            "agent_id": agent_id,
            "user": {"user_id": user_id, "username": username},
            "collaborators": collaborators,
            "timestamp": datetime.now().isoformat()
        }
        await manager.send_personal_message(json.dumps(welcome_message), websocket)
        
        # Broadcast new user joined
        join_message = {
            "type": "user_joined",
            "agent_id": agent_id,
            "user": {"user_id": user_id, "username": username},
            "timestamp": datetime.now().isoformat()
        }
        await manager.broadcast(json.dumps(join_message), agent_id, websocket)
        
        # Main message loop
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                message_type = message.get("type")
                
                if message_type == "chat_message":
                    # Broadcast chat message to all collaborators
                    chat_message = {
                        "type": "chat_message",
                        "agent_id": agent_id,
                        "user": {"user_id": user_id, "username": username},
                        "content": message.get("content", ""),
                        "timestamp": datetime.now().isoformat()
                    }
                    await manager.broadcast(json.dumps(chat_message), agent_id)
                    
                elif message_type == "agent_update":
                    # Broadcast agent configuration update
                    update_message = {
                        "type": "agent_update",
                        "agent_id": agent_id,
                        "user": {"user_id": user_id, "username": username},
                        "field": message.get("field", ""),
                        "value": message.get("value"),
                        "timestamp": datetime.now().isoformat()
                    }
                    await manager.broadcast(json.dumps(update_message), agent_id, websocket)
                    
                elif message_type == "knowledge_update":
                    # Broadcast knowledge base update
                    knowledge_message = {
                        "type": "knowledge_update",
                        "agent_id": agent_id,
                        "user": {"user_id": user_id, "username": username},
                        "action": message.get("action", ""),
                        "file_id": message.get("file_id", ""),
                        "file_name": message.get("file_name", ""),
                        "timestamp": datetime.now().isoformat()
                    }
                    await manager.broadcast(json.dumps(knowledge_message), agent_id, websocket)
                    
                elif message_type == "instructions_update":
                    # Broadcast system instructions update
                    instructions_message = {
                        "type": "instructions_update",
                        "agent_id": agent_id,
                        "user": {"user_id": user_id, "username": username},
                        "content": message.get("content", ""),
                        "timestamp": datetime.now().isoformat()
                    }
                    await manager.broadcast(json.dumps(instructions_message), agent_id, websocket)
                    
                elif message_type == "presence_update":
                    # Update user presence
                    presence_message = {
                        "type": "presence_update",
                        "agent_id": agent_id,
                        "user": {"user_id": user_id, "username": username},
                        "status": message.get("status", "active"),
                        "timestamp": datetime.now().isoformat()
                    }
                    await manager.broadcast(json.dumps(presence_message), agent_id, websocket)
                    
            except json.JSONDecodeError:
                error_msg = {
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(json.dumps(error_msg), websocket)
                
    except WebSocketDisconnect:
        # Handle client disconnect
        leave_message = {
            "type": "user_left",
            "agent_id": agent_id,
            "user": {"user_id": user_id, "username": username},
            "timestamp": datetime.now().isoformat()
        }
        await manager.broadcast(json.dumps(leave_message), agent_id, websocket)
        manager.disconnect(websocket, agent_id)
        
    except Exception as e:
        # Handle other errors
        error_msg = {
            "type": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }
        await manager.send_personal_message(json.dumps(error_msg), websocket)
        manager.disconnect(websocket, agent_id)