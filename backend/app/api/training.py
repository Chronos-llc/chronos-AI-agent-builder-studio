from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import uuid
import logging
import time

from app.core.database import get_db
from app.models.user import User
from app.models.agent import AgentModel
from app.models.training import TrainingSession, TrainingInteraction, TrainingCorrection
from app.api.auth import get_current_user
from app.schemas.training import (
    TrainingSessionResponse, TrainingSessionCreate, TrainingSessionUpdate,
    TrainingInteractionResponse, TrainingInteractionCreate,
    TrainingCorrectionResponse, TrainingCorrectionCreate, TrainingCorrectionUpdate,
    TrainingTestRequest, TrainingTestResponse
)
from app.core.agent_engine import get_agent_engine

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/agents/{agent_id}/training/sessions", response_model=TrainingSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_training_session(
    agent_id: int,
    session_data: TrainingSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new training session"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # Create training session
    training_session = TrainingSession(
        **session_data.dict(),
        agent_id=agent_id,
        user_id=current_user.id,
        started_at=datetime.utcnow()
    )
    
    db.add(training_session)
    await db.commit()
    await db.refresh(training_session)
    
    return training_session


@router.get("/agents/{agent_id}/training/sessions", response_model=List[TrainingSessionResponse])
async def get_training_sessions(
    agent_id: int,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all training sessions for an agent"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # Build query
    query = select(TrainingSession).where(TrainingSession.agent_id == agent_id)
    
    if status:
        query = query.where(TrainingSession.status == status)
    
    query = query.offset(skip).limit(limit).order_by(TrainingSession.created_at.desc())
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    return sessions


@router.get("/agents/{agent_id}/training/sessions/{session_id}", response_model=TrainingSessionResponse)
async def get_training_session(
    agent_id: int,
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific training session"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # Get training session
    result = await db.execute(
        select(TrainingSession).where(
            and_(
                TrainingSession.id == session_id,
                TrainingSession.agent_id == agent_id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found"
        )
    
    return session


@router.put("/agents/{agent_id}/training/sessions/{session_id}", response_model=TrainingSessionResponse)
async def update_training_session(
    agent_id: int,
    session_id: str,
    session_update: TrainingSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update training session details"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # Get training session
    result = await db.execute(
        select(TrainingSession).where(
            and_(
                TrainingSession.id == session_id,
                TrainingSession.agent_id == agent_id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found"
        )
    
    # Update session
    update_data = session_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    await db.commit()
    await db.refresh(session)
    
    return session


@router.post("/agents/{agent_id}/training/sessions/{session_id}/end")
async def end_training_session(
    agent_id: int,
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """End a training session"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # Get training session
    result = await db.execute(
        select(TrainingSession).where(
            and_(
                TrainingSession.id == session_id,
                TrainingSession.agent_id == agent_id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found"
        )
    
    # End the session
    session.status = "completed"
    session.ended_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(session)
    
    return {"success": True, "ended_at": session.ended_at, "session": session}


@router.post("/agents/{agent_id}/training/test", response_model=TrainingTestResponse)
async def training_test(
    agent_id: int,
    test_request: TrainingTestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a test message to the agent during training using AgentEngine"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # Use AgentEngine for real-time testing
    agent_engine = await get_agent_engine()
    
    # Prepare context with user information
    context = {
        "user_id": current_user.id,
        "user_name": current_user.username,
        "session_id": test_request.session_id
    }
    
    try:
        # Execute agent with training context
        start_time = time.time()
        execution_result = await agent_engine.execute_agent(
            agent_id=agent_id,
            user_input=test_request.message,
            session_id=test_request.session_id,
            context=context,
            db=db
        )
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Extract interaction ID if available
        interaction_id = None
        if test_request.session_id and execution_result.get("execution_summary"):
            # The interaction was already created by AgentEngine
            # We can extract it from the execution summary or metadata
            pass
        
        return {
            "response": execution_result["response"],
            "response_time_ms": response_time_ms,
            "execution_log": execution_result.get("execution_log", []),
            "interaction_id": interaction_id,
            "session_id": test_request.session_id,
            "agent_state": execution_result.get("agent_state", {})
        }
        
    except Exception as e:
        logger.error(f"Training test failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Training test failed: {str(e)}"
        )


@router.get("/agents/{agent_id}/training/test/history", response_model=List[TrainingInteractionResponse])
async def get_training_test_history(
    agent_id: int,
    session_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get test history for an agent"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # Build query
    query = select(TrainingInteraction).join(TrainingSession).
        where(TrainingSession.agent_id == agent_id)
    
    if session_id:
        query = query.where(TrainingInteraction.session_id == session_id)
    
    query = query.offset(skip).limit(limit).
        order_by(TrainingInteraction.created_at.desc())
    
    result = await db.execute(query)
    interactions = result.scalars().all()
    
    return interactions


@router.post("/agents/{agent_id}/training/interactions", response_model=TrainingInteractionResponse, status_code=status.HTTP_201_CREATED)
async def create_training_interaction(
    agent_id: int,
    interaction_data: TrainingInteractionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Record a training interaction"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # Verify session ownership
    result = await db.execute(
        select(TrainingSession).where(
            and_(
                TrainingSession.id == interaction_data.session_id,
                TrainingSession.agent_id == agent_id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found or access denied"
        )
    
    # Create interaction
    interaction = TrainingInteraction(
        **interaction_data.dict(),
        session_id=interaction_data.session_id
    )
    
    db.add(interaction)
    await db.commit()
    await db.refresh(interaction)
    
    return interaction


@router.post("/agents/{agent_id}/training/corrections", response_model=TrainingCorrectionResponse, status_code=status.HTTP_201_CREATED)
async def create_training_correction(
    agent_id: int,
    correction_data: TrainingCorrectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit a correction for agent behavior"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # Verify interaction exists
    result = await db.execute(
        select(TrainingInteraction).join(TrainingSession).
        where(
            and_(
                TrainingInteraction.id == correction_data.interaction_id,
                TrainingSession.agent_id == agent_id
            )
        )
    )
    interaction = result.scalar_one_or_none()
    
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training interaction not found or access denied"
        )
    
    # Create correction
    correction = TrainingCorrection(
        **correction_data.dict(),
        interaction_id=correction_data.interaction_id
    )
    
    db.add(correction)
    await db.commit()
    await db.refresh(correction)
    
    return correction


@router.get("/agents/{agent_id}/training/corrections", response_model=List[TrainingCorrectionResponse])
async def get_training_corrections(
    agent_id: int,
    session_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all corrections for an agent"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # Build query
    query = select(TrainingCorrection).join(TrainingInteraction).join(TrainingSession).
        where(TrainingSession.agent_id == agent_id)
    
    if session_id:
        query = query.where(TrainingSession.id == session_id)
    
    if status:
        query = query.where(TrainingCorrection.status == status)
    
    query = query.offset(skip).limit(limit).
        order_by(TrainingCorrection.created_at.desc())
    
    result = await db.execute(query)
    corrections = result.scalars().all()
    
    return corrections


@router.post("/agents/{agent_id}/training/corrections/{correction_id}/apply")
async def apply_training_correction(
    agent_id: int,
    correction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Apply a correction to the agent using AgentEngine"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # Use AgentEngine to apply correction
    agent_engine = await get_agent_engine()
    
    try:
        result = await agent_engine.apply_correction(correction_id, db)
        return result
        
    except Exception as e:
        logger.error(f"Failed to apply correction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply correction: {str(e)}"
        )


@router.post("/agents/{agent_id}/training/corrections/{correction_id}/reject")
async def reject_training_correction(
    agent_id: int,
    correction_id: str,
    rejection_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject a correction"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # Get correction
    result = await db.execute(
        select(TrainingCorrection).join(TrainingInteraction).join(TrainingSession).
        where(
            and_(
                TrainingCorrection.id == correction_id,
                TrainingSession.agent_id == agent_id
            )
        )
    )
    correction = result.scalar_one_or_none()
    
    if not correction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Correction not found or access denied"
        )
    
    # Reject correction
    correction.status = "rejected"
    
    await db.commit()
    await db.refresh(correction)
    
    return {
        "success": True,
        "rejected_at": datetime.utcnow(),
        "reason": rejection_data.get("reason", "No reason provided")
    }


@router.get("/agents/{agent_id}/training/analytics")
async def get_training_analytics(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get training analytics for an agent using AgentEngine"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # Use AgentEngine to get analytics
    agent_engine = await get_agent_engine()
    
    try:
        analytics = await agent_engine.get_training_analytics(agent_id, db)
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Failed to get training analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get training analytics: {str(e)}"
        )


# WebSocket endpoint for real-time training updates
class TrainingWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self.session_connections: Dict[str, List[str]] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str, user_id: int) -> str:
        """Accept WebSocket connection and register it"""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        
        # Store connection info
        self.active_connections[connection_id] = {
            "websocket": websocket,
            "session_id": session_id,
            "user_id": user_id,
            "connected_at": time.time()
        }
        
        # Register in session connections
        if session_id not in self.session_connections:
            self.session_connections[session_id] = []
        self.session_connections[session_id].append(connection_id)
        
        return connection_id
        
    def disconnect(self, connection_id: str):
        """Handle WebSocket disconnection"""
        if connection_id not in self.active_connections:
            return
            
        connection_info = self.active_connections[connection_id]
        session_id = connection_info["session_id"]
        
        # Remove from active connections
        del self.active_connections[connection_id]
        
        # Remove from session connections
        if session_id in self.session_connections:
            if connection_id in self.session_connections[session_id]:
                self.session_connections[session_id].remove(connection_id)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]
                
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
            
    async def broadcast_to_session(self, message: Dict[str, Any], session_id: str, exclude_connection: Optional[str] = None):
        """Broadcast message to all users in a training session"""
        if session_id not in self.session_connections:
            return
            
        for connection_id in self.session_connections[session_id]:
            if connection_id != exclude_connection:
                await self.send_message(message, connection_id)


# Global WebSocket manager instance
training_websocket_manager = TrainingWebSocketManager()


@router.websocket("/agents/{agent_id}/training/real-time")
async def training_websocket_endpoint(
    websocket: WebSocket,
    agent_id: int,
    session_id: str,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time training session updates"""
    
    # Authenticate user
    try:
        user = await get_current_user_from_token(token, db)
    except HTTPException as e:
        await websocket.close(code=4001, reason=str(e.detail))
        return
     
    # Verify agent ownership
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
    
    # Verify session ownership
    result = await db.execute(
        select(TrainingSession).where(
            and_(
                TrainingSession.id == session_id,
                TrainingSession.agent_id == agent_id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        await websocket.close(code=4005, reason="Training session not found or access denied")
        return
    
    # Connect WebSocket
    connection_id = await training_websocket_manager.connect(websocket, session_id, user.id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"Received training message: {message}")
            
            # Handle different training message types
            message_type = message.get("type")
            message_data = message.get("data", {})
            
            if message_type == "test_message":
                # Broadcast test message to other users in session
                await training_websocket_manager.broadcast_to_session({
                    "type": "test_message",
                    "data": {
                        "user_id": user.id,
                        "message": message_data.get("message"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, session_id, exclude_connection=connection_id)
                
            elif message_type == "agent_response":
                # Broadcast agent response to all users
                await training_websocket_manager.broadcast_to_session({
                    "type": "agent_response",
                    "data": {
                        "response": message_data.get("response"),
                        "response_time_ms": message_data.get("response_time_ms"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, session_id)
                
            elif message_type == "execution_log":
                # Broadcast execution log update
                await training_websocket_manager.broadcast_to_session({
                    "type": "execution_log",
                    "data": {
                        "log": message_data.get("log"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, session_id)
                
            elif message_type == "session_status":
                # Broadcast session status change
                await training_websocket_manager.broadcast_to_session({
                    "type": "session_status",
                    "data": {
                        "status": message_data.get("status"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, session_id)
                
            elif message_type == "learning_injection":
                # Broadcast learning injection applied
                await training_websocket_manager.broadcast_to_session({
                    "type": "learning_injection",
                    "data": {
                        "injection_type": message_data.get("injection_type"),
                        "content": message_data.get("content"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, session_id)
                
    except WebSocketDisconnect:
        logger.info(f"Training WebSocket disconnected: {connection_id}")
        training_websocket_manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"Training WebSocket error: {e}")
        training_websocket_manager.disconnect(connection_id)


async def get_current_user_from_token(token: str, db: AsyncSession) -> User:
    """Get current user from WebSocket token (reused from websocket.py)"""
    from app.core.security import verify_token
    from fastapi import HTTPException, status
    
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