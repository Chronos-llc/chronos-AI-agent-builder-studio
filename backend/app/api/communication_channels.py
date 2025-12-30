from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any, List

from app.core.communication_channels import (
    CommunicationChannelConfig,
    CommunicationMessage,
    communication_manager,
    CommunicationChannelError
)
from app.core.security import get_current_user
from app.models.user import User as UserModel


router = APIRouter()


@router.post("/communication/channels/", response_model=Dict[str, Any])
async def add_communication_channel(
    channel_data: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user)
):
    """Add a new communication channel"""
    try:
        config = CommunicationChannelConfig(**channel_data)
        await communication_manager.add_channel(channel_data["channel_id"], config)
        
        return {
            "success": True,
            "channel_id": channel_data["channel_id"],
            "message": "Communication channel added successfully"
        }
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add communication channel: {str(e)}")


@router.delete("/communication/channels/{channel_id}", response_model=Dict[str, Any])
async def remove_communication_channel(
    channel_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Remove a communication channel"""
    try:
        await communication_manager.remove_channel(channel_id)
        
        return {
            "success": True,
            "channel_id": channel_id,
            "message": "Communication channel removed successfully"
        }
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove communication channel: {str(e)}")


@router.get("/communication/channels/", response_model=List[Dict[str, Any]])
async def list_communication_channels(
    current_user: UserModel = Depends(get_current_user)
):
    """List all configured communication channels"""
    try:
        channels = await communication_manager.list_channels()
        return channels
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list communication channels: {str(e)}")


@router.post("/communication/send/", response_model=Dict[str, Any])
async def send_message(
    message_data: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user)
):
    """Send a message through a communication channel with advanced routing"""
    try:
        # Parse message with new fields
        message = CommunicationMessage(**message_data)
        channel_id = message_data.get("channel_id")
        
        # Support for routing to multiple channels
        route_to = message_data.get("route_to", [])
        if route_to:
            message.route_to = route_to
        
        result = await communication_manager.send_message(message, channel_id)
        return result
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.post("/communication/webhook/{channel_id}", response_model=Dict[str, Any])
async def receive_webhook(
    channel_id: str,
    request: Request,
    current_user: UserModel = Depends(get_current_user)
):
    """Receive webhook messages"""
    try:
        payload = await request.json()
        result = await communication_manager.receive_webhook(channel_id, payload)
        return result
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {str(e)}")


@router.get("/communication/health/", response_model=Dict[str, Any])
async def get_communication_health(
    current_user: UserModel = Depends(get_current_user)
):
    """Get communication system health"""
    try:
        channels = await communication_manager.list_channels()
        
        return {
            "status": "healthy",
            "total_channels": len(channels),
            "default_channel": communication_manager.default_channel,
            "channels": [channel["channel_id"] for channel in channels]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get communication health: {str(e)}")


@router.post("/communication/test/{channel_id}", response_model=Dict[str, Any])
async def test_communication_channel(
    channel_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Test a communication channel"""
    try:
        # Get channel config
        config = await communication_manager.get_channel(channel_id)
        
        # Send a test message
        test_message = CommunicationMessage(
            content="This is a test message from Chronos AI Agent Builder",
            channel_id=config.channel_id,
            message_type="text",
            analytics_id=f"test_{channel_id}_{datetime.now().timestamp()}"
        )
        
        result = await communication_manager.send_message(test_message, channel_id)
        
        if result.get("success"):
            return {
                "success": True,
                "channel_id": channel_id,
                "message": "Communication channel test successful",
                "details": result,
                "analytics_id": test_message.analytics_id
            }
        else:
            return {
                "success": False,
                "channel_id": channel_id,
                "message": "Communication channel test failed",
                "error": result.get("error")
            }
    except CommunicationChannelError as e:
        return {
            "success": False,
            "channel_id": channel_id,
            "message": "Communication channel test failed",
            "error": str(e)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test communication channel: {str(e)}")

# Routing Rules Endpoints

@router.post("/communication/routing/rules/{channel_id}", response_model=Dict[str, Any])
async def add_routing_rule(
    channel_id: str,
    rule_data: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user)
):
    """Add a routing rule for a communication channel"""
    try:
        rule = RoutingRule(**rule_data)
        await communication_manager.add_routing_rule(channel_id, rule)
        
        return {
            "success": True,
            "channel_id": channel_id,
            "rule_name": rule.name,
            "message": "Routing rule added successfully"
        }
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add routing rule: {str(e)}")

@router.get("/communication/routing/rules/{channel_id}", response_model=List[Dict[str, Any]])
async def get_routing_rules(
    channel_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Get routing rules for a communication channel"""
    try:
        rules = await communication_manager.get_routing_rules(channel_id)
        return [rule.dict() for rule in rules]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get routing rules: {str(e)}")

@router.delete("/communication/routing/rules/{channel_id}/{rule_name}", response_model=Dict[str, Any])
async def remove_routing_rule(
    channel_id: str,
    rule_name: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Remove a routing rule"""
    try:
        await communication_manager.remove_routing_rule(channel_id, rule_name)
        
        return {
            "success": True,
            "channel_id": channel_id,
            "rule_name": rule_name,
            "message": "Routing rule removed successfully"
        }
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove routing rule: {str(e)}")

# Analytics Endpoints

@router.get("/communication/analytics/messages/{analytics_id}", response_model=Dict[str, Any])
async def get_message_analytics(
    analytics_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Get analytics for a specific message"""
    try:
        analytics = await communication_manager.get_message_analytics(analytics_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="Message analytics not found")
        
        return analytics.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get message analytics: {str(e)}")

@router.get("/communication/analytics/channels/{channel_id}", response_model=Dict[str, Any])
async def get_channel_analytics(
    channel_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Get analytics for a specific channel"""
    try:
        analytics = await communication_manager.get_channel_analytics(channel_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="Channel analytics not found")
        
        return analytics.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get channel analytics: {str(e)}")

@router.get("/communication/analytics/", response_model=Dict[str, Any])
async def get_all_analytics(
    current_user: UserModel = Depends(get_current_user)
):
    """Get comprehensive analytics for all communication channels"""
    try:
        analytics = await communication_manager.get_all_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

# Queue Management Endpoints

@router.post("/communication/queue/{channel_id}", response_model=Dict[str, Any])
async def queue_message(
    channel_id: str,
    message_data: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user)
):
    """Queue a message for delayed processing"""
    try:
        message = CommunicationMessage(**message_data)
        result = await communication_manager.queue_message(channel_id, message)
        return result
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue message: {str(e)}")

@router.post("/communication/queue/{channel_id}/process", response_model=Dict[str, Any])
async def process_queue(
    channel_id: str,
    batch_size: int = 10,
    current_user: UserModel = Depends(get_current_user)
):
    """Process queued messages"""
    try:
        result = await communication_manager.process_queue(channel_id, batch_size)
        return result
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process queue: {str(e)}")

# Session Management Endpoints

@router.post("/communication/sessions/{channel_id}", response_model=Dict[str, Any])
async def start_session(
    channel_id: str,
    user_id: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user)
):
    """Start a communication session"""
    try:
        session_id = f"session_{channel_id}_{datetime.now().timestamp()}"
        result = await communication_manager.start_session(session_id, channel_id, user_id)
        return result
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@router.post("/communication/sessions/{session_id}/end", response_model=Dict[str, Any])
async def end_session(
    session_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """End a communication session"""
    try:
        result = await communication_manager.end_session(session_id)
        return result
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")

@router.post("/communication/sessions/{session_id}/messages", response_model=Dict[str, Any])
async def track_session_message(
    session_id: str,
    message_data: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user)
):
    """Track a message within a session"""
    try:
        message = CommunicationMessage(**message_data)
        await communication_manager.track_session_message(session_id, message)
        
        return {
            "success": True,
            "session_id": session_id,
            "message_id": message.analytics_id,
            "message": "Message tracked successfully"
        }
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track session message: {str(e)}")