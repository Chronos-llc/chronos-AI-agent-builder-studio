from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.communication_channels import (
    CommunicationChannelConfig,
    CommunicationMessage,
    communication_manager,
    CommunicationChannelError
)
from app.core.content_analysis import content_analyzer
from app.api.auth import get_current_user
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

# Interaction Management Endpoints

@router.post("/communication/interactions/send-with-interactions", response_model=Dict[str, Any])
async def send_message_with_interactions(
    message_data: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user)
):
    """Send a message with full interaction management (reactions and typing indicators)"""
    try:
        # Parse message with new fields
        message = CommunicationMessage(**message_data)
        channel_id = message_data.get("channel_id")
        sender_info = message_data.get("sender_info")
        
        # Support for routing to multiple channels
        route_to = message_data.get("route_to", [])
        if route_to:
            message.route_to = route_to
        
        result = await communication_manager.process_message_with_interactions(
            message, channel_id, sender_info
        )
        return result
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message with interactions: {str(e)}")

@router.get("/communication/interactions/active/{channel_id}", response_model=Dict[str, Any])
async def get_active_interactions(
    channel_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Get currently active interactions for a specific channel"""
    try:
        interactions = await communication_manager.get_active_interactions(channel_id)
        return interactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active interactions: {str(e)}")

@router.get("/communication/interactions/active", response_model=Dict[str, Any])
async def get_all_active_interactions(
    current_user: UserModel = Depends(get_current_user)
):
    """Get all currently active interactions across all channels"""
    try:
        interactions = await communication_manager.get_active_interactions()
        return interactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active interactions: {str(e)}")

@router.post("/communication/interactions/cleanup", response_model=Dict[str, Any])
async def cleanup_stale_interactions(
    max_age_seconds: float = 300.0,
    current_user: UserModel = Depends(get_current_user)
):
    """Clean up stale interactions that have been active too long"""
    try:
        result = await communication_manager.cleanup_stale_interactions(max_age_seconds)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup stale interactions: {str(e)}")

@router.post("/communication/content/analyze", response_model=Dict[str, Any])
async def analyze_message_content(
    content_data: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user)
):
    """Analyze message content to determine appropriate reactions and interactions"""
    try:
        content = content_data.get("content", "")
        sender_info = content_data.get("sender_info")
        
        analysis = content_analyzer.analyze_content(content, sender_info)
        
        return {
            "success": True,
            "analysis": analysis,
            "recommended_reaction": analysis["suggested_reaction"],
            "should_show_typing": analysis["requires_typing"],
            "typing_duration_estimate": content_analyzer.get_typing_duration_estimate(content, analysis["context"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze content: {str(e)}")

@router.get("/communication/content/analysis/stats", response_model=Dict[str, Any])
async def get_content_analysis_stats(
    current_user: UserModel = Depends(get_current_user)
):
    """Get statistics about content analysis usage"""
    try:
        stats = content_analyzer.get_analysis_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analysis stats: {str(e)}")

@router.post("/communication/interactions/manual-reaction", response_model=Dict[str, Any])
async def send_manual_reaction(
    reaction_data: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user)
):
    """Manually send a reaction to a message"""
    try:
        channel_id = reaction_data.get("channel_id")
        reaction = reaction_data.get("reaction")
        message_data = reaction_data.get("message")
        
        if not all([channel_id, reaction, message_data]):
            raise HTTPException(status_code=400, detail="Missing required fields: channel_id, reaction, message")
        
        # Get channel config
        config = await communication_manager.get_channel(channel_id)
        
        # Create communication message
        message = CommunicationMessage(**message_data)
        
        # Send reaction
        result = await communication_manager._manage_message_reaction(
            f"manual_{datetime.now().timestamp()}",
            config,
            message,
            reaction,
            "manual"
        )
        
        return result
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send manual reaction: {str(e)}")

@router.post("/communication/interactions/manual-typing", response_model=Dict[str, Any])
async def send_manual_typing(
    typing_data: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user)
):
    """Manually start a typing indicator"""
    try:
        channel_id = typing_data.get("channel_id")
        message_data = typing_data.get("message")
        duration = typing_data.get("duration", 3.0)
        
        if not all([channel_id, message_data]):
            raise HTTPException(status_code=400, detail="Missing required fields: channel_id, message")
        
        # Get channel config
        config = await communication_manager.get_channel(channel_id)
        
        # Create communication message
        message = CommunicationMessage(**message_data)
        
        # Send typing indicator
        result = await communication_manager._manage_typing_indicator(
            f"manual_{datetime.now().timestamp()}",
            config,
            message,
            duration
        )
        
        return result
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send manual typing: {str(e)}")

@router.put("/communication/channels/{channel_id}/interaction-settings", response_model=Dict[str, Any])
async def update_interaction_settings(
    channel_id: str,
    settings_data: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user)
):
    """Update interaction settings for a communication channel"""
    try:
        # Get current channel config
        config = await communication_manager.get_channel(channel_id)
        
        # Update interaction settings
        if "enable_reactions" in settings_data:
            config.enable_reactions = settings_data["enable_reactions"]
        if "enable_typing_indicator" in settings_data:
            config.enable_typing_indicator = settings_data["enable_typing_indicator"]
        if "processing_reaction" in settings_data:
            config.processing_reaction = settings_data["processing_reaction"]
        if "contextual_reactions_enabled" in settings_data:
            config.contextual_reactions_enabled = settings_data["contextual_reactions_enabled"]
        if "typing_duration_min" in settings_data:
            config.typing_duration_min = settings_data["typing_duration_min"]
        if "typing_duration_max" in settings_data:
            config.typing_duration_max = settings_data["typing_duration_max"]
        if "reaction_removal_delay" in settings_data:
            config.reaction_removal_delay = settings_data["reaction_removal_delay"]
        
        # Update the channel
        await communication_manager.remove_channel(channel_id)
        await communication_manager.add_channel(channel_id, config)
        
        return {
            "success": True,
            "channel_id": channel_id,
            "message": "Interaction settings updated successfully",
            "updated_settings": {
                "enable_reactions": config.enable_reactions,
                "enable_typing_indicator": config.enable_typing_indicator,
                "processing_reaction": config.processing_reaction,
                "contextual_reactions_enabled": config.contextual_reactions_enabled,
                "typing_duration_min": config.typing_duration_min,
                "typing_duration_max": config.typing_duration_max,
                "reaction_removal_delay": config.reaction_removal_delay
            }
        }
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update interaction settings: {str(e)}")

@router.get("/communication/channels/{channel_id}/interaction-settings", response_model=Dict[str, Any])
async def get_interaction_settings(
    channel_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Get interaction settings for a communication channel"""
    try:
        # Get current channel config
        config = await communication_manager.get_channel(channel_id)
        
        return {
            "success": True,
            "channel_id": channel_id,
            "interaction_settings": {
                "enable_reactions": config.enable_reactions,
                "enable_typing_indicator": config.enable_typing_indicator,
                "processing_reaction": config.processing_reaction,
                "contextual_reactions_enabled": config.contextual_reactions_enabled,
                "typing_duration_min": config.typing_duration_min,
                "typing_duration_max": config.typing_duration_max,
                "reaction_removal_delay": config.reaction_removal_delay
            }
        }
    except CommunicationChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get interaction settings: {str(e)}")
