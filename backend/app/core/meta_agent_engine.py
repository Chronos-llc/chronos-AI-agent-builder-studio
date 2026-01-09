"""
Meta-Agent FUZZY Core Engine

Provides the core functionality for parsing, classifying, planning,
and executing meta-agent commands.
"""
import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# Intent patterns for command classification
INTENT_PATTERNS = {
    "create_agent": [
        r"(create|build|make|generate)\s+(?:an?\s+)?agent",
        r"new\s+agent",
        r"setup\s+agent"
    ],
    "execute_action": [
        r"(run|execute|perform|do)\s+(?:the\s+)?(action|task)",
        r"trigger\s+action",
        r"invoke\s+(?:the\s+)?action"
    ],
    "query_knowledge": [
        r"(search|query|find|look\s+up)\s+(?:in\s+)?(?:the\s+)?knowledge",
        r"(get|retrieve)\s+(?:the\s+)?(?:knowledge\s+)?(?:information|data)",
        r"ask\s+(?:for\s+)?(?:the\s+)?(?:knowledge\s+)?(?:information|data)"
    ],
    "manage_session": [
        r"(start|end|close|resume)\s+(?:the\s+)?session",
        r"session\s+(?:management|control)"
    ],
    "configure_agent": [
        r"(configure|update|modify|change|set)\s+(?:the\s+)?agent",
        r"agent\s+(?:settings|configuration|options)"
    ],
    "orchestrate": [
        r"(orchestrate|coordinate|manage|supervise)\s+(?:multiple\s+)?(?:agents|tasks)",
        r"run\s+(?:multiple\s+)?(?:agents|tasks)\s+(?:in\s+)?(?:parallel|sequence)",
        r"workflow\s+(?:execution|management)"
    ],
    "analyze": [
        r"(analyze|examine|review|inspect)\s+(?:the\s+)?(?:results|output|data)",
        r"performance\s+(?:analysis|metrics)"
    ],
    "help": [
        r"(help|assist|guide|support)",
        r"what\s+(?:can\s+you\s+)?do",
        r"list\s+(?:available\s+)?commands"
    ]
}


# Action types mapping
ACTION_TYPES = {
    "create_agent": ["agent:create", "llm:generate"],
    "execute_action": ["action:invoke", "hook:trigger"],
    "query_knowledge": ["knowledge:search", "knowledge:retrieve"],
    "manage_session": ["session:manage"],
    "configure_agent": ["agent:update", "config:set"],
    "orchestrate": ["workflow:execute", "agent:coordinate"],
    "analyze": ["data:analyze", "metrics:compute"],
    "help": ["system:help"]
}


# Permission requirements for each intent
PERMISSION_REQUIREMENTS = {
    "create_agent": ["editor", "admin", "superuser"],
    "execute_action": ["editor", "admin", "superuser"],
    "query_knowledge": ["viewer", "editor", "admin", "superuser"],
    "manage_session": ["editor", "admin", "superuser"],
    "configure_agent": ["admin", "superuser"],
    "orchestrate": ["admin", "superuser"],
    "analyze": ["viewer", "editor", "admin", "superuser"],
    "help": ["viewer", "editor", "admin", "superuser"]
}


@dataclass
class ParsedCommand:
    """Structure for parsed command components"""
    type: str
    intent: str
    parameters: Dict[str, Any]
    raw_command: str


class MetaAgentEngine:
    """
    Core engine for meta-agent command processing.
    
    Provides methods for:
    - Parsing natural language commands
    - Classifying command intent
    - Planning execution actions
    - Executing planned actions
    - Validating permissions
    """
    
    def __init__(self):
        """Initialize the meta-agent engine"""
        self._compile_patterns()
        logger.info("MetaAgentEngine initialized")
    
    def _compile_patterns(self):
        """Compile regex patterns for intent classification"""
        self._compiled_patterns = {}
        for intent, patterns in INTENT_PATTERNS.items():
            self._compiled_patterns[intent] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def parse_command(self, command: str) -> Dict[str, Any]:
        """
        Parse a natural language command into structured components.
        
        Args:
            command: Natural language command string
            
        Returns:
            Dictionary containing parsed command type, parameters, and metadata
        """
        command = command.strip()
        
        # Extract key phrases and entities
        parsed = {
            "raw": command,
            "type": self._classify_command_type(command),
            "entities": self._extract_entities(command),
            "parameters": self._extract_parameters(command)
        }
        
        logger.debug(f"Parsed command: {command} -> {parsed}")
        return parsed
    
    def _classify_command_type(self, command: str) -> str:
        """Classify the command type based on content"""
        command_lower = command.lower()
        
        # Check for question patterns
        if command_lower.startswith(("what", "how", "why", "when", "where", "who")):
            return "query"
        
        # Check for imperative patterns
        if any(word in command_lower for word in ["create", "build", "make", "generate"]):
            return "creation"
        
        if any(word in command_lower for word in ["execute", "run", "perform", "do"]):
            return "execution"
        
        if any(word in command_lower for word in ["update", "modify", "change", "configure"]):
            return "modification"
        
        if any(word in command_lower for word in ["delete", "remove", "destroy"]):
            return "deletion"
        
        if any(word in command_lower for word in ["search", "find", "query", "get"]):
            return "retrieval"
        
        return "general"
    
    def _extract_entities(self, command: str) -> Dict[str, Any]:
        """Extract named entities from the command"""
        entities = {}
        
        # Extract agent names (pattern: "agent X", "my agent Y")
        agent_pattern = r"(?:the\s+)?(?:my\s+)?agent\s+([a-zA-Z0-9_-]+)"
        agent_matches = re.findall(agent_pattern, command, re.IGNORECASE)
        if agent_matches:
            entities["agent_name"] = agent_matches[0]
        
        # Extract action names (pattern: "action X", "the action Y")
        action_pattern = r"(?:the\s+)?action\s+([a-zA-Z0-9_-]+)"
        action_matches = re.findall(action_pattern, command, re.IGNORECASE)
        if action_matches:
            entities["action_name"] = action_matches[0]
        
        # Extract IDs (pattern: "ID X", "id X")
        id_pattern = r"(?:id[:\s]+([a-zA-Z0-9-]+))"
        id_matches = re.findall(id_pattern, command, re.IGNORECASE)
        if id_matches:
            entities["id"] = id_matches[0]
        
        # Extract numbers for limits/counts
        number_pattern = r"(\d+)\s+(?:items?|results?|agents?|actions?|times?)"
        number_matches = re.findall(number_pattern, command, re.IGNORECASE)
        if number_matches:
            entities["count"] = int(number_matches[0])
        
        return entities
    
    def _extract_parameters(self, command: str) -> Dict[str, Any]:
        """Extract parameters from the command"""
        parameters = {}
        
        # Extract key-value pairs (pattern: "key=value" or "with key=value")
        kv_pattern = r"(?:with\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^\s,]+)"
        kv_matches = re.findall(kv_pattern, command)
        for key, value in kv_matches:
            # Try to convert to appropriate type
            if value.lower() in ["true", "false"]:
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "").isdigit():
                value = float(value)
            parameters[key] = value
        
        # Extract quoted strings as values
        quoted_pattern = r'"([^"]*)"|\'([^\']*)\''
        quoted_matches = re.findall(quoted_pattern, command)
        if quoted_matches and not parameters:
            parameters["value"] = quoted_matches[0][0] or quoted_matches[0][1]
        
        return parameters
    
    def classify_intent(self, command: str) -> str:
        """
        Classify the intent of a natural language command.
        
        Args:
            command: Natural language command string
            
        Returns:
            Classified intent string
        """
        command_lower = command.lower()
        
        # Check each intent pattern
        for intent, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(command_lower):
                    logger.debug(f"Classified intent: {intent} for command: {command}")
                    return intent
        
        # Default to general intent
        logger.debug(f"Default intent (general) for command: {command}")
        return "general"
    
    def plan_action(self, intent: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Plan execution actions for a given intent and parameters.
        
        Args:
            intent: Classified intent
            parameters: Command parameters
            
        Returns:
            List of planned actions to execute
        """
        actions = []
        
        # Get action types for this intent
        action_types = ACTION_TYPES.get(intent, ["system:generic"])
        
        # Create base action
        base_action = {
            "intent": intent,
            "parameters": parameters,
            "action_types": action_types
        }
        
        # Add intent-specific action planning
        if intent == "create_agent":
            actions.append({
                **base_action,
                "action": "agent:create",
                "steps": [
                    "validate_agent_name",
                    "generate_agent_config",
                    "save_agent"
                ]
            })
        
        elif intent == "execute_action":
            actions.append({
                **base_action,
                "action": "action:invoke",
                "steps": [
                    "validate_action_exists",
                    "check_action_parameters",
                    "execute_action",
                    "capture_result"
                ]
            })
        
        elif intent == "query_knowledge":
            actions.append({
                **base_action,
                "action": "knowledge:search",
                "steps": [
                    "parse_query",
                    "search_knowledge_base",
                    "rank_results",
                    "format_response"
                ]
            })
        
        elif intent == "orchestrate":
            actions.append({
                **base_action,
                "action": "workflow:execute",
                "steps": [
                    "parse_workflow_definition",
                    "validate_agent_dependencies",
                    "execute_parallel_or_sequence",
                    "aggregate_results"
                ]
            })
        
        elif intent == "configure_agent":
            actions.append({
                **base_action,
                "action": "agent:update",
                "steps": [
                    "validate_agent_exists",
                    "apply_configuration_changes",
                    "validate_configuration",
                    "save_changes"
                ]
            })
        
        elif intent == "help":
            actions.append({
                **base_action,
                "action": "system:help",
                "steps": [
                    "list_available_commands",
                    "format_help_output"
                ]
            })
        
        else:
            # Generic action for unknown intents
            actions.append({
                **base_action,
                "action": "system:generic",
                "steps": [
                    "process_command",
                    "generate_response"
                ]
            })
        
        logger.debug(f"Planned actions for intent '{intent}': {actions}")
        return actions
    
    def execute_actions(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute planned actions and return results.
        
        Args:
            actions: List of planned actions to execute
            
        Returns:
            Execution results dictionary
        """
        results = {
            "success": True,
            "actions_executed": [],
            "outputs": [],
            "errors": []
        }
        
        for action in actions:
            action_name = action.get("action", "unknown")
            steps = action.get("steps", [])
            
            try:
                logger.info(f"Executing action: {action_name}")
                
                # Execute each step
                step_results = []
                for step in steps:
                    step_result = self._execute_step(step, action)
                    step_results.append(step_result)
                
                results["actions_executed"].append(action_name)
                results["outputs"].append({
                    "action": action_name,
                    "steps": step_results
                })
                
            except Exception as e:
                logger.error(f"Error executing action {action_name}: {e}")
                results["errors"].append({
                    "action": action_name,
                    "error": str(e)
                })
                results["success"] = False
        
        return results
    
    def _execute_step(self, step: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step of an action.
        
        Args:
            step: Step name
            action: Action context
            
        Returns:
            Step execution result
        """
        parameters = action.get("parameters", {})
        
        # Simulate step execution
        step_result = {
            "step": step,
            "status": "completed",
            "output": {}
        }
        
        # Add step-specific output
        if "validate" in step:
            step_result["output"]["valid"] = True
        elif "execute" in step or "process" in step:
            step_result["output"]["result"] = f"Successfully processed {step}"
        elif "generate" in step or "create" in step:
            step_result["output"]["generated"] = True
        elif "search" in step:
            step_result["output"]["results"] = []
        elif "list" in step:
            step_result["output"]["items"] = []
        
        return step_result
    
    def validate_permissions(self, action: str, permission_level: str) -> bool:
        """
        Validate if the given permission level allows the action.
        
        Args:
            action: Action/Intent to validate
            permission_level: User's permission level
            
        Returns:
            True if permission is granted, False otherwise
        """
        # Get required permissions for this action
        required_permissions = PERMISSION_REQUIREMENTS.get(
            action, 
            PERMISSION_REQUIREMENTS.get("general", ["viewer"])
        )
        
        # Check if user's permission level is sufficient
        permission_hierarchy = ["viewer", "editor", "admin", "superuser"]
        
        try:
            user_level_index = permission_hierarchy.index(permission_level.lower())
            required_level_index = min(
                permission_hierarchy.index(p) for p in required_permissions
            )
            
            is_valid = user_level_index >= required_level_index
            
            logger.debug(
                f"Permission validation: action={action}, "
                f"user_level={permission_level}, required={required_permissions}, "
                f"result={is_valid}"
            )
            
            return is_valid
            
        except ValueError:
            logger.warning(f"Unknown permission level: {permission_level}")
            return False
    
    def get_available_intents(self) -> List[Dict[str, Any]]:
        """
        Get list of available intents with descriptions.
        
        Returns:
            List of intent information dictionaries
        """
        return [
            {
                "intent": intent,
                "description": self._get_intent_description(intent),
                "required_permissions": PERMISSION_REQUIREMENTS.get(intent, ["viewer"]),
                "action_types": ACTION_TYPES.get(intent, ["system:generic"])
            }
            for intent in INTENT_PATTERNS.keys()
        ]
    
    def _get_intent_description(self, intent: str) -> str:
        """Get description for an intent"""
        descriptions = {
            "create_agent": "Create a new agent with specified configuration",
            "execute_action": "Execute a specific action or task",
            "query_knowledge": "Search and retrieve knowledge base information",
            "manage_session": "Start, end, or manage agent sessions",
            "configure_agent": "Update or modify agent configuration",
            "orchestrate": "Coordinate multiple agents and tasks",
            "analyze": "Analyze results, outputs, or performance metrics",
            "help": "Get help and list available commands"
        }
        return descriptions.get(intent, "General command processing")


# Engine initialization function
def initialize_meta_agent_engine() -> MetaAgentEngine:
    """
    Initialize and return the meta-agent engine instance.
    
    Returns:
        Initialized MetaAgentEngine instance
    """
    return MetaAgentEngine()


# Global engine instance
_meta_agent_engine: Optional[MetaAgentEngine] = None


def get_meta_agent_engine() -> MetaAgentEngine:
    """Get or create the global meta-agent engine instance"""
    global _meta_agent_engine
    if _meta_agent_engine is None:
        _meta_agent_engine = MetaAgentEngine()
    return _meta_agent_engine