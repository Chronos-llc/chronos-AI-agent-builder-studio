import re
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """Analyzes message content to determine appropriate reactions and responses"""
    
    # Emoji mappings for different contexts
    GREETING_EMOJIS = ["👋", "🙋‍♂️", "🙋‍♀️", "🤝", "💫", "🌟"]
    QUESTION_EMOJIS = ["❓", "🤔", "💭", "🧐", "🔍"]
    CONFUSION_EMOJIS = ["😕", "🤨", "❓", "😵‍💫", "🤔"]
    CELEBRATION_EMOJIS = ["🎉", "🎊", "👏", "🙌", "💯", "🔥", "✨"]
    APOLOGY_EMOJIS = ["🙏", "😔", "💔", "🥺", "😞"]
    EXCITEMENT_EMOJIS = ["🚀", "💥", "🔥", "💫", "🌟", "⚡"]
    SUPPORT_EMOJIS = ["🤗", "💪", "❤️", "🤝", "🙌", "🌟"]
    ERROR_EMOJIS = ["❌", "😱", "😤", "😡", "🤬", "💥"]
    
    # Keywords and patterns for content analysis
    GREETING_KEYWORDS = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
    QUESTION_KEYWORDS = ["what", "how", "when", "where", "why", "who", "which", "?", "??", "???", "help", "explain"]
    CONFUSION_KEYWORDS = ["confused", "lost", "don't understand", "not clear", "unclear", "what do you mean"]
    CELEBRATION_KEYWORDS = ["great", "awesome", "amazing", "fantastic", "wonderful", "excellent", "perfect", "congratulations"]
    APOLOGY_KEYWORDS = ["sorry", "apologize", "my mistake", "forgive me", "excuse me", "pardon"]
    EXCITEMENT_KEYWORDS = ["excited", "awesome", "fantastic", "wow", "incredible", "mind blown", "amazing"]
    SUPPORT_KEYWORDS = ["help", "support", "assistance", "need help", "can you help", "please help"]
    ERROR_KEYWORDS = ["error", "bug", "issue", "problem", "broken", "doesn't work", "failed", "error"]
    
    # Context-aware reaction patterns
    REACTION_PATTERNS = {
        "processing": "👀",
        "greeting": GREETING_EMOJIS,
        "question": QUESTION_EMOJIS,
        "confusion": CONFUSION_EMOJIS,
        "celebration": CELEBRATION_EMOJIS,
        "apology": APOLOGY_EMOJIS,
        "excitement": EXCITEMENT_EMOJIS,
        "support": SUPPORT_EMOJIS,
        "error": ERROR_EMOJIS
    }
    
    def __init__(self):
        self.content_cache = {}
        self.reaction_history = {}
    
    def analyze_content(self, content: str, sender_info: Optional[Dict] = None) -> Dict[str, any]:
        """
        Analyze message content and return context information
        
        Args:
            content: Message content to analyze
            sender_info: Optional sender information for personalized reactions
            
        Returns:
            Dictionary containing analysis results and suggested reactions
        """
        if not content:
            return {
                "context": "neutral",
                "confidence": 0.0,
                "suggested_reaction": "👀",
                "reasoning": "Empty message",
                "requires_typing": True
            }
        
        content_lower = content.lower().strip()
        analysis_results = []
        confidence_scores = []
        
        # Check for different content types
        if self._check_patterns(content_lower, self.GREETING_KEYWORDS):
            analysis_results.append("greeting")
            confidence_scores.append(0.9)
        
        if self._check_patterns(content_lower, self.QUESTION_KEYWORDS):
            analysis_results.append("question")
            confidence_scores.append(0.8)
        
        if self._check_patterns(content_lower, self.CONFUSION_KEYWORDS):
            analysis_results.append("confusion")
            confidence_scores.append(0.85)
        
        if self._check_patterns(content_lower, self.CELEBRATION_KEYWORDS):
            analysis_results.append("celebration")
            confidence_scores.append(0.75)
        
        if self._check_patterns(content_lower, self.APOLOGY_KEYWORDS):
            analysis_results.append("apology")
            confidence_scores.append(0.9)
        
        if self._check_patterns(content_lower, self.EXCITEMENT_KEYWORDS):
            analysis_results.append("excitement")
            confidence_scores.append(0.7)
        
        if self._check_patterns(content_lower, self.SUPPORT_KEYWORDS):
            analysis_results.append("support")
            confidence_scores.append(0.8)
        
        if self._check_patterns(content_lower, self.ERROR_KEYWORDS):
            analysis_results.append("error")
            confidence_scores.append(0.9)
        
        # Determine primary context
        if not analysis_results:
            primary_context = "neutral"
            confidence = 0.1
            suggested_reaction = "👀"
            reasoning = "No specific context detected"
            requires_typing = True
        else:
            # Get the context with highest confidence
            max_confidence_index = confidence_scores.index(max(confidence_scores))
            primary_context = analysis_results[max_confidence_index]
            confidence = confidence_scores[max_confidence_index]
            suggested_reaction = self._select_contextual_reaction(primary_context, sender_info)
            reasoning = f"Detected {primary_context} context with {confidence:.1%} confidence"
            requires_typing = self._should_show_typing(primary_context)
        
        # Special handling for commands
        if content.startswith('/'):
            primary_context = "command"
            confidence = 1.0
            suggested_reaction = "⚡"
            reasoning = "Command detected - quick processing required"
            requires_typing = False
        
        # Check for emotional indicators
        emotional_indicators = self._detect_emotional_indicators(content)
        if emotional_indicators:
            suggested_reaction = self._select_emotional_reaction(emotional_indicators, sender_info)
            reasoning += f" | Emotional indicator: {emotional_indicators[0]}"
        
        result = {
            "context": primary_context,
            "confidence": confidence,
            "suggested_reaction": suggested_reaction,
            "reasoning": reasoning,
            "requires_typing": requires_typing,
            "all_contexts": analysis_results,
            "emotional_indicators": emotional_indicators,
            "content_length": len(content),
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache the analysis
        content_hash = self._get_content_hash(content)
        self.content_cache[content_hash] = result
        
        return result
    
    def _check_patterns(self, content: str, keywords: List[str]) -> bool:
        """Check if content contains any of the specified patterns"""
        for keyword in keywords:
            if keyword in content:
                return True
        return False
    
    def _detect_emotional_indicators(self, content: str) -> List[str]:
        """Detect emotional indicators in the content"""
        indicators = []
        
        # Count exclamation marks
        exclamation_count = content.count('!')
        if exclamation_count >= 3:
            indicators.append("high_excitement")
        elif exclamation_count >= 1:
            indicators.append("excitement")
        
        # Check for caps (shouting)
        caps_ratio = sum(1 for c in content if c.isupper()) / max(len(content), 1)
        if caps_ratio > 0.5 and len(content) > 5:
            indicators.append("emphasis")
        
        # Check for question marks
        question_count = content.count('?')
        if question_count >= 2:
            indicators.append("confusion")
        elif question_count == 1:
            indicators.append("questioning")
        
        # Check for ellipsis
        if '...' in content:
            indicators.append("uncertainty")
        
        return indicators
    
    def _select_contextual_reaction(self, context: str, sender_info: Optional[Dict] = None) -> str:
        """Select an appropriate reaction based on context and sender"""
        reactions = self.REACTION_PATTERNS.get(context, ["👀"])
        
        # For greeting context, personalize if we have sender info
        if context == "greeting" and sender_info:
            # Return a friendly greeting emoji
            import random
            return random.choice(self.GREETING_EMOJIS)
        
        import random
        return random.choice(reactions)
    
    def _select_emotional_reaction(self, indicators: List[str], sender_info: Optional[Dict] = None) -> str:
        """Select reaction based on emotional indicators"""
        if "high_excitement" in indicators:
            return random.choice(self.EXCITEMENT_EMOJIS + self.CELEBRATION_EMOJIS)
        elif "emphasis" in indicators:
            return "💪"
        elif "confusion" in indicators:
            return random.choice(self.CONFUSION_EMOJIS)
        elif "uncertainty" in indicators:
            return "🤔"
        else:
            return random.choice(self.QUESTION_EMOJIS)
    
    def _should_show_typing(self, context: str) -> bool:
        """Determine if typing indicator should be shown for this context"""
        # Commands and simple acknowledgments don't need typing indicators
        if context in ["command", "greeting"]:
            return False
        
        # Questions, support requests, and complex content need typing indicators
        if context in ["question", "support", "confusion"]:
            return True
        
        # Default to showing typing for most contexts
        return True
    
    def _get_content_hash(self, content: str) -> str:
        """Generate a simple hash for content caching"""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def get_processing_reaction(self, content: str) -> str:
        """Get the standard processing reaction"""
        return "👀"
    
    def get_completion_reactions(self, context: str, original_reaction: str) -> List[str]:
        """Get appropriate reactions to use when completing a message"""
        completion_reactions = []
        
        # Remove the processing reaction
        if original_reaction == "👀":
            completion_reactions.append("✅")
        
        # Add context-specific completion reactions
        if context == "question":
            completion_reactions.append("💡")
        elif context == "support":
            completion_reactions.append("🤝")
        elif context == "celebration":
            completion_reactions.append("🎉")
        elif context == "greeting":
            completion_reactions.append("😊")
        
        return completion_reactions
    
    def should_react_to_message(self, content: str, channel_type: str) -> bool:
        """Determine if we should react to this message based on content and channel"""
        # Don't react to our own messages
        if content.startswith("Bot:") or content.startswith("[BOT]"):
            return False
        
        # Don't react to command messages
        if content.startswith('/'):
            return False
        
        # Always react to regular messages in supported channels
        if channel_type in ["telegram", "discord", "slack"]:
            return True
        
        return False
    
    def get_typing_duration_estimate(self, content: str, context: str) -> float:
        """Estimate how long to show typing indicator (in seconds)"""
        base_duration = 1.0  # Minimum duration
        
        # Longer for complex content
        content_length = len(content)
        if content_length > 100:
            base_duration += 2.0
        elif content_length > 50:
            base_duration += 1.0
        
        # Context-specific adjustments
        if context == "question":
            base_duration += 1.5  # Need more time to formulate answers
        elif context == "support":
            base_duration += 2.0  # Support often requires detailed responses
        elif context == "confusion":
            base_duration += 1.0  # May need clarification questions
        
        # Cap at reasonable maximum
        return min(base_duration, 8.0)
    
    def clear_cache(self):
        """Clear the content analysis cache"""
        self.content_cache.clear()
        self.reaction_history.clear()
    
    def get_analysis_stats(self) -> Dict[str, any]:
        """Get statistics about content analysis usage"""
        return {
            "cached_analyses": len(self.content_cache),
            "reaction_history_entries": len(self.reaction_history),
            "supported_contexts": list(self.REACTION_PATTERNS.keys()),
            "supported_emotions": ["excitement", "confusion", "emphasis", "uncertainty", "questioning"]
        }


# Global content analyzer instance
content_analyzer = ContentAnalyzer()


def analyze_content(content: str, sender_info: Optional[Dict] = None) -> Dict[str, Any]:
    """Convenience wrapper for content analysis."""
    return content_analyzer.analyze_content(content, sender_info)
