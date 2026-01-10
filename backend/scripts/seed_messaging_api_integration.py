"""
Seed the Messaging API integration into the database
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.future import select
from app.core.database import async_session_maker
from app.models.integration import Integration as IntegrationModel
from app.models.user import User as UserModel


async def seed_messaging_api():
    """Seed the Messaging API integration"""
    async with async_session_maker() as session:
        # Check if integration already exists
        result = await session.execute(
            select(IntegrationModel).where(IntegrationModel.name == "Messaging API")
        )
        existing = result.scalars().first()
        
        if existing:
            print("Messaging API integration already exists")
            return
        
        # Get the first user (or create a system user)
        result = await session.execute(select(UserModel).limit(1))
        user = result.scalars().first()
        
        if not user:
            print("No users found. Please create a user first.")
            return
        
        # Create the Messaging API integration
        messaging_api = IntegrationModel(
            name="Messaging API",
            description="Send messages to your Chronos agents from any bot backend system using Personal Access Tokens for authentication",
            integration_type="api",
            category="communication",
            icon="💬",
            documentation_url="https://docs.chronos.ai/messaging-api",
            version="0.2.3",
            is_public=True,
            download_count=0,
            rating=0.0,
            review_count=0,
            author_id=user.id,
            config_schema={
                "type": "object",
                "properties": {
                    "webhook_url": {
                        "type": "string",
                        "title": "Response Endpoint URL",
                        "description": "The bot will send its messages to this URL",
                        "format": "uri"
                    },
                    "personal_access_token": {
                        "type": "string",
                        "title": "Personal Access Token",
                        "description": "Your Chronos Personal Access Token for authentication",
                        "format": "password"
                    }
                },
                "required": ["webhook_url", "personal_access_token"]
            },
            metadata={
                "features": [
                    "Send messages to agents via API",
                    "Receive responses via webhook",
                    "Secure authentication with Personal Access Tokens",
                    "Support for multiple message types",
                    "Conversation tracking"
                ],
                "endpoints": {
                    "send_message": "/api/v1/messaging/messages/send",
                    "get_webhook": "/api/v1/messaging/messages/webhook",
                    "test_webhook": "/api/v1/messaging/messages/webhook/test"
                },
                "authentication": {
                    "type": "bearer",
                    "header": "Authorization",
                    "format": "Bearer {PERSONAL_ACCESS_TOKEN}"
                },
                "message_format": {
                    "userId": "string (required) - User ID to identify the conversation",
                    "messageId": "string (required) - Unique message ID to prevent duplicates",
                    "conversationId": "string (required) - Conversation ID for tracking",
                    "type": "string (required) - Message type (text, image, etc.)",
                    "text": "string (required) - Message text content",
                    "payload": "object (optional) - Additional message data"
                },
                "response_format": {
                    "type": "string - Message type",
                    "payload": "object - Response data",
                    "conversationId": "string - Conversation ID",
                    "chronosUserId": "string - Chronos user ID",
                    "chronosMessageId": "string - Chronos message ID",
                    "chronosConversationId": "string - Chronos conversation ID"
                }
            }
        )
        
        session.add(messaging_api)
        await session.commit()
        
        print("✅ Messaging API integration seeded successfully")


if __name__ == "__main__":
    asyncio.run(seed_messaging_api())
