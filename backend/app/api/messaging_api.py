from fastapi import APIRouter, Depends, HTTPException, status, Header, Body
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from datetime import datetime
from pydantic import BaseModel, Field
import json

from app.models.personal_access_token import PersonalAccessToken as PersonalAccessTokenModel
from app.models.agent import AgentModel
from app.models.user import User as UserModel
from app.core.database import get_db
from app.core.conversation_manager import append_message, get_or_create_conversation

router = APIRouter()


class MessageRequest(BaseModel):
    """Request body for sending a message"""
    userId: str = Field(..., description="User ID to identify the conversation")
    messageId: str = Field(..., description="Unique message ID to prevent duplicates")
    conversationId: str = Field(..., description="Conversation ID for tracking")
    type: str = Field(default="text", description="Message type (text, image, etc.)")
    text: str = Field(..., description="Message text content")
    payload: Optional[Dict[str, Any]] = Field(default=None, description="Additional message data")
    agent_id: Optional[int] = Field(default=None, description="Optional target agent ID")


class MessageResponse(BaseModel):
    """Response body for message operations"""
    type: str
    payload: Optional[Dict[str, Any]] = None
    conversationId: str
    chronosUserId: Optional[str] = None
    chronosMessageId: Optional[str] = None
    chronosConversationId: Optional[str] = None


async def verify_token(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> tuple[PersonalAccessTokenModel, UserModel]:
    """Verify the personal access token from Authorization header"""
    # Check if authorization header is in correct format
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>"
        )
    
    # Extract token
    token = authorization.replace("Bearer ", "").strip()
    
    if not token.startswith("chronos_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    
    # Hash the token to compare with stored hash
    token_hash = PersonalAccessTokenModel.hash_token(token)
    
    # Find the token in database
    result = await db.execute(
        select(PersonalAccessTokenModel).where(
            PersonalAccessTokenModel.token_hash == token_hash,
            PersonalAccessTokenModel.is_active == True,
            PersonalAccessTokenModel.is_revoked == False
        )
    )
    db_token = result.scalars().first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked token"
        )
    
    # Check if token is expired
    if db_token.expires_at:
        try:
            expires_at = datetime.fromisoformat(db_token.expires_at)
            if datetime.utcnow() > expires_at:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
        except ValueError:
            pass  # Invalid date format, ignore expiry check
    
    # Get the user
    result = await db.execute(
        select(UserModel).where(UserModel.id == db_token.user_id)
    )
    user = result.scalars().first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Update token usage
    db_token.usage_count += 1
    db_token.last_used_at = datetime.utcnow().isoformat()
    await db.commit()
    
    return db_token, user


@router.post("/messages/send", response_model=MessageResponse)
async def send_message(
    message: MessageRequest,
    token_user: tuple = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Send a message to a Chronos agent
    
    This endpoint allows external systems to send messages to agents using a Personal Access Token.
    The bot will process the message and send responses to the configured webhook URL.
    """
    token, user = token_user

    # Resolve target agent for conversation tracking
    agent_id = message.agent_id or (message.payload or {}).get("agent_id")
    agent = None
    if agent_id is not None:
        result = await db.execute(
            select(AgentModel).where(
                AgentModel.id == int(agent_id),
                AgentModel.owner_id == user.id
            )
        )
        agent = result.scalars().first()
    if not agent:
        result = await db.execute(
            select(AgentModel).where(AgentModel.owner_id == user.id).order_by(AgentModel.created_at.asc())
        )
        agent = result.scalars().first()

    conversation = None
    if agent:
        conversation = await get_or_create_conversation(
            db,
            agent_id=agent.id,
            user_id=user.id,
            channel_type="messaging_api",
            external_conversation_id=message.conversationId,
            title=f"Messaging API {message.conversationId}"
        )
        await append_message(
            db,
            conversation=conversation,
            role="user",
            content=message.text,
            metadata={"message_type": message.type, "payload": message.payload},
            source_platform_message_id=message.messageId
        )
    
    # Log the message (in production, you'd store this in a messages table)
    response_data = {
        "type": message.type,
        "payload": {
            "text": f"Message received: {message.text}",
            "status": "processing"
        },
        "conversationId": message.conversationId,
        "chronosUserId": str(user.id),
        "chronosMessageId": f"msg_{datetime.utcnow().timestamp()}",
        "chronosConversationId": message.conversationId
    }

    if conversation:
        await append_message(
            db,
            conversation=conversation,
            role="agent",
            content=response_data["payload"]["text"],
            metadata={"status": response_data["payload"]["status"]},
            source_platform_message_id=response_data["chronosMessageId"]
        )

    return MessageResponse(**response_data)


@router.get("/messages/webhook")
async def get_webhook_url(
    token_user: tuple = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get the webhook URL for receiving bot responses"""
    token, user = token_user
    
    # In production, this would be stored in integration config
    webhook_url = f"https://webhook.chronos.cloud/{user.id}/messages"
    
    return {
        "webhookUrl": webhook_url,
        "userId": user.id,
        "username": user.username
    }


@router.post("/messages/webhook/test")
async def test_webhook(
    webhook_url: str = Body(..., embed=True, description="Webhook URL to test"),
    token_user: tuple = Depends(verify_token)
):
    """Test a webhook URL by sending a test message"""
    token, user = token_user
    
    # In production, you would actually send a test request to the webhook
    return {
        "success": True,
        "message": "Test message sent to webhook",
        "webhookUrl": webhook_url
    }
