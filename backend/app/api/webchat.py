from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
from uuid import uuid4

from app.core.webchat import (
    WebChatConfig,
    WebChatMessage,
    webchat_manager,
    WebChatError
)
from app.core.security import get_current_user
from app.models.user import User as UserModel


router = APIRouter()


@router.post("/webchat/sessions/", response_model=Dict[str, Any])
async def create_webchat_session(
    config: WebChatConfig,
    current_user: UserModel = Depends(get_current_user)
):
    """Create a new WebChat session"""
    try:
        session_id = str(uuid4())
        session = await webchat_manager.create_session(
            session_id=session_id,
            config=config,
            user_id=str(current_user.id)
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "WebChat session created successfully"
        }
    except WebChatError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create WebChat session: {str(e)}")


@router.get("/webchat/sessions/{session_id}", response_model=Dict[str, Any])
async def get_webchat_session(
    session_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Get WebChat session details"""
    try:
        session = await webchat_manager.get_session(session_id)
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "agent_id": session.agent_id,
            "status": session.status,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": len(session.messages)
        }
    except WebChatError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get WebChat session: {str(e)}")


@router.post("/webchat/messages/{session_id}", response_model=WebChatMessage)
async def send_webchat_message(
    session_id: str,
    message: WebChatMessage,
    current_user: UserModel = Depends(get_current_user)
):
    """Send a message in a WebChat session"""
    try:
        result = await webchat_manager.send_message(session_id, message)
        return result
    except WebChatError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send WebChat message: {str(e)}")


@router.get("/webchat/messages/{session_id}", response_model=List[WebChatMessage])
async def get_webchat_messages(
    session_id: str,
    limit: int = 50,
    current_user: UserModel = Depends(get_current_user)
):
    """Get messages from a WebChat session"""
    try:
        messages = await webchat_manager.get_messages(session_id, limit)
        return messages
    except WebChatError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get WebChat messages: {str(e)}")


@router.post("/webchat/end/{session_id}", response_model=Dict[str, Any])
async def end_webchat_session(
    session_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """End a WebChat session"""
    try:
        session = await webchat_manager.end_session(session_id)
        return {
            "success": True,
            "session_id": session_id,
            "message": "WebChat session ended successfully"
        }
    except WebChatError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end WebChat session: {str(e)}")


@router.post("/webchat/embed/{session_id}", response_model=Dict[str, Any])
async def generate_embed_code(
    session_id: str,
    config_id: str = None,
    current_user: UserModel = Depends(get_current_user)
):
    """Generate embed code for WebChat"""
    try:
        embed_code = await webchat_manager.generate_embed_code(session_id, config_id)
        
        return {
            "success": True,
            "embed_code": embed_code,
            "session_id": session_id
        }
    except WebChatError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embed code: {str(e)}")


@router.get("/webchat/health/", response_model=Dict[str, Any])
async def get_webchat_health(
    current_user: UserModel = Depends(get_current_user)
):
    """Get WebChat system health"""
    try:
        return {
            "status": "healthy",
            "active_sessions": len(webchat_manager.sessions),
            "total_messages": sum(len(session.messages) for session in webchat_manager.sessions.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get WebChat health: {str(e)}")


# WebSocket endpoint for real-time WebChat
@router.websocket("/webchat/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str
):
    """WebSocket endpoint for real-time WebChat communication"""
    try:
        await websocket.accept()
        
        # In a real implementation, you would:
        # 1. Validate the session
        # 2. Add the websocket to the session's active connections
        # 3. Handle incoming messages
        # 4. Broadcast messages to all connected clients
        
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Process the message (in a real app, this would be more sophisticated)
                response_message = {
                    "message_id": str(uuid4()),
                    "content": f"Echo: {message['content']}",
                    "sender": "bot",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Send response back to client
                await websocket.send_text(json.dumps(response_message))
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for session {session_id}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {str(e)}")
        await websocket.close(code=1011)


# Import required for WebSocket
from datetime import datetime
import json