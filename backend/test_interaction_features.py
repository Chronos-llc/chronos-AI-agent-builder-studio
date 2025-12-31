#!/usr/bin/env python3
"""
Test script for enhanced Telegram bot communication channel interaction features.

This script tests:
1. Content analysis for contextual emoji reactions
2. Dynamic reaction management
3. Typing indicator management
4. API endpoints for interaction management
5. Integration with webhook processing
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.content_analysis import content_analyzer
from app.core.communication_channels import (
    CommunicationChannelConfig,
    CommunicationMessage,
    communication_manager,
    CommunicationChannelError
)

class InteractionFeaturesTester:
    """Test suite for enhanced interaction features"""
    
    def __init__(self):
        self.test_results = []
        self.test_channel_id = "test_telegram_channel"
    
    def log_test_result(self, test_name: str, success: bool, message: str, details: Any = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"    Details: {details}")
    
    async def test_content_analysis(self):
        """Test content analysis functionality"""
        print("\\n=== Testing Content Analysis ===")
        
        # Test cases for different message types
        test_cases = [
            {
                "content": "Hello! How are you today?",
                "expected_context": "greeting",
                "description": "Greeting message"
            },
            {
                "content": "What is the weather like?",
                "expected_context": "question",
                "description": "Question message"
            },
            {
                "content": "I'm confused about the instructions",
                "expected_context": "confusion",
                "description": "Confusion message"
            },
            {
                "content": "This is amazing! Great work!",
                "expected_context": "celebration",
                "description": "Celebration message"
            },
            {
                "content": "Sorry, I made a mistake",
                "expected_context": "apology",
                "description": "Apology message"
            },
            {
                "content": "I need help with this problem",
                "expected_context": "support",
                "description": "Support message"
            },
            {
                "content": "/start command executed",
                "expected_context": "command",
                "description": "Command message"
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            try:
                analysis = content_analyzer.analyze_content(test_case["content"])
                
                if analysis["context"] == test_case["expected_context"]:
                    self.log_test_result(
                        f"Content Analysis {i+1}",
                        True,
                        f"Correctly identified {test_case['description']} as {analysis['context']}",
                        {"suggested_reaction": analysis["suggested_reaction"], "confidence": analysis["confidence"]}
                    )
                else:
                    self.log_test_result(
                        f"Content Analysis {i+1}",
                        False,
                        f"Expected {test_case['expected_context']}, got {analysis['context']}",
                        {"content": test_case["content"], "analysis": analysis}
                    )
                
            except Exception as e:
                self.log_test_result(
                    f"Content Analysis {i+1}",
                    False,
                    f"Exception during analysis: {str(e)}"
                )
    
    async def test_channel_configuration(self):
        """Test communication channel configuration with interaction settings"""
        print("\\n=== Testing Channel Configuration ===")
        
        try:
            # Create a test channel configuration
            config = CommunicationChannelConfig(
                channel_type="telegram",
                channel_id=self.test_channel_id,
                bot_token="test_bot_token",
                telegram_bot_username="test_bot",
                enable_reactions=True,
                enable_typing_indicator=True,
                processing_reaction="👀",
                contextual_reactions_enabled=True,
                typing_duration_min=1.0,
                typing_duration_max=8.0,
                reaction_removal_delay=0.5
            )
            
            # Add the channel
            await communication_manager.add_channel(self.test_channel_id, config)
            
            self.log_test_result(
                "Channel Configuration",
                True,
                "Successfully created and configured test channel with interaction settings",
                {"channel_id": self.test_channel_id, "config": config.dict()}
            )
            
        except Exception as e:
            self.log_test_result(
                "Channel Configuration",
                False,
                f"Failed to configure channel: {str(e)}"
            )
    
    async def test_message_processing_with_interactions(self):
        """Test message processing with interactions enabled"""
        print("\\n=== Testing Message Processing with Interactions ===")
        
        try:
            # Create a test message
            test_message = CommunicationMessage(
                content="Hello! Can you help me with something?",
                channel_id=self.test_channel_id,
                user_id="test_user_123",
                message_id="msg_123456"
            )
            
            # Test with interactions
            result = await communication_manager.process_message_with_interactions(
                test_message,
                self.test_channel_id,
                {"user_id": "test_user_123", "username": "testuser"}
            )
            
            if "processing_id" in result and "interaction_analysis" in result:
                self.log_test_result(
                    "Message Processing with Interactions",
                    True,
                    "Successfully processed message with interactions",
                    {
                        "processing_id": result["processing_id"],
                        "context": result["interaction_analysis"]["context"],
                        "suggested_reaction": result["interaction_analysis"]["suggested_reaction"],
                        "requires_typing": result["interaction_analysis"]["requires_typing"]
                    }
                )
            else:
                self.log_test_result(
                    "Message Processing with Interactions",
                    False,
                    "Missing interaction data in result",
                    {"result": result}
                )
                
        except Exception as e:
            self.log_test_result(
                "Message Processing with Interactions",
                False,
                f"Failed to process message with interactions: {str(e)}"
            )
    
    async def test_active_interactions_tracking(self):
        """Test tracking of active interactions"""
        print("\\n=== Testing Active Interactions Tracking ===")
        
        try:
            # Get active interactions
            interactions = await communication_manager.get_active_interactions(self.test_channel_id)
            
            if "active_reactions" in interactions and "active_typing" in interactions:
                self.log_test_result(
                    "Active Interactions Tracking",
                    True,
                    "Successfully retrieved active interactions",
                    {
                        "active_reactions_count": len(interactions["active_reactions"]),
                        "active_typing_count": len(interactions["active_typing"])
                    }
                )
            else:
                self.log_test_result(
                    "Active Interactions Tracking",
                    False,
                    "Missing expected fields in interactions response",
                    {"interactions": interactions}
                )
                
        except Exception as e:
            self.log_test_result(
                "Active Interactions Tracking",
                False,
                f"Failed to track active interactions: {str(e)}"
            )
    
    async def test_webhook_processing_with_interactions(self):
        """Test webhook processing that triggers interactions"""
        print("\\n=== Testing Webhook Processing with Interactions ===")
        
        try:
            # Create a test Telegram webhook payload
            webhook_payload = {
                "update_id": 123456789,
                "message": {
                    "message_id": 987654321,
                    "date": int(datetime.now().timestamp()),
                    "chat": {
                        "id": -1234567890,
                        "type": "group"
                    },
                    "from": {
                        "id": 123456789,
                        "is_bot": False,
                        "first_name": "Test",
                        "username": "testuser"
                    },
                    "text": "Hey there! How can you help me today?"
                }
            }
            
            # Process the webhook
            result = await communication_manager.receive_webhook(self.test_channel_id, webhook_payload)
            
            if "content" in result and result["content"] == "Hey there! How can you help me today?":
                self.log_test_result(
                    "Webhook Processing with Interactions",
                    True,
                    "Successfully processed webhook and triggered interactions",
                    {
                        "message_id": result.get("message_id"),
                        "user_id": result.get("user_id"),
                        "content": result.get("content")
                    }
                )
            else:
                self.log_test_result(
                    "Webhook Processing with Interactions",
                    False,
                    "Webhook processing returned unexpected result",
                    {"result": result}
                )
                
        except Exception as e:
            self.log_test_result(
                "Webhook Processing with Interactions",
                False,
                f"Failed to process webhook: {str(e)}"
            )
    
    async def test_content_analysis_stats(self):
        """Test content analysis statistics"""
        print("\\n=== Testing Content Analysis Statistics ===")
        
        try:
            stats = content_analyzer.get_analysis_stats()
            
            if "cached_analyses" in stats and "supported_contexts" in stats:
                self.log_test_result(
                    "Content Analysis Statistics",
                    True,
                    "Successfully retrieved content analysis statistics",
                    stats
                )
            else:
                self.log_test_result(
                    "Content Analysis Statistics",
                    False,
                    "Missing expected fields in stats response",
                    {"stats": stats}
                )
                
        except Exception as e:
            self.log_test_result(
                "Content Analysis Statistics",
                False,
                f"Failed to get analysis stats: {str(e)}"
            )
    
    async def test_stale_interactions_cleanup(self):
        """Test cleanup of stale interactions"""
        print("\\n=== Testing Stale Interactions Cleanup ===")
        
        try:
            # Test cleanup with default age
            cleanup_result = await communication_manager.cleanup_stale_interactions()
            
            if "cleaned_reactions" in cleanup_result and "cleaned_typing" in cleanup_result:
                self.log_test_result(
                    "Stale Interactions Cleanup",
                    True,
                    "Successfully cleaned up stale interactions",
                    cleanup_result
                )
            else:
                self.log_test_result(
                    "Stale Interactions Cleanup",
                    False,
                    "Cleanup returned unexpected result",
                    {"cleanup_result": cleanup_result}
                )
                
        except Exception as e:
            self.log_test_result(
                "Stale Interactions Cleanup",
                False,
                f"Failed to cleanup stale interactions: {str(e)}"
            )
    
    async def test_contextual_reactions(self):
        """Test contextual emoji reactions based on message content"""
        print("\\n=== Testing Contextual Reactions ===")
        
        # Test different contexts and their expected reaction types
        contextual_tests = [
            ("Good morning! 👋", ["greeting"], "morning_greeting"),
            ("What time is it?", ["question"], "question_about_time"),
            ("I'm lost here... 😕", ["confusion", "uncertainty"], "confusion_with_ellipsis"),
            ("Excellent work! 🎉", ["celebration"], "celebration_message"),
            ("Oops, my bad! 🙏", ["apology"], "apology_message"),
            ("This is incredible! 🚀", ["excitement"], "excitement_message"),
            ("Can you help me please?", ["support"], "help_request")
        ]
        
        for i, (content, expected_contexts, description) in enumerate(contextual_tests):
            try:
                analysis = content_analyzer.analyze_content(content)
                
                # Check if any expected context is detected
                detected_context = analysis["context"]
                if detected_context in expected_contexts:
                    self.log_test_result(
                        f"Contextual Reaction {i+1}",
                        True,
                        f"Correctly identified {description} as {detected_context}",
                        {
                            "content": content,
                            "suggested_reaction": analysis["suggested_reaction"],
                            "confidence": analysis["confidence"]
                        }
                    )
                else:
                    self.log_test_result(
                        f"Contextual Reaction {i+1}",
                        False,
                        f"Expected one of {expected_contexts}, got {detected_context}",
                        {"content": content, "analysis": analysis}
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Contextual Reaction {i+1}",
                    False,
                    f"Exception during contextual analysis: {str(e)}"
                )
    
    async def test_typing_duration_estimation(self):
        """Test typing duration estimation based on content"""
        print("\\n=== Testing Typing Duration Estimation ===")
        
        # Test different message types and their expected typing durations
        duration_tests = [
            ("Hi", "short_greeting", 1.0),
            ("What is the meaning of life?", "philosophical_question", 3.0),
            ("Can you please help me understand how to configure the communication channels with all the interaction settings and reaction management features?", "complex_support_request", 5.0)
        ]
        
        for i, (content, description, min_expected) in enumerate(duration_tests):
            try:
                analysis = content_analyzer.analyze_content(content)
                estimated_duration = content_analyzer.get_typing_duration_estimate(content, analysis["context"])
                
                if estimated_duration >= min_expected:
                    self.log_test_result(
                        f"Typing Duration {i+1}",
                        True,
                        f"Estimated appropriate duration for {description}",
                        {
                            "content": content,
                            "estimated_duration": estimated_duration,
                            "context": analysis["context"]
                        }
                    )
                else:
                    self.log_test_result(
                        f"Typing Duration {i+1}",
                        False,
                        f"Estimated duration too short for {description}",
                        {
                            "content": content,
                            "estimated_duration": estimated_duration,
                            "min_expected": min_expected,
                            "context": analysis["context"]
                        }
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Typing Duration {i+1}",
                    False,
                    f"Exception during duration estimation: {str(e)}"
                )
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Enhanced Interaction Features Test Suite")
        print("=" * 60)
        
        # Run tests in order
        await self.test_content_analysis()
        await self.test_channel_configuration()
        await self.test_message_processing_with_interactions()
        await self.test_active_interactions_tracking()
        await self.test_webhook_processing_with_interactions()
        await self.test_content_analysis_stats()
        await self.test_stale_interactions_cleanup()
        await self.test_contextual_reactions()
        await self.test_typing_duration_estimation()
        
        # Generate test summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate test summary"""
        print("\\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        # Save detailed results to file
        with open("test_interaction_features_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100,
                    "timestamp": datetime.now().isoformat()
                },
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print(f"\\n📄 Detailed results saved to: test_interaction_features_results.json")
        
        return failed_tests == 0

async def main():
    """Main test function"""
    tester = InteractionFeaturesTester()
    success = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())